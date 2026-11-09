"""Perfil psicológico de personagens do Arconte.

Este módulo é independente de ``Character`` e da interface do editor.  Um
perfil contém listas ordenadas de traços, virtudes, defeitos, ambições, medos
e desejos, além de uma descrição livre e atributos personalizados.

Exemplo::

    from character.personality import PersonalityProfile

    artuin = PersonalityProfile(
        traits=["Arrogante", "Manipulador"],
        flaws=["Crueldade"],
        ambitions=["Expandir seu poder político"],
        description="Sabe convencer os lordes, mas teme perder influência.",
        custom_attributes={"postura_em_publico": "Cortês e persuasivo"},
    )

Os campos estruturados são armazenados como tuplas imutáveis, preservando a
ordem de inclusão. Textos são normalizados removendo espaços apenas nas
extremidades. O texto de ``description`` admite múltiplos parágrafos.

``custom_attributes`` aceita dados aninhados compatíveis com JSON (sem ciclos,
NaN ou infinito) e é copiado profundamente para estruturas imutáveis. Use
``dataclasses.replace()`` para alterar um perfil. ``to_dict()`` e
``from_dict()`` permitem serialização futura, mas não alteram, por si só,
``Character``, ``Editor`` ou o formato atual dos projetos JSON.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any


_LIST_FIELDS = ("traits", "virtues", "flaws", "ambitions", "fears", "desires")
_FIELD_NAMES = frozenset((*_LIST_FIELDS, "description", "custom_attributes"))


def _optional_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string ou None.")
    return value.strip() or None


def _text_items(value: list[str] | tuple[str, ...], name: str) -> tuple[str, ...]:
    """Valida uma lista de descritores sem alterar o objeto de entrada."""
    if type(value) not in (list, tuple):
        raise TypeError(f"{name} deve ser uma lista ou tupla de strings.")

    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise TypeError(f"{name}[{index}] deve ser uma string.")
        normalized = item.strip()
        if not normalized:
            raise ValueError(f"{name}[{index}] não pode estar vazio.")
        result.append(normalized)
    return tuple(result)


def _key(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("As chaves dos atributos personalizados devem ser strings.")
    name = value.strip()
    if not name:
        raise ValueError("A chave de um atributo personalizado não pode ser vazia.")
    return name


def _freeze_json(value: Any, seen: set[int]) -> Any:
    """Copia recursivamente dados JSON, tornando objetos e listas imutáveis."""
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
    """Produz uma nova estrutura JSON sem compartilhar dados mutáveis."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class PersonalityProfile:
    """Características psicológicas opcionais e extensíveis de um personagem.

    ``traits``, ``virtues``, ``flaws``, ``ambitions``, ``fears`` e ``desires``
    aceitam listas/tuplas de textos não vazios e são normalizados para tuplas.
    A mesma expressão pode aparecer mais de uma vez se o autor desejar; o
    módulo preserva a ordem e não interpreta semanticamente os descritores.

    O perfil é imutável e pode existir independentemente de um personagem.
    """

    traits: tuple[str, ...] = ()
    virtues: tuple[str, ...] = ()
    flaws: tuple[str, ...] = ()
    ambitions: tuple[str, ...] = ()
    fears: tuple[str, ...] = ()
    desires: tuple[str, ...] = ()
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in _LIST_FIELDS:
            object.__setattr__(self, name, _text_items(getattr(self, name), name))
        object.__setattr__(self, "description", _optional_text(self.description, "description"))

        if not isinstance(self.custom_attributes, Mapping):
            raise TypeError("custom_attributes deve ser um mapeamento.")
        object.__setattr__(self, "custom_attributes", _freeze_json(self.custom_attributes, set()))

    def to_dict(self) -> dict[str, Any]:
        """Devolve uma cópia JSON serializável (as tuplas viram listas)."""
        data: dict[str, Any] = {name: list(getattr(self, name)) for name in _LIST_FIELDS}
        data["description"] = self.description
        data["custom_attributes"] = _thaw_json(self.custom_attributes)
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PersonalityProfile:
        """Reconstrói um perfil e rejeita campos desconhecidos.

        Campos ausentes usam os padrões vazios. Rejeitar chaves inesperadas
        evita perder informações silenciosamente ao importar um projeto.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados de personalidade devem ser um mapeamento.")
        unknown = set(data) - _FIELD_NAMES
        if unknown:
            raise ValueError(f"Campos de personalidade desconhecidos: {unknown!r}.")
        return cls(**data)
