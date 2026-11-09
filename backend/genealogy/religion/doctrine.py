"""Doutrinas vinculadas a uma religião fictícia, com período e texto próprios.

Uma doutrina pode ser reformada ou abandonada com o tempo. A classe não exige
consistência teológica entre diferentes doutrinas; essa decisão é do escritor.
A verificação de ``religion_id`` e de seus limites cronológicos pertence ao
ReligionRegistry, não a esta entidade isolada.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from religion.religion import (
    _custom, _json_uuid, _optional_text, _optional_year, _parse_mapping,
    _required_text, _thaw_json, _uuid,
)


class DoctrineCategory(str, Enum):
    COSMOLOGY = "cosmology"
    DIVINITY = "divinity"
    ETHICS = "ethics"
    RITUAL = "ritual"
    AFTERLIFE = "afterlife"
    LAW = "law"
    SOCIAL = "social"
    OTHER = "other"


@dataclass(frozen=True, slots=True, kw_only=True)
class Doctrine:
    """Um ensinamento em determinada religião e período histórico."""
    religion_id: UUID
    title: str
    content: str
    category: DoctrineCategory = DoctrineCategory.OTHER
    start_year: int | None = None
    end_year: int | None = None
    notes: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        _uuid(self.id, "id")
        _uuid(self.religion_id, "religion_id")
        object.__setattr__(self, "title", _required_text(self.title, "title"))
        object.__setattr__(self, "content", _required_text(self.content, "content"))
        if not isinstance(self.category, DoctrineCategory):
            raise TypeError("category deve ser DoctrineCategory.")
        _optional_year(self.start_year, "start_year")
        _optional_year(self.end_year, "end_year")
        if self.start_year is not None and self.end_year is not None and self.end_year < self.start_year:
            raise ValueError("end_year não pode ser anterior a start_year.")
        object.__setattr__(self, "notes", _optional_text(self.notes, "notes"))
        object.__setattr__(self, "custom_attributes", _custom(self.custom_attributes))

    def is_active_at(self, year: int) -> bool:
        _optional_year(year, "year")
        if year is None:
            raise TypeError("year deve ser um inteiro.")
        return ((self.start_year is None or year >= self.start_year)
                and (self.end_year is None or year <= self.end_year))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id), "religion_id": str(self.religion_id),
            "title": self.title, "content": self.content,
            "category": self.category.value, "start_year": self.start_year,
            "end_year": self.end_year, "notes": self.notes,
            "custom_attributes": _thaw_json(self.custom_attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Doctrine:
        values = _parse_mapping(data, "doutrina", set(cls.__dataclass_fields__), {"id", "religion_id", "title", "content"})
        values["id"] = _json_uuid(values["id"], "id")
        values["religion_id"] = _json_uuid(values["religion_id"], "religion_id")
        category = values.get("category", DoctrineCategory.OTHER.value)
        if not isinstance(category, str):
            raise TypeError("category deve ser string no JSON.")
        try:
            values["category"] = DoctrineCategory(category)
        except ValueError as exc:
            raise ValueError(f"Categoria de doutrina desconhecida: {category!r}.") from exc
        return cls(**values)

    def __str__(self) -> str:
        return self.title


__all__ = ["Doctrine", "DoctrineCategory"]
