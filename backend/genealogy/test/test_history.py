"""Testes de ``character.history`` do Arconte.

Na pasta ``backend/genealogy``::

    python3 -m pytest test/test_history.py -v

Um único arquivo de testes do módulo; nenhum dado pessoal é escrito no disco.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import json
from types import MappingProxyType
from uuid import UUID, uuid4

import pytest

from character.history import CharacterHistory, HistoryEvent


@pytest.fixture
def morte_eilidh() -> HistoryEvent:
    return HistoryEvent(
        title="Morte de Eilidh ÓCuillan Hauck",
        year=48,
        category="Falecimento",
        description="Morreu aos 42 anos durante o parto de Sofia.",
    )


@pytest.fixture
def historia_eilidh(morte_eilidh) -> CharacterHistory:
    return CharacterHistory(
        biography=(
            "Eilidh ÓCuillan Hauck foi a pacificadora da Casa Hauck.\n\n"
            "Amada pelos vassalos, morreu no parto de Sofia."
        ),
        events=[HistoryEvent(title="Casamento com Boros"), morte_eilidh],
        custom_attributes={"fontes": ["Crônicas da Sarnília"], "era": "d.U."},
    )


def test_empty_character_history():
    history = CharacterHistory()
    assert history.biography is None
    assert history.events == ()
    assert dict(history.custom_attributes) == {}


def test_history_expected_fields():
    assert {f.name for f in fields(CharacterHistory)} == {
        "biography", "events", "custom_attributes"
    }


def test_event_expected_fields():
    assert {f.name for f in fields(HistoryEvent)} == {
        "title", "year", "category", "description", "id"
    }


def test_keyword_only_constructors():
    with pytest.raises(TypeError):
        HistoryEvent("Nascimento")
    with pytest.raises(TypeError):
        CharacterHistory("Biografia")


def test_history_of_eilidh_uses_original_fictional_calendar(historia_eilidh):
    assert "pacificadora" in historia_eilidh.biography
    assert "\n\n" in historia_eilidh.biography
    assert historia_eilidh.events[1].year == 48
    assert historia_eilidh.events[1].category == "Falecimento"


def test_artuin_fictional_biography():
    history = CharacterHistory(
        biography="Artuin governa Sarnília.\n\nÉ ambicioso e manipulador.",
        events=[HistoryEvent(title="Nascimento de Artuin", year=31)],
    )
    assert history.events[0].year == 31
    assert "manipulador" in history.biography


def test_aioria_history_can_have_biography_only():
    history = CharacterHistory(biography="Aioria é valente e honrado.")
    assert history.events == ()


def test_sofia_birth_and_mothers_death_are_separate_records():
    history = CharacterHistory(
        events=[HistoryEvent(title="Nascimento de Sofia", year=48)]
    )
    assert history.events[0].title == "Nascimento de Sofia"
    assert len(history.events) == 1


def test_undated_event_is_supported():
    event = HistoryEvent(title="Casamento de Artuin e Ayla")
    assert event.year is None
    assert event.category is None
    assert event.description is None


def test_events_do_not_claim_to_change_canonical_character_dates():
    history = CharacterHistory(events=[HistoryEvent(title="Morte fictícia", year=67)])
    assert not hasattr(history, "death_year")
    assert not hasattr(history, "birth_year")
    assert not hasattr(history, "character_id")
    assert not hasattr(history, "family_id")
    assert not hasattr(history, "parents")
    assert not hasattr(history, "memberships")


@pytest.mark.parametrize("value", [None, "", "   ", "\n\t  "])
def test_empty_biography_becomes_none(value):
    assert CharacterHistory(biography=value).biography is None


@pytest.mark.parametrize("value", [0, 12, 1.2, True, False, [], {}, (), b"abc", object()])
def test_biography_rejects_non_strings(value):
    with pytest.raises(TypeError):
        CharacterHistory(biography=value)


def test_biography_preserves_interior_line_breaks():
    history = CharacterHistory(biography=" \n Primeiro parágrafo.\n\nSegundo parágrafo. \n")
    assert history.biography == "Primeiro parágrafo.\n\nSegundo parágrafo."


def test_biography_preserves_accents_and_emojis():
    history = CharacterHistory(biography="ÓFiachra, ÓCuillan e Sarnília 🦅")
    assert history.biography.endswith("Sarnília 🦅")


@pytest.mark.parametrize("value", [None, "", " \n ", "\t"])
def test_event_title_must_not_be_empty(value):
    with pytest.raises((TypeError, ValueError)):
        HistoryEvent(title=value)


@pytest.mark.parametrize("value", [0, 1.5, True, False, [], {}, (), b"x", object()])
def test_event_title_must_be_string(value):
    with pytest.raises(TypeError):
        HistoryEvent(title=value)


def test_event_title_is_trimmed():
    assert HistoryEvent(title="  Fundação da Sarnília  ").title == "Fundação da Sarnília"


def test_event_title_can_contain_internal_newlines():
    event = HistoryEvent(title=" Primeiro\nSegundo ")
    assert event.title == "Primeiro\nSegundo"


@pytest.mark.parametrize("value", [-300, -1, 0, 1, 31, 48, 67, 10**12])
def test_event_accepts_any_fictional_integer_year(value):
    assert HistoryEvent(title="Evento", year=value).year == value


@pytest.mark.parametrize("value", [True, False, 1.0, 2.4, "67", "-1", [], {}, (), b"67"])
def test_event_rejects_non_integer_year(value):
    with pytest.raises(TypeError):
        HistoryEvent(title="Evento", year=value)


@pytest.mark.parametrize("name", ["category", "description"])
@pytest.mark.parametrize("value", [None, "", "  ", "\n\t"])
def test_optional_event_text_normalizes_empty_to_none(name, value):
    assert getattr(HistoryEvent(title="X", **{name: value}), name) is None


@pytest.mark.parametrize("name", ["category", "description"])
@pytest.mark.parametrize("value", [0, 1.1, True, False, [], {}, (), b"x", object()])
def test_optional_event_text_rejects_non_string(name, value):
    with pytest.raises(TypeError):
        HistoryEvent(title="X", **{name: value})


@pytest.mark.parametrize("name", ["category", "description"])
def test_optional_event_text_strips_only_outer_whitespace(name):
    event = HistoryEvent(title="X", **{name: "  Um\n\nDois  "})
    assert getattr(event, name) == "Um\n\nDois"


def test_event_can_have_multiline_description():
    event = HistoryEvent(title="Rebelião", description="Primeiro.\n\nSegundo.")
    assert event.description == "Primeiro.\n\nSegundo."


def test_events_get_different_uuid_by_default():
    a = HistoryEvent(title="Evento")
    b = HistoryEvent(title="Evento")
    assert isinstance(a.id, UUID)
    assert isinstance(b.id, UUID)
    assert a.id != b.id


def test_event_accepts_explicit_uuid():
    identifier = uuid4()
    event = HistoryEvent(title="Evento", id=identifier)
    assert event.id is identifier


@pytest.mark.parametrize("value", ["abc", None, 1, False, b"x", {}, []])
def test_event_constructor_requires_uuid(value):
    with pytest.raises(TypeError):
        HistoryEvent(title="Evento", id=value)


def test_event_is_frozen_slotted():
    event = HistoryEvent(title="Evento")
    assert not hasattr(event, "__dict__")
    with pytest.raises(FrozenInstanceError):
        event.title = "Novo"
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        event.nonexistent = "x"


def test_history_is_frozen_slotted():
    history = CharacterHistory()
    assert not hasattr(history, "__dict__")
    with pytest.raises(FrozenInstanceError):
        history.biography = "Outra"
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        history.nonexistent = 2


def test_dataclasses_replace_event_preserves_uuid():
    old = HistoryEvent(title="Primeira", year=1)
    new = replace(old, title="Segunda")
    assert new.id == old.id
    assert old.title == "Primeira"
    assert new.title == "Segunda"


def test_dataclasses_replace_event_revalidates_fields():
    event = HistoryEvent(title="Evento")
    with pytest.raises(TypeError):
        replace(event, year=True)


def test_dataclasses_replace_history_keeps_original():
    old = CharacterHistory(biography="Original")
    new = replace(old, biography="Outra")
    assert old.biography == "Original"
    assert new.biography == "Outra"


def test_dataclasses_replace_history_revalidates_fields():
    history = CharacterHistory()
    with pytest.raises(TypeError):
        replace(history, events="x")


def test_event_list_is_frozen_into_tuple():
    source = [HistoryEvent(title="Um")]
    history = CharacterHistory(events=source)
    source.append(HistoryEvent(title="Dois"))
    assert len(history.events) == 1
    assert isinstance(history.events, tuple)


def test_event_tuple_is_preserved_as_tuple():
    event = HistoryEvent(title="Um")
    history = CharacterHistory(events=(event,))
    assert history.events == (event,)


@pytest.mark.parametrize("value", [None, 3, True, "x", {}, {1}, b"x", (x for x in [])])
def test_event_collection_requires_list_or_tuple(value):
    with pytest.raises(TypeError):
        CharacterHistory(events=value)


@pytest.mark.parametrize("value", [None, "text", 1, {}, [], (), True])
def test_event_collection_rejects_items_not_history_events(value):
    with pytest.raises(TypeError):
        CharacterHistory(events=[value])


def test_event_collection_rejects_duplicate_ids():
    event = HistoryEvent(title="Evento")
    with pytest.raises(ValueError, match="duplicado"):
        CharacterHistory(events=[event, event])


def test_event_collection_rejects_distinct_events_with_same_id():
    identifier = uuid4()
    with pytest.raises(ValueError, match="duplicado"):
        CharacterHistory(events=[
            HistoryEvent(title="Um", id=identifier),
            HistoryEvent(title="Dois", id=identifier),
        ])


def test_same_event_can_be_used_in_separate_histories():
    event = HistoryEvent(title="Evento")
    first = CharacterHistory(events=[event])
    second = CharacterHistory(events=[event])
    assert first.events == second.events


def test_history_events_preserve_insertion_order():
    history = CharacterHistory(events=[
        HistoryEvent(title="Segundo", year=67),
        HistoryEvent(title="Primeiro", year=31),
    ])
    assert [event.title for event in history.events] == ["Segundo", "Primeiro"]


def test_chronological_events_sorts_ascending_years_without_mutating_history():
    history = CharacterHistory(events=[
        HistoryEvent(title="67", year=67),
        HistoryEvent(title="desconhecido"),
        HistoryEvent(title="31", year=31),
        HistoryEvent(title="48", year=48),
    ])
    result = history.chronological_events()
    assert [e.title for e in result] == ["31", "48", "67", "desconhecido"]
    assert [e.title for e in history.events] == ["67", "desconhecido", "31", "48"]


def test_chronological_events_keep_negative_and_zero_years():
    history = CharacterHistory(events=[
        HistoryEvent(title="Zero", year=0),
        HistoryEvent(title="Antes da Unificação", year=-1),
    ])
    assert [e.year for e in history.chronological_events()] == [-1, 0]


def test_chronological_events_preserve_order_for_same_year():
    history = CharacterHistory(events=[
        HistoryEvent(title="A", year=48),
        HistoryEvent(title="B", year=48),
        HistoryEvent(title="C", year=48),
    ])
    assert [e.title for e in history.chronological_events()] == ["A", "B", "C"]


def test_chronological_events_keep_undated_order():
    history = CharacterHistory(events=[
        HistoryEvent(title="A"),
        HistoryEvent(title="B", year=7),
        HistoryEvent(title="C"),
    ])
    assert [e.title for e in history.chronological_events()] == ["B", "A", "C"]


def test_chronological_events_empty_history():
    assert CharacterHistory().chronological_events() == ()


def test_chronological_events_return_tuple():
    assert isinstance(CharacterHistory(events=[HistoryEvent(title="X")]).chronological_events(), tuple)


def test_default_custom_attributes_are_independent():
    a = CharacterHistory(custom_attributes={"a": [1]})
    b = CharacterHistory()
    assert "a" not in b.custom_attributes


@pytest.mark.parametrize("value", [None, 1, False, [], (), "text", b"x"])
def test_custom_attributes_require_mapping(value):
    with pytest.raises(TypeError):
        CharacterHistory(custom_attributes=value)


@pytest.mark.parametrize("value", [{1: "n"}, {None: "x"}, {True: "yes"}])
def test_custom_attributes_require_string_keys(value):
    with pytest.raises(TypeError):
        CharacterHistory(custom_attributes=value)


@pytest.mark.parametrize("value", [{"": 1}, {"  ": 2}, {"\n\t": True}])
def test_custom_attributes_reject_empty_keys(value):
    with pytest.raises(ValueError):
        CharacterHistory(custom_attributes=value)


def test_custom_attributes_trim_keys():
    history = CharacterHistory(custom_attributes={"  fonte  ": "crônica"})
    assert history.custom_attributes["fonte"] == "crônica"


def test_custom_attributes_trim_nested_keys():
    history = CharacterHistory(custom_attributes={"fontes": {"  livro  ": 1}})
    assert history.custom_attributes["fontes"]["livro"] == 1


def test_custom_attributes_reject_duplicate_trimmed_keys():
    with pytest.raises(ValueError, match="duplicada"):
        CharacterHistory(custom_attributes={"fonte": 1, " fonte ": 2})


def test_custom_attributes_reject_nested_duplicate_trimmed_keys():
    with pytest.raises(ValueError, match="duplicada"):
        CharacterHistory(custom_attributes={"a": {"foo": 1, " foo": 2}})


def test_custom_attributes_support_json_values():
    history = CharacterHistory(custom_attributes={
        "str": "texto", "int": 3, "float": 3.5, "true": True,
        "false": False, "null": None, "nested": {"itens": [1, {"n": 2}]},
    })
    assert history.custom_attributes["str"] == "texto"
    assert history.custom_attributes["int"] == 3
    assert history.custom_attributes["float"] == 3.5
    assert history.custom_attributes["true"] is True
    assert history.custom_attributes["false"] is False
    assert history.custom_attributes["null"] is None
    assert history.custom_attributes["nested"]["itens"][1]["n"] == 2


def test_custom_attributes_defensive_deep_copy():
    source = {"fontes": ["livro"], "misc": {"page": 1}}
    history = CharacterHistory(custom_attributes=source)
    source["fontes"].append("outro")
    source["misc"]["page"] = 99
    source["extra"] = "x"
    assert history.custom_attributes["fontes"] == ("livro",)
    assert history.custom_attributes["misc"]["page"] == 1
    assert "extra" not in history.custom_attributes


def test_custom_attributes_are_immutable_recursively():
    history = CharacterHistory(custom_attributes={"a": {"b": [1]}})
    assert isinstance(history.custom_attributes, MappingProxyType)
    with pytest.raises(TypeError):
        history.custom_attributes["x"] = 2
    with pytest.raises(TypeError):
        history.custom_attributes["a"]["b"] = 2
    with pytest.raises(AttributeError):
        history.custom_attributes["a"]["b"].append(3)


@pytest.mark.parametrize("value", [object(), set(), complex(1, 2), b"abc"])
def test_custom_attributes_reject_non_json_values(value):
    with pytest.raises(TypeError):
        CharacterHistory(custom_attributes={"x": value})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_custom_attributes_reject_non_finite_numbers(value):
    with pytest.raises(ValueError):
        CharacterHistory(custom_attributes={"nested": [value]})


def test_custom_attributes_reject_self_referencing_list():
    array = []
    array.append(array)
    with pytest.raises(ValueError, match="ciclos"):
        CharacterHistory(custom_attributes={"bad": array})


def test_custom_attributes_reject_self_referencing_dict():
    obj = {}
    obj["self"] = obj
    with pytest.raises(ValueError, match="ciclos"):
        CharacterHistory(custom_attributes=obj)


def test_custom_attributes_reject_indirect_cycles():
    a, b = {}, []
    a["b"] = b
    b.append(a)
    with pytest.raises(ValueError, match="ciclos"):
        CharacterHistory(custom_attributes={"a": a})


def test_shared_non_cyclic_references_are_valid():
    shared = ["Sarnília"]
    history = CharacterHistory(custom_attributes={"a": shared, "b": shared})
    assert history.custom_attributes["a"] == history.custom_attributes["b"]


def test_custom_tuples_convert_to_json_lists():
    history = CharacterHistory(custom_attributes={"x": (1, 2)})
    assert history.custom_attributes["x"] == (1, 2)
    assert history.to_dict()["custom_attributes"]["x"] == [1, 2]


def test_event_to_dict_contains_all_fields():
    event = HistoryEvent(title=" Fundação ", year=0, category="História")
    result = event.to_dict()
    assert result == {
        "id": str(event.id), "title": "Fundação", "year": 0,
        "category": "História", "description": None,
    }


def test_event_to_dict_is_json_serializable(morte_eilidh):
    assert "Morte" in json.loads(json.dumps(morte_eilidh.to_dict(), ensure_ascii=False))["title"]


def test_event_from_dict_round_trip(morte_eilidh):
    data = morte_eilidh.to_dict()
    imported = HistoryEvent.from_dict(json.loads(json.dumps(data)))
    assert imported == morte_eilidh
    assert imported.id == morte_eilidh.id


def test_event_from_dict_can_generate_missing_id():
    event = HistoryEvent.from_dict({"title": "Evento"})
    assert isinstance(event.id, UUID)
    assert event.year is None


def test_event_from_dict_requires_title():
    with pytest.raises(TypeError):
        HistoryEvent.from_dict({"year": 48})


@pytest.mark.parametrize("value", [None, 1, False, "x", [], (), b"x"])
def test_event_from_dict_requires_mapping(value):
    with pytest.raises(TypeError):
        HistoryEvent.from_dict(value)


@pytest.mark.parametrize("key", ["character_id", "family_id", "parents", "birth_year", "irrelevant"])
def test_event_from_dict_rejects_unknown_fields(key):
    with pytest.raises(ValueError, match="desconhecidos"):
        HistoryEvent.from_dict({"title": "X", key: "y"})


@pytest.mark.parametrize("value", [None, 0, True, [], {}, UUID(int=1)])
def test_event_from_dict_rejects_non_string_ids(value):
    with pytest.raises(TypeError):
        HistoryEvent.from_dict({"title": "X", "id": value})


@pytest.mark.parametrize("value", ["", "abc", "0000", "123e4567-e89b-12d3-a456-42661417400x"])
def test_event_from_dict_rejects_invalid_uuid_text(value):
    with pytest.raises(ValueError):
        HistoryEvent.from_dict({"title": "X", "id": value})


def test_event_from_dict_rejects_noncanonical_uuid_uppercase():
    with pytest.raises(ValueError, match="canônico"):
        HistoryEvent.from_dict({"title": "X", "id": str(uuid4()).upper()})


def test_event_from_dict_rejects_noncanonical_uuid_undashed():
    with pytest.raises(ValueError, match="canônico"):
        HistoryEvent.from_dict({"title": "X", "id": uuid4().hex})


def test_event_from_dict_does_not_modify_input():
    data = {"title": "Evento", "year": 31}
    HistoryEvent.from_dict(data)
    assert data == {"title": "Evento", "year": 31}


def test_history_to_dict_default_structure():
    assert CharacterHistory().to_dict() == {
        "biography": None, "events": [], "custom_attributes": {}
    }


def test_history_to_dict_export_ids_as_strings(historia_eilidh):
    data = historia_eilidh.to_dict()
    assert len(data["events"]) == 2
    assert isinstance(data["events"][0]["id"], str)
    assert data["events"][1]["year"] == 48


def test_history_to_dict_round_trip_json(historia_eilidh):
    data = json.loads(json.dumps(historia_eilidh.to_dict(), ensure_ascii=False, allow_nan=False))
    imported = CharacterHistory.from_dict(data)
    assert imported == historia_eilidh
    assert imported.events[0].id == historia_eilidh.events[0].id
    assert imported.biography == historia_eilidh.biography
    assert imported.custom_attributes["fontes"] == ("Crônicas da Sarnília",)


def test_history_to_dict_preserves_unicode(historia_eilidh):
    payload = json.dumps(historia_eilidh.to_dict(), ensure_ascii=False)
    assert "ÓCuillan" in payload
    assert "Sarnília" in payload


def test_history_to_dict_is_independent():
    history = CharacterHistory(custom_attributes={"a": {"b": [1, 2]}})
    data = history.to_dict()
    data["custom_attributes"]["a"]["b"].append(3)
    data["events"].append({"title": "Novo"})
    assert history.custom_attributes["a"]["b"] == (1, 2)
    assert history.events == ()


def test_history_to_dict_does_not_leak_mappingproxy():
    history = CharacterHistory(custom_attributes={"meta": {"fontes": ["A"]}})
    data = history.to_dict()
    assert type(data["custom_attributes"]) is dict
    assert type(data["custom_attributes"]["meta"]) is dict
    assert type(data["custom_attributes"]["meta"]["fontes"]) is list


def test_history_from_dict_allows_empty_mapping():
    assert CharacterHistory.from_dict({}) == CharacterHistory()


def test_history_from_dict_allows_missing_fields():
    history = CharacterHistory.from_dict({"biography": "  Texto  "})
    assert history.biography == "Texto"
    assert history.events == ()


@pytest.mark.parametrize("value", [None, 1, True, "texto", [], (), b"texto"])
def test_history_from_dict_requires_mapping(value):
    with pytest.raises(TypeError):
        CharacterHistory.from_dict(value)


@pytest.mark.parametrize("key", ["id", "name", "birth_year", "death_year", "family_id", "irrelevant"])
def test_history_from_dict_rejects_unknown_fields(key):
    with pytest.raises(ValueError, match="desconhecidos"):
        CharacterHistory.from_dict({key: 1})


@pytest.mark.parametrize("value", [None, True, 1, "x", {}, {1}, (x for x in [])])
def test_history_from_dict_rejects_invalid_events_collection(value):
    with pytest.raises(TypeError):
        CharacterHistory.from_dict({"events": value})


@pytest.mark.parametrize("value", [None, 1, False, "Evento", [], ()])
def test_history_from_dict_rejects_invalid_event_item(value):
    with pytest.raises(TypeError):
        CharacterHistory.from_dict({"events": [value]})


def test_history_from_dict_rejects_duplicate_event_ids():
    item = HistoryEvent(title="Evento").to_dict()
    with pytest.raises(ValueError, match="duplicado"):
        CharacterHistory.from_dict({"events": [item, dict(item)]})


def test_history_from_dict_does_not_modify_input():
    event = HistoryEvent(title="X")
    source = {"events": [event.to_dict()], "custom_attributes": {"x": [1]}}
    snapshot = json.loads(json.dumps(source))
    CharacterHistory.from_dict(source)
    assert source == snapshot


def test_history_from_dict_accepts_tuple_of_event_mappings():
    history = CharacterHistory.from_dict({"events": ({"title": "X"},)})
    assert len(history.events) == 1


def test_serialization_keeps_registration_order():
    history = CharacterHistory(events=[
        HistoryEvent(title="Mais recente", year=67),
        HistoryEvent(title="Mais antigo", year=31),
    ])
    imported = CharacterHistory.from_dict(history.to_dict())
    assert [event.year for event in imported.events] == [67, 31]


def test_dataclasses_replace_history_with_extra_event():
    history = CharacterHistory(events=[HistoryEvent(title="A")])
    added = replace(history, events=[*history.events, HistoryEvent(title="B")])
    assert [e.title for e in added.events] == ["A", "B"]
    assert [e.title for e in history.events] == ["A"]


def test_dataclasses_replace_history_to_remove_event():
    history = CharacterHistory(events=[HistoryEvent(title="A"), HistoryEvent(title="B")])
    removed = replace(history, events=[event for event in history.events if event.title != "A"])
    assert [e.title for e in removed.events] == ["B"]
    assert len(history.events) == 2


def test_dataclasses_replace_event_inside_history_keeps_id():
    original = HistoryEvent(title="Título antigo", year=None)
    history = CharacterHistory(events=[original])
    new_event = replace(original, title="Título atualizado", year=48)
    updated = replace(history, events=[new_event])
    assert updated.events[0].id == original.id
    assert history.events[0].year is None


def test_history_has_no_disk_or_project_side_effects():
    history = CharacterHistory(biography="Exemplo")
    assert not hasattr(history, "save")
    assert not hasattr(history, "load")
    assert not hasattr(history, "project")


def test_history_does_not_import_character_or_relationship_module():
    # O módulo só representa dados; nenhuma ligação automática com a genealogia.
    history = CharacterHistory(events=[HistoryEvent(title="Casamento")])
    assert history.events[0].title == "Casamento"
    assert not hasattr(history.events[0], "spouse_id")
    assert not hasattr(history.events[0], "relationship")
