"""Entidade de domínio para organizações de mundos fictícios no Arconte.

Uma organização pode representar uma ordem de cavalaria, uma guilda, uma
facção política, uma instituição religiosa, uma sociedade secreta, etc.
A classe registra apenas a **identidade e descrição da instituição**.

- ``founder_id`` é uma referência opcional ao UUID de um personagem; a
  existência desse personagem será verificada futuramente por um registro
  de organizações integrado ao projeto.
- Participantes, cargos e períodos de filiação NÃO são armazenados aqui;
  serão responsabilidade de ``organization.membership`` / ``registry``.
- Uma instituição religiosa não é sinônimo de religião ou divindade; esses
  conceitos poderão ser modelados separadamente.
- A entidade é imutável; utilize ``dataclasses.replace`` para atualizá-la.
- Anos inteiros, inclusive negativos, admitem calendários fictícios.

Exemplo::

    from organization.organization import Organization, OrganizationType

    ordem = Organization(
        name="Ordem do Falcão Vermelho",
        type=OrganizationType.KNIGHTLY_ORDER,
        headquarters="Sarnília",
        motto="A honra guia nossas asas",
        custom_attributes={"brasão": {"animal": "falcão", "cor": "vermelho"}},
    )
    registro_json = ordem.to_dict()
    copia = Organization.from_dict(registro_json)

Este módulo usa somente a biblioteca-padrão do Python 3.10+ e não modifica o
esquema JSON atual dos projetos. A serialização aqui é apenas da entidade.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4


class OrganizationType(str, Enum):
    """Categorias gerais. ``OTHER`` cobre instituições não classificadas.

    Categorias são descritivas: elas não atribuem poderes, doutrinas ou regras
    de filiação automaticamente.
    """

    ORGANIZATION = "organization"
    GROUP = "group"
    ORDER = "order"
    KNIGHTLY_ORDER = "knightly_order"
    RELIGIOUS_ORDER = "religious_order"
    RELIGIOUS_INSTITUTION = "religious_institution"
    MAGICAL_ORDER = "magical_order"
    GUILD = "guild"
    POLITICAL_FACTION = "political_faction"
    MILITARY = "military"
    ACADEMIC = "academic"
    SECRET_SOCIETY = "secret_society"
    OTHER = "other"


_OPTIONAL_TEXT_FIELDS = ("headquarters", "motto", "emblem", "description")
_FIELDS = frozenset((
    "name", "type", "founder_id", "founded_year", "dissolved_year",
    *_OPTIONAL_TEXT_FIELDS, "custom_attributes", "id",
))


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} não pode estar vazio.")
    return normalized


def _optional_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string ou None.")
    return value.strip() or None


def _uuid(value: UUID, name: str) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{name} deve ser um UUID.")


def _optional_year(value: int | None, name: str) -> None:
    if value is not None and type(value) is not int:
        raise TypeError(f"{name} deve ser um inteiro ou None.")


def _key(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("As chaves de custom_attributes devem ser strings.")
    normalized = value.strip()
    if not normalized:
        raise ValueError("Chaves de custom_attributes não podem ser vazias.")
    return normalized


def _freeze_json(value: Any, ancestors: set[int]) -> Any:
    """Copia dados compatíveis com JSON em objetos profundamente imutáveis.

    Só rejeita ciclos verdadeiros: referências repetidas sem ciclos são aceitas.
    """
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("custom_attributes não aceita NaN ou infinito.")
        return value

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("custom_attributes não pode conter referências circulares.")
        ancestors.add(identity)
        try:
            result: dict[str, Any] = {}
            for raw_key, item in value.items():
                normalized = _key(raw_key)
                if normalized in result:
                    raise ValueError(
                        f"Chave duplicada em custom_attributes: {normalized!r}."
                    )
                result[normalized] = _freeze_json(item, ancestors)
            return MappingProxyType(result)
        finally:
            ancestors.remove(identity)

    if type(value) in (list, tuple):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("custom_attributes não pode conter referências circulares.")
        ancestors.add(identity)
        try:
            return tuple(_freeze_json(item, ancestors) for item in value)
        finally:
            ancestors.remove(identity)

    raise TypeError(
        "custom_attributes aceita apenas tipos JSON: texto, número, bool, "
        "null, listas e objetos."
    )


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _uuid_from_json(value: Any, name: str) -> UUID:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string UUID no JSON.")
    try:
        return UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{name} não é um UUID válido.") from exc


@dataclass(frozen=True, slots=True, kw_only=True)
class Organization:
    """Identidade e características de uma organização fictícia.

    ``founded_year`` e ``dissolved_year`` delimitam o período da instituição
    (inclusive); ``None`` significa data desconhecida, sem impor limite às
    consultas temporais. A classe não presume que o fundador seja membro.

    ``emblem`` é uma descrição textual do símbolo, não uma imagem ou URL.
    ``custom_attributes`` aceita dados JSON aninhados e é imutável até nos
    níveis internos. Para alterar dados, use ``dataclasses.replace``.
    """

    name: str
    type: OrganizationType = OrganizationType.ORGANIZATION
    founder_id: UUID | None = None
    founded_year: int | None = None
    dissolved_year: int | None = None
    headquarters: str | None = None
    motto: str | None = None
    emblem: str | None = None
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        _uuid(self.id, "id")
        if self.founder_id is not None:
            _uuid(self.founder_id, "founder_id")
        if not isinstance(self.type, OrganizationType):
            raise TypeError("type deve ser um OrganizationType.")

        object.__setattr__(self, "name", _required_text(self.name, "name"))
        for name in _OPTIONAL_TEXT_FIELDS:
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))

        _optional_year(self.founded_year, "founded_year")
        _optional_year(self.dissolved_year, "dissolved_year")
        if (
            self.founded_year is not None
            and self.dissolved_year is not None
            and self.dissolved_year < self.founded_year
        ):
            raise ValueError("dissolved_year não pode ser anterior a founded_year.")

        if not isinstance(self.custom_attributes, Mapping):
            raise TypeError("custom_attributes deve ser um mapeamento.")
        object.__setattr__(
            self, "custom_attributes", _freeze_json(self.custom_attributes, set())
        )

    def is_active_at(self, year: int) -> bool:
        """Informa se o ano está no intervalo de existência conhecido.

        Isto não indica se membros específicos permanecem na organização.
        """
        if type(year) is not int:
            raise TypeError("year deve ser um inteiro.")
        return (
            (self.founded_year is None or year >= self.founded_year)
            and (self.dissolved_year is None or year <= self.dissolved_year)
        )

    def to_dict(self) -> dict[str, Any]:
        """Retorna dados próprios da entidade prontos para ``json.dumps``.

        Não altera a versão do JSON de ``Project`` ou ``storage.py``.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type.value,
            "founder_id": str(self.founder_id) if self.founder_id else None,
            "founded_year": self.founded_year,
            "dissolved_year": self.dissolved_year,
            "headquarters": self.headquarters,
            "motto": self.motto,
            "emblem": self.emblem,
            "description": self.description,
            "custom_attributes": _thaw_json(self.custom_attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Organization:
        """Reconstrói uma entidade serializada, sem ignorar chaves estranhas.

        Campos opcionais omitidos recebem padrões. ``id`` e ``name`` são
        obrigatórios para não criar silenciosamente uma nova identidade.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados da organização devem ser um mapeamento.")
        unknown = set(data) - _FIELDS
        if unknown:
            raise ValueError(f"Campos de organização desconhecidos: {unknown!r}.")
        missing = {"id", "name"} - set(data)
        if missing:
            raise ValueError(f"Campos de organização ausentes: {sorted(missing)!r}.")

        values: dict[str, Any] = dict(data)
        values["id"] = _uuid_from_json(values["id"], "id")
        founder = values.get("founder_id")
        values["founder_id"] = (
            _uuid_from_json(founder, "founder_id") if founder is not None else None
        )
        raw_type = values.get("type", OrganizationType.ORGANIZATION.value)
        if not isinstance(raw_type, str):
            raise TypeError("type deve ser uma string no JSON.")
        try:
            values["type"] = OrganizationType(raw_type)
        except ValueError as exc:
            raise ValueError(f"Tipo de organização desconhecido: {raw_type!r}.") from exc
        return cls(**values)

    def __str__(self) -> str:
        return self.name


__all__ = ["OrganizationType", "Organization"]
