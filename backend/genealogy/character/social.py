"""Perfil social de personagens do Arconte.

Guarda informações **individuais** sobre a posição social de um personagem:
título, ocupação, residência, nacionalidade, religião, condição social e
uma descrição livre. Também aceita atributos personalizados para diferentes
mundos fictícios.

Exemplo::

    from character.social import SocialProfile

    artuin = SocialProfile(
        title="Conde da Sarnília",
        occupation="Governante do condado",
        residence="Castelo no Morro do Falcão",
        social_status="Nobreza",
        custom_attributes={"jurisdição": "Sarnília"},
    )

IMPORTANTE: este módulo **não** registra filiações à Casa Hauck, a clãs ou a
outras famílias: isso é feito pelo ``FamilyRegistry``. Também não registra
parentescos, que pertencem a ``Genealogy``. As strings desta ficha são
informações descritivas, não referências a entidades dessas estruturas.

A classe é imutável; use ``dataclasses.replace`` para criar uma nova versão.
O campo ``description`` admite múltiplos parágrafos. Os atributos personalizados
aceitam somente valores compatíveis com JSON e são copiados para estruturas
imutáveis (com rejeição de ciclos e números não finitos). ``to_dict`` e
``from_dict`` permitem serialização, mas esta etapa **não altera** o esquema
JSON de projetos nem a classe ``Character`` ou o editor.

Compatível com Python 3.10 ou superior; não requer dependências externas.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any


_TEXT_FIELDS = (
    "title",
    "occupation",
    "residence",
    "nationality",
    "religion",
    "social_status",
    "description",
)
_FIELD_NAMES = frozenset((*_TEXT_FIELDS, "custom_attributes"))


def _optional_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string ou None.")
    return value.strip() or None


def _key(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("As chaves dos atributos personalizados devem ser strings.")
    normalized = value.strip()
    if not normalized:
        raise ValueError("A chave de um atributo personalizado não pode ser vazia.")
    return normalized


def _freeze_json(value: Any, seen: set[int]) -> Any:
    """Copia valores JSON para tuplas e mapeamentos somente leitura.

    ``seen`` contém apenas os ancestrais do ramo atual: uma mesma lista ou
    dicionário pode ser utilizada em dois locais distintos sem formar ciclo.
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
                normalized = _key(raw_key)
                if normalized in result:
                    raise ValueError(f"Chave duplicada após normalização: {normalized!r}.")
                result[normalized] = _freeze_json(item, seen)
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
    """Devolve estruturas JSON independentes, sem objetos compartilhados."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class SocialProfile:
    """Conjunto opcional de atributos sociais de um personagem.

    Todos os textos são opcionais, livres e normalizados com ``strip()``.
    Campos não informados tornam-se ``None``. Para informações adicionais,
    utilize ``custom_attributes`` com chaves textuais e valores JSON.

    Uma ``residence`` é apenas uma descrição de moradia; ``title`` não gera
    automaticamente uma casa nobre, e ``social_status`` não equivale a uma
    afiliação familiar. Esses vínculos permanecem em seus módulos próprios.
    """

    title: str | None = None
    occupation: str | None = None
    residence: str | None = None
    nationality: str | None = None
    religion: str | None = None
    social_status: str | None = None
    description: str | None = None
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in _TEXT_FIELDS:
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))

        if not isinstance(self.custom_attributes, Mapping):
            raise TypeError("custom_attributes deve ser um mapeamento.")
        object.__setattr__(
            self, "custom_attributes", _freeze_json(self.custom_attributes, set())
        )

    def to_dict(self) -> dict[str, Any]:
        """Representa todos os campos como um dicionário pronto para JSON."""
        data: dict[str, Any] = {name: getattr(self, name) for name in _TEXT_FIELDS}
        data["custom_attributes"] = _thaw_json(self.custom_attributes)
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SocialProfile:
        """Reconstrói uma ficha sem ignorar silenciosamente campos inesperados.

        Campos omitidos recebem seus padrões opcionais. Uma versão futura do
        formato poderá fazer migrações explícitas antes de chamar este método.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados sociais devem ser um mapeamento.")
        unknown = set(data) - _FIELD_NAMES
        if unknown:
            raise ValueError(f"Campos sociais desconhecidos: {unknown!r}.")
        return cls(**data)
