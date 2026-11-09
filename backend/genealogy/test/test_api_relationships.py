"""Testes HTTP isolados da API de vínculos familiares do Arconte.

Executar a partir de ``backend/genealogy``::

    python -m pytest test/test_api_relationships.py -q

Os testes criam um mundo fictício em ``tmp_path``; nunca leem ou alteram
``data/sarnilia.json``. Não precisam do Uvicorn.

Nesta etapa, o roteador de relacionamentos é adicionado apenas à aplicação
*de teste*. O registro definitivo em ``api/main.py`` será validado depois,
quando esse arquivo for atualizado para incluir o novo roteador e o DELETE
no CORS do Flutter Web.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from character.character import Character
from project.project import Project
from relationship.relationship import Relationship, RelationshipType


@dataclass(frozen=True)
class Scenario:
    client: TestClient
    file: Path
    boros: Character
    artuin: Character
    ayla: Character
    mira: Character
    parent: Relationship
    marriage: Relationship


def _test_client(project_file: Path) -> TestClient:
    """Cria uma aplicação de teste com o roteador já registrado em main.py."""
    return TestClient(create_app(project_file=project_file))


@pytest.fixture
def scenario(tmp_path: Path) -> Scenario:
    """Cria e salva dados independentes para cada teste."""
    file = tmp_path / "mundo_teste.json"
    project = Project(name="Sarnília - projeto isolado de testes")
    boros = Character(name="Boros", surname="Hauck", birth_year=2)
    artuin = Character(name="Artuin", surname="Hauck", birth_year=31)
    ayla = Character(name="Ayla", surname="ÓFiachra", birth_year=32)
    mira = Character(name="Mira", surname="do Vale", birth_year=55)
    for person in (boros, artuin, ayla, mira):
        project.add_character(person)

    parent = Relationship(
        source_id=boros.id,
        target_id=artuin.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    )
    marriage = Relationship(
        source_id=artuin.id,
        target_id=ayla.id,
        type=RelationshipType.MARRIAGE,
        start_year=51,
    )
    project.add_relationship(parent)
    project.add_relationship(marriage)
    project.save(file)

    client = _test_client(file)
    return Scenario(client, file, boros, artuin, ayla, mira, parent, marriage)


def payload(
    source: UUID,
    target: UUID,
    kind: str = "biological_parent",
    **dates: int | None,
) -> dict[str, object]:
    return {
        "source_id": str(source),
        "target_id": str(target),
        "type": kind,
        **dates,
    }


def stored(scenario: Scenario) -> Project:
    return Project.load(scenario.file)


def test_get_relationships_returns_ids_types_names_and_direction(scenario: Scenario) -> None:
    response = scenario.client.get(f"/api/characters/{scenario.artuin.id}/relationships")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    by_id = {item["id"]: item for item in data}
    parent = by_id[str(scenario.parent.id)]
    marriage = by_id[str(scenario.marriage.id)]
    assert parent == {
        "id": str(scenario.parent.id),
        "source_id": str(scenario.boros.id),
        "target_id": str(scenario.artuin.id),
        "source_name": "Boros Hauck",
        "target_name": "Artuin Hauck",
        "type": "biological_parent",
        "is_directed": True,
        "start_year": None,
        "end_year": None,
    }
    assert marriage["type"] == "marriage"
    assert marriage["is_directed"] is False
    assert marriage["start_year"] == 51
    assert {marriage["source_name"], marriage["target_name"]} == {
        "Artuin Hauck", "Ayla ÓFiachra",
    }


def test_get_relationships_for_both_marriage_participants(scenario: Scenario) -> None:
    for character_id in (scenario.artuin.id, scenario.ayla.id):
        response = scenario.client.get(f"/api/characters/{character_id}/relationships")
        assert response.status_code == 200
        assert str(scenario.marriage.id) in {item["id"] for item in response.json()}


def test_get_relationships_for_person_without_links(scenario: Scenario) -> None:
    response = scenario.client.get(f"/api/characters/{scenario.mira.id}/relationships")
    assert response.status_code == 200
    assert response.json() == []


def test_get_does_not_modify_project_file(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    scenario.client.get(f"/api/characters/{scenario.artuin.id}/relationships")
    assert scenario.file.read_bytes() == before


def test_get_unknown_character_returns_404(scenario: Scenario) -> None:
    assert scenario.client.get(f"/api/characters/{uuid4()}/relationships").status_code == 404


@pytest.mark.parametrize("bad_id", ["abc", "123", "not-a-uuid"])
def test_get_invalid_character_uuid_returns_422(scenario: Scenario, bad_id: str) -> None:
    assert scenario.client.get(f"/api/characters/{bad_id}/relationships").status_code == 422


def test_post_biological_parent_creates_and_persists(scenario: Scenario) -> None:
    original = stored(scenario)
    old_links = {relation.id for relation in original.get_relationships()}
    old_project_id = original.id

    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.artuin.id, scenario.mira.id, "biological_parent"),
    )
    assert response.status_code == 201, response.text
    data = response.json()
    created_id = UUID(data["id"])
    assert created_id not in old_links
    assert data["source_id"] == str(scenario.artuin.id)
    assert data["target_id"] == str(scenario.mira.id)
    assert data["type"] == "biological_parent"
    assert data["is_directed"] is True
    assert data["source_name"] == "Artuin Hauck"
    assert data["target_name"] == "Mira do Vale"

    reopened = stored(scenario)
    assert reopened.id == old_project_id
    assert old_links < {relation.id for relation in reopened.get_relationships()}
    assert reopened.get_relationship(created_id).target_id == scenario.mira.id
    assert reopened.genealogy.get_parents(scenario.mira.id) == (scenario.artuin,)
    assert len(reopened.get_all_characters()) == 4
    assert {r["id"] for r in scenario.client.get(
        f"/api/characters/{scenario.mira.id}/relationships"
    ).json()} == {str(created_id)}


def test_post_adoptive_parent_preserves_an_existing_biological_link(scenario: Scenario) -> None:
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.boros.id, scenario.artuin.id, "adoptive_parent"),
    )
    assert response.status_code == 201, response.text
    assert response.json()["type"] == "adoptive_parent"
    reopened = stored(scenario)
    direct = reopened.genealogy.get_relationships(character_id=scenario.boros.id)
    assert {r.type for r in direct} == {
        RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT,
    }
    assert reopened.genealogy.get_children(scenario.boros.id) == (scenario.artuin,)


@pytest.mark.parametrize("kind", ["marriage", "partnership"])
def test_post_union_is_symmetric_and_canonical(scenario: Scenario, kind: str) -> None:
    # O casamento existente é Artuin–Ayla; aqui usamos Boros–Mira.
    response = scenario.client.post(
        "/api/relationships", json=payload(
            scenario.mira.id, scenario.boros.id, kind,
            start_year=63, end_year=67,
        ),
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["type"] == kind
    assert data["is_directed"] is False
    assert data["start_year"] == 63
    assert data["end_year"] == 67
    assert UUID(data["source_id"]).int < UUID(data["target_id"]).int
    assert {data["source_id"], data["target_id"]} == {
        str(scenario.boros.id), str(scenario.mira.id),
    }
    assert scenario.mira in stored(scenario).genealogy.get_partners(scenario.boros.id)


def test_post_allows_another_union_with_different_dates(scenario: Scenario) -> None:
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.artuin.id, scenario.ayla.id, "marriage", start_year=61),
    )
    assert response.status_code == 201, response.text
    assert len([
        rel for rel in stored(scenario).get_relationships()
        if rel.type is RelationshipType.MARRIAGE
    ]) == 2


def test_post_rejects_duplicate_without_writing(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.boros.id, scenario.artuin.id),
    )
    assert response.status_code == 422
    assert "cadastrada" in str(response.json()["detail"])
    assert scenario.file.read_bytes() == before


def test_post_rejects_reverse_duplicate_marriage(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.ayla.id, scenario.artuin.id, "marriage", start_year=51),
    )
    assert response.status_code == 422
    assert scenario.file.read_bytes() == before


def test_post_rejects_self_relationship(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.artuin.id, scenario.artuin.id, "partnership"),
    )
    assert response.status_code == 422
    assert scenario.file.read_bytes() == before


def test_post_rejects_genealogical_cycle(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    # Já existe Boros -> Artuin, então Artuin -> Boros formaria ciclo.
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.artuin.id, scenario.boros.id),
    )
    assert response.status_code == 422
    assert "ciclo" in str(response.json()["detail"])
    assert scenario.file.read_bytes() == before


@pytest.mark.parametrize("missing_side", ["source", "target"])
def test_post_unknown_character_returns_404_without_writing(
    scenario: Scenario, missing_side: str,
) -> None:
    before = scenario.file.read_bytes()
    source = uuid4() if missing_side == "source" else scenario.boros.id
    target = uuid4() if missing_side == "target" else scenario.mira.id
    response = scenario.client.post("/api/relationships", json=payload(source, target))
    assert response.status_code == 404
    assert scenario.file.read_bytes() == before


@pytest.mark.parametrize("changes", [
    {"type": "sibling"},
    {"type": "invalid"},
    {"start_year": 70, "end_year": 60},
    {"start_year": True},
    {"start_year": 14.3},
    {"end_year": "67"},
    {"extra": "não permitido"},
    {"source_id": "invalid-uuid"},
    {"target_id": "invalid-uuid"},
    {"type": None},
])
def test_post_invalid_payload_returns_422_without_writing(
    scenario: Scenario, changes: dict[str, object],
) -> None:
    before = scenario.file.read_bytes()
    body = payload(scenario.boros.id, scenario.mira.id)
    body.update(changes)
    response = scenario.client.post("/api/relationships", json=body)
    assert response.status_code == 422, response.text
    assert scenario.file.read_bytes() == before


@pytest.mark.parametrize("missing_field", ["source_id", "target_id", "type"])
def test_post_missing_required_field_returns_422(
    scenario: Scenario, missing_field: str,
) -> None:
    before = scenario.file.read_bytes()
    body = payload(scenario.boros.id, scenario.mira.id)
    body.pop(missing_field)
    assert scenario.client.post("/api/relationships", json=body).status_code == 422
    assert scenario.file.read_bytes() == before


def test_delete_removes_only_selected_relationship_and_persists(scenario: Scenario) -> None:
    before = stored(scenario)
    old_characters = before.get_all_characters()
    old_marriage = before.get_relationship(scenario.marriage.id)
    response = scenario.client.delete(f"/api/relationships/{scenario.parent.id}")
    assert response.status_code == 204, response.text
    assert response.content == b""

    reopened = stored(scenario)
    assert reopened.get_all_characters() == old_characters
    assert reopened.get_relationship(scenario.marriage.id) == old_marriage
    assert reopened.genealogy.get_parents(scenario.artuin.id) == ()
    assert {r.id for r in reopened.get_relationships()} == {scenario.marriage.id}
    assert {r["id"] for r in scenario.client.get(
        f"/api/characters/{scenario.artuin.id}/relationships"
    ).json()} == {str(scenario.marriage.id)}


def test_delete_one_of_two_parent_types_keeps_the_other(scenario: Scenario) -> None:
    created = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.boros.id, scenario.artuin.id, "adoptive_parent"),
    )
    assert created.status_code == 201
    response = scenario.client.delete(f"/api/relationships/{scenario.parent.id}")
    assert response.status_code == 204
    reopened = stored(scenario)
    assert reopened.genealogy.get_parents(scenario.artuin.id) == (scenario.boros,)
    assert reopened.get_relationship(UUID(created.json()["id"])).type is RelationshipType.ADOPTIVE_PARENT


def test_delete_unknown_relationship_returns_404_without_writing(scenario: Scenario) -> None:
    before = scenario.file.read_bytes()
    assert scenario.client.delete(f"/api/relationships/{uuid4()}").status_code == 404
    assert scenario.file.read_bytes() == before


def test_delete_twice_returns_404_on_second_attempt(scenario: Scenario) -> None:
    endpoint = f"/api/relationships/{scenario.parent.id}"
    assert scenario.client.delete(endpoint).status_code == 204
    before = scenario.file.read_bytes()
    assert scenario.client.delete(endpoint).status_code == 404
    assert scenario.file.read_bytes() == before


@pytest.mark.parametrize("bad_id", ["abc", "123", "not-a-uuid"])
def test_delete_invalid_uuid_returns_422(scenario: Scenario, bad_id: str) -> None:
    before = scenario.file.read_bytes()
    assert scenario.client.delete(f"/api/relationships/{bad_id}").status_code == 422
    assert scenario.file.read_bytes() == before


def test_missing_project_returns_503(tmp_path: Path) -> None:
    client = _test_client(tmp_path / "inexistente.json")
    response = client.get(f"/api/characters/{uuid4()}/relationships")
    assert response.status_code == 503
    response = client.post(
        "/api/relationships",
        json=payload(uuid4(), uuid4()),
    )
    assert response.status_code == 503
    response = client.delete(f"/api/relationships/{uuid4()}")
    assert response.status_code == 503


def test_post_save_error_returns_503_and_preserves_file(
    scenario: Scenario, monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = scenario.file.read_bytes()

    def failing_save(self: Project, path: Path) -> None:
        raise OSError("Falha simulada de gravação")

    monkeypatch.setattr(Project, "save", failing_save)
    response = scenario.client.post(
        "/api/relationships",
        json=payload(scenario.artuin.id, scenario.mira.id),
    )
    assert response.status_code == 503
    assert scenario.file.read_bytes() == before


def test_openapi_documents_get_post_delete(scenario: Scenario) -> None:
    spec = scenario.client.get("/openapi.json").json()
    assert "get" in spec["paths"]["/api/characters/{character_id}/relationships"]
    assert "post" in spec["paths"]["/api/relationships"]
    assert "delete" in spec["paths"]["/api/relationships/{relationship_id}"]
    assert spec["paths"]["/api/relationships"]["post"]["responses"].get("201")
