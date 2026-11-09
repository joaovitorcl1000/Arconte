"""Famílias, casas, clãs e dinastias do Arconte.

Este módulo representa **afiliações sociais**, não vínculos genealógicos.
Ser membro de uma casa não significa ser descendente de seu fundador.
Os parentescos continuam sendo responsabilidade de ``Genealogy``.

Compatível com Python 3.10+. Não utiliza banco de dados ou bibliotecas externas.

Exemplo (executar a partir de ``backend/genealogy``)::

    from character.character import Character
    from genealogy.genealogy import Genealogy
    from family.family import (
        Family, FamilyType, FamilyMembership, MembershipOrigin, FamilyRegistry,
    )

    genealogy = Genealogy()
    arthur = Character(name="Arthur", surname="Valerian")
    genealogy.add_character(arthur)

    registry = FamilyRegistry(genealogy)
    house = Family(name="Valerian", type=FamilyType.HOUSE,
                   founder_id=arthur.id, founded_year=1245)
    registry.add_family(house)
    registry.add_membership(FamilyMembership(
        family_id=house.id, character_id=arthur.id,
        origin=MembershipOrigin.FOUNDATION, role="Fundador",
    ))

    print([character.full_name for character in registry.get_members(house.id)])

ATENÇÃO: o ``storage.py`` atual persiste apenas personagens e relações.
Famílias e afiliações ainda não são gravadas em JSON por ele. O suporte
à persistência deve ser adicionado posteriormente, com nova versão do formato.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from unicodedata import combining, normalize
from uuid import UUID, uuid4

from character.character import Character
from genealogy.genealogy import Genealogy


class FamilyType(str, Enum):
    """Categorias de organização familiar e político-social."""

    FAMILY = "family"
    HOUSE = "house"
    CLAN = "clan"
    DYNASTY = "dynasty"


class MembershipOrigin(str, Enum):
    """Motivo pelo qual um personagem integra uma família ou organização.

    Uma filiação biológica/adotiva é representada em ``Relationship``;
    estas categorias NÃO criam automaticamente uma relação de parentesco.
    """

    BIRTH = "birth"
    ADOPTION = "adoption"
    MARRIAGE = "marriage"
    FOUNDATION = "foundation"
    AFFILIATION = "affiliation"


def _sort_text(value: str) -> str:
    """Ordena alfabeticamente ignorando maiúsculas e acentos comuns."""
    return "".join(c for c in normalize("NFKD", value.casefold()) if not combining(c))


def _check_uuid(value: UUID, field_name: str) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{field_name} deve ser um UUID.")


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} deve ser uma string.")
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} não pode estar vazio.")
    return text


def _optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} deve ser uma string ou None.")
    return value.strip() or None


def _optional_year(value: int | None, field_name: str) -> None:
    # bool é subtipo de int, mas não representa um ano.
    if value is not None and type(value) is not int:
        raise TypeError(f"{field_name} deve ser um inteiro ou None.")


def _check_period(start: int | None, end: int | None, start_name: str,
                  end_name: str) -> None:
    _optional_year(start, start_name)
    _optional_year(end, end_name)
    if start is not None and end is not None and end < start:
        raise ValueError(f"{end_name} não pode ser anterior a {start_name}.")


@dataclass(frozen=True, slots=True, kw_only=True)
class Family:
    """Identidade de uma família, casa, clã ou dinastia.

    ``founder_id`` é uma referência opcional a um personagem, não uma
    filiação genealógica. ``founded_year``/``dissolved_year`` aceitam anos
    negativos, permitindo calendários ficcionais; o calendário em si não é
    imposto por este módulo.

    Entidade imutável. Para alterar atributos use ``dataclasses.replace``
    e registre a nova versão com ``FamilyRegistry.update_family``.
    """

    name: str
    type: FamilyType = FamilyType.FAMILY
    founder_id: UUID | None = None
    founded_year: int | None = None
    dissolved_year: int | None = None
    motto: str | None = None
    description: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        _check_uuid(self.id, "id")
        if not isinstance(self.type, FamilyType):
            raise TypeError("type deve ser um FamilyType.")
        if self.founder_id is not None:
            _check_uuid(self.founder_id, "founder_id")
        object.__setattr__(self, "name", _required_text(self.name, "name"))
        for attr in ("motto", "description"):
            object.__setattr__(self, attr, _optional_text(getattr(self, attr), attr))
        _check_period(self.founded_year, self.dissolved_year,
                      "founded_year", "dissolved_year")

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True, kw_only=True)
class FamilyMembership:
    """Vínculo histórico de um personagem com uma família/casa/dinastia.

    O personagem pode ter várias afiliações, inclusive simultâneas.
    ``role`` é um título ou função livre ("chefe", "rainha", "herdeiro"...).
    Para promover alguém ou registrar uma nova fase de afiliação, pode-se
    criar um novo vínculo com datas distintas.

    ``start_year``/``end_year`` são inclusivos. Um extremo ``None`` indica
    uma data não especificada. A busca temporal o considera sem limite.
    """

    family_id: UUID
    character_id: UUID
    origin: MembershipOrigin = MembershipOrigin.AFFILIATION
    start_year: int | None = None
    end_year: int | None = None
    role: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        for attr in ("id", "family_id", "character_id"):
            _check_uuid(getattr(self, attr), attr)
        if not isinstance(self.origin, MembershipOrigin):
            raise TypeError("origin deve ser um MembershipOrigin.")
        _check_period(self.start_year, self.end_year,
                      "start_year", "end_year")
        object.__setattr__(self, "role", _optional_text(self.role, "role"))

    def is_active_at(self, year: int) -> bool:
        """Verifica se a afiliação abrange o ano informado (inclusive)."""
        if type(year) is not int:
            raise TypeError("year deve ser um inteiro.")
        return (self.start_year is None or year >= self.start_year) and (
            self.end_year is None or year <= self.end_year
        )


class FamilyRegistry:
    """Gerencia famílias e afiliações vinculadas a uma Genealogy existente.

    Garante que o fundador (quando indicado) e os membros estejam registrados
    em ``Genealogy`` ao criar/atualizar entidades. Não altera parentescos.

    Importante: se ``Genealogy.remove_character`` for chamado diretamente,
    afiliações podem ficar órfãs. Use ``remove_character_memberships`` antes
    da remoção, ou ``validate_integrity`` para verificar inconsistências.
    """

    def __init__(self, genealogy: Genealogy) -> None:
        if not isinstance(genealogy, Genealogy):
            raise TypeError("genealogy deve ser um objeto Genealogy.")
        self._genealogy = genealogy
        self._families: dict[UUID, Family] = {}
        self._memberships: dict[UUID, FamilyMembership] = {}
        self._memberships_by_family: dict[UUID, set[UUID]] = {}
        self._memberships_by_character: dict[UUID, set[UUID]] = {}

    # ------------------------------------------------------------------
    # Famílias
    # ------------------------------------------------------------------
    def add_family(self, family: Family) -> None:
        """Cadastra uma família, exigindo ID novo e fundador existente."""
        if not isinstance(family, Family):
            raise TypeError("family deve ser um Family.")
        if family.id in self._families:
            raise ValueError("Já existe uma família com esse id.")
        self._validate_founder(family)
        self._families[family.id] = family
        self._memberships_by_family[family.id] = set()

    def update_family(self, family: Family) -> None:
        """Substitui os dados de uma família, preservando suas afiliações."""
        if not isinstance(family, Family):
            raise TypeError("family deve ser um Family.")
        self.get_family(family.id)
        self._validate_founder(family)
        self._families[family.id] = family

    def get_family(self, family_id: UUID) -> Family:
        _check_uuid(family_id, "family_id")
        return self._families[family_id]

    def get_all_families(self) -> tuple[Family, ...]:
        """Lista famílias ordenadas por nome e UUID."""
        return tuple(sorted(self._families.values(),
                            key=lambda f: (_sort_text(f.name), str(f.id))))

    def remove_family(self, family_id: UUID) -> Family:
        """Exclui uma família e seus vínculos, sem excluir personagens."""
        family = self.get_family(family_id)
        for membership_id in tuple(self._memberships_by_family[family_id]):
            self.remove_membership(membership_id)
        del self._memberships_by_family[family_id]
        del self._families[family_id]
        return family

    # ------------------------------------------------------------------
    # Afiliações
    # ------------------------------------------------------------------
    def add_membership(self, membership: FamilyMembership) -> None:
        """Cadastra uma afiliação, impedindo repetições exatas."""
        if not isinstance(membership, FamilyMembership):
            raise TypeError("membership deve ser um FamilyMembership.")
        if membership.id in self._memberships:
            raise ValueError("Já existe uma afiliação com esse id.")
        self.get_family(membership.family_id)
        self._require_character(membership.character_id)
        self._reject_duplicate_membership(membership)
        self._memberships[membership.id] = membership
        self._memberships_by_family[membership.family_id].add(membership.id)
        self._memberships_by_character.setdefault(membership.character_id, set()).add(
            membership.id
        )

    def update_membership(self, membership: FamilyMembership) -> None:
        """Atualiza uma afiliação preservando o UUID e os índices internos."""
        if not isinstance(membership, FamilyMembership):
            raise TypeError("membership deve ser um FamilyMembership.")
        old = self.get_membership(membership.id)
        self.get_family(membership.family_id)
        self._require_character(membership.character_id)
        self._reject_duplicate_membership(membership, exclude_id=membership.id)
        if old.family_id != membership.family_id:
            self._memberships_by_family[old.family_id].remove(old.id)
            self._memberships_by_family[membership.family_id].add(membership.id)
        if old.character_id != membership.character_id:
            self._memberships_by_character[old.character_id].remove(old.id)
            if not self._memberships_by_character[old.character_id]:
                del self._memberships_by_character[old.character_id]
            self._memberships_by_character.setdefault(membership.character_id, set()).add(
                membership.id
            )
        self._memberships[membership.id] = membership

    def get_membership(self, membership_id: UUID) -> FamilyMembership:
        _check_uuid(membership_id, "membership_id")
        return self._memberships[membership_id]

    def remove_membership(self, membership_id: UUID) -> FamilyMembership:
        """Remove um vínculo sem modificar personagens ou parentescos."""
        membership = self.get_membership(membership_id)
        del self._memberships[membership_id]
        self._memberships_by_family[membership.family_id].remove(membership_id)
        self._memberships_by_character[membership.character_id].remove(membership_id)
        if not self._memberships_by_character[membership.character_id]:
            del self._memberships_by_character[membership.character_id]
        return membership

    def get_memberships(
        self, *, family_id: UUID | None = None,
        character_id: UUID | None = None,
        origin: MembershipOrigin | None = None,
        at_year: int | None = None,
    ) -> tuple[FamilyMembership, ...]:
        """Consulta vínculos, opcionalmente filtrando família, pessoa e ano."""
        if family_id is not None:
            self.get_family(family_id)
        if character_id is not None:
            self._require_character(character_id)
        if origin is not None and not isinstance(origin, MembershipOrigin):
            raise TypeError("origin deve ser um MembershipOrigin ou None.")
        if at_year is not None:
            _optional_year(at_year, "at_year")

        if family_id is not None:
            ids = self._memberships_by_family[family_id]
        elif character_id is not None:
            ids = self._memberships_by_character.get(character_id, set())
        else:
            ids = self._memberships.keys()

        matches = (
            self._memberships[mid] for mid in ids
            if (family_id is None or self._memberships[mid].family_id == family_id)
            and (character_id is None or self._memberships[mid].character_id == character_id)
            and (origin is None or self._memberships[mid].origin is origin)
            and (at_year is None or self._memberships[mid].is_active_at(at_year))
        )
        return tuple(sorted(matches, key=lambda m: (
            str(m.family_id), str(m.character_id),
            m.start_year is None,
            m.start_year if m.start_year is not None else 0,
            str(m.id),
        )))

    def get_members(
        self, family_id: UUID, *, at_year: int | None = None,
        origin: MembershipOrigin | None = None,
    ) -> tuple[Character, ...]:
        """Retorna membros únicos da família, ordenados pelo nome."""
        memberships = self.get_memberships(
            family_id=family_id, at_year=at_year, origin=origin
        )
        ids = {m.character_id for m in memberships}
        return tuple(sorted(
            (self._genealogy.get_character(cid) for cid in ids),
            key=lambda c: (_sort_text(c.full_name), str(c.id)),
        ))

    def get_families_for_character(
        self, character_id: UUID, *, at_year: int | None = None,
    ) -> tuple[Family, ...]:
        """Retorna as famílias de um personagem (inclusive vínculos históricos)."""
        memberships = self.get_memberships(
            character_id=character_id, at_year=at_year
        )
        ids = {m.family_id for m in memberships}
        return tuple(sorted(
            (self._families[fid] for fid in ids),
            key=lambda f: (_sort_text(f.name), str(f.id)),
        ))

    def remove_character_memberships(
        self, character_id: UUID,
    ) -> tuple[FamilyMembership, ...]:
        """Remove todas as afiliações antes de excluir o personagem da genealogia.

        Caso o personagem seja fundador, o campo ``founder_id`` nas famílias
        associadas também precisa ser alterado previamente (via update_family).
        """
        self._require_character(character_id)
        memberships = self.get_memberships(character_id=character_id)
        for membership in memberships:
            self.remove_membership(membership.id)
        return memberships

    def validate_integrity(self) -> None:
        """Verifica referências cruzadas e índices; lança ValueError se inválidos.

        Útil após alterações em ``Genealogy`` feitas fora do registro familiar.
        Não altera dados nem corrige automaticamente inconsistências.
        """
        try:
            for family in self._families.values():
                self._validate_founder(family)
            for mid, membership in self._memberships.items():
                self.get_family(membership.family_id)
                self._require_character(membership.character_id)
                if mid not in self._memberships_by_family[membership.family_id]:
                    raise ValueError("Índice de afiliações por família inconsistente.")
                if mid not in self._memberships_by_character.get(membership.character_id, set()):
                    raise ValueError("Índice de afiliações por personagem inconsistente.")
            for fid, mids in self._memberships_by_family.items():
                self.get_family(fid)
                if any(mid not in self._memberships or
                       self._memberships[mid].family_id != fid for mid in mids):
                    raise ValueError("Índice de afiliações por família inconsistente.")
            for cid, mids in self._memberships_by_character.items():
                self._require_character(cid)
                if any(mid not in self._memberships or
                       self._memberships[mid].character_id != cid for mid in mids):
                    raise ValueError("Índice de afiliações por personagem inconsistente.")
        except KeyError as exc:
            raise ValueError(f"Referência familiar inexistente: {exc}") from exc

    # ------------------------------------------------------------------
    # Auxiliares privados
    # ------------------------------------------------------------------
    def _require_character(self, character_id: UUID) -> None:
        _check_uuid(character_id, "character_id")
        self._genealogy.get_character(character_id)  # lança KeyError se ausente

    def _validate_founder(self, family: Family) -> None:
        if family.founder_id is not None:
            self._require_character(family.founder_id)

    def _reject_duplicate_membership(
        self, membership: FamilyMembership, *, exclude_id: UUID | None = None,
    ) -> None:
        for mid in self._memberships_by_family[membership.family_id]:
            if mid == exclude_id:
                continue
            existing = self._memberships[mid]
            if (
                existing.character_id == membership.character_id
                and existing.origin == membership.origin
                and existing.start_year == membership.start_year
                and existing.end_year == membership.end_year
                and existing.role == membership.role
            ):
                raise ValueError("Essa afiliação já foi cadastrada.")


__all__ = [
    "FamilyType", "MembershipOrigin", "Family", "FamilyMembership", "FamilyRegistry"
]
