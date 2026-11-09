"""Registro de organizações e afiliações ligado a uma Genealogy existente.

Mantém identidade de organizações e vínculos históricos separados dos dados
pessoais de Character, de famílias e de relações genealógicas. Nenhuma
afiliação é inferida automaticamente de sobrenome, religião ou parentesco.

O registro pode ser convertido para/de um objeto JSON independente por
``to_dict``/``from_dict``. Ainda NÃO é persistido por Project.save(): a
integração com Project e Storage será uma etapa separada e versionada.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping
from uuid import UUID

from character.character import Character
from genealogy.genealogy import Genealogy
from organization.membership import OrganizationMembership
from organization.organization import Organization


def _check_uuid(value: UUID, field_name: str) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{field_name} deve ser um UUID.")


def _check_year(value: int | None, label: str) -> None:
    if value is not None and type(value) is not int:
        raise TypeError(f"{label} deve ser um inteiro ou None.")


def _sort_text(value: str) -> str:
    return value.casefold()


class OrganizationRegistry:
    """Administra organizações e membros com referências validadas.

    ``genealogy`` deve ser a mesma instância cujos personagens participam
    das organizações. Caso ela seja modificada por fora, ``validate_integrity``
    detecta referências órfãs. Use ``remove_character_references`` antes de
    excluir um personagem quando houver organizações vinculadas a ele.

    Vínculos duplicados com a mesma organização, personagem, função, grau
    hierárquico e período são rejeitados. Funções diferentes simultâneas e
    períodos sucessivos são permitidos. O fundador NÃO vira membro por si só.
    """

    def __init__(self, genealogy: Genealogy) -> None:
        if not isinstance(genealogy, Genealogy):
            raise TypeError("genealogy deve ser um objeto Genealogy.")
        self._genealogy = genealogy
        self._organizations: dict[UUID, Organization] = {}
        self._memberships: dict[UUID, OrganizationMembership] = {}
        self._memberships_by_organization: dict[UUID, set[UUID]] = {}
        self._memberships_by_character: dict[UUID, set[UUID]] = {}

    # ---- Organizações -------------------------------------------------
    def add_organization(self, organization: Organization) -> None:
        if not isinstance(organization, Organization):
            raise TypeError("organization deve ser Organization.")
        if organization.id in self._organizations:
            raise ValueError("Já existe uma organização com esse id.")
        self._validate_founder(organization)
        self._organizations[organization.id] = organization
        self._memberships_by_organization[organization.id] = set()

    def update_organization(self, organization: Organization) -> None:
        """Atualiza uma organização sem invalidar seus vínculos existentes."""
        if not isinstance(organization, Organization):
            raise TypeError("organization deve ser Organization.")
        self.get_organization(organization.id)
        self._validate_founder(organization)
        for mid in self._memberships_by_organization[organization.id]:
            self._validate_membership_period(self._memberships[mid], organization)
        self._organizations[organization.id] = organization

    def get_organization(self, organization_id: UUID) -> Organization:
        _check_uuid(organization_id, "organization_id")
        return self._organizations[organization_id]

    def get_all_organizations(self) -> tuple[Organization, ...]:
        return tuple(sorted(
            self._organizations.values(),
            key=lambda o: (_sort_text(o.name), str(o.id)),
        ))

    def remove_organization(self, organization_id: UUID) -> Organization:
        """Exclui a organização e seus vínculos, nunca os personagens."""
        organization = self.get_organization(organization_id)
        for mid in tuple(self._memberships_by_organization[organization_id]):
            self.remove_membership(mid)
        del self._memberships_by_organization[organization_id]
        del self._organizations[organization_id]
        return organization

    # ---- Afiliações ---------------------------------------------------
    def add_membership(self, membership: OrganizationMembership) -> None:
        if not isinstance(membership, OrganizationMembership):
            raise TypeError("membership deve ser OrganizationMembership.")
        if membership.id in self._memberships:
            raise ValueError("Já existe uma afiliação com esse id.")
        organization = self.get_organization(membership.organization_id)
        self._require_character(membership.character_id)
        self._validate_membership_period(membership, organization)
        self._reject_duplicate(membership)
        self._memberships[membership.id] = membership
        self._memberships_by_organization[membership.organization_id].add(membership.id)
        self._memberships_by_character.setdefault(membership.character_id, set()).add(
            membership.id
        )

    def update_membership(self, membership: OrganizationMembership) -> None:
        """Atualiza um vínculo preservando seu UUID e todos os índices."""
        if not isinstance(membership, OrganizationMembership):
            raise TypeError("membership deve ser OrganizationMembership.")
        old = self.get_membership(membership.id)
        organization = self.get_organization(membership.organization_id)
        self._require_character(membership.character_id)
        self._validate_membership_period(membership, organization)
        self._reject_duplicate(membership, exclude_id=membership.id)

        if old.organization_id != membership.organization_id:
            self._memberships_by_organization[old.organization_id].remove(old.id)
            self._memberships_by_organization[membership.organization_id].add(old.id)
        if old.character_id != membership.character_id:
            self._memberships_by_character[old.character_id].remove(old.id)
            if not self._memberships_by_character[old.character_id]:
                del self._memberships_by_character[old.character_id]
            self._memberships_by_character.setdefault(membership.character_id, set()).add(
                old.id
            )
        self._memberships[membership.id] = membership

    def get_membership(self, membership_id: UUID) -> OrganizationMembership:
        _check_uuid(membership_id, "membership_id")
        return self._memberships[membership_id]

    def remove_membership(self, membership_id: UUID) -> OrganizationMembership:
        membership = self.get_membership(membership_id)
        del self._memberships[membership_id]
        self._memberships_by_organization[membership.organization_id].remove(membership.id)
        self._memberships_by_character[membership.character_id].remove(membership.id)
        if not self._memberships_by_character[membership.character_id]:
            del self._memberships_by_character[membership.character_id]
        return membership

    def get_memberships(
        self, *, organization_id: UUID | None = None,
        character_id: UUID | None = None, role: str | None = None,
        at_year: int | None = None,
    ) -> tuple[OrganizationMembership, ...]:
        """Consulta vínculos por instituição, personagem, cargo ou ano.

        Consulta temporal considera simultaneamente a validade da organização
        e o período da afiliação. Não infere entrada/saída a partir da vida do
        personagem, permitindo títulos honoríficos e costumes fictícios.
        """
        if organization_id is not None:
            self.get_organization(organization_id)
        if character_id is not None:
            self._require_character(character_id)
        if role is not None:
            if not isinstance(role, str):
                raise TypeError("role deve ser uma string ou None.")
            role = role.strip().casefold()
            if not role:
                raise ValueError("role não pode ser vazio no filtro.")
        _check_year(at_year, "at_year")

        if organization_id is not None:
            ids = self._memberships_by_organization[organization_id]
        elif character_id is not None:
            ids = self._memberships_by_character.get(character_id, set())
        else:
            ids = self._memberships.keys()

        matches = (
            self._memberships[mid] for mid in ids
            if (organization_id is None or self._memberships[mid].organization_id == organization_id)
            and (character_id is None or self._memberships[mid].character_id == character_id)
            and (role is None or (
                self._memberships[mid].role is not None
                and self._memberships[mid].role.casefold() == role
            ))
            and (
                at_year is None
                or (self._memberships[mid].is_active_at(at_year)
                    and self._organizations[self._memberships[mid].organization_id]
                        .is_active_at(at_year))
            )
        )
        return tuple(sorted(matches, key=lambda m: (
            str(m.organization_id), str(m.character_id),
            m.start_year is None,
            m.start_year if m.start_year is not None else 0,
            _sort_text(m.role or ""), str(m.id),
        )))

    def get_members(
        self, organization_id: UUID, *, at_year: int | None = None,
        role: str | None = None,
    ) -> tuple[Character, ...]:
        """Retorna personagens únicos, ordenados por nome completo."""
        memberships = self.get_memberships(
            organization_id=organization_id, at_year=at_year, role=role
        )
        ids = {item.character_id for item in memberships}
        return tuple(sorted(
            (self._genealogy.get_character(cid) for cid in ids),
            key=lambda c: (_sort_text(c.full_name), str(c.id)),
        ))

    def get_organizations_for_character(
        self, character_id: UUID, *, at_year: int | None = None,
    ) -> tuple[Organization, ...]:
        memberships = self.get_memberships(character_id=character_id, at_year=at_year)
        ids = {item.organization_id for item in memberships}
        return tuple(sorted(
            (self._organizations[oid] for oid in ids),
            key=lambda o: (_sort_text(o.name), str(o.id)),
        ))

    def remove_character_memberships(
        self, character_id: UUID,
    ) -> tuple[OrganizationMembership, ...]:
        """Limpa vínculos, mas não a referência de fundador (se existir)."""
        self._require_character(character_id)
        memberships = self.get_memberships(character_id=character_id)
        for membership in memberships:
            self.remove_membership(membership.id)
        return memberships

    def remove_character_references(
        self, character_id: UUID, *, founder_policy: str = "reject",
    ) -> tuple[OrganizationMembership, ...]:
        """Prepara a exclusão de um personagem, com política para fundadores.

        ``reject`` impede apagar um fundador; ``clear`` zera fundador nas
        organizações e remove todas as afiliações do personagem.
        Nenhum personagem da genealogia é excluído por este método.
        """
        self._require_character(character_id)
        if founder_policy not in ("reject", "clear"):
            raise ValueError("founder_policy deve ser 'reject' ou 'clear'.")
        founded = tuple(o for o in self._organizations.values()
                        if o.founder_id == character_id)
        if founded and founder_policy == "reject":
            raise ValueError("O personagem é fundador de uma organização.")
        memberships = self.get_memberships(character_id=character_id)
        for org in founded:
            self.update_organization(replace(org, founder_id=None))
        for membership in memberships:
            self.remove_membership(membership.id)
        return memberships

    # ---- Integridade e intercâmbio JSON -------------------------------
    def validate_integrity(self) -> None:
        """Detecta referências inválidas, índices inconsistentes e duplicatas."""
        try:
            for org in self._organizations.values():
                self._validate_founder(org)
            expected_by_org = {oid: set() for oid in self._organizations}
            expected_by_character: dict[UUID, set[UUID]] = {}
            fingerprints: set[tuple[Any, ...]] = set()
            for mid, membership in self._memberships.items():
                org = self.get_organization(membership.organization_id)
                self._require_character(membership.character_id)
                self._validate_membership_period(membership, org)
                fingerprint = self._fingerprint(membership)
                if fingerprint in fingerprints:
                    raise ValueError("Afiliações duplicadas encontradas.")
                fingerprints.add(fingerprint)
                expected_by_org[org.id].add(mid)
                expected_by_character.setdefault(membership.character_id, set()).add(mid)
            if expected_by_org != self._memberships_by_organization:
                raise ValueError("Índices de organização inconsistentes.")
            if expected_by_character != self._memberships_by_character:
                raise ValueError("Índices de personagem inconsistentes.")
        except KeyError as exc:
            raise ValueError(f"Referência organizacional inexistente: {exc}") from exc

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Serialização independente: não integra ainda Project.save()."""
        self.validate_integrity()
        return {
            "organizations": [org.to_dict() for org in self.get_all_organizations()],
            "memberships": [m.to_dict() for m in self.get_memberships()],
        }

    @classmethod
    def from_dict(
        cls, genealogy: Genealogy, data: Mapping[str, Any],
    ) -> OrganizationRegistry:
        """Constrói registro novo, validando referências sem efeitos colaterais."""
        if not isinstance(data, Mapping):
            raise TypeError("O registro deve ser um objeto JSON/mapeamento.")
        required = {"organizations", "memberships"}
        missing = required - data.keys()
        extra = data.keys() - required
        if missing or extra:
            raise ValueError(
                f"Campos de registro ausentes {sorted(missing)} "
                f"ou desconhecidos {sorted(extra)}."
            )
        if type(data["organizations"]) is not list:
            raise TypeError("organizations deve ser uma lista.")
        if type(data["memberships"]) is not list:
            raise TypeError("memberships deve ser uma lista.")
        registry = cls(genealogy)
        for data_org in data["organizations"]:
            registry.add_organization(Organization.from_dict(data_org))
        for data_member in data["memberships"]:
            registry.add_membership(OrganizationMembership.from_dict(data_member))
        registry.validate_integrity()
        return registry

    # ---- Validações internas -----------------------------------------
    def _require_character(self, character_id: UUID) -> None:
        _check_uuid(character_id, "character_id")
        self._genealogy.get_character(character_id)

    def _validate_founder(self, organization: Organization) -> None:
        if organization.founder_id is not None:
            self._require_character(organization.founder_id)

    @staticmethod
    def _validate_membership_period(
        membership: OrganizationMembership, organization: Organization,
    ) -> None:
        if (
            (membership.start_year is not None
             and organization.founded_year is not None
             and membership.start_year < organization.founded_year)
            or (membership.end_year is not None
                and organization.dissolved_year is not None
                and membership.end_year > organization.dissolved_year)
            or (membership.end_year is not None
                and organization.founded_year is not None
                and membership.end_year < organization.founded_year)
            or (membership.start_year is not None
                and organization.dissolved_year is not None
                and membership.start_year > organization.dissolved_year)
        ):
            raise ValueError("Período da afiliação fora da existência da organização.")

    @staticmethod
    def _fingerprint(m: OrganizationMembership) -> tuple[Any, ...]:
        return (m.organization_id, m.character_id, m.role, m.rank,
                m.start_year, m.end_year)

    def _reject_duplicate(
        self, membership: OrganizationMembership, *, exclude_id: UUID | None = None,
    ) -> None:
        for mid in self._memberships_by_organization[membership.organization_id]:
            if mid != exclude_id and self._fingerprint(self._memberships[mid]) == self._fingerprint(membership):
                raise ValueError("Essa afiliação já foi cadastrada.")


__all__ = ["OrganizationRegistry"]
