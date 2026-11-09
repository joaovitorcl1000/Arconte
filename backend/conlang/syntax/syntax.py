"""
Módulo — Sintaxe.

Define a ordem dos constituintes da conlang (oração, sintagma nominal,
adposições, perguntas, pro-drop) com distribuições e correlações do WALS, e
gera frases de exemplo com glosa interlinear no padrão de Leipzig, usando o
léxico e o motor morfológico.

Entradas:
  ../lexicon/lexicon.json
  ../morphological_engine/morphology.json
  ../grammatical_categories/grammatical_categories.json
  ../phonotactics/phonotactics.json
  ../phonemic_inventory/phonemic_inventory.json
  ../morphological_typology/morphological_typology.json   (opcional)
  ../wals/cldf/values.csv                                 (opcional)

Saídas: syntax.json e examples.md

Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python syntax.py
    python syntax.py --seed 42
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "phonotactics"))
sys.path.insert(0, str(ROOT / "morphological_engine"))
from morphological_engine import (MorphologicalEngine, NOUN_CATS, VERB_CATS,  # noqa: E402
                                  gloss as mgloss)

DEFAULT_LEXICON = ROOT / "lexicon" / "lexicon.json"
DEFAULT_MORPHOLOGY = ROOT / "morphological_engine" / "morphology.json"
DEFAULT_CATEGORIES = ROOT / "grammatical_categories" / "grammatical_categories.json"
DEFAULT_RULES = ROOT / "phonotactics" / "phonotactics.json"
DEFAULT_INVENTORY = ROOT / "phonemic_inventory" / "phonemic_inventory.json"
DEFAULT_TYPOLOGY = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_WALS = ROOT / "wals" / "cldf"
DEFAULT_OUTPUT = HERE / "syntax.json"
DEFAULT_EXAMPLES = HERE / "examples.md"

# ═══════════════════════════════════════════════════════════════════════════
# WALS: ordem básica condicionada à afixação, e demais ordens condicionadas
# à ordem básica (nº de línguas). Usado quando o WALS local não existe.
# ═══════════════════════════════════════════════════════════════════════════

ORDER_81A = {"1": "SOV", "2": "SVO", "3": "VSO", "4": "VOS", "5": "OVS", "6": "OSV", "7": "free"}

EMBEDDED_CONDITIONAL: Dict[Tuple[str, str], Dict[str, Dict[str, int]]] = {
    ("26A", "81A"): {
        "1": {"1": 29, "2": 72, "3": 15, "4": 5, "5": 1, "7": 12},
        "2": {"1": 220, "2": 65, "3": 10, "4": 2, "5": 2, "7": 56},
        "3": {"1": 56, "2": 27, "3": 9, "4": 1, "5": 1, "7": 13},
        "4": {"1": 42, "2": 43, "3": 16, "4": 7, "5": 3, "7": 27},
        "5": {"1": 15, "2": 40, "3": 8, "4": 4, "7": 20},
        "6": {"1": 4, "2": 41, "3": 7, "4": 1, "7": 2},
    },
    ("81A", "85A"): {
        "1": {"1": 374, "2": 11, "3": 2, "4": 14, "5": 7}, "2": {"1": 33, "2": 301, "4": 28, "5": 6},
        "3": {"1": 6, "2": 76, "4": 3}, "4": {"2": 20, "4": 1, "5": 1}, "5": {"1": 8, "2": 3},
        "6": {"1": 3}, "7": {"1": 53, "2": 50, "3": 5, "4": 8, "5": 15},
    },
    ("81A", "86A"): {
        "1": {"1": 398, "2": 26, "3": 17}, "2": {"1": 106, "2": 249, "3": 40},
        "3": {"1": 3, "2": 77, "3": 4}, "4": {"1": 2, "2": 21, "3": 1}, "5": {"1": 5, "2": 2, "3": 2},
        "6": {"1": 3}, "7": {"1": 67, "2": 51, "3": 25},
    },
    ("81A", "87A"): {
        "1": {"1": 182, "2": 268, "3": 22}, "2": {"1": 66, "2": 346, "3": 22},
        "3": {"1": 20, "2": 61, "3": 8}, "4": {"1": 7, "2": 13, "3": 1}, "5": {"1": 2, "2": 6},
        "6": {"1": 1, "2": 2}, "7": {"1": 46, "2": 78, "3": 26},
    },
    ("81A", "88A"): {
        "1": {"1": 258, "2": 119, "3": 5, "4": 6, "5": 4, "6": 17},
        "2": {"1": 84, "2": 296, "4": 9, "5": 4, "6": 16},
        "3": {"1": 30, "2": 39, "4": 7, "5": 1, "6": 8}, "4": {"1": 9, "2": 12, "3": 1, "5": 1},
        "5": {"1": 2, "2": 2}, "6": {"1": 1, "2": 2}, "7": {"1": 88, "2": 38, "4": 5, "5": 1, "6": 14},
    },
    ("81A", "89A"): {
        "1": {"1": 171, "2": 222, "3": 23}, "2": {"1": 118, "2": 252, "3": 14},
        "3": {"1": 59, "2": 20, "3": 2}, "4": {"1": 13, "2": 4, "3": 2}, "5": {"1": 4, "2": 2, "3": 1},
        "6": {"1": 1, "2": 1}, "7": {"1": 70, "2": 32, "3": 12},
    },
    ("81A", "90A"): {
        "1": {"1": 87, "2": 113, "3": 19, "4": 7, "5": 4, "6": 1, "7": 35},
        "2": {"1": 293, "2": 4, "5": 1, "7": 3}, "3": {"1": 68, "7": 2}, "4": {"1": 16, "7": 1},
        "5": {"1": 6, "2": 1, "5": 1}, "6": {"1": 1}, "7": {"1": 70, "2": 2, "3": 2, "5": 2, "7": 12},
    },
    ("81A", "92A"): {
        "1": {"1": 29, "2": 117, "3": 18, "4": 2, "5": 5, "6": 160},
        "2": {"1": 42, "2": 129, "3": 6, "4": 3, "5": 9, "6": 92},
        "3": {"1": 18, "2": 17, "3": 8, "4": 2, "6": 19}, "4": {"1": 6, "2": 3, "5": 1, "6": 4},
        "5": {"2": 1, "6": 5}, "6": {"2": 2, "6": 2}, "7": {"1": 21, "2": 20, "3": 19, "4": 1, "5": 7, "6": 39},
    },
    ("81A", "93A"): {
        "1": {"1": 58, "2": 266, "3": 4}, "2": {"1": 72, "2": 218, "3": 8},
        "3": {"1": 46, "2": 19, "3": 3}, "4": {"1": 10, "2": 3, "3": 2}, "5": {"1": 4, "2": 3, "3": 1},
        "6": {"2": 2}, "7": {"1": 59, "2": 41, "3": 4},
    },
}
EMBEDDED_116A = {"1": 585, "2": 164, "3": 15, "4": 13, "5": 4, "6": 173, "7": 1}

AFFIX_POSITION_26A = {"little_affixation": "1", "strongly_suffixing": "2",
                      "weakly_suffixing": "3", "equal": "4",
                      "weakly_prefixing": "5", "strongly_prefixing": "6"}

# Verbos cujo sujeito é agentivo (para alinhamento ativo-inativo)
AGENTIVE = {"GO", "COME", "RUN", "WALK", "SWIM", "FLY (MOVE THROUGH AIR)", "PLAY", "SING",
            "LAUGH", "FIGHT", "HUNT", "DIG", "CRY", "SPIT", "VOMIT", "TURN AROUND", "SIT", "STAND"}

HUMAN = {"PERSON", "MALE PERSON", "WOMAN", "CHILD (YOUNG HUMAN)", "CHILD (DESCENDANT)",
         "FATHER", "MOTHER", "HUSBAND", "WIFE"}
LONG = {"ROPE", "STICK", "SNAKE", "TREE", "TAIL", "ROAD", "RIVER", "WORM"}

# Morfologia inglesa mínima para as traduções
EN_PLURAL = {"child": "children", "person": "people", "man": "men", "woman": "women",
             "fish": "fish", "louse": "lice", "tooth": "teeth", "foot": "feet", "wife": "wives",
             "leaf": "leaves", "knife": "knives", "sheep": "sheep", "mouse": "mice"}
EN_PAST = {"see": "saw", "eat": "ate", "give": "gave", "come": "came", "go": "went",
           "sleep": "slept", "hold": "held", "know": "knew", "drink": "drank", "bite": "bit",
           "run": "ran", "fall": "fell", "hear": "heard", "say": "said", "take": "took",
           "throw": "threw", "fly": "flew", "swim": "swam", "sing": "sang", "sit": "sat",
           "stand": "stood", "hit": "hit", "cut": "cut", "think": "thought", "fight": "fought",
           "lie": "lay", "blow": "blew", "freeze": "froze", "split": "split", "make": "made"}


# ═══════════════════════════════════════════════════════════════════════════
# WALS
# ═══════════════════════════════════════════════════════════════════════════

class Wals:
    NEEDED = {"26A", "81A", "85A", "86A", "87A", "88A", "89A", "90A", "92A", "93A", "116A"}

    def __init__(self, wals_dir: Optional[Path]):
        self.by_lang: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.live = False
        values = wals_dir / "values.csv" if wals_dir else None
        if values and values.exists():
            with open(values, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    if r["Parameter_ID"] in self.NEEDED:
                        self.by_lang[r["Language_ID"]][r["Parameter_ID"]] = r["Value"]
            self.live = True

    def conditional(self, given: str, value: str, fid: str) -> Tuple[Dict[str, int], str]:
        if self.live:
            c = dict(Counter(d[fid] for d in self.by_lang.values()
                             if fid in d and d.get(given) == value))
            if sum(c.values()) >= 5:
                return c, f"WALS {fid}|{given}={value} (n={sum(c.values())})"
        table = EMBEDDED_CONDITIONAL[(given, fid)]
        return table.get(value, table[max(table, key=lambda k: sum(table[k].values()))]), \
            f"WALS {fid}|{given}={value} (embutido)"

    def marginal(self, fid: str) -> Tuple[Dict[str, int], str]:
        if self.live:
            c = dict(Counter(d[fid] for d in self.by_lang.values() if fid in d))
            return c, f"WALS {fid} (n={sum(c.values())})"
        return EMBEDDED_116A, f"WALS {fid} (embutido)"


# ═══════════════════════════════════════════════════════════════════════════
# Auxiliares
# ═══════════════════════════════════════════════════════════════════════════

def visible_len(s: str) -> int:
    return sum(1 for ch in s if unicodedata.category(ch) != "Mn")


def pad(s: str, w: int) -> str:
    return s + " " * max(0, w - visible_len(s))


def en_base(entry: Dict) -> str:
    """'to go' → 'go'; 'feather (larger...)' → 'feather'; 'flesh/meat' → 'flesh'."""
    w = entry["english"].split(" (")[0]
    if w.startswith("to "):
        w = w[3:]
    return w.split("/")[0].strip()


def en_plural(n: str) -> str:
    if n in EN_PLURAL:
        return EN_PLURAL[n]
    if n.endswith(("s", "sh", "ch", "x")):
        return n + "es"
    if n.endswith("y") and n[-2:-1] not in "aeiou":
        return n[:-1] + "ies"
    return n + "s"


def en_3sg(v: str) -> str:
    head, _, rest = v.partition(" ")
    if head == "be":
        return "is" + (" " + rest if rest else "")
    if head.endswith(("s", "sh", "ch", "x", "o")):
        head += "es"
    elif head.endswith("y") and head[-2:-1] not in "aeiou":
        head = head[:-1] + "ies"
    else:
        head += "s"
    return head + (" " + rest if rest else "")


def en_past(v: str) -> str:
    head, _, rest = v.partition(" ")
    if head in EN_PAST:
        head = EN_PAST[head]
    elif head.endswith("e"):
        head += "d"
    elif head.endswith("y") and head[-2:-1] not in "aeiou":
        head = head[:-1] + "ied"
    else:
        head += "ed"
    return head + (" " + rest if rest else "")


def lex_gloss(entry: Dict) -> str:
    return en_base(entry).replace(" ", ".").rstrip("?")


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class SyntaxBuilder:
    def __init__(self, eng: MorphologicalEngine, lexicon: Dict, typology: Dict,
                 wals: Wals, seed: Optional[int] = None):
        self.eng = eng
        self.cats = eng.cats
        self.lex = lexicon
        self.by_gloss = {e["gloss"]: e for e in lexicon["entries"]}
        self.typology = typology
        self.wals = wals
        self.rng = random.Random(seed)
        self.seed = seed
        self.sources: Dict[str, str] = {}
        self.notes: List[str] = []
        self.s: Dict = {}

    # ── decisões ─────────────────────────────────────────────────────────
    def _pick(self, key: str, counts: Dict[str, int], src: str, drop=()) -> str:
        w = {k: v for k, v in counts.items() if k not in drop and v > 0}
        self.sources[key] = src
        keys = sorted(w)
        return self.rng.choices(keys, [w[k] for k in keys])[0]

    def _side(self, code: str, before: str, after: str) -> str:
        if code == before:
            return "before"
        if code == after:
            return "after"
        return self.rng.choice(["before", "after"])  # sem ordem dominante

    def decide(self) -> Dict:
        affix = self.eng.catdata["metadata"]["typology"]["affix_position"]
        g26 = AFFIX_POSITION_26A.get(affix, "2")
        o = self._pick("word_order", *self.wals.conditional("26A", g26, "81A"))
        free = o == "7"
        basic = o
        if free:  # ordem pragmaticamente neutra usada nos exemplos
            counts, _ = self.wals.conditional("26A", g26, "81A")
            basic = self.rng.choices([k for k in sorted(counts) if k != "7"],
                                     [counts[k] for k in sorted(counts) if k != "7"])[0]
        order = ORDER_81A[basic]
        ov = order.index("O") < order.index("V")

        adp = self._pick("adpositions", *self.wals.conditional("81A", o, "85A"))
        adposition = {"1": "postpositions", "2": "prepositions", "3": "postpositions",
                      "5": "none"}.get(adp, self.rng.choice(["postpositions", "prepositions"]))
        gen = self._side(self._pick("genitive", *self.wals.conditional("81A", o, "86A")), "1", "2")
        adj = self._side(self._pick("adjective", *self.wals.conditional("81A", o, "87A")), "1", "2")
        dem = self._side(self._pick("demonstrative", *self.wals.conditional("81A", o, "88A")), "1", "2")
        num = self._side(self._pick("numeral", *self.wals.conditional("81A", o, "89A")), "1", "2")
        rel_code = self._pick("relative", *self.wals.conditional("81A", o, "90A"))
        relative = {"1": "after_noun", "2": "before_noun", "3": "internally_headed",
                    "4": "correlative", "5": "adjoined", "6": "doubly_headed"}.get(
            rel_code, self.rng.choice(["after_noun", "before_noun"]))

        q = self._pick("polar_questions", *self.wals.marginal("116A"))
        strategy = {"1": "particle", "2": "verb_morphology", "3": "particle",
                    "4": "word_order", "5": "intonation", "6": "intonation", "7": "intonation"}[q]
        polar: Dict = {"strategy": strategy}
        if strategy == "particle":
            pos = self._pick("question_particle", *self.wals.conditional("81A", o, "92A"),
                             drop=("6",))
            polar["position"] = {"1": "initial", "2": "final", "3": "second"}.get(
                pos, self.rng.choice(["initial", "final"]))
        wh = self._pick("content_questions", *self.wals.conditional("81A", o, "93A"))
        wh_pos = {"1": "initial", "2": "in_situ"}.get(wh, self.rng.choice(["initial", "in_situ"]))

        ag = self.cats.get("agreement", {})
        subj_marked = ag.get("grammaticalized") and "A" in ag.get("arguments", {})
        pro_drop = self.rng.random() < (0.9 if subj_marked else 0.35)
        self.sources["pro_drop"] = "concordância de sujeito no verbo (Dryer 2013, WALS 101A)"

        adjectives = self.lex["settings"]["adjectives"]
        copula = "none"
        if adjectives != "verbal":
            copula = "zero" if self.rng.random() < 0.5 else "word"

        compound = self.lex["settings"]["compound_head"]
        harmonic = (compound == "final") == (gen == "before")

        self.s = {
            "word_order": {"clause": order, "free": free, "object_before_verb": ov},
            "adpositions": adposition,
            "noun_phrase": {"genitive": gen, "adjective": adj, "demonstrative": dem,
                            "numeral": num, "relative_clause": relative},
            "polar_questions": polar,
            "content_questions": wh_pos,
            "pro_drop": pro_drop,
            "copula": copula,
            "negation": {"realization": self.cats["negation"]["realization"],
                         "position": self.cats["negation"].get("position")},
            "compounds": {"head": compound, "harmonic_with_genitive": harmonic},
        }
        if free:
            self.notes.append(f"sem ordem dominante: exemplos usam {order}, mas outras ordens são possíveis")
        if not harmonic:
            self.notes.append("ordem dos compostos desarmônica com a do genitivo "
                              "(possível, mas menos comum)")
        return self.s

    # ── palavras gramaticais novas ───────────────────────────────────────
    def _function_word(self) -> List[str]:
        used = {tuple(e["root"]) for e in self.lex["entries"]}
        used |= {tuple(p["segments"]) for p in self.lex["pronouns"]["cells"].values()}
        for fm in self.eng.spec["free_markers"].values():  # partículas já existentes
            used |= {tuple(w) for w in fm["forms"].values()}
        used |= {tuple(self.s.get(k, [])) for k in ("question_particle", "copula_form")}
        for _ in range(80):
            w = self.eng.ph.generate_syllables(1)[0]
            if tuple(w) not in used:
                return w
        return self.eng.ph.generate_syllables(1)[0]

    # ── escolha de lexemas ───────────────────────────────────────────────
    def pick(self, prefs: List[str], pos=None, cond=lambda e: True) -> Optional[Dict]:
        for g in prefs:
            e = self.by_gloss.get(g)
            if e and e.get("root") and (pos is None or e["pos"] in pos) and cond(e):
                return e
        pool = [e for e in self.lex["entries"] if e.get("root") and (pos is None or e["pos"] in pos)
                and cond(e)]
        return self.rng.choice(pool) if pool else None

    # ── morfossintaxe ────────────────────────────────────────────────────
    def case_for(self, role: str, verb: Optional[Dict] = None) -> Optional[str]:
        c = self.cats["case"]
        if not c.get("grammaticalized"):
            return None
        vals, al = c["values"], c["alignment"]
        core = {"neutral": ("direct", "direct", "direct"),
                "nominative_accusative": ("nominative", "nominative", "accusative"),
                "marked_nominative": ("nominative", "nominative", "accusative"),
                "ergative_absolutive": ("absolutive", "ergative", "absolutive"),
                "tripartite": ("intransitive", "ergative", "accusative"),
                "active_inactive": ("patientive", "agentive", "patientive")}[al]
        if role == "S":
            if al == "active_inactive" and verb and verb["gloss"] in AGENTIVE:
                return "agentive"
            return core[0]
        if role == "A":
            return core[1]
        if role == "P":
            return core[2]
        options = {"R": ["dative", "allative", "locative"], "POSS": ["genitive"],
                   "LOC": ["locative", "essive", "allative"]}[role]
        found = next((v for v in options if v in vals), None)
        if found or role != "R":
            return found
        return core[2]

    def agreement_value(self, person: str, number: str) -> str:
        cells = self.eng.agreement_cells()
        for cand in (f"{person}.{number}", f"{person.rstrip('inclex') or person}.{number}",
                     f"{person}.plural" if number != "singular" else "", "3.singular"):
            if cand in cells:
                return cand
        return "3.singular"

    def verb_agreement(self, transitive: bool, subj: str, obj: Optional[str]) -> Dict:
        ag = self.cats.get("agreement", {})
        if not ag.get("grammaticalized"):
            return {}
        args, al = ag["arguments"], ag["alignment"]
        f: Dict = {}
        if transitive:
            if "A" in args:
                f["agreement_A"] = subj
            if "P" in args:
                f["agreement_P"] = obj
            return f
        if al == "ergative" and "P" in args:
            f["agreement_P"] = subj
            if "A" in args:
                f["agreement_A"] = None
        elif "A" in args:
            f["agreement_A"] = subj
            if "P" in args:
                f["agreement_P"] = None
        else:
            f["agreement_P"] = None
        return f

    # ── palavras ─────────────────────────────────────────────────────────
    @staticmethod
    def _lexeme(e: Dict) -> Dict:
        return {"root": e["root"], "form": e["form"], "tones": e.get("tones", []),
                "class": e.get("class") or 0, "gender": e.get("gender")}

    def _free_words(self, domain: str, feats: Dict) -> Tuple[List[Dict], List[Dict]]:
        cats = NOUN_CATS if domain == "noun" else VERB_CATS
        full = {**self.eng.defaults(domain), **{k: v for k, v in feats.items() if v is not None}}
        before, after = [], []
        for cat, fm in self.eng.spec["free_markers"].items():
            if cat not in cats:
                continue
            v = full.get(cat)
            if cat == "negation" and v != "negative":
                continue
            if v in fm["forms"]:
                segs = fm["forms"][v]
                w = {"form": "".join(segs), "seg": "".join(segs), "gloss": mgloss(v) or v.upper()}
                (before if fm["positions"][v] == "before" else after).append(w)
        return before, after

    def morpheme_gloss(self, e: Dict, domain: str, feats: Dict, root_gloss: str) -> str:
        """
        Glosa morfema a morfema, alinhada com a forma segmentada do motor:
        refaz a montagem de inflect() e glosa só os morfemas que têm forma.
        Processos não lineares vão colados à raiz com barra invertida (Leipzig: sing\\PST).
        """
        eng = self.eng
        lex = self._lexeme(e)
        full = {**eng.defaults(domain), **feats}
        if domain == "noun" and lex.get("gender"):
            full["gender"] = lex["gender"]
        _, _, fallback, redup = eng._stem(lex, domain, full)
        nonlin, fb = [], []
        for p in eng.spec["nonlinear"]["processes"][domain]:
            v = full.get(p["category"])
            if v is None or v == self.cats[p["category"]]["default"]:
                continue
            if v in p.get("fallback_affixes", {}):
                fb.append(mgloss(v))
            elif p["realization"] in ("stem_change", "tone", "transfix") or (
                    p["realization"] == "reduplication" and v != p.get("value")):
                nonlin.append(mgloss(v))
        root = root_gloss + ("\\" + ".".join(nonlin) if nonlin else "")
        pre: List[str] = []
        post: List[str] = []
        for slot in eng.spec["affixes"][domain]:
            values = [full.get(u, eng.unit_default(u)) for u in slot["categories"]]
            if None in values:
                continue
            key = eng.cell_key(slot["categories"], values)
            cls = str(lex.get("class", 0)) if slot["class_dependent"] else "0"
            segs = slot["forms"].get(cls, slot["forms"]["0"]).get(key, [])
            if not segs:
                continue
            if "+" in segs:  # pessoa e número em afixos separados
                person, number = values[0].split(".", 1)
                glosses = [person.upper(), mgloss(number)]
            else:
                glosses = [".".join(g for g in (mgloss(v) for v in values) if g) or "?"]
            sep = "=" if slot["realization"] == "clitic" else "-"
            if slot["position"] == "prefix":
                pre += [g + sep for g in glosses]
            else:
                post += [sep + g for g in glosses]
        if redup:
            red = next((p for p in eng.spec["nonlinear"]["processes"][domain]
                        if p["realization"] == "reduplication"), None)
            pre.append(f"{mgloss(full[red['category']])}-" if red else "RED-")
        return "".join(pre) + root + "".join("-" + g for g in fb) + "".join(post)

    def noun_word(self, e: Dict, feats: Dict) -> List[Dict]:
        f = {k: v for k, v in feats.items() if v is not None}
        if e["pos"] == "pronoun" or e.get("pronoun"):
            if self.eng.skeleton or "case" not in f:
                return [{"form": e["form"], "seg": e["form"], "gloss": e["pgloss"]}]
            r = self.eng.inflect(self._lexeme(e), "noun", {"case": f["case"]})
            return [{"form": r["surface"], "seg": r["underlying"],
                     "gloss": self.morpheme_gloss(e, "noun", {"case": f["case"]}, e["pgloss"])}]
        r = self.eng.inflect(self._lexeme(e), "noun", f)
        before, after = self._free_words("noun", f)
        word = {"form": r["surface"], "seg": r["underlying"],
                "gloss": self.morpheme_gloss(e, "noun", f, lex_gloss(e))}
        return before + [word] + after

    def verb_words(self, e: Dict, feats: Dict) -> List[Dict]:
        r = self.eng.inflect(self._lexeme(e), "verb", feats)
        before, after = self._free_words("verb", feats)
        word = {"form": r["surface"], "seg": r["underlying"],
                "gloss": self.morpheme_gloss(e, "verb", feats, lex_gloss(e))}
        return before + [word] + after

    def plain_word(self, e: Dict) -> Dict:
        form = e["citation"] or e["form"]
        seg = "".join(ch for ch in form if ch not in "˥˦˧˨˩.")  # linha segmentada sem tons
        return {"form": form, "seg": seg, "gloss": lex_gloss(e)}

    def pronoun(self, cell: str) -> Optional[Dict]:
        cells = self.lex["pronouns"]["cells"]
        key = next((k for k in cells if k == cell or k.startswith(cell + ".")), None)
        if not key:
            return None
        p = cells[key]
        return {"root": p["segments"], "form": p["form"], "tones": [], "pos": "pronoun",
                "pronoun": True, "gloss": key, "pgloss": mgloss(".".join(key.split(".")[:2])),
                "english": key, "class": 0}

    # ── sintagma nominal ─────────────────────────────────────────────────
    def noun_phrase(self, e: Dict, role: str, verb: Optional[Dict] = None, number: str = "singular",
                    dem: Optional[Dict] = None, num: Optional[Dict] = None,
                    adj: Optional[Dict] = None, poss: Optional[Dict] = None) -> List[Dict]:
        np_ = self.s["noun_phrase"]
        feats: Dict = {}
        if self.cats["number"].get("grammaticalized") and e["pos"] != "pronoun":
            feats["number"] = number if number in self.cats["number"]["values"] else "singular"
        case = self.case_for(role, verb)
        if case:
            feats["case"] = case
        head = self.noun_word(e, feats)

        pre, post = [], []
        mods = []  # (tipo, palavras); ordem universal 20 de Greenberg: Dem Num Adj N / N Adj Num Dem
        if dem:
            mods.append(("demonstrative", [self.plain_word(dem)]))
        if num:
            words = [self.plain_word(num)]
            cl = self.classifier(e)
            if cl:
                words = words + [cl] if self.eng.spec["free_markers"]["classifiers"]["positions"].get(
                    cl["value"]) == "after" else [cl] + words
            mods.append(("numeral", words))
        if adj:
            mods.append(("adjective", [self.plain_word(adj)]))
        for kind, words in mods:
            (pre if np_[kind] == "before" else post).append(words)
        post.reverse()  # espelho: N Adj Num Dem
        if poss:
            pw = self.noun_phrase(poss, "POSS")
            (pre.insert(0, pw) if np_["genitive"] == "before" else post.append(pw))
        return [w for group in pre for w in group] + head + [w for group in post for w in group]

    def classifier(self, noun: Dict) -> Optional[Dict]:
        cl = self.cats.get("classifiers", {})
        fm = self.eng.spec["free_markers"].get("classifiers")
        if not cl.get("grammaticalized") or not fm or (not cl["obligatory"] and self.rng.random() < 0.5):
            return None
        g = noun["gloss"]
        want = ("human" if g in HUMAN else "animal" if noun.get("field") == "Animals"
                else "long_thin" if g in LONG else "general")
        value = want if want in fm["forms"] else "general"
        if value not in fm["forms"]:
            return None
        form = "".join(fm["forms"][value])
        return {"form": form, "seg": form, "gloss": f"CL.{value.upper()}", "value": value}

    # ── oração ───────────────────────────────────────────────────────────
    def clause(self, constituents: Dict[str, List[Dict]], loc: Optional[List[Dict]] = None) -> List[List[Dict]]:
        order = self.s["word_order"]["clause"]
        seq = []
        for role in order:
            key = {"S": "S", "O": "O", "V": "V"}[role]
            if key == "O":
                # OV: recipiente antes do objeto (S R O V); VO: objeto antes do recipiente (V O R)
                ov = self.s["word_order"]["object_before_verb"]
                parts = ([constituents.get("R"), constituents.get("O")] if ov
                         else [constituents.get("O"), constituents.get("R")])
                seq += [p for p in parts if p]
            elif constituents.get(key):
                seq.append(constituents[key])
        if loc:  # adjunto: junto ao verbo, do lado oposto ao objeto em VO, antes do V em OV
            vi = next(i for i, c in enumerate(seq) if c is constituents["V"])
            if self.s["word_order"]["object_before_verb"]:
                seq.insert(vi, loc)
            else:
                seq.insert(len(seq), loc)
        return seq

    def subject(self, words: List[Dict], is_pronoun: bool) -> Optional[List[Dict]]:
        if is_pronoun and self.s["pro_drop"]:
            return None
        return words

    def tense_feats(self, past: bool) -> Tuple[Dict, str]:
        """Passado (ou perfectivo) se a língua tiver; devolve traços e um rótulo."""
        if not past:
            return {}, "present"
        t = self.cats["tense"]
        if t.get("grammaticalized"):
            v = next((x for x in t["values"] if "past" in x and x != "non_past"), None)
            if v:
                return {"tense": v}, "past"
        a = self.cats["aspect"]
        if a.get("grammaticalized") and "perfective" in a["values"]:
            return {"aspect": "perfective"}, "past"
        return {}, "present"

    # ── frases de exemplo ────────────────────────────────────────────────
    def examples(self) -> List[Dict]:
        out = []
        P = self.pick
        animate = lambda e: e["gloss"] in HUMAN or e.get("field") == "Animals"
        intr = lambda e: e.get("transitivity") == "intransitive"
        trans = lambda e: e.get("transitivity") == "transitive"

        child = P(["CHILD (YOUNG HUMAN)", "CHILD (DESCENDANT)", "PERSON"], ["noun"], animate)
        woman = P(["WOMAN", "PERSON", "MALE PERSON", "MOTHER"], ["noun"],
                  lambda e: animate(e) and e is not child)
        dog = P(["DOG", "BIRD", "FISH", "ANIMAL"], ["noun"],
                lambda e: animate(e) and e not in (child, woman))
        thing = P(["FISH", "BIRD", "STONE", "STONE OR ROCK", "EGG", "WATER"], ["noun"],
                  lambda e: e not in (child, woman, dog))
        house = P(["HOUSE", "STONE", "STONE OR ROCK", "TREE", "WATER"], ["noun"],
                  lambda e: e not in (child, woman, dog))
        sleep = P(["SLEEP", "GO", "COME", "RUN", "DIE", "LAUGH"], ["verb"], intr)
        go = P(["COME", "GO", "RUN", "WALK"], ["verb"], intr)
        see = P(["SEE", "HEAR", "HOLD", "HIT", "KILL"], ["verb"], trans)
        eat = P(["EAT", "BITE", "DRINK", "HOLD"], ["verb"], trans)
        give = P(["GIVE"], ["verb"])
        big = P(["BIG", "GOOD", "SMALL", "RED", "BLACK", "NEW"], ["adjective", "verb"],
                lambda e: e["pos"] == "adjective" or e.get("transitivity") == "stative")
        this = P(["THIS", "THAT"], ["demonstrative"])
        two = P(["TWO", "THREE", "ONE"], ["numeral"], lambda e: e["gloss"] != "ONE")
        what = P(["WHAT", "WHO"], ["interrogative"])
        adp = self.by_gloss.get("IN") or self.by_gloss.get("AT")

        def add(key, title, words, translation):
            out.append({"key": key, "title": title, "words": words, "translation": translation})

        def flat(seq):
            return [w for c in seq if c for w in c]

        def agr_np(number="singular"):
            return self.agreement_value("3", number)

        # 1. intransitiva
        if child and sleep:
            S = self.noun_phrase(child, "S", sleep)
            V = self.verb_words(sleep, self.verb_agreement(False, agr_np(), None))
            add("intransitive", "Oração intransitiva", flat(self.clause({"S": S, "V": V})),
                f"The {en_base(child)} {en_3sg(en_base(sleep))}.")
        # 2. transitiva
        if woman and see and thing:
            A = self.noun_phrase(woman, "A")
            O = self.noun_phrase(thing, "P")
            V = self.verb_words(see, self.verb_agreement(True, agr_np(), agr_np()))
            add("transitive", "Oração transitiva", flat(self.clause({"S": A, "O": O, "V": V})),
                f"The {en_base(woman)} {en_3sg(en_base(see))} the {en_base(thing)}.")
        # 3. passado com objeto plural
        if dog and eat and thing:
            tf, label = self.tense_feats(True)
            pl = "plural" if self.cats["number"].get("grammaticalized") else "singular"
            A = self.noun_phrase(dog, "A")
            O = self.noun_phrase(thing, "P", number=pl)
            V = self.verb_words(eat, {**tf, **self.verb_agreement(True, agr_np(), agr_np(pl))})
            obj = en_plural(en_base(thing)) if pl == "plural" else en_base(thing)
            vb = en_past(en_base(eat)) if label == "past" else en_3sg(en_base(eat))
            title = ("Passado" if label == "past" else "Presente (sem passado gramatical)") + \
                (", objeto plural" if pl == "plural" else "")
            add("past", title, flat(self.clause({"S": A, "O": O, "V": V})),
                f"The {en_base(dog)} {vb} the {obj}.")
        # 4. bitransitiva
        if give and woman and child and thing:
            A = self.noun_phrase(woman, "A")
            R = self.noun_phrase(child, "R")
            O = self.noun_phrase(thing, "P")
            V = self.verb_words(give, self.verb_agreement(True, agr_np(), agr_np()))
            add("ditransitive", "Oração bitransitiva",
                flat(self.clause({"S": A, "O": O, "R": R, "V": V})),
                f"The {en_base(woman)} gives the {en_base(thing)} to the {en_base(child)}.")
        # 5. pronomes (pro-drop)
        i, you = self.pronoun("1.singular"), self.pronoun("2.singular")
        if i and you and see:
            A = self.subject(self.noun_phrase(i, "A"), True)
            O = self.noun_phrase(you, "P")
            V = self.verb_words(see, self.verb_agreement(True, self.agreement_value("1", "singular"),
                                                         self.agreement_value("2", "singular")))
            add("pronouns", "Pronomes" + (" (sujeito omitido: pro-drop)" if self.s["pro_drop"] else ""),
                flat(self.clause({"S": A, "O": O, "V": V})), f"I {en_base(see)} you.")
        # 6. sintagma nominal complexo
        if dog and go and (this or two or big):
            pl = "plural" if two and self.cats["number"].get("grammaticalized") else "singular"
            S = self.noun_phrase(dog, "S", go, number=pl, dem=this, num=two, adj=big)
            V = self.verb_words(go, self.verb_agreement(False, agr_np(pl), None))
            parts = ([("these" if pl == "plural" else "this") if this else "the"]
                     + ([en_base(two)] if two else []) + ([en_base(big)] if big else [])
                     + [en_plural(en_base(dog)) if pl == "plural" else en_base(dog)])
            vb = en_base(go) if pl == "plural" else en_3sg(en_base(go))
            add("noun_phrase", "Sintagma nominal (demonstrativo, numeral, adjetivo)",
                flat(self.clause({"S": S, "V": V})), f"{' '.join(parts).capitalize()} {vb}.")
        # 7. posse
        if dog and woman and sleep:
            S = self.noun_phrase(dog, "S", sleep, poss=woman)
            V = self.verb_words(sleep, self.verb_agreement(False, agr_np(), None))
            add("possession", "Posse (genitivo)", flat(self.clause({"S": S, "V": V})),
                f"The {en_base(woman)}'s {en_base(dog)} {en_3sg(en_base(sleep))}.")
        # 8. local
        if child and sleep and house:
            S = self.noun_phrase(child, "S", sleep)
            V = self.verb_words(sleep, self.verb_agreement(False, agr_np(), None))
            loc_case = self.case_for("LOC")
            if loc_case:
                L = self.noun_phrase(house, "LOC")
            else:
                L = self.noun_phrase(house, "P") if self.cats["case"].get("grammaticalized") \
                    else self.noun_word(house, {})
                if adp and adp.get("root") and self.s["adpositions"] != "none":
                    w = self.plain_word(adp)
                    L = [w] + L if self.s["adpositions"] == "prepositions" else L + [w]
            add("location", "Adjunto locativo", flat(self.clause({"S": S, "V": V}, loc=L)),
                f"The {en_base(child)} {en_3sg(en_base(sleep))} in the {en_base(house)}.")
        # 9. predicado adjetival
        if big and thing:
            S = self.noun_phrase(thing, "S", big)
            if big["pos"] == "verb":
                V = self.verb_words(big, self.verb_agreement(False, agr_np(), None))
                seq = self.clause({"S": S, "V": V})
            else:
                pred = [self.plain_word(big)]
                if self.s["copula"] == "word":
                    if "copula_form" not in self.s:
                        self.s["copula_form"] = self._function_word()
                    c = "".join(self.s["copula_form"])
                    cop = {"form": c, "seg": c, "gloss": "COP"}
                    pred = pred + [cop] if self.s["word_order"]["object_before_verb"] else [cop] + pred
                seq = self.clause({"S": S, "V": pred})
            add("predicate_adjective", "Predicado adjetival"
                + (" (adjetivo verbal)" if big["pos"] == "verb" else
                   f" (cópula {'zero' if self.s['copula'] == 'zero' else 'explícita'})"),
                flat(seq), f"The {en_base(thing)} is {en_base(big)}.")
        # 10. negação
        if child and sleep:
            S = self.noun_phrase(child, "S", sleep)
            V = self.verb_words(sleep, {"negation": "negative",
                                        **self.verb_agreement(False, agr_np(), None)})
            add("negation", "Negação", flat(self.clause({"S": S, "V": V})),
                f"The {en_base(child)} does not {en_base(sleep)}.")
        # 11. pergunta sim/não
        if woman and see and thing:
            A = self.noun_phrase(woman, "A")
            O = self.noun_phrase(thing, "P")
            V = self.verb_words(see, self.verb_agreement(True, agr_np(), agr_np()))
            seq = self.polar(self.clause({"S": A, "O": O, "V": V}), V)
            add("polar_question", "Pergunta sim/não", flat(seq),
                f"Does the {en_base(woman)} {en_base(see)} the {en_base(thing)}?")
        # 12. pergunta de conteúdo
        if woman and see and what:
            A = self.noun_phrase(woman, "A")
            Wq = self.noun_word({**what, "pos": "noun"}, {"case": self.case_for("P")}) \
                if not self.eng.skeleton else [self.plain_word(what)]
            V = self.verb_words(see, self.verb_agreement(True, agr_np(), agr_np()))
            seq = self.clause({"S": A, "O": Wq, "V": V})
            if self.s["content_questions"] == "initial":
                seq = [Wq] + [c for c in seq if c is not Wq]
            add("content_question", "Pergunta de conteúdo ("
                + ("palavra interrogativa no início" if self.s["content_questions"] == "initial"
                   else "palavra interrogativa in situ") + ")",
                flat(seq), f"What does the {en_base(woman)} {en_base(see)}?")
        return out

    def polar(self, seq: List[List[Dict]], verb: List[Dict]) -> List[List[Dict]]:
        p = self.s["polar_questions"]
        if p["strategy"] in ("particle", "verb_morphology") and "question_particle" not in self.s:
            self.s["question_particle"] = self._function_word()
        q = "".join(self.s.get("question_particle", []))
        if p["strategy"] == "particle":
            word = [{"form": q, "seg": q, "gloss": "Q"}]
            if p["position"] == "initial":
                return [word] + seq
            if p["position"] == "second":
                return seq[:1] + [word] + seq[1:]
            return seq + [word]
        if p["strategy"] == "verb_morphology":  # enclítico interrogativo no verbo
            main = next(w for w in verb if not w["gloss"].isupper())
            main.update(form=main["form"] + q, seg=main["seg"] + "=" + q, gloss=main["gloss"] + "=Q")
            return seq
        if p["strategy"] == "word_order":  # verbo vai para o início
            return [verb] + [c for c in seq if c is not verb]
        return seq  # só entonação


# ═══════════════════════════════════════════════════════════════════════════
# Exibição
# ═══════════════════════════════════════════════════════════════════════════

LABELS = {"before": "antes do nome", "after": "depois do nome", "after_noun": "depois do nome",
          "before_noun": "antes do nome", "internally_headed": "núcleo interno",
          "correlative": "correlativa", "adjoined": "adjunta", "doubly_headed": "dois núcleos",
          "postpositions": "posposições", "prepositions": "preposições", "none": "nenhuma",
          "initial": "no início", "final": "no fim", "second": "na 2ª posição",
          "in_situ": "in situ", "particle": "partícula", "verb_morphology": "morfologia verbal",
          "word_order": "inversão (verbo no início)", "intonation": "só entonação",
          "zero": "zero", "word": "palavra própria"}


def interlinear(ex: Dict) -> List[str]:
    words = ex["words"]
    widths = [max(visible_len(w["form"]), visible_len(w["seg"]), visible_len(w["gloss"])) + 2
              for w in words]
    line1 = "".join(pad(w["form"], n) for w, n in zip(words, widths)).rstrip()
    line2 = "".join(pad(w["seg"], n) for w, n in zip(words, widths)).rstrip()
    line3 = "".join(pad(w["gloss"], n) for w, n in zip(words, widths)).rstrip()
    lines = [line1]
    if line2 != line1:
        lines.append(line2)
    lines += [line3, f"'{ex['translation']}'"]
    return lines


def describe(s: Dict) -> List[str]:
    wo, np_ = s["word_order"], s["noun_phrase"]
    polar = s["polar_questions"]
    pq = LABELS[polar["strategy"]] + (f" {LABELS[polar['position']]}" if polar.get("position") else "")
    return [
        f"Ordem básica: {wo['clause']}" + (" (ordem livre; esta é a neutra)" if wo["free"] else ""),
        f"Adposições: {LABELS[s['adpositions']]}",
        f"Genitivo {LABELS[np_['genitive']]}; adjetivo {LABELS[np_['adjective']]}; "
        f"demonstrativo {LABELS[np_['demonstrative']]}; numeral {LABELS[np_['numeral']]}",
        f"Oração relativa: {LABELS[np_['relative_clause']]}",
        f"Perguntas sim/não: {pq}; perguntas de conteúdo: {LABELS[s['content_questions']]}",
        f"Pro-drop: {'sim' if s['pro_drop'] else 'não'}; cópula: "
        f"{LABELS.get(s['copula'], 'adjetivos são verbos')}",
        f"Compostos: núcleo {s['compounds']['head']} "
        f"({'harmônico' if s['compounds']['harmonic_with_genitive'] else 'desarmônico'} com o genitivo)",
    ]


def print_summary(data: Dict) -> None:
    print("\nSINTAXE")
    for line in describe(data["settings"]):
        print("  " + line)
    for ex in data["examples"]:
        print(f"\n{ex['title']}")
        for line in interlinear(ex):
            print("  " + line)
    if data["metadata"]["notes"]:
        print("\nNotas: " + "; ".join(data["metadata"]["notes"]))


def write_examples(path: Path, data: Dict) -> None:
    lines = ["# Sintaxe e frases de exemplo", ""]
    lines += [f"- {l}" for l in describe(data["settings"])]
    for i, ex in enumerate(data["examples"], 1):
        lines += ["", f"## {i}. {ex['title']}", "", "```"] + interlinear(ex) + ["```"]
    if data["metadata"]["notes"]:
        lines += ["", "## Notas", ""] + [f"- {n}" for n in data["metadata"]["notes"]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def _load(path: Path, hint: str) -> Dict:
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}\nRode antes: {hint}")
    return json.loads(path.read_text(encoding="utf-8"))


def build(eng: MorphologicalEngine, lexicon: Dict, typology: Dict, wals: Wals,
          seed: Optional[int]) -> Dict:
    sb = SyntaxBuilder(eng, lexicon, typology, wals, seed)
    settings = sb.decide()
    examples = sb.examples()
    function_words = {k: settings.pop(k) for k in ("question_particle", "copula_form") if k in settings}
    return {"settings": settings, "function_words": function_words, "examples": examples,
            "metadata": {"seed": seed, "sources": sb.sources, "notes": sb.notes,
                         "wals": "local" if wals.live else "embutido"}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera a sintaxe e frases de exemplo da conlang.")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON)
    ap.add_argument("--morphology", type=Path, default=DEFAULT_MORPHOLOGY)
    ap.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    ap.add_argument("--phonotactics", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    ap.add_argument("--morph", type=Path, default=DEFAULT_TYPOLOGY)
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLES)
    args = ap.parse_args()

    lexicon = _load(args.lexicon, "lexicon.py")
    morphology = _load(args.morphology, "morphological_engine.py")
    categories = _load(args.categories, "grammatical_categories.py")
    rules = _load(args.phonotactics, "phonotactics.py")
    inventory = _load(args.inventory, "phonemic_inventory.py")
    typology = json.loads(args.morph.read_text(encoding="utf-8")) if args.morph.exists() else {}

    eng = MorphologicalEngine.load(morphology, inventory, rules, categories, typology)
    wals = Wals(None if args.no_wals else args.wals)
    data = build(eng, lexicon, typology, wals, args.seed)

    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_examples(args.examples, data)
    print_summary(data)
    print(f"\n[OK] Sintaxe salva em '{args.output}' e exemplos em '{args.examples}'.")


if __name__ == "__main__":
    main()
