"""Rotas HTTP de leitura dos personagens do Arconte.

Execute a API a partir de ``backend/genealogy``::

    python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

Estas rotas são apenas de consulta. Todas as validações e a persistência
continuam no domínio Python (``Project`` e seus componentes).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from character.character import Character
from project.project import Project
from storage.storage import StorageError

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

    return CharacterDetail(
        **_summary(person).model_dump(),
        biography=person.history.biography,
        physical=person.physical.to_dict(),
        personality=person.personality.to_dict(),
        social=person.social.to_dict(),
        history=person.history.to_dict(),
    )


__all__ = ["router", "CharacterSummary", "CharacterDetail"]
