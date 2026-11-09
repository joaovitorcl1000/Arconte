"""Testes de SVG do Arconte (Python 3.10+, pytest).

Executar a partir de backend/genealogy::

    python3 -m pytest test/test_visualization.py -v
    python3 -m pytest test/ -q
"""

from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path
from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest

from character.character import Character
from genealogy.genealogy import Genealogy
from project.project import Project
from relationship.relationship import Relationship, RelationshipType
from tree.tree import TreeBuilder, TreeEdge, TreeGraph, TreeLayout, TreeNode, TreePosition, layout_tree
from visualization.visualization import SvgOptions, render_svg, save_svg


NS = {"svg": "http://www.w3.org/2000/svg"}


@pytest.fixture
def sample():
    project = Project(name="Reino de Éldoria")
    characters = {
        name: Character(name=name, surname="Valéry", birth_year=year,
                        biography=f"Biografia de {name} & da família")
        for name, year in (
            ("Árthur", 100), ("Élena", 102), ("Edric", 125),
            ("Lyara", 127), ("Thorin", 126), ("Érik", 150),
        )
    }
    for character in characters.values():
        project.add_character(character)

    def connect(a, b, kind):
        project.add_relationship(Relationship(
            source_id=characters[a].id, target_id=characters[b].id, type=kind
        ))

    connect("Árthur", "Élena", RelationshipType.MARRIAGE)
    connect("Árthur", "Edric", RelationshipType.BIOLOGICAL_PARENT)
    connect("Élena", "Edric", RelationshipType.BIOLOGICAL_PARENT)
    connect("Árthur", "Lyara", RelationshipType.BIOLOGICAL_PARENT)
    connect("Élena", "Lyara", RelationshipType.BIOLOGICAL_PARENT)
    connect("Thorin", "Lyara", RelationshipType.PARTNERSHIP)
    connect("Lyara", "Érik", RelationshipType.ADOPTIVE_PARENT)
    return project, characters, layout_tree(TreeBuilder(project).build())


def root(svg):
    return ET.fromstring(svg)


def findall(root_element, tag):
    return root_element.findall(f".//svg:{tag}", NS)


def test_svg_is_well_formed_and_namespaced(sample):
    _, _, layout = sample
    document = root(render_svg(layout))
    assert document.tag == "{http://www.w3.org/2000/svg}svg"
    assert document.attrib["role"] == "img"
    assert document.attrib["aria-labelledby"] == "arconte-title arconte-description"


def test_renderer_exposes_one_card_per_character(sample):
    _, _, layout = sample
    cards = [element for element in findall(root(render_svg(layout)), "g")
             if element.get("data-role") == "character"]
    assert len(cards) == len(layout.graph.nodes) == 6
    assert {card.attrib["data-character-id"] for card in cards} == {
        str(node.id) for node in layout.graph.nodes
    }


def test_renderer_exposes_one_path_per_relationship(sample):
    _, _, layout = sample
    links = [element for element in findall(root(render_svg(layout)), "path")
             if element.get("data-edge-id")]
    assert len(links) == len(layout.graph.edges) == 7
    assert {link.get("data-edge-id") for link in links} == {
        str(edge.id) for edge in layout.graph.edges
    }


def test_direction_information_is_in_svg(sample):
    _, _, layout = sample
    links = [element for element in findall(root(render_svg(layout)), "path")
             if element.get("data-edge-id")]
    for element in links:
        is_parent = element.get("data-relation") in {
            "biological_parent", "adoptive_parent"
        }
        assert element.get("data-directed") == str(is_parent).lower()


def test_relationship_styles_distinguish_types(sample):
    _, _, layout = sample
    links = {element.get("data-relation"): element
             for element in findall(root(render_svg(layout)), "path")
             if element.get("data-relation")}
    assert links["biological_parent"].get("stroke") != links["adoptive_parent"].get("stroke")
    assert links["adoptive_parent"].get("stroke-dasharray")
    assert links["marriage"].get("stroke-dasharray") is None
    assert links["partnership"].get("stroke-dasharray")


