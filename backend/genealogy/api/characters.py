"""Rotas HTTP de consulta, criação e edição dos personagens do Arconte.

Execute a API a partir de ``backend/genealogy``::

    python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

POST/PATCH delegam as validações ao Editor e salvam o Project completo.
Os GETs e a genealogia HTML continuam sendo somente de leitura.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, StrictInt

from character.character import Character
from character.history import CharacterHistory
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from editor.editor import Editor
from project.project import Project
from storage.storage import StorageError

from fastapi.responses import HTMLResponse
from tree.tree import TreeBuilder, layout_tree
from viewer.viewer import ViewerOptions, render_html

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/characters", tags=["Personagens"])


class CharacterSummary(BaseModel):
    """Dados suficientes para os cartões/lista de personagens no Flutter."""

    id: UUID
    name: str
    surname: str | None
    full_name: str
    gender: str | None
    birth_year: int | None
    death_year: int | None
    title: str | None


class CharacterDetail(CharacterSummary):
    """Ficha completa, preservando os quatro blocos do domínio."""

    biography: str | None
    physical: dict[str, Any]
    personality: dict[str, Any]
    social: dict[str, Any]
    history: dict[str, Any]



class CharacterWrite(BaseModel):
    """Campos opcionais para PATCH; POST requer name explicitamente.

    Campos ausentes no PATCH são preservados. ``null`` limpa campos
    opcionais. Perfis aceitam atualizações parciais por chave.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    surname: str | None = None
    gender: str | None = None
    birth_year: StrictInt | None = None
    death_year: StrictInt | None = None
    biography: str | None = None
    physical: dict[str, Any] | None = None
    personality: dict[str, Any] | None = None
    social: dict[str, Any] | None = None
    history: dict[str, Any] | None = None


def _invalid(message: str) -> HTTPException:
    return HTTPException(status_code=422, detail=message)


def _parse_profiles(
    changes: dict[str, Any], *, current: Character | None = None,
) -> dict[str, Any]:
    """Converte objetos JSON em perfis do domínio, sem apagar chaves omitidas."""
    for field_name, profile_type in (
        ("physical", PhysicalAttributes),
        ("personality", PersonalityProfile),
        ("social", SocialProfile),
        ("history", CharacterHistory),
    ):
        if field_name not in changes:
            continue
        delta = changes[field_name]
        if delta is None:
            raise _invalid(f"{field_name} deve ser um objeto JSON, não null.")
        original = getattr(current, field_name).to_dict() if current else {}
        original.update(delta)
        changes[field_name] = profile_type.from_dict(original)

    # Exigir coerência se as duas representações da biografia vierem juntas.
    if "history" in changes and "biography" in changes:
        biography = changes["biography"]
        normalized = biography.strip() or None if isinstance(biography, str) else biography
        if normalized != changes["history"].biography:
            raise _invalid("biography e history.biography devem coincidir.")
    return changes


def _detail(person: Character) -> CharacterDetail:
    return CharacterDetail(
        **_summary(person).model_dump(),
        biography=person.history.biography,
        physical=person.physical.to_dict(),
        personality=person.personality.to_dict(),
        social=person.social.to_dict(),
        history=person.history.to_dict(),
    )


def _save_project(project: Project, request: Request) -> None:
    """Project.save valida e substitui o JSON de forma atômica."""
    try:
        project.save(request.app.state.project_file)
    except (OSError, ValueError, TypeError, StorageError) as exc:
        logger.exception("Falha ao salvar o projeto do Arconte")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível salvar o projeto JSON.",
        ) from exc


def _get_project(request: Request) -> Project:
    """Lê o JSON atual a cada requisição, inclusive após edição no terminal.

    Não cria nem modifica arquivos. A gravação atômica do Project permite
    compartilhar o projeto com o editor de terminal durante o desenvolvimento.
    """
    project_file: Path = request.app.state.project_file
    try:
        return Project.load(project_file)
    except FileNotFoundError as exc:
        logger.warning("Arquivo do projeto Arconte não encontrado: %s", project_file)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Projeto não encontrado. Salve um projeto JSON e confira ARCONTE_PROJECT_FILE.",
        ) from exc
    except (OSError, StorageError, ValueError, TypeError) as exc:
        logger.exception("Falha ao ler o projeto Arconte: %s", project_file)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível carregar o projeto JSON do Arconte.",
        ) from exc


