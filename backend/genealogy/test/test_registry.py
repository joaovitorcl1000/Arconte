"""Testes de OrganizationRegistry: integração sem alterar Project/Storage.

Rodar na raiz backend/genealogy:
    python3 -m pytest test/test_registry.py -v
"""
from __future__ import annotations

from dataclasses import replace
import json
from uuid import uuid4

import pytest

from character.character import Character
from family.family import Family, FamilyRegistry, FamilyMembership
from genealogy.genealogy import Genealogy
from organization.membership import OrganizationMembership
from organization.organization import Organization, OrganizationType
from organization.registry import OrganizationRegistry


@pytest.fixture
def world():
    genealogy = Genealogy()
    boros = Character(name="Boros", surname="Hauck", birth_year=2, death_year=63)
    aioria = Character(name="Aioria", surname="Hauck", birth_year=46)
    manohar = Character(name="Manohar", surname="Hauck")
    for person in (boros, aioria, manohar):
        genealogy.add_character(person)
    registry = OrganizationRegistry(genealogy)
    order = Organization(
        name="Ordem de Mezena", type=OrganizationType.RELIGIOUS_ORDER,
        founder_id=boros.id, founded_year=12, dissolved_year=90,
    )
    guild = Organization(
        name="Guilda dos Mercadores", type=OrganizationType.GUILD,
        founded_year=-100,
    )
    registry.add_organization(order)
    registry.add_organization(guild)
    return genealogy, registry, (boros, aioria, manohar), (order, guild)


def _member(org, character, **kwargs):
    return OrganizationMembership(
        organization_id=org.id, character_id=character.id, **kwargs
    )


def test_registry_rejects_wrong_genealogy():
    with pytest.raises(TypeError):
        OrganizationRegistry(None)
    with pytest.raises(TypeError):
        OrganizationRegistry("Genealogy")


def test_empty_registry():
    reg = OrganizationRegistry(Genealogy())
    assert reg.get_all_organizations() == ()
    assert reg.get_memberships() == ()
    assert reg.to_dict() == {"organizations": [], "memberships": []}
    reg.validate_integrity()


def test_existing_organizations(world):
    _, reg, _, (order, guild) = world
    assert reg.get_organization(order.id) is order
    assert {o.id for o in reg.get_all_organizations()} == {order.id, guild.id}
    assert reg.get_memberships() == ()


def test_founder_is_not_automatically_member(world):
    _, reg, (boros, _, _), (order, _) = world
    assert order.founder_id == boros.id
    assert reg.get_members(order.id) == ()
    assert reg.get_organizations_for_character(boros.id) == ()


def test_rejects_org_nonobject(world):
    _, reg, _, _ = world
    with pytest.raises(TypeError):
        reg.add_organization({"name": "X"})
    with pytest.raises(TypeError):
        reg.update_organization("X")


def test_org_duplicate_id(world):
    _, reg, _, (order, _) = world
    with pytest.raises(ValueError, match="id"):
        reg.add_organization(replace(order, name="Outra"))


def test_org_unknown_founder(world):
    _, reg, _, _ = world
    org = Organization(name="Outra", founder_id=uuid4())
    before = reg.get_all_organizations()
    with pytest.raises(KeyError):
        reg.add_organization(org)
    assert reg.get_all_organizations() == before


def test_org_founder_can_be_none(world):
    _, reg, _, _ = world
    org = Organization(name="Sem fundador")
    reg.add_organization(org)
    assert reg.get_organization(org.id) == org


def test_update_org_keeps_memberships(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, start_year=60)
    reg.add_membership(m)
    updated = replace(order, motto="Verdade acima de tudo")
    reg.update_organization(updated)
    assert reg.get_organization(order.id) == updated
    assert reg.get_membership(m.id) == m


def test_update_org_rejects_new_unknown_founder(world):
    _, reg, _, (order, _) = world
    with pytest.raises(KeyError):
        reg.update_organization(replace(order, founder_id=uuid4()))
    assert reg.get_organization(order.id) is order


def test_update_org_rejects_incompatible_timeline(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, start_year=60, end_year=70)
    reg.add_membership(m)
    with pytest.raises(ValueError, match="Período"):
        reg.update_organization(replace(order, dissolved_year=65))
    assert reg.get_organization(order.id) is order
    assert reg.get_membership(m.id) == m


