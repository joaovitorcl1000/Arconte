"""Testes do módulo religion.religion; um arquivo por módulo."""
import json
from dataclasses import FrozenInstanceError, replace
from uuid import UUID, uuid4

import pytest

from religion.religion import Religion, ReligionType


def test_defaults_and_immutable_identity():
    r = Religion(name="  Culto de Mezena  ")
    assert r.name == "Culto de Mezena"
    assert r.type is ReligionType.OTHER
    assert isinstance(r.id, UUID)
    assert r.scriptures == r.traditions == ()
    assert r.custom_attributes == {}
    with pytest.raises(FrozenInstanceError):
        r.name = "Outro"


@pytest.mark.parametrize("value,exception", [(None, TypeError), (4, TypeError), (False, TypeError), ("", ValueError), ("  ", ValueError)])
def test_invalid_name(value, exception):
    with pytest.raises(exception):
        Religion(name=value)


@pytest.mark.parametrize("value", [" ", "", "\n", None])
def test_optional_text_is_empty(value):
    r = Religion(name="A", origin_place=value, description=value)
    assert r.origin_place is None and r.description is None


@pytest.mark.parametrize("field", ["origin_place", "description"])
def test_optional_text_rejects_other_types(field):
    with pytest.raises(TypeError):
        Religion(name="A", **{field: 1})


@pytest.mark.parametrize("field", ["id", "founder_id", "parent_religion_id"])
def test_bad_uuid_types(field):
    with pytest.raises(TypeError):
        Religion(name="A", **{field: "123"})


def test_religion_cannot_parent_self():
    uid = uuid4()
    with pytest.raises(ValueError, match="própria"):
        Religion(name="A", id=uid, parent_religion_id=uid)


@pytest.mark.parametrize("value", [None, 0, -9, 67, 999])
def test_fictional_year_values(value):
    r = Religion(name="A", founded_year=value)
    assert r.founded_year == value


@pytest.mark.parametrize("field", ["founded_year", "ended_year"])
@pytest.mark.parametrize("value", [True, False, 4.0, "67", [], object()])
def test_invalid_year_types(field, value):
    with pytest.raises(TypeError):
        Religion(name="A", **{field: value})


def test_ends_before_foundation_rejected():
    with pytest.raises(ValueError, match="ended_year"):
        Religion(name="A", founded_year=10, ended_year=9)


def test_active_at_inclusive_boundaries():
    religion = Religion(name="A", founded_year=-20, ended_year=30)
    assert not religion.is_active_at(-21)
    assert religion.is_active_at(-20)
    assert religion.is_active_at(30)
    assert not religion.is_active_at(31)


@pytest.mark.parametrize("year", [None, True, 2.0, "4", False])
def test_active_at_rejects_bad_year(year):
    with pytest.raises(TypeError):
        Religion(name="A").is_active_at(year)


def test_unknown_boundaries_are_not_invented():
    r = Religion(name="A")
    assert r.is_active_at(-9999)
    assert r.is_active_at(9999)


@pytest.mark.parametrize("value", [123, True, None, "texto", {"a": 1}])
def test_scriptures_invalid_container(value):
    with pytest.raises(TypeError):
        Religion(name="A", scriptures=value)


@pytest.mark.parametrize("field", ["scriptures", "traditions"])
def test_lists_normalize_become_immutable(field):
    original = ["  Manuscrito  ", "Cânticos"]
    r = Religion(name="A", **{field: original})
    original.append("Invasão")
    assert getattr(r, field) == ("Manuscrito", "Cânticos")
    with pytest.raises(AttributeError):
        getattr(r, field).append("Outro")


@pytest.mark.parametrize("field", ["scriptures", "traditions"])
@pytest.mark.parametrize("value", [["Livro", " livro "], ["", "Outro"], ["Um", 3]])
def test_invalid_text_items(field, value):
    with pytest.raises((TypeError, ValueError)):
        Religion(name="A", **{field: value})


def test_enum_type_and_case():
    assert Religion(name="A", type=ReligionType.NON_THEISTIC).type == ReligionType.NON_THEISTIC
    with pytest.raises(TypeError):
        Religion(name="A", type="non_theistic")


