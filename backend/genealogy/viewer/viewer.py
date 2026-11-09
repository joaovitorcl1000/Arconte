"""Visualizador HTML interativo, autônomo e somente leitura do Arconte.

Recebe um TreeLayout criado por tree.layout_tree e reutiliza o SVG seguro do
módulo visualization. Não modifica Project, Genealogy ou os objetos do layout.
Não precisa de servidor, Flutter, JavaScript externo ou dependências adicionais.

Exemplo (executar em backend/genealogy)::

    from project.project import Project
    from tree.tree import TreeBuilder, layout_tree
    from viewer.viewer import save_html, ViewerOptions

    project = Project.load("data/eldoria.json")
    layout = layout_tree(TreeBuilder(project).build())
    save_html(layout, "data/eldoria.html", project=project,
              options=ViewerOptions(title="Genealogia de Eldoria"))

Interações: zoom por roda/botões, arraste, restauração da vista, pesquisa
sem acentos, resultados clicáveis, painel de informações e atalhos de teclado.
A saída é HTML com SVG, CSS e JS embutidos e funciona com o protocolo file://.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
import os
from os import PathLike
from pathlib import Path
from string import Template
import tempfile
from typing import Any
from uuid import UUID
import xml.etree.ElementTree as ET

from project.project import Project
from tree.tree import TreeLayout
from visualization.visualization import SvgOptions, render_svg


_SVG_NS = "http://www.w3.org/2000/svg"


def _validated_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} deve ser uma string.")
    if not value.strip():
        raise ValueError(f"{name} não pode estar vazio.")
    # XML 1.0 não aceita certos caracteres de controle, inclusive NUL.
    for character in value:
        code = ord(character)
        if not (
            code in (9, 10, 13)
            or 0x20 <= code <= 0xD7FF
            or 0xE000 <= code <= 0xFFFD
            or 0x10000 <= code <= 0x10FFFF
        ):
            raise ValueError(f"{name} contém caracteres inválidos em XML.")
    return value.strip()


@dataclass(frozen=True, slots=True, kw_only=True)
class ViewerOptions:
    """Configurações de apresentação, independentes do grafo genealógico."""

    title: str = "Árvore genealógica"
    subtitle: str | None = None
    show_years: bool = True
    show_legend: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", _validated_text(self.title, "title"))
        if self.subtitle is not None:
            if not isinstance(self.subtitle, str):
                raise TypeError("subtitle deve ser uma string ou None.")
            subtitle = self.subtitle.strip()
            if subtitle:
                _validated_text(subtitle, "subtitle")
            object.__setattr__(self, "subtitle", subtitle or None)
        for field_name in ("show_years", "show_legend"):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} deve ser bool.")


def _embedded_json(value: Any) -> str:
    """Serializa dados para <script type=application/json> sem injeção HTML.

    </script>, <, >, &, U+2028 e U+2029 devem ser codificados na origem.
    Usar html.escape aqui corromperia o JSON lido por textContent no JS.
    """
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _interactive_svg(layout: TreeLayout, options: ViewerOptions) -> str:
    svg = render_svg(
        layout,
        options=SvgOptions(
            title=options.title,
            show_years=options.show_years,
            show_legend=options.show_legend,
        ),
    )
    root = ET.fromstring(svg)
    # O SVG mantém a estrutura do render_svg e adiciona acessibilidade.
    root.set("id", "arconte-svg")
    root.set("tabindex", "0")
    for node in root.findall(f".//{{{_SVG_NS}}}g[@data-character-id]"):
        node.set("tabindex", "0")
        node.set("role", "button")
        node.set("aria-label", "Abrir informações de " + (
            node.findtext(f"{{{_SVG_NS}}}title") or "personagem"
        ).split("\n", 1)[0])
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


_HTML = Template(r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>$PAGE_TITLE</title>
<style>
  :root { font-family: system-ui,-apple-system,"Segoe UI",sans-serif; color:#e7edf5;
          background:#0b1828; font-synthesis:none; }
  * { box-sizing:border-box; }
  body { margin:0; min-width:320px; }
  button, input { font:inherit; }
  button { cursor:pointer; }
  button:focus-visible, input:focus-visible, [data-character-id]:focus-visible {
    outline:3px solid #e7b765; outline-offset:3px;
  }
  .app { display:grid; grid-template-columns:330px minmax(0,1fr); height:100dvh; min-height:550px; }
  .sidebar { display:flex; flex-direction:column; min-height:0; overflow:auto;
             background:linear-gradient(160deg,#12263c 0%,#0b192a 85%);
             border-right:1px solid rgba(255,255,255,.08); }
  .brand { padding:29px 26px 20px; border-bottom:1px solid rgba(255,255,255,.1); }
  .brand-mark { color:#efbb68; font-size:12px; letter-spacing:.22em; font-weight:750; }
  h1 { font-size:23px; line-height:1.25; letter-spacing:-.03em; margin:17px 0 9px; overflow-wrap:anywhere; }
  .subtitle { color:#b6c5d6; font-size:13px; line-height:1.5; margin:0; }
  .tag { display:inline-block; margin-top:18px; border:1px solid #436078; border-radius:100px;
         padding:5px 10px; color:#c9d7e4; font-size:10px; font-weight:650; letter-spacing:.12em; }
  .search-area { padding:23px 22px 15px; border-bottom:1px solid rgba(255,255,255,.08); }
  label { display:block; margin-bottom:10px; font-size:11px; color:#aac0d4;
          letter-spacing:.10em; text-transform:uppercase; font-weight:700; }
  #search { width:100%; background:#20364c; border:1px solid #445d74; color:#f6f9fd;
            border-radius:11px; padding:13px 14px; font-size:14px; }
  #search::placeholder { color:#a7b6c6; }
  #result-count { margin:9px 0 0; color:#a6bed0; font-size:12px; }
  #results { display:flex; flex-direction:column; gap:6px; max-height:180px;
             margin-top:10px; overflow-y:auto; }
  .result-button { width:100%; text-align:left; background:#20364c; color:#e9f1f9;
                   border:1px solid transparent; border-radius:9px; padding:9px 12px;
                   font-size:13px; overflow-wrap:anywhere; }
  .result-button:hover { border-color:#cba366; background:#2b445d; }
  .details { padding:24px 23px 32px; overflow:auto; flex:1; }
  h2 { font-size:11px; letter-spacing:.12em; color:#b8c9d7; text-transform:uppercase;
       margin:0 0 16px; }
  .empty { color:#a7bac9; font-size:14px; line-height:1.7; }
  #person-name { font-size:21px; color:#fff; line-height:1.3; margin:0 0 9px; overflow-wrap:anywhere; }
  .meta { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px; }
  .chip { display:inline-flex; align-items:center; background:#29415a; border-radius:7px;
          color:#e8edf5; font-size:12px; padding:6px 9px; overflow-wrap:anywhere; }
  .description { color:#d2dce7; font-size:13px; line-height:1.7; white-space:pre-wrap;
                 overflow-wrap:anywhere; margin:11px 0 22px; }
  .section-title { font-weight:700; font-size:11px; color:#e5b978; text-transform:uppercase;
                   letter-spacing:.09em; margin:20px 0 8px; }
  .linklist { display:flex; gap:6px; flex-wrap:wrap; }
  .person-link { border:1px solid #4c6579; color:#e5edf4; background:transparent;
                 border-radius:9px; font-size:12px; padding:7px 9px; text-align:left; }
  .person-link:hover { background:#243e55; border-color:#e5b978; }
  .workspace { position:relative; overflow:hidden; display:flex; flex-direction:column;
               background:#f4f7fb; min-width:0; }
  .toolbar { position:absolute; z-index:2; display:flex; gap:8px; flex-wrap:wrap;
             align-items:center; top:19px; left:22px; right:22px; pointer-events:none; }
  .toolbar button, .toolbar .hint { pointer-events:auto; }
  .toolbar button { border:1px solid #d4dce7; border-radius:10px; background:#fff;
                    color:#19324b; min-width:42px; height:40px; padding:0 12px;
                    box-shadow:0 3px 16px #152a3e12; font-weight:700; }
  .toolbar button:hover { background:#e8edf5; }
  .hint { margin-left:auto; background:#fffdf5ed; color:#4a5d70; border:1px solid #e6e3d5;
          border-radius:10px; padding:11px 13px; font-size:12px; }
  #svg-area { flex:1; min-height:0; overflow:hidden; }
  #svg-area svg { display:block; width:100%; height:100%; touch-action:none; cursor:grab; }
  #svg-area svg.is-panning { cursor:grabbing; }
  #svg-area [data-character-id] { cursor:pointer; transition:opacity 110ms ease; }
  #svg-area [data-character-id].is-dimmed { opacity:.16; }
  #svg-area [data-character-id].is-search-match rect:first-of-type {
    stroke:#d79b27; stroke-width:3.5;
  }
  #svg-area [data-character-id].is-selected rect:first-of-type {
    stroke:#c26740; stroke-width:4.3;
  }
  .footer { position:absolute; bottom:15px; right:19px; pointer-events:none;
            color:#5e7186; font-size:11px; background:#ffffffd6; border-radius:8px;
            padding:7px 9px; }
  @media(max-width:840px) {
    .app { display:flex; flex-direction:column; height:auto; min-height:100dvh; }
    .workspace { height:60vh; min-height:390px; order:1; }
    .sidebar { order:2; min-height:320px; max-height:none; overflow:visible; }
    .brand { padding:19px 22px; }
    .tag { margin-top:8px; }
    .hint { display:none; }
    .details { overflow:visible; }
  }
  @media(prefers-reduced-motion:reduce) {
    #svg-area [data-character-id] { transition:none; }
  }
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar" aria-label="Busca e informações dos personagens">
    <header class="brand">
      <div class="brand-mark">✦ ARCONTE / GENEALOGIA</div>
      <h1>$TITLE</h1>
      <p class="subtitle">$SUBTITLE</p>
      <span class="tag">EXPLORAÇÃO · SOMENTE LEITURA</span>
    </header>
    <div class="search-area">
      <label for="search">Localizar personagem</label>
      <input id="search" type="search" placeholder="Digite um nome..." autocomplete="off">
      <p id="result-count" aria-live="polite"></p>
      <div id="results" aria-label="Resultados da pesquisa"></div>
    </div>
    <section class="details" aria-label="Detalhes selecionados">
      <h2>Ficha do personagem</h2>
      <div id="details-body" aria-live="polite">
        <p class="empty">Clique em um cartão para consultar dados, vínculos e famílias.</p>
      </div>
    </section>
  </aside>
  <main class="workspace" aria-label="Árvore genealógica">
    <div class="toolbar" aria-label="Controles de visualização">
      <button id="zoom-in" type="button" title="Aproximar" aria-label="Aproximar">+</button>
      <button id="zoom-out" type="button" title="Afastar" aria-label="Afastar">−</button>
      <button id="reset" type="button" title="Enquadrar toda a árvore">Enquadrar</button>
      <span class="hint">Arraste para mover · Roda para zoom · Clique para selecionar</span>
    </div>
    <div id="svg-area">$INLINE_SVG</div>
    <div class="footer" id="scene-count"></div>
  </main>
</div>
<script id="arconte-data" type="application/json">$DATA_JSON</script>
<script>
(function () {
  'use strict';
  const data = JSON.parse(document.getElementById('arconte-data').textContent);
  const svg = document.getElementById('arconte-svg');
  const nodes = data.nodes;
  const byId = new Map(nodes.map(function(n) { return [n.id, n]; }));
  const cards = new Map();
  svg.querySelectorAll('[data-character-id]').forEach(function(el) {
    cards.set(el.getAttribute('data-character-id'), el);
  });
  const search = document.getElementById('search');
  const results = document.getElementById('results');
  const resultCount = document.getElementById('result-count');
  const details = document.getElementById('details-body');
  document.getElementById('scene-count').textContent =
    nodes.length + ' personagens · ' + data.edges.length + ' relações';

  const original = svg.viewBox.baseVal;
  const base = {x: original.x, y: original.y, width: original.width, height: original.height};
  let view = Object.assign({}, base);
  let selectedId = null;
  let pointer = null;
  let moved = false;

  function setView(v) {
    view = v;
    svg.setAttribute('viewBox', [v.x, v.y, v.width, v.height].join(' '));
  }
  function screenToWorld(x, y) {
    const matrix = svg.getScreenCTM();
    if (!matrix) return null;
    return new DOMPoint(x, y).matrixTransform(matrix.inverse());
  }
  function zoomAt(x, y, factor) {
    const scale = Math.min(8, Math.max(0.35, base.width / view.width * factor));
    const width = base.width / scale;
    const height = base.height / scale;
    const pivot = screenToWorld(x, y);
    if (!pivot) return;
    const ratio = width / view.width;
    setView({x: pivot.x - (pivot.x - view.x) * ratio,
             y: pivot.y - (pivot.y - view.y) * ratio, width:width, height:height});
  }
  function zoomButton(factor) {
    const box = svg.getBoundingClientRect();
    zoomAt(box.left + box.width / 2, box.top + box.height / 2, factor);
  }
  function fit() { setView(Object.assign({}, base)); }
  document.getElementById('zoom-in').addEventListener('click', function() { zoomButton(1.25); });
  document.getElementById('zoom-out').addEventListener('click', function() { zoomButton(1 / 1.25); });
  document.getElementById('reset').addEventListener('click', fit);
  svg.addEventListener('wheel', function(event) {
    event.preventDefault();
    zoomAt(event.clientX, event.clientY, Math.exp(-event.deltaY * 0.0015));
  }, {passive:false});
  svg.addEventListener('pointerdown', function(event) {
    if (event.button !== 0 || pointer) return;
    pointer = {id:event.pointerId, x:event.clientX, y:event.clientY};
    moved = false;
  });
  window.addEventListener('pointermove', function(event) {
    if (!pointer || pointer.id !== event.pointerId) return;
    if (Math.hypot(event.clientX - pointer.x, event.clientY - pointer.y) < 3 && !moved) return;
    moved = true;
    svg.classList.add('is-panning');
    const before = screenToWorld(pointer.x, pointer.y);
    const after = screenToWorld(event.clientX, event.clientY);
    if (before && after) setView({x:view.x + before.x - after.x,
                                   y:view.y + before.y - after.y,
                                   width:view.width, height:view.height});
    pointer.x = event.clientX;
    pointer.y = event.clientY;
  });
  function finishPointer(event) {
    if (pointer && (event.pointerId === pointer.id || event.type === 'blur')) {
      pointer = null;
      svg.classList.remove('is-panning');
      // Evita selecionar cartão imediatamente depois de arrastá-lo.
      if (moved) window.setTimeout(function() { moved = false; }, 0);
    }
  }
  window.addEventListener('pointerup', finishPointer);
  window.addEventListener('pointercancel', finishPointer);
  window.addEventListener('blur', finishPointer);

  function normalize(value) {
    return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('pt-BR').trim();
  }
  function newEl(tag, className, textValue) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (textValue !== undefined) element.textContent = String(textValue);
    return element;
  }
  function focusNode(id) {
    const element = cards.get(id);
    if (!element) return;
    const box = element.getBBox();
    const scale = Math.max(1.3, Math.min(8, base.width / view.width));
    const width = base.width / scale;
    const height = base.height / scale;
    setView({x:box.x + box.width / 2 - width / 2,
             y:box.y + box.height / 2 - height / 2, width:width, height:height});
  }
  function addSection(container, title, names, interactive) {
    if (!names.length) return;
    container.appendChild(newEl('p', 'section-title', title));
    const wrap = newEl('div', 'linklist');
    names.forEach(function(idOrName) {
      if (interactive && byId.has(idOrName)) {
        const button = newEl('button', 'person-link', byId.get(idOrName).full_name);
        button.type = 'button';
        button.addEventListener('click', function() { selectNode(idOrName, true); });
        wrap.appendChild(button);
      } else {
        wrap.appendChild(newEl('span', 'chip', idOrName));
      }
    });
    container.appendChild(wrap);
  }
  function selectNode(id, focus) {
    const node = byId.get(id);
    if (!node) return;
    selectedId = id;
    cards.forEach(function(card, key) { card.classList.toggle('is-selected', key === id); });
    details.replaceChildren();
    details.appendChild(newEl('h3', '', node.full_name));
    details.lastChild.id = 'person-name';
    const meta = newEl('div', 'meta');
    if (node.birth_year !== null) meta.appendChild(newEl('span', 'chip', 'Nasc. ' + node.birth_year));
    if (node.death_year !== null) meta.appendChild(newEl('span', 'chip', 'Falec. ' + node.death_year));
    if (node.gender) meta.appendChild(newEl('span', 'chip', node.gender));
    details.appendChild(meta);
    if (node.biography) details.appendChild(newEl('p', 'description', node.biography));
    const families = node.family_ids.map(function(fid) { return data.families[fid] || fid; });
    addSection(details, 'Famílias e casas', families, false);
    const groups = [
      ['Pais e responsáveis', data.edges.filter(function(e) { return e.directed && e.target_id === id; })
       .map(function(e) { return e.source_id; })],
      ['Filhos', data.edges.filter(function(e) { return e.directed && e.source_id === id; })
       .map(function(e) { return e.target_id; })],
      ['Casamentos e uniões', data.edges.filter(function(e) { return !e.directed && (e.source_id === id || e.target_id === id); })
       .map(function(e) { return e.source_id === id ? e.target_id : e.source_id; })]
    ];
    groups.forEach(function(group) {
      const unique = Array.from(new Set(group[1])).filter(function(value) { return byId.has(value); });
      unique.sort(function(a,b) { return byId.get(a).full_name.localeCompare(byId.get(b).full_name, 'pt-BR'); });
      addSection(details, group[0], unique, true);
    });
    if (focus) focusNode(id);
  }
  svg.addEventListener('click', function(event) {
    if (moved) return;
    const element = event.target.closest('[data-character-id]');
    if (element) selectNode(element.getAttribute('data-character-id'), false);
  });
  svg.addEventListener('keydown', function(event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const element = event.target.closest('[data-character-id]');
    if (element) {
      event.preventDefault();
      selectNode(element.getAttribute('data-character-id'), true);
    }
  });
  function updateSearch() {
    const query = normalize(search.value);
    const found = query ? nodes.filter(function(n) { return normalize(n.full_name).includes(query); }) : [];
    cards.forEach(function(card, id) {
      const match = query && found.some(function(n) { return n.id === id; });
      card.classList.toggle('is-search-match', Boolean(match));
      card.classList.toggle('is-dimmed', Boolean(query) && !match);
    });
    results.replaceChildren();
    resultCount.textContent = query ? (found.length + ' resultado(s)')
      : (nodes.length + ' personagem(ns) no mapa');
    found.slice(0, 30).forEach(function(node) {
      const button = newEl('button', 'result-button', node.full_name);
      button.type = 'button';
      button.addEventListener('click', function() { selectNode(node.id, true); });
      results.appendChild(button);
    });
    if (found.length > 30) results.appendChild(newEl('p', 'empty', 'Exibindo os primeiros 30 resultados.'));
  }
  search.addEventListener('input', updateSearch);
  search.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      const query = normalize(search.value);
      const found = nodes.find(function(n) { return query && normalize(n.full_name).includes(query); });
      if (found) selectNode(found.id, true);
    }
  });
  document.addEventListener('keydown', function(event) {
    if (event.target === search || event.target.tagName === 'BUTTON') return;
    if (event.key === '+' || event.key === '=') { event.preventDefault(); zoomButton(1.25); }
    else if (event.key === '-') { event.preventDefault(); zoomButton(1 / 1.25); }
    else if (event.key === '0') { event.preventDefault(); fit(); }
    else if (event.key === 'Escape') {
      selectedId = null;
      cards.forEach(function(card) { card.classList.remove('is-selected'); });
      details.replaceChildren(newEl('p', 'empty', 'Clique em um cartão para consultar suas informações.'));
    }
  });
  updateSearch();
})();
</script>
</body>
</html>
''')


def render_html(
    layout: TreeLayout,
    *,
    options: ViewerOptions | None = None,
    project: Project | None = None,
) -> str:
    """Devolve um HTML autocontido a partir do ``TreeLayout`` existente.

    ``project`` é opcional e serve somente para exibir nomes de famílias.
    O arquivo pode ser aberto diretamente no navegador, sem servidor.
    """
    if options is None:
        options = ViewerOptions()
    if not isinstance(options, ViewerOptions):
        raise TypeError("options deve ser ViewerOptions ou None.")
    if project is not None and not isinstance(project, Project):
        raise TypeError("project deve ser Project ou None.")

    # render_svg faz validação integral do layout (IDs, posições, arestas,
    # coordenadas finitas e textos XML) antes de gerar conteúdo.
    svg = _interactive_svg(layout, options)
    data = layout.to_dict()
    family_names: dict[str, str] = {}
    if project is not None:
        project.validate_integrity()
        family_names = {str(family.id): family.name for family in project.get_all_families()}
    data["families"] = family_names

    subtitle = options.subtitle if options.subtitle is not None else (
        project.description if project is not None and project.description else
        "Explore personagens, gerações e conexões familiares."
    )
    return _HTML.substitute(
        PAGE_TITLE=escape(options.title, quote=True) + " | Arconte",
        TITLE=escape(options.title, quote=True),
        SUBTITLE=escape(subtitle, quote=True),
        INLINE_SVG=svg,
        DATA_JSON=_embedded_json(data),
    )


def save_html(
    layout: TreeLayout,
    path: str | PathLike[str],
    *,
    options: ViewerOptions | None = None,
    project: Project | None = None,
) -> Path:
    """Grava o visualizador em UTF-8, substituindo o destino atomicamente."""
    html = render_html(layout, options=options, project=project)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(html)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


__all__ = ["ViewerOptions", "render_html", "save_html"]