def test_remove_org_cascades_only_its_memberships(world):
    genealogy, reg, (boros, aioria, _), (order, guild) = world
    m1 = _member(order, aioria)
    m2 = _member(guild, aioria)
    reg.add_membership(m1)
    reg.add_membership(m2)
    removed = reg.remove_organization(order.id)
    assert removed == order
    assert reg.get_memberships() == (m2,)
    assert reg.get_organization(guild.id) == guild
    assert genealogy.get_character(boros.id) == boros
    assert genealogy.get_character(aioria.id) == aioria
    reg.validate_integrity()


@pytest.mark.parametrize("bad", [None, "no", 3, False, {}, ()])
def test_bad_organization_lookup(world, bad):
    _, reg, _, _ = world
    with pytest.raises(TypeError, match="organization_id"):
        reg.get_organization(bad)


def test_missing_organization_lookup(world):
    _, reg, _, _ = world
    with pytest.raises(KeyError):
        reg.get_organization(uuid4())


def test_org_list_is_sorted():
    reg = OrganizationRegistry(Genealogy())
    for name in ("Zeta", "álfa", "alpha", "Beta", "Alpha"):
        reg.add_organization(Organization(name=name))
    assert [o.name.casefold() for o in reg.get_all_organizations()] == sorted(
        (name.casefold() for name in ("Zeta", "álfa", "alpha", "Beta", "Alpha"))
    )


def test_add_membership_and_get(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, role="Cavaleiro", start_year=67)
    reg.add_membership(m)
    assert reg.get_membership(m.id) is m
    assert reg.get_members(order.id) == (aioria,)
    assert reg.get_organizations_for_character(aioria.id) == (order,)
    reg.validate_integrity()


def test_member_does_not_create_parenthood_or_family(world):
    genealogy, reg, (boros, aioria, _), (order, _) = world
    reg.add_membership(_member(order, aioria))
    assert genealogy.get_all_characters() == tuple(sorted((boros, aioria, world[2][2]),
            key=lambda p: (p.full_name.casefold(), str(p.id))))
    assert genealogy.get_relationships() == ()


