"""Projeto de escrita do Arconte: ponto de entrada do domínio genealógico.

Compatível com Python 3.10+. Nenhuma dependência externa.

Um Project agrega Genealogy, FamilyRegistry, OrganizationRegistry e ReligionRegistry.
A genealogia permanece independente das afiliações institucionais e crenças.

Formato de salvamento próprio (arconte.project, versão 1 ou 2):
    {"format": "arconte.project", "version": 1,
     "metadata": {"id": "...", "name": "...", "description": null},
     "data": { ... documento arconte.genealogy v2 ... }}

A versão 1 do projeto permanece idêntica quando os registros novos estão vazios.
A versão 2 adiciona, no envelope, os campos "organizations" e "religions".
Arquivos legados arconte.genealogy v1/v2/v3 podem ser importados via Project.load.
Para arquivos legados, o nome é derivado do arquivo e um novo UUID é criado,
porque esses campos não existiam no formato antigo.

Exemplo, executando na pasta backend/genealogy::

    from project.project import Project
    from character.character import Character
    from family.family import Family, FamilyType

    project = Project(name="Eldoria")
    arthur = Character(name="Arthur")
    project.add_character(arthur)
    project.add_family(Family(name="Valerian", type=FamilyType.HOUSE,
                              founder_id=arthur.id))
    project.save("data/eldoria.json")
    restored = Project.load("data/eldoria.json")

Observação: ``genealogy`` e ``families`` são objetos mutáveis expostos para
consultas avançadas. Para manter a consistência, altere dados por meio dos
métodos de Project, especialmente ao excluir personagens. A exclusão é feita
em uma cópia validada, que substitui os componentes somente após o sucesso;
por isso, referências previamente guardadas para project.genealogy ou
project.families devem ser obtidas novamente depois de remove_character().
"""

from __future__ import annotations

from dataclasses import replace
import json
import os
from os import PathLike
from pathlib import Path
import tempfile
from typing import Any
from uuid import UUID, uuid4

from character.character import Character
from family.family import Family, FamilyMembership, FamilyRegistry
from genealogy.genealogy import Genealogy
from organization.organization import Organization
from organization.membership import OrganizationMembership
from organization.registry import OrganizationRegistry
from religion.religion import Religion
from religion.deity import Deity
from religion.doctrine import Doctrine
from religion.registry import ReligionRegistry
from relationship.relationship import Relationship
from storage.storage import (
    FORMAT as GENEALOGY_FORMAT,
    StorageError,
    project_from_dict,
    project_to_dict,
)

PROJECT_FORMAT = "arconte.project"
PROJECT_VERSION = 1  # formato original, preservado para documentos sem instituições
EXTENDED_PROJECT_VERSION = 2  # armazena organizações, afiliações, religiões e crenças
_PROJECT_KEYS = frozenset({"format", "version", "metadata", "data"})
_EXTENDED_PROJECT_KEYS = _PROJECT_KEYS | frozenset({"organizations", "religions"})
_METADATA_KEYS = frozenset({"id", "name", "description"})
_FOUNDER_POLICIES = frozenset({"reject", "clear"})


