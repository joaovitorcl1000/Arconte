"""Testes isolados de ``character.personality`` do Arconte.

Execute, na pasta ``backend/genealogy``::

    python3 -m pytest test/test_personality.py -v

O teste não altera arquivos de projeto e não acessa a rede.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import json
from types import MappingProxyType

import pytest

from character.personality import PersonalityProfile


LIST_FIELDS = ("traits", "virtues", "flaws", "ambitions", "fears", "desires")


@pytest.fixture
def artuin() -> PersonalityProfile:
    return PersonalityProfile(
        traits=["Arrogante", "Manipulador", "Ambicioso"],
        flaws=["Sádico", "Cruel"],
        ambitions=["Expandir o poder da Casa Hauck"],
        desires=["Conquistar influência entre os lordes"],
        description="Sabe se portar e mentir bem diante da nobreza.",
        custom_attributes={"comportamento_publico": {"diplomacia": "Persuasivo"}},
    )


def test_default_profile_is_empty():
    profile = PersonalityProfile()
    for name in LIST_FIELDS:
        assert getattr(profile, name) == ()
    assert profile.description is None
    assert dict(profile.custom_attributes) == {}


def test_expected_fields():
    assert {f.name for f in fields(PersonalityProfile)} == {
        *LIST_FIELDS, "description", "custom_attributes",
    }


def test_constructor_is_keyword_only():
    with pytest.raises(TypeError):
        PersonalityProfile(["Corajoso"])


def test_artuin_profile(artuin):
    assert artuin.traits == ("Arrogante", "Manipulador", "Ambicioso")
    assert artuin.flaws == ("Sádico", "Cruel")
    assert artuin.ambitions == ("Expandir o poder da Casa Hauck",)
    assert "mentir" in artuin.description
    assert artuin.custom_attributes["comportamento_publico"]["diplomacia"] == "Persuasivo"


def test_aioria_profile_can_describe_honored_sociable_character():
    profile = PersonalityProfile(
        traits=["Sonhador", "Bem-humorado", "Namorador"],
        virtues=["Valente", "Honrado"],
        flaws=["Ingênuo"],
    )
    assert profile.virtues == ("Valente", "Honrado")
    assert profile.flaws == ("Ingênuo",)


def test_fictional_character_can_use_arbitrary_psychological_concepts():
    profile = PersonalityProfile(
        traits=["Pacífico", "Telepático"],
        fears=["Ruptura do elo coletivo"],
        custom_attributes={"mente_coletiva": True, "vínculos": ["Espécie alfa"]},
    )
    assert profile.traits[1] == "Telepático"
    assert profile.custom_attributes["mente_coletiva"] is True


@pytest.mark.parametrize("name", LIST_FIELDS)
def test_each_list_field_accepts_python_list(name):
    profile = PersonalityProfile(**{name: [" Corajoso ", " Honrado "]})
    assert getattr(profile, name) == ("Corajoso", "Honrado")


@pytest.mark.parametrize("name", LIST_FIELDS)
def test_each_list_field_accepts_tuple(name):
    profile = PersonalityProfile(**{name: (" Criativo ", " Observador ")})
    assert getattr(profile, name) == ("Criativo", "Observador")


@pytest.mark.parametrize("name", LIST_FIELDS)
def test_each_list_field_accepts_empty_collections(name):
    assert getattr(PersonalityProfile(**{name: []}), name) == ()
    assert getattr(PersonalityProfile(**{name: ()}), name) == ()


@pytest.mark.parametrize("name", LIST_FIELDS)
@pytest.mark.parametrize("value", [None, "Corajoso", 13, True, {"a": 1}, {"a"}, b"x", (x for x in ["a"])])
def test_list_fields_reject_non_list_tuple_values(name, value):
    with pytest.raises(TypeError):
        PersonalityProfile(**{name: value})


@pytest.mark.parametrize("name", LIST_FIELDS)
@pytest.mark.parametrize("value", [1, 1.5, True, None, {}, [], ("texto",)])
def test_list_fields_reject_non_string_items(name, value):
    with pytest.raises(TypeError):
        PersonalityProfile(**{name: [value]})


@pytest.mark.parametrize("name", LIST_FIELDS)
@pytest.mark.parametrize("value", ["", " ", "\n\t"])
def test_list_fields_reject_empty_items(name, value):
    with pytest.raises(ValueError, match="vazio"):
        PersonalityProfile(**{name: [value]})


@pytest.mark.parametrize("name", LIST_FIELDS)
def test_list_fields_normalize_whitespace_but_preserve_interior(name):
    profile = PersonalityProfile(**{name: ["  Ambição  política  ", "  Medo\nde altura  "]})
    assert getattr(profile, name) == ("Ambição  política", "Medo\nde altura")


@pytest.mark.parametrize("name", LIST_FIELDS)
def test_list_field_preserves_order_and_duplicate_terms(name):
    profile = PersonalityProfile(**{name: ["A", "B", "A"]})
    assert getattr(profile, name) == ("A", "B", "A")


def test_source_list_changes_do_not_affect_profile():
    source = ["Valente"]
    profile = PersonalityProfile(virtues=source)
    source.append("Honrado")
    assert profile.virtues == ("Valente",)


def test_list_fields_are_tuples_and_cannot_be_appended(artuin):
    with pytest.raises(AttributeError):
        artuin.traits.append("Novo")


def test_description_accepts_paragraphs_and_accents():
    profile = PersonalityProfile(description="\n  Primeiro parágrafo.\n\nSegundo parágrafo: ÓFiachra.  \n")
    assert profile.description == "Primeiro parágrafo.\n\nSegundo parágrafo: ÓFiachra."


@pytest.mark.parametrize("value", [None, "", " ", "\n\t"])
def test_description_is_optional(value):
    assert PersonalityProfile(description=value).description is None


@pytest.mark.parametrize("value", [0, 4.2, True, [], {}, b"texto"])
def test_description_rejects_non_string_values(value):
    with pytest.raises(TypeError):
        PersonalityProfile(description=value)


def test_unicode_is_preserved_in_all_fields():
    profile = PersonalityProfile(
        traits=["Ingênua", "Compaixão 🦅"],
        description="Coração de cobre.\n\nForça da Sarnília.",
        custom_attributes={"fé": "ÓCuillan"},
    )
    assert "🦅" in profile.traits[1]
    assert profile.custom_attributes["fé"] == "ÓCuillan"


@pytest.mark.parametrize("value", [None, 1, [], (), False, "dict"])
def test_custom_attributes_must_be_mapping(value):
    with pytest.raises(TypeError):
        PersonalityProfile(custom_attributes=value)


@pytest.mark.parametrize("value", [{1: 2}, {None: 2}, {True: "sim"}])
def test_custom_keys_must_be_strings(value):
    with pytest.raises(TypeError):
        PersonalityProfile(custom_attributes=value)


@pytest.mark.parametrize("value", [{"": 1}, {" ": 1}, {"\n": 1}])
def test_custom_keys_cannot_be_empty(value):
    with pytest.raises(ValueError):
        PersonalityProfile(custom_attributes=value)


def test_custom_keys_are_trimmed():
    profile = PersonalityProfile(custom_attributes={"  gatilhos emocionais  ": ["injustiça"]})
    assert profile.custom_attributes["gatilhos emocionais"] == ("injustiça",)


def test_custom_duplicate_keys_after_normalization_are_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        PersonalityProfile(custom_attributes={" medo": 1, "medo ": 2})


def test_custom_attributes_support_json_scalars_and_nested_structures():
    profile = PersonalityProfile(custom_attributes={
        "str": "nobre",
        "int": 17,
        "float": 1.75,
        "bool_true": True,
        "bool_false": False,
        "none": None,
        "nest": {"motivações": ["honra", {"perigo": 3}]},
    })
    assert profile.custom_attributes["str"] == "nobre"
    assert profile.custom_attributes["int"] == 17
    assert profile.custom_attributes["float"] == 1.75
    assert profile.custom_attributes["bool_true"] is True
    assert profile.custom_attributes["bool_false"] is False
    assert profile.custom_attributes["none"] is None
    assert profile.custom_attributes["nest"]["motivações"][1]["perigo"] == 3


def test_custom_attributes_are_defensively_copied():
    original = {"dilemas": ["honra"], "temperamento": {"grau": 1}}
    profile = PersonalityProfile(custom_attributes=original)
    original["dilemas"].append("poder")
    original["temperamento"]["grau"] = 999
    original["novo"] = "segredo"
    assert profile.custom_attributes["dilemas"] == ("honra",)
    assert profile.custom_attributes["temperamento"]["grau"] == 1
    assert "novo" not in profile.custom_attributes


def test_custom_attributes_are_immutable_in_nested_objects():
    profile = PersonalityProfile(custom_attributes={"interior": {"medos": ["mar"]}})
    with pytest.raises(TypeError):
        profile.custom_attributes["interior"]["novo"] = 2
    with pytest.raises(AttributeError):
        profile.custom_attributes["interior"]["medos"].append("altura")
    with pytest.raises(TypeError):
        profile.custom_attributes["novo"] = 2


@pytest.mark.parametrize("value", [object(), {"x"}, complex(1, 2), b"bytes"])
def test_custom_attributes_reject_unknown_types(value):
    with pytest.raises(TypeError):
        PersonalityProfile(custom_attributes={"x": value})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_custom_attributes_reject_nonfinite_numbers(value):
    with pytest.raises(ValueError):
        PersonalityProfile(custom_attributes={"x": {"deep": [value]}})


def test_custom_mapping_cycles_are_rejected():
    cyclic = {}
    cyclic["itself"] = cyclic
    with pytest.raises(ValueError, match="ciclos"):
        PersonalityProfile(custom_attributes={"cyclic": cyclic})


def test_custom_list_cycles_are_rejected():
    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(ValueError, match="ciclos"):
        PersonalityProfile(custom_attributes={"cyclic": cyclic})


def test_reusing_same_nested_list_without_cycle_is_supported():
    shared = ["temeroso"]
    profile = PersonalityProfile(custom_attributes={"a": shared, "b": shared})
    assert profile.custom_attributes["a"] == profile.custom_attributes["b"]


def test_nested_custom_keys_normalize():
    profile = PersonalityProfile(custom_attributes={"perfil": {"  temperamento ": "calmo"}})
    assert profile.custom_attributes["perfil"]["temperamento"] == "calmo"


def test_nested_custom_duplicate_keys_raise():
    with pytest.raises(ValueError, match="duplicada"):
        PersonalityProfile(custom_attributes={"perfil": {" medo": 1, "medo ": 2}})


def test_mapping_proxy_and_tuples_are_accepted_in_custom_values():
    original = MappingProxyType({"influências": ("família", "poder")})
    profile = PersonalityProfile(custom_attributes=original)
    assert profile.custom_attributes["influências"] == ("família", "poder")


def test_is_frozen_and_slotted(artuin):
    assert not hasattr(artuin, "__dict__")
    with pytest.raises(FrozenInstanceError):
        artuin.description = "Alterado"
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        artuin.another_field = "Novo"


def test_dataclass_replace_creates_modified_independent_profile(artuin):
    other = replace(artuin, virtues=["Perspicaz"])
    assert other.virtues == ("Perspicaz",)
    assert artuin.virtues == ()
    assert other.traits == artuin.traits


def test_empty_profile_to_dict_is_json_ready():
    data = PersonalityProfile().to_dict()
    for name in LIST_FIELDS:
        assert data[name] == []
    assert data["description"] is None
    assert data["custom_attributes"] == {}
    json.dumps(data, allow_nan=False)


def test_profile_to_dict_returns_nested_lists_and_no_mappingproxies(artuin):
    data = artuin.to_dict()
    assert data["traits"] == ["Arrogante", "Manipulador", "Ambicioso"]
    assert data["custom_attributes"]["comportamento_publico"] == {"diplomacia": "Persuasivo"}
    assert isinstance(data["traits"], list)
    json.dumps(data, ensure_ascii=False, allow_nan=False)


def test_to_dict_defensively_copies_all_values():
    profile = PersonalityProfile(
        traits=["Reflexivo"],
        custom_attributes={"x": [{"a": ["um"]}]},
    )
    raw = profile.to_dict()
    raw["traits"].append("Falso")
    raw["custom_attributes"]["x"][0]["a"].append("dois")
    assert profile.traits == ("Reflexivo",)
    assert profile.custom_attributes["x"][0]["a"] == ("um",)


def test_roundtrip_preserves_content(artuin):
    encoded = json.dumps(artuin.to_dict(), ensure_ascii=False, allow_nan=False)
    restored = PersonalityProfile.from_dict(json.loads(encoded))
    assert restored == artuin
    assert restored.to_dict() == artuin.to_dict()


def test_roundtrip_preserves_multiline_unicode():
    profile = PersonalityProfile(
        fears=["Perder o trono", "Ódio alheio"],
        description="Primeiro parágrafo.\n\nSegundo parágrafo: 🦅",
    )
    restored = PersonalityProfile.from_dict(json.loads(json.dumps(profile.to_dict())))
    assert restored == profile


def test_from_dict_accepts_partial_data():
    profile = PersonalityProfile.from_dict({"traits": ["Calmo"]})
    assert profile.traits == ("Calmo",)
    assert profile.description is None
    assert profile.virtues == ()


def test_from_dict_accepts_readonly_mapping():
    profile = PersonalityProfile.from_dict(MappingProxyType({"flaws": ["Teimosia"]}))
    assert profile.flaws == ("Teimosia",)


@pytest.mark.parametrize("value", [None, "texto", 5, [], (), True])
def test_from_dict_rejects_non_mapping(value):
    with pytest.raises(TypeError):
        PersonalityProfile.from_dict(value)


def test_from_dict_rejects_unknown_fields():
    with pytest.raises(ValueError, match="desconhecidos"):
        PersonalityProfile.from_dict({"traits": [], "tittle": "Conde"})


def test_from_dict_rejects_bad_known_field_values():
    with pytest.raises(TypeError):
        PersonalityProfile.from_dict({"traits": "Ambicioso"})


def test_from_dict_does_not_modify_input():
    data = {"traits": ["Valente"], "custom_attributes": {"psique": [1, 2]}}
    expected = json.loads(json.dumps(data))
    PersonalityProfile.from_dict(data)
    assert data == expected


def test_profile_is_independent_from_character_entity():
    # Uma ficha psicológica não precisa de UUID, genealogia ou personagem.
    profile = PersonalityProfile(traits=["Humilde"])
    assert not hasattr(profile, "character_id")
    assert profile.to_dict()["traits"] == ["Humilde"]