def test_svg_contains_visible_names_and_dates(sample):
    _, characters, layout = sample
    text = " ".join((element.text or "") for element in findall(root(render_svg(layout)), "text"))
    for character in characters.values():
        assert character.full_name in text
    assert "100" in text and "150" in text


def test_does_not_mutate_input_layout(sample):
    _, _, layout = sample
    before = layout.to_dict()
    render_svg(layout)
    assert layout.to_dict() == before


def test_serialization_is_deterministic(sample):
    _, _, layout = sample
    assert render_svg(layout) == render_svg(layout)


def test_custom_title_is_in_document(sample):
    _, _, layout = sample
    svg = render_svg(layout, options=SvgOptions(title="A Casa do Dragão"))
    parsed = root(svg)
    assert parsed.find("svg:title", NS).text == "A Casa do Dragão"


def test_hide_years_does_not_remove_names(sample):
    _, _, layout = sample
    svg = render_svg(layout, options=SvgOptions(show_years=False))
    content = " ".join((tag.text or "") for tag in findall(root(svg), "text"))
    assert "Árthur Valéry" in content
    assert "100 —" not in content


def test_hide_legend_removes_legend_group(sample):
    _, _, layout = sample
    svg = root(render_svg(layout, options=SvgOptions(show_legend=False)))
    assert not any(element.get("id") == "arconte-legend" for element in findall(svg, "g"))


def test_legend_has_four_kinds(sample):
    _, _, layout = sample
    svg = root(render_svg(layout))
    legend = next(el for el in findall(svg, "g") if el.get("id") == "arconte-legend")
    labels = [el.text for el in legend.findall("svg:text", NS)]
    assert labels == ["Filiação biológica", "Filiação adotiva", "Casamento", "União"]


def test_empty_tree_is_visible():
    layout = layout_tree(TreeBuilder(Genealogy()).build())
    document = root(render_svg(layout))
    assert not any(el.get("data-role") == "character" for el in findall(document, "g"))
    assert any(el.text == "Nenhum personagem cadastrado" for el in findall(document, "text"))


def test_layout_can_be_made_from_genealogy_without_project():
    genealogy = Genealogy()
    genealogy.add_character(Character(name="Único"))
    svg = render_svg(layout_tree(TreeBuilder(genealogy).build()))
    assert "Único" in svg


def test_escapes_untrusted_character_data():
    genealogy = Genealogy()
    person = Character(name="</text><script>alert('x')</script>&",
                       biography="<img src=x onerror=alert(1)>")
    genealogy.add_character(person)
    svg = render_svg(layout_tree(TreeBuilder(genealogy).build()))
    parsed = root(svg)
    assert "<script>" not in svg
    assert "<img" not in svg
    assert not findall(parsed, "script")
    assert not findall(parsed, "img")
    assert person.full_name in [el.text for el in findall(parsed, "text")]
    assert any(person.biography in (el.text or "") for el in findall(parsed, "title"))


def test_xml_illegal_control_char_is_rejected():
    genealogy = Genealogy()
    genealogy.add_character(Character(name="A\x00B"))
    layout = layout_tree(TreeBuilder(genealogy).build())
    with pytest.raises(ValueError, match="XML"):
        render_svg(layout)


@pytest.mark.parametrize("invalid", [None, 12, "wrong", object()])
def test_invalid_layout_rejected(invalid):
    with pytest.raises(TypeError):
        render_svg(invalid)


@pytest.mark.parametrize("invalid", [None, "settings", 22, object()])
def test_invalid_options_rejected(invalid):
    layout = layout_tree(TreeBuilder(Genealogy()).build())
    if invalid is None:
        assert root(render_svg(layout, options=invalid)) is not None
    else:
        with pytest.raises(TypeError):
            render_svg(layout, options=invalid)


@pytest.mark.parametrize("field,value", [
    ("card_width", 0), ("card_width", -1), ("card_width", True),
    ("card_width", float("inf")), ("card_width", float("nan")),
    ("card_height", 0), ("card_height", -1),
    ("padding", 0), ("padding", "large"),
    ("title", ""), ("title", "   "), ("title", "abc\x00"),
    ("show_years", 1), ("show_legend", "False"),
])
def test_svg_options_validation(field, value):
    with pytest.raises((ValueError, TypeError)):
        SvgOptions(**{field: value})