def _required_name(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("name deve ser uma string.")
    value = value.strip()
    if not value:
        raise ValueError("name não pode estar vazio.")
    return value


def _optional_description(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("description deve ser uma string ou None.")
    return value.strip() or None


def _check_keys(value: Any, keys: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StorageError(f"{label} deve ser um objeto JSON.")
    missing = keys - value.keys()
    extra = value.keys() - keys
    if missing or extra:
        raise StorageError(
            f"{label} possui campos ausentes {sorted(missing)} "
            f"ou desconhecidos {sorted(extra)}."
        )
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise StorageError(f"Chave JSON repetida: {key!r}.")
        record[key] = value
    return record


def _reject_nonfinite(token: str) -> None:
    raise StorageError(f"Número JSON não finito: {token}.")


class Project:
    """Coordena personagens, parentescos, famílias e persistência.

    Project é uma agregação por composição, não uma subclasse de Genealogy.
    O identificador e os metadados permanecem independentes dos UUIDs das
    entidades do domínio.
    """

    def __init__(
        self,
        name: str,
        *,
        description: str | None = None,
        id: UUID | None = None,
    ) -> None:
        self._name = _required_name(name)
        self._description = _optional_description(description)
        self._id = uuid4() if id is None else id
        if not isinstance(self._id, UUID):
            raise TypeError("id deve ser um UUID ou None.")
        self._genealogy = Genealogy()
        self._families = FamilyRegistry(self._genealogy)
        self._organizations = OrganizationRegistry(self._genealogy)
        self._religions = ReligionRegistry()

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def genealogy(self) -> Genealogy:
        """Núcleo genealógico. Prefira os métodos de Project para alterações."""
        return self._genealogy

    @property
    def families(self) -> FamilyRegistry:
        """Registro de famílias associado a esta genealogia."""
        return self._families

    @property
    def organizations(self) -> OrganizationRegistry:
        """Registro de organizações vinculadas aos personagens deste projeto."""
        return self._organizations

    @property
    def religions(self) -> ReligionRegistry:
        """Registro das tradições, divindades e doutrinas do projeto."""
        return self._religions

    def rename(self, name: str) -> None:
        """Altera o nome validando-o antes de modificar os metadados."""
        self._name = _required_name(name)

    def set_description(self, description: str | None) -> None:
        self._description = _optional_description(description)

    # ------------------------------------------------------------------
    # Personagens: a exclusão é coordenada com as afiliações e fundadores.
    # ------------------------------------------------------------------
    def add_character(self, character: Character) -> None:
        self._genealogy.add_character(character)

    def update_character(self, character: Character) -> None:
        self._genealogy.update_character(character)

    def get_character(self, character_id: UUID) -> Character:
        return self._genealogy.get_character(character_id)

    def get_all_characters(self) -> tuple[Character, ...]:
        return self._genealogy.get_all_characters()

    def remove_character(
        self, character_id: UUID, *, founder_policy: str = "reject",
    ) -> Character:
        """Exclui personagem, parentescos e afiliações de modo consistente.

        ``founder_policy='reject'`` (padrão): impede excluir fundadores.
        ``founder_policy='clear'``: limpa ``founder_id`` nas famílias afetadas.

        O procedimento é transacional em memória: executa todas as etapas
        em uma cópia do estado, verificando a integridade antes de confirmá-la.
        Se ocorrer erro, o estado original permanece intocado. Após o sucesso,
        obtenha novamente ``project.genealogy``/``project.families`` caso tenha
        armazenado referências anteriores a eles.
        """
        if not isinstance(founder_policy, str):
            raise TypeError("founder_policy deve ser uma string.")
        if founder_policy not in _FOUNDER_POLICIES:
            raise ValueError("founder_policy deve ser 'reject' ou 'clear'.")

        character = self._genealogy.get_character(character_id)
        # Valida o estado integral antes de iniciar a alteração transacional.
        self.validate_integrity()
        founder_families = tuple(
            family for family in self._families.get_all_families()
            if family.founder_id == character_id
        )
        founder_organizations = tuple(
            org for org in self._organizations.get_all_organizations()
            if org.founder_id == character_id
        )
        founder_religions = tuple(
            religion for religion in self._religions.get_all_religions()
            if religion.founder_id == character_id
        )
        founded = (*founder_families, *founder_organizations, *founder_religions)
        if founded and founder_policy == "reject":
            names = ", ".join(item.name for item in founded)
            raise ValueError(
                f"Personagem é fundador de: {names}. "
                "Use founder_policy='clear' para limpar essas referências."
            )

        # Cópia independente: erros posteriores não alteram nenhum registro original.
        snapshot = project_to_dict(self._genealogy, self._families)
        new_genealogy, new_families = project_from_dict(snapshot)
        new_organizations = OrganizationRegistry.from_dict(
            new_genealogy, self._organizations.to_dict()
        )
        new_religions = ReligionRegistry.from_dict(self._religions.to_dict())
        for family in founder_families:
            new_families.update_family(replace(family, founder_id=None))
        for religion in founder_religions:
            new_religions.update_religion(replace(religion, founder_id=None))
        new_organizations.remove_character_references(
            character_id, founder_policy=founder_policy
        )
        new_families.remove_character_memberships(character_id)
        new_genealogy.remove_character(character_id)
        new_families.validate_integrity()
        new_organizations.validate_integrity()
        new_religions.validate_integrity()

        self._genealogy = new_genealogy
        self._families = new_families
        self._organizations = new_organizations
        self._religions = new_religions
        return character

    # ------------------------------------------------------------------
    # Relações genealógicas
    # ------------------------------------------------------------------
    def add_relationship(self, relationship: Relationship) -> None:
        self._genealogy.add_relationship(relationship)

    def get_relationship(self, relationship_id: UUID) -> Relationship:
        return self._genealogy.get_relationship(relationship_id)

    def get_relationships(self) -> tuple[Relationship, ...]:
        return self._genealogy.get_relationships()

    def remove_relationship(self, relationship_id: UUID) -> Relationship:
        return self._genealogy.remove_relationship(relationship_id)

    # ------------------------------------------------------------------
    # Casas, clãs, dinastias e afiliações
    # ------------------------------------------------------------------
    def add_family(self, family: Family) -> None:
        self._families.add_family(family)

    def update_family(self, family: Family) -> None:
        self._families.update_family(family)

    def get_family(self, family_id: UUID) -> Family:
        return self._families.get_family(family_id)

    def get_all_families(self) -> tuple[Family, ...]:
        return self._families.get_all_families()

    def remove_family(self, family_id: UUID) -> Family:
        return self._families.remove_family(family_id)

    def add_membership(self, membership: FamilyMembership) -> None:
        self._families.add_membership(membership)

    def update_membership(self, membership: FamilyMembership) -> None:
        self._families.update_membership(membership)

    def get_membership(self, membership_id: UUID) -> FamilyMembership:
        return self._families.get_membership(membership_id)

    def get_memberships(self) -> tuple[FamilyMembership, ...]:
        return self._families.get_memberships()

    def remove_membership(self, membership_id: UUID) -> FamilyMembership:
        return self._families.remove_membership(membership_id)

    # ------------------------------------------------------------------
    # Organizações, ordens, guildas e cargos
    # ------------------------------------------------------------------
    def add_organization(self, organization: Organization) -> None:
        self._organizations.add_organization(organization)

    def update_organization(self, organization: Organization) -> None:
        self._organizations.update_organization(organization)

    def get_organization(self, organization_id: UUID) -> Organization:
        return self._organizations.get_organization(organization_id)

    def get_all_organizations(self) -> tuple[Organization, ...]:
        return self._organizations.get_all_organizations()

    def remove_organization(self, organization_id: UUID) -> Organization:
        return self._organizations.remove_organization(organization_id)

    def add_organization_membership(self, membership: OrganizationMembership) -> None:
        self._organizations.add_membership(membership)

    def update_organization_membership(self, membership: OrganizationMembership) -> None:
        self._organizations.update_membership(membership)

    def get_organization_membership(self, membership_id: UUID) -> OrganizationMembership:
        return self._organizations.get_membership(membership_id)

    def get_organization_memberships(self, **filters: Any) -> tuple[OrganizationMembership, ...]:
        return self._organizations.get_memberships(**filters)

    def remove_organization_membership(self, membership_id: UUID) -> OrganizationMembership:
        return self._organizations.remove_membership(membership_id)

    # ------------------------------------------------------------------
    # Religiões, divindades, doutrinas e suas associações
    # ------------------------------------------------------------------
    def _check_religion_founder(self, religion: Religion) -> None:
        if not isinstance(religion, Religion):
            raise TypeError("religion deve ser Religion.")
        if religion.founder_id is not None:
            self._genealogy.get_character(religion.founder_id)

    def add_religion(self, religion: Religion) -> None:
        self._check_religion_founder(religion)
        self._religions.add_religion(religion)

    def update_religion(self, religion: Religion) -> None:
        self._check_religion_founder(religion)
        self._religions.update_religion(religion)

    def get_religion(self, religion_id: UUID) -> Religion:
        return self._religions.get_religion(religion_id)

    def get_all_religions(self) -> tuple[Religion, ...]:
        return self._religions.get_all_religions()

    def remove_religion(self, religion_id: UUID, *, on_children: str = "reject") -> Religion:
        return self._religions.remove_religion(religion_id, on_children=on_children)

    def add_deity(self, deity: Deity) -> None:
        self._religions.add_deity(deity)

    def update_deity(self, deity: Deity) -> None:
        self._religions.update_deity(deity)

    def get_deity(self, deity_id: UUID) -> Deity:
        return self._religions.get_deity(deity_id)

    def get_all_deities(self) -> tuple[Deity, ...]:
        return self._religions.get_all_deities()

    def remove_deity(self, deity_id: UUID) -> Deity:
        return self._religions.remove_deity(deity_id)

    def link_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        self._religions.link_deity(religion_id, deity_id)

    def unlink_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        self._religions.unlink_deity(religion_id, deity_id)

    def get_deities(self, religion_id: UUID) -> tuple[Deity, ...]:
        return self._religions.get_deities(religion_id)

    def add_doctrine(self, doctrine: Doctrine) -> None:
        self._religions.add_doctrine(doctrine)

    def update_doctrine(self, doctrine: Doctrine) -> None:
        self._religions.update_doctrine(doctrine)

    def get_doctrine(self, doctrine_id: UUID) -> Doctrine:
        return self._religions.get_doctrine(doctrine_id)

    def get_doctrines(self, **filters: Any) -> tuple[Doctrine, ...]:
        return self._religions.get_doctrines(**filters)

    def remove_doctrine(self, doctrine_id: UUID) -> Doctrine:
        return self._religions.remove_doctrine(doctrine_id)

    def validate_integrity(self) -> None:
        """Verifica todas as referências antes de salvar ou exportar."""
        project_to_dict(self._genealogy, self._families)
        self._organizations.validate_integrity()
        self._religions.validate_integrity()
        for religion in self._religions.get_all_religions():
            self._check_religion_founder(religion)

    # ------------------------------------------------------------------
    # Formato de documento completo; suporta importação dos JSONs antigos.
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        self.validate_integrity()
        organization_data = self._organizations.to_dict()
        religion_data = self._religions.to_dict()
        has_extended_data = (
            any(organization_data.values()) or any(religion_data.values())
        )
        document = {
            "format": PROJECT_FORMAT,
            "version": EXTENDED_PROJECT_VERSION if has_extended_data else PROJECT_VERSION,
            "metadata": {
                "id": str(self._id),
                "name": self._name,
                "description": self._description,
            },
            "data": project_to_dict(self._genealogy, self._families),
        }
        if has_extended_data:
            document["organizations"] = organization_data
            document["religions"] = religion_data
        return document

    @classmethod
    def from_dict(
        cls, document: Any, *, legacy_name: str = "Projeto importado",
    ) -> Project:
        if not isinstance(document, dict):
            raise StorageError("Documento deve ser um objeto JSON.")

        if document.get("format") == GENEALOGY_FORMAT:
            # Importação do documento genealógico, sem metadados de projeto.
            genealogy, registry = project_from_dict(document)
            try:
                project = cls(name=legacy_name)
            except (TypeError, ValueError) as exc:
                raise StorageError(f"Nome do projeto importado inválido: {exc}") from exc
            extended = False
        else:
            if document.get("format") != PROJECT_FORMAT:
                raise StorageError("Formato de projeto desconhecido.")
            version = document.get("version")
            if type(version) is not int or version not in (
                PROJECT_VERSION, EXTENDED_PROJECT_VERSION
            ):
                raise StorageError(f"Versão de projeto não suportada: {version!r}.")
            extended = version == EXTENDED_PROJECT_VERSION
            doc = _check_keys(
                document,
                _EXTENDED_PROJECT_KEYS if extended else _PROJECT_KEYS,
                "Projeto",
            )
            meta = _check_keys(doc["metadata"], _METADATA_KEYS, "Metadados")
            try:
                if not isinstance(meta["id"], str):
                    raise TypeError("id deve ser uma string UUID.")
                project_id = UUID(meta["id"])
                project = cls(
                    name=meta["name"], description=meta["description"], id=project_id
                )
            except (ValueError, TypeError, AttributeError) as exc:
                raise StorageError(f"Metadados de projeto inválidos: {exc}") from exc
            genealogy, registry = project_from_dict(doc["data"])

        project._genealogy = genealogy
        project._families = registry
        if extended:
            try:
                project._organizations = OrganizationRegistry.from_dict(
                    genealogy, document["organizations"]
                )
                project._religions = ReligionRegistry.from_dict(document["religions"])
                project.validate_integrity()
            except (ValueError, TypeError, KeyError) as exc:
                raise StorageError(f"Registros institucionais inválidos: {exc}") from exc
        else:
            project._organizations = OrganizationRegistry(genealogy)
            project._religions = ReligionRegistry()
        return project

    def save(self, path: str | PathLike[str]) -> None:
        """Salva em JSON UTF-8 com substituição atômica do arquivo."""
        document = self.to_dict()  # valida todo o estado antes de criar arquivo
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=destination.parent,
                prefix=f".{destination.name}.", suffix=".tmp", delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                json.dump(document, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @classmethod
    def load(cls, path: str | PathLike[str]) -> Project:
        """Carrega arquivo do Arconte; importa também JSON v1/v2 legados."""
        source = Path(path)
        try:
            with source.open("r", encoding="utf-8") as handle:
                document = json.load(
                    handle,
                    object_pairs_hook=_reject_duplicate_keys,
                    parse_constant=_reject_nonfinite,
                )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StorageError(f"Arquivo JSON inválido: {exc}") from exc
        return cls.from_dict(document, legacy_name=source.stem)

    def __repr__(self) -> str:
        return f"Project(name={self._name!r}, id={self._id!s})"


__all__ = ["Project", "PROJECT_FORMAT", "PROJECT_VERSION", "EXTENDED_PROJECT_VERSION"]
