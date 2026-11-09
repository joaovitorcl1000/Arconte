"""Testes da projecao e do layout genealogico do Arconte (pytest).

Executar da pasta backend/genealogy::

    python3 -m pytest test/test_tree.py -v
    python3 -m pytest test/ -q
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from dataclasses import replace
import json
from uuid import UUID, uuid4

import pytest

from character.character import Character
from family.family import Family, FamilyMembership, FamilyType, MembershipOrigin
from genealogy.genealogy import Genealogy
from project.project import Project
from relationship.relationship import Relationship, RelationshipType
from tree.tree import (
    TreeBuilder, TreeEdge, TreeGraph, TreeLayout, TreeNode, TreePosition,
    layout_tree,
)


@pytest.fixture
def sample():
    """Multiplas geracoes, ancestrais comuns, adocao, unioes e um isolado."""
    project = Project(name="Eldoria")
    characters = {}
    for name in (
        "Afonso", "Beatriz", "Carlos", "Diana", "Eva", "Felipe",
        "Gina", "Heitor", "Iris", "Jorge", "Zora",
    ):
        person = Character(name=name, biography=f"Historia de {name}")
        project.add_character(person)
        characters[name] = person

    def parent(a, b, kind=RelationshipType.BIOLOGICAL_PARENT):
        project.add_relationship(Relationship(
            source_id=characters[a].id, target_id=characters[b].id, type=kind
        ))

    def marriage(a, b, kind=RelationshipType.MARRIAGE):
        project.add_relationship(Relationship(
            source_id=characters[a].id, target_id=characters[b].id, type=kind
        ))

    for a, b in (
        ("Afonso", "Carlos"), ("Beatriz", "Carlos"),
        ("Afonso", "Diana"), ("Beatriz", "Diana"),
        ("Carlos", "Eva"), ("Gina", "Eva"),
        ("Diana", "Felipe"), ("Heitor", "Felipe"),
        ("Eva", "Iris"), ("Felipe", "Iris"),
        ("Iris", "Jorge"),
    ):
        parent(a, b)
    parent("Gina", "Jorge", RelationshipType.ADOPTIVE_PARENT)

    for a, b in (
        ("Afonso", "Beatriz"), ("Carlos", "Gina"),
        ("Diana", "Heitor"), ("Eva", "Felipe"),
    ):
        marriage(a, b)

    family = Family(name="Valerian", type=FamilyType.HOUSE,
                    founder_id=characters["Afonso"].id)
    project.add_family(family)
    for name in ("Afonso", "Carlos", "Eva"):
        project.add_membership(FamilyMembership(
            family_id=family.id,
            character_id=characters[name].id,
            origin=MembershipOrigin.AFFILIATION,
        ))
    return project, characters, family


def ids(graph):
    return {node.id for node in graph.nodes}


def names(graph):
    return {node.name for node in graph.nodes}


def positions(layout):
    return {item.character_id: item for item in layout.positions}


def test_builder_accepts_project(sample):
    project, _, _ = sample
    assert len(TreeBuilder(project).build().nodes) == 11


def test_builder_accepts_genealogy(sample):
    project, _, _ = sample
    assert len(TreeBuilder(project.genealogy).build().nodes) == 11


@pytest.mark.parametrize("invalid", [None, 42, "genealogy", object()])
def test_builder_rejects_invalid_sources(invalid):
    with pytest.raises(TypeError):
        TreeBuilder(invalid)


def test_empty_genealogy_produces_empty_graph_and_layout():
    graph = TreeBuilder(Genealogy()).build()
    layout = layout_tree(graph)
    assert graph.nodes == graph.edges == ()
    assert layout.positions == ()
    assert (layout.width, layout.height) == (0, 0)


def test_global_view_contains_isolated_characters(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert "Zora" in names(graph)
    assert len(graph.edges) == len(project.get_relationships())


def test_no_root_has_no_selection_metadata(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert graph.root_id is None
    assert graph.direction == "all"


def test_global_node_order_is_deterministic_and_alphabetic(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert [node.name for node in graph.nodes] == sorted(
        (character.name for character in project.get_all_characters()),
        key=str.casefold,
    )
    assert graph.to_dict() == TreeBuilder(project).build().to_dict()


def test_global_edges_reference_only_selected_characters(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert all(e.source_id in ids(graph) and e.target_id in ids(graph) for e in graph.edges)


def test_global_view_can_remove_partner_edges(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build(include_partners=False)
    assert all(edge.directed for edge in graph.edges)
    assert "Zora" in names(graph)


def test_parent_edges_preserve_direction(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build()
    assert any(
        edge.source_id == characters["Afonso"].id
        and edge.target_id == characters["Carlos"].id
        and edge.directed for edge in graph.edges
    )


def test_unions_remain_undirected(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build()
    union = next(
        edge for edge in graph.edges
        if {edge.source_id, edge.target_id} ==
        {characters["Eva"].id, characters["Felipe"].id}
        and edge.type == RelationshipType.MARRIAGE
    )
    assert not union.directed


def test_adoption_is_preserved(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build()
    assert any(
        edge.source_id == characters["Gina"].id
        and edge.target_id == characters["Jorge"].id
        and edge.type == RelationshipType.ADOPTIVE_PARENT
        for edge in graph.edges
    )


def test_family_ids_are_available_when_source_is_project(sample):
    project, characters, family = sample
    graph = TreeBuilder(project).build()
    by_id = {node.id: node for node in graph.nodes}
    assert by_id[characters["Afonso"].id].family_ids == (family.id,)
    assert by_id[characters["Zora"].id].family_ids == ()


def test_family_ids_empty_when_using_genealogy_alone(sample):
    project, _, _ = sample
    assert all(not n.family_ids for n in TreeBuilder(project.genealogy).build().nodes)


def test_node_data_preserves_character_information(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build()
    node = next(n for n in graph.nodes if n.id == characters["Eva"].id)
    assert node.biography == "Historia de Eva"
    assert node.full_name == "Eva"


def test_descendants_of_afonso(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Afonso"].id,
        direction="descendants", include_partners=False,
    )
    assert names(graph) == {"Afonso", "Carlos", "Diana", "Eva", "Felipe", "Iris", "Jorge"}


def test_ancestors_of_iris(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Iris"].id, direction="ancestors",
        include_partners=False,
    )
    assert names(graph) == {
        "Iris", "Eva", "Felipe", "Carlos", "Gina", "Diana", "Heitor",
        "Afonso", "Beatriz",
    }


@pytest.mark.parametrize("limit,expected", [
    (0, {"Afonso"}),
    (1, {"Afonso", "Carlos", "Diana"}),
    (2, {"Afonso", "Carlos", "Diana", "Eva", "Felipe"}),
    (3, {"Afonso", "Carlos", "Diana", "Eva", "Felipe", "Iris"}),
    (4, {"Afonso", "Carlos", "Diana", "Eva", "Felipe", "Iris", "Jorge"}),
])
def test_descendant_generation_limit(sample, limit, expected):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Afonso"].id, direction="descendants",
        include_partners=False, max_generations=limit,
    )
    assert names(graph) == expected


def test_ancestor_depth_limit(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Iris"].id, direction="ancestors",
        max_generations=1, include_partners=False,
    )
    assert names(graph) == {"Iris", "Eva", "Felipe"}


def test_spouses_added_one_hop_without_following_their_ancestors(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Carlos"].id, direction="ancestors",
        max_generations=0, include_partners=True,
    )
    assert names(graph) == {"Carlos", "Gina"}
    assert all(edge.type in {RelationshipType.MARRIAGE, RelationshipType.PARTNERSHIP}
               for edge in graph.edges)


def test_no_spouses_when_disabled(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Carlos"].id, direction="ancestors",
        max_generations=0, include_partners=False,
    )
    assert names(graph) == {"Carlos"}


def test_all_root_limits_connected_component(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(root_id=characters["Afonso"].id)
    assert "Zora" not in names(graph)
    assert len(graph.nodes) == 10


def test_all_root_zero_is_only_root(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Afonso"].id, max_generations=0,
    )
    assert names(graph) == {"Afonso"}


def test_all_root_one_includes_partner_and_children(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Afonso"].id, max_generations=1,
    )
    assert names(graph) == {"Afonso", "Beatriz", "Carlos", "Diana"}


def test_all_root_one_without_partner(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Afonso"].id,
        max_generations=1, include_partners=False,
    )
    assert names(graph) == {"Afonso", "Carlos", "Diana"}


def test_root_isolated_component(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(root_id=characters["Zora"].id)
    assert names(graph) == {"Zora"}
    assert graph.edges == ()


def test_adoptive_filter_follows_only_adoptive_parentage(sample):
    project, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters["Gina"].id,
        direction="descendants", include_partners=False,
        parent_types=[RelationshipType.ADOPTIVE_PARENT],
    )
    assert names(graph) == {"Gina", "Jorge"}
    assert {e.type for e in graph.edges} == {RelationshipType.ADOPTIVE_PARENT}


def test_biological_filter_omits_adoption_edges(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build(
        include_partners=False,
        parent_types=[RelationshipType.BIOLOGICAL_PARENT],
    )
    assert RelationshipType.ADOPTIVE_PARENT not in {e.type for e in graph.edges}


def test_empty_parent_filter_keeps_nodes_but_not_parent_edges(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build(parent_types=[], include_partners=False)
    assert len(graph.nodes) == 11
    assert graph.edges == ()


def test_parent_type_filter_does_not_hide_marriage_edges(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build(parent_types=[], include_partners=True)
    assert {e.type for e in graph.edges} == {RelationshipType.MARRIAGE}


@pytest.mark.parametrize("direction", ["up", "children", "", None, 3])
def test_invalid_direction_is_rejected(sample, direction):
    project, _, _ = sample
    with pytest.raises(ValueError):
        TreeBuilder(project).build(direction=direction)


@pytest.mark.parametrize("value", [-1, True, 1.5, "2", False])
def test_invalid_max_generation_is_rejected(sample, value):
    project, chars, _ = sample
    with pytest.raises(ValueError):
        TreeBuilder(project).build(root_id=chars["Afonso"].id,
                                   max_generations=value)


@pytest.mark.parametrize("value", [None, "yes", 1, [], False])
def test_include_partner_type_validation(sample, value):
    project, _, _ = sample
    if type(value) is bool:
        TreeBuilder(project).build(include_partners=value)
    else:
        with pytest.raises(TypeError):
            TreeBuilder(project).build(include_partners=value)


@pytest.mark.parametrize("value", ["abc", 5, 1.25])
def test_invalid_root_type(sample, value):
    project, _, _ = sample
    with pytest.raises(TypeError):
        TreeBuilder(project).build(root_id=value)


def test_unknown_root_rejected(sample):
    project, _, _ = sample
    with pytest.raises(KeyError):
        TreeBuilder(project).build(root_id=uuid4())


@pytest.mark.parametrize("direction,depth", [("ancestors", None), ("descendants", None), ("all", 0)])
def test_direction_or_depth_without_root_is_rejected(sample, direction, depth):
    project, _, _ = sample
    with pytest.raises(ValueError):
        TreeBuilder(project).build(direction=direction, max_generations=depth)


@pytest.mark.parametrize("value,error", [
    (["biological_parent"], TypeError),
    ([RelationshipType.MARRIAGE], ValueError),
    (42, TypeError),
    ([None], TypeError),
])
def test_invalid_parent_type_filter(sample, value, error):
    project, _, _ = sample
    with pytest.raises(error):
        TreeBuilder(project).build(parent_types=value)


def test_graph_serialization_is_json_safe_and_has_explicit_direction(sample):
    project, _, _ = sample
    doc = TreeBuilder(project).build().to_dict()
    json.dumps(doc, ensure_ascii=False)
    assert {"nodes", "edges", "root_id", "direction"} == set(doc)
    assert any(edge["directed"] is False for edge in doc["edges"])
    assert any(edge["directed"] is True for edge in doc["edges"])


def test_graph_data_does_not_mutate_project(sample):
    project, _, _ = sample
    original = project.to_dict()
    graph = TreeBuilder(project).build()
    layout_tree(graph).to_dict()
    assert project.to_dict() == original


def test_build_does_not_drop_distinct_parentage_types_on_same_pair():
    genealogy = Genealogy()
    a, b = Character(name="A"), Character(name="B")
    genealogy.add_character(a)
    genealogy.add_character(b)
    for kind in (RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT):
        genealogy.add_relationship(Relationship(source_id=a.id, target_id=b.id, type=kind))
    graph = TreeBuilder(genealogy).build()
    assert len(graph.edges) == 2
    assert {edge.type for edge in graph.edges} == {
        RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT,
    }


def test_layout_is_produced_for_all_nodes(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    layout = layout_tree(graph)
    assert isinstance(layout, TreeLayout)
    assert {p.character_id for p in layout.positions} == ids(graph)


def test_layout_generations_obey_parent_child_constraints(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    pos = positions(layout_tree(graph))
    for edge in graph.edges:
        if edge.directed:
            assert pos[edge.source_id].generation < pos[edge.target_id].generation
            assert pos[edge.source_id].y < pos[edge.target_id].y


def test_layout_ancestors_root_at_generation_zero(sample):
    project, chars, _ = sample
    graph = TreeBuilder(project).build(
        root_id=chars["Iris"].id, direction="ancestors", include_partners=False,
    )
    pos = positions(layout_tree(graph))
    assert pos[chars["Iris"].id].generation == 0
    assert all(p.generation <= 0 for p in pos.values())


def test_layout_descendants_root_at_generation_zero(sample):
    project, chars, _ = sample
    graph = TreeBuilder(project).build(
        root_id=chars["Afonso"].id, direction="descendants", include_partners=False,
    )
    pos = positions(layout_tree(graph))
    assert pos[chars["Afonso"].id].generation == 0
    assert all(p.generation >= 0 for p in pos.values())


def test_marriage_never_creates_a_parentage_constraint():
    genealogy = Genealogy()
    a, b = Character(name="A"), Character(name="B")
    genealogy.add_character(a)
    genealogy.add_character(b)
    genealogy.add_relationship(Relationship(
        source_id=a.id, target_id=b.id, type=RelationshipType.MARRIAGE,
    ))
    pos = positions(layout_tree(TreeBuilder(genealogy).build()))
    assert pos[a.id].generation == pos[b.id].generation == 0


def test_layout_no_two_nodes_overlap_in_same_generation(sample):
    project, _, _ = sample
    layout = layout_tree(TreeBuilder(project).build())
    xy = {(position.x, position.y) for position in layout.positions}
    assert len(xy) == len(layout.positions)


def test_layout_is_deterministic(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert layout_tree(graph).to_dict() == layout_tree(graph).to_dict()


def test_layout_spacing_and_bounds(sample):
    project, _, _ = sample
    layout = layout_tree(TreeBuilder(project).build(),
                         horizontal_spacing=100, vertical_spacing=75)
    assert layout.width > 0 and layout.height > 0
    assert all(0 <= p.x < layout.width and 0 <= p.y < layout.height
               for p in layout.positions)


def test_layout_spacing_changes_positions(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    first = positions(layout_tree(graph, horizontal_spacing=120))
    second = positions(layout_tree(graph, horizontal_spacing=240))
    assert all(second[cid].x == 2 * position.x for cid, position in first.items())


@pytest.mark.parametrize("value", [0, -5, None, True, "100", float("nan"), float("inf")])
def test_invalid_horizontal_spacing(value):
    with pytest.raises(ValueError):
        layout_tree(TreeBuilder(Genealogy()).build(), horizontal_spacing=value)


@pytest.mark.parametrize("value", [0, -5, None, False, "100", float("nan"), float("inf")])
def test_invalid_vertical_spacing(value):
    with pytest.raises(ValueError):
        layout_tree(TreeBuilder(Genealogy()).build(), vertical_spacing=value)


@pytest.mark.parametrize("value", [-1, 1.5, None, True, "4"])
def test_invalid_layout_pass_count(value):
    with pytest.raises(ValueError):
        layout_tree(TreeBuilder(Genealogy()).build(), passes=value)


def test_zero_layout_passes_still_produces_coordinates(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    assert len(layout_tree(graph, passes=0).positions) == len(graph.nodes)


def test_layout_rejects_bad_input():
    with pytest.raises(TypeError):
        layout_tree(None)


def test_layout_rejects_edge_to_unknown_character():
    node = TreeNode.from_character(Character(name="A"))
    edge = TreeEdge(uuid4(), node.id, uuid4(), RelationshipType.BIOLOGICAL_PARENT)
    graph = TreeGraph((node,), (edge,), None, "all")
    with pytest.raises(ValueError, match="ausente"):
        layout_tree(graph)


def test_layout_rejects_parent_cycle_in_manually_built_graph():
    a = TreeNode.from_character(Character(name="A"))
    b = TreeNode.from_character(Character(name="B"))
    graph = TreeGraph(
        (a, b),
        (TreeEdge(uuid4(), a.id, b.id, RelationshipType.ADOPTIVE_PARENT),
         TreeEdge(uuid4(), b.id, a.id, RelationshipType.BIOLOGICAL_PARENT)),
        None, "all",
    )
    with pytest.raises(ValueError, match="Ciclo"):
        layout_tree(graph)


def test_layout_rejects_duplicate_node_ids():
    node = TreeNode.from_character(Character(name="A"))
    graph = TreeGraph((node, node), (), None, "all")
    with pytest.raises(ValueError, match="duplicado"):
        layout_tree(graph)


def test_nodes_and_edges_are_immutable(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    with pytest.raises(FrozenInstanceError):
        graph.nodes[0].name = "Outro"
    with pytest.raises(FrozenInstanceError):
        graph.edges[0].source_id = uuid4()
    with pytest.raises(FrozenInstanceError):
        graph.root_id = uuid4()


def test_layout_result_serializes_combined_coordinates(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    data = layout_tree(graph).to_dict()
    json.dumps(data)
    assert "layout" in data
    assert {"generation", "x", "y"} <= set(data["nodes"][0])
    assert len(data["edges"]) == len(graph.edges)


def test_export_to_dict_does_not_change_graph(sample):
    project, _, _ = sample
    graph = TreeBuilder(project).build()
    snapshot = graph.to_dict()
    document = layout_tree(graph).to_dict()
    document["nodes"][0]["name"] = "Mutacao"
    assert graph.to_dict() == snapshot


def test_graph_reflects_character_update_without_modifying_old_snapshot(sample):
    project, characters, _ = sample
    old_graph = TreeBuilder(project).build()
    project.update_character(replace(characters["Afonso"], name="Rei Afonso"))
    new_graph = TreeBuilder(project).build()
    assert "Rei Afonso" in names(new_graph)
    assert "Afonso" in names(old_graph)


def test_graph_after_character_removal(sample):
    project, characters, _ = sample
    project.remove_character(characters["Jorge"].id)
    graph = TreeBuilder(project).build()
    assert "Jorge" not in names(graph)
    assert all(e.source_id in ids(graph) and e.target_id in ids(graph) for e in graph.edges)


def test_loaded_project_can_build_same_tree(tmp_path, sample):
    project, _, _ = sample
    before = TreeBuilder(project).build().to_dict()
    path = tmp_path / "eldoria.json"
    project.save(path)
    loaded = Project.load(path)
    assert TreeBuilder(loaded).build().to_dict() == before
    assert layout_tree(TreeBuilder(loaded).build()).to_dict() == layout_tree(
        TreeBuilder(project).build()
    ).to_dict()


def test_project_with_multiple_families_tags_both(sample):
    project, chars, _ = sample
    new_family = Family(name="Drakon")
    project.add_family(new_family)
    project.add_membership(FamilyMembership(
        family_id=new_family.id, character_id=chars["Afonso"].id,
    ))
    node = next(n for n in TreeBuilder(project).build().nodes
                if n.id == chars["Afonso"].id)
    assert len(node.family_ids) == 2
    assert new_family.id in node.family_ids


def test_large_chain_layout_has_valid_generations():
    genealogy = Genealogy()
    people = [Character(name=f"P{i:03d}") for i in range(80)]
    for person in people:
        genealogy.add_character(person)
    for parent, child in zip(people, people[1:]):
        genealogy.add_relationship(Relationship(
            source_id=parent.id, target_id=child.id,
            type=RelationshipType.BIOLOGICAL_PARENT,
        ))
    graph = TreeBuilder(genealogy).build(root_id=people[0].id,
                                        direction="descendants")
    pos = positions(layout_tree(graph))
    assert len(pos) == 80
    assert pos[people[-1].id].generation == 79
