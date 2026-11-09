"""Editor de projetos genealógicos do Arconte (Python 3.10+).

Este módulo fornece duas camadas:

* ``Editor``: operações de edição sobre ``Project`` com validações e controle
  de alterações não salvas. Não duplica a lógica dos modelos de domínio.
* ``main``: menu de terminal para usar o programa antes da interface Flutter.

Não depende de FastAPI, Flutter ou bibliotecas externas. Para executar,
na pasta ``backend/genealogy``::

    python3 -m editor.editor
    python3 -m editor.editor --file data/eldoria.json

As operações de exclusão seguem as regras de ``Project``. Em especial, por
padrão não é permitido apagar o fundador de uma família.

A propriedade ``project`` expõe o objeto de domínio para consultas avançadas.
Alterações feitas diretamente sobre ele não são rastreadas em ``is_dirty``:
para editar, prefira sempre os métodos do Editor.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import fields, replace
from os import PathLike
from pathlib import Path
from typing import Any, Iterable
from uuid import UUID

from character.character import Character
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory, HistoryEvent
from family.family import Family, FamilyMembership, FamilyType, MembershipOrigin
from project.project import Project
from organization.organization import Organization, OrganizationType
from organization.membership import OrganizationMembership
from religion.religion import Religion, ReligionType
from religion.deity import Deity
from religion.doctrine import Doctrine, DoctrineCategory
from relationship.relationship import Relationship, RelationshipType
from tree.tree import TreeBuilder, TreeLayout, layout_tree
from viewer.viewer import ViewerOptions, save_html
from visualization.visualization import SvgOptions, save_svg


_CHARACTER_FIELDS = frozenset(
    {"name", "surname", "gender", "birth_year", "death_year", "biography",
     "physical", "personality", "social", "history"}
)
_FAMILY_FIELDS = frozenset(
    {"name", "type", "founder_id", "founded_year", "dissolved_year", "motto", "description"}
)
_MEMBERSHIP_FIELDS = frozenset(
    {"family_id", "character_id", "origin", "start_year", "end_year", "role"}
)
_PARENT_TYPES = frozenset(
    {RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT}
)
_UNION_TYPES = frozenset({RelationshipType.MARRIAGE, RelationshipType.PARTNERSHIP})


def _path(value: str | PathLike[str]) -> Path:
    if not isinstance(value, (str, PathLike)):
        raise TypeError("O caminho deve ser string ou PathLike.")
    destination = Path(value)
    if not str(value).strip() or str(value).strip() == ".":
        raise ValueError("Informe um caminho de arquivo válido.")
    return destination


def _changes(changes: dict[str, Any], allowed: frozenset[str]) -> dict[str, Any]:
    invalid = sorted(set(changes) - allowed)
    if invalid:
        raise ValueError(f"Campos não editáveis: {', '.join(invalid)}.")
    return changes


class Editor:
    """Ponto de entrada para editar um projeto Arconte.

    Modificações delegam ao Project e às entidades imutáveis existentes.
    Falhas de validação não alteram o estado nem a marca de modificações.
    ``save()`` preserva o último arquivo válido em caso de erro de escrita,
    pois utiliza ``Project.save()`` (substituição atômica).
    """

    def __init__(
        self,
        project: Project,
        *,
        path: str | PathLike[str] | None = None,
        dirty: bool = True,
    ) -> None:
        if not isinstance(project, Project):
            raise TypeError("project deve ser Project.")
        if type(dirty) is not bool:
            raise TypeError("dirty deve ser bool.")
        self._project = project
        self._path = _path(path) if path is not None else None
        self._dirty = dirty

    @classmethod
    def new(
        cls,
        name: str,
        *,
        description: str | None = None,
        path: str | PathLike[str] | None = None,
    ) -> Editor:
        return cls(Project(name, description=description), path=path, dirty=True)

    @classmethod
    def open(cls, path: str | PathLike[str]) -> Editor:
        source = _path(path)
        return cls(Project.load(source), path=source, dirty=False)

    @property
    def project(self) -> Project:
        return self._project

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def is_dirty(self) -> bool:
        """True se houver modificações feitas por meio do Editor não salvas."""
        return self._dirty

    def rename_project(self, name: str) -> None:
        old = self._project.name
        self._project.rename(name)
        self._dirty |= self._project.name != old

    def describe_project(self, description: str | None) -> None:
        old = self._project.description
        self._project.set_description(description)
        self._dirty |= self._project.description != old

    # ------------------------------------------------------------------
    # Personagens
    # ------------------------------------------------------------------
    def create_character(
        self,
        name: str,
        *,
        surname: str | None = None,
        gender: str | None = None,
        birth_year: int | None = None,
        death_year: int | None = None,
        biography: str | None = None,
        physical: PhysicalAttributes | None = None,
        personality: PersonalityProfile | None = None,
        social: SocialProfile | None = None,
        history: CharacterHistory | None = None,
    ) -> Character:
        if history is not None and biography is not None:
            if not isinstance(history, CharacterHistory):
                raise TypeError("history deve ser CharacterHistory.")
            if isinstance(biography, str) and (biography.strip() or None) != history.biography:
                raise ValueError("biography e history.biography devem coincidir.")
        character = Character(
            name=name, surname=surname, gender=gender,
            birth_year=birth_year, death_year=death_year, biography=biography,
            physical=physical if physical is not None else PhysicalAttributes(),
            personality=personality if personality is not None else PersonalityProfile(),
            social=social if social is not None else SocialProfile(),
            history=history if history is not None else CharacterHistory(),
        )
        self._project.add_character(character)
        self._dirty = True
        return character

    def update_character(self, character_id: UUID, **changes: Any) -> Character:
        _changes(changes, _CHARACTER_FIELDS)
        current = self._project.get_character(character_id)
        if "history" in changes and not isinstance(changes["history"], CharacterHistory):
            raise TypeError("history deve ser CharacterHistory.")
        if "biography" in changes and "history" not in changes:
            changes["history"] = replace(current.history, biography=changes["biography"])
        if "history" in changes and "biography" not in changes:
            if not isinstance(changes["history"], CharacterHistory):
                raise TypeError("history deve ser CharacterHistory.")
            changes["biography"] = changes["history"].biography
        if "history" in changes and "biography" in changes:
            if changes["history"].biography != (
                changes["biography"].strip() or None
                if isinstance(changes["biography"], str) else changes["biography"]
            ):
                raise ValueError("biography e history.biography devem coincidir.")
        updated = replace(current, **changes)
        if updated == current:
            return current
        self._project.update_character(updated)
        self._dirty = True
        return updated

    def update_physical(self, character_id: UUID, **changes: Any) -> Character:
        """Altera apenas o bloco de atributos físicos, preservando os outros."""
        _changes(changes, frozenset(f.name for f in fields(PhysicalAttributes)))
        current = self._project.get_character(character_id)
        return self.update_character(
            character_id, physical=replace(current.physical, **changes)
        )

    def update_personality(self, character_id: UUID, **changes: Any) -> Character:
        """Altera apenas personalidade, incluindo listas e atributos personalizados."""
        _changes(changes, frozenset(f.name for f in fields(PersonalityProfile)))
        current = self._project.get_character(character_id)
        return self.update_character(
            character_id, personality=replace(current.personality, **changes)
        )

    def update_social(self, character_id: UUID, **changes: Any) -> Character:
        """Altera a ficha social sem criar afiliações no FamilyRegistry."""
        _changes(changes, frozenset(f.name for f in fields(SocialProfile)))
        current = self._project.get_character(character_id)
        return self.update_character(character_id, social=replace(current.social, **changes))

    def update_history(self, character_id: UUID, **changes: Any) -> Character:
        """Atualiza a história e sincroniza o campo legado biography."""
        _changes(changes, frozenset(f.name for f in fields(CharacterHistory)))
        current = self._project.get_character(character_id)
        new_history = replace(current.history, **changes)
        return self.update_character(character_id, history=new_history)

    def add_history_event(
        self, character_id: UUID, title: str, *, year: int | None = None,
        category: str | None = None, description: str | None = None,
    ) -> HistoryEvent:
        """Anexa acontecimento narrativo validado (sem alterar parentescos)."""
        event = HistoryEvent(
            title=title, year=year, category=category, description=description
        )
        current = self._project.get_character(character_id)
        self.update_history(character_id, events=(*current.history.events, event))
        return event

    def remove_history_event(self, character_id: UUID, event_id: UUID) -> HistoryEvent:
        current = self._project.get_character(character_id)
        event = next((e for e in current.history.events if e.id == event_id), None)
        if event is None:
            raise KeyError(f"Evento não encontrado: {event_id}")
        self.update_history(
            character_id, events=tuple(e for e in current.history.events if e.id != event_id)
        )
        return event

    def remove_character(
        self, character_id: UUID, *, founder_policy: str = "reject",
    ) -> Character:
        removed = self._project.remove_character(character_id, founder_policy=founder_policy)
        self._dirty = True
        return removed

    def list_characters(self) -> tuple[Character, ...]:
        return self._project.get_all_characters()

    # ------------------------------------------------------------------
    # Relacionamentos
    # ------------------------------------------------------------------
    def create_relationship(
        self,
        source_id: UUID,
        target_id: UUID,
        type: RelationshipType,
        *,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> Relationship:
        relation = Relationship(
            source_id=source_id, target_id=target_id, type=type,
            start_year=start_year, end_year=end_year,
        )
        self._project.add_relationship(relation)
        self._dirty = True
        return relation

    def remove_relationship(self, relationship_id: UUID) -> Relationship:
        relation = self._project.remove_relationship(relationship_id)
        self._dirty = True
        return relation

    def list_relationships(self) -> tuple[Relationship, ...]:
        return self._project.get_relationships()

    # ------------------------------------------------------------------
    # Famílias e afiliações
    # ------------------------------------------------------------------
    def create_family(
        self,
        name: str,
        *,
        type: FamilyType = FamilyType.FAMILY,
        founder_id: UUID | None = None,
        founded_year: int | None = None,
        dissolved_year: int | None = None,
        motto: str | None = None,
        description: str | None = None,
    ) -> Family:
        family = Family(
            name=name, type=type, founder_id=founder_id,
            founded_year=founded_year, dissolved_year=dissolved_year,
            motto=motto, description=description,
        )
        self._project.add_family(family)
        self._dirty = True
        return family

    def update_family(self, family_id: UUID, **changes: Any) -> Family:
        _changes(changes, _FAMILY_FIELDS)
        current = self._project.get_family(family_id)
        updated = replace(current, **changes)
        if updated == current:
            return current
        self._project.update_family(updated)
        self._dirty = True
        return updated

    def remove_family(self, family_id: UUID) -> Family:
        family = self._project.remove_family(family_id)
        self._dirty = True
        return family

    def list_families(self) -> tuple[Family, ...]:
        return self._project.get_all_families()

    def add_membership(
        self,
        family_id: UUID,
        character_id: UUID,
        *,
        origin: MembershipOrigin = MembershipOrigin.AFFILIATION,
        role: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> FamilyMembership:
        membership = FamilyMembership(
            family_id=family_id, character_id=character_id,
            origin=origin, role=role, start_year=start_year, end_year=end_year,
        )
        self._project.add_membership(membership)
        self._dirty = True
        return membership

    def update_membership(self, membership_id: UUID, **changes: Any) -> FamilyMembership:
        _changes(changes, _MEMBERSHIP_FIELDS)
        current = self._project.get_membership(membership_id)
        updated = replace(current, **changes)
        if updated == current:
            return current
        self._project.update_membership(updated)
        self._dirty = True
        return updated

    def remove_membership(self, membership_id: UUID) -> FamilyMembership:
        membership = self._project.remove_membership(membership_id)
        self._dirty = True
        return membership

    def list_memberships(self) -> tuple[FamilyMembership, ...]:
        return self._project.get_memberships()

    # ------------------------------------------------------------------
    # Organizações e suas afiliações
    # ------------------------------------------------------------------
    def create_organization(
        self, name: str, *, type: OrganizationType = OrganizationType.ORGANIZATION,
        founder_id: UUID | None = None, founded_year: int | None = None,
        dissolved_year: int | None = None, headquarters: str | None = None,
        motto: str | None = None, emblem: str | None = None,
        description: str | None = None, custom_attributes: dict[str, Any] | None = None,
    ) -> Organization:
        organization = Organization(
            name=name, type=type, founder_id=founder_id,
            founded_year=founded_year, dissolved_year=dissolved_year,
            headquarters=headquarters, motto=motto, emblem=emblem,
            description=description,
            custom_attributes={} if custom_attributes is None else custom_attributes,
        )
        self._project.add_organization(organization)
        self._dirty = True
        return organization

    def update_organization(self, organization_id: UUID, **changes: Any) -> Organization:
        _changes(changes, frozenset(f.name for f in fields(Organization)) - {"id"})
        current = self._project.get_organization(organization_id)
        updated = replace(current, **changes)
        if updated != current:
            self._project.update_organization(updated)
            self._dirty = True
        return updated

    def remove_organization(self, organization_id: UUID) -> Organization:
        removed = self._project.remove_organization(organization_id)
        self._dirty = True
        return removed

    def list_organizations(self) -> tuple[Organization, ...]:
        return self._project.get_all_organizations()

    def add_organization_membership(
        self, organization_id: UUID, character_id: UUID, *,
        role: str | None = None, rank: str | None = None,
        start_year: int | None = None, end_year: int | None = None,
        notes: str | None = None,
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            organization_id=organization_id, character_id=character_id,
            role=role, rank=rank, start_year=start_year,
            end_year=end_year, notes=notes,
        )
        self._project.add_organization_membership(membership)
        self._dirty = True
        return membership

    def update_organization_membership(
        self, membership_id: UUID, **changes: Any,
    ) -> OrganizationMembership:
        _changes(
            changes, frozenset(f.name for f in fields(OrganizationMembership)) - {"id"},
        )
        current = self._project.get_organization_membership(membership_id)
        updated = replace(current, **changes)
        if updated != current:
            self._project.update_organization_membership(updated)
            self._dirty = True
        return updated

    def remove_organization_membership(self, membership_id: UUID) -> OrganizationMembership:
        result = self._project.remove_organization_membership(membership_id)
        self._dirty = True
        return result

    def list_organization_memberships(self, **filters: Any) -> tuple[OrganizationMembership, ...]:
        return self._project.get_organization_memberships(**filters)

    # ------------------------------------------------------------------
    # Religiões, divindades e doutrinas
    # ------------------------------------------------------------------
    def create_religion(
        self, name: str, *, type: ReligionType = ReligionType.OTHER,
        founder_id: UUID | None = None, parent_religion_id: UUID | None = None,
        founded_year: int | None = None, ended_year: int | None = None,
        origin_place: str | None = None, scriptures: Iterable[str] = (),
        traditions: Iterable[str] = (), description: str | None = None,
        custom_attributes: dict[str, Any] | None = None,
    ) -> Religion:
        religion = Religion(
            name=name, type=type, founder_id=founder_id,
            parent_religion_id=parent_religion_id, founded_year=founded_year,
            ended_year=ended_year, origin_place=origin_place,
            scriptures=tuple(scriptures), traditions=tuple(traditions),
            description=description,
            custom_attributes={} if custom_attributes is None else custom_attributes,
        )
        self._project.add_religion(religion)
        self._dirty = True
        return religion

    def update_religion(self, religion_id: UUID, **changes: Any) -> Religion:
        _changes(changes, frozenset(f.name for f in fields(Religion)) - {"id"})
        current = self._project.get_religion(religion_id)
        updated = replace(current, **changes)
        if updated != current:
            self._project.update_religion(updated)
            self._dirty = True
        return updated

    def remove_religion(self, religion_id: UUID, *, on_children: str = "reject") -> Religion:
        removed = self._project.remove_religion(religion_id, on_children=on_children)
        self._dirty = True
        return removed

    def list_religions(self) -> tuple[Religion, ...]:
        return self._project.get_all_religions()

    def create_deity(
        self, name: str, *, epithets: Iterable[str] = (),
        domains: Iterable[str] = (), symbols: Iterable[str] = (),
        description: str | None = None, custom_attributes: dict[str, Any] | None = None,
    ) -> Deity:
        deity = Deity(
            name=name, epithets=tuple(epithets), domains=tuple(domains),
            symbols=tuple(symbols), description=description,
            custom_attributes={} if custom_attributes is None else custom_attributes,
        )
        self._project.add_deity(deity)
        self._dirty = True
        return deity

    def update_deity(self, deity_id: UUID, **changes: Any) -> Deity:
        _changes(changes, frozenset(f.name for f in fields(Deity)) - {"id"})
        current = self._project.get_deity(deity_id)
        updated = replace(current, **changes)
        if updated != current:
            self._project.update_deity(updated)
            self._dirty = True
        return updated

    def remove_deity(self, deity_id: UUID) -> Deity:
        result = self._project.remove_deity(deity_id)
        self._dirty = True
        return result

    def list_deities(self) -> tuple[Deity, ...]:
        return self._project.get_all_deities()

    def link_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        self._project.link_deity(religion_id, deity_id)
        self._dirty = True

    def unlink_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        self._project.unlink_deity(religion_id, deity_id)
        self._dirty = True

    def create_doctrine(
        self, religion_id: UUID, title: str, content: str, *,
        category: DoctrineCategory = DoctrineCategory.OTHER,
        start_year: int | None = None, end_year: int | None = None,
        notes: str | None = None, custom_attributes: dict[str, Any] | None = None,
    ) -> Doctrine:
        doctrine = Doctrine(
            religion_id=religion_id, title=title, content=content,
            category=category, start_year=start_year, end_year=end_year,
            notes=notes,
            custom_attributes={} if custom_attributes is None else custom_attributes,
        )
        self._project.add_doctrine(doctrine)
        self._dirty = True
        return doctrine

    def update_doctrine(self, doctrine_id: UUID, **changes: Any) -> Doctrine:
        _changes(changes, frozenset(f.name for f in fields(Doctrine)) - {"id"})
        current = self._project.get_doctrine(doctrine_id)
        updated = replace(current, **changes)
        if updated != current:
            self._project.update_doctrine(updated)
            self._dirty = True
        return updated

    def remove_doctrine(self, doctrine_id: UUID) -> Doctrine:
        removed = self._project.remove_doctrine(doctrine_id)
        self._dirty = True
        return removed

    def list_doctrines(self, **filters: Any) -> tuple[Doctrine, ...]:
        return self._project.get_doctrines(**filters)

    # ------------------------------------------------------------------
    # Persistência e exportação
    # ------------------------------------------------------------------
    def save(self, path: str | PathLike[str] | None = None) -> Path:
        destination = _path(path) if path is not None else self._path
        if destination is None:
            raise ValueError("Informe o caminho do arquivo para salvar o projeto.")
        self._project.save(destination)
        self._path = destination
        self._dirty = False
        return destination

    def tree_layout(
        self,
        *,
        root_id: UUID | None = None,
        direction: str = "all",
        max_generations: int | None = None,
        include_partners: bool = True,
        parent_types: Iterable[RelationshipType] | None = None,
        horizontal_spacing: float = 240.0,
        vertical_spacing: float = 170.0,
    ) -> TreeLayout:
        graph = TreeBuilder(self._project).build(
            root_id=root_id, direction=direction,
            max_generations=max_generations,
            include_partners=include_partners, parent_types=parent_types,
        )
        return layout_tree(
            graph, horizontal_spacing=horizontal_spacing,
            vertical_spacing=vertical_spacing,
        )

    def export_html(
        self, path: str | PathLike[str],
        *,
        options: ViewerOptions | None = None,
        **tree_options: Any,
    ) -> Path:
        layout = self.tree_layout(**tree_options)
        if options is None:
            options = ViewerOptions(title=self._project.name)
        return save_html(layout, _path(path), options=options, project=self._project)

    def export_svg(
        self, path: str | PathLike[str],
        *,
        options: SvgOptions | None = None,
        **tree_options: Any,
    ) -> Path:
        layout = self.tree_layout(**tree_options)
        if options is None:
            options = SvgOptions(title=self._project.name)
        return save_svg(layout, _path(path), options=options)


# ----------------------------------------------------------------------
# Interface simples de terminal. O futuro frontend Flutter usará Editor
# diretamente e não dependerá desta interface.
# ----------------------------------------------------------------------

def _ask(prompt: str) -> str:
    return input(prompt).strip()


def _ask_text(prompt: str) -> str:
    """Entrada normal de uma linha ou modo :multi encerrado por linha '.'."""
    first = _ask(prompt)
    if first != ":multi":
        return first
    print("Modo multilinha: escreva ou cole vários parágrafos; finalize com '.' isolado.")
    lines: list[str] = []
    while True:
        line = input("")
        if line == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _required(prompt: str) -> str:
    result = _ask(prompt)
    if not result:
        raise ValueError("Este campo é obrigatório.")
    return result


def _year(prompt: str) -> int | None:
    raw = _ask(prompt + " (opcional): ")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError("Ano inválido: informe um inteiro.") from exc


def _choose(items: tuple[Any, ...], label: str, *, allow_none: bool = False) -> Any:
    if not items and not allow_none:
        raise ValueError(f"Não há registros de {label} disponíveis.")
    if allow_none:
        print("0. Nenhum")
    for index, item in enumerate(items, start=1):
        name = getattr(item, "full_name", None) or getattr(item, "name", None) or getattr(
            item, "title", None
        ) or getattr(item, "role", None) or str(item.id)
        print(f"{index}. {name} [{item.id}]")
    selected = _required(f"Selecione {label} pelo número: ")
    if not selected.isdecimal():
        raise ValueError("Informe um número da lista.")
    number = int(selected)
    if allow_none and number == 0:
        return None
    if number < 1 or number > len(items):
        raise ValueError("Opção fora da lista.")
    return items[number - 1]


def _show_characters(editor: Editor) -> None:
    characters = editor.list_characters()
    if not characters:
        print("Nenhum personagem cadastrado.")
    for index, character in enumerate(characters, start=1):
        interval = (
            f" ({character.birth_year if character.birth_year is not None else '?'}"
            f"–{character.death_year if character.death_year is not None else '?'})"
        )
        print(f"{index}. {character.full_name}{interval} | {character.id}")


def _show_relationships(editor: Editor) -> None:
    relations = editor.list_relationships()
    if not relations:
        print("Nenhum relacionamento cadastrado.")
    for index, relation in enumerate(relations, start=1):
        a = editor.project.get_character(relation.source_id).full_name
        b = editor.project.get_character(relation.target_id).full_name
        print(f"{index}. {a} → {b} [{relation.type.value}] | {relation.id}")


def _show_families(editor: Editor) -> None:
    families = editor.list_families()
    if not families:
        print("Nenhuma família cadastrada.")
    for index, family in enumerate(families, start=1):
        count = len(editor.project.families.get_members(family.id))
        print(f"{index}. {family.name} [{family.type.value}] ({count} membros) | {family.id}")


def _create_person(editor: Editor) -> None:
    character = editor.create_character(
        _required("Nome: "),
        surname=_ask("Sobrenome (opcional): ") or None,
        gender=_ask("Gênero (opcional): ") or None,
        birth_year=_year("Nascimento"),
        death_year=_year("Falecimento"),
        biography=_ask_text("Biografia (opcional, :multi para parágrafos): ") or None,
    )
    print(f"Personagem criado: {character.full_name} ({character.id})")


def _edit_person(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    print("Deixe em branco para manter o valor. Use '-' para limpar opcionais.")
    labels = (
        ("name", "Nome"), ("surname", "Sobrenome"),
        ("gender", "Gênero"), ("birth_year", "Nascimento"),
        ("death_year", "Falecimento"), ("biography", "Biografia"),
    )
    updates: dict[str, Any] = {}
    for key, label in labels:
        raw = (_ask_text if key == "biography" else _ask)(
            f"{label} [{getattr(person, key) if getattr(person, key) is not None else '—'}]: "
        )
        if not raw:
            continue
        if raw == "-" and key != "name":
            updates[key] = None
        elif key in ("birth_year", "death_year"):
            try:
                updates[key] = int(raw)
            except ValueError as exc:
                raise ValueError(f"{label}: informe um número inteiro.") from exc
        else:
            updates[key] = raw
    updated = editor.update_character(person.id, **updates)
    print(f"Personagem atualizado: {updated.full_name}")


def _show_character_details(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    print(f"\n=== Ficha de {person.full_name} ===")
    print(f"Identidade: {person.gender or '—'} | nascimento: {person.birth_year} | falecimento: {person.death_year}")
    for label, profile in (
        ("FÍSICO", person.physical),
        ("PERSONALIDADE", person.personality),
        ("SOCIAL", person.social),
    ):
        print(f"\n[{label}]")
        for field in fields(type(profile)):
            value = getattr(profile, field.name)
            if field.name == "custom_attributes":
                value = profile.to_dict()["custom_attributes"]
            print(f"  {field.name}: {value if value not in (None, (), {}, '') else '—'}")
    print("\n[HISTÓRIA]")
    print(person.history.biography or "Sem biografia.")
    for event in person.history.chronological_events():
        print(f"  - {event.year if event.year is not None else 's/d'}: {event.title} ({event.category or 'evento'})")
        if event.description:
            print(f"    {event.description}")
    print(f"  custom_attributes: {person.history.to_dict()['custom_attributes']}")


def _profile_changes(profile: Any) -> dict[str, Any]:
    print("Deixe vazio para manter; '-' para limpar. 'description': :multi para parágrafos.")
    changes: dict[str, Any] = {}
    for field in fields(type(profile)):
        key = field.name
        old = getattr(profile, key)
        shown = profile.to_dict()[key] if key == "custom_attributes" else old
        prompt = f"{key} [{shown if shown not in (None, (), {}, '') else '—'}]: "
        raw = (_ask_text if key == "description" else _ask)(prompt)
        if not raw:
            continue
        if key == "custom_attributes":
            if raw == "-":
                changes[key] = {}
            else:
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"JSON de custom_attributes inválido: {exc}") from exc
                if not isinstance(obj, dict):
                    raise ValueError("custom_attributes precisa ser um objeto JSON: { ... }.")
                changes[key] = obj
        elif isinstance(profile, PhysicalAttributes) and key in ("height_m", "weight_kg"):
            if raw == "-":
                changes[key] = None
            else:
                try:
                    changes[key] = float(raw.replace(",", "."))
                except ValueError as exc:
                    raise ValueError(f"{key}: informe um número válido.") from exc
        elif isinstance(profile, PersonalityProfile) and key != "description":
            changes[key] = [] if raw == "-" else [item.strip() for item in raw.split(",")]
        else:
            changes[key] = None if raw == "-" else raw
    return changes


def _edit_profile(editor: Editor, kind: str) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    profile = getattr(person, kind)
    print(f"\n=== {kind.upper()}: {person.full_name} ===")
    if kind == "personality":
        print("Nas listas, separe as características com vírgulas.")
    if kind == "physical":
        print("Altura em metros (1,68 ou 1.68), peso em quilogramas (80).")
    changes = _profile_changes(profile)
    method = getattr(editor, f"update_{kind}")
    method(person.id, **changes)
    print(f"Bloco {kind} atualizado.")


def _edit_history(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    print("Digite :multi para escrever vários parágrafos e finalize com '.' isolado.")
    print(f"Biografia atual:\n{person.history.biography or '—'}")
    value = _ask_text("Nova biografia (vazio mantém, '-' limpa): ")
    if value:
        editor.update_history(person.id, biography=None if value == "-" else value)
    print("História atualizada.")


def _add_history_event_interactive(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    event = editor.add_history_event(
        person.id,
        _required("Título do acontecimento: "),
        year=_year("Ano do acontecimento"),
        category=_ask("Categoria (opcional): ") or None,
        description=_ask_text("Descrição (opcional, :multi para parágrafos): ") or None,
    )
    print(f"Acontecimento criado: {event.title} ({event.id})")


def _remove_history_event_interactive(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    events = person.history.events
    if not events:
        raise ValueError("Este personagem não possui acontecimentos cadastrados.")
    for index, event in enumerate(events, 1):
        print(f"{index}. {event.title} ({event.year if event.year is not None else 's/d'})")
    raw = _required("Número do acontecimento para remover: ")
    if not raw.isdecimal() or not 1 <= int(raw) <= len(events):
        raise ValueError("Escolha um acontecimento da lista.")
    selected = events[int(raw) - 1]
    if _ask(f"Remover '{selected.title}'? [s/N]: ").lower() != "s":
        print("Operação cancelada.")
        return
    editor.remove_history_event(person.id, selected.id)
    print("Acontecimento removido.")


def _delete_person(editor: Editor) -> None:
    person = _choose(editor.list_characters(), "um personagem")
    policy = "clear" if _ask("Se for fundador, desvincular casas? [s/N]: ").lower() == "s" else "reject"
    if _ask(f"Confirma exclusão de {person.full_name}? [s/N]: ").lower() != "s":
        print("Operação cancelada.")
        return
    editor.remove_character(person.id, founder_policy=policy)
    print("Personagem excluído.")


def _create_relationship(editor: Editor) -> None:
    characters = editor.list_characters()
    first = _choose(characters, "a primeira pessoa")
    second = _choose(characters, "a segunda pessoa")
    types = list(RelationshipType)
    for index, item in enumerate(types, 1):
        description = {
            RelationshipType.BIOLOGICAL_PARENT: "Filiação biológica (genitor → filho[a])",
            RelationshipType.ADOPTIVE_PARENT: "Filiação adotiva (responsável → filho[a])",
            RelationshipType.MARRIAGE: "Casamento",
            RelationshipType.PARTNERSHIP: "União",
        }.get(item, item.value)
        print(f"{index}. {description}")
    try:
        index = int(_required("Tipo (número): "))
        if not 1 <= index <= len(types):
            raise ValueError("Tipo de relação fora da lista.")
        relationship_type = types[index - 1]
    except (ValueError, IndexError) as exc:
        raise ValueError("Tipo de relação inválido.") from exc
    if relationship_type in _PARENT_TYPES:
        print("A primeira pessoa será pai/mãe/responsável; a segunda, filho(a).")
    relation = editor.create_relationship(
        first.id, second.id, relationship_type,
        start_year=_year("Ano inicial"), end_year=_year("Ano final"),
    )
    print(f"Relação criada: {relation.id}")


def _delete_relationship(editor: Editor) -> None:
    relation = _choose(editor.list_relationships(), "um vínculo")
    editor.remove_relationship(relation.id)
    print("Vínculo removido.")


def _create_family(editor: Editor) -> None:
    name = _required("Nome da família/casa/clã/dinastia: ")
    types = list(FamilyType)
    for index, item in enumerate(types, 1):
        print(f"{index}. {item.value}")
    try:
        index = int(_required("Tipo (número): "))
        if not 1 <= index <= len(types):
            raise ValueError("Tipo de família fora da lista.")
        family_type = types[index - 1]
    except (ValueError, IndexError) as exc:
        raise ValueError("Tipo de família inválido.") from exc
    founder = _choose(editor.list_characters(), "o fundador", allow_none=True)
    family = editor.create_family(
        name, type=family_type,
        founder_id=founder.id if founder else None,
        founded_year=_year("Ano de fundação"),
        motto=_ask("Lema (opcional): ") or None,
    )
    print(f"Família criada: {family.name} ({family.id})")


def _add_membership(editor: Editor) -> None:
    family = _choose(editor.list_families(), "uma família")
    character = _choose(editor.list_characters(), "um personagem")
    origins = list(MembershipOrigin)
    for index, item in enumerate(origins, 1):
        print(f"{index}. {item.value}")
    try:
        index = int(_required("Origem (número): "))
        if not 1 <= index <= len(origins):
            raise ValueError("Origem fora da lista.")
        origin = origins[index - 1]
    except (ValueError, IndexError) as exc:
        raise ValueError("Origem inválida.") from exc
    member = editor.add_membership(
        family.id, character.id, origin=origin,
        role=_ask("Papel/título (opcional): ") or None,
        start_year=_year("Ano inicial"), end_year=_year("Ano final"),
    )
    print(f"Afiliação criada: {member.id}")


def _save_interactive(editor: Editor) -> None:
    file = editor.path
    if file is None:
        file = _required("Arquivo JSON (ex.: data/eldoria.json): ")
    else:
        if _ask(f"Salvar em {file}? [S/n]: ").lower() == "n":
            file = _required("Novo caminho: ")
    path = editor.save(file)
    print(f"Projeto salvo em {path}")


def _export_interactive(editor: Editor, *, svg: bool = False) -> None:
    extension = "svg" if svg else "html"
    path = _required(f"Caminho do .{extension}: ")
    exported = editor.export_svg(path) if svg else editor.export_html(path)
    print(f"Árvore exportada em {exported}")


def _choose_enum(enum_class: Any, label: str) -> Any:
    values = tuple(enum_class)
    for index, value in enumerate(values, 1):
        print(f"{index}. {value.value}")
    raw = _required(f"{label} (número): ")
    if not raw.isdecimal() or not 1 <= int(raw) <= len(values):
        raise ValueError(f"{label}: escolha uma opção válida.")
    return values[int(raw) - 1]


def _text_tuple(prompt: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in _ask(prompt).split(",") if part.strip())


def _optional_uuid_person(editor: Editor, prompt: str) -> UUID | None:
    print(prompt)
    character = _choose(editor.list_characters(), "um personagem", allow_none=True)
    return character.id if character is not None else None


def _confirm_delete(text: str) -> bool:
    return _ask(f"Excluir {text}? [s/N]: ").lower() == "s"


def _create_organization_interactive(editor: Editor) -> None:
    name = _required("Nome da organização: ")
    kind = _choose_enum(OrganizationType, "Tipo de organização")
    founder = _optional_uuid_person(editor, "Fundador (0 para desconhecido):")
    organization = editor.create_organization(
        name, type=kind, founder_id=founder,
        founded_year=_year("Ano de fundação"),
        dissolved_year=_year("Ano de dissolução"),
        headquarters=_ask("Sede (opcional): ") or None,
        motto=_ask("Lema (opcional): ") or None,
        emblem=_ask("Emblema (opcional): ") or None,
        description=_ask_text("Descrição (:multi para parágrafos, opcional): ") or None,
    )
    print(f"Organização criada: {organization.name} ({organization.id})")


def _show_organizations(editor: Editor) -> None:
    for organization in editor.list_organizations():
        print(f"{organization.name} [{organization.type.value}] | {organization.id}")
    if not editor.list_organizations():
        print("Nenhuma organização cadastrada.")


def _add_organization_member_interactive(editor: Editor) -> None:
    organization = _choose(editor.list_organizations(), "uma organização")
    character = _choose(editor.list_characters(), "um personagem")
    member = editor.add_organization_membership(
        organization.id, character.id,
        role=_ask("Cargo/função (opcional): ") or None,
        rank=_ask("Grau hierárquico (opcional): ") or None,
        start_year=_year("Ano inicial"), end_year=_year("Ano final"),
        notes=_ask_text("Observações (:multi opcional): ") or None,
    )
    print(f"Afiliação institucional cadastrada: {member.id}")


def _show_organization_members(editor: Editor) -> None:
    members = editor.list_organization_memberships()
    if not members:
        print("Nenhuma afiliação organizacional cadastrada.")
    for member in members:
        organization = editor.project.get_organization(member.organization_id)
        character = editor.project.get_character(member.character_id)
        print(f"{character.full_name} — {organization.name} | {member.role or 'membro'} | {member.id}")


def _remove_organization_member_interactive(editor: Editor) -> None:
    member = _choose(editor.list_organization_memberships(), "uma afiliação")
    if _confirm_delete("esta afiliação"):
        editor.remove_organization_membership(member.id)
        print("Afiliação removida.")


def _create_religion_interactive(editor: Editor) -> None:
    name = _required("Nome da religião: ")
    kind = _choose_enum(ReligionType, "Tipo de religião")
    founder = _optional_uuid_person(editor, "Fundador (0 para desconhecido):")
    parent = _choose(editor.list_religions(), "a religião de origem", allow_none=True)
    religion = editor.create_religion(
        name, type=kind, founder_id=founder,
        parent_religion_id=parent.id if parent else None,
        founded_year=_year("Ano de fundação"), ended_year=_year("Ano de encerramento"),
        origin_place=_ask("Local de origem (opcional): ") or None,
        scriptures=_text_tuple("Escrituras (separe por vírgulas, opcional): "),
        traditions=_text_tuple("Tradições (separe por vírgulas, opcional): "),
        description=_ask_text("Descrição (:multi opcional): ") or None,
    )
    print(f"Religião criada: {religion.name} ({religion.id})")


def _show_religions(editor: Editor) -> None:
    religions = editor.list_religions()
    if not religions:
        print("Nenhuma religião cadastrada.")
    for religion in religions:
        print(f"{religion.name} [{religion.type.value}] | {religion.id}")


def _create_deity_interactive(editor: Editor) -> None:
    deity = editor.create_deity(
        _required("Nome da divindade: "),
        epithets=_text_tuple("Epítetos (por vírgula, opcional): "),
        domains=_text_tuple("Domínios (por vírgula, opcional): "),
        symbols=_text_tuple("Símbolos (por vírgula, opcional): "),
        description=_ask_text("Descrição (:multi opcional): ") or None,
    )
    print(f"Divindade cadastrada: {deity.name} ({deity.id})")


def _link_deity_interactive(editor: Editor, *, unlink: bool = False) -> None:
    religion = _choose(editor.list_religions(), "uma religião")
    deities = (
        editor.project.religions.get_deities(religion.id)
        if unlink else editor.list_deities()
    )
    deity = _choose(deities, "uma divindade")
    if unlink:
        editor.unlink_deity(religion.id, deity.id)
        print("Associação desfeita.")
    else:
        editor.link_deity(religion.id, deity.id)
        print("Divindade associada à religião.")


def _show_deities(editor: Editor) -> None:
    deities = editor.list_deities()
    if not deities:
        print("Nenhuma divindade cadastrada.")
    for deity in deities:
        associated = ", ".join(
            religion.name for religion in editor.project.religions.get_religions_for_deity(deity.id)
        ) or "sem religião associada"
        print(f"{deity.name} ({associated}) | {deity.id}")


def _create_doctrine_interactive(editor: Editor) -> None:
    religion = _choose(editor.list_religions(), "uma religião")
    title = _required("Título da doutrina: ")
    content = _ask_text("Conteúdo (:multi para parágrafos): ")
    if not content:
        raise ValueError("Conteúdo da doutrina é obrigatório.")
    category = _choose_enum(DoctrineCategory, "Categoria de doutrina")
    doctrine = editor.create_doctrine(
        religion.id, title, content, category=category,
        start_year=_year("Ano inicial"), end_year=_year("Ano final"),
        notes=_ask_text("Observações (:multi opcional): ") or None,
    )
    print(f"Doutrina criada: {doctrine.title} ({doctrine.id})")


def _show_doctrines(editor: Editor) -> None:
    doctrines = editor.list_doctrines()
    if not doctrines:
        print("Nenhuma doutrina cadastrada.")
    for doctrine in doctrines:
        religion = editor.project.get_religion(doctrine.religion_id)
        print(f"{doctrine.title} — {religion.name} | {doctrine.id}")


def _edit_dataclass_interactive(editor: Editor, item: Any, update_method: Any) -> None:
    """Edita dados simples da entidade sem modificar seus identificadores."""
    changes: dict[str, Any] = {}
    print("Vazio mantém o valor atual; '-' limpa campos opcionais.")
    for field in fields(type(item)):
        key = field.name
        if key == "id":
            continue
        previous = getattr(item, key)
        if key.endswith("_id"):
            # Alterar referências é uma operação de domínio explícita.
            continue
        if key == "custom_attributes":
            print("Atributos personalizados podem ser editados via API Python.")
            continue
        if isinstance(previous, tuple):
            raw = _ask(f"{key} (vírgulas) [{', '.join(previous)}]: ")
            if raw:
                changes[key] = () if raw == "-" else tuple(x.strip() for x in raw.split(",") if x.strip())
        elif hasattr(previous, "value"):
            print(f"{key} atual: {previous.value} (Enter para manter)")
            raw = _ask("Mudar tipo/categoria? [s/N]: ")
            if raw.lower() == "s":
                changes[key] = _choose_enum(type(previous), key)
        elif key.endswith("year"):
            raw = _ask(f"{key} [{previous if previous is not None else '—'}]: ")
            if raw:
                if raw == "-":
                    changes[key] = None
                else:
                    try:
                        changes[key] = int(raw)
                    except ValueError as exc:
                        raise ValueError(f"{key}: ano inválido.") from exc
        else:
            raw = (_ask_text if key in ("description", "content", "notes") else _ask)(
                f"{key} [{previous if previous is not None else '—'}]: "
            )
            if raw:
                changes[key] = None if raw == "-" else raw
    update_method(item.id, **changes)
    print("Registro atualizado.")


def _run_submenu(editor: Editor, actions: dict[str, Any], menu: str,
                 *, autosave: bool = False) -> None:
    while True:
        print("\n" + menu)
        command = _ask("Opção: ")
        if command == "0":
            return
        action = actions.get(command)
        if action is None:
            print("Opção desconhecida.")
            continue
        try:
            action()
            if autosave and editor.is_dirty:
                try:
                    path = editor.save()
                    print(f"Salvamento automático: {path}")
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    print(f"AVISO: salvamento automático falhou: {exc}")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            print(f"Não foi possível executar a operação: {exc}")


def _organization_console(editor: Editor, *, autosave: bool = False) -> None:
    menu = (
        "=== Organizações ===\n"
        "1. Listar                2. Criar\n"
        "3. Editar                4. Excluir\n"
        "5. Listar integrantes    6. Adicionar integrante\n"
        "7. Editar afiliação     8. Remover afiliação\n"
        "0. Voltar"
    )
    def update_org() -> None:
        org = _choose(editor.list_organizations(), "uma organização")
        _edit_dataclass_interactive(editor, org, editor.update_organization)
    def delete_org() -> None:
        org = _choose(editor.list_organizations(), "uma organização")
        if _confirm_delete(org.name):
            editor.remove_organization(org.id)
    def update_member() -> None:
        m = _choose(editor.list_organization_memberships(), "uma afiliação")
        _edit_dataclass_interactive(editor, m, editor.update_organization_membership)
    _run_submenu(editor, {
        "1": lambda: _show_organizations(editor),
        "2": lambda: _create_organization_interactive(editor),
        "3": update_org, "4": delete_org,
        "5": lambda: _show_organization_members(editor),
        "6": lambda: _add_organization_member_interactive(editor),
        "7": update_member,
        "8": lambda: _remove_organization_member_interactive(editor),
    }, menu, autosave=autosave)


def _religion_console(editor: Editor, *, autosave: bool = False) -> None:
    menu = (
        "=== Religiões ===\n"
        " 1. Listar religiões      2. Criar religião\n"
        " 3. Editar religião      4. Excluir religião\n"
        " 5. Listar divindades    6. Criar divindade\n"
        " 7. Editar divindade    8. Excluir divindade\n"
        " 9. Associar divindade  10. Desassociar divindade\n"
        "11. Listar doutrinas    12. Criar doutrina\n"
        "13. Editar doutrina    14. Excluir doutrina\n"
        " 0. Voltar"
    )
    def update_religion() -> None:
        item = _choose(editor.list_religions(), "uma religião")
        _edit_dataclass_interactive(editor, item, editor.update_religion)
    def delete_religion() -> None:
        item = _choose(editor.list_religions(), "uma religião")
        if _confirm_delete(item.name):
            editor.remove_religion(item.id)
    def update_deity() -> None:
        item = _choose(editor.list_deities(), "uma divindade")
        _edit_dataclass_interactive(editor, item, editor.update_deity)
    def delete_deity() -> None:
        item = _choose(editor.list_deities(), "uma divindade")
        if _confirm_delete(item.name):
            editor.remove_deity(item.id)
    def update_doctrine() -> None:
        item = _choose(editor.list_doctrines(), "uma doutrina")
        _edit_dataclass_interactive(editor, item, editor.update_doctrine)
    def delete_doctrine() -> None:
        item = _choose(editor.list_doctrines(), "uma doutrina")
        if _confirm_delete(item.title):
            editor.remove_doctrine(item.id)
    _run_submenu(editor, {
        "1": lambda: _show_religions(editor),
        "2": lambda: _create_religion_interactive(editor),
        "3": update_religion, "4": delete_religion,
        "5": lambda: _show_deities(editor),
        "6": lambda: _create_deity_interactive(editor),
        "7": update_deity, "8": delete_deity,
        "9": lambda: _link_deity_interactive(editor),
        "10": lambda: _link_deity_interactive(editor, unlink=True),
        "11": lambda: _show_doctrines(editor),
        "12": lambda: _create_doctrine_interactive(editor),
        "13": update_doctrine, "14": delete_doctrine,
    }, menu, autosave=autosave)


def run_console(editor: Editor, *, autosave: bool = False) -> None:
    """Menu de terminal. Autosave requer um caminho de projeto previamente definido."""
    if not isinstance(editor, Editor):
        raise TypeError("editor deve ser Editor.")
    if type(autosave) is not bool:
        raise TypeError("autosave deve ser bool.")
    if autosave and editor.path is None:
        raise ValueError("Para salvamento automático, informe um caminho de arquivo.")
    actions = {
        "1": lambda: _show_characters(editor),
        "2": lambda: _create_person(editor),
        "3": lambda: _edit_person(editor),
        "4": lambda: _delete_person(editor),
        "5": lambda: _show_relationships(editor),
        "6": lambda: _create_relationship(editor),
        "7": lambda: _delete_relationship(editor),
        "8": lambda: _show_families(editor),
        "9": lambda: _create_family(editor),
        "10": lambda: _add_membership(editor),
        "11": lambda: _save_interactive(editor),
        "12": lambda: _export_interactive(editor),
        "13": lambda: _export_interactive(editor, svg=True),
        "14": lambda: _show_character_details(editor),
        "15": lambda: _edit_profile(editor, "physical"),
        "16": lambda: _edit_profile(editor, "personality"),
        "17": lambda: _edit_profile(editor, "social"),
        "18": lambda: _edit_history(editor),
        "19": lambda: _add_history_event_interactive(editor),
        "20": lambda: _remove_history_event_interactive(editor),
        "21": lambda: _organization_console(editor, autosave=autosave),
        "22": lambda: _religion_console(editor, autosave=autosave),
    }
    menu = (
        "\n=== Arconte | Editor de genealogias ===\n"
        " 1. Listar personagens       2. Criar personagem\n"
        " 3. Editar personagem        4. Excluir personagem\n"
        " 5. Listar vínculos         6. Criar vínculo\n"
        " 7. Remover vínculo         8. Listar famílias\n"
        " 9. Criar família          10. Vincular personagem à família\n"
        "11. Salvar projeto         12. Exportar HTML\n"
        "13. Exportar SVG           14. Ver ficha completa\n"
        "15. Editar físico          16. Editar personalidade\n"
        "17. Editar social          18. Editar história\n"
        "19. Adicionar acontecimento 20. Remover acontecimento\n"
        "21. Organizações          22. Religiões\n"
        " 0. Sair\n"
    )
    while True:
        print(menu)
        print(f"Projeto: {editor.project.name}{' *não salvo' if editor.is_dirty else ''}")
        try:
            command = _ask("Opção: ")
            if command == "0":
                if editor.is_dirty:
                    answer = _ask("Há alterações não salvas. Salvar antes de sair? [s/N/c]: ").lower()
                    if answer == "c":
                        continue
                    if answer == "s":
                        try:
                            _save_interactive(editor)
                        except (OSError, ValueError, TypeError, KeyError) as exc:
                            print(f"Erro ao salvar: {exc}. Saída cancelada.")
                            continue
                print("Até logo!")
                return
            action = actions.get(command)
            if action is None:
                print("Opção desconhecida.")
                continue
            try:
                action()
                if autosave and editor.is_dirty:
                    try:
                        saved = editor.save()
                        print(f"Salvamento automático: {saved}")
                    except (OSError, ValueError, TypeError, KeyError) as exc:
                        print(f"AVISO: salvamento automático falhou: {exc}")
                        print("Alterações não salvas; tente a opção 11 antes de sair.")
            except (OSError, ValueError, TypeError, KeyError) as exc:
                print(f"Não foi possível executar a operação: {exc}")
        except EOFError:
            print("\nEntrada encerrada.")
            if editor.is_dirty:
                print("ATENÇÃO: há alterações não salvas na memória.")
            return
        except KeyboardInterrupt:
            print("\nInterrompido.")
            if editor.is_dirty:
                print("O projeto possui alterações NÃO SALVAS.")
                try:
                    answer = _ask("Salvar antes de encerrar? [s/N]: ").lower()
                    if answer == "s":
                        try:
                            _save_interactive(editor)
                        except (OSError, ValueError, TypeError, KeyError) as exc:
                            print(f"Não foi possível salvar: {exc}")
                            print("Não foi possível preservar as alterações.")
                except (EOFError, KeyboardInterrupt):
                    print("Saindo sem salvar.")
            return


def main(argv: list[str] | None = None) -> int:
    """Permite executar o editor com ``python3 -m editor.editor``."""
    parser = argparse.ArgumentParser(description="Editor de genealogias do Arconte")
    parser.add_argument("--file", help="Arquivo de projeto JSON para abrir ou criar")
    parser.add_argument("--name", default="Novo projeto", help="Nome de um novo projeto")
    parser.add_argument("--autosave", action="store_true",
                        help="Salva automaticamente no arquivo definido com --file")
    args = parser.parse_args(argv)
    if args.autosave and args.file is None:
        parser.error("--autosave exige --file CAMINHO")
    if args.file is not None and Path(args.file).is_file():
        editor = Editor.open(args.file)
    else:
        editor = Editor.new(args.name, path=args.file)
    if args.autosave:
        run_console(editor, autosave=True)
    else:
        run_console(editor)
    return 0


__all__ = ["Editor", "run_console", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
