"""Projecao visual de genealogias do Arconte (sem interface ou dependencias externas).

O dominio genealogico e um grafo: casamentos e diferentes caminhos de
ancestralidade podem conectar os mesmos personagens. Este modulo NAO altera
personagens nem relacionamentos; apenas produz uma visao para desenhar.

Uso (a partir de ``backend/genealogy``)::

    from project.project import Project
    from tree.tree import TreeBuilder, layout_tree

    project = Project(name="Eldoria")
    graph = TreeBuilder(project).build()  # visao global
    graph = TreeBuilder(project).build(root_id=personagem.id,
                                      direction="descendants", max_generations=3)
    data = layout_tree(graph).to_dict()  # adequado para JSON / Flutter

Limitacoes do layout inicial: ele alinha personagens por camadas de filiacoes
(e aproxima pais de filhos por ordenacao baricentrica), mas nao garante que
casais fiquem sempre lado a lado nem minimiza globalmente os cruzamentos.
Vinculos de uniao sao arestas simetricas e nunca alteram a geracao biologica.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
import heapq
from statistics import mean
from typing import Iterable
from uuid import UUID

from character.character import Character
from genealogy.genealogy import Genealogy
from project.project import Project
from relationship.relationship import Relationship, RelationshipType

_PARENT_TYPES = frozenset(
    {RelationshipType.BIOLOGICAL_PARENT, RelationshipType.ADOPTIVE_PARENT}
)
_PARTNER_TYPES = frozenset({RelationshipType.MARRIAGE, RelationshipType.PARTNERSHIP})
_DIRECTIONS = frozenset({"all", "ancestors", "descendants"})


def _id_key(value: UUID) -> str:
    return str(value)


def _node_key(node: TreeNode) -> tuple[str, str]:
    return (node.full_name.casefold(), _id_key(node.id))


@dataclass(frozen=True, slots=True)
class TreeNode:
    """Dados básicos de um cartão de personagem, copiados do domínio."""

    id: UUID
    name: str
    surname: str | None
    gender: str | None
    birth_year: int | None
    death_year: int | None
    biography: str | None
    family_ids: tuple[UUID, ...] = ()

    @classmethod
    def from_character(
        cls, character: Character, *, family_ids: Iterable[UUID] = (),
    ) -> TreeNode:
        return cls(
            id=character.id, name=character.name, surname=character.surname,
            gender=character.gender, birth_year=character.birth_year,
            death_year=character.death_year, biography=character.biography,
            family_ids=tuple(sorted(set(family_ids), key=_id_key)),
        )

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}" if self.surname else self.name

    def to_dict(self) -> dict:
        return {
            "id": str(self.id), "name": self.name, "surname": self.surname,
            "full_name": self.full_name, "gender": self.gender,
            "birth_year": self.birth_year, "death_year": self.death_year,
            "biography": self.biography,
            "family_ids": [str(item) for item in self.family_ids],
        }


@dataclass(frozen=True, slots=True)
class TreeEdge:
    """Aresta original; parent -> child é dirigido, uniões são simétricas."""

    id: UUID
    source_id: UUID
    target_id: UUID
    type: RelationshipType

    @property
    def directed(self) -> bool:
        return self.type.is_directed

    @classmethod
    def from_relationship(cls, relation: Relationship) -> TreeEdge:
        return cls(relation.id, relation.source_id, relation.target_id, relation.type)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id), "source_id": str(self.source_id),
            "target_id": str(self.target_id), "type": self.type.value,
            "directed": self.directed,
        }


@dataclass(frozen=True, slots=True)
class TreeGraph:
    """Representação imutável do recorte da genealogia, sem coordenadas."""

    nodes: tuple[TreeNode, ...]
    edges: tuple[TreeEdge, ...]
    root_id: UUID | None
    direction: str

    def to_dict(self) -> dict:
        return {
            "root_id": str(self.root_id) if self.root_id else None,
            "direction": self.direction,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass(frozen=True, slots=True)
class TreePosition:
    character_id: UUID
    generation: int
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class TreeLayout:
    """Grafo original + coordenadas abstratas, sem depender do Flutter."""

    graph: TreeGraph
    positions: tuple[TreePosition, ...]
    width: float
    height: float

    def to_dict(self) -> dict:
        coords = {position.character_id: position for position in self.positions}
        graph_data = self.graph.to_dict()
        for node in graph_data["nodes"]:
            position = coords[UUID(node["id"])]
            node.update({
                "generation": position.generation,
                "x": position.x,
                "y": position.y,
            })
        graph_data["layout"] = {"width": self.width, "height": self.height}
        return graph_data


class TreeBuilder:
    """Seleciona personagens e arestas a partir de Project ou Genealogy.

    Sem ``root_id``: gera todos os personagens (inclusive isolados) e arestas;
    ``direction`` deve ser ``all`` e ``max_generations`` deve ser None.

    Com ``root_id``:
    - ``ancestors``/``descendants``: percorre apenas filiacoes no sentido
      escolhido. ``max_generations`` conta passos de filiação, sendo 0 a raiz.
      Se ``include_partners`` for True, adiciona um grau de parceiros dos
      personagens encontrados, sem percorrer as familias desses parceiros.
    - ``all``: percorre o componente conexo da raiz, considerando filiacoes
      nos dois sentidos e unioes (se habilitadas). ``max_generations`` limita
      o numero de arestas percorridas, seja filiação ou uniao.

    Um filtro de filiação afeta tanto a busca quanto as arestas exibidas.
    """

    def __init__(self, source: Project | Genealogy) -> None:
        if isinstance(source, Project):
            self._project: Project | None = source
            self._genealogy = source.genealogy
        elif isinstance(source, Genealogy):
            self._project = None
            self._genealogy = source
        else:
            raise TypeError("source deve ser Project ou Genealogy.")

    def build(
        self,
        *,
        root_id: UUID | None = None,
        direction: str = "all",
        max_generations: int | None = None,
        include_partners: bool = True,
        parent_types: Iterable[RelationshipType] | None = None,
    ) -> TreeGraph:
        if not isinstance(direction, str) or direction not in _DIRECTIONS:
            raise ValueError("direction deve ser 'all', 'ancestors' ou 'descendants'.")
        if type(include_partners) is not bool:
            raise TypeError("include_partners deve ser bool.")
        if max_generations is not None and (
            type(max_generations) is not int or max_generations < 0
        ):
            raise ValueError("max_generations deve ser inteiro nao negativo ou None.")
        if root_id is not None and not isinstance(root_id, UUID):
            raise TypeError("root_id deve ser UUID ou None.")
        if root_id is None and (direction != "all" or max_generations is not None):
            raise ValueError("Um recorte por direcao/profundidade exige root_id.")
        if root_id is not None:
            self._genealogy.get_character(root_id)  # KeyError se ausente

        if parent_types is None:
            types = _PARENT_TYPES
        else:
            try:
                types = frozenset(parent_types)
            except TypeError as exc:
                raise TypeError("parent_types deve ser iteravel de RelationshipType.") from exc
            if not all(isinstance(item, RelationshipType) for item in types):
                raise TypeError("parent_types deve conter somente RelationshipType.")
            if not types <= _PARENT_TYPES:
                raise ValueError("parent_types aceita apenas tipos de filiacao.")

        # Consulta apenas dados publicos. A validacao detecta referencias de
        # familias que possam ter ficado orfas por alteracoes diretas.
        if self._project is not None:
            self._project.validate_integrity()
        characters = {c.id: c for c in self._genealogy.get_all_characters()}
        relationships = tuple(
            rel for rel in self._genealogy.get_relationships()
            if rel.type in types or (include_partners and rel.type in _PARTNER_TYPES)
        )

        parents: dict[UUID, set[UUID]] = defaultdict(set)
        children: dict[UUID, set[UUID]] = defaultdict(set)
        adjacent: dict[UUID, set[UUID]] = defaultdict(set)
        partners: dict[UUID, set[UUID]] = defaultdict(set)
        for rel in relationships:
            a, b = rel.source_id, rel.target_id
            adjacent[a].add(b)
            adjacent[b].add(a)
            if rel.type in _PARENT_TYPES:
                parents[b].add(a)
                children[a].add(b)
            else:
                partners[a].add(b)
                partners[b].add(a)

        if root_id is None:
            selected = set(characters)
        elif direction == "all":
            selected = self._walk(root_id, adjacent, max_generations)
        else:
            adjacency = parents if direction == "ancestors" else children
            selected = self._walk(root_id, adjacency, max_generations)
            if include_partners:
                for character_id in tuple(selected):
                    selected.update(partners[character_id])

        nodes = []
        for character_id in selected:
            member_family_ids: tuple[UUID, ...] = ()
            if self._project is not None:
                member_family_ids = tuple(
                    family.id for family in self._project.families.get_families_for_character(
                        character_id
                    )
                )
            nodes.append(TreeNode.from_character(
                characters[character_id], family_ids=member_family_ids,
            ))
        nodes.sort(key=_node_key)
        edges = sorted(
            (
                TreeEdge.from_relationship(rel) for rel in relationships
                if rel.source_id in selected and rel.target_id in selected
            ),
            key=lambda e: (e.type.value, _id_key(e.source_id),
                           _id_key(e.target_id), _id_key(e.id)),
        )
        return TreeGraph(tuple(nodes), tuple(edges), root_id, direction)

    @staticmethod
    def _walk(
        root_id: UUID, adjacent: dict[UUID, set[UUID]], limit: int | None,
    ) -> set[UUID]:
        distances = {root_id: 0}
        queue = deque([root_id])
        while queue:
            current = queue.popleft()
            if limit is not None and distances[current] >= limit:
                continue
            for neighbor in sorted(adjacent[current], key=_id_key):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return set(distances)


def layout_tree(
    graph: TreeGraph, *,
    horizontal_spacing: float = 240.0,
    vertical_spacing: float = 170.0,
    passes: int = 4,
) -> TreeLayout:
    """Organiza nos por geracao usando ordem topologica e heuristica local.

    Todas as arestas de filiacao descem pelo menos uma camada; unioes nao
    impõem ascendencia. Pais que compartilham filhos tendem a ficar proximos.
    A ordem e deterministica para o mesmo grafo; nao e um layout otimo.

    Espacamentos sao unidades abstratas (tipicamente pixels no Flutter).
    """
    if not isinstance(graph, TreeGraph):
        raise TypeError("graph deve ser TreeGraph.")
    for key, value in (
        ("horizontal_spacing", horizontal_spacing),
        ("vertical_spacing", vertical_spacing),
    ):
        if type(value) not in (float, int) or not (0 < value < float("inf")):
            raise ValueError(f"{key} deve ser numero positivo e finito.")
    if type(passes) is not int or passes < 0:
        raise ValueError("passes deve ser inteiro nao negativo.")

    if not graph.nodes:
        return TreeLayout(graph, (), 0.0, 0.0)

    nodes = {node.id: node for node in graph.nodes}
    if len(nodes) != len(graph.nodes):
        raise ValueError("TreeGraph possui UUID de personagem duplicado.")
    parents: dict[UUID, set[UUID]] = {key: set() for key in nodes}
    children: dict[UUID, set[UUID]] = {key: set() for key in nodes}
    for edge in graph.edges:
        if edge.source_id not in nodes or edge.target_id not in nodes:
            raise ValueError("Aresta referencia personagem ausente do TreeGraph.")
        if edge.type in _PARENT_TYPES:
            parents[edge.target_id].add(edge.source_id)
            children[edge.source_id].add(edge.target_id)

    # Ordenacao topologica assegura que um filho apareca abaixo de todos os
    # pais selecionados, mesmo com multiplos caminhos de ascendencia.
    indegree = {key: len(value) for key, value in parents.items()}
    queue = [(_node_key(nodes[key]), key) for key, degree in indegree.items() if degree == 0]
    heapq.heapify(queue)
    generation = {key: 0 for key in nodes}
    processed = 0
    while queue:
        _, current = heapq.heappop(queue)
        processed += 1
        for child in sorted(children[current], key=lambda key: _node_key(nodes[key])):
            generation[child] = max(generation[child], generation[current] + 1)
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(queue, (_node_key(nodes[child]), child))
    if processed != len(nodes):
        raise ValueError("Ciclo detectado nas filiações do TreeGraph.")

    if graph.root_id in generation:
        offset = generation[graph.root_id]
        generation = {key: value - offset for key, value in generation.items()}

    layers: dict[int, list[UUID]] = defaultdict(list)
    for key, layer in generation.items():
        layers[layer].append(key)
    for ids in layers.values():
        ids.sort(key=lambda key: _node_key(nodes[key]))

    # Barycenter pass: ordena segundo a posicao media dos pais ou filhos.
    # Empates e nos desconectados mantem a ordem anterior, garantindo
    # repetibilidade e evitando que as iteracoes oscilem desnecessariamente.
    for _ in range(passes):
        for levels, contacts in (
            (sorted(layers), parents), (sorted(layers, reverse=True), children),
        ):
            index = {key: rank for layer in layers.values() for rank, key in enumerate(layer)}
            for layer in levels:
                current_order = {key: index[key] for key in layers[layer]}

                def sort_key(key: UUID) -> tuple[float, int, str]:
                    neighbors = [index[n] for n in contacts[key] if n in index]
                    bary = mean(neighbors) if neighbors else current_order[key]
                    return (float(bary), current_order[key], _id_key(key))

                layers[layer].sort(key=sort_key)
                for rank, key in enumerate(layers[layer]):
                    index[key] = rank

    min_layer = min(layers)
    positions = tuple(
        TreePosition(
            character_id=key,
            generation=generation[key],
            x=(rank + 0.5) * float(horizontal_spacing),
            y=(layer - min_layer + 0.5) * float(vertical_spacing),
        )
        for layer in sorted(layers)
        for rank, key in enumerate(layers[layer])
    )
    return TreeLayout(
        graph=graph,
        positions=positions,
        width=max(len(layer) for layer in layers.values()) * float(horizontal_spacing),
        height=(max(layers) - min_layer + 1) * float(vertical_spacing),
    )


__all__ = [
    "TreeNode", "TreeEdge", "TreeGraph", "TreePosition", "TreeLayout",
    "TreeBuilder", "layout_tree",
]
