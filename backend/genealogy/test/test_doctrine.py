"""Testes do módulo religion.doctrine."""
import json
from dataclasses import FrozenInstanceError, replace
from uuid import UUID, uuid4

import pytest

from religion.doctrine import Doctrine, DoctrineCategory


def doctrine(**kwargs):
    return Doctrine(religion_id=uuid4(), title="Luz", content="Cultivar a luz.", **kwargs)


def test_defaults_and_immutable():
    d = doctrine()
    assert d.title == "Luz"
    assert d.category == DoctrineCategory.OTHER
    assert isinstance(d.id, UUID)
    assert d.start_year is None and d.end_year is None
    assert str(d) == "Luz"
    with pytest.raises(FrozenInstanceError):
        d.title = "Outro"


@pytest.mark.parametrize("field", ["religion_id", "id"])
def test_reject_invalid_uuid(field):
    kwargs = dict(religion_id=uuid4(), title="A", content="Texto")
    kwargs[field] = "bad"
    with pytest.raises(TypeError):
        Doctrine(**kwargs)


@pytest.mark.parametrize("field", ["title", "content"])
@pytest.mark.parametrize("value,exception", [(None, TypeError), (2, TypeError), (False, TypeError), ("", ValueError), ("  ", ValueError)])
def test_required_text_validation(field, value, exception):
    kwargs = dict(religion_id=uuid4(), title="A", content="Texto")
    kwargs[field] = value
    with pytest.raises(exception):
        Doctrine(**kwargs)


def test_multiline_content_and_notes():
    d = doctrine(notes="  Nota  ")
    assert d.notes == "Nota"
    d2 = Doctrine(religion_id=uuid4(), title=" Rito ", content="  Linha 1\n\nLinha 2  ")
    assert d2.content == "Linha 1\n\nLinha 2"
    assert Doctrine(religion_id=uuid4(), title="A", content="B", notes=" ").notes is None
    with pytest.raises(TypeError):
        doctrine(notes=[])


@pytest.mark.parametrize("field", ["start_year", "end_year"])
@pytest.mark.parametrize("value", [True, False, 12.0, "12", []])
def test_reject_bad_year(field, value):
    with pytest.raises(TypeError):
        doctrine(**{field: value})


def test_years_allow_negative_and_inclusive():
    d = doctrine(start_year=-10, end_year=67)
    assert not d.is_active_at(-11)
    assert d.is_active_at(-10)
    assert d.is_active_at(67)
    assert not d.is_active_at(68)
    with pytest.raises(ValueError):
        doctrine(start_year=67, end_year=66)


@pytest.mark.parametrize("bad", [None, True, 2.5, "67", False])
def test_active_year_invalid(bad):
    with pytest.raises(TypeError):
        doctrine().is_active_at(bad)


def test_unbounded_doctrine_works_in_fiction():
    d = doctrine()
    assert d.is_active_at(-1000000) and d.is_active_at(1000000)


def test_category_enum_validation():
    d = doctrine(category=DoctrineCategory.COSMOLOGY)
    assert d.category == DoctrineCategory.COSMOLOGY
    with pytest.raises(TypeError):
        doctrine(category="cosmology")


def test_custom_nested_immutability():
    source = {"regras": ["paz", {"limite": 2}]}
    d = doctrine(custom_attributes=source)
    source["regras"].append("alterado")
    assert len(d.custom_attributes["regras"]) == 2
    with pytest.raises(TypeError):
        d.custom_attributes["foo"] = "bar"
    output = d.to_dict()
    output["custom_attributes"]["regras"].append("alterado")
    assert len(d.to_dict()["custom_attributes"]["regras"]) == 2


@pytest.mark.parametrize("bad", [{"n": float("nan")}, {"n": float("inf")}, {1: "x"}, {"x": object()}])
def test_invalid_custom(bad):
    with pytest.raises((ValueError, TypeError)):
        doctrine(custom_attributes=bad)


def test_roundtrip_unicode():
    d = doctrine(category=DoctrineCategory.ETHICS, start_year=-7, end_year=67, notes="ÓFiachra", custom_attributes={"texto": "Dúvida"})
    data = json.loads(json.dumps(d.to_dict(), allow_nan=False, ensure_ascii=False))
    assert Doctrine.from_dict(data) == d
    assert Doctrine.from_dict(data).id == d.id


@pytest.mark.parametrize("bad", [None, [], 3, "a"])
def test_from_dict_bad_container(bad):
    with pytest.raises(TypeError):
        Doctrine.from_dict(bad)


def test_from_dict_minimal_and_missing():
    uid, rid = uuid4(), uuid4()
    d = Doctrine.from_dict({"id": str(uid), "religion_id": str(rid), "title": "A", "content": "B"})
    assert d.id == uid and d.religion_id == rid
    with pytest.raises(ValueError, match="ausentes"):
        Doctrine.from_dict({"id": str(uid), "religion_id": str(rid), "title": "A"})


def test_from_dict_unknown_fields():
    record = doctrine().to_dict()
    record["deity_id"] = str(uuid4())
    with pytest.raises(ValueError, match="desconhecidos"):
        Doctrine.from_dict(record)


@pytest.mark.parametrize("bad", ["oops", uuid4(), str(uuid4()).upper(), 3])
@pytest.mark.parametrize("field", ["id", "religion_id"])
def test_from_dict_bad_uuid(field, bad):
    record = doctrine().to_dict()
    record[field] = bad
    with pytest.raises((TypeError, ValueError)):
        Doctrine.from_dict(record)


@pytest.mark.parametrize("bad", [None, True, "other-invalid", 2])
def test_bad_category_json(bad):
    record = doctrine().to_dict()
    record["category"] = bad
    with pytest.raises((TypeError, ValueError)):
        Doctrine.from_dict(record)


def test_replace_identity_and_validation():
    d = doctrine()
    newer = replace(d, title="Nova lei", content="Revisão")
    assert newer.id == d.id
    assert d.title == "Luz"
    with pytest.raises(ValueError):
        replace(d, content=" ")
