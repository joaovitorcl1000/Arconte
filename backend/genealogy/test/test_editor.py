"""Testes de edição, persistência, exportação e menu do Arconte.

Execute da pasta ``backend/genealogy``::

    python3 -m pytest test/test_editor.py -v

Usa tmp_path e monkeypatch para nunca alterar os projetos do escritor.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import xml.etree.ElementTree as ET

import pytest

from character.character import Character
from editor.editor import Editor, main, run_console
from family.family import FamilyType, MembershipOrigin
from project.project import Project
from relationship.relationship import RelationshipType
from tree.tree import TreeLayout
from viewer.viewer import ViewerOptions
from visualization.visualization import SvgOptions


@pytest.fixture
def editor() -> Editor:
    return Editor.new("Eldoria", description="Um reino de fantasia")


@pytest.fixture
def people(editor: Editor) -> tuple[Character, Character, Character]:
    arthur = editor.create_character("Arthur", surname="Valerian", birth_year=100)
    elena = editor.create_character("Elena", surname="Drakon", birth_year=105)
    edric = editor.create_character("Edric", birth_year=130)
    return arthur, elena, edric


def test_new_editor_wraps_project_and_sets_dirty(editor):
    assert isinstance(editor.project, Project)
    assert editor.project.name == "Eldoria"
    assert editor.project.description == "Um reino de fantasia"
    assert editor.is_dirty is True
    assert editor.path is None


def test_init_with_project_and_saved_state():
    project = Project("Arconte")
    e = Editor(project, dirty=False)
    assert e.project is project and e.is_dirty is False


@pytest.mark.parametrize("value", [None, 123, {}, "Eldoria"])
def test_init_rejects_invalid_project(value):
    with pytest.raises(TypeError):
        Editor(value)


@pytest.mark.parametrize("value", [None, 2, "true"])
def test_init_rejects_invalid_dirty_flag(value):
    with pytest.raises(TypeError):
        Editor(Project("X"), dirty=value)


@pytest.mark.parametrize("path", [123, False, [], {}])
def test_editor_rejects_bad_path(path):
    with pytest.raises(TypeError):
        Editor.new("X", path=path)


@pytest.mark.parametrize("path", ["", " ", "."])
def test_editor_rejects_empty_path(path):
    with pytest.raises(ValueError):
        Editor.new("X", path=path)


def test_new_editor_with_path_is_still_unsaved(tmp_path):
    file = tmp_path / "a" / "novo.json"
    e = Editor.new("Novo", path=file)
    assert e.path == file and e.is_dirty
    assert not file.exists()


@pytest.mark.parametrize("name", ["", "  ", None, 13])
def test_new_rejects_invalid_project_name(name):
    with pytest.raises((TypeError, ValueError)):
        Editor.new(name)


def test_rename_and_describe_changes(editor):
    editor.rename_project("  Novo reino  ")
    editor.describe_project(" Nova descrição ")
    assert editor.project.name == "Novo reino"
    assert editor.project.description == "Nova descrição"


def test_rename_noop_preserves_clean_state(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    editor.rename_project(" Eldoria ")
    editor.describe_project(" Um reino de fantasia ")
    assert not editor.is_dirty


def test_invalid_rename_does_not_mark_dirty(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.rename_project(" ")
    assert editor.project.name == "Eldoria" and not editor.is_dirty


def test_invalid_description_does_not_mark_dirty(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    with pytest.raises(TypeError):
        editor.describe_project(123)
    assert not editor.is_dirty


def test_create_character_normalizes_and_returns_character(editor):
    c = editor.create_character("  Arthur  ", surname=" Valerian ", biography=" Rei ")
    assert c.full_name == "Arthur Valerian"
    assert c.biography == "Rei"
    assert editor.project.get_character(c.id) is c


def test_create_character_rejects_bad_birth(editor):
    with pytest.raises(TypeError):
        editor.create_character("A", birth_year=1.5)
    assert not editor.list_characters()


def test_create_character_failure_does_not_mark_dirty(editor, tmp_path):
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.create_character(" ")
    assert not editor.is_dirty


def test_edit_character_preserves_id_and_family_and_relationship(editor, people):
    father, spouse, child = people
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    family = editor.create_family("Valerian", founder_id=father.id)
    editor.add_membership(family.id, father.id)
    edited = editor.update_character(father.id, name="Artur", biography="Rei da fronteira")
    assert edited.id == father.id and edited.full_name == "Artur Valerian"
    assert editor.project.genealogy.get_children(father.id) == (child,)
    assert editor.project.families.get_members(family.id) == (edited,)


def test_edit_character_updates_optional_fields(editor, people):
    father = people[0]
    edited = editor.update_character(father.id, surname=None, birth_year=-120)
    assert edited.surname is None and edited.birth_year == -120


def test_update_character_no_fields_is_noop(tmp_path, editor, people):
    c = people[0]
    editor.save(tmp_path / "a.json")
    assert editor.update_character(c.id) is c
    assert not editor.is_dirty


def test_update_character_normalized_noop(tmp_path, editor, people):
    c = people[0]
    editor.save(tmp_path / "a.json")
    assert editor.update_character(c.id, name=" Arthur ") == c
    assert not editor.is_dirty


@pytest.mark.parametrize("field", ["id", "parent", "children", "family_id", "bogus"])
def test_edit_character_rejects_unknown_fields(editor, people, field):
    c = people[0]
    with pytest.raises(ValueError):
        editor.update_character(c.id, **{field: 100})
    assert editor.project.get_character(c.id) == c


def test_edit_character_invalid_does_not_modify(tmp_path, editor, people):
    c = people[0]
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.update_character(c.id, death_year=1, birth_year=100)
    assert editor.project.get_character(c.id) == c
    assert not editor.is_dirty


def test_edit_unknown_character(editor):
    with pytest.raises(KeyError):
        editor.update_character(uuid4(), name="Desconhecido")


def test_editor_creates_directed_parenthood(editor, people):
    father, _, child = people
    rel = editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    assert rel.source_id == father.id and rel.target_id == child.id
    assert editor.project.genealogy.get_parents(child.id) == (father,)


def test_editor_creates_adoption(editor, people):
    father, _, child = people
    editor.create_relationship(father.id, child.id, RelationshipType.ADOPTIVE_PARENT)
    assert editor.project.genealogy.get_parents(
        child.id, types=[RelationshipType.ADOPTIVE_PARENT]
    ) == (father,)


def test_editor_creates_marriage_and_partnership(editor, people):
    a, b, _ = people
    editor.create_relationship(a.id, b.id, RelationshipType.MARRIAGE, start_year=125)
    editor.create_relationship(a.id, b.id, RelationshipType.PARTNERSHIP, start_year=115)
    assert editor.project.genealogy.get_partners(b.id) == (a,)
    assert len(editor.list_relationships()) == 2


def test_rejected_duplicate_relationship_keeps_clean_state(tmp_path, editor, people):
    father, _, child = people
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    assert len(editor.list_relationships()) == 1 and not editor.is_dirty


def test_rejected_parentage_cycle_does_not_add_relationship(editor, people):
    a, _, b = people
    editor.create_relationship(a.id, b.id, RelationshipType.BIOLOGICAL_PARENT)
    with pytest.raises(ValueError):
        editor.create_relationship(b.id, a.id, RelationshipType.ADOPTIVE_PARENT)
    assert len(editor.list_relationships()) == 1


def test_missing_character_in_relation_is_rejected(editor, people):
    a = people[0]
    with pytest.raises(KeyError):
        editor.create_relationship(a.id, uuid4(), RelationshipType.MARRIAGE)


def test_remove_relationship_keeps_characters(editor, people):
    father, _, child = people
    rel = editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    assert editor.remove_relationship(rel.id) == rel
    assert editor.project.genealogy.get_children(father.id) == ()
    assert len(editor.list_characters()) == 3


def test_remove_unknown_relationship_does_not_dirty(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    with pytest.raises(KeyError):
        editor.remove_relationship(uuid4())
    assert not editor.is_dirty


def test_create_all_family_types(editor, people):
    for family_type in FamilyType:
        family = editor.create_family(f"A {family_type.value}", type=family_type)
        assert family.type == family_type
    assert len(editor.list_families()) == len(FamilyType)


def test_create_family_with_founder(editor, people):
    father = people[0]
    family = editor.create_family("Valerian", type=FamilyType.HOUSE, founder_id=father.id,
                                  founded_year=-60, motto="Um só estandarte")
    assert family.founder_id == father.id and family.founded_year == -60
    assert editor.project.get_family(family.id) == family


def test_create_family_rejects_unknown_founder(editor):
    with pytest.raises(KeyError):
        editor.create_family("Casa inválida", founder_id=uuid4())
    assert editor.list_families() == ()


def test_update_family_preserves_memberships(editor, people):
    father = people[0]
    family = editor.create_family("Velha", founder_id=father.id)
    member = editor.add_membership(family.id, father.id, origin=MembershipOrigin.FOUNDATION)
    family2 = editor.update_family(family.id, name="Nova", description="História")
    assert family2.id == family.id and family2.name == "Nova"
    assert editor.project.get_membership(member.id) == member


def test_update_family_noop_preserves_clean_state(tmp_path, editor, people):
    family = editor.create_family("Casa")
    editor.save(tmp_path / "a.json")
    assert editor.update_family(family.id, name=" Casa ") == family
    assert not editor.is_dirty


@pytest.mark.parametrize("field", ["id", "members", "characters", "unknown"])
def test_update_family_rejects_unknown_fields(editor, people, field):
    family = editor.create_family("Casa")
    with pytest.raises(ValueError):
        editor.update_family(family.id, **{field: None})
    assert editor.project.get_family(family.id) == family


def test_family_can_be_removed_without_deleting_people(editor, people):
    family = editor.create_family("Casa")
    editor.add_membership(family.id, people[0].id)
    editor.remove_family(family.id)
    assert editor.list_families() == () and len(editor.list_characters()) == 3


@pytest.mark.parametrize("origin", list(MembershipOrigin))
def test_membership_all_origins(editor, people, origin):
    family = editor.create_family("Casa")
    membership = editor.add_membership(family.id, people[0].id, origin=origin)
    assert membership.origin == origin
    assert editor.project.get_membership(membership.id) == membership


def test_membership_can_have_role_and_dates(editor, people):
    family = editor.create_family("Valerian")
    member = editor.add_membership(
        family.id, people[0].id, role="Fundador", start_year=125, end_year=150,
    )
    assert member.is_active_at(140)
    assert not member.is_active_at(151)


def test_membership_update_and_delete(editor, people):
    family = editor.create_family("Casa")
    member = editor.add_membership(family.id, people[0].id)
    changed = editor.update_membership(member.id, role="Herdeiro", start_year=-200)
    assert changed.id == member.id and changed.role == "Herdeiro"
    assert editor.remove_membership(member.id) == changed
    assert editor.list_memberships() == ()


@pytest.mark.parametrize("field", ["id", "family", "character", "invalid"])
def test_update_membership_rejects_unknown_fields(editor, people, field):
    family = editor.create_family("Casa")
    member = editor.add_membership(family.id, people[0].id)
    with pytest.raises(ValueError):
        editor.update_membership(member.id, **{field: None})
    assert editor.project.get_membership(member.id) == member


def test_update_membership_invalid_leaves_record(tmp_path, editor, people):
    family = editor.create_family("Casa")
    member = editor.add_membership(family.id, people[0].id)
    editor.save(tmp_path / "a.json")
    with pytest.raises(KeyError):
        editor.update_membership(member.id, family_id=uuid4())
    assert editor.project.get_membership(member.id) == member
    assert not editor.is_dirty


def test_delete_non_founder_removes_relations_and_memberships(editor, people):
    father, _, child = people
    family = editor.create_family("Casa")
    editor.add_membership(family.id, child.id)
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    assert editor.remove_character(child.id) == child
    assert editor.project.genealogy.get_children(father.id) == ()
    assert editor.list_memberships() == ()


def test_delete_founder_defaults_to_reject(editor, people):
    founder = people[0]
    family = editor.create_family("Casa", founder_id=founder.id)
    with pytest.raises(ValueError):
        editor.remove_character(founder.id)
    assert editor.project.get_family(family.id).founder_id == founder.id
    assert editor.project.get_character(founder.id) == founder


def test_delete_founder_with_clear(editor, people):
    founder = people[0]
    family = editor.create_family("Casa", founder_id=founder.id)
    editor.remove_character(founder.id, founder_policy="clear")
    assert editor.project.get_family(family.id).founder_id is None
    with pytest.raises(KeyError):
        editor.project.get_character(founder.id)


def test_delete_founder_reject_does_not_mark_dirty(tmp_path, editor, people):
    founder = people[0]
    editor.create_family("Casa", founder_id=founder.id)
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.remove_character(founder.id)
    assert not editor.is_dirty


def test_save_requires_path(editor):
    with pytest.raises(ValueError):
        editor.save()


def test_save_and_open_preserves_all_data_and_uuid(tmp_path, editor, people):
    father, spouse, child = people
    marriage = editor.create_relationship(father.id, spouse.id, RelationshipType.MARRIAGE)
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    family = editor.create_family("Casa Valerian", type=FamilyType.HOUSE, founder_id=father.id)
    membership = editor.add_membership(family.id, child.id, origin=MembershipOrigin.BIRTH)
    destination = tmp_path / "subdir" / "eldoria.json"
    assert editor.save(destination) == destination
    assert not editor.is_dirty and editor.path == destination
    loaded = Editor.open(destination)
    assert not loaded.is_dirty and loaded.path == destination
    assert loaded.project.id == editor.project.id
    assert loaded.project.get_character(father.id).full_name == "Arthur Valerian"
    assert loaded.project.get_relationship(marriage.id).type == RelationshipType.MARRIAGE
    assert loaded.project.get_family(family.id).name == "Casa Valerian"
    assert loaded.project.get_membership(membership.id).origin == MembershipOrigin.BIRTH


def test_save_to_existing_path_and_modify_again(tmp_path, editor, people):
    path = tmp_path / "data.json"
    editor.save(path)
    editor.create_character("Nova")
    assert editor.is_dirty
    assert editor.save() == path
    assert not editor.is_dirty
    assert any(c.name == "Nova" for c in Editor.open(path).list_characters())


def test_save_as_updates_path_only_after_success(tmp_path, editor):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    editor.save(a)
    editor.rename_project("Outro")
    editor.save(b)
    assert editor.path == b and a.exists() and b.exists()
    assert Project.load(a).name == "Eldoria"
    assert Project.load(b).name == "Outro"


def test_failed_save_does_not_mark_clean(monkeypatch, tmp_path, editor):
    editor.save(tmp_path / "old.json")
    editor.rename_project("Alterado")
    original = editor.path

    def fail(*args):
        raise PermissionError("Não pode gravar")

    monkeypatch.setattr(Project, "save", fail)
    with pytest.raises(PermissionError):
        editor.save(tmp_path / "new.json")
    assert editor.is_dirty and editor.path == original


def test_open_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        Editor.open(tmp_path / "inexistente.json")


def test_tree_layout_contains_all_people(editor, people):
    father, _, child = people
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    layout = editor.tree_layout()
    assert isinstance(layout, TreeLayout)
    assert {n.id for n in layout.graph.nodes} == {c.id for c in people}
    assert {p.character_id for p in layout.positions} == {c.id for c in people}


def test_tree_filter_descendants(editor, people):
    father, spouse, child = people
    editor.create_relationship(father.id, child.id, RelationshipType.BIOLOGICAL_PARENT)
    descendants = editor.tree_layout(root_id=father.id, direction="descendants",
                                     max_generations=1, include_partners=False)
    assert {node.id for node in descendants.graph.nodes} == {father.id, child.id}


def test_invalid_tree_parameters_do_not_change_project(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.tree_layout(direction="ancestors")
    assert not editor.is_dirty


def test_export_html_works_and_does_not_save_project(tmp_path, editor, people):
    editor.create_relationship(people[0].id, people[2].id, RelationshipType.BIOLOGICAL_PARENT)
    path = tmp_path / "page.html"
    assert editor.export_html(path) == path
    text = path.read_text(encoding="utf-8")
    assert "<!doctype html>" in text
    assert "Arthur Valerian" in text
    assert "Eldoria" in text
    assert editor.is_dirty and editor.path is None


def test_export_html_escapes_untrusted_text(tmp_path, editor):
    editor.create_character("</script><script>alert(1)</script>")
    path = editor.export_html(tmp_path / "page.html")
    data = path.read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in data
    assert "\\u003cscript" in data or "&lt;script" in data


def test_export_html_custom_options(tmp_path, editor):
    opts = ViewerOptions(title="Outro título", show_legend=False)
    html = editor.export_html(tmp_path / "page.html", options=opts)
    assert "Outro título" in html.read_text(encoding="utf-8")


def test_export_svg_valid_xml(tmp_path, editor, people):
    path = tmp_path / "tree.svg"
    assert editor.export_svg(path) == path
    root = ET.parse(path).getroot()
    assert root.tag.endswith("svg")
    assert "Elena" in path.read_text(encoding="utf-8")


def test_export_svg_custom_options(tmp_path, editor):
    path = editor.export_svg(tmp_path / "a.svg", options=SvgOptions(title="Outra árvore"))
    assert "Outra árvore" in path.read_text(encoding="utf-8")


def test_invalid_export_does_not_change_dirty_state(tmp_path, editor):
    editor.save(tmp_path / "a.json")
    with pytest.raises(ValueError):
        editor.export_html(tmp_path / "file.html", direction="ancestors")
    assert not editor.is_dirty


def test_editor_interactive_exit_without_dirty(monkeypatch, capsys, tmp_path, editor):
    editor.save(tmp_path / "a.json")
    monkeypatch.setattr("builtins.input", lambda prompt: "0")
    run_console(editor)
    assert "Até logo!" in capsys.readouterr().out


def test_editor_interactive_invalid_command_recovers(monkeypatch, capsys, tmp_path, editor):
    editor.save(tmp_path / "a.json")
    it = iter(["99", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(it))
    run_console(editor)
    output = capsys.readouterr().out
    assert "Opção desconhecida" in output and "Até logo" in output


def test_editor_interactive_create_save_exit(monkeypatch, capsys, tmp_path):
    savefile = tmp_path / "a.json"
    editor = Editor.new("Terras Antigas")
    answers = iter(["2", "Joana", "", "", "", "", "", "11", str(savefile), "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    run_console(editor)
    assert Editor.open(savefile).list_characters()[0].name == "Joana"
    assert not editor.is_dirty
    assert "Projeto salvo" in capsys.readouterr().out


def test_editor_interactive_exit_unsaved_cancel(monkeypatch, capsys, tmp_path):
    editor = Editor.new("A")
    answers = iter(["0", "c", "11", str(tmp_path / "a.json"), "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    run_console(editor)
    assert (tmp_path / "a.json").exists()
    assert not editor.is_dirty


def test_editor_interactive_exit_without_saving(monkeypatch, capsys):
    editor = Editor.new("A")
    answers = iter(["0", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    run_console(editor)
    assert "Até logo!" in capsys.readouterr().out
    assert editor.is_dirty


def test_editor_interactive_export_html(monkeypatch, tmp_path):
    file = tmp_path / "test.html"
    editor = Editor.new("Eldoria")
    answers = iter(["12", str(file), "0", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    run_console(editor)
    assert file.exists()


def test_editor_interactive_handles_validation_error(monkeypatch, capsys):
    editor = Editor.new("Eldoria")
    answers = iter(["6", "0", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    run_console(editor)
    assert "Não foi possível" in capsys.readouterr().out


def test_editor_main_creates_new_session(monkeypatch):
    seen = []
    monkeypatch.setattr("editor.editor.run_console", lambda editor: seen.append(editor))
    assert main(["--name", "O Reino"]) == 0
    assert seen[0].project.name == "O Reino" and seen[0].is_dirty


def test_editor_main_opens_existing_project(monkeypatch, tmp_path):
    existing = Project("Eldoria")
    filename = tmp_path / "saved.json"
    existing.save(filename)
    seen = []
    monkeypatch.setattr("editor.editor.run_console", lambda editor: seen.append(editor))
    assert main(["--file", str(filename)]) == 0
    assert seen[0].project.id == existing.id
    assert not seen[0].is_dirty


def test_editor_main_new_with_file(monkeypatch, tmp_path):
    filename = tmp_path / "missing.json"
    seen = []
    monkeypatch.setattr("editor.editor.run_console", lambda editor: seen.append(editor))
    assert main(["--file", str(filename), "--name", "Eldoria"]) == 0
    assert seen[0].project.name == "Eldoria"
    assert seen[0].path == filename and not filename.exists()

# ── Integração modular dos perfis do personagem (v3) ─────────────────────
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory, HistoryEvent


def test_editor_creates_character_with_four_components():
    e = Editor.new("Sarnília")
    person = e.create_character(
        "Artuin", surname="Hauck", birth_year=31,
        physical=PhysicalAttributes(height_m=1.68, weight_kg=80),
        personality=PersonalityProfile(traits=["Ambicioso"]),
        social=SocialProfile(title="Conde da Sarnília"),
        history=CharacterHistory(biography="Morro do Falcão"),
    )
    assert person.physical.height_m == 1.68
    assert person.personality.traits == ("Ambicioso",)
    assert person.social.title == "Conde da Sarnília"
    assert person.biography == person.history.biography == "Morro do Falcão"


def test_update_components_preserves_identity_and_other_data(tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Artuin", birth_year=31)
    e.save(tmp_path / "s.json")
    e.update_physical(c.id, height_m=1.68, weight_kg=80)
    e.update_personality(c.id, flaws=["Arrogante", "Cruel"])
    e.update_social(c.id, title="Conde", residence="Morro do Falcão")
    e.update_history(c.id, biography="Primeiro.\n\nSegundo.")
    actual = e.project.get_character(c.id)
    assert actual.id == c.id and actual.birth_year == 31
    assert actual.physical.weight_kg == 80
    assert actual.personality.flaws == ("Arrogante", "Cruel")
    assert actual.social.residence == "Morro do Falcão"
    assert actual.biography == actual.history.biography == "Primeiro.\n\nSegundo."
    assert e.is_dirty


def test_editor_modular_noop_is_clean(tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Sofia")
    e.save(tmp_path / "s.json")
    e.update_physical(c.id)
    e.update_personality(c.id)
    e.update_social(c.id)
    e.update_history(c.id)
    assert not e.is_dirty


@pytest.mark.parametrize("method", [
    "update_physical", "update_personality", "update_social", "update_history",
])
def test_editor_rejects_unknown_modular_fields_without_dirty(method, tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Sofia")
    e.save(tmp_path / "s.json")
    with pytest.raises(ValueError, match="Campos não editáveis"):
        getattr(e, method)(c.id, fake="bad")
    assert not e.is_dirty


@pytest.mark.parametrize("method,field,value", [
    ("update_physical", "height_m", -5),
    ("update_personality", "traits", [5]),
    ("update_social", "residence", 13),
    ("update_history", "biography", 123),
])
def test_editor_rejects_invalid_modular_values_atomically(method,field,value,tmp_path):
    e = Editor.new("X")
    c = e.create_character("X")
    e.save(tmp_path / "x.json")
    with pytest.raises((TypeError, ValueError)):
        getattr(e, method)(c.id, **{field:value})
    assert e.project.get_character(c.id) == c
    assert not e.is_dirty


def test_editor_history_event_and_removal(tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Sofia", birth_year=48)
    event = e.add_history_event(c.id, "Nascimento de Sofia", year=48)
    assert e.project.get_character(c.id).history.events == (event,)
    e.save(tmp_path / "s.json")
    assert e.remove_history_event(c.id, event.id) == event
    assert e.project.get_character(c.id).history.events == ()
    assert e.is_dirty


def test_editor_remove_unknown_event_does_not_dirty(tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Sofia")
    e.save(tmp_path / "s.json")
    with pytest.raises(KeyError):
        e.remove_history_event(c.id, uuid4())
    assert not e.is_dirty


def test_editor_profiles_survive_save_load_and_family_operations(tmp_path):
    e = Editor.new("Sarnília")
    a = e.create_character("Artuin", physical=PhysicalAttributes(height_m=1.68))
    sofia = e.create_character("Sofia", birth_year=48)
    family = e.create_family("Casa Hauck", founder_id=a.id)
    e.add_membership(family.id, a.id)
    e.add_membership(family.id, sofia.id)
    e.update_personality(a.id, traits=["Ambicioso"])
    e.add_history_event(a.id, "Investidura", year=67)
    path = tmp_path / "sarnilia.json"
    e.save(path)
    opened = Editor.open(path)
    c = opened.project.get_character(a.id)
    assert c.physical.height_m == 1.68
    assert c.personality.traits == ("Ambicioso",)
    assert c.history.events[0].year == 67
    assert opened.project.families.get_members(family.id)
    opened.remove_character(sofia.id)
    assert opened.project.get_character(a.id).physical.height_m == 1.68


def test_editor_update_history_directly_is_synchronized():
    e = Editor.new("X")
    c = e.create_character("X", biography="Texto antigo")
    e.update_character(c.id, history=CharacterHistory(biography="Novo"))
    updated = e.project.get_character(c.id)
    assert updated.biography == updated.history.biography == "Novo"


def test_editor_rejects_mismatched_biography():
    e = Editor.new("X")
    c = e.create_character("X")
    with pytest.raises(ValueError, match="devem coincidir"):
        e.update_character(c.id, biography="A", history=CharacterHistory(biography="B"))


def test_console_multiline_biography(monkeypatch, tmp_path):
    from editor.editor import _ask_text
    incoming = iter([":multi", "Primeiro parágrafo.", "", "Segundo parágrafo.", "."])
    monkeypatch.setattr("builtins.input", lambda _: next(incoming))
    assert _ask_text("Biografia: ") == "Primeiro parágrafo.\n\nSegundo parágrafo."


def test_console_multiline_profile_and_event(monkeypatch, tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Artuin")
    file = tmp_path / "sarnilia.json"
    # 15 editar físico, 19 acontecimento e salvar.
    entries = iter([
        "15", "1", "1,68", "80", "Ruivo", "", "", "", "", "", "",
        "19", "1", "Ascensão", "67", "Política", ":multi",
        "Era herdeiro.", "", "Virou conde.", ".",
        "11", str(file), "0",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entries))
    run_console(e)
    saved = Editor.open(file).list_characters()[0]
    assert saved.physical.height_m == 1.68
    assert saved.physical.weight_kg == 80
    assert saved.history.events[0].description == "Era herdeiro.\n\nVirou conde."


def test_console_keyboard_interrupt_offers_save(monkeypatch, tmp_path):
    e = Editor.new("Sarnília")
    e.create_character("Sofia")
    file = tmp_path / "interrompido.json"
    replies = iter([KeyboardInterrupt(), "s", str(file)])
    def answer(_):
        value = next(replies)
        if isinstance(value, BaseException):
            raise value
        return value
    monkeypatch.setattr("builtins.input", answer)
    run_console(e)
    assert Editor.open(file).list_characters()[0].name == "Sofia"


def test_edit_character_biography_can_be_cleared():
    e = Editor.new("X")
    c = e.create_character("X", biography="Texto antigo")
    updated = e.update_character(c.id, biography=None)
    assert updated.biography is None
    assert updated.history.biography is None


def test_console_autosave_requires_file():
    with pytest.raises(ValueError, match="caminho"):
        run_console(Editor.new("X"), autosave=True)


def test_console_autosave_after_mutation(monkeypatch, tmp_path):
    file = tmp_path / "sarnilia.json"
    e = Editor.new("Sarnília", path=file)
    inputs = iter(["2", "Sofia", "Hauck", "Feminino", "48", "", "", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run_console(e, autosave=True)
    assert Editor.open(file).list_characters()[0].full_name == "Sofia Hauck"
    assert not e.is_dirty


def test_main_autosave_needs_file(monkeypatch):
    with pytest.raises(SystemExit):
        main(["--autosave", "--name", "Sarnília"])


def test_editor_create_character_rejects_two_different_biographies():
    e = Editor.new("X")
    with pytest.raises(ValueError, match="devem coincidir"):
        e.create_character("X", biography="Uma", history=CharacterHistory(biography="Outra"))
    assert not e.list_characters()


@pytest.mark.parametrize("updates", [
    {"history": "invalido"},
    {"biography": "Texto", "history": 123},
])
def test_editor_rejects_invalid_history_type(updates):
    e = Editor.new("X")
    c = e.create_character("X")
    with pytest.raises(TypeError):
        e.update_character(c.id, **updates)
    assert e.project.get_character(c.id) == c


def test_console_removes_history_event(monkeypatch):
    e = Editor.new("X")
    c = e.create_character("X")
    e.add_history_event(c.id, "Primeiro", year=1)
    inputs = iter(["20", "1", "1", "s", "0", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    run_console(e)
    assert not e.project.get_character(c.id).history.events

# ---------------------------------------------------------------------------
# Editor — integração com organizações, religiões e persistência
# ---------------------------------------------------------------------------
from organization.organization import OrganizationType
from religion.religion import ReligionType
from religion.doctrine import DoctrineCategory


def test_editor_creates_organization_and_member_and_persists(tmp_path):
    e = Editor.new("Sarnília")
    c = e.create_character("Manohar", surname="Hauck")
    path = tmp_path / "sarnilia.json"
    e.save(path)
    org = e.create_organization("Ordem de Mezena", type=OrganizationType.RELIGIOUS_ORDER)
    m = e.add_organization_membership(org.id, c.id, role="Sumo-sacerdote", start_year=55)
    assert e.is_dirty
    e.save()
    restored = Editor.open(path)
    assert not restored.is_dirty
    assert restored.project.get_organization(org.id) == org
    assert restored.project.get_organization_membership(m.id).role == "Sumo-sacerdote"


def test_editor_creates_religion_deity_doctrine_and_persists(tmp_path):
    e = Editor.new("Sarnília")
    rel = e.create_religion("Mezena", type=ReligionType.POLYTHEISTIC)
    deity = e.create_deity("Mezena", domains=("sabedoria",))
    e.link_deity(rel.id, deity.id)
    doctrine = e.create_doctrine(rel.id, "Dever", "Seja honrado", category=DoctrineCategory.ETHICS)
    path = tmp_path / "sarnilia.json"
    e.save(path)
    loaded = Editor.open(path)
    assert loaded.list_religions() == (rel,)
    assert loaded.project.religions.get_deities(rel.id) == (deity,)
    assert loaded.project.get_doctrine(doctrine.id) == doctrine


def test_editor_invalid_organization_creation_does_not_mark_dirty(tmp_path):
    e = Editor.new("X")
    e.save(tmp_path / "x.json")
    with pytest.raises(KeyError):
        e.create_organization("Órfã", founder_id=uuid4())
    assert e.list_organizations() == ()
    assert not e.is_dirty


def test_editor_invalid_religion_creation_does_not_mark_dirty(tmp_path):
    e = Editor.new("X")
    e.save(tmp_path / "x.json")
    with pytest.raises(KeyError):
        e.create_religion("Órfã", founder_id=uuid4())
    assert e.list_religions() == ()
    assert not e.is_dirty


def test_editor_noop_org_update_keeps_clean_state(tmp_path):
    e = Editor.new("X")
    org = e.create_organization("Ordem")
    e.save(tmp_path / "x.json")
    assert e.update_organization(org.id, name="Ordem") == org
    assert not e.is_dirty


def test_editor_rejects_id_change_for_new_entities():
    e = Editor.new("X")
    org = e.create_organization("Ordem")
    rel = e.create_religion("Religião")
    deity = e.create_deity("Divindade")
    doctrine = e.create_doctrine(rel.id, "Doutrina", "Conteúdo")
    for callback, entity in (
        (e.update_organization, org), (e.update_religion, rel),
        (e.update_deity, deity), (e.update_doctrine, doctrine),
    ):
        with pytest.raises(ValueError):
            callback(entity.id, id=uuid4())


def test_editor_duplicate_deity_link_does_not_mark_dirty(tmp_path):
    e = Editor.new("X")
    rel = e.create_religion("Religião")
    deity = e.create_deity("Divindade")
    e.link_deity(rel.id, deity.id)
    e.save(tmp_path / "x.json")
    with pytest.raises(ValueError):
        e.link_deity(rel.id, deity.id)
    assert not e.is_dirty


def test_editor_org_submenu_creates_and_autosaves(monkeypatch, tmp_path):
    from editor.editor import _organization_console
    e = Editor.new("X", path=tmp_path / "x.json")
    # 2 cria organização; tipo=1, sem fundador=0, anos vazios, textos vazios; 0 volta.
    prompts = iter(["2", "Ordem", "1", "0", "", "", "", "", "", "", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))
    _organization_console(e, autosave=True)
    loaded = Editor.open(tmp_path / "x.json")
    assert loaded.list_organizations()[0].name == "Ordem"


def test_editor_religion_submenu_creates_and_autosaves(monkeypatch, tmp_path):
    from editor.editor import _religion_console
    e = Editor.new("X", path=tmp_path / "x.json")
    prompts = iter(["2", "Mezena", "8", "0", "0", "", "", "", "", "", "", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))
    _religion_console(e, autosave=True)
    loaded = Editor.open(tmp_path / "x.json")
    assert loaded.list_religions()[0].name == "Mezena"


def test_editor_organization_member_delete_preserves_character():
    e = Editor.new("X")
    c = e.create_character("Ayla")
    org = e.create_organization("Conselho")
    member = e.add_organization_membership(org.id, c.id)
    e.remove_organization_membership(member.id)
    assert e.project.get_character(c.id) == c
    assert e.list_organization_memberships() == ()
