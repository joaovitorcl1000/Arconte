"""Testes unitários e de integração do núcleo genealógico do Arconte.

Execute na raiz ``backend/genealogy``:

    python3 -m pytest test/ -v

Os testes não acessam banco de dados, rede ou sistema de arquivos.
Cada teste recebe uma genealogia nova para evitar interferência entre casos.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
from uuid import UUID, uuid4

import pytest

# Funciona tanto com `pytest` quanto com `python3 -m pytest`, mesmo
# que a pasta `test/` não seja um pacote Python.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from character.character import Character
from genealogy.genealogy import Genealogy, Kinship
from relationship.relationship import Relationship, RelationshipType


BIOLOGICAL = RelationshipType.BIOLOGICAL_PARENT
ADOPTIVE = RelationshipType.ADOPTIVE_PARENT
MARRIAGE = RelationshipType.MARRIAGE
PARTNERSHIP = RelationshipType.PARTNERSHIP


def create_link(
    genealogy: Genealogy,
    source: Character,
    target: Character,
    relation_type: RelationshipType = BIOLOGICAL,
    *,
    start_year: int | None = None,
    end_year: int | None = None,
) -> Relationship:
    """Cadastra uma relação entre dois personagens e a devolve."""
    relationship = Relationship(
        source_id=source.id,
        target_id=target.id,
        type=relation_type,
        start_year=start_year,
        end_year=end_year,
    )
    genealogy.add_relationship(relationship)
    return relationship


def ids(characters: tuple[Character, ...]) -> set[UUID]:
    return {character.id for character in characters}


@pytest.fixture
def genealogy() -> Genealogy:
    return Genealogy()


@pytest.fixture
def family() -> tuple[Genealogy, dict[str, Character]]:
    """Família de 4 gerações com irmãos, tios, primos e primo removido.

    Afonso + Beatriz
       ├── Bruno + Diana
       │     ├── Eduardo + Isabela
       │     │     └── Joana
       │     └── Fernanda
       └── Carla + Gabriel
             └── Helena

    Yuri é independente, sem vínculos conhecidos.
    """
    genealogy = Genealogy()
    people = {
        name: Character(name=name)
        for name in (
            "Afonso", "Beatriz", "Bruno", "Carla", "Diana", "Eduardo",
            "Fernanda", "Gabriel", "Helena", "Isabela", "Joana", "Yuri",
        )
    }
    for person in people.values():
        genealogy.add_character(person)

    for parent_name, child_name in (
        ("Afonso", "Bruno"), ("Beatriz", "Bruno"),
        ("Afonso", "Carla"), ("Beatriz", "Carla"),
        ("Bruno", "Eduardo"), ("Diana", "Eduardo"),
        ("Bruno", "Fernanda"), ("Diana", "Fernanda"),
        ("Carla", "Helena"), ("Gabriel", "Helena"),
        ("Eduardo", "Joana"), ("Isabela", "Joana"),
    ):
        create_link(genealogy, people[parent_name], people[child_name])

    for spouse_a, spouse_b in (
        ("Afonso", "Beatriz"), ("Bruno", "Diana"),
        ("Carla", "Gabriel"), ("Eduardo", "Isabela"),
    ):
        create_link(genealogy, people[spouse_a], people[spouse_b], MARRIAGE)

    return genealogy, people


# ---------------------------------------------------------------------------
# Character: criação, validação e imutabilidade
# ---------------------------------------------------------------------------


def test_character_generates_uuid_and_full_name() -> None:
    character = Character(name="  Arthur ", surname=" Valerian ")
    assert isinstance(character.id, UUID)
    assert character.name == "Arthur"
    assert character.surname == "Valerian"
    assert character.full_name == "Arthur Valerian"
    assert str(character) == "Arthur Valerian"


def test_character_accepts_unknown_fields_and_fictional_years() -> None:
    character = Character(
        name="Elena", surname=" ", gender=" ", biography=" ",
        birth_year=-200, death_year=-150,
    )
    assert character.surname is None
    assert character.gender is None
    assert character.biography is None
    assert character.birth_year == -200
    assert character.full_name == "Elena"


@pytest.mark.parametrize("invalid_name", ["", "   ", None, 123])
def test_character_rejects_invalid_names(invalid_name: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        Character(name=invalid_name)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [("surname", 10), ("gender", False), ("biography", [])],
)
def test_character_rejects_invalid_optional_text(
    field_name: str, invalid_value: object
) -> None:
    with pytest.raises(TypeError):
        Character(name="Arthur", **{field_name: invalid_value})


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [("birth_year", 1.5), ("death_year", True), ("birth_year", "100")],
)
def test_character_rejects_non_integer_years(
    field_name: str, invalid_value: object
) -> None:
    with pytest.raises(TypeError):
        Character(name="Arthur", **{field_name: invalid_value})


def test_character_rejects_death_before_birth() -> None:
    with pytest.raises(ValueError, match="death_year"):
        Character(name="Arthur", birth_year=150, death_year=100)


def test_character_rejects_invalid_uuid() -> None:
    with pytest.raises(TypeError, match="UUID"):
        Character(name="Arthur", id="not-a-uuid")


def test_character_is_immutable_but_can_be_replaced() -> None:
    original = Character(name="Arthur", biography="Rei")
    with pytest.raises(FrozenInstanceError):
        original.name = "Outro"  # type: ignore[misc]

    updated = replace(original, biography="Fundador da dinastia")
    assert original.biography == "Rei"
    assert updated.biography == "Fundador da dinastia"
    assert updated.id == original.id


# ---------------------------------------------------------------------------
# Relationship: direção, simetria, validação e datas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("relation_type", [BIOLOGICAL, ADOPTIVE])
def test_parentage_is_directed(relation_type: RelationshipType) -> None:
    parent, child = Character(name="Pai"), Character(name="Filho")
    relation = Relationship(
        source_id=parent.id, target_id=child.id, type=relation_type
    )
    assert relation.is_directed
    assert relation.connects(parent.id, child.id)
    assert not relation.connects(child.id, parent.id)


@pytest.mark.parametrize("relation_type", [MARRIAGE, PARTNERSHIP])
def test_partnership_is_symmetric(relation_type: RelationshipType) -> None:
    first, second = uuid4(), uuid4()
    direct = Relationship(source_id=first, target_id=second, type=relation_type)
    reverse = Relationship(source_id=second, target_id=first, type=relation_type)
    assert not direct.is_directed
    assert direct.connects(first, second)
    assert direct.connects(second, first)
    assert (direct.source_id, direct.target_id) == (
        reverse.source_id, reverse.target_id
    )


def test_relationship_rejects_self_connection() -> None:
    character_id = uuid4()
    with pytest.raises(ValueError):
        Relationship(
            source_id=character_id, target_id=character_id, type=BIOLOGICAL
        )


@pytest.mark.parametrize("invalid_type", ["marriage", None, 42])
def test_relationship_rejects_invalid_type(invalid_type: object) -> None:
    with pytest.raises(TypeError):
        Relationship(source_id=uuid4(), target_id=uuid4(), type=invalid_type)


def test_relationship_rejects_invalid_uuids() -> None:
    with pytest.raises(TypeError, match="UUID"):
        Relationship(source_id="abc", target_id=uuid4(), type=BIOLOGICAL)


def test_relationship_rejects_invalid_date_interval() -> None:
    with pytest.raises(ValueError, match="end_year"):
        Relationship(
            source_id=uuid4(), target_id=uuid4(), type=MARRIAGE,
            start_year=200, end_year=100,
        )


@pytest.mark.parametrize("value", [False, 3.2, "1200"])
def test_relationship_rejects_non_integer_dates(value: object) -> None:
    with pytest.raises(TypeError):
        Relationship(
            source_id=uuid4(), target_id=uuid4(), type=MARRIAGE,
            start_year=value,
        )


# ---------------------------------------------------------------------------
# Genealogy: gerenciamento de personagens e relações
# ---------------------------------------------------------------------------


def test_new_genealogy_is_empty(genealogy: Genealogy) -> None:
    assert genealogy.get_all_characters() == ()
    assert genealogy.get_relationships() == ()


def test_add_get_and_list_characters_sorted(genealogy: Genealogy) -> None:
    zelda, ana = Character(name="Zelda"), Character(name="Ana")
    genealogy.add_character(zelda)
    genealogy.add_character(ana)
    assert genealogy.get_character(ana.id) == ana
    assert genealogy.get_all_characters() == (ana, zelda)


def test_add_character_rejects_duplicate_id(genealogy: Genealogy) -> None:
    character = Character(name="Arthur")
    genealogy.add_character(character)
    with pytest.raises(ValueError, match="id"):
        genealogy.add_character(replace(character, name="Arthur II"))


def test_add_character_rejects_wrong_object(genealogy: Genealogy) -> None:
    with pytest.raises(TypeError):
        genealogy.add_character("Arthur")


def test_missing_character_and_invalid_id(genealogy: Genealogy) -> None:
    with pytest.raises(KeyError):
        genealogy.get_character(uuid4())
    with pytest.raises(TypeError):
        genealogy.get_character("123")


def test_update_character_preserves_relationships(
    genealogy: Genealogy,
) -> None:
    parent, child = Character(name="Arthur"), Character(name="Edric")
    genealogy.add_character(parent)
    genealogy.add_character(child)
    create_link(genealogy, parent, child)

    newer = replace(parent, name="Arthur II")
    genealogy.update_character(newer)
    assert genealogy.get_character(parent.id) == newer
    assert genealogy.get_children(parent.id) == (child,)


def test_updating_missing_character_is_rejected(genealogy: Genealogy) -> None:
    with pytest.raises(KeyError):
        genealogy.update_character(Character(name="Fantasma"))


def test_add_relationship_requires_registered_characters(
    genealogy: Genealogy,
) -> None:
    parent, child = Character(name="Arthur"), Character(name="Edric")
    genealogy.add_character(parent)
    relation = Relationship(
        source_id=parent.id, target_id=child.id, type=BIOLOGICAL
    )
    with pytest.raises(KeyError):
        genealogy.add_relationship(relation)
    assert genealogy.get_relationships() == ()


def test_add_relationship_rejects_wrong_object(genealogy: Genealogy) -> None:
    with pytest.raises(TypeError):
        genealogy.add_relationship("parent")


def test_duplicate_parentage_is_rejected(genealogy: Genealogy) -> None:
    first, second = Character(name="Arthur"), Character(name="Edric")
    genealogy.add_character(first)
    genealogy.add_character(second)
    create_link(genealogy, first, second)
    with pytest.raises(ValueError, match="cadastrada"):
        create_link(genealogy, first, second)
    assert len(genealogy.get_relationships()) == 1


def test_duplicate_relationship_uuid_is_rejected(genealogy: Genealogy) -> None:
    first, second = Character(name="Arthur"), Character(name="Edric")
    genealogy.add_character(first)
    genealogy.add_character(second)
    relation = create_link(genealogy, first, second)
    with pytest.raises(ValueError, match="id"):
        genealogy.add_relationship(replace(relation, type=ADOPTIVE))


def test_reverse_marriage_duplicate_is_rejected(genealogy: Genealogy) -> None:
    a, b = Character(name="Arthur"), Character(name="Elena")
    genealogy.add_character(a)
    genealogy.add_character(b)
    create_link(genealogy, a, b, MARRIAGE, start_year=1200)
    with pytest.raises(ValueError, match="cadastrada"):
        create_link(genealogy, b, a, MARRIAGE, start_year=1200)


def test_multiple_marriages_with_different_dates_are_allowed(
    genealogy: Genealogy,
) -> None:
    a, b = Character(name="Arthur"), Character(name="Elena")
    genealogy.add_character(a)
    genealogy.add_character(b)
    first = create_link(genealogy, a, b, MARRIAGE, start_year=100, end_year=110)
    second = create_link(genealogy, b, a, MARRIAGE, start_year=120)
    assert {first.id, second.id} == {
        r.id for r in genealogy.get_relationships(a.id)
    }


def test_get_relationships_filters_character_and_type(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, people = family
    afonso = people["Afonso"]
    relations = genealogy.get_relationships(afonso.id)
    assert len(relations) == 3  # 2 filiações + 1 casamento
    only_marriage = genealogy.get_relationships(afonso.id, types=[MARRIAGE])
    assert len(only_marriage) == 1
    assert only_marriage[0].type is MARRIAGE
    assert genealogy.get_relationship(only_marriage[0].id) == only_marriage[0]


def test_parentage_cycle_is_rejected_without_side_effects(
    genealogy: Genealogy,
) -> None:
    a, b, c = (Character(name=name) for name in ("A", "B", "C"))
    for character in (a, b, c):
        genealogy.add_character(character)
    create_link(genealogy, a, b)
    create_link(genealogy, b, c)
    with pytest.raises(ValueError, match="ciclo"):
        create_link(genealogy, c, a)
    assert genealogy.get_parents(a.id) == ()
    assert ids(genealogy.get_descendants(a.id)) == {b.id, c.id}
    assert len(genealogy.get_relationships()) == 2


def test_mixed_biological_adoptive_cycle_is_rejected(
    genealogy: Genealogy,
) -> None:
    a, b, c = (Character(name=name) for name in ("A", "B", "C"))
    for character in (a, b, c):
        genealogy.add_character(character)
    create_link(genealogy, a, b, ADOPTIVE)
    create_link(genealogy, b, c, BIOLOGICAL)
    with pytest.raises(ValueError, match="ciclo"):
        create_link(genealogy, c, a, ADOPTIVE)


# ---------------------------------------------------------------------------
# Genealogy: consultas genealógicas e parentescos
# ---------------------------------------------------------------------------


def test_get_parents_and_children(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    assert ids(genealogy.get_parents(p["Eduardo"].id)) == {
        p["Bruno"].id, p["Diana"].id
    }
    assert ids(genealogy.get_children(p["Bruno"].id)) == {
        p["Eduardo"].id, p["Fernanda"].id
    }


def test_get_siblings_excludes_self_and_includes_half_siblings(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    assert genealogy.get_siblings(p["Eduardo"].id) == (p["Fernanda"],)
    assert genealogy.get_siblings(p["Carla"].id) == (p["Bruno"],)


def test_ancestors_and_descendants_are_sorted_by_distance(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    ancestors = genealogy.get_ancestors(p["Joana"].id)
    assert set(ancestors) == {
        p["Eduardo"], p["Isabela"], p["Bruno"],
        p["Diana"], p["Afonso"], p["Beatriz"],
    }
    assert set(ancestors[:2]) == {p["Eduardo"], p["Isabela"]}
    assert set(ancestors[-2:]) == {p["Afonso"], p["Beatriz"]}
    assert ids(genealogy.get_descendants(p["Afonso"].id)) == {
        p["Bruno"].id, p["Carla"].id, p["Eduardo"].id,
        p["Fernanda"].id, p["Helena"].id, p["Joana"].id,
    }


def test_common_ancestors(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    assert ids(genealogy.get_common_ancestors(p["Fernanda"].id, p["Helena"].id)) == {
        p["Afonso"].id, p["Beatriz"].id
    }


def test_get_partners_is_bidirectional(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    assert genealogy.get_partners(p["Afonso"].id) == (p["Beatriz"],)
    assert genealogy.get_partners(p["Beatriz"].id) == (p["Afonso"],)
    assert genealogy.get_partners(p["Yuri"].id) == ()


@pytest.mark.parametrize(
    ("first", "second", "relation", "generation", "degree", "removed"),
    [
        ("Afonso", "Afonso", "self", None, None, None),
        ("Afonso", "Bruno", "ancestor", 1, None, None),
        ("Afonso", "Joana", "ancestor", 3, None, None),
        ("Joana", "Afonso", "descendant", 3, None, None),
        ("Bruno", "Carla", "sibling", None, None, None),
        ("Eduardo", "Fernanda", "sibling", None, None, None),
        ("Carla", "Eduardo", "aunt_uncle", None, None, 0),
        ("Eduardo", "Carla", "niece_nephew", None, None, 0),
        ("Fernanda", "Helena", "cousin", None, 1, 0),
        ("Joana", "Helena", "cousin", None, 1, 1),
        ("Yuri", "Helena", "unknown", None, None, None),
    ],
)
def test_kinship_classification(
    family: tuple[Genealogy, dict[str, Character]],
    first: str,
    second: str,
    relation: str,
    generation: int | None,
    degree: int | None,
    removed: int | None,
) -> None:
    genealogy, p = family
    result = genealogy.get_kinship(p[first].id, p[second].id)
    assert isinstance(result, Kinship)
    assert result.relation == relation
    assert result.generation_distance == generation
    assert result.cousin_degree == degree
    assert result.removed == removed


def test_adoptive_and_biological_filters(genealogy: Genealogy) -> None:
    bio_parent = Character(name="Biológico")
    adopt_parent = Character(name="Adotivo")
    child = Character(name="Filho")
    for person in (bio_parent, adopt_parent, child):
        genealogy.add_character(person)

    create_link(genealogy, bio_parent, child, BIOLOGICAL)
    create_link(genealogy, adopt_parent, child, ADOPTIVE)
    assert ids(genealogy.get_parents(child.id)) == {bio_parent.id, adopt_parent.id}
    assert genealogy.get_parents(child.id, types=[BIOLOGICAL]) == (bio_parent,)
    assert genealogy.get_parents(child.id, types=[ADOPTIVE]) == (adopt_parent,)
    assert genealogy.get_ancestors(child.id, types=[ADOPTIVE]) == (adopt_parent,)
    assert genealogy.get_kinship(bio_parent.id, child.id, types=[ADOPTIVE]).relation == "unknown"
    assert genealogy.get_kinship(bio_parent.id, child.id, types=[BIOLOGICAL]).relation == "ancestor"


def test_two_parentage_types_same_pair_have_independent_indices(
    genealogy: Genealogy,
) -> None:
    parent, child = Character(name="Arthur"), Character(name="Edric")
    genealogy.add_character(parent)
    genealogy.add_character(child)
    biological = create_link(genealogy, parent, child, BIOLOGICAL)
    adoptive = create_link(genealogy, parent, child, ADOPTIVE)
    assert genealogy.get_parents(child.id) == (parent,)

    genealogy.remove_relationship(biological.id)
    assert genealogy.get_parents(child.id) == (parent,)
    assert genealogy.get_parents(child.id, types=[BIOLOGICAL]) == ()
    assert genealogy.get_parents(child.id, types=[ADOPTIVE]) == (parent,)

    genealogy.remove_relationship(adoptive.id)
    assert genealogy.get_parents(child.id) == ()
    assert genealogy.get_children(parent.id) == ()


def test_remove_character_deletes_incoming_and_outgoing_relations(
    genealogy: Genealogy,
) -> None:
    parent, child, grandchild = (
        Character(name=name) for name in ("Pai", "Filho", "Neto")
    )
    for person in (parent, child, grandchild):
        genealogy.add_character(person)
    create_link(genealogy, parent, child)
    create_link(genealogy, child, grandchild)
    removed = genealogy.remove_character(child.id)

    assert removed == child
    assert genealogy.get_relationships() == ()
    assert genealogy.get_children(parent.id) == ()
    assert genealogy.get_parents(grandchild.id) == ()
    with pytest.raises(KeyError):
        genealogy.get_character(child.id)


def test_remove_relationship_allows_readding_new_path(
    genealogy: Genealogy,
) -> None:
    a, b = Character(name="A"), Character(name="B")
    genealogy.add_character(a)
    genealogy.add_character(b)
    original = create_link(genealogy, a, b)
    assert genealogy.remove_relationship(original.id) == original
    assert genealogy.get_relationships() == ()
    create_link(genealogy, b, a)
    assert genealogy.get_parents(a.id) == (b,)


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("get_parents", ()),
        ("get_children", ()),
        ("get_ancestors", ()),
        ("get_descendants", ()),
        ("get_siblings", ()),
    ],
)
def test_family_queries_reject_missing_character(
    genealogy: Genealogy, method_name: str, args: tuple[object, ...]
) -> None:
    method = getattr(genealogy, method_name)
    with pytest.raises(KeyError):
        method(uuid4(), *args)


def test_invalid_filter_on_parent_query_is_rejected(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    with pytest.raises(ValueError):
        genealogy.get_parents(p["Bruno"].id, types=[MARRIAGE])
    with pytest.raises(TypeError):
        genealogy.get_parents(p["Bruno"].id, types=["biological_parent"])


def test_invalid_filter_on_partner_query_is_rejected(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    with pytest.raises(ValueError):
        genealogy.get_partners(p["Afonso"].id, types=[BIOLOGICAL])


def test_genealogy_returns_read_only_tuples(
    family: tuple[Genealogy, dict[str, Character]],
) -> None:
    genealogy, p = family
    assert isinstance(genealogy.get_all_characters(), tuple)
    assert isinstance(genealogy.get_relationships(), tuple)
    assert isinstance(genealogy.get_parents(p["Bruno"].id), tuple)
    assert isinstance(genealogy.get_descendants(p["Afonso"].id), tuple)