def test_family_membership_untouched(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    fam = Family(name="Casa Hauck")
    fam_registry = FamilyRegistry(genealogy)
    fam_registry.add_family(fam)
    fm = FamilyMembership(family_id=fam.id, character_id=aioria.id)
    fam_registry.add_membership(fm)
    reg.add_membership(_member(order, aioria))
    assert fam_registry.get_memberships() == (fm,)


def test_add_rejects_wrong_type(world):
    _, reg, _, _ = world
    with pytest.raises(TypeError):
        reg.add_membership("bad")
    with pytest.raises(TypeError):
        reg.update_membership(23)


def test_add_rejects_unknown_org(world):
    _, reg, (_, aioria, _), _ = world
    m = OrganizationMembership(organization_id=uuid4(), character_id=aioria.id)
    with pytest.raises(KeyError):
        reg.add_membership(m)
    assert reg.get_memberships() == ()


def test_add_rejects_unknown_character(world):
    _, reg, _, (order, _) = world
    m = OrganizationMembership(organization_id=order.id, character_id=uuid4())
    with pytest.raises(KeyError):
        reg.add_membership(m)
    assert reg.get_memberships() == ()


def test_add_rejects_duplicate_uuid(world):
    _, reg, (_, aioria, manohar), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    with pytest.raises(ValueError, match="id"):
        reg.add_membership(replace(m, character_id=manohar.id))
    assert reg.get_memberships() == (m,)


def test_add_rejects_same_semantic_membership(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, role="Cavaleiro", start_year=50, end_year=60)
    reg.add_membership(m)
    with pytest.raises(ValueError, match="já foi cadastrada"):
        reg.add_membership(_member(order, aioria, role="Cavaleiro", start_year=50,
                                   end_year=60, notes="texto diferente"))
    assert reg.get_memberships() == (m,)


def test_allows_different_roles_in_same_year(world):
    _, reg, (_, aioria, _), (order, _) = world
    m1 = _member(order, aioria, role="Cavaleiro", start_year=60, end_year=67)
    m2 = _member(order, aioria, role="Tesoureiro", start_year=60, end_year=67)
    reg.add_membership(m1)
    reg.add_membership(m2)
    assert set(reg.get_memberships()) == {m1, m2}
    assert reg.get_members(order.id) == (aioria,)


def test_allows_promotions_with_successive_periods(world):
    _, reg, (_, aioria, _), (order, _) = world
    reg.add_membership(_member(order, aioria, role="Escudeiro", start_year=60, end_year=62))
    reg.add_membership(_member(order, aioria, role="Cavaleiro", start_year=63))
    assert reg.get_members(order.id, at_year=61)[0] == aioria
    assert reg.get_members(order.id, at_year=67)[0] == aioria


@pytest.mark.parametrize("start,end", [(10, None), (None, 100), (91, None),
                                        (None, 11), (10, 100)])
def test_rejects_membership_outside_org_lifetime(world, start, end):
    _, reg, (_, aioria, _), (order, _) = world
    with pytest.raises(ValueError, match="Período"):
        reg.add_membership(_member(order, aioria, start_year=start, end_year=end))


def test_lifetime_edges_inclusive(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, start_year=12, end_year=90)
    reg.add_membership(m)
    assert reg.get_memberships(at_year=12) == (m,)
    assert reg.get_memberships(at_year=90) == (m,)
    assert reg.get_memberships(at_year=91) == ()


def test_undated_membership_respects_org_life(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    assert reg.get_memberships(at_year=11) == ()
    assert reg.get_memberships(at_year=12) == (m,)
    assert reg.get_memberships(at_year=91) == ()


def test_remove_member_keeps_character(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    assert reg.remove_membership(m.id) == m
    assert reg.get_memberships() == ()
    assert genealogy.get_character(aioria.id) == aioria
    reg.validate_integrity()


def test_remove_unknown_member(world):
    _, reg, _, _ = world
    with pytest.raises(KeyError):
        reg.remove_membership(uuid4())


def test_update_member_keeps_id_and_indexes(world):
    _, reg, (_, aioria, manohar), (order, guild) = world
    original = _member(order, aioria, role="Membro", start_year=50)
    reg.add_membership(original)
    new = replace(original, organization_id=guild.id, character_id=manohar.id,
                  role="Mestre", start_year=60, notes="promoção")
    reg.update_membership(new)
    assert reg.get_memberships(organization_id=order.id) == ()
    assert reg.get_memberships(character_id=aioria.id) == ()
    assert reg.get_memberships(organization_id=guild.id) == (new,)
    assert reg.get_memberships(character_id=manohar.id) == (new,)
    reg.validate_integrity()


def test_update_member_rejects_missing(world):
    _, reg, (_, aioria, _), (order, _) = world
    with pytest.raises(KeyError):
        reg.update_membership(_member(order, aioria))


def test_update_member_rejects_semantic_duplicate_and_keeps_old(world):
    _, reg, (_, aioria, _), (order, _) = world
    m1 = _member(order, aioria, role="Cavaleiro", start_year=60)
    m2 = _member(order, aioria, role="Mestre", start_year=60)
    reg.add_membership(m1)
    reg.add_membership(m2)
    with pytest.raises(ValueError, match="cadastrada"):
        reg.update_membership(replace(m2, role="Cavaleiro"))
    assert set(reg.get_memberships()) == {m1, m2}
    reg.validate_integrity()


def test_update_member_rejects_invalid_period_without_mutation(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria, start_year=20)
    reg.add_membership(m)
    with pytest.raises(ValueError):
        reg.update_membership(replace(m, start_year=11))
    assert reg.get_membership(m.id) is m


def test_update_member_rejects_unknown_org_and_person(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    with pytest.raises(KeyError):
        reg.update_membership(replace(m, organization_id=uuid4()))
    with pytest.raises(KeyError):
        reg.update_membership(replace(m, character_id=uuid4()))
    assert reg.get_membership(m.id) is m
    reg.validate_integrity()


def test_get_memberships_multiple_filters(world):
    _, reg, (boros, aioria, manohar), (order, guild) = world
    m1 = _member(order, aioria, role="Cavaleiro", start_year=62, end_year=65)
    m2 = _member(order, manohar, role="Sumo-sacerdote", start_year=66)
    m3 = _member(guild, aioria, role="Mercador")
    for m in (m1, m2, m3):
        reg.add_membership(m)
    assert reg.get_memberships(organization_id=order.id, role="  CAVALEIRO  ") == (m1,)
    assert reg.get_memberships(character_id=aioria.id, organization_id=order.id) == (m1,)
    assert reg.get_memberships(at_year=67, organization_id=order.id) == (m2,)
    assert reg.get_memberships(organization_id=guild.id) == (m3,)
    assert reg.get_memberships(role="Sumo-sacerdote") == (m2,)
    assert reg.get_memberships(role="Sumo-sacerdote", character_id=boros.id) == ()


@pytest.mark.parametrize("bad", [True, 2.0, "67", [], {}, ()])
def test_year_filter_rejects_non_int(world, bad):
    _, reg, _, _ = world
    with pytest.raises(TypeError):
        reg.get_memberships(at_year=bad)


@pytest.mark.parametrize("bad", [True, 4, [], {}, (), "", "  "])
def test_role_filter_rejects_invalid(world, bad):
    _, reg, _, _ = world
    with pytest.raises((TypeError, ValueError)):
        reg.get_memberships(role=bad)


def test_unknown_org_filter_is_error(world):
    _, reg, _, _ = world
    with pytest.raises(KeyError):
        reg.get_memberships(organization_id=uuid4())


def test_unknown_character_filter_is_error(world):
    _, reg, _, _ = world
    with pytest.raises(KeyError):
        reg.get_memberships(character_id=uuid4())


def test_members_are_unique_and_ordered(world):
    _, reg, (boros, aioria, manohar), (order, _) = world
    reg.add_membership(_member(order, manohar, role="Sacerdote"))
    reg.add_membership(_member(order, aioria, role="Conselheiro"))
    reg.add_membership(_member(order, aioria, role="Cavaleiro"))
    assert reg.get_members(order.id) == (aioria, manohar)


def test_organizations_for_character_are_unique_and_ordered(world):
    _, reg, (_, aioria, _), (order, guild) = world
    reg.add_membership(_member(order, aioria, role="Membro"))
    reg.add_membership(_member(order, aioria, role="Conselheiro"))
    reg.add_membership(_member(guild, aioria))
    assert reg.get_organizations_for_character(aioria.id) == tuple(sorted(
        (order, guild), key=lambda org: (org.name.casefold(), str(org.id))
    ))


def test_remove_character_memberships(world):
    _, reg, (boros, aioria, _), (order, guild) = world
    m1 = _member(order, aioria)
    m2 = _member(guild, aioria)
    reg.add_membership(m1)
    reg.add_membership(m2)
    assert set(reg.remove_character_memberships(aioria.id)) == {m1, m2}
    assert reg.get_memberships() == ()
    assert reg.get_organization(order.id).founder_id == boros.id
    reg.validate_integrity()


def test_remove_character_references_rejects_founder(world):
    _, reg, (boros, _, _), (order, _) = world
    m = _member(order, boros)
    reg.add_membership(m)
    with pytest.raises(ValueError, match="fundador"):
        reg.remove_character_references(boros.id)
    assert reg.get_membership(m.id) == m
    assert reg.get_organization(order.id).founder_id == boros.id


def test_remove_character_references_clear_founder(world):
    _, reg, (boros, aioria, _), (order, guild) = world
    m1 = _member(order, boros)
    m2 = _member(guild, boros)
    m3 = _member(guild, aioria)
    for m in (m1, m2, m3):
        reg.add_membership(m)
    assert set(reg.remove_character_references(boros.id, founder_policy="clear")) == {m1, m2}
    assert reg.get_organization(order.id).founder_id is None
    assert reg.get_memberships() == (m3,)
    reg.validate_integrity()


@pytest.mark.parametrize("bad", ["unknown", "", None, True, []])
def test_remove_character_references_bad_policy_no_changes(world, bad):
    _, reg, (boros, _, _), (order, _) = world
    with pytest.raises(ValueError, match="founder_policy"):
        reg.remove_character_references(boros.id, founder_policy=bad)
    assert reg.get_organization(order.id).founder_id == boros.id


def test_out_of_band_genealogy_remove_detected(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    reg.add_membership(_member(order, aioria))
    genealogy.remove_character(aioria.id)
    with pytest.raises(ValueError, match="Referência"):
        reg.validate_integrity()


def test_out_of_band_founder_remove_detected(world):
    genealogy, reg, (boros, _, _), _, = world
    genealogy.remove_character(boros.id)
    with pytest.raises(ValueError, match="Referência"):
        reg.validate_integrity()


def test_integrity_corrupted_index_detected(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    reg._memberships_by_organization[order.id].clear()
    with pytest.raises(ValueError, match="Índices"):
        reg.validate_integrity()


def test_json_roundtrip(world):
    genealogy, reg, (_, aioria, manohar), (order, guild) = world
    m1 = _member(order, aioria, role="Sacerdote", start_year=60, end_year=65)
    m2 = _member(guild, manohar, rank="Mestre", notes="Notas\n\nlongas")
    reg.add_membership(m1)
    reg.add_membership(m2)
    data = reg.to_dict()
    copied = json.loads(json.dumps(data, ensure_ascii=False))
    restored = OrganizationRegistry.from_dict(genealogy, copied)
    assert restored.to_dict() == data
    assert restored.get_organization(order.id) == order
    assert restored.get_membership(m1.id) == m1
    restored.validate_integrity()


def test_from_dict_empty():
    genealogy = Genealogy()
    restored = OrganizationRegistry.from_dict(genealogy, {
        "organizations": [], "memberships": [],
    })
    assert restored.to_dict() == {"organizations": [], "memberships": []}


@pytest.mark.parametrize("bad", [None, False, 4, "json", [], ()])
def test_from_dict_wrong_container(bad):
    with pytest.raises(TypeError):
        OrganizationRegistry.from_dict(Genealogy(), bad)


@pytest.mark.parametrize("bad", [
    {}, {"organizations": []}, {"memberships": []},
    {"organizations": [], "memberships": [], "extra": 3},
])
def test_from_dict_bad_fields(bad):
    with pytest.raises(ValueError, match="Campos"):
        OrganizationRegistry.from_dict(Genealogy(), bad)


@pytest.mark.parametrize("field, bad", [
    ("organizations", ()), ("organizations", {}), ("organizations", None),
    ("memberships", ()), ("memberships", {}), ("memberships", None),
])
def test_from_dict_list_checks(field, bad):
    data = {"organizations": [], "memberships": []}
    data[field] = bad
    with pytest.raises(TypeError, match=field):
        OrganizationRegistry.from_dict(Genealogy(), data)


def test_from_dict_unknown_reference_rejected(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    m = OrganizationMembership(organization_id=uuid4(), character_id=aioria.id)
    data = {"organizations": [order.to_dict()], "memberships": [m.to_dict()]}
    with pytest.raises(KeyError):
        OrganizationRegistry.from_dict(genealogy, data)


def test_from_dict_unknown_founder_rejected(world):
    genealogy, reg, _, _ = world
    org = Organization(name="Ordem", founder_id=uuid4())
    with pytest.raises(KeyError):
        OrganizationRegistry.from_dict(genealogy, {
            "organizations": [org.to_dict()], "memberships": []
        })


def test_from_dict_rejects_duplicate_organizations(world):
    genealogy, reg, _, (order, _) = world
    with pytest.raises(ValueError, match="id"):
        OrganizationRegistry.from_dict(genealogy, {
            "organizations": [order.to_dict(), order.to_dict()], "memberships": []
        })


def test_from_dict_rejects_duplicate_memberships(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    with pytest.raises(ValueError, match="id"):
        OrganizationRegistry.from_dict(genealogy, {
            "organizations": [order.to_dict()], "memberships": [m.to_dict(), m.to_dict()]
        })


def test_changing_role_does_not_change_person(world):
    genealogy, reg, (_, aioria, _), (order, _) = world
    original = genealogy.get_character(aioria.id)
    m = _member(order, aioria, role="Cavaleiro")
    reg.add_membership(m)
    reg.update_membership(replace(m, role="Grão-mestre"))
    assert genealogy.get_character(aioria.id) is original
    assert reg.get_membership(m.id).role == "Grão-mestre"


def test_get_member_with_late_org_existence_is_filtered(world):
    _, reg, (_, aioria, _), (order, _) = world
    m = _member(order, aioria)
    reg.add_membership(m)
    assert reg.get_members(order.id, at_year=0) == ()
    assert reg.get_members(order.id, at_year=50) == (aioria,)
