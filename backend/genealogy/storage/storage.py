"""Persistência JSON do Arconte, compatível com genealogias v1, v2 e v3.

O formato v1 registra personagens e parentescos. O formato v2 inclui também
famílias (casas, clãs, dinastias) e afiliações históricas. O formato v3
preserva também as fichas física, psicológica, social e histórica dos personagens.

A API original ``save_genealogy`` / ``load_genealogy`` continua gravando e
lendo **v1**, para evitar alterar contratos de código e testes existentes.
Use ``save_project`` / ``load_project`` para genealogias com famílias **v2/v3**.
Use ``save_full_project`` / ``load_full_project`` para a entidade Project,
incluindo organizações, seus membros, religiões, divindades e doutrinas.
O formato completo é arconte.project v1 (sem instituições) ou v2 (com elas).
A v3 é selecionada apenas quando há perfis enriquecidos. Os projetos antigos
continuam legíveis e um arquivo v2 permanece v2 se não contiver fichas novas.
A API legada v1 rejeita gravações que perderiam essas fichas.

    save_project(genealogy, registry, "data/eldoria.json")
    restored_genealogy, restored_registry = load_project("data/eldoria.json")

``load_project`` também lê documentos v1, criando um FamilyRegistry vazio.
``load_genealogy`` rejeita v2/v3 explicitamente, para não descartar afiliações
silenciosamente. Todas as gravações são atômicas no nível do arquivo.

Os modelos, as estruturas de famílias e a lógica de parentesco permanecem
independentes da persistência e da interface gráfica.
"""

from __future__ import annotations

import json
import os
import tempfile
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import UUID

from character.character import Character
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory
from family.family import (
    Family, FamilyMembership, FamilyRegistry, FamilyType, MembershipOrigin,
)
from genealogy.genealogy import Genealogy
from relationship.relationship import Relationship, RelationshipType

if TYPE_CHECKING:
    from project.project import Project


FORMAT = "arconte.genealogy"
FORMAT_VERSION = 1  # versão legada usada pela API save/load_genealogy
PROJECT_FORMAT_VERSION = 2  # versão com famílias e afiliações
RICH_PROJECT_FORMAT_VERSION = 3  # versão com os quatro perfis completos

_CHARACTER_FIELDS = frozenset(
    {"id", "name", "surname", "gender", "birth_year", "death_year", "biography"}
)
_RICH_CHARACTER_FIELDS = _CHARACTER_FIELDS | frozenset(
    {"physical", "personality", "social", "history"}
)
_RELATIONSHIP_FIELDS = frozenset(
    {"id", "source_id", "target_id", "type", "start_year", "end_year"}
)
_DOCUMENT_FIELDS = frozenset({"format", "version", "characters", "relationships"})
_PROJECT_FIELDS = _DOCUMENT_FIELDS | frozenset({"families", "memberships"})
_FAMILY_FIELDS = frozenset({
    "id", "name", "type", "founder_id", "founded_year", "dissolved_year",
    "motto", "description",
})
_MEMBERSHIP_FIELDS = frozenset({
    "id", "family_id", "character_id", "origin", "start_year", "end_year", "role",
})


class StorageError(ValueError):
    """O arquivo não representa uma genealogia válida ou suportada."""


