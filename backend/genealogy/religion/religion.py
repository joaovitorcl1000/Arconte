"""Identidade de religiões fictícias no Arconte (Python 3.10+).

Uma religião representa crenças e tradições, NÃO uma ordem/templo nem uma
organização de personagens. ``founder_id`` e ``parent_religion_id`` são UUIDs
referenciais; a validade do segundo é controlada por ReligionRegistry. A
existência do fundador em Genealogy será conferida na futura integração com
Project. Nenhum campo cria afiliações automaticamente.

Entidade imutável, anos inteiros (inclusive negativos), JSON independente.
Não altera o formato de Project/storage até a fase de integração.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4


class ReligionType(str, Enum):
    MONOTHEISTIC = "monotheistic"
    POLYTHEISTIC = "polytheistic"
    HENOTHEISTIC = "henotheistic"
    ANIMISTIC = "animistic"
    PANTHEISTIC = "pantheistic"
    NON_THEISTIC = "non_theistic"
    PHILOSOPHICAL = "philosophical"
    OTHER = "other"


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string.")
    value = value.strip()
    if not value:
        raise ValueError(f"{name} não pode estar vazio.")
    return value


def _optional_text(value: Any, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser string ou None.")
    return value.strip() or None


def _optional_year(value: Any, name: str) -> None:
    if value is not None and type(value) is not int:
        raise TypeError(f"{name} deve ser um inteiro ou None.")


def _uuid(value: Any, name: str) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{name} deve ser UUID.")


def _json_uuid(value: Any, name: str) -> UUID:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string UUID no JSON.")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{name} não é um UUID válido.") from exc
    if str(parsed) != value:
        raise ValueError(f"{name} deve ser um UUID canônico.")
    return parsed


def _text_sequence(value: Any, name: str) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise TypeError(f"{name} deve ser lista ou tupla de strings.")
    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item = _required_text(item, f"{name}[{index}]")
        normalized = item.casefold()
        if normalized in seen:
            raise ValueError(f"{name} não aceita valores repetidos.")
        seen.add(normalized)
        result.append(item)
    return tuple(result)


def _freeze_json(value: Any, ancestors: set[int]) -> Any:
    """Copia dados compatíveis com JSON e os torna profundamente imutáveis."""
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("custom_attributes não aceita NaN ou infinito.")
        return value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("custom_attributes não aceita referências circulares.")
        ancestors.add(identity)
        try:
            result: dict[str, Any] = {}
            for key, item in value.items():
                key = _required_text(key, "Chave de custom_attributes")
                if key in result:
                    raise ValueError(f"Chave duplicada em custom_attributes: {key}.")
                result[key] = _freeze_json(item, ancestors)
            return MappingProxyType(result)
        finally:
            ancestors.remove(identity)
    if type(value) in (list, tuple):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("custom_attributes não aceita referências circulares.")
        ancestors.add(identity)
        try:
            return tuple(_freeze_json(item, ancestors) for item in value)
        finally:
            ancestors.remove(identity)
    raise TypeError("custom_attributes só aceita tipos JSON (sem objetos Python arbitrários).")


def _custom(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("custom_attributes deve ser um mapeamento.")
    return _freeze_json(value, set())


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _parse_mapping(data: Any, name: str, allowed: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(data, Mapping):
        raise TypeError(f"Os dados de {name} devem ser um mapeamento.")
    extras = set(data) - allowed
    missing = required - set(data)
    if extras:
        raise ValueError(f"Campos desconhecidos de {name}: {sorted(extras, key=str)}.")
    if missing:
        raise ValueError(f"Campos ausentes de {name}: {sorted(missing)}.")
    return dict(data)


@dataclass(frozen=True, slots=True, kw_only=True)
class Religion:
    """Tradição de crenças com identidade e cronologia próprias.

    ``parent_religion_id`` permite representar uma reforma/cisma; o registro
    verifica a existência de origem e impede ciclos. ``None`` em datas
    significa data desconhecida, não prova de existência eterna.
    """
    name: str
    type: ReligionType = ReligionType.OTHER
    founder_id: UUID | None = None
    parent_religion_id: UUID | None = None
    founded_year: int | None = None
    ended_year: int | None = None
    origin_place: str | None = None
    scriptures: tuple[str, ...] = field(default_factory=tuple)
    traditions: tuple[str, ...] = field(default_factory=tuple)
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        _uuid(self.id, "id")
        for name in ("founder_id", "parent_religion_id"):
            value = getattr(self, name)
            if value is not None:
                _uuid(value, name)
        if self.parent_religion_id == self.id:
            raise ValueError("Uma religião não pode ser sua própria origem.")
        if not isinstance(self.type, ReligionType):
            raise TypeError("type deve ser ReligionType.")
        object.__setattr__(self, "name", _required_text(self.name, "name"))
        for name in ("origin_place", "description"):
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))
        for name in ("scriptures", "traditions"):
            object.__setattr__(self, name, _text_sequence(getattr(self, name), name))
        _optional_year(self.founded_year, "founded_year")
        _optional_year(self.ended_year, "ended_year")
        if self.founded_year is not None and self.ended_year is not None and self.ended_year < self.founded_year:
            raise ValueError("ended_year não pode ser anterior a founded_year.")
        object.__setattr__(self, "custom_attributes", _custom(self.custom_attributes))

    def is_active_at(self, year: int) -> bool:
        _optional_year(year, "year")
        if year is None:
            raise TypeError("year deve ser um inteiro.")
        return ((self.founded_year is None or year >= self.founded_year)
                and (self.ended_year is None or year <= self.ended_year))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id), "name": self.name, "type": self.type.value,
            "founder_id": str(self.founder_id) if self.founder_id else None,
            "parent_religion_id": str(self.parent_religion_id) if self.parent_religion_id else None,
            "founded_year": self.founded_year, "ended_year": self.ended_year,
            "origin_place": self.origin_place, "scriptures": list(self.scriptures),
            "traditions": list(self.traditions), "description": self.description,
            "custom_attributes": _thaw_json(self.custom_attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Religion:
        allowed = set(cls.__dataclass_fields__)
        values = _parse_mapping(data, "religion", allowed, {"id", "name"})
        values["id"] = _json_uuid(values["id"], "id")
        for name in ("founder_id", "parent_religion_id"):
            if values.get(name) is not None:
                values[name] = _json_uuid(values[name], name)
        raw_type = values.get("type", ReligionType.OTHER.value)
        if not isinstance(raw_type, str):
            raise TypeError("type deve ser string no JSON.")
        try:
            values["type"] = ReligionType(raw_type)
        except ValueError as exc:
            raise ValueError(f"Tipo de religião desconhecido: {raw_type!r}.") from exc
        return cls(**values)

    def __str__(self) -> str:
        return self.name


__all__ = ["ReligionType", "Religion"]
