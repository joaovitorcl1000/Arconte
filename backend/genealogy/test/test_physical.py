"""Testes do módulo ``character.physical`` do Arconte.

Execute a partir de ``backend/genealogy``::

    python3 -m pytest test/test_physical.py -v

Não cria arquivos, não acessa rede e não altera projetos do escritor.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import json
from types import MappingProxyType

import pytest

from character.physical import PhysicalAttributes


@pytest.fixture
def artuin() -> PhysicalAttributes:
    return PhysicalAttributes(
        height_m=1.68,
        weight_kg=80,
        hair_color="Ruivo",
        body_type="Baixo e entroncado",
        description="Rosto de aspecto enferrujado; físico forte.",
        custom_attributes={"marcas": ["Cicatriz na mão", "Sardas"]},
    )


def test_defaults_are_unknown_and_custom_attributes_are_empty():
    physical = PhysicalAttributes()
    assert physical.height_m is None
    assert physical.weight_kg is None
    assert physical.hair_color is None
    assert physical.eye_color is None
    assert physical.skin_tone is None
    assert physical.body_type is None
    assert physical.distinctive_features is None
    assert physical.description is None
    assert dict(physical.custom_attributes) == {}


def test_expected_field_names():
    assert {f.name for f in fields(PhysicalAttributes)} == {
        "height_m", "weight_kg", "hair_color", "eye_color", "skin_tone",
        "body_type", "distinctive_features", "description", "custom_attributes",
    }


def test_keyword_only_constructor():
    with pytest.raises(TypeError):
        PhysicalAttributes(1.68)


def test_real_character_profile(artuin):
    assert artuin.height_m == 1.68
    assert artuin.weight_kg == 80.0
    assert artuin.hair_color == "Ruivo"
    assert artuin.body_type == "Baixo e entroncado"
    assert "enferrujado" in artuin.description
    assert artuin.custom_attributes["marcas"] == ("Cicatriz na mão", "Sardas")


def test_nonhuman_character_is_supported():
    physical = PhysicalAttributes(
        height_m=4.5,
        weight_kg=900,
        skin_tone="Escamas douradas",
        custom_attributes={"asas": 2, "chifres": True, "cauda": {"comprimento_m": 3.2}},
    )
    assert physical.custom_attributes["asas"] == 2
    assert physical.custom_attributes["chifres"] is True
    assert physical.custom_attributes["cauda"]["comprimento_m"] == 3.2


@pytest.mark.parametrize("name", ["height_m", "weight_kg"])
@pytest.mark.parametrize("value", [1, 1.68, 80, 0.001, 1000000])
def test_accepts_any_positive_finite_measure(name, value):
    profile = PhysicalAttributes(**{name: value})
    assert getattr(profile, name) == float(value)


@pytest.mark.parametrize("name", ["height_m", "weight_kg"])
@pytest.mark.parametrize("value", [0, -1, -0.0001, -1.5, float("inf"), float("-inf"), float("nan")])
def test_rejects_invalid_measure_values(name, value):
    with pytest.raises(ValueError):
        PhysicalAttributes(**{name: value})


@pytest.mark.parametrize("name", ["height_m", "weight_kg"])
@pytest.mark.parametrize("value", [True, False, "1.68", "80", [], {}, (1,), 1 + 2j])
def test_rejects_non_numeric_measures(name, value):
    with pytest.raises(TypeError):
        PhysicalAttributes(**{name: value})


@pytest.mark.parametrize("name", ["height_m", "weight_kg"])
def test_rejects_huge_integer_that_cannot_become_float(name):
    with pytest.raises(ValueError):
        PhysicalAttributes(**{name: 10**500})


@pytest.mark.parametrize("name", [
    "hair_color", "eye_color", "skin_tone", "body_type",
    "distinctive_features", "description",
])
def test_optional_text_is_trimmed(name):
    profile = PhysicalAttributes(**{name: "  Árvore rubra  \n"})
    assert getattr(profile, name) == "Árvore rubra"


@pytest.mark.parametrize("name", [
    "hair_color", "eye_color", "skin_tone", "body_type",
    "distinctive_features", "description",
])
@pytest.mark.parametrize("value", ["", "  ", "\t\n  "])
def test_blank_optional_text_becomes_none(name, value):
    profile = PhysicalAttributes(**{name: value})
    assert getattr(profile, name) is None


@pytest.mark.parametrize("name", [
    "hair_color", "eye_color", "skin_tone", "body_type",
    "distinctive_features", "description",
])
@pytest.mark.parametrize("value", [42, True, [], {}, 1.5])
def test_optional_text_rejects_non_string(name, value):
    with pytest.raises(TypeError):
        PhysicalAttributes(**{name: value})


def test_multiline_description_is_preserved_including_internal_line_breaks():
    profile = PhysicalAttributes(description="\n  Primeiro parágrafo.\n\nSegundo parágrafo.  \n")
    assert profile.description == "Primeiro parágrafo.\n\nSegundo parágrafo."


def test_unicode_characters_are_preserved():
    profile = PhysicalAttributes(eye_color="Verde vívido", description="Cicatriz em formato de 🦅")
    assert "vívido" in profile.eye_color
    assert "🦅" in profile.description


def test_custom_attributes_must_be_mapping():
    for bad in (None, [], (), "foo", 5, True):
        with pytest.raises(TypeError):
            PhysicalAttributes(custom_attributes=bad)


@pytest.mark.parametrize("attributes", [{0: "zero"}, {None: "null"}, {True: 1}])
def test_custom_keys_must_be_strings(attributes):
    with pytest.raises(TypeError):
        PhysicalAttributes(custom_attributes=attributes)


@pytest.mark.parametrize("attributes", [{"": 1}, {"   ": 1}, {"\n\t": 1}])
def test_custom_keys_must_be_nonempty(attributes):
    with pytest.raises(ValueError):
        PhysicalAttributes(custom_attributes=attributes)


def test_custom_keys_are_trimmed():
    physical = PhysicalAttributes(custom_attributes={"  número de asas  ": 2})
    assert physical.custom_attributes["número de asas"] == 2
    assert "  número de asas  " not in physical.custom_attributes


def test_duplicate_custom_keys_after_trimming_are_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        PhysicalAttributes(custom_attributes={" asas": 1, "asas ": 2})


def test_custom_attributes_can_have_json_scalar_values():
    physical = PhysicalAttributes(custom_attributes={
        "string": "dragão", "int": 2, "float": 1.5,
        "true": True, "false": False, "null": None,
    })
    assert physical.custom_attributes["string"] == "dragão"
    assert physical.custom_attributes["int"] == 2
    assert physical.custom_attributes["float"] == 1.5
    assert physical.custom_attributes["true"] is True
    assert physical.custom_attributes["false"] is False
    assert physical.custom_attributes["null"] is None


def test_nested_custom_attributes_preserve_values():
    physical = PhysicalAttributes(custom_attributes={
        "anatomia": {"asas": 2, "escamas": ["douradas", "azuis"]},
        "títulos": ["Lorde", "Conde"],
    })
    assert physical.custom_attributes["anatomia"]["escamas"] == ("douradas", "azuis")
    assert physical.custom_attributes["títulos"] == ("Lorde", "Conde")


def test_custom_attributes_defensively_copy_source_dict_and_list():
    original = {"traços": ["cicatriz"], "detalhes": {"cor": "ruiva"}}
    physical = PhysicalAttributes(custom_attributes=original)
    original["traços"].append("nova cicatriz")
    original["detalhes"]["cor"] = "preta"
    original["novo"] = 10
    assert physical.custom_attributes["traços"] == ("cicatriz",)
    assert physical.custom_attributes["detalhes"]["cor"] == "ruiva"
    assert "novo" not in physical.custom_attributes


def test_top_level_custom_attributes_are_immutable():
    physical = PhysicalAttributes(custom_attributes={"marca": "lunar"})
    with pytest.raises(TypeError):
        physical.custom_attributes["marca"] = "solar"


def test_nested_mapping_cannot_be_mutated():
    physical = PhysicalAttributes(custom_attributes={"detalhes": {"marca": "lunar"}})
    with pytest.raises(TypeError):
        physical.custom_attributes["detalhes"]["marca"] = "solar"


def test_nested_list_cannot_be_mutated():
    physical = PhysicalAttributes(custom_attributes={"marcas": ["lunar"]})
    with pytest.raises(AttributeError):
        physical.custom_attributes["marcas"].append("solar")


def test_frozen_fields_cannot_be_modified(artuin):
    with pytest.raises(FrozenInstanceError):
        artuin.height_m = 1.90


def test_slots_prevent_arbitrary_attributes(artuin):
    assert not hasattr(artuin, "__dict__")
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        artuin.new_field = 10


@pytest.mark.parametrize("value", [object(), set(["asa"]), complex(1, 2), b"bytes"])
def test_invalid_custom_value_types_are_rejected(value):
    with pytest.raises(TypeError):
        PhysicalAttributes(custom_attributes={"invalid": value})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_custom_attributes_reject_nonfinite_floats(value):
    with pytest.raises(ValueError):
        PhysicalAttributes(custom_attributes={"invalid": {"nested": [value]}})


def test_rejects_cycle_in_a_dict():
    value = {}
    value["same"] = value
    with pytest.raises(ValueError, match="ciclos"):
        PhysicalAttributes(custom_attributes={"invalid": value})


def test_rejects_cycle_in_a_list():
    value = []
    value.append(value)
    with pytest.raises(ValueError, match="ciclos"):
        PhysicalAttributes(custom_attributes={"invalid": value})


def test_allows_shared_noncyclic_references():
    shared = ["alto", "ruivo"]
    profile = PhysicalAttributes(custom_attributes={"A": shared, "B": shared})
    assert profile.custom_attributes["A"] == ("alto", "ruivo")
    assert profile.custom_attributes["B"] == ("alto", "ruivo")


def test_nested_keys_get_normalized_and_checked():
    physical = PhysicalAttributes(custom_attributes={"detalhes": {"  tipo ": "alado"}})
    assert physical.custom_attributes["detalhes"]["tipo"] == "alado"


def test_nested_duplicate_keys_are_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        PhysicalAttributes(custom_attributes={"anatomia": {" asas ": 1, "asas": 2}})


def test_custom_attributes_accept_mapping_proxy_and_tuples():
    attributes = MappingProxyType({"olhos": ("verde", "azul")})
    profile = PhysicalAttributes(custom_attributes=attributes)
    assert profile.custom_attributes["olhos"] == ("verde", "azul")


def test_separate_profiles_do_not_share_custom_attributes():
    first = PhysicalAttributes()
    second = PhysicalAttributes()
    assert first.custom_attributes is not second.custom_attributes


def test_to_dict_exposes_all_fields(artuin):
    data = artuin.to_dict()
    assert set(data) == {f.name for f in fields(PhysicalAttributes)}
    assert data["height_m"] == 1.68
    assert data["custom_attributes"] == {"marcas": ["Cicatriz na mão", "Sardas"]}


def test_to_dict_is_json_serializable(artuin):
    encoded = json.dumps(artuin.to_dict(), ensure_ascii=False, allow_nan=False)
    assert "mão" in encoded
    decoded = json.loads(encoded)
    assert decoded["height_m"] == 1.68


def test_to_dict_returns_independent_objects():
    profile = PhysicalAttributes(custom_attributes={"anatomia": {"cores": ["vermelho"]}})
    exported = profile.to_dict()
    exported["custom_attributes"]["anatomia"]["cores"].append("azul")
    exported["height_m"] = 90
    assert profile.height_m is None
    assert profile.custom_attributes["anatomia"]["cores"] == ("vermelho",)


def test_from_dict_reads_complete_profile(artuin):
    recovered = PhysicalAttributes.from_dict(artuin.to_dict())
    assert recovered == artuin
    assert recovered is not artuin


def test_from_dict_reads_partial_profile():
    recovered = PhysicalAttributes.from_dict({"hair_color": "Ruivo", "height_m": 1.68})
    assert recovered.hair_color == "Ruivo"
    assert recovered.height_m == 1.68
    assert recovered.weight_kg is None
    assert not recovered.custom_attributes


def test_from_dict_accepts_empty_mapping():
    assert PhysicalAttributes.from_dict({}) == PhysicalAttributes()


@pytest.mark.parametrize("value", [None, [], "data", 10, False])
def test_from_dict_rejects_non_mapping(value):
    with pytest.raises(TypeError):
        PhysicalAttributes.from_dict(value)


def test_from_dict_rejects_unknown_fields():
    with pytest.raises(ValueError, match="desconhecidos"):
        PhysicalAttributes.from_dict({"height_m": 1.5, "nickname": "O Pequeno"})


def test_from_dict_applies_regular_validation():
    with pytest.raises(ValueError):
        PhysicalAttributes.from_dict({"weight_kg": -20})
    with pytest.raises(TypeError):
        PhysicalAttributes.from_dict({"custom_attributes": [1, 2]})


def test_from_dict_accepts_mapping_proxy():
    p = PhysicalAttributes.from_dict(MappingProxyType({"eye_color": "Verde"}))
    assert p.eye_color == "Verde"


def test_json_round_trip_with_nested_attributes():
    profile = PhysicalAttributes(
        hair_color="Ruivo", skin_tone="Pálido",
        custom_attributes={"anatomia": {"asas": ["esquerda", "direita"], "chifres": True}},
    )
    loaded = json.loads(json.dumps(profile.to_dict(), ensure_ascii=False))
    assert PhysicalAttributes.from_dict(loaded) == profile


def test_dataclasses_replace_creates_new_valid_instance(artuin):
    modified = replace(artuin, height_m=1.72, hair_color="Castanho")
    assert modified is not artuin
    assert modified.height_m == 1.72
    assert modified.hair_color == "Castanho"
    assert artuin.height_m == 1.68
    assert artuin.hair_color == "Ruivo"
    assert modified.custom_attributes == artuin.custom_attributes


def test_dataclasses_replace_rejects_invalid_update(artuin):
    with pytest.raises(ValueError):
        replace(artuin, height_m=0)
    assert artuin.height_m == 1.68


def test_dataclasses_replace_can_edit_custom_attributes(artuin):
    old_attrs = dict(artuin.custom_attributes)
    modified = replace(artuin, custom_attributes={**old_attrs, "marca": "falcão"})
    assert modified.custom_attributes["marca"] == "falcão"
    assert "marca" not in artuin.custom_attributes


def test_independent_of_character_entity():
    from character.character import Character

    character = Character(name="Artuin", surname="Hauck", birth_year=31)
    physical = PhysicalAttributes(height_m=1.68, weight_kg=80)
    assert character.full_name == "Artuin Hauck"
    assert physical.height_m == 1.68
    assert "height_m" not in {f.name for f in fields(Character)}
