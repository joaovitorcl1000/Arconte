"""História pessoal de personagens fictícios no Arconte.

Representa a biografia de um personagem (com múltiplos parágrafos) e uma
coleção de acontecimentos de sua vida. Cada acontecimento tem identidade
estável (UUID), título obrigatório, ano opcional, categoria e descrição.

O ano é um inteiro do calendário *do mundo criado pelo autor*: pode ser
negativo, zero ou positivo; o módulo não presume o calendário gregoriano.
Eventos sem data são válidos. As datas de nascimento/falecimento oficiais
continuam pertencendo a ``Character``; eventos aqui são registros narrativos,
não relações familiares nem mudanças automáticas de estado.

As classes são imutáveis e independentes de ``Character``, ``Editor`` e JSON
de projetos: ``to_dict``/``from_dict`` serializam somente este componente.
Use ``dataclasses.replace`` para editar informações e ``chronological_events``
para obter uma visualização ordenada sem modificar a ordem de cadastro.

Exemplo::

    from character.history import CharacterHistory, HistoryEvent

    historia = CharacterHistory(
        biography="Eilidh ÓCuillan foi a pacificadora dos Hauck.\n\n"
                  "Morreu no parto de Sofia.",
        events=[
            HistoryEvent(title="Morte de Eilidh", year=48,
                         category="Falecimento", description="Parto de Sofia."),
            HistoryEvent(title="Casamento com Boros"),
        ],
    )

Compatível com Python 3.10+, sem dependências externas.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4

_EVENT_FIELDS = frozenset({"id", "title", "year", "category", "description"})
_HISTORY_FIELDS = frozenset({"biography", "events", "custom_attributes"})


def _optional_text(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string ou None.")
    return value.strip() or None


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string.")
    result = value.strip()
    if not result:
        raise ValueError(f"{name} não pode estar vazio.")
    return result


def _year(value: int | None) -> int | None:
    if value is not None and type(value) is not int:
        raise TypeError("year deve ser um inteiro ou None (booleanos não são anos).")
    return value


def _key(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("As chaves dos atributos personalizados devem ser strings.")
    result = value.strip()
    if not result:
        raise ValueError("A chave de um atributo personalizado não pode ser vazia.")
    return result


def _freeze_json(value: Any, seen: set[int]) -> Any:
    """Copia recursivamente dados JSON, tornando-os imutáveis e sem ciclos."""
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
                key = _key(raw_key)
                if key in result:
                    raise ValueError(f"Chave duplicada após normalização: {key!r}.")
                result[key] = _freeze_json(item, seen)
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
    """Produz dados JSON independentes dos objetos imutáveis internos."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoryEvent:
    """Acontecimento narrativo, com identidade estável para edição futura.

    Um evento não altera automaticamente personagens, relações de parentesco,
    afiliações familiares nem datas oficiais de nascimento e falecimento.
    """

    title: str
    year: int | None = None
    category: str | None = None
    description: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise TypeError("id deve ser um UUID.")
        object.__setattr__(self, "title", _required_text(self.title, "title"))
        object.__setattr__(self, "year", _year(self.year))
        for name in ("category", "description"):
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))

    def to_dict(self) -> dict[str, Any]:
        """Exporta uma representação compatível com JSON."""
        return {
            "id": str(self.id),
            "title": self.title,
            "year": self.year,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> HistoryEvent:
        """Importa um evento; rejeita campos desconhecidos e UUIDs inválidos.

        O ``id`` pode ser omitido em uma importação nova e será gerado; quando
        estiver presente deve ser uma string UUID canônica (não um objeto UUID).
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados do evento devem ser um mapeamento.")
        unknown = set(data) - _EVENT_FIELDS
        if unknown:
            raise ValueError(f"Campos do evento desconhecidos: {unknown!r}.")
        kwargs = dict(data)
        if "id" in kwargs:
            raw_id = kwargs["id"]
            if not isinstance(raw_id, str):
                raise TypeError("O id do evento no JSON deve ser uma string UUID.")
            try:
                parsed = UUID(raw_id)
            except (ValueError, AttributeError) as exc:
                raise ValueError("O id do evento não é um UUID válido.") from exc
            if str(parsed) != raw_id:
                raise ValueError("O id do evento deve estar no formato UUID canônico.")
            kwargs["id"] = parsed
        return cls(**kwargs)


@dataclass(frozen=True, slots=True, kw_only=True)
class CharacterHistory:
    """Biografia e acontecimentos de um personagem, sem dependência de outras entidades.

    Os eventos preservam a ordem de cadastro; ``chronological_events`` oferece
    uma visão ordenada por ano, mantendo eventos sem data ao final. Anos iguais
    mantêm a ordem original (ordenação estável).

    Os campos personalizados seguem o mesmo contrato de imutabilidade e JSON
    usado pelos módulos ``physical``, ``personality`` e ``social``.
    """

    biography: str | None = None
    events: tuple[HistoryEvent, ...] = field(default_factory=tuple)
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "biography", _optional_text(self.biography, "biography"))
        if type(self.events) not in (list, tuple):
            raise TypeError("events deve ser uma lista ou tupla de HistoryEvent.")
        ids: set[UUID] = set()
        events: list[HistoryEvent] = []
        for index, event in enumerate(self.events):
            if not isinstance(event, HistoryEvent):
                raise TypeError(f"events[{index}] deve ser um HistoryEvent.")
            if event.id in ids:
                raise ValueError(f"ID de evento duplicado: {event.id}.")
            ids.add(event.id)
            events.append(event)
        object.__setattr__(self, "events", tuple(events))

        if not isinstance(self.custom_attributes, Mapping):
            raise TypeError("custom_attributes deve ser um mapeamento.")
        object.__setattr__(
            self, "custom_attributes", _freeze_json(self.custom_attributes, set())
        )

    def chronological_events(self) -> tuple[HistoryEvent, ...]:
        """Eventos em ordem temporal; acontecimentos sem data ficam por último."""
        return tuple(sorted(
            self.events,
            key=lambda event: (event.year is None,
                               event.year if event.year is not None else 0),
        ))

    def to_dict(self) -> dict[str, Any]:
        """Dicionário independente, serializável com ``json.dumps``."""
        return {
            "biography": self.biography,
            "events": [event.to_dict() for event in self.events],
            "custom_attributes": _thaw_json(self.custom_attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CharacterHistory:
        """Reconstrói uma ficha, aplicando valores padrão a campos omitidos.

        Não ignora campos inesperados, evitando perdas silenciosas de dados.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Os dados históricos devem ser um mapeamento.")
        unknown = set(data) - _HISTORY_FIELDS
        if unknown:
            raise ValueError(f"Campos históricos desconhecidos: {unknown!r}.")
        kwargs = dict(data)
        if "events" in kwargs:
            raw_events = kwargs["events"]
            if type(raw_events) not in (list, tuple):
                raise TypeError("events deve ser uma lista ou tupla de eventos.")
            kwargs["events"] = [HistoryEvent.from_dict(event) for event in raw_events]
        return cls(**kwargs)
