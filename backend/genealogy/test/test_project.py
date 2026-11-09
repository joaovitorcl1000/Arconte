"""Testes da integração dos módulos do Arconte através de Project.

Execute a partir de ~/Arconte/backend/genealogy::

    python3 -m pytest test/test_project.py -v
    python3 -m pytest test/ -q

Os arquivos de teste usam tmp_path e não afetam arquivos de projetos reais.
Compatível com Python 3.10+ e pytest.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys
from uuid import UUID, uuid4

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from character.character import Character
from family.family import (
    Family, FamilyMembership, FamilyRegistry, FamilyType, MembershipOrigin,
)
from genealogy.genealogy import Genealogy
from project import project as project_module
from project.project import Project, PROJECT_FORMAT, PROJECT_VERSION
from relationship.relationship import Relationship, RelationshipType
from storage.storage import (
    StorageError, genealogy_to_dict, project_to_dict, save_genealogy, save_project,
)


@pytest.fixture
def populated() -> tuple[Project, Character, Character, Character, Family, Family]:
    """Projeto de fantasia com fundador, casamento, filiação e duas casas."""
    project = Project("  Crônicas de Éldoria  ", description="  Reino das florestas 🌳  ")
    arthur = Character(name="Árthur", surname="Valerian", birth_year=-400)
    elena = Character(name="Elena", birth_year=-390)
    edric = Character(name="Édric", birth_year=-360)
    for person in (arthur, elena, edric):
        project.add_character(person)
    project.add_relationship(Relationship(
        source_id=arthur.id, target_id=edric.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    ))
    project.add_relationship(Relationship(
        source_id=elena.id, target_id=edric.id,
        type=RelationshipType.ADOPTIVE_PARENT,
    ))
    project.add_relationship(Relationship(
        source_id=arthur.id, target_id=elena.id,
        type=RelationshipType.MARRIAGE, start_year=-380,
    ))
    valerian = Family(
        name="Casa Valerian", type=FamilyType.HOUSE,
        founder_id=arthur.id, founded_year=-410,
        motto="Honra, tradição e 🔥",
    )
    mist = Family(name="Clã da Névoa", type=FamilyType.CLAN)
    project.add_family(valerian)
    project.add_family(mist)
    project.add_membership(FamilyMembership(
        family_id=valerian.id, character_id=arthur.id,
        origin=MembershipOrigin.FOUNDATION, start_year=-410, role="Fundador",
    ))
    project.add_membership(FamilyMembership(
        family_id=valerian.id, character_id=edric.id,
        origin=MembershipOrigin.BIRTH, start_year=-360, role="Herdeiro",
    ))
    project.add_membership(FamilyMembership(
        family_id=mist.id, character_id=edric.id,
        origin=MembershipOrigin.ADOPTION, start_year=-350,
    ))
    return project, arthur, elena, edric, valerian, mist


def test_format_identifiers() -> None:
    assert PROJECT_FORMAT == "arconte.project"
    assert PROJECT_VERSION == 1


def test_new_project_is_empty_and_linked() -> None:
    project = Project("Eldoria")
    assert project.name == "Eldoria"
    assert project.description is None
    assert isinstance(project.id, UUID)
    assert isinstance(project.genealogy, Genealogy)
    assert isinstance(project.families, FamilyRegistry)
    assert project.get_all_characters() == ()
    assert project.get_all_families() == ()
    assert project.get_relationships() == ()
    assert project.get_memberships() == ()
    project.validate_integrity()


def test_independent_projects_have_independent_objects() -> None:
    first, second = Project("Mesmo nome"), Project("Mesmo nome")
    assert first.id != second.id
    person = Character(name="Visitante")
    first.add_character(person)
    assert second.get_all_characters() == ()


def test_explicit_uuid_is_preserved() -> None:
    pid = uuid4()
    project = Project("Eldoria", id=pid)
    assert project.id == pid


@pytest.mark.parametrize("invalid", ["", "   ", None, 123, True, [], {}])
def test_invalid_project_name_is_rejected(invalid: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        Project(invalid)


@pytest.mark.parametrize("invalid", [False, 12, [], {}, 1.5])
def test_invalid_project_description_is_rejected(invalid: object) -> None:
    with pytest.raises(TypeError):
        Project("Eldoria", description=invalid)


@pytest.mark.parametrize("invalid", ["uuid", 0, [], object()])
def test_invalid_project_id_is_rejected(invalid: object) -> None:
    with pytest.raises(TypeError):
        Project("Eldoria", id=invalid)


def test_normalizes_name_and_description() -> None:
    project = Project("  O  Reino  ", description="  História de Érion ✨  ")
    assert project.name == "O  Reino"
    assert project.description == "História de Érion ✨"
    project.set_description(" \t ")
    assert project.description is None


def test_rename_and_description_updates_preserve_id() -> None:
    project = Project("Antigo", description="Anterior")
    original_id = project.id
    project.rename(" Novo ")
    project.set_description(None)
    assert (project.name, project.description, project.id) == ("Novo", None, original_id)


def test_invalid_rename_does_not_change_metadata() -> None:
    project = Project("Bom")
    with pytest.raises(ValueError):
        project.rename("   ")
    with pytest.raises(TypeError):
        project.set_description(22)
    assert (project.name, project.description) == ("Bom", None)


def test_character_methods_delegate_to_genealogy(populated) -> None:
    project, arthur, _, edric, _, _ = populated
    assert project.get_character(arthur.id) == arthur
    updated = replace(edric, biography="Herdeiro de Éldoria")
    project.update_character(updated)
    assert project.get_character(edric.id).biography == "Herdeiro de Éldoria"
    assert len(project.get_all_characters()) == 3


def test_rejects_duplicate_character_through_project() -> None:
    project = Project("Eldoria")
    person = Character(name="Arthur")
    project.add_character(person)
    with pytest.raises(ValueError):
        project.add_character(person)
    assert project.get_all_characters() == (person,)


def test_relationship_operations_preserve_direction_and_uuids(populated) -> None:
    project, arthur, _, edric, _, _ = populated
    relationship = next(
        rel for rel in project.get_relationships()
        if rel.source_id == arthur.id and rel.target_id == edric.id
    )
    assert project.get_relationship(relationship.id) == relationship
    assert arthur in project.genealogy.get_parents(edric.id)
    assert project.remove_relationship(relationship.id) == relationship
    assert arthur not in project.genealogy.get_parents(edric.id)
    project.add_relationship(relationship)
    assert arthur in project.genealogy.get_parents(edric.id)


def test_invalid_relationship_is_rejected_without_change() -> None:
    project = Project("Eldoria")
    first, second = Character(name="A"), Character(name="B")
    project.add_character(first)
    rel = Relationship(source_id=first.id, target_id=second.id,
                       type=RelationshipType.BIOLOGICAL_PARENT)
    with pytest.raises(KeyError):
        project.add_relationship(rel)
    assert project.get_relationships() == ()


def test_family_operations_delegate_to_registry(populated) -> None:
    project, arthur, _, _, family, _ = populated
    assert project.get_family(family.id) == family
    updated = replace(family, motto="Nova divisa")
    project.update_family(updated)
    assert project.get_family(family.id).motto == "Nova divisa"
    removed = project.remove_family(family.id)
    assert removed.id == family.id
    assert len(project.get_all_families()) == 1
    assert len(project.get_all_characters()) == 3
    assert project.get_character(arthur.id) == arthur


def test_membership_operations_delegate_to_registry(populated) -> None:
    project, _, _, edric, _, mist = populated
    existing = next(m for m in project.get_memberships() if m.family_id == mist.id)
    assert project.get_membership(existing.id) == existing
    moved = replace(existing, role="Guardião da névoa")
    project.update_membership(moved)
    assert project.get_membership(existing.id).role == "Guardião da névoa"
    assert project.remove_membership(existing.id) == moved
    assert project.families.get_memberships(family_id=mist.id) == ()
    assert project.get_character(edric.id) == edric


def test_multiple_families_are_not_genealogical_relationships(populated) -> None:
    project, _, _, edric, _, _ = populated
    families = project.families.get_families_for_character(edric.id)
    assert len(families) == 2
    assert len(project.genealogy.get_parents(edric.id)) == 2


def test_remove_unaffiliated_character() -> None:
    project = Project("Eldoria")
    person = Character(name="Visitante")
    project.add_character(person)
    assert project.remove_character(person.id) == person
    assert project.get_all_characters() == ()
    project.validate_integrity()


def test_remove_member_cascades_memberships_and_parentage(populated) -> None:
    project, _, _, edric, _, mist = populated
    before = project.to_dict()
    genealogy_ref = project.genealogy
    removed = project.remove_character(edric.id)
    assert removed == edric
    assert len(project.get_all_characters()) == 2
    assert all(r.source_id != edric.id and r.target_id != edric.id
               for r in project.get_relationships())
    assert all(m.character_id != edric.id for m in project.get_memberships())
    assert project.families.get_memberships(family_id=mist.id) == ()
    assert project.genealogy is not genealogy_ref  # implementação transacional
    assert project.to_dict() != before
    project.validate_integrity()


def test_remove_founder_rejects_without_side_effects(populated) -> None:
    project, arthur, _, _, _, _ = populated
    original_document = project.to_dict()
    original_genealogy = project.genealogy
    original_families = project.families
    with pytest.raises(ValueError, match="fundador"):
        project.remove_character(arthur.id)
    assert project.to_dict() == original_document
    assert project.genealogy is original_genealogy
    assert project.families is original_families


def test_remove_founder_can_clear_its_references(populated) -> None:
    project, arthur, _, edric, valerian, _ = populated
    project.remove_character(arthur.id, founder_policy="clear")
    assert project.get_family(valerian.id).founder_id is None
    assert arthur.id not in (person.id for person in project.get_all_characters())
    assert all(m.character_id != arthur.id for m in project.get_memberships())
    assert project.genealogy.get_parents(edric.id)  # Elena continua mãe adotiva
    project.validate_integrity()


def test_remove_founder_of_multiple_families() -> None:
    project = Project("Eldoria")
    founder = Character(name="Fundador")
    project.add_character(founder)
    families = [Family(name=f"Casa {i}", founder_id=founder.id) for i in range(3)]
    for family in families:
        project.add_family(family)
    project.remove_character(founder.id, founder_policy="clear")
    assert all(f.founder_id is None for f in project.get_all_families())
    assert len(project.get_all_families()) == 3


@pytest.mark.parametrize("invalid", [None, "delete", "", 123])
def test_remove_character_invalid_policy_does_not_change_project(populated, invalid) -> None:
    project, _, _, edric, _, _ = populated
    state = project.to_dict()
    with pytest.raises((TypeError, ValueError)):
        project.remove_character(edric.id, founder_policy=invalid)
    assert project.to_dict() == state


def test_remove_unknown_character_is_not_destructive(populated) -> None:
    project, *_ = populated
    original = project.to_dict()
    with pytest.raises(KeyError):
        project.remove_character(uuid4())
    assert project.to_dict() == original


def test_direct_inconsistent_mutation_is_detected_before_remove(populated) -> None:
    project, arthur, _, _, _, _ = populated
    project.genealogy.remove_character(arthur.id)  # edição externa incorreta
    with pytest.raises(StorageError):
        project.remove_character(project.get_all_characters()[0].id,
                                 founder_policy="clear")


def test_project_roundtrip_saves_all_data_and_metadata(populated, tmp_path: Path) -> None:
    project, arthur, _, edric, family, _ = populated
    path = tmp_path / "nested" / "eldoria.json"
    project.save(path)
    restored = Project.load(path)
    assert restored is not project
    assert restored.id == project.id
    assert restored.name == project.name
    assert restored.description == project.description
    assert restored.to_dict() == project.to_dict()
    assert restored.get_family(family.id).founder_id == arthur.id
    assert arthur in restored.genealogy.get_parents(edric.id)
    assert set(restored.families.get_families_for_character(edric.id)) == set(
        project.families.get_families_for_character(edric.id)
    )
    restored.validate_integrity()


def test_project_roundtrip_empty(tmp_path: Path) -> None:
    project = Project("Vazio")
    project.save(tmp_path / "vazio.json")
    assert Project.load(tmp_path / "vazio.json").to_dict() == project.to_dict()


def test_saved_file_has_project_envelope_and_v2_data(populated, tmp_path: Path) -> None:
    project, *_ = populated
    path = tmp_path / "project.json"
    project.save(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert set(document) == {"format", "version", "metadata", "data"}
    assert document["format"] == PROJECT_FORMAT
    assert document["version"] == PROJECT_VERSION
    assert document["metadata"]["id"] == str(project.id)
    assert document["data"]["format"] == "arconte.genealogy"
    assert document["data"]["version"] == 2
    assert isinstance(document["data"]["families"], list)


def test_to_dict_is_json_serializable_and_deterministic(populated) -> None:
    project, *_ = populated
    state = project.to_dict()
    assert json.loads(json.dumps(state)) == state
    assert project.to_dict() == state


def test_from_dict_does_not_mutate_input(populated) -> None:
    project, *_ = populated
    original = project.to_dict()
    doc_copy = deepcopy(original)
    restored = Project.from_dict(original)
    assert original == doc_copy
    assert restored.to_dict() == doc_copy


def test_legacy_v1_file_can_be_imported(populated, tmp_path: Path) -> None:
    project, *_ = populated
    file = tmp_path / "antiga_genealogia.json"
    save_genealogy(project.genealogy, file)
    migrated = Project.load(file)
    assert migrated.name == "antiga_genealogia"
    assert migrated.id != project.id
    assert len(migrated.get_all_characters()) == 3
    assert len(migrated.get_relationships()) == 3
    assert migrated.get_all_families() == ()
    assert migrated.get_memberships() == ()


def test_legacy_v2_file_can_be_imported(populated, tmp_path: Path) -> None:
    project, *_ = populated
    file = tmp_path / "antigo_projeto.json"
    save_project(project.genealogy, project.families, file)
    migrated = Project.load(file)
    assert migrated.name == "antigo_projeto"
    assert migrated.id != project.id
    assert project_to_dict(migrated.genealogy, migrated.families) == project_to_dict(
        project.genealogy, project.families
    )


def test_legacy_import_migrates_to_current_format(populated, tmp_path: Path) -> None:
    project, *_ = populated
    legacy = tmp_path / "familias.json"
    modern = tmp_path / "atualizado.json"
    save_project(project.genealogy, project.families, legacy)
    restored = Project.load(legacy)
    restored.save(modern)
    assert Project.load(modern).to_dict() == restored.to_dict()


def test_import_from_v1_dict_accepts_custom_name(populated) -> None:
    project, *_ = populated
    migrated = Project.from_dict(genealogy_to_dict(project.genealogy),
                                 legacy_name="Novo universo")
    assert migrated.name == "Novo universo"
    assert migrated.get_all_families() == ()


@pytest.mark.parametrize("invalid", [None, 4, [], True, "json"])
def test_from_dict_rejects_non_object(invalid: object) -> None:
    with pytest.raises(StorageError):
        Project.from_dict(invalid)


def test_from_dict_rejects_unknown_format(populated) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["format"] = "unknown"
    with pytest.raises(StorageError):
        Project.from_dict(document)


@pytest.mark.parametrize("version", [0, 2, True, "1", None])
def test_from_dict_rejects_invalid_version(populated, version) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["version"] = version
    with pytest.raises(StorageError):
        Project.from_dict(document)


@pytest.mark.parametrize("key", ["format", "version", "metadata", "data"])
def test_from_dict_rejects_missing_fields(populated, key) -> None:
    project, *_ = populated
    document = project.to_dict()
    document.pop(key)
    with pytest.raises(StorageError):
        Project.from_dict(document)


def test_from_dict_rejects_extra_fields(populated) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["unexpected"] = 20
    with pytest.raises(StorageError):
        Project.from_dict(document)


@pytest.mark.parametrize("bad_id", [None, "bad-uuid", 34])
def test_from_dict_rejects_invalid_project_id(populated, bad_id) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["metadata"]["id"] = bad_id
    with pytest.raises(StorageError):
        Project.from_dict(document)


def test_from_dict_rejects_invalid_project_name(populated) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["metadata"]["name"] = ""
    with pytest.raises(StorageError):
        Project.from_dict(document)


def test_from_dict_rejects_extra_metadata(populated) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["metadata"]["owner"] = "algum usuário"
    with pytest.raises(StorageError):
        Project.from_dict(document)


def test_from_dict_rejects_invalid_nested_genealogy(populated) -> None:
    project, *_ = populated
    document = project.to_dict()
    document["data"]["characters"] = []  # casas têm fundadores órfãos
    with pytest.raises(StorageError):
        Project.from_dict(document)


def test_load_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Project.load(tmp_path / "missing.json")


@pytest.mark.parametrize("contents", ["{", "not json", "", "[1, 2", "NaN"])
def test_load_rejects_malformed_json(tmp_path: Path, contents: str) -> None:
    file = tmp_path / "invalid.json"
    file.write_text(contents, encoding="utf-8")
    with pytest.raises(StorageError):
        Project.load(file)


def test_load_rejects_invalid_utf8(tmp_path: Path) -> None:
    file = tmp_path / "bytes.json"
    file.write_bytes(b"\xff\xfe\xf8")
    with pytest.raises(StorageError):
        Project.load(file)


def test_load_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    file = tmp_path / "duplicates.json"
    file.write_text('{"format": "arconte.project", "format": "arconte.project"}',
                    encoding="utf-8")
    with pytest.raises(StorageError, match="repetida"):
        Project.load(file)


def test_save_preserves_existing_file_if_replace_fails(populated, tmp_path, monkeypatch) -> None:
    project, *_ = populated
    file = tmp_path / "project.json"
    file.write_text("conteúdo anterior", encoding="utf-8")

    def fail_replace(*args):
        raise OSError("falha simulada de troca")

    monkeypatch.setattr(project_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulada"):
        project.save(file)
    assert file.read_text(encoding="utf-8") == "conteúdo anterior"
    assert list(tmp_path.glob(".*.tmp")) == []


def test_save_invalid_state_does_not_touch_file(populated, tmp_path: Path) -> None:
    project, arthur, *_ = populated
    file = tmp_path / "project.json"
    file.write_text("anterior", encoding="utf-8")
    project.genealogy.remove_character(arthur.id)  # simular edição direta perigosa
    with pytest.raises(StorageError):
        project.save(file)
    assert file.read_text(encoding="utf-8") == "anterior"
    assert list(tmp_path.iterdir()) == [file]


def test_save_twice_rewrites_same_content(populated, tmp_path: Path) -> None:
    project, *_ = populated
    file = tmp_path / "projeto.json"
    project.save(file)
    before = file.read_bytes()
    project.save(file)
    assert file.read_bytes() == before


def test_updates_after_load_persist(populated, tmp_path: Path) -> None:
    project, _, _, edric, _, _ = populated
    file = tmp_path / "save.json"
    project.save(file)
    loaded = Project.load(file)
    loaded.update_character(replace(loaded.get_character(edric.id), name="Novo Édric"))
    loaded.rename("Crônicas do Novo Reino")
    loaded.save(file)
    again = Project.load(file)
    assert again.get_character(edric.id).name == "Novo Édric"
    assert again.name == "Crônicas do Novo Reino"
    assert again.id == project.id


def test_repr_is_useful(populated) -> None:
    project, *_ = populated
    assert project.name in repr(project)
    assert str(project.id) in repr(project)

# ---------------------------------------------------------------------------
# Integração institucional — organizações e religiões (envelope v2)
# ---------------------------------------------------------------------------
from organization.organization import Organization, OrganizationType
from organization.membership import OrganizationMembership
from organization.registry import OrganizationRegistry
from religion.religion import Religion, ReligionType
from religion.deity import Deity
from religion.doctrine import Doctrine, DoctrineCategory
from religion.registry import ReligionRegistry
from project.project import EXTENDED_PROJECT_VERSION


def test_extended_project_initializes_linked_registries():
    p = Project("Sarnília")
    assert isinstance(p.organizations, OrganizationRegistry)
    assert isinstance(p.religions, ReligionRegistry)
    assert p.get_all_organizations() == ()
    assert p.get_all_religions() == ()
    assert p.to_dict()["version"] == PROJECT_VERSION


def test_organization_and_membership_roundtrip_v2(tmp_path):
    p = Project("Sarnília")
    manohar = Character(name="Manohar", surname="Hauck")
    p.add_character(manohar)
    order = Organization(name="Ordem do Bosque", founder_id=manohar.id,
                         type=OrganizationType.RELIGIOUS_ORDER)
    p.add_organization(order)
    membership = OrganizationMembership(organization_id=order.id, character_id=manohar.id,
                                        role="Sumo-sacerdote", start_year=45)
    p.add_organization_membership(membership)
    doc = p.to_dict()
    assert doc["version"] == EXTENDED_PROJECT_VERSION == 2
    assert set(doc) == {"format", "version", "metadata", "data", "organizations", "religions"}
    dest = tmp_path / "sarnilia.json"
    p.save(dest)
    restored = Project.load(dest)
    assert restored.to_dict() == doc
    assert restored.get_organization(order.id).name == "Ordem do Bosque"
    assert restored.get_organization_membership(membership.id).role == "Sumo-sacerdote"
    assert restored.organizations.get_members(order.id)[0].id == manohar.id


def test_religion_deity_doctrine_and_origin_roundtrip(tmp_path):
    p = Project("Sarnília")
    founder = Character(name="Fundador")
    p.add_character(founder)
    mezena = Religion(name="Mezena", founder_id=founder.id,
                      type=ReligionType.POLYTHEISTIC)
    p.add_religion(mezena)
    sect = Religion(name="Reforma de Mezena", parent_religion_id=mezena.id)
    p.add_religion(sect)
    deity = Deity(name="Mezena", domains=("Sabedoria",))
    p.add_deity(deity)
    p.link_deity(mezena.id, deity.id)
    doctrine = Doctrine(religion_id=mezena.id, title="O juramento", content="Texto sagrado")
    p.add_doctrine(doctrine)
    dest = tmp_path / "religion.json"
    p.save(dest)
    restored = Project.load(dest)
    assert restored.to_dict() == p.to_dict()
    assert restored.get_deities(mezena.id)[0].id == deity.id
    assert restored.get_doctrine(doctrine.id).content == "Texto sagrado"
    assert restored.religions.get_derived_religions(mezena.id)[0].id == sect.id


def test_deity_alone_still_uses_extended_envelope_and_persists(tmp_path):
    p = Project("Panteão")
    deity = Deity(name="Entidade")
    p.add_deity(deity)
    assert p.to_dict()["version"] == 2
    path = tmp_path / "pantheon.json"
    p.save(path)
    assert Project.load(path).get_deity(deity.id) == deity


def test_project_checks_nonexistent_religious_founder():
    p = Project("X")
    with pytest.raises(KeyError):
        p.add_religion(Religion(name="Fé", founder_id=uuid4()))
    assert p.get_all_religions() == ()


def test_project_checks_nonexistent_organization_founder():
    p = Project("X")
    with pytest.raises(KeyError):
        p.add_organization(Organization(name="Ordem", founder_id=uuid4()))
    assert p.get_all_organizations() == ()


def test_remove_character_clears_organization_membership_atomically():
    p = Project("X")
    c = Character(name="Membro")
    p.add_character(c)
    org = Organization(name="Ordem")
    p.add_organization(org)
    m = OrganizationMembership(organization_id=org.id, character_id=c.id)
    p.add_organization_membership(m)
    p.remove_character(c.id)
    assert p.get_all_characters() == ()
    assert p.get_organization_memberships() == ()
    assert p.get_organization(org.id) == org
    p.validate_integrity()


@pytest.mark.parametrize("kind", ["family", "organization", "religion"])
def test_remove_founder_reject_is_unchanged_for_every_registry(kind):
    p = Project("X")
    c = Character(name="Fundador")
    p.add_character(c)
    if kind == "family":
        p.add_family(Family(name="Casa", founder_id=c.id))
    elif kind == "organization":
        p.add_organization(Organization(name="Ordem", founder_id=c.id))
    else:
        p.add_religion(Religion(name="Tradição", founder_id=c.id))
    before = p.to_dict()
    with pytest.raises(ValueError, match="fundador"):
        p.remove_character(c.id)
    assert p.to_dict() == before


def test_remove_character_clear_all_founder_types():
    p = Project("X")
    c = Character(name="Fundador")
    p.add_character(c)
    f = Family(name="Casa", founder_id=c.id)
    o = Organization(name="Ordem", founder_id=c.id)
    r = Religion(name="Tradição", founder_id=c.id)
    p.add_family(f)
    p.add_organization(o)
    p.add_religion(r)
    p.remove_character(c.id, founder_policy="clear")
    assert p.get_family(f.id).founder_id is None
    assert p.get_organization(o.id).founder_id is None
    assert p.get_religion(r.id).founder_id is None
    p.validate_integrity()


def test_old_v1_project_roundtrip_does_not_gain_extra_keys(tmp_path):
    p = Project("Legacy")
    p.add_character(Character(name="Artuin"))
    path = tmp_path / "legacy.json"
    p.save(path)
    assert set(p.to_dict()) == {"format", "version", "metadata", "data"}
    assert Project.load(path).to_dict()["version"] == 1


def test_extended_project_unknown_top_level_key_fails():
    p = Project("X")
    p.add_religion(Religion(name="X"))
    data = p.to_dict()
    data["extras"] = True
    with pytest.raises(StorageError):
        Project.from_dict(data)


def test_extended_project_missing_registry_fails():
    p = Project("X")
    p.add_religion(Religion(name="X"))
    data = p.to_dict()
    del data["religions"]
    with pytest.raises(StorageError):
        Project.from_dict(data)


def test_extended_project_rejects_orphan_religion_founder_on_load():
    p = Project("X")
    p.add_religion(Religion(name="X"))
    doc = p.to_dict()
    doc["religions"]["religions"][0]["founder_id"] = str(uuid4())
    with pytest.raises(StorageError, match="Registros institucionais"):
        Project.from_dict(doc)


def test_remove_organizations_and_religions_reverts_to_v1():
    p = Project("X")
    org = Organization(name="Ordem")
    rel = Religion(name="Religião")
    p.add_organization(org)
    p.add_religion(rel)
    assert p.to_dict()["version"] == 2
    p.remove_organization(org.id)
    p.remove_religion(rel.id)
    assert p.to_dict()["version"] == 1


def test_extended_save_is_atomic_on_invalid_institution_founder(tmp_path):
    p = Project("X")
    path = tmp_path / "preserved.json"
    p.save(path)
    before = path.read_bytes()
    # Mudança direta no registro, após a qual se remove o personagem por fora.
    person = Character(name="Fundador")
    p.add_character(person)
    p.add_religion(Religion(name="Fé", founder_id=person.id))
    p.genealogy.remove_character(person.id)
    with pytest.raises(KeyError):
        p.save(path)
    assert path.read_bytes() == before
