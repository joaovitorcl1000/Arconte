"""Testes unificados de persistência JSON do Arconte (v1 e v2).

Execute a partir de ~/Arconte/backend/genealogy:

    python3 -m pytest test/test_storage.py -v
    python3 -m pytest test/ -q

Cobertura:
- v1: personagens, parentescos e compatibilidade da API legada;
- v2: famílias, casas, clãs, dinastias e afiliações históricas;
- migração v1 -> v2, integridade e gravação atômica.

Utiliza o fixture tmp_path do pytest: não altera arquivos do escritor.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
from uuid import uuid4

import pytest

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
from storage import storage as storage_module
from storage.storage import (
    FORMAT,
    FORMAT_VERSION,
    PROJECT_FORMAT_VERSION,
    StorageError,
    genealogy_from_dict,
    genealogy_to_dict,
    load_genealogy,
    load_project,
    project_from_dict,
    project_to_dict,
    save_genealogy,
    save_project,
)


# ===========================================================================
# Compatibilidade v1: testes da API save_genealogy/load_genealogy
# ===========================================================================

@pytest.fixture
def sample_genealogy() -> Genealogy:
    """Genealogia com acentos, datas fictícias e diferentes tipos de vínculo."""
    genealogy = Genealogy()
    alvaro = Character(
        name="Álvaro",
        surname="de São João",
        gender="Masculino",
        birth_year=-1200,
        death_year=-1100,
        biography="Fundador da casa; dragões, magia e ✨.",
    )
    beatriz = Character(name="Beatriz", gender="Feminino", birth_year=-1190)
    caio = Character(name="Caio", birth_year=-1160)
    dalia = Character(name="Dália", biography="Viajante de Érion")
    for person in (dalia, caio, alvaro, beatriz):
        genealogy.add_character(person)

    for relationship in (
        Relationship(
            source_id=alvaro.id,
            target_id=beatriz.id,
            type=RelationshipType.MARRIAGE,
            start_year=-1180,
            end_year=-1150,
        ),
        Relationship(
            source_id=alvaro.id,
            target_id=caio.id,
            type=RelationshipType.BIOLOGICAL_PARENT,
        ),
        Relationship(
            source_id=beatriz.id,
            target_id=caio.id,
            type=RelationshipType.ADOPTIVE_PARENT,
        ),
        Relationship(
            source_id=caio.id,
            target_id=dalia.id,
            type=RelationshipType.PARTNERSHIP,
        ),
    ):
        genealogy.add_relationship(relationship)
    return genealogy


@pytest.fixture
def sample_document(sample_genealogy: Genealogy) -> dict:
    return genealogy_to_dict(sample_genealogy)


def test_empty_genealogy_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    save_genealogy(Genealogy(), path)
    loaded = load_genealogy(path)
    assert genealogy_to_dict(loaded) == {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "characters": [],
        "relationships": [],
    }


def test_roundtrip_preserves_all_character_and_relationship_data(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "genealogia.json"
    original = genealogy_to_dict(sample_genealogy)
    save_genealogy(sample_genealogy, path)
    restored = load_genealogy(path)
    assert isinstance(restored, Genealogy)
    assert genealogy_to_dict(restored) == original


def test_roundtrip_preserves_uuid_identity_and_relationship_types(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "identidade.json"
    save_genealogy(sample_genealogy, path)
    restored = load_genealogy(path)

    original_characters = {c.id: c for c in sample_genealogy.get_all_characters()}
    restored_characters = {c.id: c for c in restored.get_all_characters()}
    assert restored_characters == original_characters

    original_relationships = {r.id: r for r in sample_genealogy.get_relationships()}
    restored_relationships = {r.id: r for r in restored.get_relationships()}
    assert restored_relationships == original_relationships
    assert {r.type for r in restored_relationships.values()} == set(RelationshipType)


def test_roundtrip_preserves_genealogical_queries(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "queries.json"
    save_genealogy(sample_genealogy, path)
    restored = load_genealogy(path)
    people = {person.name: person for person in restored.get_all_characters()}

    caio = people["Caio"]
    alvaro = people["Álvaro"]
    beatriz = people["Beatriz"]
    dalia = people["Dália"]
    assert {p.id for p in restored.get_parents(caio.id)} == {alvaro.id, beatriz.id}
    assert {p.id for p in restored.get_children(alvaro.id)} == {caio.id}
    assert {p.id for p in restored.get_partners(alvaro.id)} == {beatriz.id}
    assert {p.id for p in restored.get_partners(dalia.id)} == {caio.id}
    assert {p.id for p in restored.get_ancestors(caio.id)} == {alvaro.id, beatriz.id}


def test_to_dict_is_json_serializable(sample_document: dict) -> None:
    assert json.loads(json.dumps(sample_document)) == sample_document


def test_from_dict_is_an_inverse_of_to_dict(sample_document: dict) -> None:
    restored = genealogy_from_dict(sample_document)
    assert genealogy_to_dict(restored) == sample_document


def test_from_dict_does_not_modify_input(sample_document: dict) -> None:
    original = deepcopy(sample_document)
    genealogy_from_dict(sample_document)
    assert sample_document == original


def test_serialization_has_stable_uuid_order(sample_document: dict) -> None:
    for field in ("characters", "relationships"):
        ids = [item["id"] for item in sample_document[field]]
        assert ids == sorted(ids)


def test_file_is_utf8_and_keeps_accents_and_emoji(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "acentuação.json"
    save_genealogy(sample_genealogy, path)
    contents = path.read_text(encoding="utf-8")
    assert "Álvaro" in contents
    assert "São João" in contents
    assert "dragões" in contents
    assert "✨" in contents
    assert contents.endswith("\n")


def test_save_creates_nested_directories(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "universos" / "Érion" / "familias" / "familia.json"
    save_genealogy(sample_genealogy, path)
    assert path.is_file()
    assert genealogy_to_dict(load_genealogy(path)) == genealogy_to_dict(sample_genealogy)


def test_v1_save_and_load_accept_string_paths(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = str(tmp_path / "string-path.json")
    save_genealogy(sample_genealogy, path)
    assert genealogy_to_dict(load_genealogy(path)) == genealogy_to_dict(sample_genealogy)


def test_saving_overwrites_existing_document(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    path = tmp_path / "overwrite.json"
    save_genealogy(Genealogy(), path)
    save_genealogy(sample_genealogy, path)
    assert genealogy_to_dict(load_genealogy(path)) == genealogy_to_dict(sample_genealogy)


def test_repeated_save_is_deterministic(
    sample_genealogy: Genealogy, tmp_path: Path
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    save_genealogy(sample_genealogy, first)
    save_genealogy(sample_genealogy, second)
    assert first.read_bytes() == second.read_bytes()


def test_to_dict_rejects_non_genealogy_object() -> None:
    with pytest.raises(TypeError):
        genealogy_to_dict({"characters": []})  # type: ignore[arg-type]


@pytest.mark.parametrize("document", [None, [], 123, "a string"])
def test_from_dict_rejects_non_object(document: object) -> None:
    with pytest.raises(StorageError):
        genealogy_from_dict(document)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("format", "another.format"),
        ("format", None),
        ("version", 0),
        ("version", 2),
        ("version", "1"),
        ("version", True),
        ("characters", None),
        ("characters", {}),
        ("relationships", None),
        ("relationships", {}),
    ],
)
def test_document_rejects_invalid_header_or_collection(
    sample_document: dict, field: str, value: object
) -> None:
    sample_document[field] = value
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


@pytest.mark.parametrize("missing_field", ["format", "version", "characters", "relationships"])
def test_document_rejects_missing_fields(
    sample_document: dict, missing_field: str
) -> None:
    del sample_document[missing_field]
    with pytest.raises(StorageError, match="campos ausentes"):
        genealogy_from_dict(sample_document)


def test_document_rejects_extra_fields(sample_document: dict) -> None:
    sample_document["unexpected"] = "value"
    with pytest.raises(StorageError, match="campos desconhecidos"):
        genealogy_from_dict(sample_document)


@pytest.mark.parametrize("bad_record", [None, 123, [], "invalid"])
def test_character_rejects_non_object_record(
    sample_document: dict, bad_record: object
) -> None:
    sample_document["characters"][0] = bad_record
    with pytest.raises(StorageError, match="characters"):
        genealogy_from_dict(sample_document)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "not-a-uuid"),
        ("id", 12),
        ("name", "   "),
        ("name", None),
        ("surname", 12),
        ("birth_year", 1.5),
        ("birth_year", True),
        ("death_year", "100"),
    ],
)
def test_character_rejects_invalid_field_values(
    sample_document: dict, field: str, value: object
) -> None:
    sample_document["characters"][0][field] = value
    with pytest.raises(StorageError, match="characters"):
        genealogy_from_dict(sample_document)


def test_character_rejects_death_before_birth(sample_document: dict) -> None:
    entry = sample_document["characters"][0]
    entry["birth_year"] = 100
    entry["death_year"] = 50
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_character_rejects_missing_and_extra_fields(sample_document: dict) -> None:
    missing = deepcopy(sample_document)
    del missing["characters"][0]["name"]
    with pytest.raises(StorageError):
        genealogy_from_dict(missing)

    extra = deepcopy(sample_document)
    extra["characters"][0]["nickname"] = "Rei"
    with pytest.raises(StorageError):
        genealogy_from_dict(extra)


def test_duplicate_character_ids_are_rejected(sample_document: dict) -> None:
    sample_document["characters"].append(deepcopy(sample_document["characters"][0]))
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


@pytest.mark.parametrize("bad_record", [None, 100, [], "invalid"])
def test_relationship_rejects_non_object_record(
    sample_document: dict, bad_record: object
) -> None:
    sample_document["relationships"][0] = bad_record
    with pytest.raises(StorageError, match="relationships"):
        genealogy_from_dict(sample_document)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "invalid"),
        ("id", None),
        ("source_id", "bad-id"),
        ("target_id", 0),
        ("type", "unknown_relationship"),
        ("type", None),
        ("start_year", 1.5),
        ("end_year", False),
    ],
)
def test_relationship_rejects_invalid_field_values(
    sample_document: dict, field: str, value: object
) -> None:
    sample_document["relationships"][0][field] = value
    with pytest.raises(StorageError, match="relationships"):
        genealogy_from_dict(sample_document)


def test_relationship_rejects_missing_and_extra_fields(sample_document: dict) -> None:
    missing = deepcopy(sample_document)
    del missing["relationships"][0]["type"]
    with pytest.raises(StorageError):
        genealogy_from_dict(missing)

    extra = deepcopy(sample_document)
    extra["relationships"][0]["comment"] = "novo"
    with pytest.raises(StorageError):
        genealogy_from_dict(extra)


def test_relationship_rejects_invalid_date_interval(sample_document: dict) -> None:
    entry = sample_document["relationships"][0]
    entry["start_year"] = 100
    entry["end_year"] = 99
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_relationship_rejects_self_connection(sample_document: dict) -> None:
    entry = sample_document["relationships"][0]
    entry["target_id"] = entry["source_id"]
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_relationship_rejects_nonexistent_character(sample_document: dict) -> None:
    sample_document["relationships"][0]["target_id"] = str(uuid4())
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_duplicate_relationship_uuid_is_rejected(sample_document: dict) -> None:
    sample_document["relationships"].append(deepcopy(sample_document["relationships"][0]))
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_duplicate_parentage_with_different_uuid_is_rejected(sample_document: dict) -> None:
    parentage = next(
        item for item in sample_document["relationships"]
        if item["type"] == RelationshipType.BIOLOGICAL_PARENT.value
    )
    duplicate = deepcopy(parentage)
    duplicate["id"] = str(uuid4())
    sample_document["relationships"].append(duplicate)
    with pytest.raises(StorageError):
        genealogy_from_dict(sample_document)


def test_parentage_cycle_is_rejected() -> None:
    a, b, c = (Character(name=name) for name in ("A", "B", "C"))
    document = genealogy_to_dict(Genealogy())
    document["characters"] = [
        {"id": str(x.id), "name": x.name, "surname": None,
         "gender": None, "birth_year": None, "death_year": None,
         "biography": None}
        for x in (a, b, c)
    ]
    document["relationships"] = [
        {"id": str(uuid4()), "source_id": str(first.id),
         "target_id": str(second.id), "type": kind.value,
         "start_year": None, "end_year": None}
        for first, second, kind in (
            (a, b, RelationshipType.BIOLOGICAL_PARENT),
            (b, c, RelationshipType.ADOPTIVE_PARENT),
            (c, a, RelationshipType.BIOLOGICAL_PARENT),
        )
    ]
    with pytest.raises(StorageError):
        genealogy_from_dict(document)


def test_loading_nonexistent_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_genealogy(tmp_path / "missing.json")


@pytest.mark.parametrize("contents", ["", "{", "not json", "[1, 2"])
def test_loading_malformed_json_raises_storage_error(
    tmp_path: Path, contents: str
) -> None:
    path = tmp_path / "broken.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(StorageError):
        load_genealogy(path)


def test_loading_invalid_utf8_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "invalid-utf8.json"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(StorageError):
        load_genealogy(path)


def test_loading_duplicate_json_keys_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-keys.json"
    path.write_text(
        '{"format":"arconte.genealogy",'
        '"format":"arconte.genealogy",'
        '"version":1,"characters":[],"relationships":[]}',
        encoding="utf-8",
    )
    with pytest.raises(StorageError, match="Chave JSON repetida"):
        load_genealogy(path)


def test_loading_valid_json_with_wrong_schema_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "wrong-schema.json"
    path.write_text('[1, 2, 3]', encoding="utf-8")
    with pytest.raises(StorageError):
        load_genealogy(path)


def test_failed_atomic_replace_keeps_previous_file_and_cleans_temp(
    sample_genealogy: Genealogy, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "existing.json"
    original = b"existing data must survive"
    destination.write_bytes(original)

    def simulated_replace_failure(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated os.replace failure")

    monkeypatch.setattr(storage_module.os, "replace", simulated_replace_failure)
    with pytest.raises(OSError, match="simulated"):
        save_genealogy(sample_genealogy, destination)

    assert destination.read_bytes() == original
    assert list(tmp_path.iterdir()) == [destination]


def test_failed_json_write_keeps_previous_file_and_cleans_temp(
    sample_genealogy: Genealogy, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "existing.json"
    original = b"old version"
    destination.write_bytes(original)

    def simulated_dump_failure(_document: object, stream: object, **_kwargs: object) -> None:
        stream.write("partial document")
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(storage_module.json, "dump", simulated_dump_failure)
    with pytest.raises(OSError, match="simulated"):
        save_genealogy(sample_genealogy, destination)

    assert destination.read_bytes() == original
    assert list(tmp_path.iterdir()) == [destination]


# ===========================================================================
# Persistência v2: famílias, afiliações e migração da v1
# ===========================================================================

@pytest.fixture
def sample_project() -> tuple[Genealogy, FamilyRegistry]:
    """Projeto fictício com todas as variantes de família e de afiliação."""
    genealogy = Genealogy()
    arthur = Character(
        name="Árthur", surname="d'Áurea", gender="masculino",
        birth_year=-1300, death_year=-1200,
        biography="Rei de Érion; dragões, magia e ✨",
    )
    elena = Character(name="Elena", birth_year=-1290)
    edric = Character(name="Édric", birth_year=-1250)
    lyra = Character(name="Lyra", biography="Guardiã da floresta 🌳")
    for character in (lyra, edric, elena, arthur):
        genealogy.add_character(character)

    genealogy.add_relationship(Relationship(
        source_id=arthur.id, target_id=edric.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    ))
    genealogy.add_relationship(Relationship(
        source_id=elena.id, target_id=edric.id,
        type=RelationshipType.ADOPTIVE_PARENT,
    ))
    genealogy.add_relationship(Relationship(
        source_id=arthur.id, target_id=elena.id,
        type=RelationshipType.MARRIAGE, start_year=-1280,
    ))
    genealogy.add_relationship(Relationship(
        source_id=edric.id, target_id=lyra.id,
        type=RelationshipType.PARTNERSHIP,
    ))

    registry = FamilyRegistry(genealogy)
    house = Family(
        name="Casa Áurea", type=FamilyType.HOUSE, founder_id=arthur.id,
        founded_year=-1300, dissolved_year=-900,
        motto="Honra, força e 🔥", description="Casa antiga de Érion.",
    )
    clan = Family(name="Clã da Névoa", type=FamilyType.CLAN)
    dynasty = Family(
        name="Dinastia do Sol", type=FamilyType.DYNASTY,
        founder_id=elena.id, founded_year=-1290,
    )
    family = Family(name="Família Campos", type=FamilyType.FAMILY)
    for item in (dynasty, house, family, clan):
        registry.add_family(item)

    memberships = (
        FamilyMembership(
            family_id=house.id, character_id=arthur.id,
            origin=MembershipOrigin.FOUNDATION, start_year=-1300,
            role="Fundador e rei",
        ),
        FamilyMembership(
            family_id=house.id, character_id=edric.id,
            origin=MembershipOrigin.BIRTH, start_year=-1250,
            role="Herdeiro",
        ),
        FamilyMembership(
            family_id=house.id, character_id=elena.id,
            origin=MembershipOrigin.MARRIAGE,
            start_year=-1280, end_year=-1210, role="Rainha",
        ),
        FamilyMembership(
            family_id=clan.id, character_id=edric.id,
            origin=MembershipOrigin.ADOPTION, start_year=-1220,
            role="Guardião",
        ),
        FamilyMembership(
            family_id=dynasty.id, character_id=elena.id,
            origin=MembershipOrigin.FOUNDATION,
        ),
        FamilyMembership(
            family_id=family.id, character_id=lyra.id,
            origin=MembershipOrigin.AFFILIATION,
        ),
        FamilyMembership(
            family_id=house.id, character_id=edric.id,
            origin=MembershipOrigin.AFFILIATION,
            start_year=-1190, end_year=-1100,
            role="Regente",
        ),
    )
    for membership in reversed(memberships):
        registry.add_membership(membership)
    return genealogy, registry


@pytest.fixture
def project_document(sample_project: tuple[Genealogy, FamilyRegistry]) -> dict:
    return project_to_dict(*sample_project)


def test_format_constants() -> None:
    assert FORMAT == "arconte.genealogy"
    assert FORMAT_VERSION == 1
    assert PROJECT_FORMAT_VERSION == 2


def test_empty_project_roundtrip(tmp_path: Path) -> None:
    genealogy = Genealogy()
    registry = FamilyRegistry(genealogy)
    path = tmp_path / "vazio.json"
    save_project(genealogy, registry, path)
    loaded_genealogy, loaded_registry = load_project(path)
    assert project_to_dict(loaded_genealogy, loaded_registry) == {
        "format": FORMAT,
        "version": 2,
        "characters": [],
        "relationships": [],
        "families": [],
        "memberships": [],
    }


def test_v2_file_roundtrip_preserves_everything(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    genealogy, registry = sample_project
    path = tmp_path / "universo.json"
    expected = project_to_dict(genealogy, registry)
    save_project(genealogy, registry, path)
    restored_genealogy, restored_registry = load_project(path)
    assert project_to_dict(restored_genealogy, restored_registry) == expected
    assert restored_genealogy is not genealogy
    assert restored_registry is not registry


def test_v2_dict_roundtrip_is_lossless(project_document: dict) -> None:
    assert project_to_dict(*project_from_dict(project_document)) == project_document


def test_v2_dict_conversion_does_not_change_input(project_document: dict) -> None:
    original = deepcopy(project_document)
    project_from_dict(project_document)
    assert project_document == original


def test_v2_document_is_json_serializable(project_document: dict) -> None:
    assert json.loads(json.dumps(project_document)) == project_document


def test_v2_preserves_uuid_and_attributes(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    original_genealogy, original_registry = sample_project
    restored_genealogy, restored_registry = project_from_dict(
        project_to_dict(original_genealogy, original_registry)
    )
    assert {x.id: x for x in restored_genealogy.get_all_characters()} == {
        x.id: x for x in original_genealogy.get_all_characters()
    }
    assert {x.id: x for x in restored_genealogy.get_relationships()} == {
        x.id: x for x in original_genealogy.get_relationships()
    }
    assert {x.id: x for x in restored_registry.get_all_families()} == {
        x.id: x for x in original_registry.get_all_families()
    }
    assert {x.id: x for x in restored_registry.get_memberships()} == {
        x.id: x for x in original_registry.get_memberships()
    }


def test_all_family_types_survive_roundtrip(project_document: dict) -> None:
    _, registry = project_from_dict(project_document)
    assert {family.type for family in registry.get_all_families()} == set(FamilyType)


def test_all_membership_origins_survive_roundtrip(project_document: dict) -> None:
    _, registry = project_from_dict(project_document)
    assert {item.origin for item in registry.get_memberships()} == set(MembershipOrigin)


def test_family_founders_and_periods_are_preserved(project_document: dict) -> None:
    _, registry = project_from_dict(project_document)
    house = next(f for f in registry.get_all_families() if f.name == "Casa Áurea")
    assert house.founder_id is not None
    assert house.founded_year == -1300
    assert house.dissolved_year == -900
    assert house.motto == "Honra, força e 🔥"
    assert house.description == "Casa antiga de Érion."


def test_memberships_keep_historical_dates(project_document: dict) -> None:
    _, registry = project_from_dict(project_document)
    memberships = registry.get_memberships()
    queen = next(m for m in memberships if m.role == "Rainha")
    assert queen.start_year == -1280
    assert queen.end_year == -1210
    assert queen.is_active_at(-1250)
    assert not queen.is_active_at(-1200)


def test_character_can_belong_to_multiple_families(project_document: dict) -> None:
    genealogy, registry = project_from_dict(project_document)
    edric = next(c for c in genealogy.get_all_characters() if c.name == "Édric")
    assert {f.name for f in registry.get_families_for_character(edric.id)} == {
        "Casa Áurea", "Clã da Névoa"
    }


def test_genealogical_queries_still_work_after_roundtrip(project_document: dict) -> None:
    genealogy, registry = project_from_dict(project_document)
    by_name = {c.name: c for c in genealogy.get_all_characters()}
    assert {p.name for p in genealogy.get_parents(by_name["Édric"].id)} == {
        "Árthur", "Elena"
    }
    assert {p.name for p in genealogy.get_partners(by_name["Árthur"].id)} == {"Elena"}
    assert {c.name for c in registry.get_members(
        next(f.id for f in registry.get_all_families() if f.name == "Casa Áurea")
    )} == {"Árthur", "Elena", "Édric"}


def test_families_do_not_create_parent_child_links(project_document: dict) -> None:
    genealogy, _ = project_from_dict(project_document)
    by_name = {c.name: c for c in genealogy.get_all_characters()}
    assert genealogy.get_parents(by_name["Lyra"].id) == ()


def test_collections_are_sorted_by_uuid(project_document: dict) -> None:
    for name in ("characters", "relationships", "families", "memberships"):
        ids = [item["id"] for item in project_document[name]]
        assert ids == sorted(ids)


def test_serializing_twice_gives_same_document(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    assert project_to_dict(*sample_project) == project_to_dict(*sample_project)


def test_saving_twice_gives_identical_bytes(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path_a = tmp_path / "a.json"
    path_b = tmp_path / "b.json"
    save_project(*sample_project, path_a)
    save_project(*sample_project, path_b)
    assert path_a.read_bytes() == path_b.read_bytes()


def test_utf8_accents_emoji_and_newline(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path = tmp_path / "Érion.json"
    save_project(*sample_project, path)
    text = path.read_text(encoding="utf-8")
    assert "Casa Áurea" in text
    assert "Clã da Névoa" in text
    assert "Érion" in text
    assert "✨" in text
    assert "🔥" in text
    assert text.endswith("\n")


def test_save_project_creates_nested_folders(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path = tmp_path / "livros" / "Érion" / "dinastias.json"
    save_project(*sample_project, path)
    assert path.is_file()
    assert project_to_dict(*load_project(path)) == project_to_dict(*sample_project)


def test_v2_save_and_load_accept_string_paths(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path = str(tmp_path / "universo.json")
    save_project(*sample_project, path)
    assert project_to_dict(*load_project(path)) == project_to_dict(*sample_project)


def test_save_project_overwrites_previous_file(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path = tmp_path / "universo.json"
    path.write_text("old content", encoding="utf-8")
    save_project(*sample_project, path)
    assert project_to_dict(*load_project(path)) == project_to_dict(*sample_project)


def test_v1_genealogy_can_be_loaded_as_v2_project(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    genealogy, _ = sample_project
    path = tmp_path / "legado.json"
    save_genealogy(genealogy, path)
    restored_genealogy, restored_registry = load_project(path)
    assert genealogy_to_dict(restored_genealogy) == genealogy_to_dict(genealogy)
    assert restored_registry.get_all_families() == ()
    assert restored_registry.get_memberships() == ()


def test_v1_dict_can_be_loaded_as_project(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    genealogy, _ = sample_project
    restored_genealogy, restored_registry = project_from_dict(genealogy_to_dict(genealogy))
    assert genealogy_to_dict(restored_genealogy) == genealogy_to_dict(genealogy)
    assert restored_registry.get_memberships() == ()


def test_legacy_api_still_writes_v1(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    genealogy, _ = sample_project
    path = tmp_path / "legado.json"
    save_genealogy(genealogy, path)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 1
    assert genealogy_to_dict(load_genealogy(path)) == genealogy_to_dict(genealogy)


def test_legacy_loader_rejects_v2_to_avoid_losing_families(
    sample_project: tuple[Genealogy, FamilyRegistry], tmp_path: Path,
) -> None:
    path = tmp_path / "versao2.json"
    save_project(*sample_project, path)
    with pytest.raises(StorageError, match="load_project"):
        load_genealogy(path)


def test_legacy_dict_loader_rejects_v2(project_document: dict) -> None:
    with pytest.raises(StorageError, match="project_from_dict"):
        genealogy_from_dict(project_document)


@pytest.mark.parametrize("bad_genealogy", [None, {}, "genealogy", 1])
def test_project_to_dict_requires_genealogy(bad_genealogy: object) -> None:
    genealogy = Genealogy()
    registry = FamilyRegistry(genealogy)
    with pytest.raises(TypeError):
        project_to_dict(bad_genealogy, registry)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_registry", [None, {}, "registry", 42])
def test_project_to_dict_requires_registry(bad_registry: object) -> None:
    with pytest.raises(TypeError):
        project_to_dict(Genealogy(), bad_registry)  # type: ignore[arg-type]


def test_registry_must_reference_same_genealogy(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    _, registry = sample_project
    with pytest.raises(ValueError, match="associado"):
        project_to_dict(Genealogy(), registry)


def test_project_save_rejects_orphaned_founder(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    genealogy, registry = sample_project
    founder_id = next(f.founder_id for f in registry.get_all_families()
                      if f.founder_id is not None)
    registry.remove_character_memberships(founder_id)
    genealogy.remove_character(founder_id)
    with pytest.raises(StorageError, match="inconsistente"):
        project_to_dict(genealogy, registry)


def test_project_save_rejects_orphaned_member(
    sample_project: tuple[Genealogy, FamilyRegistry],
) -> None:
    genealogy, registry = sample_project
    lyra = next(c for c in genealogy.get_all_characters() if c.name == "Lyra")
    genealogy.remove_character(lyra.id)
    with pytest.raises(StorageError, match="inconsistente"):
        project_to_dict(genealogy, registry)


@pytest.mark.parametrize("invalid", [None, [], "text", 17, True])
def test_project_from_dict_rejects_non_object(invalid: object) -> None:
    with pytest.raises(StorageError):
        project_from_dict(invalid)


@pytest.mark.parametrize("version", [0, -1, 4, True, 2.0, "2", None])
def test_project_rejects_unsupported_version(project_document: dict, version: object) -> None:
    project_document["version"] = version
    with pytest.raises(StorageError, match="Versão"):
        project_from_dict(project_document)


@pytest.mark.parametrize("bad_format", [None, "outro.formato", [], 4])
def test_project_rejects_bad_format(project_document: dict, bad_format: object) -> None:
    project_document["format"] = bad_format
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize("missing", [
    "format", "version", "characters", "relationships", "families", "memberships",
])
def test_project_rejects_missing_top_level_field(project_document: dict, missing: str) -> None:
    del project_document[missing]
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_extra_top_level_field(project_document: dict) -> None:
    project_document["unrecognized"] = True
    with pytest.raises(StorageError, match="desconhecidos"):
        project_from_dict(project_document)


@pytest.mark.parametrize("field", ["characters", "relationships", "families", "memberships"])
@pytest.mark.parametrize("wrong", [None, {}, "not a list", 15])
def test_project_rejects_non_list_collections(
    project_document: dict, field: str, wrong: object,
) -> None:
    project_document[field] = wrong
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize("field", ["families", "memberships"])
@pytest.mark.parametrize("invalid", [None, 42, [], "text"])
def test_project_rejects_non_object_records(
    project_document: dict, field: str, invalid: object,
) -> None:
    project_document[field][0] = invalid
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize("field", [
    "id", "name", "type", "founder_id", "founded_year", "dissolved_year",
    "motto", "description",
])
def test_project_rejects_missing_family_field(project_document: dict, field: str) -> None:
    del project_document["families"][0][field]
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_extra_family_field(project_document: dict) -> None:
    project_document["families"][0]["unexpected"] = 42
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize("field", [
    "id", "family_id", "character_id", "origin", "start_year", "end_year", "role",
])
def test_project_rejects_missing_membership_field(project_document: dict, field: str) -> None:
    del project_document["memberships"][0][field]
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_extra_membership_field(project_document: dict) -> None:
    project_document["memberships"][0]["unexpected"] = "x"
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize(("field", "wrong"), [
    ("id", "not-a-uuid"),
    ("id", 5),
    ("name", "   "),
    ("name", None),
    ("type", "not-a-family-type"),
    ("type", None),
    ("founder_id", "not-a-uuid"),
    ("founder_id", 100),
    ("founder_id", str(uuid4())),
    ("founded_year", True),
    ("founded_year", 100.5),
    ("dissolved_year", "100"),
    ("dissolved_year", False),
    ("motto", ["invalid"]),
    ("description", False),
])
def test_project_rejects_invalid_family_values(
    project_document: dict, field: str, wrong: object,
) -> None:
    project_document["families"][0][field] = wrong
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize(("field", "wrong"), [
    ("id", "not-a-uuid"),
    ("id", None),
    ("family_id", "not-a-uuid"),
    ("family_id", str(uuid4())),
    ("character_id", "not-a-uuid"),
    ("character_id", str(uuid4())),
    ("origin", "invented-origin"),
    ("origin", 3),
    ("start_year", 12.5),
    ("start_year", True),
    ("end_year", "1200"),
    ("end_year", False),
    ("role", ["invalid"]),
])
def test_project_rejects_invalid_membership_values(
    project_document: dict, field: str, wrong: object,
) -> None:
    project_document["memberships"][0][field] = wrong
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_family_end_before_start(project_document: dict) -> None:
    item = project_document["families"][0]
    item["founded_year"], item["dissolved_year"] = 100, 99
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_membership_end_before_start(project_document: dict) -> None:
    item = project_document["memberships"][0]
    item["start_year"], item["end_year"] = 100, 99
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_duplicate_family_uuid(project_document: dict) -> None:
    project_document["families"].append(deepcopy(project_document["families"][0]))
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_duplicate_membership_uuid(project_document: dict) -> None:
    project_document["memberships"].append(deepcopy(project_document["memberships"][0]))
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_duplicate_membership_with_different_uuid(
    project_document: dict,
) -> None:
    duplicated = deepcopy(project_document["memberships"][0])
    duplicated["id"] = str(uuid4())
    project_document["memberships"].append(duplicated)
    with pytest.raises(StorageError):
        project_from_dict(project_document)


def test_project_rejects_invalid_genealogical_relation(project_document: dict) -> None:
    project_document["relationships"][0]["source_id"] = str(uuid4())
    with pytest.raises(StorageError):
        project_from_dict(project_document)


@pytest.mark.parametrize("content", ["", "{", "not-json", "[1, 2"])
def test_load_project_rejects_malformed_json(tmp_path: Path, content: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError):
        load_project(path)


def test_load_project_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "invalid-utf8.json"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(StorageError):
        load_project(path)


def test_load_project_rejects_duplicate_json_keys(
    project_document: dict, tmp_path: Path,
) -> None:
    path = tmp_path / "repeated-key.json"
    content = json.dumps(project_document, ensure_ascii=False)
    content = content.replace('"version": 2', '"version": 2, "version": 2', 1)
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError, match="repetida"):
        load_project(path)


def test_load_project_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_project(tmp_path / "does-not-exist.json")


def test_failed_replace_preserves_old_file_and_removes_temporary(
    sample_project: tuple[Genealogy, FamilyRegistry],
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "existing.json"
    original = b"conteudo anterior intacto"
    destination.write_bytes(original)

    def fail_replace(*_args: object, **_kwargs: object) -> None:
        raise OSError("falha simulada na substituicao")

    monkeypatch.setattr(storage_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="falha simulada"):
        save_project(*sample_project, destination)
    assert destination.read_bytes() == original
    assert sorted(tmp_path.iterdir()) == [destination]


def test_failed_json_dump_preserves_old_file_and_removes_temporary(
    sample_project: tuple[Genealogy, FamilyRegistry],
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "existing.json"
    original = b"arquivo original"
    destination.write_bytes(original)

    def fail_dump(_document: object, stream: object, **_kwargs: object) -> None:
        stream.write("escrita parcial")
        raise OSError("falha simulada na gravacao")

    monkeypatch.setattr(storage_module.json, "dump", fail_dump)
    with pytest.raises(OSError, match="falha simulada"):
        save_project(*sample_project, destination)
    assert destination.read_bytes() == original
    assert sorted(tmp_path.iterdir()) == [destination]

# ── Persistência v3 dos perfis modulares do personagem ────────────────────
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory, HistoryEvent
from storage.storage import RICH_PROJECT_FORMAT_VERSION


def test_project_v3_roundtrip_all_profiles(tmp_path):
    from project.project import Project
    p = Project("Sarnília")
    c = Character(
        name="Artuin", surname="Hauck", birth_year=31,
        physical=PhysicalAttributes(
            height_m=1.68, weight_kg=80,
            custom_attributes={"cicatrizes": ["rosto", "braço"]},
        ),
        personality=PersonalityProfile(traits=["Ambicioso", "Manipulador"]),
        social=SocialProfile(title="Conde", residence="Morro do Falcão"),
        history=CharacterHistory(
            biography="Primeiro.\n\nSegundo.",
            events=[HistoryEvent(title="Ascensão", year=67, category="Política")],
        ),
    )
    p.add_character(c)
    file = tmp_path / "sarnilia.json"
    p.save(file)
    contents = json.loads(file.read_text(encoding="utf-8"))
    assert contents["format"] == "arconte.project"
    assert contents["data"]["version"] == RICH_PROJECT_FORMAT_VERSION == 3
    assert contents["data"]["characters"][0]["physical"]["weight_kg"] == 80
    restored = Project.load(file)
    person = restored.get_character(c.id)
    assert person == c
    assert person.id == c.id
    assert person.history.events[0].id == c.history.events[0].id
    assert person.personality.traits == ("Ambicioso", "Manipulador")


def test_project_old_schema_stays_v2_when_profiles_empty():
    from project.project import Project
    p = Project("Antigo")
    p.add_character(Character(name="Artuin", biography="Texto antigo"))
    doc = project_to_dict(p.genealogy, p.families)
    assert doc["version"] == 2
    restored, _ = project_from_dict(doc)
    character = restored.get_all_characters()[0]
    assert character.history.biography == "Texto antigo"


def test_legacy_genealogy_writer_rejects_rich_profiles():
    genealogy = Genealogy()
    genealogy.add_character(Character(name="Artuin", physical=PhysicalAttributes(height_m=1.68)))
    with pytest.raises(StorageError, match="save_project"):
        genealogy_to_dict(genealogy)


@pytest.mark.parametrize("broken", [
    lambda x: x.update({"history": {"biography": "outro"}}),
    lambda x: x.pop("physical"),
    lambda x: x["physical"].update({"altura_inventada": 3}),
])
def test_v3_rejects_corrupted_character_profiles(broken):
    genealogy = Genealogy()
    registry = FamilyRegistry(genealogy)
    genealogy.add_character(Character(name="Artuin", physical=PhysicalAttributes(height_m=1.68)))
    document = project_to_dict(genealogy, registry)
    broken(document["characters"][0])
    with pytest.raises(StorageError):
        project_from_dict(document)


def test_version_three_is_not_accepted_by_legacy_loaders(tmp_path):
    genealogy = Genealogy()
    registry = FamilyRegistry(genealogy)
    genealogy.add_character(Character(name="Artuin", physical=PhysicalAttributes(height_m=1.68)))
    document = project_to_dict(genealogy, registry)
    with pytest.raises(StorageError):
        genealogy_from_dict(document)
    file = tmp_path / "v3.json"
    file.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(StorageError):
        load_genealogy(file)


# ==========================================================================
# Project completo: organizações, religiões, deuses e doutrinas
# (testes adicionais no MESMO test_storage.py, sem fragmentar a suíte).
# ==========================================================================

from project.project import Project
from organization.organization import Organization, OrganizationType
from organization.membership import OrganizationMembership
from religion.religion import Religion, ReligionType
from religion.deity import Deity
from religion.doctrine import Doctrine
from character.physical import PhysicalAttributes
from storage.storage import (
    full_project_to_dict, full_project_from_dict,
    save_full_project, load_full_project,
)


@pytest.fixture
def complete_project() -> Project:
    project = Project("Sarnília")
    manohar = Character(
        name="Manohar", surname="Hauck", birth_year=12,
        physical=PhysicalAttributes(height_m=1.78),
        biography="Sumo-sacerdote de Mezena.",
    )
    project.add_character(manohar)
    order = Organization(
        name="Ordem de Mezena", type=OrganizationType.RELIGIOUS_ORDER,
        founder_id=manohar.id, founded_year=20,
        custom_attributes={"hierarquia": ["sumo-sacerdote", "sacerdotes"]},
    )
    project.add_organization(order)
    project.add_organization_membership(OrganizationMembership(
        organization_id=order.id, character_id=manohar.id,
        role="Sumo-sacerdote", start_year=40,
    ))
    faith = Religion(
        name="Fé de Mezena", type=ReligionType.POLYTHEISTIC,
        founder_id=manohar.id, founded_year=20,
    )
    project.add_religion(faith)
    divinity = Deity(name="Mezena", domains=("Sabedoria",))
    project.add_deity(divinity)
    project.link_deity(faith.id, divinity.id)
    project.add_doctrine(Doctrine(
        religion_id=faith.id, title="O Juramento",
        content="Guardar o conhecimento dos antigos.",
        start_year=30,
    ))
    return project


def test_full_storage_serializes_project_envelope_v2(complete_project):
    document = full_project_to_dict(complete_project)
    assert document == complete_project.to_dict()
    assert document["format"] == "arconte.project"
    assert document["version"] == 2
    assert document["data"]["version"] == 3
    assert len(document["organizations"]["organizations"]) == 1
    assert len(document["organizations"]["memberships"]) == 1
    assert len(document["religions"]["religions"]) == 1
    assert len(document["religions"]["deities"]) == 1
    assert len(document["religions"]["doctrines"]) == 1
    assert len(document["religions"]["religion_deities"]) == 1


def test_full_storage_roundtrip_persists_all_references(complete_project, tmp_path):
    path = tmp_path / "sarnília e mezena.json"
    save_full_project(complete_project, path)
    restored = load_full_project(path)
    assert restored.to_dict() == complete_project.to_dict()
    person = complete_project.get_all_characters()[0]
    organization = complete_project.get_all_organizations()[0]
    religion = complete_project.get_all_religions()[0]
    assert restored.get_character(person.id).physical.height_m == 1.78
    assert restored.organizations.get_members(organization.id)[0].id == person.id
    assert restored.get_organization_memberships()[0].role == "Sumo-sacerdote"
    assert restored.get_deities(religion.id)[0].name == "Mezena"
    assert restored.get_doctrines()[0].title == "O Juramento"
    assert restored.id == complete_project.id


def test_full_storage_roundtrip_in_memory_is_independent(complete_project):
    restored = full_project_from_dict(full_project_to_dict(complete_project))
    assert restored.to_dict() == complete_project.to_dict()
    organization_id = complete_project.get_all_organizations()[0].id
    restored.remove_organization(organization_id)
    assert complete_project.get_organization(organization_id).name == "Ordem de Mezena"
    assert restored.to_dict() != complete_project.to_dict()


def test_full_storage_empty_project_remains_version_one(tmp_path):
    project = Project("Novo projeto")
    path = tmp_path / "novo.json"
    save_full_project(project, path)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["version"] == 1
    assert "organizations" not in document
    assert "religions" not in document
    assert load_full_project(path).to_dict() == document


def test_full_storage_legacy_genealogy_is_importable(sample_project, tmp_path):
    path = tmp_path / "sarnilia_legada.json"
    genealogy, families = sample_project
    save_project(genealogy, families, path)
    imported = load_full_project(path)
    assert imported.name == "sarnilia_legada"
    assert imported.get_all_characters() == genealogy.get_all_characters()
    assert imported.get_all_families() == families.get_all_families()
    assert imported.get_all_organizations() == ()
    assert imported.get_all_religions() == ()


def test_full_storage_rejects_wrong_type_without_creating_file(tmp_path):
    path = tmp_path / "must-not-exist.json"
    with pytest.raises(TypeError, match="Project"):
        save_full_project({}, path)
    assert not path.exists()
    with pytest.raises(TypeError, match="Project"):
        full_project_to_dict(None)


@pytest.mark.parametrize("bad_version", [0, 3, -1, True, "2", None])
def test_full_storage_rejects_unknown_project_version(complete_project, bad_version):
    document = full_project_to_dict(complete_project)
    document["version"] = bad_version
    with pytest.raises(StorageError, match="Versão"):
        full_project_from_dict(document)


def test_full_storage_rejects_orphan_member(complete_project):
    document = full_project_to_dict(complete_project)
    document["organizations"]["memberships"][0]["character_id"] = str(uuid4())
    with pytest.raises(StorageError, match="institucionais"):
        full_project_from_dict(document)


def test_full_storage_rejects_orphan_religion_founder(complete_project):
    document = full_project_to_dict(complete_project)
    document["religions"]["religions"][0]["founder_id"] = str(uuid4())
    with pytest.raises(StorageError, match="institucionais"):
        full_project_from_dict(document)


def test_full_storage_rejects_malformed_religion_registry(complete_project):
    document = full_project_to_dict(complete_project)
    document["religions"].pop("religion_deities")
    with pytest.raises(StorageError, match="institucionais"):
        full_project_from_dict(document)


def test_full_storage_rejects_repeated_json_key(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"format": "arconte.project", "format": "arconte.project"}', encoding="utf-8")
    with pytest.raises(StorageError, match="repetida"):
        load_full_project(path)


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_full_storage_rejects_nonstandard_json_numbers(tmp_path, token):
    path = tmp_path / "numbers.json"
    path.write_text('{"bad": ' + token + '}', encoding="utf-8")
    with pytest.raises(StorageError, match="não finito"):
        load_full_project(path)


def test_genealogy_readers_also_reject_nonstandard_json_numbers(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text('{"bad": NaN}', encoding="utf-8")
    with pytest.raises(StorageError, match="não finito"):
        load_project(path)
    with pytest.raises(StorageError, match="não finito"):
        load_genealogy(path)


def test_full_storage_preserves_existing_file_if_new_data_invalid(tmp_path):
    project = Project("Sarnília")
    path = tmp_path / "safe.json"
    save_full_project(project, path)
    original_bytes = path.read_bytes()
    project.add_religion(Religion(name="Fé do Bosque"))
    project.religions._religions[next(iter(project.religions._religions))] = Religion(
        name="Fé inválida", founder_id=uuid4(),
        id=next(iter(project.religions._religions)),
    )
    with pytest.raises(KeyError):
        save_full_project(project, path)
    assert path.read_bytes() == original_bytes


def test_full_storage_output_equals_project_native_save(complete_project, tmp_path):
    a = tmp_path / "from_storage.json"
    b = tmp_path / "from_project.json"
    save_full_project(complete_project, a)
    complete_project.save(b)
    assert a.read_bytes() == b.read_bytes()


def test_full_storage_still_rejects_institutional_document_via_genealogy_loader(
    complete_project, tmp_path,
):
    path = tmp_path / "project.json"
    save_full_project(complete_project, path)
    with pytest.raises(StorageError):
        load_project(path)
    with pytest.raises(StorageError):
        load_genealogy(path)
