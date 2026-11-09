"""Núcleo de genealogias do Arconte.

Gerencia personagens e relacionamentos exclusivamente em memória, sem
banco de dados, interface gráfica ou dependências externas.

Execute a partir da pasta ``backend/genealogy`` (raiz dos módulos irmãos):

    from character.character import Character
    from relationship.relationship import Relationship, RelationshipType
    from genealogy.genealogy import Genealogy

As regras de parentesco consideram somente filiações cadastradas. Assim,
um parentesco desconhecido não é necessariamente inexistente. Casamentos
não criam vínculos de ancestralidade.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from character.character import Character
from relationship.relationship import Relationship, RelationshipType


_PARENT_TYPES = frozenset(
    {RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT}
)
_PARTNER_TYPES = frozenset({RelationshipType.MARRIAGE, RelationshipType.PARTNERSHIP})


@dataclass(frozen=True, slots=True)
class Kinship:
    """Descrição estrutural do parentesco do primeiro personagem com o segundo.

    ``relation`` é um dos valores: self, ancestor, descendant, sibling,
    aunt_uncle, niece_nephew, cousin ou unknown.

    ``generation_distance`` é preenchida para ancestralidade direta.
    ``cousin_degree`` e ``removed`` descrevem primos (1 = primos de 1º grau).
    ``common_ancestor_ids`` registra os ancestrais mais próximos encontrados.

    É possível haver mais de um caminho de parentesco entre duas pessoas.
    Nesse caso, esta classe descreve um dos vínculos mais próximos.
    """

    relation: str
    generation_distance: int | None = None
    cousin_degree: int | None = None
    removed: int | None = None
    common_ancestor_ids: tuple[UUID, ...] = ()


class Genealogy:
    """Coleção de personagens e relações, com validações de consistência.

    - IDs UUID referenciam personagens de forma estável.
    - Filiação é dirigida (responsável -> filho); casamentos são simétricos.
    - Ciclos de filiação são proibidos, inclusive com filiações adotivas.
    - Não há limites impostos a famílias, idades ou números de parceiros.
    - Alterações são feitas pelos métodos públicos para manter os índices.
    """

    def __init__(self) -> None:
        self._characters: dict[UUID, Character] = {}
        self._relationships: dict[UUID, Relationship] = {}
        self._relationships_by_character: dict[UUID, set[UUID]] = {}
        self._parents: dict[UUID, set[UUID]] = {}
        self._children: dict[UUID, set[UUID]] = {}
        # Várias filiações (biológica/adotiva) podem ligar o mesmo par.
        self._parent_edges: dict[tuple[UUID, UUID], set[UUID]] = {}

    # ------------------------------------------------------------------
    # Personagens
    # ------------------------------------------------------------------
    def add_character(self, character: Character) -> None:
        """Adiciona um personagem; IDs repetidos geram ValueError."""
        if not isinstance(character, Character):
            raise TypeError("character deve ser um Character.")
        if character.id in self._characters:
            raise ValueError("Já existe um personagem com esse id.")
        self._characters[character.id] = character
        self._relationships_by_character[character.id] = set()
        self._parents[character.id] = set()
        self._children[character.id] = set()

    def update_character(self, character: Character) -> None:
        """Substitui um personagem existente pelo mesmo UUID.

        Use ``dataclasses.replace(personagem, campo=valor)`` para produzir
        a versão atualizada sem modificar a entidade imutável original.
        """
        if not isinstance(character, Character):
            raise TypeError("character deve ser um Character.")
        self._require_character(character.id)
        self._characters[character.id] = character

    def get_character(self, character_id: UUID) -> Character:
        """Consulta personagem pelo UUID; lança KeyError se não existir."""
        self._require_character(character_id)
        return self._characters[character_id]

    def get_all_characters(self) -> tuple[Character, ...]:
        """Retorna todos os personagens, ordenados pelo nome completo."""
        return self._ordered_characters(self._characters)

    def remove_character(self, character_id: UUID) -> Character:
        """Remove o personagem e todas as suas relações (cascata)."""
        self._require_character(character_id)
        for rel_id in tuple(self._relationships_by_character[character_id]):
            self.remove_relationship(rel_id)
        self._relationships_by_character.pop(character_id)
        self._parents.pop(character_id)
        self._children.pop(character_id)
        return self._characters.pop(character_id)

    # ------------------------------------------------------------------
    # Relações
    # ------------------------------------------------------------------
    def add_relationship(self, relationship: Relationship) -> None:
        """Insere uma relação, impedindo duplicatas e ciclos genealógicos.

        A mesma dupla pode casar-se mais de uma vez, desde que os registros
        não sejam exatamente iguais (por exemplo, datas diferentes).
        """
        if not isinstance(relationship, Relationship):
            raise TypeError("relationship deve ser um Relationship.")
        source, target = relationship.source_id, relationship.target_id
        self._require_character(source)
        self._require_character(target)

        if relationship.id in self._relationships:
            raise ValueError("Já existe uma relação com esse id.")

        # A classe Relationship já normaliza a ordem de relações simétricas.
        for rel_id in self._relationships_by_character[source]:
            existing = self._relationships[rel_id]
            if (
                existing.source_id == source
                and existing.target_id == target
                and existing.type == relationship.type
                and existing.start_year == relationship.start_year
                and existing.end_year == relationship.end_year
            ):
                raise ValueError("Essa relação já foi cadastrada.")

        if relationship.type in _PARENT_TYPES and self._has_lineage_path(
            start=target, destination=source
        ):
            raise ValueError("Essa filiação produziria um ciclo genealógico.")

        self._relationships[relationship.id] = relationship
        self._relationships_by_character[source].add(relationship.id)
        self._relationships_by_character[target].add(relationship.id)

        if relationship.type in _PARENT_TYPES:
            pair = (source, target)
            self._parent_edges.setdefault(pair, set()).add(relationship.id)
            self._children[source].add(target)
            self._parents[target].add(source)

    def get_relationship(self, relationship_id: UUID) -> Relationship:
        """Consulta relação pelo UUID; lança KeyError se não existir."""
        self._require_uuid(relationship_id, "relationship_id")
        return self._relationships[relationship_id]

    def get_relationships(
        self,
        character_id: UUID | None = None,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Relationship, ...]:
        """Lista relações, opcionalmente por personagem e/ou tipo."""
        selected_types = self._normalize_types(types)
        if character_id is None:
            candidates = self._relationships.values()
        else:
            self._require_character(character_id)
            candidates = (
                self._relationships[rel_id]
                for rel_id in self._relationships_by_character[character_id]
            )
        return tuple(
            sorted(
                (r for r in candidates if selected_types is None or r.type in selected_types),
                key=lambda r: (r.type.value, r.start_year is None,
                               r.start_year if r.start_year is not None else 0,
                               str(r.id)),
            )
        )

    def remove_relationship(self, relationship_id: UUID) -> Relationship:
        """Remove uma relação, preservando outras conexões do mesmo par."""
        self._require_uuid(relationship_id, "relationship_id")
        relationship = self._relationships.pop(relationship_id)
        source, target = relationship.source_id, relationship.target_id
        self._relationships_by_character[source].remove(relationship_id)
        self._relationships_by_character[target].remove(relationship_id)

        if relationship.type in _PARENT_TYPES:
            pair = (source, target)
            remaining = self._parent_edges[pair]
            remaining.remove(relationship_id)
            if not remaining:
                del self._parent_edges[pair]
                self._children[source].remove(target)
                self._parents[target].remove(source)
        return relationship

    # ------------------------------------------------------------------
    # Consultas genealógicas
    # ------------------------------------------------------------------
    def get_parents(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Pais/responsáveis registrados, biológicos e/ou adotivos."""
        self._require_character(character_id)
        chosen = self._normalize_parent_types(types)
        return self._ordered_characters(self._neighbors(character_id, True, chosen))

    def get_children(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Filhos registrados, biológicos e/ou adotivos."""
        self._require_character(character_id)
        chosen = self._normalize_parent_types(types)
        return self._ordered_characters(self._neighbors(character_id, False, chosen))

    def get_siblings(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Pessoas com ao menos um responsável parental em comum."""
        self._require_character(character_id)
        chosen = self._normalize_parent_types(types)
        sibling_ids: set[UUID] = set()
        for parent_id in self._neighbors(character_id, True, chosen):
            sibling_ids.update(self._neighbors(parent_id, False, chosen))
        sibling_ids.discard(character_id)
        return self._ordered_characters(sibling_ids)

    def get_ancestors(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Ancestrais ordenados por geração (mais próximos primeiro)."""
        distances = self._lineage_distances(character_id, upward=True, types=types)
        del distances[character_id]
        return self._ordered_by_distance(distances)

    def get_descendants(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Descendentes ordenados por geração (mais próximos primeiro)."""
        distances = self._lineage_distances(character_id, upward=False, types=types)
        del distances[character_id]
        return self._ordered_by_distance(distances)

    def get_common_ancestors(
        self,
        first_id: UUID,
        second_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Ancestrais de ambos, priorizando a menor distância combinada."""
        first = self._lineage_distances(first_id, upward=True, types=types)
        second = self._lineage_distances(second_id, upward=True, types=types)
        first.pop(first_id)
        second.pop(second_id)
        ids = set(first) & set(second)
        return tuple(
            self._characters[cid]
            for cid in sorted(
                ids,
                key=lambda cid: (first[cid] + second[cid],
                                 max(first[cid], second[cid]),
                                 self._character_sort_key(cid)),
            )
        )

    def get_partners(
        self,
        character_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> tuple[Character, ...]:
        """Todos os parceiros registrados, inclusive vínculos encerrados."""
        self._require_character(character_id)
        chosen = self._normalize_types(types)
        if chosen is None:
            chosen = _PARTNER_TYPES
        if not chosen <= _PARTNER_TYPES:
            raise ValueError("types aceita apenas MARRIAGE e PARTNERSHIP.")
        partners: set[UUID] = set()
        for rel_id in self._relationships_by_character[character_id]:
            rel = self._relationships[rel_id]
            if rel.type in chosen:
                partners.add(rel.target_id if rel.source_id == character_id else rel.source_id)
        return self._ordered_characters(partners)

    def get_kinship(
        self,
        first_id: UUID,
        second_id: UUID,
        *,
        types: Iterable[RelationshipType] | None = None,
    ) -> Kinship:
        """Identifica um parentesco próximo derivado exclusivamente da filiação.

        Quando múltiplos vínculos coexistem, privilegia o caminho com menor
        soma de gerações até um ancestral comum. Para informações completas,
        consulte ``get_common_ancestors``. ``unknown`` significa que nenhum
        parentesco foi encontrado nos registros disponíveis.
        """
        self._require_character(first_id)
        self._require_character(second_id)
        self._normalize_parent_types(types)
        if first_id == second_id:
            return Kinship(relation="self")

        first = self._lineage_distances(first_id, upward=True, types=types)
        second = self._lineage_distances(second_id, upward=True, types=types)
        if first_id in second:
            return Kinship("ancestor", generation_distance=second[first_id])
        if second_id in first:
            return Kinship("descendant", generation_distance=first[second_id])

        common = (set(first) & set(second)) - {first_id, second_id}
        if not common:
            return Kinship(relation="unknown")

        distance_pair = min(
            ((first[ancestor], second[ancestor]) for ancestor in common),
            key=lambda pair: (sum(pair), max(pair), pair),
        )
        # Distingue parentescos mais próximos em caso de múltiplos caminhos.
        a, b = distance_pair
        closest = tuple(sorted(
            (ancestor for ancestor in common
             if (first[ancestor], second[ancestor]) == distance_pair),
            key=str,
        ))
        if (a, b) == (1, 1):
            return Kinship("sibling", common_ancestor_ids=closest)
        if a == 1:
            return Kinship("aunt_uncle", removed=b - 2,
                           common_ancestor_ids=closest)
        if b == 1:
            return Kinship("niece_nephew", removed=a - 2,
                           common_ancestor_ids=closest)
        return Kinship("cousin", cousin_degree=min(a, b) - 1,
                       removed=abs(a - b), common_ancestor_ids=closest)

    # ------------------------------------------------------------------
    # Implementação privada
    # ------------------------------------------------------------------
    @staticmethod
    def _require_uuid(value: UUID, name: str) -> None:
        if not isinstance(value, UUID):
            raise TypeError(f"{name} deve ser um UUID.")

    def _require_character(self, character_id: UUID) -> None:
        self._require_uuid(character_id, "character_id")
        if character_id not in self._characters:
            raise KeyError(f"Personagem não encontrado: {character_id}")

    @staticmethod
    def _normalize_types(
        types: Iterable[RelationshipType] | None,
    ) -> frozenset[RelationshipType] | None:
        if types is None:
            return None
        try:
            normalized = frozenset(types)
        except TypeError as exc:
            raise TypeError("types deve ser iterável de RelationshipType.") from exc
        if not all(isinstance(t, RelationshipType) for t in normalized):
            raise TypeError("types deve conter apenas RelationshipType.")
        return normalized

    @classmethod
    def _normalize_parent_types(
        cls, types: Iterable[RelationshipType] | None,
    ) -> frozenset[RelationshipType]:
        chosen = cls._normalize_types(types)
        if chosen is None:
            return _PARENT_TYPES
        if not chosen <= _PARENT_TYPES:
            raise ValueError("types aceita apenas BIOLOGICAL_PARENT e ADOPTIVE_PARENT.")
        return chosen

    def _character_sort_key(self, character_id: UUID) -> tuple[str, str]:
        return (self._characters[character_id].full_name.casefold(), str(character_id))

    def _ordered_characters(self, ids: Iterable[UUID]) -> tuple[Character, ...]:
        return tuple(self._characters[cid] for cid in sorted(ids, key=self._character_sort_key))

    def _ordered_by_distance(self, distances: dict[UUID, int]) -> tuple[Character, ...]:
        return tuple(
            self._characters[cid]
            for cid in sorted(distances, key=lambda cid: (
                distances[cid], self._character_sort_key(cid)
            ))
        )

    def _neighbors(
        self, character_id: UUID, upward: bool,
        types: frozenset[RelationshipType],
    ) -> set[UUID]:
        if types == _PARENT_TYPES:
            return self._parents[character_id] if upward else self._children[character_id]
        result: set[UUID] = set()
        for rel_id in self._relationships_by_character[character_id]:
            rel = self._relationships[rel_id]
            if rel.type not in types:
                continue
            if upward and rel.target_id == character_id:
                result.add(rel.source_id)
            elif not upward and rel.source_id == character_id:
                result.add(rel.target_id)
        return result

    def _lineage_distances(
        self, character_id: UUID, *, upward: bool,
        types: Iterable[RelationshipType] | None,
    ) -> dict[UUID, int]:
        self._require_character(character_id)
        chosen = self._normalize_parent_types(types)
        distances = {character_id: 0}
        queue = deque([character_id])
        while queue:
            current = queue.popleft()
            for neighbor in self._neighbors(current, upward, chosen):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _has_lineage_path(self, *, start: UUID, destination: UUID) -> bool:
        """Procura caminho de filiação, usando índice atualizado de filhos."""
        seen = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current == destination:
                return True
            for child in self._children[current]:
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return False