def _summary(person: Character) -> CharacterSummary:
    return CharacterSummary(
        id=person.id,
        name=person.name,
        surname=person.surname,
        full_name=person.full_name,
        gender=person.gender,
        birth_year=person.birth_year,
        death_year=person.death_year,
        title=person.social.title,
    )


@router.get("", response_model=list[CharacterSummary], summary="Listar personagens")
def list_characters(project: Project = Depends(_get_project)) -> list[CharacterSummary]:
    """Retorna os personagens em ordem alfabética, sem inventar idades."""
    people = sorted(
        project.get_all_characters(),
        key=lambda person: (person.full_name.casefold(), str(person.id)),
    )
    return [_summary(person) for person in people]


@router.get("/{character_id}", response_model=CharacterDetail, summary="Ver ficha completa")
def get_character(
    character_id: UUID,
    project: Project = Depends(_get_project),
) -> CharacterDetail:
    """Consulta um personagem por UUID (404 se não existir; 422 se malformado)."""
    try:
        person = project.get_character(character_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado neste projeto.",
        ) from exc

    return _detail(person)


@router.get(
    "/{character_id}/genealogy",
    response_class=HTMLResponse,
    summary="Explorar a genealogia de um personagem (HTML)",
)
def get_character_genealogy(
    character_id: UUID,
    project: Project = Depends(_get_project),
) -> HTMLResponse:
    try:
        person = project.get_character(character_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Personagem não encontrado neste projeto.",
        ) from exc

    graph = TreeBuilder(project).build(
        root_id=person.id,
        direction="all",
        include_partners=True,
    )

    layout = layout_tree(graph)

    html = render_html(
        layout,
        options=ViewerOptions(
            title=f"Genealogia de {person.full_name}",
        ),
        project=project,
    )

    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )




@router.post(
    "", response_model=CharacterDetail, status_code=status.HTTP_201_CREATED,
    summary="Criar personagem",
)
def create_character(
    payload: CharacterWrite,
    request: Request,
    project: Project = Depends(_get_project),
) -> CharacterDetail:
    """Cria personagem via Editor, preservando genealogia e outros módulos."""
    changes = payload.model_dump(exclude_unset=True)
    if not isinstance(changes.get("name"), str) or not changes["name"].strip():
        raise _invalid("name é obrigatório e não pode estar vazio.")
    try:
        _parse_profiles(changes)
        editor = Editor(project, dirty=False)
        person = editor.create_character(changes.pop("name"), **changes)
    except (TypeError, ValueError, KeyError) as exc:
        raise _invalid(str(exc)) from exc
    _save_project(project, request)
    return _detail(person)


@router.patch(
    "/{character_id}", response_model=CharacterDetail,
    summary="Editar personagem sem descartar os campos omitidos",
)
def update_character(
    character_id: UUID,
    payload: CharacterWrite,
    request: Request,
    project: Project = Depends(_get_project),
) -> CharacterDetail:
    """Edição parcial mantendo UUID, genealogia e histórico não modificado."""
    try:
        current = project.get_character(character_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado neste projeto.",
        ) from exc

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return _detail(current)
    if "name" in changes and (
        not isinstance(changes["name"], str) or not changes["name"].strip()
    ):
        raise _invalid("name não pode ser vazio.")
    try:
        _parse_profiles(changes, current=current)
        editor = Editor(project, dirty=False)
        updated = editor.update_character(character_id, **changes)
    except (TypeError, ValueError, KeyError) as exc:
        raise _invalid(str(exc)) from exc

    if updated != current:
        _save_project(project, request)
    return _detail(updated)


__all__ = ["router", "CharacterSummary", "CharacterDetail", "CharacterWrite"]
