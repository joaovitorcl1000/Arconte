"""Características físicas de personagens do Arconte.

Este módulo é independente de ``Character`` e de qualquer interface gráfica.
Permite descrever personagens humanos ou de mundos fictícios sem impor limites
arbitrários de altura, peso, espécie ou aparência.

Uso::

    from character.physical import PhysicalAttributes

    physical = PhysicalAttributes(
        height_m=1.68,
        weight_kg=80,
        hair_color="Ruivo",
        body_type="Baixo e entroncado",
        custom_attributes={"cicatrizes": ["Cicatriz na mão direita"]},
    )

As unidades são **metros** (altura) e **quilogramas** (peso). Campos sem
informação recebem ``None``. Textos vazios são normalizados para ``None``.

``PhysicalAttributes`` é imutável, inclusive em seus atributos personalizados.
Use ``dataclasses.replace()`` para criar uma versão modificada e ``to_dict`` /
``from_dict`` para converter dados JSON. Este módulo, por si só, ainda não
altera ``Character``, ``Editor`` nem os formatos de projeto já existentes.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any


_TEXT_FIELDS = (
    "hair_color",
    "eye_color",
    "skin_tone",
    "body_type",
    "distinctive_features",
    "description",
)
_NUMBER_FIELDS = ("height_m", "weight_kg")
_FIELD_NAMES = frozenset((*_NUMBER_FIELDS, *_TEXT_FIELDS, "custom_attributes"))


def _optional_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string ou None.")
    return value.strip() or None


def _positive_measure(value: float | None, name: str) -> float | None:
    if value is None:
        return None
    if type(value) not in (int, float):
        raise TypeError(f"{name} deve ser um número ou None.")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} deve ser um número finito e positivo.") from exc
    if not isfinite(number) or number <= 0:
        raise ValueError(f"{name} deve ser um número finito e positivo.")
    return number


def _key(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("As chaves dos atributos personalizados devem ser strings.")
    name = value.strip()
    if not name:
        raise ValueError("A chave de um atributo personalizado não pode ser vazia.")
    return name


def _freeze_json(value: Any, seen: set[int]) -> Any:
    """Copia valores compatíveis com JSON para estruturas não modificáveis.

    Dicionários tornam-se ``MappingProxyType``; listas, tuplas. Rejeita ciclos,
    objetos arbitrários e números não finitos, evitando perda de dados ao salvar.
    """
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("Atributos personalizados não aceitam NaN ou infinito.")
        return value

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in seen:
            raise ValueError("Atributos personalizados não podem conter ciclos.")
        seen.add(identity)
        try:
            result: dict[str, Any] = {}
            for raw_key, item in value.items():
                name = _key(raw_key)
                if name in result:
                    raise ValueError(f"Chave duplicada após normalização: {name!r}.")
                result[name] = _freeze_json(item, seen)
            return MappingProxyType(result)
        finally:
            seen.remove(identity)

    if type(value) in (list, tuple):
        identity = id(value)
        if identity in seen:
            raise ValueError("Atributos personalizados não podem conter ciclos.")
        seen.add(identity)
        try:
            return tuple(_freeze_json(item, seen) for item in value)
        finally:
            seen.remove(identity)

    raise TypeError(
        "Atributos personalizados aceitam apenas valores JSON: "
        "texto, número, booleano, null, listas e objetos."
    )


def _thaw_json(value: Any) -> Any:
    """Devolve uma cópia JSON serializável, sem referências ao estado interno."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class PhysicalAttributes:
    """Perfil físico opcional e extensível de um personagem.

    ``height_m`` é a altura em metros e ``weight_kg`` é o peso em quilogramas.
    Valores devem ser positivos e finitos; ``bool`` não é uma medida válida.
    As descrições textuais são livres, inclusive para anatomias não humanas.

    ``custom_attributes`` aceita valores compostos exclusivamente por tipos
    JSON, inclusive listas e objetos aninhados. Internamente são imutáveis:
    para editá-los, crie outro objeto (por exemplo, com ``replace``).
    """

    height_m: float | None = None
    weight_kg: float | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    skin_tone: str | None = None
    body_type: str | None = None
    distinctive_features: str | None = None
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in _NUMBER_FIELDS:
            object.__setattr__(self, name, _positive_measure(getattr(self, name), name))
        for name in _TEXT_FIELDS:
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))

        if not isinstance(self.custom_attributes, Mapping):
            raise TypeError("custom_attributes deve ser um mapeamento.")
        object.__setattr__(
            self,
            "custom_attributes",
            _freeze_json(self.custom_attributes, set()),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte o perfil em um dicionário independente e compatível com JSON."""
        data = {name: getattr(self, name) for name in (*_NUMBER_FIELDS, *_TEXT_FIELDS)}
        data["custom_attributes"] = _thaw_json(self.custom_attributes)
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PhysicalAttributes:
        """Cria um perfil a partir dos dados de ``to_dict`` ou JSON equivalente.

        Campos ausentes recebem o valor padrão. Campos desconhecidos são
        rejeitados para evitar perdas silenciosas de dados ao importar.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados físicos devem ser um mapeamento.")
        invalid = set(data) - _FIELD_NAMES
        if invalid:
            raise ValueError(f"Campos físicos desconhecidos: {invalid!r}.")
        return cls(**data)
