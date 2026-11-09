"""
Módulo — Comparação (comparativo, superlativo e equativo).

Completa a gramática dos adjetivos, como a tabela "Adjectives" do Vulgarlang
(heq-æd 'bigger', heq-ax 'biggest'), mas com as estratégias das línguas reais
(WALS 121A):

    locativa    — 'o cão é grande do peixe'  (o termo comparado vai num caso
                  como ablativo ou locativo; comum em línguas SOV)
    de superar  — 'o cão é grande, supera o peixe'  (verbo 'superar';
                  comum em línguas SVO da África e do Sudeste Asiático)
    conjunta    — 'o cão é grande, o peixe é pequeno'
    partícula   — 'o cão é mais grande que o peixe'  (como no português)

Também decide o superlativo ('o maior'), o equativo ('tão grande quanto') e se
o adjetivo recebe um afixo de grau (como o '-er' / '-est' do inglês).

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico (sândi e flexão), da ortografia e do acento.

Uso:
    python comparison/comparison.py --language languages/lang-31

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "orthography", "stress"):
    sys.path.insert(0, str(ROOT / folder))
from morphological_engine import MorphologicalEngine, gloss as mgloss  # noqa: E402

try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import stress as stress_mod  # noqa: E402
except ImportError:
    stress_mod = None

DEFAULT_WALS = ROOT / "wals" / "cldf"
TONE_LETTERS = "˥˦˧˨˩"

# WALS 121A condicionado à ordem básica (81A); nº de línguas
EMBEDDED_121A_BY_81A = {
    "1": {"1": 40, "2": 2, "3": 11, "4": 3},   # SOV: locativa domina
    "2": {"1": 10, "2": 27, "3": 7, "4": 7},   # SVO: de superar domina
    "3": {"1": 9, "2": 1, "3": 1, "4": 4},     # VSO
    "4": {"3": 1, "4": 2},                      # VOS
    "5": {"1": 1, "3": 2},                      # OVS
    "7": {"1": 5, "3": 6, "4": 4},              # sem ordem dominante
}
EMBEDDED_121A = {"1": 78, "2": 33, "3": 34, "4": 22}
ORDER_81A = {"SOV": "1", "SVO": "2", "VSO": "3", "VOS": "4", "OVS": "5", "OSV": "6"}
STRATEGY_121A = {"1": "locational", "2": "exceed", "3": "conjoined", "4": "particle"}

# Afixo de grau no adjetivo ('-er'), por estratégia (aproximação; Stassen 1985)
P_DEGREE_AFFIX = {"particle": 0.6, "locational": 0.2, "exceed": 0.05, "conjoined": 0.0}

ADJECTIVES = ["BIG", "GOOD", "LONG", "HEAVY", "OLD", "SMALL", "WARM (OF WEATHER)", "COLD (OF WEATHER)"]
ANTONYMS = {"BIG": "SMALL", "SMALL": "BIG", "GOOD": "BAD", "LONG": "SHORT", "OLD": "NEW",
            "HEAVY": "SMALL", "WARM (OF WEATHER)": "COLD (OF WEATHER)", "COLD (OF WEATHER)": "WARM (OF WEATHER)"}
EN_COMPARATIVE = {"good": ("better", "best"), "bad": ("worse", "worst"), "big": ("bigger", "biggest"),
                  "old": ("older", "oldest"), "long": ("longer", "longest"), "heavy": ("heavier", "heaviest"),
                  "small": ("smaller", "smallest"), "warm": ("warmer", "warmest"), "cold": ("colder", "coldest")}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def short(e: Dict) -> str:
    label = (e.get("label") or e["english"].split(" (")[0]).split("/")[0]
    return label[3:] if label.startswith("to ") else label


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class ComparisonBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None, wals_dir: Optional[Path] = None):
        d = language_dir
        self.inv = _load(d / "phonemic_inventory.json")
        self.rules = _load(d / "phonotactics.json")
        self.catdata = _load(d / "grammatical_categories.json")
        self.morph = _load(d / "morphology.json")
        self.lex = _load(d / "lexicon.json")
        self.syntax = _load(d / "syntax.json")
        if not all((self.inv, self.rules, self.catdata, self.morph, self.lex, self.syntax)):
            raise SystemExit(f"A pasta {d} precisa ter inventário, fonotática, categorias, morfologia, "
                             "léxico e sintaxe (gere a língua com o orquestrador).")
        self.cats = self.catdata["categories"]
        typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "comparison") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.wals_dir = wals_dir
        self.sources: Dict[str, str] = {}
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.used = {tuple(self.segments(e["citation"])) for e in self.lex["entries"] if e.get("citation")}
        self.used |= {tuple(p["segments"]) for p in self.lex["pronouns"]["cells"].values()}
        for fm in self.morph["free_markers"].values():
            self.used |= {tuple(w) for w in fm["forms"].values()}
        for v in self.syntax.get("function_words", {}).values():
            self.used.add(tuple(v))
        # formas criadas pelo módulo de posse, se ele já rodou (ex: o possessivo '-il')
        poss = _load(d / "possession.json")
        if poss:
            st_p = poss["settings"]
            self.used |= {tuple(x for x in f if x != " ") for f in st_p["pronominal"]["forms"].values()}
            for key in ("affix", "linker"):
                if st_p["nominal"].get(key):
                    self.used.add(tuple(st_p["nominal"][key]))
            for key in ("alienable_marker", "food_marker", "unpossessed_affix"):
                if st_p["alienability"].get(key):
                    self.used.add(tuple(st_p["alienability"][key]))
        for domain in ("noun", "verb"):  # afixos de grau não repetem afixos existentes
            for slot in self.morph["affixes"][domain]:
                for forms in slot["forms"].values():
                    self.used |= {tuple(x for x in f if x != "+") for f in forms.values() if f}
        st = self.syntax["settings"]
        self.ov = st["word_order"]["object_before_verb"]
        self.order = st["word_order"]["clause"]
        self.free = st["word_order"]["free"]
        self.prepositions = st["adpositions"] == "prepositions"
        self.copula = st.get("copula", "none")
        self.copula_form = self.syntax.get("function_words", {}).get("copula_form")

    # ── utilidades ───────────────────────────────────────────────────────
    def segments(self, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ"), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def new_word(self, syllables: int = 1) -> List[str]:
        for _ in range(60):
            w = [x for syl in self.ph.generate_syllables(syllables) for x in syl]
            if tuple(w) not in self.used:
                self.used.add(tuple(w))
                return w
        return w

    def new_affix(self, kind: str) -> List[str]:
        for _ in range(40):
            a = self.ph.generate_affix(kind)["segments"]
            if tuple(a) not in self.used:
                self.used.add(tuple(a))
                return a
        return a

    def attach(self, base: List[str], affix: List[str], kind: str) -> List[str]:
        if kind == "prefix":
            morphs = [{"segs": list(affix), "role": "prefix", "label": "", "sep": "-"},
                      {"segs": list(base), "role": "root", "label": "", "sep": "-"}]
        else:
            morphs = [{"segs": list(base), "role": "root", "label": "", "sep": "-"},
                      {"segs": list(affix), "role": "suffix", "label": "", "sep": "-"}]
        morphs, _, _ = self.eng.resolve(morphs)
        return [s for m in morphs for s in m["segs"]]

    def word(self, ipa: str, gl: str, seg: Optional[str] = None) -> Dict:
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = self.stress.mark(ipa) if self.stress else ipa
        return {"written": written, "ipa": ipa, "pronunciation": pron, "seg": seg or ipa, "gloss": gl}

    def noun(self, e: Dict, case: Optional[str] = None) -> Dict:
        lex = {"root": e["root"], "form": e["form"], "tones": e.get("tones", []),
               "class": e.get("class") or 0, "gender": e.get("gender")}
        feats = {"case": case} if case else {}
        r = self.eng.inflect(lex, "noun", feats)
        lg = short(e).replace(" ", ".")
        return self.word(r["surface"], lg + (f"-{r['gloss']}" if r["gloss"] else ""), r["underlying"])

    # ── decisões ─────────────────────────────────────────────────────────
    def wals_121a(self) -> Tuple[Dict[str, int], str]:
        code = "7" if self.free else ORDER_81A.get(self.order, "1")
        values = self.wals_dir / "values.csv" if self.wals_dir else None
        if values and values.exists():
            by: Dict[str, Dict[str, str]] = defaultdict(dict)
            with open(values, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    if r["Parameter_ID"] in ("81A", "121A"):
                        by[r["Language_ID"]][r["Parameter_ID"]] = r["Value"]
            c = Counter(d["121A"] for d in by.values() if d.get("81A") == code and "121A" in d)
            if sum(c.values()) >= 5:
                return dict(c), f"WALS 121A|81A={code} (n={sum(c.values())})"
        if code in EMBEDDED_121A_BY_81A and sum(EMBEDDED_121A_BY_81A[code].values()) >= 5:
            return EMBEDDED_121A_BY_81A[code], f"WALS 121A|81A={code} (embutido)"
        return EMBEDDED_121A, "WALS 121A (embutido)"

    def decide(self) -> Dict:
        counts, src = self.wals_121a()
        self.sources["comparative"] = src
        keys = sorted(counts)
        strategy = STRATEGY_121A[self.rng.choices(keys, [counts[k] for k in keys])[0]]

        typ = self.catdata["metadata"]["typology"]
        isolating = typ["synthesis"] == "isolating"
        case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
        s: Dict = {"strategy": strategy}

        if strategy == "locational":
            case = next((c for c in ("ablative", "locative", "allative", "essive") if c in case_vals), None)
            if case:
                s["standard_case"] = case
            else:
                s["standard_marker"] = self.new_word()
        elif strategy == "exceed":
            s["exceed_verb"] = self.new_word(self.rng.choice([1, 2]))
        elif strategy == "particle":
            s["standard_marker"] = self.new_word()

        # grau no adjetivo: afixo ('-er') ou palavra ('mais')
        prefixing = typ["affix_position"] in ("weakly_prefixing", "strongly_prefixing")
        pos = "prefix" if prefixing else "suffix"
        if strategy != "conjoined":
            if not isolating and self.rng.random() < P_DEGREE_AFFIX[strategy]:
                s["degree"] = {"type": "affix", "position": pos, "comparative": self.new_affix(pos)}
            elif strategy == "particle" or self.rng.random() < 0.3:
                s["degree"] = {"type": "word", "comparative": self.new_word()}
            else:
                s["degree"] = {"type": "none"}
        else:
            s["degree"] = {"type": "none"}

        # superlativo
        r = self.rng.random()
        if s["degree"]["type"] == "affix" and r < 0.6:
            s["superlative"] = {"type": "affix", "position": pos, "form": self.new_affix(pos)}
        elif "ALL" in self.entries and r < 0.75 and strategy in ("locational", "exceed", "particle"):
            s["superlative"] = {"type": "universal"}  # 'maior que todos'
        elif r < 0.9:
            s["superlative"] = {"type": "word", "form": self.new_word()}
        else:
            s["superlative"] = {"type": "intensifier", "form": self.new_word()}  # 'muito grande'

        # equativo
        com = next((c for c in ("comitative", "essive") if c in case_vals), None)
        if com and self.rng.random() < 0.4:
            s["equative"] = {"type": "case", "case": com}
        else:
            s["equative"] = {"type": "particle", "form": self.new_word()}
        self.settings = s
        return s

    # ── frases ───────────────────────────────────────────────────────────
    def adjective(self, adj: Dict, degree: Optional[str] = None) -> List[Dict]:
        """Adjetivo, com afixo ou palavra de grau quando houver."""
        base = self.segments(adj["citation"])
        g = short(adj).replace(" ", ".")
        s = self.settings
        if degree == "comparative" and s["degree"]["type"] == "affix":
            d = s["degree"]
            form = "".join(self.attach(base, d["comparative"], d["position"]))
            seg = (f"{''.join(d['comparative'])}-{adj['citation']}" if d["position"] == "prefix"
                   else f"{adj['citation']}-{''.join(d['comparative'])}")
            gl = f"COMPR-{g}" if d["position"] == "prefix" else f"{g}-COMPR"
            return [self.word(form, gl, seg)]
        if degree == "superlative" and s["superlative"]["type"] == "affix":
            sp = s["superlative"]
            form = "".join(self.attach(base, sp["form"], sp["position"]))
            seg = (f"{''.join(sp['form'])}-{adj['citation']}" if sp["position"] == "prefix"
                   else f"{adj['citation']}-{''.join(sp['form'])}")
            gl = f"SUPL-{g}" if sp["position"] == "prefix" else f"{g}-SUPL"
            return [self.word(form, gl, seg)]
        words = [self.word(adj["citation"], g)]
        marker = None
        if degree == "comparative" and s["degree"]["type"] == "word":
            marker = self.word("".join(s["degree"]["comparative"]), "more")
        if degree == "superlative" and s["superlative"]["type"] in ("word", "intensifier"):
            marker = self.word("".join(s["superlative"]["form"]),
                               "most" if s["superlative"]["type"] == "word" else "very")
        if marker:  # a palavra de grau vem do lado em que ficam os modificadores
            words = [marker] + words if not self.ov else words + [marker]
        return words

    def standard(self, e: Dict) -> List[Dict]:
        """O termo de comparação ('que o peixe')."""
        s = self.settings
        if s.get("standard_case"):
            return [self.noun(e, s["standard_case"])]
        n = self.noun(e)
        if s.get("standard_marker"):
            m = self.word("".join(s["standard_marker"]), "than")
            return [m, n] if self.prepositions else [n, m]
        return [n]

    def predicate(self, subj: List[Dict], pred: List[Dict]) -> List[Dict]:
        """Sujeito + predicado adjetival, com cópula se a língua tiver."""
        if self.copula == "word" and self.copula_form:
            cop = self.word("".join(self.copula_form), "COP")
            pred = pred + [cop] if self.ov else [cop] + pred
        return subj + pred

    def sentences(self, x: Dict, y: Dict, adj: Dict) -> List[Dict]:
        s = self.settings
        en_x, en_y, en_a = short(x), short(y), short(adj)
        er, est = EN_COMPARATIVE.get(en_a, (f"more {en_a}", f"most {en_a}"))
        out = []
        X = [self.noun(x)]
        # comparativo
        if s["strategy"] == "conjoined":
            ant = self.entries.get(ANTONYMS.get(adj["gloss"], ""))
            conj = self.entries.get("AND")
            a1 = self.predicate(X, self.adjective(adj))
            if ant:
                a2 = self.predicate([self.noun(y)], self.adjective(ant))
                mid = [self.word(conj["citation"], "and")] if conj else []
                words = a1 + mid + a2
                note = f"literalmente: 'the {en_x} is {en_a}, the {en_y} is {short(ant)}'"
            else:
                words = a1
                note = "sem antônimo no léxico: só a primeira oração"
        elif s["strategy"] == "exceed":
            verb = self.word("".join(s["exceed_verb"]), "exceed")
            Y = [self.noun(y)]
            vp = [verb] + Y if not self.ov else Y + [verb]
            adjw = self.adjective(adj, "comparative")
            words = X + (adjw + vp if not self.ov else vp + adjw)
            note = f"literalmente: 'the {en_x} is {en_a}, it exceeds the {en_y}'"
        else:
            st = self.standard(y)
            adjw = self.adjective(adj, "comparative")
            pred = st + adjw if self.ov else adjw + st  # OV: padrão antes do adjetivo
            words = self.predicate(X, pred)
            note = None
        out.append({"key": "comparative", "title": "Comparativo", "words": words,
                    "translation": f"The {en_x} is {er} than the {en_y}.", "literal": note})
        # superlativo
        sp = s["superlative"]
        if sp["type"] == "universal":
            all_e = self.entries["ALL"]
            if s["strategy"] == "exceed":
                verb = self.word("".join(s["exceed_verb"]), "exceed")
                allw = [self.word(all_e["citation"], "all")]
                vp = [verb] + allw if not self.ov else allw + [verb]
                adjw = self.adjective(adj, "comparative")
                words = X + (adjw + vp if not self.ov else vp + adjw)
            else:
                std = ([self.noun(all_e, s["standard_case"])] if s.get("standard_case") and not self.eng.skeleton
                       else [self.word(all_e["citation"], "all")])
                if s.get("standard_marker"):
                    m = self.word("".join(s["standard_marker"]), "than")
                    std = [m] + std if self.prepositions else std + [m]
                adjw = self.adjective(adj, "comparative")
                words = self.predicate(X, std + adjw if self.ov else adjw + std)
            lit = f"literalmente: 'the {en_x} is {er} than all'"
        else:
            words = self.predicate(X, self.adjective(adj, "superlative"))
            lit = (f"literalmente: 'the {en_x} is very {en_a}'" if sp["type"] == "intensifier" else None)
        out.append({"key": "superlative", "title": "Superlativo", "words": words,
                    "translation": f"The {en_x} is the {est}.", "literal": lit})
        # equativo
        eq = s["equative"]
        if eq["type"] == "case":
            std = [self.noun(y, eq["case"])]
        else:
            m = self.word("".join(eq["form"]), "as")
            n = self.noun(y)
            std = [m, n] if self.prepositions else [n, m]
        adjw = self.adjective(adj)
        words = self.predicate(X, std + adjw if self.ov else adjw + std)
        out.append({"key": "equative", "title": "Equativo", "words": words,
                    "translation": f"The {en_x} is as {en_a} as the {en_y}.", "literal": None})
        return out

    def build(self) -> Dict:
        s = self.decide()
        adj = next((self.entries[g] for g in ADJECTIVES if g in self.entries
                    and (self.entries[g]["pos"] == "adjective" or self.entries[g].get("transitivity") == "stative")), None)
        x = next((self.entries[g] for g in ("DOG", "WOMAN", "TREE", "HOUSE") if g in self.entries
                  and self.entries[g]["pos"] == "noun"), None)
        y = next((self.entries[g] for g in ("FISH", "BIRD", "STONE", "STONE OR ROCK", "CHILD (YOUNG HUMAN)")
                  if g in self.entries and self.entries[g]["pos"] == "noun" and self.entries[g] is not x), None)
        forms, sentences = {}, []
        if adj:
            forms = {"positive": self.adjective(adj), "comparative": self.adjective(adj, "comparative"),
                     "superlative": self.adjective(adj, "superlative")}
            if x and y:
                sentences = self.sentences(x, y, adj)
        else:
            self.notes.append("o léxico não tem adjetivos de tamanho ou qualidade para os exemplos")
        return {"settings": s, "forms": forms, "sentences": sentences,
                "metadata": {"seed": self.seed, "sources": self.sources, "notes": self.notes,
                             "lexemes": {"adjective": short(adj) if adj else None,
                                         "compared": short(x) if x else None,
                                         "standard": short(y) if y else None}}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

STRATEGY_PT = {"locational": "locativa (o termo comparado vai num caso ou adposição de origem/lugar)",
               "exceed": "de superar (verbo 'superar', como em várias línguas da África e da Ásia)",
               "conjoined": "conjunta ('X é grande, Y é pequeno')",
               "particle": "partícula ('mais grande que', como no português)"}


def describe(data: Dict, sp) -> List[str]:
    s = data["settings"]
    lines = [f"Comparativo: {STRATEGY_PT[s['strategy']]}"]
    if s.get("standard_case"):
        lines.append(f"Termo comparado no caso {s['standard_case']}")
    if s.get("standard_marker"):
        lines.append(f"Marca do termo comparado ('que'): {sp(''.join(s['standard_marker']))}")
    if s.get("exceed_verb"):
        lines.append(f"Verbo 'superar': {sp(''.join(s['exceed_verb']))}")
    d = s["degree"]
    if d["type"] == "affix":
        f = sp("".join(d["comparative"]))
        lines.append(f"Grau comparativo no adjetivo: {'-' + f if d['position'] == 'suffix' else f + '-'}")
    elif d["type"] == "word":
        lines.append(f"Palavra de grau ('mais'): {sp(''.join(d['comparative']))}")
    sup = s["superlative"]
    sup_pt = {"affix": "afixo", "universal": "'maior que todos'", "word": "palavra ('o mais')",
              "intensifier": "intensificador ('muito grande')"}[sup["type"]]
    extra = ""
    if sup.get("form"):
        f = sp("".join(sup["form"]))
        extra = " " + ({"suffix": f"-{f}", "prefix": f"{f}-"}.get(sup.get("position"), f) if sup["type"] == "affix" else f)
    lines.append(f"Superlativo: {sup_pt}{extra}")
    eq = s["equative"]
    lines.append("Equativo: " + (f"caso {eq['case']}" if eq["type"] == "case"
                                 else f"partícula ('como') {sp(''.join(eq['form']))}"))
    return lines


def interlinear(sent: Dict) -> List[str]:
    def vis(t: str) -> int:
        return sum(1 for ch in t if unicodedata.category(ch) != "Mn")

    def pad(t: str, w: int) -> str:
        return t + " " * max(0, w - vis(t))
    ws = sent["words"]
    widths = [max(vis(w["written"]), vis(w["seg"]), vis(w["gloss"])) + 2 for w in ws]
    lines = ["".join(pad(w["written"], n) for w, n in zip(ws, widths)).rstrip(),
             "".join(pad(w["seg"], n) for w, n in zip(ws, widths)).rstrip(),
             "".join(pad(w["gloss"], n) for w, n in zip(ws, widths)).rstrip(),
             f"'{sent['translation']}'"]
    if sent.get("literal"):
        lines.append(f"({sent['literal']})")
    return lines


def write_markdown(path: Path, data: Dict, sp) -> None:
    lines = ["# Comparação", ""] + [f"- {l}" for l in describe(data, sp)]
    f = data["forms"]
    if f:
        lines += ["", "## Formas do adjetivo", "", "| Grau | Forma | Pronúncia |", "|---|---|---|"]
        for k, pt in (("positive", "Positivo"), ("comparative", "Comparativo"), ("superlative", "Superlativo")):
            ws = f[k]
            lines.append(f"| {pt} | **{' '.join(w['written'] for w in ws)}** | "
                         f"/{' '.join(w['pronunciation'] for w in ws)}/ |")
    for sent in data["sentences"]:
        written = " ".join(w["written"] for w in sent["words"])
        lines += ["", f"## {sent['title']}", "", f"**{written[:1].upper() + written[1:]}.**", "", "```"]
        lines += interlinear(sent) + ["```"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera comparativo, superlativo e equativo da conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    args = ap.parse_args()

    wals = None if args.no_wals or not args.wals.exists() else args.wals
    b = ComparisonBuilder(args.language, args.seed, wals)
    data = json.loads(json.dumps(b.build()))
    sp = (lambda x: b.ortho.spell(x)) if b.ortho else (lambda x: x)
    (args.language / "comparison.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "comparison.md", data, sp)

    print("\nCOMPARAÇÃO")
    for l in describe(data, sp):
        print(f"  {l}")
    for sent in data["sentences"]:
        print(f"\n  {sent['title']}")
        for l in interlinear(sent):
            print(f"    {l}")
    for n in data["metadata"]["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Comparação salva em '{args.language / 'comparison.json'}' e 'comparison.md'.")


if __name__ == "__main__":
    main()