def test_multiple_parentage_types_draw_as_distinct_paths():
    genealogy = Genealogy()
    adult = Character(name="Adulta")
    child = Character(name="Criança")
    genealogy.add_character(adult)
    genealogy.add_character(child)
    for kind in (RelationshipType.ADOPTIVE_PARENT, RelationshipType.BIOLOGICAL_PARENT):
        genealogy.add_relationship(Relationship(
            source_id=adult.id, target_id=child.id, type=kind
        ))
    rendered = root(render_svg(layout_tree(TreeBuilder(genealogy).build())))
    paths = [el for el in findall(rendered, "path") if el.get("data-edge-id")]
    assert len(paths) == 2
    assert paths[0].get("d") != paths[1].get("d")


def test_marriage_between_different_generations_is_visible(sample):
    _, _, layout = sample
    doc = root(render_svg(layout))
    assert any(link.get("data-relation") == "marriage" for link in findall(doc, "path"))


def test_save_creates_nested_directories(tmp_path, sample):
    _, _, layout = sample
    location = tmp_path / "sub" / "out" / "árvore.svg"
    saved = save_svg(layout, location)
    assert saved == location
    assert location.exists()
    assert root(location.read_text(encoding="utf-8")).tag.endswith("svg")


def test_save_accepts_str_paths(tmp_path, sample):
    _, _, layout = sample
    path = tmp_path / "tree.svg"
    assert save_svg(layout, str(path)) == path


def test_save_deterministic_bytes(tmp_path, sample):
    _, _, layout = sample
    location = tmp_path / "arvore.svg"
    save_svg(layout, location)
    first = location.read_bytes()
    save_svg(layout, location)
    assert location.read_bytes() == first


def test_save_failure_does_not_overwrite_previous_file(tmp_path, sample, monkeypatch):
    _, _, layout = sample
    path = tmp_path / "arvore.svg"
    path.write_bytes(b"keep")

    def fail(*args, **kwargs):
        raise OSError("Falha simulada")

    monkeypatch.setattr("visualization.visualization.os.replace", fail)
    with pytest.raises(OSError, match="Falha simulada"):
        save_svg(layout, path)
    assert path.read_bytes() == b"keep"
    assert list(tmp_path.iterdir()) == [path]


def test_save_invalid_input_does_not_touch_previous_file(tmp_path):
    path = tmp_path / "arvore.svg"
    path.write_bytes(b"old")
    with pytest.raises(TypeError):
        save_svg("invalid", path)
    assert path.read_bytes() == b"old"


def test_save_works_without_dependencies_other_than_stdlib(tmp_path):
    # Não testa dependências do pytest, mas a API de escrita é síncrona,
    # retornando um Path e não exigindo programas externos como Graphviz.
    genealogy = Genealogy()
    genealogy.add_character(Character(name="Exemplo"))
    layout = layout_tree(TreeBuilder(genealogy).build())
    assert isinstance(save_svg(layout, tmp_path / "exemplo.svg"), Path)


def test_invalid_missing_position_rejected(sample):
    _, _, layout = sample
    bad = replace(layout, positions=layout.positions[:-1])
    with pytest.raises(ValueError, match="posição"):
        render_svg(bad)


def test_duplicate_position_rejected(sample):
    _, _, layout = sample
    bad = replace(layout, positions=layout.positions + (layout.positions[0],))
    with pytest.raises(ValueError, match="duplicada"):
        render_svg(bad)


def test_position_for_unknown_node_rejected(sample):
    _, _, layout = sample
    bad = replace(layout, positions=layout.positions +
                  (TreePosition(character_id=uuid4(), generation=0, x=0, y=0),))
    with pytest.raises(ValueError):
        render_svg(bad)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_coordinates_rejected(sample, value):
    _, _, layout = sample
    bad_positions = (replace(layout.positions[0], x=value),) + layout.positions[1:]
    with pytest.raises(ValueError, match="finitas"):
        render_svg(replace(layout, positions=bad_positions))


