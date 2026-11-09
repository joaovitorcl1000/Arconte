"""
Famílias de línguas (etapa 4 do módulo de evolução).

Transforma uma língua numa família: a protolíngua se divide em ramos, cada ramo
evolui por um caminho próprio (etapas 1, 2 e 3) e pode se dividir de novo, como o
proto-indo-europeu deu o latim, o germânico e o céltico, e o latim deu o
português, o espanhol e o francês.

Depois, o módulo faz o que a linguística histórica faz com uma família real:

    árvore genealógica      ramos, perfis, tempos e leis de cada língua
    cognatos                as palavras básicas em todas as línguas, com as classes de
                            cognatos (a, b, c...) como nas tabelas dos manuais
    correspondências        o reflexo de cada som da protolíngua em cada língua
                            (o método comparativo: proto *p → A f, B b, C ∅)
    distâncias              porcentagem de cognatos compartilhados entre cada par
                            (lexicoestatística)

Não altera nenhum outro arquivo: usa as etapas 1, 2 e 3 como elas são.

Uso:
    python evolution/family.py --language languages/lang-31
    python evolution/family.py --language languages/lang-31 --branches 3 --sub-branches 2 --years 1500 --rebuild
    python evolution/family.py --language languages/lang-31 --profiles romance,germanic,celtic

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import json
import random
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
for folder in ("generate_language", "orthography"):
    sys.path.insert(0, str(ROOT / folder))

import evolution as evo_mod  # noqa: E402
import laws as L  # noqa: E402

TONE_LETTERS = "˥˦˧˨˩"
FIRST_LEVEL_PROFILES = ["romance", "germanic", "celtic", "slavic", "indo_iranian", "hellenic",
                        "polynesian", "sinitic"]
CORE = ["I", "THOU", "WE", "ONE", "TWO", "THREE", "PERSON", "WOMAN", "MALE PERSON", "CHILD (YOUNG HUMAN)",
        "MOTHER", "FATHER", "NAME", "DOG", "FISH", "BIRD", "LOUSE", "TREE", "LEAF", "ROOT", "SEED", "FLESH OR MEAT",
        "BLOOD", "BONE", "EGG", "HORN (ANATOMY)", "TAIL", "FEATHER", "HAIR", "HEAD", "EAR", "EYE", "NOSE", "MOUTH",
        "TOOTH", "TONGUE", "FOOT", "KNEE", "HAND", "BELLY", "NECK", "BREAST", "HEART", "LIVER", "DRINK", "EAT",
        "BITE", "SEE", "HEAR", "KNOW", "SLEEP", "DIE", "KILL", "SWIM", "FLY (MOVE THROUGH AIR)", "WALK", "COME",
        "LIE (REST)", "SIT", "STAND", "GIVE", "SAY", "SUN", "MOON", "STAR", "WATER", "RAIN (PRECIPITATION)",
        "STONE", "SAND", "EARTH (SOIL)", "CLOUD", "SMOKE (EXHAUST)", "FIRE", "ASH", "BURNING", "ROAD", "MOUNTAIN",
        "RED", "GREEN", "YELLOW", "WHITE", "BLACK", "NIGHT", "WARM (OF WEATHER)", "COLD (OF WEATHER)", "FULL",
        "NEW", "GOOD", "ROUND", "DRY", "BIG", "SMALL", "LONG"]


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


# ═══════════════════════════════════════════════════════════════════════════
# Árvore
# ═══════════════════════════════════════════════════════════════════════════

class Node:
    def __init__(self, name: str, path: str, parent: Optional["Node"], profile: Optional[str],
                 years: int, dir: Path):
        self.name, self.path, self.parent = name, path, parent
        self.profile, self.years, self.dir = profile, years, dir
        self.children: List["Node"] = []
        self.evo: Optional[Dict] = None

    @property
    def depth(self) -> int:
        return 0 if self.parent is None else self.parent.depth + 1

    def total_years(self) -> int:
        return self.years + (self.parent.total_years() if self.parent else 0)

    def leaves(self) -> List["Node"]:
        return [self] if not self.children else [x for c in self.children for x in c.leaves()]

    def all(self) -> List["Node"]:
        return [self] + [x for c in self.children for x in c.all()]


class FamilyBuilder:
    def __init__(self, proto_dir: Path, branches: int = 3, sub_branches: int = 2, depth: int = 2,
                 years: int = 1500, profiles: Optional[List[str]] = None, grammar: bool = True,
                 seed: Optional[int] = None, prefix: Optional[str] = None):
        if not (proto_dir / "lexicon.json").exists():
            raise SystemExit(f"{proto_dir} não é uma língua gerada (falta lexicon.json).")
        self.proto_dir = proto_dir
        manifest = _load(proto_dir / "manifest.json") or {}
        self.master = manifest.get("seed", 0)
        self.seed = seed if seed is not None else derive_seed(self.master, f"family:{branches}:{sub_branches}:{depth}:{years}")
        self.rng = random.Random(self.seed)
        self.branches, self.sub, self.depth, self.years = branches, sub_branches, depth, years
        self.grammar = grammar
        self.prefix = prefix or proto_dir.name
        bad = [p for p in (profiles or []) if p not in L.PROFILES]
        if bad:
            raise SystemExit(f"Perfis desconhecidos: {', '.join(bad)}")
        self.profiles = profiles

    def plan(self) -> Node:
        root = Node(self.proto_dir.name, "", None, None, 0, self.proto_dir)
        pool = list(self.profiles or self.rng.sample(FIRST_LEVEL_PROFILES, min(self.branches, len(FIRST_LEVEL_PROFILES))))
        letters = "ABCDEFGHIJ"

        def grow(node: Node, level: int) -> None:
            if level > self.depth:
                return
            n = self.branches if level == 1 else self.sub
            for i in range(n):
                path = (letters[i] if level == 1 else f"{node.path}{i + 1}")
                if level == 1:
                    profile = pool[i % len(pool)]
                else:  # sub-ramos: continuam o caminho do ramo ou seguem mudanças comuns
                    profile = self.rng.choice([node.profile, "natural"])
                yrs = int(round(self.years * self.rng.uniform(0.7, 1.3) / 50) * 50)
                child = Node(f"{self.prefix}-{path}", path, node, profile, yrs,
                             self.proto_dir.parent / f"{self.prefix}-{path}")
                node.children.append(child)
                grow(child, level + 1)
        grow(root, 1)
        return root

    def build(self, rebuild: bool = False, log=print) -> Node:
        root = self.plan()
        for node in root.all()[1:]:  # pais antes dos filhos (ordem da árvore)
            ev = evo_mod.Evolver(node.parent.dir, node.profile, node.years,
                                 seed=derive_seed(self.seed, f"node:{node.path}"))
            ev.build(node.dir)
            # a pasta pode ser de uma família anterior: o retrato da etapa 3 precisa ser o desta língua
            shutil.rmtree(node.dir / ".before_grammar", ignore_errors=True)
            if self.grammar:
                import grammar_evolution as G
                G.GrammarEvolver(node.dir, seed=derive_seed(self.seed, f"grammar:{node.path}")).run()
            node.evo = _load(node.dir / "evolution.json")
            log(f"  {node.name:<22} ← {node.parent.name:<22} {L.PROFILES[node.profile]['name']:<14} "
                f"{node.years:>5} anos, {len(node.evo['laws'])} leis")
            if rebuild:
                import generate_language as gl
                opts = (_load(self.proto_dir / "manifest.json") or {}).get("options", {})
                kwargs = {"out": node.dir.parent, "start": "orthography"}
                if opts.get("no_wals"):
                    kwargs["no_wals"] = True
                gl.generate(self.master, name=node.dir.name, **kwargs)
            # história de cada língua (com grafia, se houver ortografia)
            evo_mod.write_markdown(node.dir / "evolution.md", node.evo, spell_for(node.dir), spell_for(node.parent.dir))
            if self.grammar:
                import grammar_evolution as G
                G.write_markdown(node.dir, node.evo, spell_for(node.dir))
        return root


def spell_for(d: Path):
    o = _load(d / "orthography.json")
    if not o:
        return None
    import orthography as ortho_mod
    return ortho_mod.Orthography(o).spell


# ═══════════════════════════════════════════════════════════════════════════
# Análise comparativa
# ═══════════════════════════════════════════════════════════════════════════

class Comparison:
    def __init__(self, root: Node):
        self.root = root
        self.nodes = root.all()
        self.lex = {n.name: {e["gloss"]: e for e in (_load(n.dir / "lexicon.json") or {}).get("entries", [])
                             if e.get("citation")} for n in self.nodes}
        inv = {n.name: _load(n.dir / "phonemic_inventory.json") for n in self.nodes}
        self.symbols = {k: sorted({nfd(x["ipa"]) for x in v["consonants"] + v["vowels"]}, key=len, reverse=True)
                        for k, v in inv.items() if v}
        self.vowels = {k: {nfd(x["ipa"]) for x in v["vowels"]} for k, v in inv.items() if v}
        self.origin = self._origins()

    def segments(self, lang: str, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ -"), 0
            while i < len(s):
                hit = next((x for x in self.symbols[lang] if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def _origins(self) -> Dict[str, Dict[str, str]]:
        """De onde vem a palavra de cada significado em cada língua: da protolíngua ou de uma
        inovação (substituição, mudança de significado, empréstimo) num ramo. Palavras com a
        mesma origem formam uma classe de cognatos."""
        out: Dict[str, Dict[str, str]] = {self.root.name: {g: self.root.name for g in self.lex[self.root.name]}}
        for n in self.nodes[1:]:
            innov = {x["gloss"] for x in (n.evo or {}).get("lexical", {}).get("events", [])
                     if x["type"] in ("replacement", "shift", "loan")}
            parent = out[n.parent.name]
            out[n.name] = {g: (n.name if g in innov else parent.get(g, n.name)) for g in self.lex[n.name]}
        return out

    # ── cognatos ─────────────────────────────────────────────────────────
    def cognate_table(self, concepts: List[str]) -> List[Dict]:
        rows = []
        leaves = [self.root] + self.root.leaves()
        for g in concepts:
            if g not in self.lex[self.root.name]:
                continue
            classes: Dict[str, str] = {}
            cells = []
            for n in leaves:
                e = self.lex[n.name].get(g)
                if not e:
                    cells.append(None)
                    continue
                o = self.origin[n.name].get(g)
                classes.setdefault(o, "abcdefghij"[len(classes)])
                cells.append({"lang": n.name, "form": e["citation"], "class": classes[o]})
            label = (self.lex[self.root.name][g].get("label") or g.lower())
            rows.append({"gloss": g, "label": label, "cells": cells})
        return rows

    def distances(self) -> Tuple[List[str], List[List[Optional[float]]]]:
        langs = [self.root.name] + [n.name for n in self.root.leaves()]
        m = []
        for a in langs:
            row = []
            for b in langs:
                common = set(self.origin[a]) & set(self.origin[b])
                row.append(round(100 * sum(1 for g in common if self.origin[a][g] == self.origin[b][g]) / len(common), 1)
                           if common else None)
            m.append(row)
        return langs, m

    # ── correspondências sonoras ─────────────────────────────────────────
    @staticmethod
    def align(a: List[str], b: List[str]) -> List[Tuple[Optional[str], Optional[str]]]:
        """Alinhamento de Needleman-Wunsch (custo 1 para troca e para lacuna)."""
        n, m = len(a), len(b)
        D = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            D[i][0] = i
        for j in range(m + 1):
            D[0][j] = j
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                D[i][j] = min(D[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1), D[i - 1][j] + 1, D[i][j - 1] + 1)
        out, i, j = [], n, m
        while i > 0 or j > 0:
            if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1):
                out.append((a[i - 1], b[j - 1]))
                i, j = i - 1, j - 1
            elif i > 0 and D[i][j] == D[i - 1][j] + 1:
                out.append((a[i - 1], None))
                i -= 1
            else:
                out.append((None, b[j - 1]))
                j -= 1
        return list(reversed(out))

    def correspondences(self, min_count: int = 4) -> Tuple[List[str], List[Dict]]:
        """Reflexo mais frequente de cada som da protolíngua em cada língua, a partir dos cognatos."""
        proto = self.root.name
        leaves = [n.name for n in self.root.leaves()]
        counts: Dict[str, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
        totals: Counter = Counter()
        for g, pe in self.lex[proto].items():
            if "-" in pe["citation"]:
                continue
            ps = self.segments(proto, pe["citation"])
            totals.update(ps)
            for lang in leaves:
                e = self.lex[lang].get(g)
                if not e or self.origin[lang].get(g) != proto or "-" in e["citation"]:
                    continue
                for x, y in self.align(ps, self.segments(lang, e["citation"])):
                    if x is not None:
                        counts[x][lang][y or "∅"] += 1
        rows = []
        for s, _ in totals.most_common():
            if totals[s] < min_count:
                continue
            refl = {}
            for lang in leaves:
                c = counts[s][lang]
                if c:
                    top, k = c.most_common(1)[0]
                    refl[lang] = {"reflex": top, "share": round(k / sum(c.values()), 2)}
            if refl:
                rows.append({"proto": s, "vowel": s in self.vowels[proto], "reflexes": refl,
                             "changed": any(v["reflex"] != s for v in refl.values())})
        return leaves, rows


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def ascii_tree(root: Node) -> List[str]:
    lines = [f"{root.name} (protolíngua)"]

    def walk(node: Node, prefix: str) -> None:
        for i, c in enumerate(node.children):
            last = i == len(node.children) - 1
            laws = ", ".join(x["name"] for x in (c.evo or {}).get("laws", [])[:3])
            more = "..." if len((c.evo or {}).get("laws", [])) > 3 else ""
            lines.append(f"{prefix}{'└── ' if last else '├── '}{c.name}  [{L.PROFILES[c.profile]['name']}, "
                         f"{c.years} anos; {laws}{more}]")
            walk(c, prefix + ("    " if last else "│   "))
    walk(root, "")
    return lines


def mermaid(root: Node) -> List[str]:
    ids = {n.name: f"n{i}" for i, n in enumerate(root.all())}
    out = ["```mermaid", "graph TD"]
    for n in root.all():
        lab = f"{n.name}" if n.parent is None else f"{n.name}<br/>{L.PROFILES[n.profile]['name']}, {n.years} anos"
        out.append(f'  {ids[n.name]}["{lab}"]')
    for n in root.all()[1:]:
        out.append(f"  {ids[n.parent.name]} --> {ids[n.name]}")
    return out + ["```"]


def write_family(path: Path, root: Node, cmp: Comparison, data: Dict) -> None:
    spells = {n.name: spell_for(n.dir) for n in root.all()}
    sp = lambda lang, f: (spells[lang](f) if spells[lang] else f)  # noqa: E731
    leaves = root.leaves()
    lines = [f"# Família {root.name}", "",
             f"{len(root.all()) - 1} línguas descendentes em {max(n.depth for n in root.all())} níveis, "
             f"de {min(n.total_years() for n in leaves)} a {max(n.total_years() for n in leaves)} anos de separação da protolíngua.",
             "É uma simulação plausível, não uma previsão.", "", "## Árvore", "", "```"] + ascii_tree(root) + ["```", ""]
    lines += mermaid(root) + ["", "## Línguas", "", "| Língua | Vem de | Perfil | Anos | Leis fonéticas | Pasta |",
                              "|---|---|---|---|---|---|"]
    for n in root.all()[1:]:
        laws = ", ".join(x["name"] for x in n.evo["laws"])
        lines.append(f"| **{n.name}** | {n.parent.name} | {L.PROFILES[n.profile]['name']} | {n.years} "
                     f"| {laws} | [`{n.dir.name}/`](../{n.dir.name}/) |")

    rows = data["cognates"]
    head = [root.name] + [n.name for n in leaves]
    lines += ["", "## Cognatos", "",
              "As letras indicam as classes de cognatos de cada significado: palavras com a mesma letra "
              "descendem da mesma palavra; uma letra nova marca uma inovação (substituição, mudança de "
              "significado ou empréstimo) num ramo.", "",
              "| Significado | " + " | ".join(head) + " |", "|---|" + "---|" * len(head)]
    for r in rows:
        cells = []
        for c in r["cells"]:
            cells.append("—" if c is None else f"{sp(c['lang'], c['form'])} *({c['class']})*")
        lines.append(f"| {r['label']} | " + " | ".join(cells) + " |")

    langs, rows_c = data["correspondences"]
    lines += ["", "## Correspondências sonoras", "",
              "O reflexo mais frequente de cada som da protolíngua em cada língua, nos cognatos alinhados "
              "(o método comparativo). Em negrito, os sons que mudaram; ∅ indica perda.", "",
              f"| *{root.name} | " + " | ".join(langs) + " |", "|---|" + "---|" * len(langs)]
    for r in rows_c:
        cells = []
        for lang in langs:
            v = r["reflexes"].get(lang)
            if not v:
                cells.append("—")
                continue
            txt = f"{v['reflex']}"
            cells.append(f"**{txt}**" if v["reflex"] != r["proto"] else txt)
        lines.append(f"| *{r['proto']} | " + " | ".join(cells) + " |")

    names, m = data["distances"]
    lines += ["", "## Distâncias (cognatos compartilhados)", "",
              "Porcentagem do vocabulário em que cada par de línguas ainda usa palavras cognatas "
              "(lexicoestatística): quanto maior, mais próximas.", "",
              "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for a, row in zip(names, m):
        lines.append(f"| **{a}** | " + " | ".join("—" if v is None else f"{v:.0f}%" for v in row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cria uma família de línguas a partir de uma protolíngua.")
    ap.add_argument("--language", type=Path, required=True, help="protolíngua (pasta em languages/)")
    ap.add_argument("--branches", type=int, default=3, help="ramos principais (padrão: 3)")
    ap.add_argument("--sub-branches", type=int, default=2, help="sub-ramos de cada ramo (padrão: 2)")
    ap.add_argument("--depth", type=int, default=2, choices=[1, 2, 3], help="níveis da árvore (padrão: 2)")
    ap.add_argument("--years", type=int, default=1500, help="tempo médio de cada divisão, em anos (padrão: 1500)")
    ap.add_argument("--profiles", help="perfis dos ramos principais, separados por vírgula (padrão: sorteados)")
    ap.add_argument("--no-grammar", action="store_true", help="sem a etapa 3 (só sons e léxico)")
    ap.add_argument("--name", help="nome da família (padrão: <protolíngua>-familia)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da protolíngua e das opções)")
    ap.add_argument("--rebuild", action="store_true", help="gera ortografia e grammar.md de cada língua (demora mais)")
    args = ap.parse_args()

    profiles = [p.strip() for p in args.profiles.split(",")] if args.profiles else None
    fb = FamilyBuilder(args.language, args.branches, args.sub_branches, args.depth, args.years, profiles,
                       grammar=not args.no_grammar, seed=args.seed)
    print(f"\nFAMÍLIA — protolíngua {args.language.name}")
    root = fb.build(rebuild=args.rebuild)
    cmp = Comparison(root)
    data = {"cognates": cmp.cognate_table(CORE), "correspondences": cmp.correspondences(),
            "distances": cmp.distances()}
    name = args.name or f"{args.language.name}-familia"
    fam_dir = args.language.parent / name
    fam_dir.mkdir(exist_ok=True)
    tree = [{"name": n.name, "parent": n.parent.name if n.parent else None, "profile": n.profile,
             "years": n.years, "total_years": n.total_years(), "folder": n.dir.name,
             "laws": [x["id"] for x in (n.evo or {}).get("laws", [])]} for n in root.all()]
    (fam_dir / "family.json").write_text(json.dumps(
        {"proto": root.name, "seed": fb.seed, "tree": tree, "cognates": data["cognates"],
         "correspondences": {"languages": data["correspondences"][0], "rows": data["correspondences"][1]},
         "distances": {"languages": data["distances"][0], "matrix": data["distances"][1]}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    write_family(fam_dir / "family.md", root, cmp, data)

    print("\n" + "\n".join(ascii_tree(root)))
    names, m = data["distances"]
    print("\n  Cognatos compartilhados com a protolíngua:")
    for a, row in zip(names[1:], m[1:]):
        print(f"    {a:<22} {row[0]:.0f}%")
    langs, rows = data["correspondences"]
    changed = [r for r in rows if r["changed"]][:6]
    if changed:
        print("\n  Correspondências sonoras (proto → " + ", ".join(langs) + "):")
        for r in changed:
            print(f"    *{r['proto']:<4} → " + "  ".join(r["reflexes"].get(l, {}).get("reflex", "—") for l in langs))
    print(f"\n[OK] Família em '{fam_dir}' (family.md e family.json)"
          + ("" if args.rebuild else "; rode com --rebuild para ter a grafia e o grammar.md de cada língua"))


if __name__ == "__main__":
    main()
