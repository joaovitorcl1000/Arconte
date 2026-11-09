"""Testes de ``character.social`` para o Arconte.

A partir de ``backend/genealogy``::

    python3 -m pytest test/test_social.py -v

Um único arquivo para todos os testes deste módulo. Não cria projetos no disco.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import json
from types import MappingProxyType

import pytest

from character.social import SocialProfile


TEXT_FIELDS = (
    "title", "occupation", "residence", "nationality", "religion",
    "social_status", "description",
)


@pytest.fixture
def artuin() -> SocialProfile:
    return SocialProfile(
        title="Conde da Sarnília",
        occupation="Governante do condado da Sarnília",
        residence="Castelo no Morro do Falcão",
        social_status="Nobreza",
        description="Senhor do Morro do Falcão.\n\nBusca ampliar seu poder.",
        custom_attributes={"jurisdição": "Sarnília", "brasão": "Falcão vermelho"},
    )


def test_default_profile_has_no_data():
    profile = SocialProfile()
    for name in TEXT_FIELDS:
        assert getattr(profile, name) is None
    assert dict(profile.custom_attributes) == {}


def test_expected_fields_only():
    assert {item.name for item in fields(SocialProfile)} == {
        *TEXT_FIELDS, "custom_attributes",
    }


def test_constructor_requires_keyword_arguments():
    with pytest.raises(TypeError):
        SocialProfile("Conde")


def test_artuin_social_profile(artuin):
    assert artuin.title == "Conde da Sarnília"
    assert artuin.occupation == "Governante do condado da Sarnília"
    assert artuin.residence == "Castelo no Morro do Falcão"
    assert artuin.social_status == "Nobreza"
    assert artuin.custom_attributes["brasão"] == "Falcão vermelho"


def test_ayla_social_profile():
    profile = SocialProfile(
        residence="Morro do Falcão, Sarnília",
        title="Consorte do conde da Sarnília",
        description="Filha de Dogen ÓFiachra, nobre do ducado da Secúria.",
    )
    assert "Secúria" in profile.description
    assert profile.nationality is None


def test_manohar_social_profile():
    profile = SocialProfile(
        occupation="Sumo-sacerdote de Mezena",
        religion="Culto de Mezena",
    )
    assert profile.occupation == "Sumo-sacerdote de Mezena"
    assert profile.religion == "Culto de Mezena"


def test_fantasy_setting_accepts_unusual_titles_and_statuses():
    profile = SocialProfile(
        title="Guardião da Nona Lua",
        social_status="Protetor eleito pelos dragões",
        custom_attributes={"espécie": "Draconiano", "mandatos": [3, 4]},
    )
    assert profile.title == "Guardião da Nona Lua"
    assert profile.custom_attributes["mandatos"] == (3, 4)


def test_nationality_and_religion_are_descriptions_not_enums():
    profile = SocialProfile(nationality="Cidadã de ÓCuillan", religion="Fé dos Bosques")
    assert profile.nationality == "Cidadã de ÓCuillan"
    assert profile.religion == "Fé dos Bosques"


@pytest.mark.parametrize("name", TEXT_FIELDS)
def test_text_fields_accept_none(name):
    assert getattr(SocialProfile(**{name: None}), name) is None


@pytest.mark.parametrize("name", TEXT_FIELDS)
@pytest.mark.parametrize("value", ["", "  ", "\n\t  "])
def test_text_fields_normalize_empty_to_none(name, value):
    assert getattr(SocialProfile(**{name: value}), name) is None


@pytest.mark.parametrize("name", TEXT_FIELDS)
def test_text_fields_strip_outer_spaces(name):
    profile = SocialProfile(**{name: "  ÓFiachra   Sarnília  "})
    assert getattr(profile, name) == "ÓFiachra   Sarnília"


@pytest.mark.parametrize("name", TEXT_FIELDS)
def test_text_fields_allow_internal_newlines(name):
    profile = SocialProfile(**{name: "  Primeiro parágrafo.\n\nSegundo parágrafo.  "})
    assert getattr(profile, name) == "Primeiro parágrafo.\n\nSegundo parágrafo."


@pytest.mark.parametrize("name", TEXT_FIELDS)
@pytest.mark.parametrize("value", [0, 1.5, True, False, [], {}, (), b"x", object()])
def test_text_fields_reject_non_strings(name, value):
    with pytest.raises(TypeError):
        SocialProfile(**{name: value})


def test_unicode_and_multiline_content_survives():
    profile = SocialProfile(
        title="Conde da Sarnília 🦅",
        residence="Morro do Falcão",
        description="Primeiro parágrafo.\n\nÓCuillan e ÓFiachra.\nTerceiro.",
    )
    assert "🦅" in profile.title
    assert profile.description.splitlines()[2].startswith("ÓCuillan")


def test_no_character_identity_or_family_records_in_social_profile():
    profile = SocialProfile(title="Conde")
    assert not hasattr(profile, "id")
    assert not hasattr(profile, "character_id")
    assert not hasattr(profile, "family_id")
    assert not hasattr(profile, "parents")
    assert not hasattr(profile, "membership")


def test_social_profile_can_exist_independently():
    profile = SocialProfile(title="Duquesa")
    assert profile.to_dict()["title"] == "Duquesa"


def test_social_title_does_not_automatically_create_family_membership():
    profile = SocialProfile(title="Lorde da Casa Hauck")
    assert "family_id" not in profile.to_dict()
    assert "memberships" not in profile.to_dict()


def test_fields_are_frozen_and_slotted(artuin):
    assert not hasattr(artuin, "__dict__")
    with pytest.raises(FrozenInstanceError):
        artuin.title = "Rei"
    with pytest.raises((AttributeError, FrozenInstanceError, TypeError)):
        artuin.unknown = "novo"


def test_replace_creates_a_new_social_profile(artuin):
    changed = replace(artuin, title="Duque da Sarnília")
    assert changed.title == "Duque da Sarnília"
    assert artuin.title == "Conde da Sarnília"
    assert changed.residence == artuin.residence


def test_replace_revalidates_fields(artuin):
    with pytest.raises(TypeError):
        replace(artuin, title=42)


def test_profiles_are_independent_instances():
    first = SocialProfile(custom_attributes={"jurisdição": ["Morro"]})
    second = SocialProfile()
    assert "jurisdição" not in second.custom_attributes
    assert first.custom_attributes["jurisdição"] == ("Morro",)


@pytest.mark.parametrize("value", [None, 5, False, [], (), "texto"])
def test_custom_attributes_require_mapping(value):
    with pytest.raises(TypeError):
        SocialProfile(custom_attributes=value)


@pytest.mark.parametrize("value", [{1: "a"}, {None: 5}, {False: "a"}])
def test_custom_attribute_keys_must_be_strings(value):
    with pytest.raises(TypeError):
        SocialProfile(custom_attributes=value)


@pytest.mark.parametrize("value", [{"": 1}, {" ": 2}, {"\n\t": True}])
def test_custom_attribute_keys_must_not_be_empty(value):
    with pytest.raises(ValueError):
        SocialProfile(custom_attributes=value)


def test_custom_attribute_keys_are_trimmed():
    profile = SocialProfile(custom_attributes={"  tributo  ": 200})
    assert profile.custom_attributes["tributo"] == 200


def test_duplicate_keys_after_trimming_are_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        SocialProfile(custom_attributes={"título": "A", " título ": "B"})


def test_nested_keys_are_trimmed():
    profile = SocialProfile(custom_attributes={"posses": {"  minas  ": ["prata"]}})
    assert profile.custom_attributes["posses"]["minas"] == ("prata",)


def test_nested_duplicate_keys_are_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        SocialProfile(custom_attributes={"posses": {"mina": 1, " mina": 2}})


def test_custom_attribute_scalars_json():
    profile = SocialProfile(custom_attributes={
        "texto": "Hauck", "inteiro": 67, "real": 1.5, "sim": True,
        "nao": False, "nulo": None,
    })
    assert profile.custom_attributes["texto"] == "Hauck"
    assert profile.custom_attributes["inteiro"] == 67
    assert profile.custom_attributes["real"] == 1.5
    assert profile.custom_attributes["sim"] is True
    assert profile.custom_attributes["nao"] is False
    assert profile.custom_attributes["nulo"] is None


def test_nested_lists_and_dicts_are_supported():
    profile = SocialProfile(custom_attributes={
        "jurisdições": ["Sarnília", {"montanhas": ["ouro", "prata"]}],
    })
    assert profile.custom_attributes["jurisdições"][1]["montanhas"] == ("ouro", "prata")


def test_source_custom_data_cannot_be_mutated_through_profile():
    original = {"regiões": ["Sarnília"], "propriedades": {"minas": 1}}
    profile = SocialProfile(custom_attributes=original)
    original["regiões"].append("Secúria")
    original["propriedades"]["minas"] = 99
    original["novo"] = "ruído"
    assert profile.custom_attributes["regiões"] == ("Sarnília",)
    assert profile.custom_attributes["propriedades"]["minas"] == 1
    assert "novo" not in profile.custom_attributes


def test_cannot_mutate_custom_mapping_or_nested_items():
    profile = SocialProfile(custom_attributes={"x": {"y": [1, 2]}})
    with pytest.raises(TypeError):
        profile.custom_attributes["novo"] = 0
    with pytest.raises(TypeError):
        profile.custom_attributes["x"]["novo"] = 0
    with pytest.raises(AttributeError):
        profile.custom_attributes["x"]["y"].append(3)


def test_readonly_mapping_and_tuple_accepted():
    source = MappingProxyType({"locais": ("Norte", "Sul")})
    profile = SocialProfile(custom_attributes=source)
    assert profile.custom_attributes["locais"] == ("Norte", "Sul")


@pytest.mark.parametrize("value", [object(), {1, 2}, complex(1, 3), b"abc"])
def test_custom_values_reject_non_json_types(value):
    with pytest.raises(TypeError):
        SocialProfile(custom_attributes={"dado": value})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_custom_values_reject_nonfinite_floats(value):
    with pytest.raises(ValueError):
        SocialProfile(custom_attributes={"deep": {"x": [value]}})


def test_custom_mapping_cycle_is_rejected():
    obj = {}
    obj["self"] = obj
    with pytest.raises(ValueError, match="ciclos"):
        SocialProfile(custom_attributes={"obj": obj})


def test_custom_list_cycle_is_rejected():
    obj = []
    obj.append(obj)
    with pytest.raises(ValueError, match="ciclos"):
        SocialProfile(custom_attributes={"obj": obj})


def test_custom_cross_cycle_is_rejected():
    first = {}
    second = [first]
    first["second"] = second
    with pytest.raises(ValueError, match="ciclos"):
        SocialProfile(custom_attributes={"first": first})


def test_same_list_can_be_shared_without_cycle():
    reused = ["Sarnília"]
    profile = SocialProfile(custom_attributes={"a": reused, "b": reused})
    assert profile.custom_attributes["a"] == profile.custom_attributes["b"]


def test_empty_profile_to_dict_is_json_serializable():
    data = SocialProfile().to_dict()
    assert set(data) == {*TEXT_FIELDS, "custom_attributes"}
    assert all(data[name] is None for name in TEXT_FIELDS)
    assert data["custom_attributes"] == {}
    json.dumps(data, allow_nan=False)


def test_artuin_to_dict(artuin):
    data = artuin.to_dict()
    assert data["title"] == "Conde da Sarnília"
    assert data["custom_attributes"]["jurisdição"] == "Sarnília"
    json.dumps(data, ensure_ascii=False, allow_nan=False)


def test_to_dict_returns_independent_nested_collections():
    profile = SocialProfile(custom_attributes={"x": [{"y": [1]}]})
    data = profile.to_dict()
    data["custom_attributes"]["x"][0]["y"].append(2)
    data["custom_attributes"]["x"].append("outra")
    data["custom_attributes"]["extra"] = True
    assert profile.custom_attributes["x"][0]["y"] == (1,)
    assert "extra" not in profile.custom_attributes


def test_to_dict_does_not_return_mappingproxy_or_tuples():
    profile = SocialProfile(custom_attributes={"a": (1, {"b": [2]})})
    result = profile.to_dict()["custom_attributes"]
    assert isinstance(result, dict)
    assert isinstance(result["a"], list)
    assert isinstance(result["a"][1], dict)
    assert isinstance(result["a"][1]["b"], list)


def test_roundtrip_json_for_artuin(artuin):
    encoded = json.dumps(artuin.to_dict(), ensure_ascii=False, allow_nan=False)
    restored = SocialProfile.from_dict(json.loads(encoded))
    assert restored == artuin
    assert restored.to_dict() == artuin.to_dict()


def test_roundtrip_multiline_and_accents():
    original = SocialProfile(
        description="Introdução.\n\nOs ÓFiachra e os ÓCuillan. 🦅",
        custom_attributes={"religião": {"práticas": ["oração", "festas"]}},
    )
    restored = SocialProfile.from_dict(json.loads(json.dumps(original.to_dict())))
    assert restored == original


def test_from_dict_accepts_empty_data():
    assert SocialProfile.from_dict({}) == SocialProfile()


def test_from_dict_accepts_partial_data():
    profile = SocialProfile.from_dict({"occupation": "Sacerdote"})
    assert profile.occupation == "Sacerdote"
    assert profile.title is None


def test_from_dict_accepts_mappingproxy():
    profile = SocialProfile.from_dict(MappingProxyType({"title": "Dama"}))
    assert profile.title == "Dama"


@pytest.mark.parametrize("value", [None, "texto", 1, True, [], ()])
def test_from_dict_rejects_non_mapping(value):
    with pytest.raises(TypeError):
        SocialProfile.from_dict(value)


def test_from_dict_rejects_unknown_fields():
    with pytest.raises(ValueError, match="desconhecidos"):
        SocialProfile.from_dict({"title": "Conde", "family_id": "arbitrary"})


def test_from_dict_rejects_typo_fields():
    with pytest.raises(ValueError, match="desconhecidos"):
        SocialProfile.from_dict({"tittle": "Conde"})


def test_from_dict_revalidates_bad_known_data():
    with pytest.raises(TypeError):
        SocialProfile.from_dict({"title": 20})


def test_from_dict_does_not_mutate_input():
    raw = {"title": " Conde ", "custom_attributes": {"test": [1, 2]}}
    previous = json.loads(json.dumps(raw))
    SocialProfile.from_dict(raw)
    assert raw == previous


def test_fields_do_not_add_new_year_or_parentage_semantics():
    profile = SocialProfile(title="Conde")
    assert not hasattr(profile, "birth_year")
    assert not hasattr(profile, "death_year")
    assert "relationships" not in profile.to_dict()