def test_custom_deep_immutability_and_detached_output():
    original = {"sagrado": {"nomes": ["Mezena", "ÓCuillan"]}, "ativo": True}
    religion = Religion(name="A", custom_attributes=original)
    original["sagrado"]["nomes"].append("INTRUSO")
    assert religion.custom_attributes["sagrado"]["nomes"] == ("Mezena", "ÓCuillan")
    with pytest.raises(TypeError):
        religion.custom_attributes["ativo"] = False
    with pytest.raises(TypeError):
        religion.custom_attributes["sagrado"]["novo"] = 5
    data = religion.to_dict()
    data["custom_attributes"]["sagrado"]["nomes"].append("modificado")
    assert religion.to_dict()["custom_attributes"]["sagrado"]["nomes"] == ["Mezena", "ÓCuillan"]


def test_repeated_object_not_confused_with_cycle():
    nested = ["a"]
    r = Religion(name="A", custom_attributes={"a": nested, "b": nested})
    assert r.to_dict()["custom_attributes"] == {"a": ["a"], "b": ["a"]}


def test_true_cycle_rejected():
    d = {}
    d["ciclo"] = d
    with pytest.raises(ValueError, match="circulares"):
        Religion(name="A", custom_attributes=d)


@pytest.mark.parametrize("value,exception", [({" ": 1}, ValueError), ({1: "x"}, TypeError), ({"x": float("nan")}, ValueError), ({"x": float("inf")}, ValueError), ({"x": {"y": object()}}, TypeError), ([], TypeError)])
def test_invalid_custom_attributes(value, exception):
    with pytest.raises(exception):
        Religion(name="A", custom_attributes=value)


def test_trim_duplicate_keys_rejected():
    with pytest.raises(ValueError, match="duplicada"):
        Religion(name="A", custom_attributes={"chave": 1, " chave ": 2})


def test_roundtrip_unicode_and_time():
    r = Religion(
        name=" Culto de Mezena ", type=ReligionType.POLYTHEISTIC,
        parent_religion_id=uuid4(), founder_id=uuid4(),
        founded_year=-45, ended_year=67, origin_place="Sarnília",
        scriptures=["Tratado de ÓFiachra"], traditions=["Oração noturna"],
        description="Primeiro parágrafo\n\nSegundo parágrafo",
        custom_attributes={"rituais": [{"tipo": "dança", "n": 2}]},
    )
    doc = json.loads(json.dumps(r.to_dict(), ensure_ascii=False, allow_nan=False))
    assert Religion.from_dict(doc) == r
    assert Religion.from_dict(doc).id == r.id
    assert str(r) == "Culto de Mezena"


def test_optional_fields_can_be_omitted_on_import():
    r = Religion(name="Culto", id=uuid4())
    loaded = Religion.from_dict({"id": str(r.id), "name": r.name})
    assert loaded == r


@pytest.mark.parametrize("value", [None, [], "texto"])
def test_from_dict_rejects_non_mapping(value):
    with pytest.raises(TypeError):
        Religion.from_dict(value)


def test_from_dict_unknown_and_missing_fields():
    with pytest.raises(ValueError, match="ausentes"):
        Religion.from_dict({"id": str(uuid4())})
    with pytest.raises(ValueError, match="desconhecidos"):
        Religion.from_dict({"name": "Culto", "id": str(uuid4()), "organization_id": str(uuid4())})


@pytest.mark.parametrize("bad", ["sem-uuid", "A"*36, str(uuid4()).upper(), str(uuid4()).replace("-", "")])
def test_from_dict_invalid_uuid(bad):
    with pytest.raises(ValueError):
        Religion.from_dict({"id": bad, "name": "Culto"})


def test_from_dict_uuid_object_rejected():
    with pytest.raises(TypeError):
        Religion.from_dict({"id": uuid4(), "name": "A"})


@pytest.mark.parametrize("field", ["founder_id", "parent_religion_id"])
def test_from_dict_bad_reference(field):
    with pytest.raises((ValueError, TypeError)):
        Religion.from_dict({"id": str(uuid4()), "name": "A", field: "bad"})


@pytest.mark.parametrize("value", ["inexistente", 4, True, None])
def test_from_dict_bad_type(value):
    with pytest.raises((ValueError, TypeError)):
        Religion.from_dict({"name": "Culto", "id": str(uuid4()), "type": value})


def test_replace_revalidates_and_preserves_uuid():
    r = Religion(name="Mezena")
    updated = replace(r, name=" Nova tradição ")
    assert updated.name == "Nova tradição"
    assert updated.id == r.id
    with pytest.raises(ValueError):
        replace(r, name="")
