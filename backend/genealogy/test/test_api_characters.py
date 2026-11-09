"""Testes HTTP da API de personagens e visualizador de genealogia.

Executar de backend/genealogy::

    python3 -m pytest test/test_api_characters.py -q

Não exige iniciar o Uvicorn ou abrir o navegador.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from character.character import Character
from project.project import Project
from relationship.relationship import Relationship, RelationshipType


@pytest.fixture
def sample(tmp_path: Path):
    file = tmp_path / 'project.json'
    project = Project(name='Sarnília')
    boros = Character(name='Boros', surname='Hauck', birth_year=2)
    artuin = Character(name='Artuin', surname='Hauck', birth_year=31)
    ayla = Character(name='Ayla', surname='ÓFiachra', birth_year=32)
    isolated = Character(name='Pessoa isolada')
    for person in (boros, artuin, ayla, isolated):
        project.add_character(person)
    project.add_relationship(Relationship(
        source_id=boros.id, target_id=artuin.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    ))
    project.add_relationship(Relationship(
        source_id=artuin.id, target_id=ayla.id,
        type=RelationshipType.MARRIAGE,
    ))
    project.save(file)
    return TestClient(create_app(project_file=file)), file, project, boros, artuin, ayla, isolated


def parse_graph(html: str):
    match = re.search(
        r'<script id="arconte-data" type="application/json">(.*?)</script>',
        html, re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_genealogy_is_rendered_as_interactive_html(sample):
    client, _, _, _, artuin, _, _ = sample
    response = client.get(f'/api/characters/{artuin.id}/genealogy')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/html')
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert 'Genealogia de Artuin Hauck' in response.text
    assert 'id="arconte-svg"' in response.text
    assert 'id="zoom-in"' in response.text
    assert 'id="search"' in response.text


def test_genealogy_uses_requested_person_as_root(sample):
    client, _, _, boros, artuin, ayla, isolated = sample
    graph = parse_graph(client.get(f'/api/characters/{artuin.id}/genealogy').text)
    assert graph['root_id'] == str(artuin.id)
    assert graph['direction'] == 'all'
    assert {item['id'] for item in graph['nodes']} == {
        str(boros.id), str(artuin.id), str(ayla.id),
    }
    assert str(isolated.id) not in {item['id'] for item in graph['nodes']}
    assert len(graph['edges']) == 2


def test_genealogy_for_isolated_person(sample):
    client, _, _, _, _, _, isolated = sample
    response = client.get(f'/api/characters/{isolated.id}/genealogy')
    assert response.status_code == 200
    graph = parse_graph(response.text)
    assert graph['root_id'] == str(isolated.id)
    assert len(graph['nodes']) == 1
    assert graph['edges'] == []


def test_genealogy_returns_404_for_missing_character(sample):
    client, _, _, _, _, _, _ = sample
    response = client.get(f'/api/characters/{uuid4()}/genealogy')
    assert response.status_code == 404
    assert 'não encontrado' in response.json()['detail']


@pytest.mark.parametrize('bad_id', ['not-a-uuid', '123', '...', 'x' * 50])
def test_genealogy_returns_422_for_invalid_uuid(sample, bad_id):
    client, _, _, _, _, _, _ = sample
    assert client.get(f'/api/characters/{bad_id}/genealogy').status_code == 422


def test_genealogy_returns_503_for_missing_project(tmp_path):
    client = TestClient(create_app(project_file=tmp_path / 'missing.json'))
    response = client.get(f'/api/characters/{uuid4()}/genealogy')
    assert response.status_code == 503


def test_genealogy_does_not_write_project_file(sample):
    client, file, _, _, artuin, _, _ = sample
    before = file.read_bytes()
    assert client.get(f'/api/characters/{artuin.id}/genealogy').status_code == 200
    assert file.read_bytes() == before


def test_api_still_provides_summary_and_details(sample):
    client, _, _, _, artuin, _, _ = sample
    assert client.get('/health').json() == {'status': 'ok'}
    summaries = client.get('/api/characters')
    assert summaries.status_code == 200
    assert len(summaries.json()) == 4
    detail = client.get(f'/api/characters/{artuin.id}')
    assert detail.status_code == 200
    assert detail.json()['full_name'] == 'Artuin Hauck'
    for key in ('physical', 'personality', 'social', 'history'):
        assert isinstance(detail.json()[key], dict)


def test_api_docs_declares_genealogy_endpoint(sample):
    client, _, _, _, _, _, _ = sample
    spec = client.get('/openapi.json').json()
    route = spec['paths']['/api/characters/{character_id}/genealogy']['get']
    assert 'text/html' in route['responses']['200']['content']


def test_genealogy_endpoint_reflects_project_changes(sample):
    client, file, project, _, artuin, _, _ = sample
    response = client.get(f'/api/characters/{artuin.id}/genealogy')
    assert 'Maeve' not in response.text
    maeve = Character(name='Maeve')
    project.add_character(maeve)
    project.add_relationship(Relationship(
        source_id=artuin.id, target_id=maeve.id,
        type=RelationshipType.BIOLOGICAL_PARENT,
    ))
    project.save(file)
    graph = parse_graph(client.get(f'/api/characters/{artuin.id}/genealogy').text)
    assert str(maeve.id) in {node['id'] for node in graph['nodes']}


def test_genealogy_cors_supports_flutter_local_origin(sample):
    client, _, _, _, artuin, _, _ = sample
    response = client.get(
        f'/api/characters/{artuin.id}/genealogy',
        headers={'Origin': 'http://localhost:8080'},
    )
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:8080'

# ---------------------------------------------------------------------------
# Criação e edição: a API deve preservar todo o documento Arconte.
# ---------------------------------------------------------------------------

def test_post_creates_full_character_and_persists(sample):
    client, file, _, _, _, _, _ = sample
    body = {
        'name': 'Eilidh', 'surname': 'ÓCuillan', 'birth_year': 6,
        'death_year': 48, 'biography': 'Uma história longa.\nOutro parágrafo.',
        'physical': {'height_m': 1.72, 'hair_color': 'Ruivo'},
        'personality': {'traits': ['Perspicaz', 'Gentil']},
        'social': {'title': 'Senhora', 'residence': 'Morro do Falcão'},
    }
    response = client.post('/api/characters', json=body)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['full_name'] == 'Eilidh ÓCuillan'
    assert data['history']['biography'] == body['biography']
    assert data['physical']['height_m'] == 1.72
    assert data['personality']['traits'] == ['Perspicaz', 'Gentil']
    assert data['social']['title'] == 'Senhora'
    assert Project.load(file).get_character(__import__('uuid').UUID(data['id'])).full_name == data['full_name']
    assert client.get(f"/api/characters/{data['id']}").json() == data


def test_patch_changes_only_requested_fields_and_preserves_links(sample):
    client, file, _, boros, artuin, ayla, _ = sample
    before = Project.load(file)
    links = tuple(before.get_relationships())
    response = client.patch(f'/api/characters/{artuin.id}', json={
        'surname': 'Hauck de Sarnília',
        'physical': {'height_m': 1.8, 'custom_attributes': {'cicatriz': True}},
        'social': {'title': 'Conde da Sarnília'},
    })
    assert response.status_code == 200, response.text
    assert response.json()['id'] == str(artuin.id)
    restored = Project.load(file)
    assert restored.get_character(artuin.id).surname == 'Hauck de Sarnília'
    assert restored.get_character(artuin.id).physical.height_m == 1.8
    assert restored.get_character(artuin.id).physical.to_dict()['custom_attributes']['cicatriz']
    assert restored.get_character(artuin.id).social.title == 'Conde da Sarnília'
    assert tuple(restored.get_relationships()) == links
    assert restored.get_character(boros.id) == boros
    assert restored.get_character(ayla.id) == ayla


def test_patch_biography_retains_existing_events_and_custom_attributes(sample):
    from character.history import CharacterHistory, HistoryEvent
    from dataclasses import replace
    client, file, _, _, artuin, _, _ = sample
    project = Project.load(file)
    event = HistoryEvent(title='Ascensão', year=45)
    project.update_character(replace(
        artuin,
        biography='Texto antigo',
        history=CharacterHistory(biography='Texto antigo', events=(event,),
                                 custom_attributes={'idioma': 'norte'}),
    ))
    project.save(file)
    response = client.patch(f'/api/characters/{artuin.id}', json={'biography': 'Texto novo'})
    assert response.status_code == 200, response.text
    history = response.json()['history']
    assert history['biography'] == 'Texto novo'
    assert history['events'][0]['id'] == str(event.id)
    assert history['custom_attributes'] == {'idioma': 'norte'}
    assert Project.load(file).get_character(artuin.id).history.events[0].id == event.id


@pytest.mark.parametrize('body', [
    {}, {'name': ''}, {'name': '   '},
    {'name': 'Alguém', 'birth_year': True},
    {'name': 'Alguém', 'birth_year': 44, 'death_year': 10},
    {'name': 'Alguém', 'physical': {'height_m': -1}},
    {'name': 'Alguém', 'physical': {'evil_field': 'x'}},
    {'name': 'Alguém', 'history': None},
    {'name': 'Alguém', 'unexpected_field': 'x'},
    {'name': 'Alguém', 'biography': 'A', 'history': {'biography': 'B'}},
])
def test_post_invalid_does_not_touch_json(sample, body):
    client, file, *_ = sample
    contents = file.read_bytes()
    response = client.post('/api/characters', json=body)
    assert response.status_code == 422, response.text
    assert file.read_bytes() == contents


@pytest.mark.parametrize('body', [
    {'name': None}, {'birth_year': 30, 'death_year': 20},
    {'social': {'unknown': 1}}, {'personality': {'traits': [None]}},
    {'physical': None}, {'history': {'events': 'not-an-array'}},
    {'biography': 'Texto', 'history': {'biography': 'Texto diferente'}},
    {'id': str(uuid4())},
])
def test_patch_invalid_does_not_touch_json(sample, body):
    client, file, _, _, artuin, _, _ = sample
    contents = file.read_bytes()
    response = client.patch(f'/api/characters/{artuin.id}', json=body)
    assert response.status_code == 422, response.text
    assert file.read_bytes() == contents


def test_patch_missing_person_is_404_and_does_not_create_one(sample):
    client, file, *_ = sample
    original = file.read_bytes()
    assert client.patch(f'/api/characters/{uuid4()}', json={'name':'Fantasma'}).status_code == 404
    assert file.read_bytes() == original


def test_post_then_patch_roundtrip_preserves_history_events(sample):
    client, file, *_ = sample
    created = client.post('/api/characters', json={
        'name': 'Ilías',
        'history': {'biography': 'Conselheiro', 'events': [
            {'title':'Retorno', 'year': 58, 'description': 'Voltou ao castelo'}]},
    })
    assert created.status_code == 201, created.text
    data = created.json()
    event_id = data['history']['events'][0]['id']
    edited = client.patch(f"/api/characters/{data['id']}", json={
        'social': {'occupation': 'Conselheiro'}, 'history': {'biography': 'Sábio conselheiro'}
    })
    assert edited.status_code == 200, edited.text
    assert edited.json()['history']['events'][0]['id'] == event_id
    assert edited.json()['biography'] == 'Sábio conselheiro'
    assert len(Project.load(file).get_all_characters()) == 5


def test_cors_preflight_for_write_methods(sample):
    client, *_ = sample
    for method in ('POST', 'PATCH'):
        response = client.options('/api/characters', headers={
            'Origin': 'http://localhost:8080',
            'Access-Control-Request-Method': method,
            'Access-Control-Request-Headers': 'content-type',
        })
        assert response.status_code == 200, response.text
        assert response.headers['access-control-allow-origin'] == 'http://localhost:8080'


def test_write_routes_in_api_docs(sample):
    client, *_ = sample
    spec = client.get('/openapi.json').json()
    assert 'post' in spec['paths']['/api/characters']
    assert 'patch' in spec['paths']['/api/characters/{character_id}']


def test_patch_empty_document_is_noop_without_write(sample):
    client, file, _, _, artuin, _, _ = sample
    before = file.read_bytes()
    response = client.patch(f"/api/characters/{artuin.id}", json={})
    assert response.status_code == 200
    assert file.read_bytes() == before


def test_failed_validation_does_not_remove_other_project_data(sample):
    client, file, _, _, artuin, _, _ = sample
    before = Project.load(file)
    original_relations = before.get_relationships()
    response = client.patch(
        f"/api/characters/{artuin.id}",
        json={"physical": {"height_m": -5}},
    )
    assert response.status_code == 422
    assert Project.load(file).get_relationships() == original_relations


def test_rejects_foreign_origin_for_write_preflight(sample):
    client, *_ = sample
    response = client.options('/api/characters', headers={
        'Origin': 'https://example.com',
        'Access-Control-Request-Method': 'POST',
    })
    assert response.headers.get('access-control-allow-origin') is None


def test_write_preserves_families_organizations_religions(sample):
    """Uma edição de personagem não pode descartar outros registros do códice."""
    from family.family import Family, FamilyType
    from organization.organization import Organization
    from religion.religion import Religion

    client, file, _, _, artuin, _, _ = sample
    before = Project.load(file)
    house = Family(name='Casa Hauck', type=FamilyType.HOUSE, founder_id=artuin.id)
    guild = Organization(name='Ordem do Falcão', founder_id=artuin.id)
    faith = Religion(name='Crença antiga', founder_id=artuin.id)
    before.add_family(house)
    before.add_organization(guild)
    before.add_religion(faith)
    before.save(file)

    assert client.patch(f'/api/characters/{artuin.id}', json={
        'social': {'title': 'Conde de Sarnília'},
    }).status_code == 200
    created = client.post('/api/characters', json={'name': 'Novo personagem'})
    assert created.status_code == 201, created.text

    restored = Project.load(file)
    assert restored.get_family(house.id) == house
    assert restored.get_organization(guild.id) == guild
    assert restored.get_religion(faith.id) == faith
    assert restored.get_character(artuin.id).social.title == 'Conde de Sarnília'
