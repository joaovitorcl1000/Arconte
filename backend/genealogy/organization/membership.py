"""Vínculos históricos entre personagens e organizações do Arconte.

Um personagem pode participar de muitas organizações e exercer múltiplas
funções (simultâneas ou sucessivas). O vínculo é uma entidade imutável,
independente das famílias e dos parentescos.

As datas (inteiros, inclusive negativos) são inclusivas. ``None`` significa
que o limite do período é desconhecido, e não que houve filiação perpétua.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID, uuid4


_FIELDS = frozenset({
    "id", "organization_id", "character_id", "role", "rank", "start_year",
    "end_year", "notes",
})
_REQUIRED_FIELDS = frozenset({"id", "organization_id", "character_id"})


def _uuid(value: Any, label: str) -> UUID:
    if not isinstance(value, UUID):
        raise TypeError(f"{label} deve ser um UUID.")
    return value


def _text(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{label} deve ser uma string ou None.")
    return value.strip() or None


def _year(value: int | None, label: str) -> None:
    if value is not None and type(value) is not int:
        raise TypeError(f"{label} deve ser um inteiro ou None.")


def _uuid_from_json(value: Any, label: str) -> UUID:
    if not isinstance(value, str):
        raise TypeError(f"{label} deve ser uma string UUID no JSON.")
    try:
        return UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{label} não é um UUID válido.") from exc


@dataclass(frozen=True, slots=True, kw_only=True)
class OrganizationMembership:
    """Afiliação de um personagem a uma organização (não a uma família).

    ``role`` descreve a função (ex.: sumo-sacerdote, cavaleiro, tesoureiro).
    ``rank`` descreve um grau hierárquico, quando aplicável (ex.: mestre).
    Se um personagem muda de cargo, preserve o histórico criando um novo
    vínculo com outro período. Vários cargos simultâneos são permitidos.

    Um ``organization_id`` ou ``character_id`` válido não prova a existência
    das entidades correspondentes: essa validação cabe a OrganizationRegistry.
    """

    organization_id: UUID
    character_id: UUID
    role: str | None = None
    rank: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    notes: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        for label in ("id", "organization_id", "character_id"):
            _uuid(getattr(self, label), label)
        for label in ("role", "rank", "notes"):
            object.__setattr__(self, label, _text(getattr(self, label), label))
        _year(self.start_year, "start_year")
        _year(self.end_year, "end_year")
        if (
            self.start_year is not None
            and self.end_year is not None
            and self.end_year < self.start_year
        ):
            raise ValueError("end_year não pode ser anterior a start_year.")

    def is_active_at(self, year: int) -> bool:
        """Indica se a afiliação compreende um ano conhecido."""
        if type(year) is not int:
            raise TypeError("year deve ser um inteiro.")
        return (
            (self.start_year is None or year >= self.start_year)
            and (self.end_year is None or year <= self.end_year)
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte o vínculo para um objeto JSON independente."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "character_id": str(self.character_id),
            "role": self.role,
            "rank": self.rank,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> OrganizationMembership:
        """Reconstitui o vínculo, rejeitando campos desconhecidos."""
        if not isinstance(data, Mapping):
            raise TypeError("Os dados da afiliação devem ser um mapeamento.")
        missing = _REQUIRED_FIELDS - data.keys()
        extra = data.keys() - _FIELDS
        if missing or extra:
            raise ValueError(
                f"Campos de afiliação ausentes {sorted(missing)} "
                f"ou desconhecidos {sorted(extra)}."
            )
        values = dict(data)
        for label in ("id", "organization_id", "character_id"):
            values[label] = _uuid_from_json(values[label], label)
        return cls(**values)


__all__ = ["OrganizationMembership"]
