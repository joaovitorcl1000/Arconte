"""Testes de OrganizationMembership. Um teste por arquivo do módulo de vínculo."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import json
from uuid import UUID, uuid4

import pytest

from organization.membership import OrganizationMembership


@pytest.fixture
def membership() -> OrganizationMembership:
    return OrganizationMembership(
        organization_id=uuid4(), character_id=uuid4(),
        role="Sumo-sacerdote", rank="Superior", start_year=35,
        end_year=67, notes="Primeira parte.\n\nSegunda parte.",
    )


def test_minimal_membership():
    m = OrganizationMembership(organization_id=uuid4(), character_id=uuid4())
    assert isinstance(m.id, UUID)
    assert m.role is m.rank is m.start_year is m.end_year is m.notes is None


def test_exact_fields():
    assert {f.name for f in fields(OrganizationMembership)} == {
        "id", "organization_id", "character_id", "role", "rank",
        "start_year", "end_year", "notes",
    }


def test_required_keywords():
    with pytest.raises(TypeError):
        OrganizationMembership(uuid4(), uuid4())
    with pytest.raises(TypeError):
        OrganizationMembership(organization_id=uuid4())
    with pytest.raises(TypeError):
        OrganizationMembership(character_id=uuid4())


def test_auto_ids_distinct():
    kwargs = dict(organization_id=uuid4(), character_id=uuid4())
    assert OrganizationMembership(**kwargs).id != OrganizationMembership(**kwargs).id


def test_can_supply_identity():
    uid = uuid4()
    m = OrganizationMembership(organization_id=uuid4(), character_id=uuid4(), id=uid)
    assert m.id is uid
    assert replace(m, role="Cavaleiro").id == uid


def test_immutable(membership):
    with pytest.raises(FrozenInstanceError):
        membership.role = "Outro"


@pytest.mark.parametrize("field", ["id", "organization_id", "character_id"])
@pytest.mark.parametrize("bad", [None, "1234", 9, False, (), []])
def test_uuid_validation(field, bad):
    kwargs = dict(organization_id=uuid4(), character_id=uuid4())
    kwargs[field] = bad
    with pytest.raises(TypeError, match=field):
        OrganizationMembership(**kwargs)


@pytest.mark.parametrize("field", ["role", "rank", "notes"])
@pytest.mark.parametrize("bad", [9, False, (), [], {}, b"A"])
def test_text_validation(field, bad):
    kwargs = dict(organization_id=uuid4(), character_id=uuid4())
    kwargs[field] = bad
    with pytest.raises(TypeError, match=field):
        OrganizationMembership(**kwargs)


@pytest.mark.parametrize("field", ["role", "rank", "notes"])
@pytest.mark.parametrize("blank", ["", " ", "\t\n "])
def test_empty_optional_text_normalized(field, blank):
    kwargs = dict(organization_id=uuid4(), character_id=uuid4())
    kwargs[field] = blank
    assert getattr(OrganizationMembership(**kwargs), field) is None


def test_unicode_trimmed_and_multiline():
    m = OrganizationMembership(
        organization_id=uuid4(), character_id=uuid4(),
        role="  Sumô-sacerdote de Mezena  ", rank="  🜁 ",
        notes="  Nota 1\n\nNota 2  ",
    )
    assert m.role == "Sumô-sacerdote de Mezena"
    assert m.rank == "🜁"
    assert m.notes == "Nota 1\n\nNota 2"


@pytest.mark.parametrize("field", ["start_year", "end_year"])
@pytest.mark.parametrize("bad", [False, True, 1.2, "67", [], (), {}])
def test_year_types(field, bad):
    kwargs = dict(organization_id=uuid4(), character_id=uuid4())
    kwargs[field] = bad
    with pytest.raises(TypeError, match=field):
        OrganizationMembership(**kwargs)


def test_fictional_negative_years():
    m = OrganizationMembership(
        organization_id=uuid4(), character_id=uuid4(),
        start_year=-50, end_year=-1,
    )
    assert m.is_active_at(-50)
    assert m.is_active_at(-1)
    assert not m.is_active_at(0)


def test_invalid_period():
    with pytest.raises(ValueError, match="end_year"):
        OrganizationMembership(
            organization_id=uuid4(), character_id=uuid4(),
            start_year=67, end_year=66,
        )


def test_one_year_membership():
    m = OrganizationMembership(
        organization_id=uuid4(), character_id=uuid4(),
        start_year=67, end_year=67,
    )
    assert m.is_active_at(67)
    assert not m.is_active_at(66)
    assert not m.is_active_at(68)


def test_open_period():
    m = OrganizationMembership(organization_id=uuid4(), character_id=uuid4())
    assert m.is_active_at(-90000)
    assert m.is_active_at(90000)


@pytest.mark.parametrize("year", [None, True, 1.0, "67", (), [], {}])
def test_is_active_strict_type(membership, year):
    with pytest.raises(TypeError, match="year"):
        membership.is_active_at(year)


def test_bounded_period(membership):
    assert not membership.is_active_at(34)
    assert membership.is_active_at(35)
    assert membership.is_active_at(60)
    assert membership.is_active_at(67)
    assert not membership.is_active_at(68)


def test_json_roundtrip(membership):
    obj = membership.to_dict()
    assert set(obj) == {f.name for f in fields(OrganizationMembership)}
    assert isinstance(obj["organization_id"], str)
    assert isinstance(obj["character_id"], str)
    assert isinstance(obj["id"], str)
    restored = OrganizationMembership.from_dict(json.loads(json.dumps(obj, ensure_ascii=False)))
    assert restored == membership
    assert restored.id == membership.id


def test_from_dict_optional_fields_missing(membership):
    data = {k: v for k, v in membership.to_dict().items()
            if k in ("id", "organization_id", "character_id")}
    m = OrganizationMembership.from_dict(data)
    assert m.role is m.rank is m.start_year is m.end_year is m.notes is None


@pytest.mark.parametrize("bad", [None, 5, False, "hi", [], ()])
def test_from_dict_rejects_wrong_container(bad):
    with pytest.raises(TypeError):
        OrganizationMembership.from_dict(bad)


@pytest.mark.parametrize("missing", ["id", "organization_id", "character_id"])
def test_from_dict_requires_reference(membership, missing):
    data = membership.to_dict()
    del data[missing]
    with pytest.raises(ValueError, match="ausentes"):
        OrganizationMembership.from_dict(data)


def test_from_dict_rejects_extras(membership):
    data = membership.to_dict()
    data["bogus"] = "x"
    with pytest.raises(ValueError, match="desconhecidos"):
        OrganizationMembership.from_dict(data)


@pytest.mark.parametrize("field", ["id", "organization_id", "character_id"])
@pytest.mark.parametrize("bad", [None, 123, "invalid", "", False])
def test_from_dict_bad_ids(membership, field, bad):
    data = membership.to_dict()
    data[field] = bad
    with pytest.raises((TypeError, ValueError), match=field):
        OrganizationMembership.from_dict(data)


def test_from_dict_rejects_invalid_year(membership):
    data = membership.to_dict()
    data["start_year"] = True
    with pytest.raises(TypeError, match="start_year"):
        OrganizationMembership.from_dict(data)


def test_from_dict_rejects_period(membership):
    data = membership.to_dict()
    data["start_year"] = 100
    with pytest.raises(ValueError, match="end_year"):
        OrganizationMembership.from_dict(data)


def test_constructor_does_not_claim_references_exist():
    m = OrganizationMembership(organization_id=uuid4(), character_id=uuid4())
    assert m.organization_id != m.character_id


def test_to_dict_is_new_instance(membership):
    obj = membership.to_dict()
    obj["notes"] = "alterada"
    assert membership.notes == "Primeira parte.\n\nSegunda parte."


def test_replace_revalidates(membership):
    with pytest.raises(ValueError):
        replace(membership, start_year=100)
    assert replace(membership, role="  Sacerdote ").role == "Sacerdote"
