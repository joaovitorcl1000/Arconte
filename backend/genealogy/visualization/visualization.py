"""Exportação SVG das árvores genealógicas do Arconte.

Este módulo *não* calcula parentescos, não altera projetos e não depende de
Flutter ou de bibliotecas externas. Recebe um ``TreeLayout`` criado por
``tree.layout_tree`` e desenha os personagens e os vínculos em SVG.

Exemplo (executar na pasta backend/genealogy)::

    from project.project import Project
    from tree.tree import TreeBuilder, layout_tree
    from visualization.visualization import save_svg

    project = Project.load('data/eldoria.json')
    layout = layout_tree(TreeBuilder(project).build())
    save_svg(layout, 'data/eldoria.svg')

Limitação: o layout é produzido por ``tree.py``, cuja heurística não garante
que todos os casais fiquem lado a lado ou que não existam cruzamentos.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import os
from os import PathLike
from pathlib import Path
import tempfile
from typing import Iterable
from uuid import UUID
import xml.etree.ElementTree as ET

from relationship.relationship import RelationshipType
from tree.tree import TreeEdge, TreeLayout, TreeNode, TreePosition


_SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _SVG_NS)

_COLOR_BACKGROUND = "#f4f7fb"
_COLOR_TEXT = "#172943"
_COLOR_MUTED = "#60718a"
_COLOR_BORDER = "#d7e0eb"
_COLOR_PARENT = "#3a6ea5"
_COLOR_ADOPTION = "#168973"
_COLOR_MARRIAGE = "#9c61aa"
_COLOR_PARTNERSHIP = "#c78c42"


def _svg(tag: str) -> str:
    return f"{{{_SVG_NS}}}{tag}"


def _valid_xml_text(value: str, label: str) -> str:
    """Não produza SVG inválido mesmo quando o nome é dado pelo usuário."""
    if not isinstance(value, str):
        raise TypeError(f"{label} deve ser uma string.")
    for character in value:
        code = ord(character)
        if not (
            code in (0x09, 0x0A, 0x0D)
            or 0x20 <= code <= 0xD7FF
            or 0xE000 <= code <= 0xFFFD
            or 0x10000 <= code <= 0x10FFFF
        ):
            raise ValueError(f"{label} contém caracteres inválidos em XML.")
    return value


def _positive_number(value: object, field: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} deve ser um número positivo e finito.")
    return float(value)


def _n(value: float) -> str:
    """Representação determinística de coordenadas SVG, sem -0."""
    return f"{0.0 if value == 0 else value:.2f}"


def _elem(parent: ET.Element, name: str, **attrs: object) -> ET.Element:
    return ET.SubElement(parent, _svg(name), {k.replace("_", "-"): str(v) for k, v in attrs.items()})


def _label(parent: ET.Element, text: str, *, x: float, y: float, **attrs: object) -> ET.Element:
    node = _elem(parent, "text", x=_n(x), y=_n(y), **attrs)
    node.text = _valid_xml_text(text, "texto")
    return node


@dataclass(frozen=True, slots=True, kw_only=True)
class SvgOptions:
    """Ajustes de apresentação. Coordenadas e dados vêm exclusivamente de tree.py."""

    title: str = "Árvore genealógica"
    card_width: float = 196.0
    card_height: float = 98.0
    padding: float = 60.0
    show_years: bool = True
    show_legend: bool = True

    def __post_init__(self) -> None:
        _valid_xml_text(self.title, "title")
        if not self.title.strip():
            raise ValueError("title não pode estar vazio.")
        for field in ("card_width", "card_height", "padding"):
            _positive_number(getattr(self, field), field)
        for field in ("show_years", "show_legend"):
            if type(getattr(self, field)) is not bool:
                raise TypeError(f"{field} deve ser bool.")


def _checked_positions(layout: TreeLayout) -> dict[UUID, TreePosition]:
    """Valida layout inteiro antes de gerar a primeira linha do documento."""
    if not isinstance(layout, TreeLayout):
        raise TypeError("layout deve ser TreeLayout.")
    for field in ("width", "height"):
        value = getattr(layout, field)
        if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
            raise ValueError(f"layout.{field} deve ser finito e não negativo.")

    nodes = layout.graph.nodes
    node_ids: set[UUID] = set()
    for node in nodes:
        if not isinstance(node, TreeNode) or not isinstance(node.id, UUID):
            raise TypeError("layout contém TreeNode inválido.")
        if node.id in node_ids:
            raise ValueError("Personagem duplicado no layout.")
        node_ids.add(node.id)
        _valid_xml_text(node.full_name, "nome do personagem")
        for field in ("biography", "gender"):
            raw = getattr(node, field)
            if raw is not None:
                _valid_xml_text(raw, field)

    positions: dict[UUID, TreePosition] = {}
    for position in layout.positions:
        if not isinstance(position, TreePosition) or not isinstance(position.character_id, UUID):
            raise TypeError("layout contém TreePosition inválida.")
        if position.character_id in positions:
            raise ValueError("Posição duplicada para o mesmo personagem.")
        if type(position.generation) is not int:
            raise TypeError("generation deve ser inteiro.")
        if not all(type(value) in (float, int) and math.isfinite(value)
                   for value in (position.x, position.y)):
            raise ValueError("Posições devem conter coordenadas finitas.")
        positions[position.character_id] = position
    if set(positions) != node_ids:
        raise ValueError("Cada personagem precisa de exatamente uma posição.")

    seen_edges: set[UUID] = set()
    for edge in layout.graph.edges:
        if not isinstance(edge, TreeEdge) or not isinstance(edge.type, RelationshipType):
            raise TypeError("layout contém TreeEdge inválida.")
        if edge.id in seen_edges:
            raise ValueError("Relação duplicada no layout.")
        seen_edges.add(edge.id)
        if edge.source_id not in positions or edge.target_id not in positions:
            raise ValueError("Relação referencia personagem ausente.")
    if not nodes and layout.graph.edges:
        raise ValueError("Grafo vazio não pode ter arestas.")
    return positions


def _edge_styles(kind: RelationshipType) -> tuple[str, str | None]:
    if kind is RelationshipType.BIOLOGICAL_PARENT:
        return _COLOR_PARENT, None
    if kind is RelationshipType.ADOPTIVE_PARENT:
        return _COLOR_ADOPTION, "7 6"
    if kind is RelationshipType.MARRIAGE:
        return _COLOR_MARRIAGE, None
    if kind is RelationshipType.PARTNERSHIP:
        return _COLOR_PARTNERSHIP, "3 5"
    raise ValueError(f"Tipo de relação não suportado: {kind!r}.")


def _path_for_edge(
    edge: TreeEdge,
    points: dict[UUID, tuple[float, float]],
    options: SvgOptions,
    *, offset: float = 0.0,
) -> str:
    x1, y1 = points[edge.source_id]
    x2, y2 = points[edge.target_id]
    if edge.type.is_directed:
        # Parent -> child: saída inferior do cartão e entrada superior do filho.
        x1 += offset
        x2 += offset
        start = y1 + options.card_height / 2
        end = y2 - options.card_height / 2
        middle = (start + end) / 2
        return (f"M {_n(x1)} {_n(start)} V {_n(middle)} "
                f"H {_n(x2)} V {_n(end)}")

    # União simétrica: saída pelas laterais, independente da ordem dos UUIDs.
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    if abs(x1 - x2) < 1e-9:
        # Casal alinhado na mesma coluna, em níveis distintos.
        if y1 > y2:
            y1, y2 = y2, y1
        start = y1 + options.card_height / 2
        end = y2 - options.card_height / 2
        return (f"M {_n(x1 + offset)} {_n(start)} "
                f"L {_n(x2 + offset)} {_n(end)}")
    start_x = x1 + options.card_width / 2
    end_x = x2 - options.card_width / 2
    y1 += offset
    y2 += offset
    mid_x = (start_x + end_x) / 2
    return (f"M {_n(start_x)} {_n(y1)} "
            f"C {_n(mid_x)} {_n(y1)}, {_n(mid_x)} {_n(y2)}, "
            f"{_n(end_x)} {_n(y2)}")


def _draw_edges(
    group: ET.Element, layout: TreeLayout,
    points: dict[UUID, tuple[float, float]], options: SvgOptions,
) -> None:
    # Vários vínculos entre o mesmo par têm trajetórias ligeiramente distintas.
    groups: dict[tuple[UUID, UUID, bool], list[TreeEdge]] = defaultdict(list)
    for edge in layout.graph.edges:
        pair = (edge.source_id, edge.target_id) if edge.type.is_directed else tuple(
            sorted((edge.source_id, edge.target_id), key=str)
        )
        groups[(pair[0], pair[1], edge.type.is_directed)].append(edge)
    for edges in groups.values():
        edges.sort(key=lambda edge: (edge.type.value, str(edge.id)))
        for index, edge in enumerate(edges):
            offset = (index - (len(edges) - 1) / 2) * 9
            color, dash = _edge_styles(edge.type)
            attrs: dict[str, object] = {
                "d": _path_for_edge(edge, points, options, offset=offset),
                "fill": "none",
                "stroke": color,
                "stroke_width": "2.6",
                "stroke_linejoin": "round",
                "stroke_linecap": "round",
                "vector_effect": "non-scaling-stroke",
                "data_edge_id": str(edge.id),
                "data_relation": edge.type.value,
                "data_source": str(edge.source_id),
                "data_target": str(edge.target_id),
                "data_directed": str(edge.directed).lower(),
            }
            if dash:
                attrs["stroke_dasharray"] = dash
            path = _elem(group, "path", **attrs)
            _elem(path, "title").text = (
                f"{edge.type.value}: {edge.source_id} → {edge.target_id}"
            )


def _years(node: TreeNode) -> str | None:
    if node.birth_year is not None and node.death_year is not None:
        return f"{node.birth_year} — {node.death_year}"
    if node.birth_year is not None:
        return f"Nasc. {node.birth_year}"
    if node.death_year is not None:
        return f"Falec. {node.death_year}"
    return None


def _draw_nodes(
    group: ET.Element, layout: TreeLayout,
    points: dict[UUID, tuple[float, float]], options: SvgOptions,
) -> None:
    half_w, half_h = options.card_width / 2, options.card_height / 2
    for node in layout.graph.nodes:
        cx, cy = points[node.id]
        top = cy - half_h
        left = cx - half_w
        card = _elem(group, "g", data_character_id=str(node.id), data_role="character")
        hint = node.full_name
        if node.biography:
            hint = f"{hint}\n{node.biography}"
        _elem(card, "title").text = hint
        _elem(card, "rect", x=_n(left), y=_n(top),
              width=_n(options.card_width), height=_n(options.card_height),
              rx="15", fill="#ffffff", stroke=_COLOR_BORDER,
              stroke_width="1.3", filter="url(#card-shadow)")
        _elem(card, "rect", x=_n(left), y=_n(top + 14), width="4",
              height=_n(options.card_height - 28), rx="2", fill=_COLOR_PARENT)
        name = _label(card, node.full_name, x=cx, y=cy - 11,
                      text_anchor="middle", fill=_COLOR_TEXT, font_size="16",
                      font_weight="650", font_family="system-ui, Arial, sans-serif")
        if len(node.full_name) > max(8, int((options.card_width - 25) / 9)):
            name.set("textLength", _n(options.card_width - 25))
            name.set("lengthAdjust", "spacingAndGlyphs")
        years = _years(node) if options.show_years else None
        if years:
            _label(card, years, x=cx, y=cy + 17, text_anchor="middle",
                   fill=_COLOR_MUTED, font_size="12",
                   font_family="system-ui, Arial, sans-serif")
        elif node.family_ids:
            _label(card, "Membro de organização", x=cx, y=cy + 17,
                   text_anchor="middle", fill=_COLOR_MUTED, font_size="11",
                   font_family="system-ui, Arial, sans-serif")
        if node.family_ids:
            _elem(card, "circle", cx=_n(left + options.card_width - 14),
                  cy=_n(top + 14), r="5", fill="#d4a84e")


def _draw_legend(
    parent: ET.Element, x: float, y: float, width: float, options: SvgOptions,
) -> None:
    legend = _elem(parent, "g", id="arconte-legend")
    entries = [
        (_COLOR_PARENT, "Filiação biológica", None),
        (_COLOR_ADOPTION, "Filiação adotiva", "7 6"),
        (_COLOR_MARRIAGE, "Casamento", None),
        (_COLOR_PARTNERSHIP, "União", "3 5"),
    ]
    columns = max(1, min(4, int(width // 170)))
    for index, (color, description, dash) in enumerate(entries):
        column, row = index % columns, index // columns
        left = x + column * 170
        top = y + row * 28
        attrs: dict[str, object] = {
            "x1": _n(left), "x2": _n(left + 25),
            "y1": _n(top), "y2": _n(top),
            "stroke": color, "stroke_width": "3", "stroke_linecap": "round",
        }
        if dash:
            attrs["stroke_dasharray"] = dash
        _elem(legend, "line", **attrs)
        _label(legend, description, x=left + 32, y=top + 4,
               fill=_COLOR_MUTED, font_size="11",
               font_family="system-ui, Arial, sans-serif")


def render_svg(layout: TreeLayout, *, options: SvgOptions | None = None) -> str:
    """Gera um SVG UTF-8 independente e autocontido a partir do ``TreeLayout``.

    XML é escapado de forma segura: nomes e biografias não são interpretados
    como HTML ou elementos SVG. O documento não contém scripts nem recursos
    externos. Não modifica o layout recebido.
    """
    coords = _checked_positions(layout)
    if options is None:
        options = SvgOptions()
    if not isinstance(options, SvgOptions):
        raise TypeError("options deve ser SvgOptions ou None.")

    padding = float(options.padding)
    header = 92.0
    width = max(float(layout.width) + 2 * padding,
                float(options.card_width) + 2 * padding, 320.0)
    # Mesmo no caso de grafo vazio há espaço para título e mensagem.
    graph_height = max(float(layout.height), float(options.card_height) if coords else 150.0)
    available = width - 2 * padding
    legend_columns = max(1, min(4, int(available // 170)))
    legend_rows = math.ceil(4 / legend_columns) if options.show_legend else 0
    footer = (36 + 28 * legend_rows) if options.show_legend else 24.0
    height = graph_height + 2 * padding + header + footer
    x_shift = (width - float(layout.width)) / 2 if coords else width / 2
    y_shift = padding + header

    root = ET.Element(_svg("svg"), {
        "version": "1.1", "width": _n(width), "height": _n(height),
        "viewBox": f"0 0 {_n(width)} {_n(height)}",
        "role": "img", "aria-labelledby": "arconte-title arconte-description",
    })
    _elem(root, "title", id="arconte-title").text = options.title
    _elem(root, "desc", id="arconte-description").text = (
        f"Genealogia com {len(layout.graph.nodes)} personagens e "
        f"{len(layout.graph.edges)} relações."
    )
    defs = _elem(root, "defs")
    shadow = _elem(defs, "filter", id="card-shadow", x="-20%", y="-30%",
                   width="140%", height="170%")
    _elem(shadow, "feDropShadow", dx="0", dy="4", stdDeviation="6",
          flood_color="#172943", flood_opacity="0.09")
    _elem(root, "rect", width="100%", height="100%", fill=_COLOR_BACKGROUND)
    _label(root, "ARCONTE  /  GENEALOGIA", x=padding, y=padding + 2,
           fill=_COLOR_PARENT, font_size="11", font_weight="700",
           letter_spacing="2", font_family="system-ui, Arial, sans-serif")
    _label(root, options.title, x=padding, y=padding + 36,
           fill=_COLOR_TEXT, font_size="22", font_weight="700",
           font_family="system-ui, Arial, sans-serif")

    points = {
        uid: (position.x + x_shift, position.y + y_shift)
        for uid, position in coords.items()
    }
    if points:
        _draw_edges(_elem(root, "g", id="arconte-edges"), layout, points, options)
        _draw_nodes(_elem(root, "g", id="arconte-nodes"), layout, points, options)
    else:
        _label(root, "Nenhum personagem cadastrado", x=width / 2,
               y=y_shift + 70, text_anchor="middle", fill=_COLOR_MUTED,
               font_size="17", font_family="system-ui, Arial, sans-serif")

    if options.show_legend:
        _draw_legend(root, padding, y_shift + graph_height + padding + 9,
                     available, options)

    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def save_svg(
    layout: TreeLayout, path: str | PathLike[str], *,
    options: SvgOptions | None = None,
) -> Path:
    """Escreve SVG com UTF-8 e substituição atômica; devolve caminho salvo."""
    document = render_svg(layout, options=options)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(document)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


__all__ = ["SvgOptions", "render_svg", "save_svg"]