def _check_fields(value: Any, expected: frozenset[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise StorageError(f"{where} deve ser um objeto JSON.")

    missing = expected - value.keys()
    extra = value.keys() - expected
    if missing:
        raise StorageError(f"{where}: campos ausentes: {', '.join(sorted(missing))}.")
    if extra:
        raise StorageError(f"{where}: campos desconhecidos: {', '.join(sorted(extra))}.")
    return value


def _uuid_from_json(value: Any, where: str) -> UUID:
    if not isinstance(value, str):
        raise StorageError(f"{where} deve ser uma string UUID.")
    try:
        return UUID(value)
    except ValueError as exc:
        raise StorageError(f"{where} contém um UUID inválido: {value!r}.") from exc


def _character_to_json(character: Character) -> dict[str, Any]:
    return {
        "id": str(character.id),
        "name": character.name,
        "surname": character.surname,
        "gender": character.gender,
        "birth_year": character.birth_year,
        "death_year": character.death_year,
        "biography": character.biography,
    }


def _rich_character(character: Character) -> bool:
    return (
        character.physical != PhysicalAttributes()
        or character.personality != PersonalityProfile()
        or character.social != SocialProfile()
        or character.history != CharacterHistory(biography=character.biography)
    )


def _rich_character_to_json(character: Character) -> dict[str, Any]:
    record = _character_to_json(character)
    record.update({
        "physical": character.physical.to_dict(),
        "personality": character.personality.to_dict(),
        "social": character.social.to_dict(),
        "history": character.history.to_dict(),
    })
    return record


def _relationship_to_json(relationship: Relationship) -> dict[str, Any]:
    return {
        "id": str(relationship.id),
        "source_id": str(relationship.source_id),
        "target_id": str(relationship.target_id),
        "type": relationship.type.value,
        "start_year": relationship.start_year,
        "end_year": relationship.end_year,
    }


def _genealogy_to_dict(genealogy: Genealogy, *, enriched: bool = False) -> dict[str, Any]:
    """Converte a genealogia em um documento JSON serializável.

    Utiliza somente a API pública de Genealogy. A ordem estável dos IDs
    facilita comparar versões do arquivo e revisar alterações.
    """
    if not isinstance(genealogy, Genealogy):
        raise TypeError("genealogy deve ser um objeto Genealogy.")

    characters = sorted(genealogy.get_all_characters(), key=lambda item: str(item.id))
    relationships = sorted(genealogy.get_relationships(), key=lambda item: str(item.id))

    return {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "characters": [
            _rich_character_to_json(item) if enriched else _character_to_json(item)
            for item in characters
        ],
        "relationships": [_relationship_to_json(item) for item in relationships],
    }


def genealogy_to_dict(genealogy: Genealogy) -> dict[str, Any]:
    """Exporta v1 apenas se os dados couberem nesse formato sem perdas."""
    if not isinstance(genealogy, Genealogy):
        raise TypeError("genealogy deve ser um objeto Genealogy.")
    if any(_rich_character(c) for c in genealogy.get_all_characters()):
        raise StorageError(
            "A genealogia possui perfis físicos, sociais ou históricos; "
            "use save_project() para preservar esses dados no formato v3."
        )
    return _genealogy_to_dict(genealogy)


def _character_from_json(value: Any, index: int, *, enriched: bool = False) -> Character:
    where = f"characters[{index}]"
    record = _check_fields(
        value, _RICH_CHARACTER_FIELDS if enriched else _CHARACTER_FIELDS, where
    )
    try:
        profiles = {}
        if enriched:
            profiles = {
                "physical": PhysicalAttributes.from_dict(record["physical"]),
                "personality": PersonalityProfile.from_dict(record["personality"]),
                "social": SocialProfile.from_dict(record["social"]),
                "history": CharacterHistory.from_dict(record["history"]),
            }
            if record["biography"] != profiles["history"].biography:
                raise ValueError("biography e history.biography são incompatíveis.")
        return Character(
            id=_uuid_from_json(record["id"], f"{where}.id"),
            name=record["name"],
            surname=record["surname"],
            gender=record["gender"],
            birth_year=record["birth_year"],
            death_year=record["death_year"],
            biography=record["biography"],
            **profiles,
        )
    except (TypeError, ValueError) as exc:
        raise StorageError(f"{where}: {exc}") from exc


def _relationship_from_json(value: Any, index: int) -> Relationship:
    where = f"relationships[{index}]"
    record = _check_fields(value, _RELATIONSHIP_FIELDS, where)

    raw_type = record["type"]
    if not isinstance(raw_type, str):
        raise StorageError(f"{where}.type deve ser uma string.")
    try:
        relationship_type = RelationshipType(raw_type)
    except ValueError as exc:
        raise StorageError(f"{where}.type desconhecido: {raw_type!r}.") from exc

    try:
        return Relationship(
            id=_uuid_from_json(record["id"], f"{where}.id"),
            source_id=_uuid_from_json(record["source_id"], f"{where}.source_id"),
            target_id=_uuid_from_json(record["target_id"], f"{where}.target_id"),
            type=relationship_type,
            start_year=record["start_year"],
            end_year=record["end_year"],
        )
    except (TypeError, ValueError) as exc:
        raise StorageError(f"{where}: {exc}") from exc


def genealogy_from_dict(document: Any, *, _enriched: bool = False) -> Genealogy:
    """Reconstrói uma Genealogy validando os dados e suas relações.

    Cada relação é inserida por ``Genealogy.add_relationship``. Por isso,
    arquivos com personagens ausentes, duplicações ou ciclos de filiação
    são rejeitados em vez de produzir um estado interno inconsistente.
    """
    if (isinstance(document, dict) and
            document.get("version") in (PROJECT_FORMAT_VERSION, RICH_PROJECT_FORMAT_VERSION)
            and not _enriched):
        raise StorageError(
            "O documento contém dados de projeto. Use project_from_dict() "
            "para restaurar tudo sem perda."
        )
    doc = _check_fields(document, _DOCUMENT_FIELDS, "Documento")
    if doc["format"] != FORMAT:
        raise StorageError("Arquivo não pertence ao formato Arconte Genealogy.")
    expected_version = RICH_PROJECT_FORMAT_VERSION if _enriched else FORMAT_VERSION
    if type(doc["version"]) is not int or doc["version"] != expected_version:
        raise StorageError(
            f"Versão de arquivo não suportada: {doc['version']!r}. "
            f"Esta versão do programa aceita apenas {FORMAT_VERSION}."
        )
    if not isinstance(doc["characters"], list):
        raise StorageError("characters deve ser uma lista.")
    if not isinstance(doc["relationships"], list):
        raise StorageError("relationships deve ser uma lista.")

    genealogy = Genealogy()
    for index, item in enumerate(doc["characters"]):
        character = _character_from_json(item, index, enriched=_enriched)
        try:
            genealogy.add_character(character)
        except (TypeError, ValueError) as exc:
            raise StorageError(f"characters[{index}]: {exc}") from exc

    for index, item in enumerate(doc["relationships"]):
        relationship = _relationship_from_json(item, index)
        try:
            genealogy.add_relationship(relationship)
        except (TypeError, ValueError, KeyError) as exc:
            raise StorageError(f"relationships[{index}]: {exc}") from exc

    return genealogy


def _family_to_json(family: Family) -> dict[str, Any]:
    return {
        "id": str(family.id),
        "name": family.name,
        "type": family.type.value,
        "founder_id": str(family.founder_id) if family.founder_id is not None else None,
        "founded_year": family.founded_year,
        "dissolved_year": family.dissolved_year,
        "motto": family.motto,
        "description": family.description,
    }


def _membership_to_json(membership: FamilyMembership) -> dict[str, Any]:
    return {
        "id": str(membership.id),
        "family_id": str(membership.family_id),
        "character_id": str(membership.character_id),
        "origin": membership.origin.value,
        "start_year": membership.start_year,
        "end_year": membership.end_year,
        "role": membership.role,
    }


def _family_from_json(value: Any, index: int) -> Family:
    where = f"families[{index}]"
    record = _check_fields(value, _FAMILY_FIELDS, where)
    family_type = record["type"]
    if type(family_type) is not str:
        raise StorageError(f"{where}.type deve ser uma string.")
    try:
        family_type_enum = FamilyType(family_type)
    except ValueError as exc:
        raise StorageError(f"{where}.type desconhecido: {family_type!r}.") from exc
    founder = record["founder_id"]
    try:
        return Family(
            id=_uuid_from_json(record["id"], f"{where}.id"),
            name=record["name"],
            type=family_type_enum,
            founder_id=(
                _uuid_from_json(founder, f"{where}.founder_id")
                if founder is not None else None
            ),
            founded_year=record["founded_year"],
            dissolved_year=record["dissolved_year"],
            motto=record["motto"],
            description=record["description"],
        )
    except (TypeError, ValueError) as exc:
        raise StorageError(f"{where}: {exc}") from exc


def _membership_from_json(value: Any, index: int) -> FamilyMembership:
    where = f"memberships[{index}]"
    record = _check_fields(value, _MEMBERSHIP_FIELDS, where)
    origin = record["origin"]
    if type(origin) is not str:
        raise StorageError(f"{where}.origin deve ser uma string.")
    try:
        membership_origin = MembershipOrigin(origin)
    except ValueError as exc:
        raise StorageError(f"{where}.origin desconhecido: {origin!r}.") from exc
    try:
        return FamilyMembership(
            id=_uuid_from_json(record["id"], f"{where}.id"),
            family_id=_uuid_from_json(record["family_id"], f"{where}.family_id"),
            character_id=_uuid_from_json(record["character_id"], f"{where}.character_id"),
            origin=membership_origin,
            start_year=record["start_year"],
            end_year=record["end_year"],
            role=record["role"],
        )
    except (TypeError, ValueError) as exc:
        raise StorageError(f"{where}: {exc}") from exc


def project_to_dict(genealogy: Genealogy, registry: FamilyRegistry) -> dict[str, Any]:
    """Gera o documento v2/v3 completo, com ordenação estável por UUID.

    ``registry`` precisa gerenciar a própria instância ``genealogy``.
    Integridade familiar é verificada antes de produzir o documento.
    """
    if not isinstance(genealogy, Genealogy):
        raise TypeError("genealogy deve ser um objeto Genealogy.")
    if not isinstance(registry, FamilyRegistry):
        raise TypeError("registry deve ser um FamilyRegistry.")
    # A API pública do FamilyRegistry ainda não expõe genealogy; a verificação
    # evita misturar personagens de dois projetos diferentes.
    if registry._genealogy is not genealogy:
        raise ValueError("registry deve estar associado à genealogy informada.")
    try:
        registry.validate_integrity()
    except ValueError as exc:
        raise StorageError(f"O registro familiar está inconsistente: {exc}") from exc

    enriched = any(_rich_character(c) for c in genealogy.get_all_characters())
    document = _genealogy_to_dict(genealogy, enriched=enriched)
    document["version"] = RICH_PROJECT_FORMAT_VERSION if enriched else PROJECT_FORMAT_VERSION
    document["families"] = [
        _family_to_json(family)
        for family in sorted(registry.get_all_families(), key=lambda family: str(family.id))
    ]
    document["memberships"] = [
        _membership_to_json(membership)
        for membership in sorted(registry.get_memberships(), key=lambda m: str(m.id))
    ]
    return document


def project_from_dict(document: Any) -> tuple[Genealogy, FamilyRegistry]:
    """Restaura genealogia, famílias e perfis dos documentos v1, v2 ou v3.

    O carregamento valida estritamente o formato e usa as operações públicas
    do domínio, evitando referências órfãs e afiliações duplicadas.
    """
    if not isinstance(document, dict):
        raise StorageError("Documento deve ser um objeto JSON.")
    if document.get("format") != FORMAT:
        raise StorageError("Arquivo não pertence ao formato Arconte Genealogy.")
    version = document.get("version")
    if type(version) is not int or version not in (
        FORMAT_VERSION, PROJECT_FORMAT_VERSION, RICH_PROJECT_FORMAT_VERSION
    ):
        raise StorageError(f"Versão de arquivo não suportada: {version!r}.")

    if version == FORMAT_VERSION:
        genealogy = genealogy_from_dict(document)
        return genealogy, FamilyRegistry(genealogy)

    doc = _check_fields(document, _PROJECT_FIELDS, "Documento")
    if not isinstance(doc["families"], list):
        raise StorageError("families deve ser uma lista.")
    if not isinstance(doc["memberships"], list):
        raise StorageError("memberships deve ser uma lista.")

    # As validações legadas reconstroem toda a genealogia antes das afiliações.
    genealogy_document = {key: doc[key] for key in _DOCUMENT_FIELDS}
    enriched = version == RICH_PROJECT_FORMAT_VERSION
    genealogy_document["version"] = version if enriched else FORMAT_VERSION
    genealogy = genealogy_from_dict(genealogy_document, _enriched=enriched)
    registry = FamilyRegistry(genealogy)

    for index, item in enumerate(doc["families"]):
        family = _family_from_json(item, index)
        try:
            registry.add_family(family)
        except (TypeError, ValueError, KeyError) as exc:
            raise StorageError(f"families[{index}]: {exc}") from exc

    for index, item in enumerate(doc["memberships"]):
        membership = _membership_from_json(item, index)
        try:
            registry.add_membership(membership)
        except (TypeError, ValueError, KeyError) as exc:
            raise StorageError(f"memberships[{index}]: {exc}") from exc

    try:
        registry.validate_integrity()
    except ValueError as exc:
        raise StorageError(f"Documento possui afiliações inconsistentes: {exc}") from exc
    return genealogy, registry


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Evita a perda silenciosa de dados em objetos com chaves repetidas."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StorageError(f"Chave JSON repetida: {key!r}.")
        result[key] = value
    return result


def _write_json_document(document: dict[str, Any], path: str | PathLike[str]) -> None:
    """Grava o JSON em UTF-8 de modo atômico usando arquivo temporário."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(document, temporary_file, indent=2, ensure_ascii=False, allow_nan=False)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _reject_nonfinite(token: str) -> None:
    """Impede extensões não padronizadas do JSON (NaN e Infinity)."""
    raise StorageError(f"Número JSON não finito: {token}.")


def _read_json_document(path: str | PathLike[str]) -> Any:
    """Lê JSON estrito; rejeita codificação, chaves duplicadas e NaN/Infinity."""
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as stream:
            return json.load(
                stream,
                object_pairs_hook=_reject_duplicate_json_keys,
                parse_constant=_reject_nonfinite,
            )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise StorageError(f"Arquivo JSON inválido: {exc}") from exc


def save_genealogy(genealogy: Genealogy, path: str | PathLike[str]) -> None:
    """API legada: salva somente personagens e relações no formato v1.

    Use ``save_project`` para preservar famílias e perfis (v2/v3).
    """
    _write_json_document(genealogy_to_dict(genealogy), path)


def load_genealogy(path: str | PathLike[str]) -> Genealogy:
    """API legada: carrega somente arquivos v1.

    Rejeita arquivos v2 para impedir perda silenciosa de dados de família.
    """
    document = _read_json_document(path)
    if (isinstance(document, dict) and document.get("version") in
            (PROJECT_FORMAT_VERSION, RICH_PROJECT_FORMAT_VERSION)):
        raise StorageError(
            "Arquivo de projeto v2/v3 contém dados adicionais. Use load_project() "
            "para restaurar genealogia e famílias sem perda de informações."
        )
    return genealogy_from_dict(document)


def save_project(
    genealogy: Genealogy, registry: FamilyRegistry, path: str | PathLike[str],
) -> None:
    """Salva o núcleo genealógico nos formatos v2/v3 (sem instituições)."""
    _write_json_document(project_to_dict(genealogy, registry), path)


def load_project(path: str | PathLike[str]) -> tuple[Genealogy, FamilyRegistry]:
    """Carrega documento genealógico v1/v2/v3; v1 cria FamilyRegistry vazio."""
    return project_from_dict(_read_json_document(path))


# ---------------------------------------------------------------------------
# Project completo: arconte.project v1/v2
# ---------------------------------------------------------------------------
# A API genealógica acima continua intacta. O envelope completo (identidade do
# projeto, organizações e religiões) é validado pelo domínio Project. Importação
# local evita dependência circular: Project já importa as APIs genealógicas deste
# módulo e fornece as validações de referências cruzadas.


def full_project_to_dict(project: "Project") -> dict[str, Any]:
    """Serializa o projeto completo, sem omitir organizações ou religiões.

    Produz arconte.project v1 quando não há instituições, e v2 quando há.
    """
    from project.project import Project

    if not isinstance(project, Project):
        raise TypeError("project deve ser um objeto Project.")
    return project.to_dict()


def full_project_from_dict(
    document: Any, *, legacy_name: str = "Projeto importado",
) -> "Project":
    """Restaura Project completo, inclusive documentos genealógicos legados."""
    from project.project import Project

    return Project.from_dict(document, legacy_name=legacy_name)


def save_full_project(project: "Project", path: str | PathLike[str]) -> None:
    """Grava todo o Project em JSON UTF-8 de modo atômico e sem perdas."""
    _write_json_document(full_project_to_dict(project), path)


def load_full_project(path: str | PathLike[str]) -> "Project":
    """Carrega Project v1/v2 ou importa um documento genealógico v1/v2/v3."""
    source = Path(path)
    return full_project_from_dict(
        _read_json_document(source), legacy_name=source.stem,
    )


__all__ = [
    "FORMAT", "FORMAT_VERSION", "PROJECT_FORMAT_VERSION", "RICH_PROJECT_FORMAT_VERSION", "StorageError",
    "genealogy_to_dict", "genealogy_from_dict", "save_genealogy", "load_genealogy",
    "project_to_dict", "project_from_dict", "save_project", "load_project",
    "full_project_to_dict", "full_project_from_dict",
    "save_full_project", "load_full_project",
]