def test_nonfinite_size_rejected(sample):
    _, _, layout = sample
    with pytest.raises(ValueError):
        render_svg(replace(layout, width=math.nan))


def test_negative_size_rejected(sample):
    _, _, layout = sample
    with pytest.raises(ValueError):
        render_svg(replace(layout, height=-2.0))


def test_missing_endpoint_rejected(sample):
    _, _, layout = sample
    edge = replace(layout.graph.edges[0], target_id=uuid4())
    bad_graph = replace(layout.graph, edges=(edge,) + layout.graph.edges[1:])
    with pytest.raises(ValueError, match="ausente"):
        render_svg(replace(layout, graph=bad_graph))


def test_duplicate_node_id_rejected(sample):
    _, _, layout = sample
    bad_graph = replace(layout.graph, nodes=layout.graph.nodes + (layout.graph.nodes[0],))
    with pytest.raises(ValueError, match="duplicado"):
        render_svg(replace(layout, graph=bad_graph))


def test_duplicate_edge_id_rejected(sample):
    _, _, layout = sample
    bad_graph = replace(layout.graph, edges=layout.graph.edges + (layout.graph.edges[0],))
    with pytest.raises(ValueError, match="duplicada"):
        render_svg(replace(layout, graph=bad_graph))


def test_invalid_generation_rejected(sample):
    _, _, layout = sample
    bad_positions = (replace(layout.positions[0], generation=True),) + layout.positions[1:]
    with pytest.raises(TypeError):
        render_svg(replace(layout, positions=bad_positions))


def test_svg_viewbox_dimensions_are_positive(sample):
    _, _, layout = sample
    parsed = root(render_svg(layout))
    viewbox = list(map(float, parsed.attrib["viewBox"].split()))
    assert viewbox[:2] == [0.0, 0.0]
    assert viewbox[2] > 0 and viewbox[3] > 0


def test_root_metadata_does_not_change_sample_project(sample):
    project, _, layout = sample
    before = project.to_dict()
    render_svg(layout)
    assert project.to_dict() == before


def test_svg_no_external_urls_or_scripts(sample):
    _, _, layout = sample
    xml = render_svg(layout)
    assert not findall(root(xml), "script")
    assert "http://www.w3.org/2000/svg" in xml
    assert 'href="http' not in xml


def test_long_name_gets_text_length_hint():
    g = Genealogy()
    person = Character(name="Uma personagem com um nome extraordinariamente longo")
    g.add_character(person)
    svg = root(render_svg(layout_tree(TreeBuilder(g).build())))
    assert any(el.get("textLength") for el in findall(svg, "text"))


def test_unknown_dates_are_not_invented():
    g = Genealogy()
    g.add_character(Character(name="Sem datas"))
    svg = root(render_svg(layout_tree(TreeBuilder(g).build())))
    texts = [el.text for el in findall(svg, "text")]
    assert not any(text and ("Nasc." in text or "Falec." in text)
                   for text in texts)


def test_birth_only_and_death_only_dates():
    g = Genealogy()
    g.add_character(Character(name="Nascimento", birth_year=-120))
    g.add_character(Character(name="Morte", death_year=140))
    svg = root(render_svg(layout_tree(TreeBuilder(g).build())))
    texts = [el.text for el in findall(svg, "text")]
    assert "Nasc. -120" in texts
    assert "Falec. 140" in texts


def test_svg_show_family_marker():
    # A marca visual depende de family_ids nos TreeNodes, não da semântica da casa.
    g = Genealogy()
    person = Character(name="Fundadora")
    g.add_character(person)
    original = TreeBuilder(g).build()
    node = replace(original.nodes[0], family_ids=(uuid4(),))
    graph = replace(original, nodes=(node,))
    layout = layout_tree(graph)
    doc = root(render_svg(layout))
    assert any(el.get("fill") == "#d4a84e" for el in findall(doc, "circle"))


