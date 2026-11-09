"""Testes de Family, FamilyMembership e FamilyRegistry do Arconte.

Execute a partir da pasta ``backend/genealogy``::

    python3 -m pytest test/test_family.py -v
    python3 -m pytest test/ -q

Os testes usam dados em memória e não alteram JSONs ou bancos de dados.
Compatível com Python 3.10+ e pytest.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
from uuid import UUID, uuid4

import pytest

# Permite executar com "pytest" ou "python3 -m pytest" a partir da raiz.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from character.character import Character
from family.family import (
    Family,
    FamilyMembership,
    FamilyRegistry,
    FamilyType,
    MembershipOrigin,
)
from genealogy.genealogy import Genealogy
from relationship.relationship import Relationship, RelationshipType


@pytest.fixture
def people() -> tuple[Genealogy, dict[str, Character]]:
    genealogy = Genealogy()
    characters = {
        name: Character(name=name)
        for name in ("Álvaro", "Beatriz", "Caio", "Dália", "Érico", "Zoe")
    }
    for character in characters.values():
        genealogy.add_character(character)
    return genealogy, characters


@pytest.fixture
def context(
    people: tuple[Genealogy, dict[str, Character]],
) -> tuple[Genealogy, dict[str, Character], FamilyRegistry, dict[str, Family]]:
    genealogy, characters = people
    registry = FamilyRegistry(genealogy)
    families = {
        "valerian": Family(
            name="Valerian",
            type=FamilyType.HOUSE,
            founder_id=characters["Álvaro"].id,
            founded_year=-600,
            motto=" Honra e coragem ",
        ),
        "drakon": Family(
            name="Drakon", type=FamilyType.DYNASTY, founded_year=-550
        ),
        "aurora": Family(name="Aurora", type=FamilyType.CLAN),
    }
    for family in families.values():
        registry.add_family(family)
    return genealogy, characters, registry, families


def membership(
    family: Family,
    character: Character,
    *,
    origin: MembershipOrigin = MembershipOrigin.AFFILIATION,
    start_year: int | None = None,
    end_year: int | None = None,
    role: str | None = None,
) -> FamilyMembership:
    return FamilyMembership(
        family_id=family.id,
        character_id=character.id,
        origin=origin,
        start_year=start_year,
        end_year=end_year,
        role=role,
    )


# ---------------------------------------------------------------------------
# Tipos e entidade Family
# ---------------------------------------------------------------------------


def test_family_type_values_are_stable() -> None:
    assert {item.value for item in FamilyType} == {
        "family", "house", "clan", "dynasty"
    }


def test_membership_origin_values_are_stable() -> None:
    assert {item.value for item in MembershipOrigin} == {
        "birth", "adoption", "marriage", "foundation", "affiliation"
    }


@pytest.mark.parametrize("kind", list(FamilyType))
def test_family_accepts_every_type(kind: FamilyType) -> None:
    family = Family(name="Casa de Érion", type=kind)
    assert family.type is kind
    assert family.founder_id is None
    assert family.founded_year is None
    assert family.dissolved_year is None


def test_family_defaults_uuid_and_type() -> None:
    first = Family(name="Alvorada")
    second = Family(name="Alvorada")
    assert first.type is FamilyType.FAMILY
    assert isinstance(first.id, UUID)
    assert first.id != second.id
    assert str(first) == "Alvorada"


def test_family_normalizes_text_and_preserves_unicode() -> None:
    family = Family(
        name="  Casa Áurea ✨  ",
        motto="  Pela aurora  ",
        description="  Tradição antiga.  ",
    )
    assert family.name == "Casa Áurea ✨"
    assert family.motto == "Pela aurora"
    assert family.description == "Tradição antiga."


def test_family_turns_empty_optional_text_into_none() -> None:
    family = Family(name="Érion", motto="  ", description="")
    assert family.motto is None
    assert family.description is None


def test_family_accepts_fictional_negative_years_and_founder() -> None:
    founder_id = uuid4()
    family = Family(
        name="Primeira Dinastia",
        founder_id=founder_id,
        founded_year=-1200,
        dissolved_year=-900,
    )
    assert family.founder_id == founder_id
    assert family.founded_year == -1200
    assert family.dissolved_year == -900


def test_family_allows_equal_start_and_end_year() -> None:
    family = Family(name="Breve", founded_year=100, dissolved_year=100)
    assert family.founded_year == family.dissolved_year


@pytest.mark.parametrize("name", ["", "   ", None, 42, True])
def test_family_rejects_invalid_name(name: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        Family(name=name)


@pytest.mark.parametrize("kind", ["house", "invalid", None, 123])
def test_family_rejects_invalid_type(kind: object) -> None:
    with pytest.raises(TypeError):
        Family(name="Valerian", type=kind)


@pytest.mark.parametrize("field_name", ["id", "founder_id"])
@pytest.mark.parametrize("invalid", ["bad-id", 13, None])
def test_family_rejects_invalid_uuid_fields(
    field_name: str, invalid: object,
) -> None:
    if field_name == "founder_id" and invalid is None:
        # None is deliberately allowed for unknown founders.
        assert Family(name="Sem fundador", founder_id=None).founder_id is None
    else:
        with pytest.raises(TypeError):
            Family(name="Valerian", **{field_name: invalid})


@pytest.mark.parametrize("field_name", ["motto", "description"])
@pytest.mark.parametrize("invalid", [123, False, []])
def test_family_rejects_invalid_optional_text(
    field_name: str, invalid: object,
) -> None:
    with pytest.raises(TypeError):
        Family(name="Valerian", **{field_name: invalid})


@pytest.mark.parametrize("field_name", ["founded_year", "dissolved_year"])
@pytest.mark.parametrize("invalid", [True, 1.5, "-500"])
def test_family_rejects_invalid_years(
    field_name: str, invalid: object,
) -> None:
    with pytest.raises(TypeError):
        Family(name="Valerian", **{field_name: invalid})


def test_family_rejects_dissolution_before_foundation() -> None:
    with pytest.raises(ValueError):
        Family(name="Drakon", founded_year=150, dissolved_year=120)


def test_family_is_immutable_but_replace_preserves_identity() -> None:
    family = Family(name="Valerian", motto="Antigo")
    with pytest.raises(FrozenInstanceError):
        family.name = "Outro"
    updated = replace(family, name="Valerian II", motto="Novo")
    assert updated.id == family.id
    assert updated.name == "Valerian II"
    assert family.name == "Valerian"


def test_replacing_family_rechecks_validation() -> None:
    family = Family(name="Valerian", founded_year=100)
    with pytest.raises(ValueError):
        replace(family, dissolved_year=50)


# ---------------------------------------------------------------------------
# Entidade FamilyMembership: estados, datas e validações
# ---------------------------------------------------------------------------


def test_membership_defaults_and_uuid_generation() -> None:
    family_id, character_id = uuid4(), uuid4()
    one = FamilyMembership(family_id=family_id, character_id=character_id)
    two = FamilyMembership(family_id=family_id, character_id=character_id)
    assert one.origin is MembershipOrigin.AFFILIATION
    assert one.role is None
    assert one.start_year is None
    assert one.end_year is None
    assert one.id != two.id


@pytest.mark.parametrize("origin", list(MembershipOrigin))
def test_membership_accepts_every_origin(origin: MembershipOrigin) -> None:
    item = FamilyMembership(family_id=uuid4(), character_id=uuid4(), origin=origin)
    assert item.origin is origin


def test_membership_normalizes_role_and_accepts_negative_years() -> None:
    item = FamilyMembership(
        family_id=uuid4(), character_id=uuid4(),
        role="  Rainha  ", start_year=-120, end_year=-90,
    )
    assert item.role == "Rainha"
    assert item.start_year == -120
    assert item.end_year == -90
    assert FamilyMembership(family_id=uuid4(), character_id=uuid4(), role=" ").role is None


@pytest.mark.parametrize("field_name", ["id", "family_id", "character_id"])
@pytest.mark.parametrize("invalid", ["not-a-uuid", 42, None])
def test_membership_rejects_invalid_uuid_fields(
    field_name: str, invalid: object,
) -> None:
    with pytest.raises(TypeError):
        FamilyMembership(
            family_id=uuid4(), character_id=uuid4(), **{field_name: invalid}
        )


@pytest.mark.parametrize("invalid", ["birth", None, True, 5])
def test_membership_rejects_invalid_origin(invalid: object) -> None:
    with pytest.raises(TypeError):
        FamilyMembership(family_id=uuid4(), character_id=uuid4(), origin=invalid)


@pytest.mark.parametrize("invalid", [1, False, [], {}])
def test_membership_rejects_invalid_role(invalid: object) -> None:
    with pytest.raises(TypeError):
        FamilyMembership(family_id=uuid4(), character_id=uuid4(), role=invalid)


@pytest.mark.parametrize("field_name", ["start_year", "end_year"])
@pytest.mark.parametrize("invalid", [True, 1.4, "1450"])
def test_membership_rejects_invalid_year_fields(
    field_name: str, invalid: object,
) -> None:
    with pytest.raises(TypeError):
        FamilyMembership(
            family_id=uuid4(), character_id=uuid4(), **{field_name: invalid}
        )


def test_membership_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        FamilyMembership(
            family_id=uuid4(), character_id=uuid4(),
            start_year=50, end_year=49,
        )


@pytest.mark.parametrize(
    ("year", "expected"),
    [(99, False), (100, True), (130, True), (150, True), (151, False)],
)
def test_membership_period_is_inclusive(year: int, expected: bool) -> None:
    item = FamilyMembership(
        family_id=uuid4(), character_id=uuid4(),
        start_year=100, end_year=150,
    )
    assert item.is_active_at(year) is expected


def test_membership_open_ended_dates() -> None:
    family_id, character_id = uuid4(), uuid4()
    forever = FamilyMembership(family_id=family_id, character_id=character_id)
    until = replace(forever, end_year=-30)
    since = replace(forever, start_year=80)
    assert forever.is_active_at(-10_000)
    assert forever.is_active_at(10_000)
    assert until.is_active_at(-30)
    assert not until.is_active_at(-29)
    assert since.is_active_at(80)
    assert not since.is_active_at(79)


@pytest.mark.parametrize("invalid", [True, 1.5, "100", None])
def test_membership_active_at_rejects_invalid_year(invalid: object) -> None:
    item = FamilyMembership(family_id=uuid4(), character_id=uuid4())
    with pytest.raises(TypeError):
        item.is_active_at(invalid)


def test_membership_is_immutable_and_can_be_replaced() -> None:
    original = FamilyMembership(
        family_id=uuid4(), character_id=uuid4(), role="Herdeiro",
    )
    with pytest.raises(FrozenInstanceError):
        original.role = "Monarca"
    updated = replace(original, role="Monarca")
    assert updated.id == original.id
    assert original.role == "Herdeiro"
    assert updated.role == "Monarca"


# ---------------------------------------------------------------------------
# FamilyRegistry: construção e CRUD de famílias
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("invalid", [None, 10, {}, "genealogy"])
def test_registry_requires_genealogy(invalid: object) -> None:
    with pytest.raises(TypeError):
        FamilyRegistry(invalid)


def test_registry_starts_empty(people: tuple[Genealogy, dict[str, Character]]) -> None:
    genealogy, characters = people
    registry = FamilyRegistry(genealogy)
    assert registry.get_all_families() == ()
    assert registry.get_memberships() == ()
    assert registry.get_families_for_character(characters["Álvaro"].id) == ()
    assert registry.validate_integrity() is None


def test_registry_add_and_get_family(context) -> None:
    _, _, registry, families = context
    assert registry.get_family(families["valerian"].id) is families["valerian"]
    assert {family.id for family in registry.get_all_families()} == {
        item.id for item in families.values()
    }


def test_registry_sorts_family_names_ignoring_accents(people) -> None:
    genealogy, _ = people
    registry = FamilyRegistry(genealogy)
    for name in ("Zênite", "Árvore", "brasa", "Aliança"):
        registry.add_family(Family(name=name))
    assert [family.name for family in registry.get_all_families()] == [
        "Aliança", "Árvore", "brasa", "Zênite"
    ]


def test_registry_rejects_duplicate_family_id_without_mutation(context) -> None:
    _, _, registry, families = context
    original = registry.get_all_families()
    with pytest.raises(ValueError):
        registry.add_family(replace(families["valerian"], name="Outro nome"))
    assert registry.get_all_families() == original


def test_registry_rejects_unknown_founder_without_mutation(people) -> None:
    genealogy, _ = people
    registry = FamilyRegistry(genealogy)
    with pytest.raises(KeyError):
        registry.add_family(Family(name="Perdida", founder_id=uuid4()))
    assert registry.get_all_families() == ()


@pytest.mark.parametrize("invalid", [None, 3, "Valerian"])
def test_registry_add_family_rejects_wrong_object(people, invalid) -> None:
    genealogy, _ = people
    registry = FamilyRegistry(genealogy)
    with pytest.raises(TypeError):
        registry.add_family(invalid)


def test_registry_update_family_preserves_memberships(context) -> None:
    _, characters, registry, families = context
    val = families["valerian"]
    record = membership(val, characters["Álvaro"])
    registry.add_membership(record)
    new_family = replace(val, name="Valerian da Aurora", motto="Outro")
    registry.update_family(new_family)
    assert registry.get_family(val.id) == new_family
    assert registry.get_memberships(family_id=val.id) == (record,)


def test_registry_update_family_can_change_existing_founder(context) -> None:
    _, characters, registry, families = context
    family = families["valerian"]
    updated = replace(family, founder_id=characters["Beatriz"].id)
    registry.update_family(updated)
    assert registry.get_family(family.id).founder_id == characters["Beatriz"].id


def test_registry_update_family_rejects_unregistered_founder_without_change(context) -> None:
    _, _, registry, families = context
    current = families["valerian"]
    with pytest.raises(KeyError):
        registry.update_family(replace(current, founder_id=uuid4()))
    assert registry.get_family(current.id) == current


def test_registry_update_family_rejects_unknown_family(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(KeyError):
        registry.update_family(Family(name="Inexistente"))


def test_registry_update_family_rejects_wrong_object(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.update_family("Casa")


def test_registry_remove_family_deletes_affiliations_only(context) -> None:
    genealogy, characters, registry, families = context
    family = families["valerian"]
    item = membership(family, characters["Álvaro"])
    registry.add_membership(item)
    removed = registry.remove_family(family.id)
    assert removed == family
    assert registry.get_memberships() == ()
    assert registry.get_families_for_character(characters["Álvaro"].id) == ()
    assert genealogy.get_character(characters["Álvaro"].id) == characters["Álvaro"]
    assert registry.validate_integrity() is None


def test_registry_remove_family_preserves_other_families_memberships(context) -> None:
    _, characters, registry, families = context
    person = characters["Beatriz"]
    removed = membership(families["valerian"], person)
    retained = membership(families["drakon"], person)
    registry.add_membership(removed)
    registry.add_membership(retained)
    registry.remove_family(families["valerian"].id)
    assert registry.get_memberships(character_id=person.id) == (retained,)
    assert registry.get_memberships(family_id=families["drakon"].id) == (retained,)


@pytest.mark.parametrize("invalid", ["not-uuid", None, 123])
def test_registry_rejects_invalid_family_lookup_id(context, invalid) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.get_family(invalid)


def test_registry_rejects_missing_family_lookup_and_removal(context) -> None:
    _, _, registry, _ = context
    unknown = uuid4()
    with pytest.raises(KeyError):
        registry.get_family(unknown)
    with pytest.raises(KeyError):
        registry.remove_family(unknown)


# ---------------------------------------------------------------------------
# FamilyRegistry: CRUD de afiliações, índices e multiplicidade histórica
# ---------------------------------------------------------------------------


def test_registry_add_membership_and_get_it(context) -> None:
    _, characters, registry, families = context
    item = membership(
        families["valerian"], characters["Álvaro"],
        origin=MembershipOrigin.FOUNDATION, role="Fundador", start_year=-600,
    )
    registry.add_membership(item)
    assert registry.get_membership(item.id) == item
    assert registry.get_memberships() == (item,)
    assert registry.get_members(families["valerian"].id) == (characters["Álvaro"],)


def test_registry_membership_does_not_create_genealogical_links(context) -> None:
    genealogy, characters, registry, families = context
    registry.add_membership(membership(families["valerian"], characters["Álvaro"]))
    registry.add_membership(membership(families["valerian"], characters["Caio"]))
    assert genealogy.get_relationships() == ()
    assert genealogy.get_kinship(characters["Álvaro"].id, characters["Caio"].id).relation == "unknown"


def test_registry_accepts_simultaneous_membership_in_multiple_families(context) -> None:
    _, characters, registry, families = context
    person = characters["Dália"]
    items = [
        membership(families["valerian"], person, origin=MembershipOrigin.MARRIAGE),
        membership(families["drakon"], person, origin=MembershipOrigin.BIRTH),
        membership(families["aurora"], person),
    ]
    for item in items:
        registry.add_membership(item)
    assert {family.id for family in registry.get_families_for_character(person.id)} == {
        family.id for family in families.values()
    }
    assert {item.id for item in registry.get_memberships(character_id=person.id)} == {
        item.id for item in items
    }


def test_registry_allows_distinct_historical_periods(context) -> None:
    _, characters, registry, families = context
    first = membership(families["valerian"], characters["Beatriz"],
                       start_year=10, end_year=20, role="Princesa")
    second = membership(families["valerian"], characters["Beatriz"],
                        start_year=21, end_year=40, role="Rainha")
    registry.add_membership(first)
    registry.add_membership(second)
    assert len(registry.get_memberships(character_id=characters["Beatriz"].id)) == 2
    assert registry.get_members(families["valerian"].id) == (characters["Beatriz"],)


def test_registry_allows_distinct_origin_or_role(context) -> None:
    _, characters, registry, families = context
    family, person = families["valerian"], characters["Beatriz"]
    items = [
        membership(family, person, origin=MembershipOrigin.BIRTH, role="Membro"),
        membership(family, person, origin=MembershipOrigin.ADOPTION, role="Membro"),
        membership(family, person, origin=MembershipOrigin.BIRTH, role="Líder"),
    ]
    for item in items:
        registry.add_membership(item)
    assert set(registry.get_memberships(family_id=family.id)) == set(items)


def test_registry_rejects_duplicate_membership_id(context) -> None:
    _, characters, registry, families = context
    record = membership(families["valerian"], characters["Álvaro"])
    registry.add_membership(record)
    with pytest.raises(ValueError):
        registry.add_membership(replace(record, role="Segundo título"))
    assert registry.get_memberships() == (record,)


def test_registry_rejects_exact_duplicate_with_distinct_uuid(context) -> None:
    _, characters, registry, families = context
    record = membership(families["valerian"], characters["Álvaro"],
                        origin=MembershipOrigin.BIRTH, start_year=80)
    registry.add_membership(record)
    with pytest.raises(ValueError):
        registry.add_membership(replace(record, id=uuid4()))
    assert registry.get_memberships() == (record,)


@pytest.mark.parametrize("invalid", [None, "member", 5])
def test_registry_rejects_invalid_membership_object(context, invalid) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.add_membership(invalid)


def test_registry_rejects_membership_for_unknown_family(context) -> None:
    _, characters, registry, _ = context
    with pytest.raises(KeyError):
        registry.add_membership(FamilyMembership(
            family_id=uuid4(), character_id=characters["Caio"].id,
        ))
    assert registry.get_memberships() == ()


def test_registry_rejects_membership_for_unknown_character(context) -> None:
    _, _, registry, families = context
    with pytest.raises(KeyError):
        registry.add_membership(FamilyMembership(
            family_id=families["valerian"].id, character_id=uuid4(),
        ))
    assert registry.get_memberships() == ()


def test_registry_update_membership_role_and_period(context) -> None:
    _, characters, registry, families = context
    original = membership(families["valerian"], characters["Caio"],
                          role="Herdeiro", start_year=30)
    registry.add_membership(original)
    updated = replace(original, role="Rei", end_year=100)
    registry.update_membership(updated)
    assert registry.get_membership(original.id) == updated
    assert registry.get_memberships(family_id=families["valerian"].id) == (updated,)


def test_registry_update_membership_transfers_family_index(context) -> None:
    _, characters, registry, families = context
    old = membership(families["valerian"], characters["Beatriz"])
    registry.add_membership(old)
    new = replace(old, family_id=families["drakon"].id)
    registry.update_membership(new)
    assert registry.get_memberships(family_id=families["valerian"].id) == ()
    assert registry.get_memberships(family_id=families["drakon"].id) == (new,)
    assert registry.get_families_for_character(characters["Beatriz"].id) == (families["drakon"],)
    assert registry.validate_integrity() is None


def test_registry_update_membership_transfers_character_index(context) -> None:
    _, characters, registry, families = context
    old = membership(families["valerian"], characters["Beatriz"])
    registry.add_membership(old)
    new = replace(old, character_id=characters["Caio"].id)
    registry.update_membership(new)
    assert registry.get_memberships(character_id=characters["Beatriz"].id) == ()
    assert registry.get_memberships(character_id=characters["Caio"].id) == (new,)
    assert registry.validate_integrity() is None


def test_registry_update_membership_transfers_both_indices(context) -> None:
    _, characters, registry, families = context
    old = membership(families["valerian"], characters["Beatriz"])
    registry.add_membership(old)
    new = replace(old, family_id=families["aurora"].id,
                  character_id=characters["Dália"].id)
    registry.update_membership(new)
    assert registry.get_memberships(family_id=families["valerian"].id) == ()
    assert registry.get_memberships(character_id=characters["Beatriz"].id) == ()
    assert registry.get_memberships(family_id=families["aurora"].id) == (new,)
    assert registry.validate_integrity() is None


def test_registry_update_membership_rejects_duplicate_without_mutation(context) -> None:
    _, characters, registry, families = context
    first = membership(families["valerian"], characters["Caio"], role="A")
    second = membership(families["valerian"], characters["Caio"], role="B")
    registry.add_membership(first)
    registry.add_membership(second)
    with pytest.raises(ValueError):
        registry.update_membership(replace(second, role="A"))
    assert set(registry.get_memberships()) == {first, second}
    assert registry.validate_integrity() is None


def test_registry_update_membership_rejects_unknown_family_without_mutation(context) -> None:
    _, characters, registry, families = context
    original = membership(families["valerian"], characters["Caio"])
    registry.add_membership(original)
    with pytest.raises(KeyError):
        registry.update_membership(replace(original, family_id=uuid4()))
    assert registry.get_membership(original.id) == original
    assert registry.validate_integrity() is None


def test_registry_update_membership_rejects_unknown_character_without_mutation(context) -> None:
    _, characters, registry, families = context
    original = membership(families["valerian"], characters["Caio"])
    registry.add_membership(original)
    with pytest.raises(KeyError):
        registry.update_membership(replace(original, character_id=uuid4()))
    assert registry.get_membership(original.id) == original
    assert registry.validate_integrity() is None


def test_registry_update_membership_rejects_unknown_id(context) -> None:
    _, characters, registry, families = context
    with pytest.raises(KeyError):
        registry.update_membership(membership(families["valerian"], characters["Caio"]))


def test_registry_update_membership_rejects_wrong_object(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.update_membership(None)


def test_registry_remove_membership_preserves_family_and_character(context) -> None:
    genealogy, characters, registry, families = context
    record = membership(families["valerian"], characters["Beatriz"])
    registry.add_membership(record)
    assert registry.remove_membership(record.id) == record
    assert registry.get_memberships() == ()
    assert registry.get_family(families["valerian"].id) == families["valerian"]
    assert genealogy.get_character(characters["Beatriz"].id) == characters["Beatriz"]
    assert registry.validate_integrity() is None


def test_registry_remove_membership_keeps_other_memberships(context) -> None:
    _, characters, registry, families = context
    first = membership(families["valerian"], characters["Caio"])
    second = membership(families["drakon"], characters["Caio"])
    registry.add_membership(first)
    registry.add_membership(second)
    registry.remove_membership(first.id)
    assert registry.get_memberships() == (second,)


@pytest.mark.parametrize("invalid", [None, "bad", 99])
def test_registry_rejects_invalid_membership_lookup_id(context, invalid) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.get_membership(invalid)


def test_registry_rejects_unknown_membership_lookup_and_removal(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(KeyError):
        registry.get_membership(uuid4())
    with pytest.raises(KeyError):
        registry.remove_membership(uuid4())


# ---------------------------------------------------------------------------
# Filtros, ordenação, funções de consulta e integridade
# ---------------------------------------------------------------------------


def test_registry_membership_filtering_by_family_character_origin_and_time(context) -> None:
    _, characters, registry, families = context
    a = membership(families["valerian"], characters["Caio"],
                   origin=MembershipOrigin.BIRTH, start_year=10, end_year=20)
    b = membership(families["valerian"], characters["Caio"],
                   origin=MembershipOrigin.MARRIAGE, start_year=25, end_year=40)
    c = membership(families["drakon"], characters["Caio"],
                   origin=MembershipOrigin.BIRTH, start_year=10, end_year=60)
    d = membership(families["valerian"], characters["Dália"],
                   origin=MembershipOrigin.BIRTH, start_year=10)
    for item in (a, b, c, d):
        registry.add_membership(item)
    assert set(registry.get_memberships(family_id=families["valerian"].id)) == {a, b, d}
    assert set(registry.get_memberships(character_id=characters["Caio"].id)) == {a, b, c}
    assert set(registry.get_memberships(origin=MembershipOrigin.MARRIAGE)) == {b}
    assert set(registry.get_memberships(at_year=15)) == {a, c, d}
    assert registry.get_memberships(
        family_id=families["valerian"].id,
        character_id=characters["Caio"].id,
        origin=MembershipOrigin.BIRTH,
        at_year=20,
    ) == (a,)
    assert registry.get_memberships(
        family_id=families["drakon"].id,
        character_id=characters["Dália"].id,
    ) == ()


def test_registry_get_members_unique_and_sorted(context) -> None:
    _, characters, registry, families = context
    family = families["valerian"]
    for name in ("Zoe", "Érico", "Álvaro", "Caio"):
        registry.add_membership(membership(family, characters[name]))
    registry.add_membership(membership(
        family, characters["Caio"], origin=MembershipOrigin.BIRTH,
    ))
    assert [person.name for person in registry.get_members(family.id)] == [
        "Álvaro", "Caio", "Érico", "Zoe"
    ]
    assert isinstance(registry.get_members(family.id), tuple)


def test_registry_get_members_filters_by_origin_and_year(context) -> None:
    _, characters, registry, families = context
    family = families["valerian"]
    first = membership(family, characters["Álvaro"],
                       origin=MembershipOrigin.FOUNDATION, start_year=-500)
    second = membership(family, characters["Beatriz"],
                        origin=MembershipOrigin.MARRIAGE, start_year=-400)
    for item in (first, second):
        registry.add_membership(item)
    assert registry.get_members(family.id, at_year=-450) == (characters["Álvaro"],)
    assert registry.get_members(family.id, origin=MembershipOrigin.MARRIAGE) == (
        characters["Beatriz"],
    )


def test_registry_get_families_for_character_deduplicates(context) -> None:
    _, characters, registry, families = context
    person = characters["Caio"]
    registry.add_membership(membership(
        families["valerian"], person, origin=MembershipOrigin.BIRTH,
        start_year=10,
    ))
    registry.add_membership(membership(
        families["valerian"], person, origin=MembershipOrigin.MARRIAGE,
        start_year=20,
    ))
    registry.add_membership(membership(families["aurora"], person, start_year=30))
    assert registry.get_families_for_character(person.id, at_year=15) == (
        families["valerian"],
    )
    assert {family.id for family in registry.get_families_for_character(person.id)} == {
        families["valerian"].id, families["aurora"].id,
    }


@pytest.mark.parametrize("bad_origin", ["birth", 1, False])
def test_registry_rejects_invalid_origin_filter(context, bad_origin) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.get_memberships(origin=bad_origin)


@pytest.mark.parametrize("bad_year", ["150", True, 1.5])
def test_registry_rejects_invalid_year_filter(context, bad_year) -> None:
    _, _, registry, _ = context
    with pytest.raises(TypeError):
        registry.get_memberships(at_year=bad_year)


def test_registry_filter_rejects_unknown_family_or_character(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(KeyError):
        registry.get_memberships(family_id=uuid4())
    with pytest.raises(KeyError):
        registry.get_memberships(character_id=uuid4())


def test_registry_queries_return_read_only_tuples(context) -> None:
    _, characters, registry, families = context
    item = membership(families["valerian"], characters["Beatriz"])
    registry.add_membership(item)
    assert isinstance(registry.get_all_families(), tuple)
    assert isinstance(registry.get_memberships(), tuple)
    assert isinstance(registry.get_members(families["valerian"].id), tuple)
    assert isinstance(registry.get_families_for_character(characters["Beatriz"].id), tuple)


def test_registry_remove_character_memberships_from_all_families(context) -> None:
    genealogy, characters, registry, families = context
    person = characters["Beatriz"]
    items = [membership(family, person) for family in families.values()]
    for item in items:
        registry.add_membership(item)
    removed = registry.remove_character_memberships(person.id)
    assert set(removed) == set(items)
    assert registry.get_memberships(character_id=person.id) == ()
    assert genealogy.get_character(person.id) == person
    assert registry.validate_integrity() is None


def test_registry_remove_character_memberships_rejects_unknown_character(context) -> None:
    _, _, registry, _ = context
    with pytest.raises(KeyError):
        registry.remove_character_memberships(uuid4())


def test_registry_integrity_detects_orphan_membership_after_direct_character_delete(context) -> None:
    genealogy, characters, registry, families = context
    person = characters["Beatriz"]
    registry.add_membership(membership(families["valerian"], person))
    genealogy.remove_character(person.id)
    with pytest.raises(ValueError):
        registry.validate_integrity()


def test_registry_integrity_detects_missing_founder_after_direct_delete(context) -> None:
    genealogy, characters, registry, _ = context
    genealogy.remove_character(characters["Álvaro"].id)
    with pytest.raises(ValueError):
        registry.validate_integrity()


def test_registry_character_can_be_removed_cleanly(context) -> None:
    genealogy, characters, registry, families = context
    person = characters["Álvaro"]
    registry.add_membership(membership(families["valerian"], person))
    registry.remove_character_memberships(person.id)
    family_without_founder = replace(families["valerian"], founder_id=None)
    registry.update_family(family_without_founder)
    genealogy.remove_character(person.id)
    assert registry.validate_integrity() is None
    assert registry.get_family(families["valerian"].id).founder_id is None


def test_registry_does_not_modify_genealogical_parentage(context) -> None:
    genealogy, characters, registry, families = context
    parent = characters["Álvaro"]
    child = characters["Caio"]
    link = Relationship(
        source_id=parent.id, target_id=child.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    )
    genealogy.add_relationship(link)
    registry.add_membership(membership(families["valerian"], parent))
    registry.add_membership(membership(families["drakon"], child))
    registry.remove_family(families["valerian"].id)
    assert genealogy.get_parents(child.id) == (parent,)
    assert genealogy.get_relationship(link.id) == link


def test_registry_integrity_after_combined_updates_and_removals(context) -> None:
    _, characters, registry, families = context
    first = membership(families["valerian"], characters["Caio"], role="Membro")
    second = membership(families["drakon"], characters["Dália"], role="Chefe")
    registry.add_membership(first)
    registry.add_membership(second)
    registry.update_membership(replace(first, family_id=families["aurora"].id))
    registry.remove_membership(second.id)
    registry.remove_family(families["drakon"].id)
    assert registry.validate_integrity() is None

