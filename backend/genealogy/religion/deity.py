"""Divindades e entidades mitológicas descritas em mundos fictícios.

Uma divindade não pertence obrigatoriamente a uma só religião. As associações
com religiões são registradas em ``religion.registry``, sem modificar Deity.
Também não se presume que a entidade exista de fato dentro do mundo.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from religion.religion import (
    _custom, _json_uuid, _optional_text, _parse_mapping, _required_text,
    _text_sequence, _thaw_json, _uuid,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Deity:
    """Registro neutro de uma divindade, espírito ou entidade reverenciada."""
    name: str
    epithets: tuple[str, ...] = field(default_factory=tuple)
    domains: tuple[str, ...] = field(default_factory=tuple)
    symbols: tuple[str, ...] = field(default_factory=tuple)
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        _uuid(self.id, "id")
        object.__setattr__(self, "name", _required_text(self.name, "name"))
        for name in ("epithets", "domains", "symbols"):
            object.__setattr__(self, name, _text_sequence(getattr(self, name), name))
        object.__setattr__(self, "description", _optional_text(self.description, "description"))
        object.__setattr__(self, "custom_attributes", _custom(self.custom_attributes))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id), "name": self.name, "epithets": list(self.epithets),
            "domains": list(self.domains), "symbols": list(self.symbols),
            "description": self.description,
            "custom_attributes": _thaw_json(self.custom_attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Deity:
        values = _parse_mapping(data, "divindade", set(cls.__dataclass_fields__), {"id", "name"})
        values["id"] = _json_uuid(values["id"], "id")
        return cls(**values)

    def __str__(self) -> str:
        return self.name


__all__ = ["Deity"]
