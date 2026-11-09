"""Testes do visualizador HTML do Arconte (Python 3.10+, pytest).

Executar a partir de backend/genealogy::

    python3 -m pytest test/test_viewer.py -v
    python3 -m pytest test/ -q

Não precisa de servidor nem navegador: os testes verificam saída HTML,
SVG, serialização segura, controles declarados e persistência atômica.
A interação real também pode ser conferida abrindo o HTML no Firefox.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest

from character.character import Character
from family.family import Family, FamilyMembership, FamilyType
from genealogy.genealogy import Genealogy
from project.project import Project
from relationship.relationship import Relationship, RelationshipType
from tree.tree import TreeBuilder, TreeLayout, TreePosition, layout_tree
from viewer.viewer import ViewerOptions, render_html, save_html
from visualization.visualization import render_svg


class DataParser(HTMLParser):
    """Extrai somente o JSON do <script type=application/json> conhecido."""

    def __init__(self):
        super().__init__()
        self.in_data = False
        self.chunks = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attrs = dict(attrs)
            self.scripts.append(attrs)
            self.in_data = attrs.get("id") == "arconte-data"

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_data = False

    def handle_data(self, data):
        if self.in_data:
            self.chunks.append(data)


def parse_data(html):
    parser = DataParser()
    parser.feed(html)
    return json.loads("".join(parser.chunks))


def parse_svg(html):
    match = re.search(r"<svg\b.*?</svg>", html, flags=re.DOTALL)
    assert match is not None, "SVG não foi incluído"
    return ET.fromstring(match.group(0))


SVG = "{http://www.w3.org/2000/svg}"


@pytest.fixture
def sample():
    project = Project(name="Eldória", description="Linhagens e histórias")
    arthur = Character(name="Árthur", surname="Valerian", birth_year=101,
                       death_year=180, gender="Masculino", biography="Fundou uma casa.")
    elena = Character(name="Elena", birth_year=110)
    edric = Character(name="Edric", birth_year=135, biography="O sucessor")
    orfa = Character(name="Zora")
    for person in (arthur, elena, edric, orfa):
        project.add_character(person)
    project.add_relationship(Relationship(
        source_id=arthur.id, target_id=elena.id, type=RelationshipType.MARRIAGE
    ))
    project.add_relationship(Relationship(
        source_id=arthur.id, target_id=edric.id, type=RelationshipType.BIOLOGICAL_PARENT
    ))
    project.add_relationship(Relationship(
        source_id=elena.id, target_id=edric.id, type=RelationshipType.ADOPTIVE_PARENT
    ))
    family = Family(name="Casa Áurea", type=FamilyType.HOUSE, founder_id=arthur.id)
    project.add_family(family)
    project.add_membership(FamilyMembership(character_id=arthur.id, family_id=family.id))
    graph = TreeBuilder(project).build()
    layout = layout_tree(graph)
    return project, layout, {c.name: c for c in (arthur, elena, edric, orfa)}, family


def test_default_options():
    options = ViewerOptions()
    assert options.title == "Árvore genealógica"
    assert options.subtitle is None
    assert options.show_years and options.show_legend


def test_normalizes_options():
    item = ViewerOptions(title="  Eldória  ", subtitle="   Uma história  ")
    assert (item.title, item.subtitle) == ("Eldória", "Uma história")
    assert ViewerOptions(subtitle="   ").subtitle is None


@pytest.mark.parametrize("invalid", [None, 25, True, [], object()])
def test_title_rejects_wrong_types(invalid):
    with pytest.raises(TypeError):
        ViewerOptions(title=invalid)


@pytest.mark.parametrize("invalid", ["", "  ", "\n\t"])
def test_title_rejects_empty(invalid):
    with pytest.raises(ValueError):
        ViewerOptions(title=invalid)


@pytest.mark.parametrize("invalid", [1, False, [], object()])
def test_subtitle_rejects_wrong_types(invalid):
    with pytest.raises(TypeError):
        ViewerOptions(subtitle=invalid)


@pytest.mark.parametrize("invalid", [1, "yes", None, 1.0, []])
def test_show_years_requires_bool(invalid):
    with pytest.raises(TypeError):
        ViewerOptions(show_years=invalid)


@pytest.mark.parametrize("invalid", [False, 1, "yes", None, 0.0, []])
def test_show_legend_requires_bool(invalid):
    if invalid is False:
        assert ViewerOptions(show_legend=False).show_legend is False
    else:
        with pytest.raises(TypeError):
            ViewerOptions(show_legend=invalid)


@pytest.mark.parametrize("invalid", ["\x00", "\x01", "\ud800"])
def test_options_reject_xml_invalid_text(invalid):
    with pytest.raises(ValueError):
        ViewerOptions(title="Eldoria" + invalid)
    with pytest.raises(ValueError):
        ViewerOptions(subtitle="Eldoria" + invalid)


def test_options_immutable():
    item = ViewerOptions()
    with pytest.raises(FrozenInstanceError):
        item.title = "Nova"
    assert replace(item, title="Nova").title == "Nova"


def test_render_returns_html5_document(sample):
    _, layout, _, _ = sample
    html = render_html(layout)
    assert html.startswith("<!doctype html>")
    assert '<html lang="pt-BR">' in html
    assert '<meta charset="utf-8">' in html
    assert 'id="arconte-svg"' in html
    assert html.rstrip().endswith("</html>")


def test_page_title_and_subtitle_escape_html(sample):
    _, layout, _, _ = sample
    html = render_html(layout, options=ViewerOptions(
        title='A & <B> "C"', subtitle='<img src=x onerror="alert(1)">'
    ))
    assert 'A &amp; &lt;B&gt; &quot;C&quot;' in html
    assert '&lt;img src=x onerror=' in html
    assert '<img src=x onerror=' not in html


def test_project_description_used_as_default_subtitle(sample):
    project, layout, _, _ = sample
    html = render_html(layout, project=project)
    assert 'Linhagens e histórias' in html


def test_explicit_subtitle_overrides_project(sample):
    project, layout, _, _ = sample
    html = render_html(layout, project=project, options=ViewerOptions(subtitle='Minha árvore'))
    assert 'Minha árvore' in html


def test_svg_is_parseable_with_accessible_roles(sample):
    _, layout, _, _ = sample
    root = parse_svg(render_html(layout))
    assert root.tag == SVG + 'svg'
    assert root.get('id') == 'arconte-svg'
    assert root.get('tabindex') == '0'
    cards = root.findall(f'.//{SVG}g[@data-character-id]')
    assert len(cards) == 4
    assert all(card.get('role') == 'button' for card in cards)
    assert all(card.get('tabindex') == '0' for card in cards)
    assert all('Abrir informações' in card.get('aria-label', '') for card in cards)


def test_svg_keeps_every_relationship_type(sample):
    _, layout, _, _ = sample
    root = parse_svg(render_html(layout))
    edges = root.findall(f'.//{SVG}path[@data-edge-id]')
    assert len(edges) == 3
    assert {e.get('data-relation') for e in edges} == {
        'marriage', 'biological_parent', 'adoptive_parent'
    }


def test_embedded_json_matches_layout(sample):
    _, layout, _, _ = sample
    data = parse_data(render_html(layout))
    expected = layout.to_dict()
    assert data['nodes'] == expected['nodes']
    assert data['edges'] == expected['edges']
    assert data['layout'] == expected['layout']
    assert data['families'] == {}


def test_families_are_named_if_project_supplied(sample):
    project, layout, characters, family = sample
    data = parse_data(render_html(layout, project=project))
    assert data['families'] == {str(family.id): 'Casa Áurea'}
    arthur = next(node for node in data['nodes'] if node['id'] == str(characters['Árthur'].id))
    assert arthur['family_ids'] == [str(family.id)]


def test_isolated_character_is_included(sample):
    _, layout, characters, _ = sample
    data = parse_data(render_html(layout))
    assert str(characters['Zora'].id) in {n['id'] for n in data['nodes']}


def test_years_on_card_option(sample):
    _, layout, _, _ = sample
    html = render_html(layout, options=ViewerOptions(show_years=True))
    assert '101 — 180' in html
    html2 = render_html(layout, options=ViewerOptions(show_years=False))
    assert '101 — 180' not in html2[:html2.index('<script id="arconte-data"')]
    assert parse_data(html2)['nodes'][0]['birth_year'] is not None or any(
        node['birth_year'] is not None for node in parse_data(html2)['nodes']
    )


def test_hide_legend_option(sample):
    _, layout, _, _ = sample
    root = parse_svg(render_html(layout, options=ViewerOptions(show_legend=False)))
    assert root.find(f'.//{SVG}g[@id="arconte-legend"]') is None
    root2 = parse_svg(render_html(layout, options=ViewerOptions(show_legend=True)))
    assert root2.find(f'.//{SVG}g[@id="arconte-legend"]') is not None


def test_search_and_buttons_present(sample):
    _, layout, _, _ = sample
    html = render_html(layout)
    for target in ('id="search"', 'id="results"', 'id="result-count"',
                   'id="details-body"', 'id="zoom-in"', 'id="zoom-out"',
                   'id="reset"', 'id="scene-count"'):
        assert target in html
    assert 'type="search"' in html
    assert 'aria-live="polite"' in html


def test_contains_javascript_for_navigation(sample):
    _, layout, _, _ = sample
    html = render_html(layout)
    for phrase in ('wheel', 'pointerdown', 'pointermove', 'pointerup', 'keydown',
                   'getScreenCTM', 'viewBox', 'focusNode', 'updateSearch',
                   'normalize(\'NFD\')', 'selectNode', 'textContent'):
        assert phrase in html


def test_no_remote_scripts_or_styles(sample):
    _, layout, _, _ = sample
    html = render_html(layout)
    assert '<script src=' not in html
    assert '<link rel="stylesheet"' not in html
    assert 'fetch(' not in html
    assert 'XMLHttpRequest' not in html


def test_description_and_names_survive_json(sample):
    _, layout, _, _ = sample
    data = parse_data(render_html(layout))
    arthur = next(node for node in data['nodes'] if node['name'] == 'Árthur')
    assert arthur['biography'] == 'Fundou uma casa.'
    assert arthur['birth_year'] == 101
    assert arthur['death_year'] == 180


def test_dangerous_user_content_is_escaped():
    project = Project(name='Eldoria')
    malicious = '</script><script>alert("x")</script><img src=x onerror="x">'
    person = Character(name='A & <B>', biography=malicious)
    project.add_character(person)
    layout = layout_tree(TreeBuilder(project).build())
    html = render_html(layout)
    assert '</script><script>alert' not in html
    assert '<img src=x onerror=' not in html
    assert '&lt;B&gt;' in html
    assert malicious in parse_data(html)['nodes'][0]['biography']
    assert '<script' not in html[:html.index('<script id="arconte-data"')]


@pytest.mark.parametrize('unsafe', ['&', '<', '>', '</script>', '\u2028', '\u2029'])
def test_script_json_escaping(unsafe):
    project = Project(name='World')
    project.add_character(Character(name='X', biography='before ' + unsafe + ' after'))
    layout = layout_tree(TreeBuilder(project).build())
    html = render_html(layout)
    parsed = DataParser()
    parsed.feed(html)
    assert json.loads(''.join(parsed.chunks))['nodes'][0]['biography'] == 'before ' + unsafe + ' after'
    embedded = ''.join(parsed.chunks)
    if unsafe in ('<', '>', '&', '</script>', '\u2028', '\u2029'):
        assert unsafe not in embedded


def test_render_is_deterministic(sample):
    project, layout, _, _ = sample
    assert render_html(layout, project=project) == render_html(layout, project=project)


def test_render_does_not_modify_layout_or_project(sample):
    project, layout, _, _ = sample
    graph_data = layout.to_dict()
    before = project.to_dict()
    render_html(layout, project=project)
    assert graph_data == layout.to_dict()
    assert before == project.to_dict()


def test_empty_genealogy_renders_friendly_message():
    graph = TreeBuilder(Genealogy()).build()
    html = render_html(layout_tree(graph))
    assert 'Nenhum personagem cadastrado' in html
    assert parse_data(html)['nodes'] == []
    assert 'scene-count' in html


def test_custom_tree_subselection_is_respected(sample):
    project, _, characters, _ = sample
    graph = TreeBuilder(project).build(
        root_id=characters['Edric'].id,
        direction='ancestors',
        max_generations=1,
        include_partners=False,
    )
    data = parse_data(render_html(layout_tree(graph), project=project))
    assert data['direction'] == 'ancestors'
    assert data['root_id'] == str(characters['Edric'].id)
    assert len(data['nodes']) == 3


@pytest.mark.parametrize('invalid', [None, 'layout', 5, {}, object()])
def test_invalid_layout_is_rejected(invalid):
    with pytest.raises(TypeError):
        render_html(invalid)


@pytest.mark.parametrize('invalid', [True, 'ViewerOptions', {}, 12])
def test_invalid_options_rejected(sample, invalid):
    _, layout, _, _ = sample
    with pytest.raises(TypeError):
        render_html(layout, options=invalid)


@pytest.mark.parametrize('invalid', [False, 12, 'project', object()])
def test_invalid_project_rejected(sample, invalid):
    _, layout, _, _ = sample
    with pytest.raises(TypeError):
        render_html(layout, project=invalid)


def test_missing_node_position_is_rejected(sample):
    _, layout, _, _ = sample
    invalid = replace(layout, positions=layout.positions[:-1])
    with pytest.raises(ValueError):
        render_html(invalid)


def test_duplicate_node_position_is_rejected(sample):
    _, layout, _, _ = sample
    invalid = replace(layout, positions=layout.positions + layout.positions[:1])
    with pytest.raises(ValueError):
        render_html(invalid)


def test_invalid_coordinate_is_rejected(sample):
    _, layout, _, _ = sample
    positions = list(layout.positions)
    positions[0] = replace(positions[0], x=float('nan'))
    with pytest.raises(ValueError):
        render_html(replace(layout, positions=tuple(positions)))


def test_layout_with_inconsistent_dimensions_is_rejected(sample):
    _, layout, _, _ = sample
    with pytest.raises(ValueError):
        render_html(replace(layout, width=-12))


def test_output_svg_uses_original_renderer(sample):
    _, layout, _, _ = sample
    root_view = parse_svg(render_html(layout))
    root_original = ET.fromstring(render_svg(layout))
    assert root_view.get('viewBox') == root_original.get('viewBox')
    assert len(root_view.findall(f'.//{SVG}g[@data-character-id]')) == len(
        root_original.findall(f'.//{SVG}g[@data-character-id]')
    )


def test_save_creates_nested_folders(tmp_path, sample):
    _, layout, _, _ = sample
    output = tmp_path / 'nested' / 'history' / 'tree.html'
    assert save_html(layout, output) == output
    assert output.is_file()
    assert output.read_text('utf-8').startswith('<!doctype html>')


def test_save_accepts_string_path(tmp_path, sample):
    _, layout, _, _ = sample
    output = tmp_path / 'tree.html'
    result = save_html(layout, str(output))
    assert result == output


def test_save_keeps_utf8_accents(tmp_path, sample):
    project, layout, _, _ = sample
    output = tmp_path / 'arconte.html'
    save_html(layout, output, project=project)
    text = output.read_text(encoding='utf-8')
    assert 'Árthur' in text
    assert 'Casa Áurea' in parse_data(text)['families'].values()


def test_save_overwrites_existing_content(tmp_path, sample):
    _, layout, _, _ = sample
    path = tmp_path / 'tree.html'
    path.write_text('old', encoding='utf-8')
    save_html(layout, path)
    assert path.read_text('utf-8') != 'old'


def test_save_twice_is_byte_identical(tmp_path, sample):
    _, layout, _, _ = sample
    path = tmp_path / 'tree.html'
    save_html(layout, path)
    original = path.read_bytes()
    save_html(layout, path)
    assert original == path.read_bytes()


def test_failed_replace_preserves_old_document(tmp_path, sample, monkeypatch):
    import viewer.viewer as module
    _, layout, _, _ = sample
    path = tmp_path / 'tree.html'
    path.write_text('ORIGINAL', encoding='utf-8')
    def fail_replace(source, target):
        raise OSError('disk error')
    monkeypatch.setattr(module.os, 'replace', fail_replace)
    with pytest.raises(OSError, match='disk error'):
        save_html(layout, path)
    assert path.read_text(encoding='utf-8') == 'ORIGINAL'
    assert sorted(child.name for child in tmp_path.iterdir()) == ['tree.html']


def test_invalid_render_does_not_overwrite(tmp_path, sample):
    _, layout, _, _ = sample
    path = tmp_path / 'tree.html'
    path.write_text('ORIGINAL', encoding='utf-8')
    with pytest.raises(ValueError):
        save_html(replace(layout, width=-1), path)
    assert path.read_text('utf-8') == 'ORIGINAL'


def test_file_path_with_unicode(tmp_path, sample):
    _, layout, _, _ = sample
    path = tmp_path / 'Crônicas Áureas 🌳.html'
    save_html(layout, path)
    assert path.exists()


def test_source_tree_has_no_mutation_from_render(sample):
    project, layout, characters, _ = sample
    rendered = render_html(layout, project=project)
    assert characters['Árthur'].biography == 'Fundou uma casa.'
    assert '<svg' in rendered


def test_single_node_tree():
    genealogy = Genealogy()
    genealogy.add_character(Character(name='Sol'))
    html = render_html(layout_tree(TreeBuilder(genealogy).build()))
    assert len(parse_data(html)['nodes']) == 1
    assert parse_svg(html) is not None


def test_large_chain_tree_renders():
    genealogy = Genealogy()
    people = [Character(name='Geração ' + str(i)) for i in range(45)]
    for person in people:
        genealogy.add_character(person)
    for parent, child in zip(people, people[1:]):
        genealogy.add_relationship(Relationship(
            source_id=parent.id, target_id=child.id,
            type=RelationshipType.BIOLOGICAL_PARENT
        ))
    html = render_html(layout_tree(TreeBuilder(genealogy).build()))
    assert len(parse_data(html)['nodes']) == 45
    assert len(parse_svg(html).findall(f'.//{SVG}path[@data-edge-id]')) == 44
