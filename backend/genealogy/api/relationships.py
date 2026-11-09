"""Rotas HTTP para consultar, criar e remover vínculos familiares do Arconte.

Toda validação genealógica permanece no domínio (Editor/Project/Genealogy).
As rotas de escrita salvam o documento completo por substituição atômica.

Para ativar as rotas, registre ``router`` em ``api/main.py``.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, StrictInt

from api.characters import _get_project, _save_project
from editor.editor import Editor
from project.project import Project
from relationship.relationship import Relationship, RelationshipType


router = APIRouter(prefix="/api", tags=["Relacionamentos"])


class RelationshipCreate(BaseModel):
    """Dados para criar uma relação; UUIDs apontam para personagens existentes."""

    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    target_id: UUID
    type: RelationshipType
    start_year: StrictInt | None = None
    end_year: StrictInt | None = None


class RelationshipDetail(BaseModel):
    """Relação com os nomes de ambos os personagens para a interface Flutter."""

    id: UUID
    source_id: UUID
    target_id: UUID
    source_name: str
    target_name: str
    type: RelationshipType
    is_directed: bool
    start_year: int | None
    end_year: int | None


def _detail(relation: Relationship, project: Project) -> RelationshipDetail:
    return RelationshipDetail(
        id=relation.id,
        source_id=relation.source_id,
        target_id=relation.target_id,
        source_name=project.get_character(relation.source_id).full_name,
        target_name=project.get_character(relation.target_id).full_name,
        type=relation.type,
        is_directed=relation.is_directed,
        start_year=relation.start_year,
        end_year=relation.end_year,
    )


@router.get(
    "/characters/{character_id}/relationships",
    response_model=list[RelationshipDetail],
    summary="Listar vínculos familiares de um personagem",
)
def list_character_relationships(
    character_id: UUID,
    project: Project = Depends(_get_project),
) -> list[RelationshipDetail]:
    try:
        project.get_character(character_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado neste projeto.",
        ) from exc

    relationships = project.genealogy.get_relationships(character_id=character_id)
    return [_detail(relation, project) for relation in relationships]


@router.post(
    "/relationships",
    response_model=RelationshipDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Criar vínculo familiar",
)
def create_relationship(
    payload: RelationshipCreate,
    request: Request,
    project: Project = Depends(_get_project),
) -> RelationshipDetail:
    editor = Editor(project, dirty=False)
    try:
        relation = editor.create_relationship(
            source_id=payload.source_id,
            target_id=payload.target_id,
            type=payload.type,
            start_year=payload.start_year,
            end_year=payload.end_year,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um dos personagens informados não existe neste projeto.",
        ) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    _save_project(project, request)
    return _detail(relation, project)


@router.delete(
    "/relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover vínculo familiar sem excluir os personagens",
)
def delete_relationship(
    relationship_id: UUID,
    request: Request,
    project: Project = Depends(_get_project),
) -> Response:
    editor = Editor(project, dirty=False)
    try:
        editor.remove_relationship(relationship_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relacionamento não encontrado neste projeto.",
        ) from exc

    _save_project(project, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router", "RelationshipCreate", "RelationshipDetail"]
