"""
Módulo — Categorias Gramaticais.

Define o espaço morfossemântico da conlang: quais categorias existem (número,
caso, gênero, definitude, classificadores, tempo, aspecto, modo,
evidencialidade, negação, concordância), quais valores contrastam, como cada
uma é realizada (afixo, clítico, partícula, mudança de raiz, tom...), quais se
fundem num único afixo e em que ordem os afixos aparecem.

Separa sempre a CATEGORIA (o contraste semântico) da sua REALIZAÇÃO (a forma),
para que línguas isolantes tenham as mesmas categorias expressas por partículas.

Entradas:
  ../morphological_typology/morphological_typology.json  (recomendada)
  ../wals/cldf/values.csv                                (opcional)

Sem o WALS, usa distribuições embutidas extraídas dele (contagens de línguas).
Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python grammatical_categories.py
    python grammatical_categories.py --seed 42
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Caminhos padrão
# ═══════════════════════════════════════════════════════════════════════════

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_MORPH = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_WALS = ROOT / "wals" / "cldf"
DEFAULT_OUTPUT = HERE / "grammatical_categories.json"

# ═══════════════════════════════════════════════════════════════════════════
# Distribuições do WALS (nº de línguas por valor), usadas quando o WALS
# não está disponível localmente. Chave = coluna "Value" do values.csv.
# ═══════════════════════════════════════════════════════════════════════════

EMBEDDED: Dict[str, Dict[str, int]] = {
    "30A": {"1": 145, "2": 50, "3": 26, "4": 12, "5": 24},          # nº de gêneros
    "31A": {"1": 145, "2": 84, "3": 28},                             # base do gênero
    "32A": {"1": 145, "2": 53, "3": 59},                             # atribuição
    "33A": {"1": 126, "2": 513, "3": 6, "4": 4, "5": 8, "6": 60,     # codificação do plural
            "7": 170, "8": 81, "9": 98},
    "34A": {"1": 28, "2": 20, "3": 40, "4": 55, "5": 15, "6": 133},  # ocorrência do plural
    "37A": {"1": 216, "2": 69, "3": 92, "4": 45, "5": 198},          # artigo definido
    "38A": {"1": 102, "2": 112, "3": 24, "4": 98, "5": 198},         # artigo indefinido
    "39A": {"1": 2, "2": 10, "3": 120, "4": 5, "5": 63},             # inclusivo/exclusivo
    "51A": {"1": 452, "2": 38, "3": 5, "4": 1, "5": 9, "6": 123,     # posição do caso
            "7": 17, "8": 7, "9": 379},
    "55A": {"1": 260, "2": 62, "3": 78},                             # classificadores
    "65A": {"1": 101, "2": 121},                                     # perfectivo/imperfectivo
    "66A": {"1": 94, "2": 38, "3": 2, "4": 88},                      # passado
    "67A": {"1": 110, "2": 112},                                     # futuro
    "69A": {"1": 153, "2": 667, "3": 13, "4": 146, "5": 152},        # posição de T/A
    "70A": {"1": 292, "2": 43, "3": 2, "4": 89, "5": 122},           # imperativo
    "73A": {"1": 48, "2": 271},                                      # optativo
    "74A": {"1": 63, "2": 158, "3": 13},                             # possibilidade
    "77A": {"1": 181, "2": 166, "3": 71},                            # evidencialidade
    "112A": {"1": 395, "2": 502, "3": 47, "4": 73, "5": 21, "6": 119},  # negação
}

# Tabelas condicionais: (feature condicionante, feature) → {valor: contagens}
EMBEDDED_CONDITIONAL: Dict[Tuple[str, str], Dict[str, Dict[str, int]]] = {
    ("26A", "49A"): {  # nº de casos | prefixação vs. sufixação
        "1": {"1": 27, "2": 2, "4": 1, "7": 1, "9": 1},
        "2": {"1": 19, "2": 12, "3": 5, "4": 5, "5": 7, "6": 24, "7": 11, "8": 14, "9": 7},
        "3": {"1": 9, "2": 3, "3": 1, "4": 2, "5": 2, "6": 4, "7": 4, "8": 1, "9": 3},
        "4": {"1": 13, "2": 4, "3": 2, "5": 1, "6": 2, "7": 4, "8": 4, "9": 6},
        "5": {"1": 10, "6": 2, "8": 2, "9": 2},
        "6": {"1": 11, "2": 1, "6": 1},
    },
    ("26A", "102A"): {  # marcação de pessoa no verbo | prefixação vs. sufixação
        "1": {"1": 26, "2": 7, "3": 4, "5": 9},
        "2": {"1": 30, "2": 38, "3": 7, "4": 1, "5": 47},
        "3": {"1": 4, "2": 4, "3": 4, "5": 32},
        "4": {"1": 1, "2": 4, "3": 1, "4": 3, "5": 41},
        "5": {"1": 2, "2": 2, "5": 21},
        "6": {"1": 1, "2": 6, "5": 12},
    },
    ("102A", "100A"): {  # alinhamento da concordância | argumentos marcados
        "2": {"2": 64, "3": 3, "4": 3, "6": 3},
        "3": {"2": 18, "3": 5, "6": 1},
        "4": {"2": 2, "5": 3, "6": 1},
        "5": {"2": 128, "3": 11, "4": 23, "5": 8, "6": 23},
    },
}

# Alinhamento do caso (98A) entre línguas que TÊM caso (49A ≠ 1, 9)
EMBEDDED_ALIGNMENT_GIVEN_CASE = {"1": 17, "2": 38, "3": 5, "4": 28, "5": 3, "6": 3}

# Sem capítulo no WALS: aproximações (Corbett 2000; Aikhenvald 2004; Palmer 2001)
P_DUAL = 0.15            # dual, dado que há plural
P_TRIAL = 0.10           # trial, dado que há dual (trial → dual → plural)
P_PAUCAL = 0.05          # paucal, dado que há plural
P_IRREALIS = 0.35        # oposição realis/irrealis ou subjuntivo
P_CLASSES_WITH_NUMBER = 0.7  # classes nominais pareadas com número (estilo bantu)

# Mapeamento da tipologia morfológica para o WALS 26A
AFFIX_POSITION_26A = {"little_affixation": "1", "strongly_suffixing": "2",
                      "weakly_suffixing": "3", "equal": "4",
                      "weakly_prefixing": "5", "strongly_prefixing": "6"}
P_PREFIX = {"little_affixation": 0.3, "strongly_suffixing": 0.08, "weakly_suffixing": 0.3,
            "equal": 0.5, "weakly_prefixing": 0.7, "strongly_prefixing": 0.92}

# Hierarquia de relevância (Bybee 1985; Greenberg, universal 39): quanto menor,
# mais perto da raiz. A negação é sorteada como interna ou externa por língua.
RANK = {
    "noun": {"gender": 0.5, "number": 1, "definiteness": 2, "case": 3},
    "verb": {"agreement_P": 0.8, "aspect": 1, "tense": 2, "mood": 3,
             "evidentiality": 4, "agreement_A": 6},
}

BOUND = {"affix", "clitic"}
NONLINEAR = {"stem_change", "tone", "reduplication", "transfix"}

OBLIQUE_CASES = ["genitive", "dative", "locative", "instrumental", "ablative", "comitative",
                 "allative", "vocative", "partitive", "essive", "translative", "abessive",
                 "comparative", "perlative"]

CORE_CASES = {  # 98A → (nome, casos centrais, caso de marca zero)
    "1": ("neutral", ["direct"], "direct"),
    "2": ("nominative_accusative", ["nominative", "accusative"], "nominative"),
    "3": ("marked_nominative", ["nominative", "accusative"], "accusative"),
    "4": ("ergative_absolutive", ["absolutive", "ergative"], "absolutive"),
    "5": ("tripartite", ["intransitive", "ergative", "accusative"], "intransitive"),
    "6": ("active_inactive", ["agentive", "patientive"], "patientive"),
}

AGREEMENT_ALIGNMENT = {"1": "neutral", "2": "accusative", "3": "ergative", "4": "active",
                       "5": "hierarchical", "6": "split"}

CLASS_SEMANTICS = ["humans", "animals", "plants", "artifacts", "abstract", "liquids_masses",
                   "long_objects", "augmentative", "diminutive", "locative"]

CLASSIFIER_SEMANTICS = ["human", "animal", "long_thin", "flat", "round", "small_round",
                        "vehicle", "pair", "plant", "building", "volume"]


# ═══════════════════════════════════════════════════════════════════════════
# Acesso ao WALS
# ═══════════════════════════════════════════════════════════════════════════

class Wals:
    """Distribuições do WALS: lidas dos CSVs se disponíveis, senão embutidas."""

    NEEDED = set(EMBEDDED) | {"26A", "49A", "98A", "100A", "102A"}

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

    def _count(self, fid: str, cond: Callable[[Dict[str, str]], bool]) -> Dict[str, int]:
        return dict(Counter(d[fid] for d in self.by_lang.values() if fid in d and cond(d)))

    def marginal(self, fid: str) -> Tuple[Dict[str, int], str]:
        if self.live:
            c = self._count(fid, lambda d: True)
            return c, f"WALS {fid} (n={sum(c.values())})"
        return EMBEDDED[fid], f"WALS {fid} (embutido)"

    def conditional(self, given: str, value: str, fid: str) -> Tuple[Dict[str, int], str]:
        if self.live:
            c = self._count(fid, lambda d: d.get(given) == value)
            if sum(c.values()) >= 5:
                return c, f"WALS {fid}|{given}={value} (n={sum(c.values())})"
        table = EMBEDDED_CONDITIONAL.get((given, fid), {})
        if value in table:
            return table[value], f"WALS {fid}|{given}={value} (embutido)"
        return self.marginal(fid)

    def alignment_given_case(self) -> Tuple[Dict[str, int], str]:
        if self.live:
            c = self._count("98A", lambda d: d.get("49A") not in (None, "1", "9"))
            return c, f"WALS 98A|com caso (n={sum(c.values())})"
        return EMBEDDED_ALIGNMENT_GIVEN_CASE, "WALS 98A|com caso (embutido)"


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

def not_grammaticalized(source: str, **extra) -> Dict:
    return {"grammaticalized": False, "source": source, **extra}


class CategoryBuilder:
    def __init__(self, morph: Dict, wals: Wals, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.wals = wals
        self.seed = seed
        self.synthesis = morph.get("degree_of_synthesis", "synthetic")
        self.fusion = morph.get("degree_of_fusion", "agglutinative")
        self.locus = morph.get("locus_of_marking", "dependent_marking")
        self.affix_pos = morph.get("affix_position", "strongly_suffixing")
        self.procs = set(morph.get("active_processes", ["affixation", "compounding"]))
        self.isolating = self.synthesis == "isolating"
        self.notes: List[str] = []
        self.sources: Dict[str, str] = {}
        if self.affix_pos not in P_PREFIX:  # JSON da versão antiga da tipologia
            self.affix_pos = "strongly_suffixing"

    # ── auxiliares ───────────────────────────────────────────────────────
    def pick(self, counts: Dict[str, float], mult: Optional[Dict[str, float]] = None) -> str:
        mult = mult or {}
        w = {k: v * mult.get(k, 1.0) for k, v in counts.items()}
        w = {k: v for k, v in w.items() if v > 0}
        keys = list(w)
        return self.rng.choices(keys, weights=[w[k] for k in keys], k=1)[0]

    def wals_pick(self, key: str, fid: str, mult=None, given: Optional[Tuple[str, str]] = None) -> str:
        counts, src = (self.wals.conditional(given[0], given[1], fid) if given
                       else self.wals.marginal(fid))
        prev = self.sources.get(key)
        self.sources[key] = f"{prev}; {src}" if prev else src
        return self.pick(counts, mult)

    def side(self, bias: float = 1.0) -> str:
        """prefix/suffix conforme a preferência da língua, ajustada por categoria."""
        p = P_PREFIX[self.affix_pos]
        odds = p / (1 - p) * bias
        return "prefix" if self.rng.random() < odds / (1 + odds) else "suffix"

    def free_side(self, p_before: Optional[float] = None) -> str:
        if p_before is None:
            p_before = P_PREFIX[self.affix_pos]
        return "before" if self.rng.random() < p_before else "after"

    def realize(self, kind: str, bias: float = 1.0) -> Dict:
        """Ajusta uma realização à tipologia (isolantes não têm morfemas presos)."""
        if self.isolating and kind in BOUND:
            kind = "particle"
        if kind in BOUND:
            return {"realization": kind, "position": self.side(bias)}
        if kind in ("particle", "auxiliary", "article"):
            return {"realization": kind, "position": self.free_side()}
        return {"realization": kind, "position": None}

    def zero(self, value: str, p: float) -> List[str]:
        return [value] if self.rng.random() < p else []

    # ── NOME ─────────────────────────────────────────────────────────────
    def build_number(self) -> Dict:
        occ = self.wals_pick("number", "34A", {"1": 3, "2": 2, "4": 2} if self.isolating else None)
        if occ == "1":
            return not_grammaticalized(self.sources["number"])

        mult = {"9": 0}
        mult["3"] = 15 if "apophony" in self.procs else 0
        mult["4"] = 15 if "tonal_morphology" in self.procs else 0
        mult["5"] = 8 if self.procs & {"reduplication_full", "reduplication_partial"} else 0
        if self.isolating:
            mult.update({"1": 0, "2": 0, "6": 0, "8": 0, "7": 4})
        coding = self.wals_pick("number", "33A", mult)
        kind = {"1": "affix", "2": "affix", "3": "stem_change", "4": "tone",
                "5": "reduplication", "6": "affix", "7": "particle", "8": "clitic"}[coding]
        real = self.realize(kind)
        if coding in ("1", "2") and not self.isolating:
            real["position"] = "prefix" if coding == "1" else "suffix"

        values = ["singular", "plural"]
        p_dual = P_DUAL * (0.2 if self.isolating else 1)
        if self.rng.random() < p_dual:
            values.insert(1, "dual")
            if self.rng.random() < P_TRIAL:
                values.insert(2, "trial")
        if self.rng.random() < P_PAUCAL:
            values.insert(-1, "paucal")
        self.sources["number"] += "; dual/trial/paucal: aproximação (Corbett 2000)"

        scope = {"2": "human_nouns", "3": "human_nouns", "5": "all_nouns_optional_inanimates"}
        return {
            "grammaticalized": True,
            "values": values,
            "default": "singular",
            "zero": self.zero("singular", 0.9),
            **real,
            "scope": scope.get(occ, "all_nouns"),
            "obligatory": occ in ("3", "6"),
            "source": self.sources["number"],
        }

    def build_case(self) -> Dict:
        if self.isolating:
            self.sources["case"] = "língua isolante: relações por ordem e adposições"
            return not_grammaticalized(self.sources["case"], relations="word_order_and_adpositions")

        mult: Dict[str, float] = {}
        if self.locus == "head_marking":
            mult["1"] = 2.0
        elif self.locus == "dependent_marking":
            mult.update({"1": 0.5, "9": 0.6})
        elif self.locus == "double_marking":
            mult["1"] = 0.7
        if self.synthesis == "polysynthetic":
            mult["1"] = mult.get("1", 1.0) * 1.5
        c = self.wals_pick("case", "49A", mult, given=("26A", AFFIX_POSITION_26A[self.affix_pos]))
        if c in ("1", "9"):
            return not_grammaticalized(
                self.sources["case"],
                relations="adpositional_clitics" if c == "9" else "word_order_and_adpositions")

        n = {"2": 2, "3": 3, "4": 4, "5": 5, "6": self.rng.randint(6, 7),
             "7": self.rng.randint(8, 9), "8": self.rng.randint(10, 14)}[c]
        counts, src = self.wals.alignment_given_case()
        self.sources["case"] += f"; {src}"
        align_code = self.pick(counts)
        alignment, core, zero_case = CORE_CASES[align_code]
        n = max(n, len(core))

        # Oblíquos pela hierarquia de casos (Blake 1994): genitivo e dativo primeiro
        pool = list(OBLIQUE_CASES)
        values = list(core)
        while len(values) < n and pool:
            weights = [1.0 / (i + 1) ** 1.2 for i in range(len(pool))]
            choice = self.rng.choices(pool, weights=weights, k=1)[0]
            pool.remove(choice)
            values.append(choice)
        values = core + sorted(values[len(core):], key=OBLIQUE_CASES.index)

        # Posição (51A): caso é fortemente sufixal, mesmo em línguas prefixantes
        p = P_PREFIX[self.affix_pos]
        prefix_factor = ((p / (1 - p)) / (0.08 / 0.92)) ** 0.5
        pos = self.wals_pick("case", "51A", {"1": 1, "2": prefix_factor, "6": 1, "7": prefix_factor,
                                              "3": 0, "4": 0, "5": 0, "8": 0, "9": 0})
        kind = "clitic" if pos in ("6", "7") else "affix"
        return {
            "grammaticalized": True,
            "alignment": alignment,
            "values": values,
            "default": core[0] if alignment != "marked_nominative" else "accusative",
            # No alinhamento neutro o caso direto nunca contrasta com outro caso central,
            # então é sempre Ø; nos demais, o caso não marcado é Ø em 85% das línguas.
            "zero": self.zero(zero_case, 1.0 if alignment == "neutral" else 0.85),
            "realization": kind,
            "position": "prefix" if pos in ("2", "7") else "suffix",
            "source": self.sources["case"],
        }

    def build_gender(self, number: Dict) -> Dict:
        mult = {"1": 30} if self.isolating else None
        g = self.wals_pick("gender", "30A", mult)
        if g == "1":
            return not_grammaticalized(self.sources["gender"])

        basis = "sex_based" if self.wals_pick("gender", "31A", {"1": 0}) == "2" else "non_sex_based"
        assignment = ("semantic" if self.wals_pick("gender", "32A", {"1": 0}) == "2"
                      else "semantic_and_formal")
        n = {"2": 2, "3": 3, "4": 4, "5": self.rng.randint(5, 10)}[g]
        semantics: Optional[List[str]] = None
        if n == 2:
            values = ["masculine", "feminine"] if basis == "sex_based" else ["animate", "inanimate"]
        elif n == 3:
            values = (["masculine", "feminine", "neuter"] if basis == "sex_based"
                      else ["human", "animate", "inanimate"])
        else:
            values = [f"class_{i}" for i in range(1, n + 1)]
            semantics = ["humans"] + self.rng.sample(CLASS_SEMANTICS[1:], n - 2) + ["residual"]
            if basis == "sex_based":
                semantics[0], semantics[1] = "male_humans", "female_humans"

        large = n >= 5
        on_noun = self.rng.random() < (0.7 if large else 0.3) and not self.isolating
        paired = large and number.get("grammaticalized") and self.rng.random() < P_CLASSES_WITH_NUMBER
        entry = {
            "grammaticalized": True,
            "type": "noun_class" if large else "gender",
            "basis": basis,
            "assignment": assignment,
            "values": values,
            "default": values[-1],
            "zero": [],
            "marked_on_noun": on_noun,
            "paired_with_number": bool(paired),
            "agreement_targets": ["adjective", "demonstrative"],
            "source": self.sources["gender"],
        }
        if semantics:
            entry["semantic_cores"] = dict(zip(values, semantics))
        entry.update(self.realize("affix") if on_noun else {"realization": "agreement_only",
                                                            "position": None})
        return entry

    def build_definiteness(self) -> Dict:
        d = self.wals_pick("definiteness", "37A")
        definite = {"1": "article", "2": "demonstrative_article", "3": "affix"}.get(d)
        if d == "5":
            indefinite = None
        elif d == "4":
            indefinite = "article"
        else:
            i = self.wals_pick("definiteness", "38A", {"5": 0})
            indefinite = {"1": "article", "2": "numeral_one", "3": "affix"}.get(i)
        if not definite and not indefinite:
            return not_grammaticalized(self.sources["definiteness"])

        markers = {}
        art_side = self.free_side(0.6)
        for value, kind in (("definite", definite), ("indefinite", indefinite)):
            if not kind:
                continue
            if kind in ("article", "demonstrative_article", "numeral_one"):
                markers[value] = {"realization": kind, "position": art_side}
            else:
                markers[value] = self.realize("affix")
        values = ["unmarked"] + list(markers)
        kinds = {m["realization"] for m in markers.values()}
        return {
            "grammaticalized": True,
            "values": values,
            "default": "unmarked",
            "zero": ["unmarked"],
            "markers": markers,
            "realization": kinds.pop() if len(kinds) == 1 else "mixed",
            "position": next(iter(markers.values()))["position"] if len(markers) == 1 else None,
            "source": self.sources["definiteness"],
        }

    def build_classifiers(self, gender: Dict) -> Dict:
        mult: Dict[str, float] = {}
        if self.isolating:
            mult.update({"2": 4, "3": 8})
        if gender.get("grammaticalized"):  # gênero e classificadores raramente coexistem
            mult.update({"2": mult.get("2", 1) * 0.5, "3": mult.get("3", 1) * 0.3})
        c = self.wals_pick("classifiers", "55A", mult)
        if c == "1":
            return not_grammaticalized(self.sources["classifiers"])
        n = self.rng.randint(4, 10)
        values = ["general"] + self.rng.sample(CLASSIFIER_SEMANTICS, n - 1)
        return {
            "grammaticalized": True,
            "obligatory": c == "3",
            "values": values,
            "default": "general",
            "zero": [],
            "realization": "word",
            "position": self.free_side(0.6),
            "note": "usados com numerais (ex: 'três CL.ANIMAL cão')",
            "source": self.sources["classifiers"],
        }

    # ── VERBO ────────────────────────────────────────────────────────────
    def _ta_realization(self) -> Dict:
        """Posição dos afixos de tempo/aspecto (69A), sorteada uma vez por língua."""
        if not hasattr(self, "_ta"):
            if self.isolating:
                code = "5"
            else:
                p = P_PREFIX[self.affix_pos]
                f = ((p / (1 - p)) / (153 / 667)) ** 0.5
                mult = {"1": f, "3": 1 if "tonal_morphology" in self.procs else 0, "5": 0.3}
                code = self.wals_pick("tense_aspect_position", "69A", mult)
            self._ta = code
        code = self._ta
        if code == "1":
            return {"realization": "affix", "position": "prefix"}
        if code == "2":
            return {"realization": "affix", "position": "suffix"}
        if code == "3":
            return {"realization": "tone", "position": None}
        if code == "4":
            return self.realize("affix")
        return self.realize(self.rng.choice(["particle", "auxiliary"]))

    def build_tense(self) -> Dict:
        past = self.wals_pick("tense", "66A", {"4": 3} if self.isolating else None)
        future = self.wals_pick("tense", "67A", {"2": 3} if self.isolating else None)
        has_past, has_future = past != "4", future == "1"
        if not has_past and not has_future:
            return not_grammaticalized(self.sources["tense"])

        if has_past and has_future:
            values, default = ["present", "past", "future"], "present"
        elif has_past:
            values, default = ["non_past", "past"], "non_past"
        else:
            values, default = ["non_future", "future"], "non_future"

        if past == "2":
            degrees = (["recent_past", "remote_past"] if self.rng.random() < 0.6
                       else ["hodiernal_past", "hesternal_past", "remote_past"])
            values = [v for v in values if v != "past"] + degrees
        elif past == "3":
            values = [v for v in values if v != "past"] + [
                "immediate_past", "hodiernal_past", "hesternal_past", "remote_past"]

        real = self._ta_realization()
        if "transfixation" in self.procs and self.rng.random() < 0.3:
            real = {"realization": "transfix", "position": None}
        elif "apophony" in self.procs and self.rng.random() < 0.3:
            real = {"realization": "stem_change", "position": None}
        return {"grammaticalized": True, "values": values, "default": default,
                "zero": self.zero(default, 0.7), **real, "source": self.sources["tense"]}

    def build_aspect(self) -> Dict:
        if self.wals_pick("aspect", "65A") == "2":
            return not_grammaticalized(self.sources["aspect"])
        values = ["perfective", "imperfective"]
        if self.rng.random() < 0.25:
            values.append("progressive")
        if self.rng.random() < 0.15:
            values.append("habitual")
        default = self.rng.choice(["perfective", "imperfective"])

        real = self._ta_realization()
        if "transfixation" in self.procs and self.rng.random() < 0.7:
            real = {"realization": "transfix", "position": None}
        elif self.procs & {"reduplication_full", "reduplication_partial"} and self.rng.random() < 0.25:
            real = {"realization": "reduplication", "position": None}
        self.sources["aspect"] += "; valores além de perf/imperf: aproximação"
        return {"grammaticalized": True, "values": values, "default": default,
                "zero": self.zero(default, 0.6), **real, "source": self.sources["aspect"]}

    def build_mood(self) -> Dict:
        values = ["indicative"]
        extra: Dict = {}
        imp = self.wals_pick("mood", "70A")
        if imp != "5":
            values.append("imperative")
            extra["imperative_number"] = {"1": "singular_and_plural", "2": "singular_only",
                                          "3": "plural_only", "4": "number_neutral"}[imp]
        if self.wals_pick("mood", "73A") == "1":
            values.append("optative")
        if self.wals_pick("mood", "74A") == "1":
            values.append("potential")
        if self.rng.random() < P_IRREALIS:
            values.append("irrealis")
        self.sources["mood"] += "; irrealis: aproximação (Palmer 2001)"
        if len(values) == 1:
            return not_grammaticalized(self.sources["mood"])
        return {"grammaticalized": True, "values": values, "default": "indicative",
                "zero": self.zero("indicative", 0.85), **extra, **self.realize("affix"),
                "source": self.sources["mood"]}

    def build_evidentiality(self) -> Dict:
        e = self.wals_pick("evidentiality", "77A")
        if e == "1":
            return not_grammaticalized(self.sources["evidentiality"])
        if e == "2":
            values = (["direct", "inferential", "reportative"] if self.rng.random() < 0.35
                      else ["direct", "indirect"])
        else:
            values = (["visual", "nonvisual", "inferential", "reportative"]
                      if self.rng.random() < 0.3 else ["direct", "inferential", "reportative"])
        kind = self.pick({"affix": 0.6, "clitic": 0.25, "particle": 0.15})
        self.sources["evidentiality"] += "; realização: aproximação (Aikhenvald 2004)"
        return {"grammaticalized": True, "type": {"2": "indirect_only", "3": "direct_and_indirect"}[e],
                "values": values, "default": values[0], "zero": self.zero(values[0], 0.8),
                **self.realize(kind), "source": self.sources["evidentiality"]}

    def build_negation(self) -> Dict:
        mult = {"1": 0, "5": 0, "6": 0.3} if self.isolating else None
        n = self.wals_pick("negation", "112A", mult)
        kind = {"1": "affix", "2": "particle", "3": "auxiliary", "4": "particle",
                "5": "affix", "6": "double"}[n]
        if kind == "double":
            real = {"realization": "double", "position": None,
                    "markers": {"particle": {"realization": "particle", "position": self.free_side(0.75)},
                                "affix": self.realize("affix", 1.5)}}
        elif kind in ("particle", "auxiliary"):
            real = {"realization": kind, "position": self.free_side(0.75)}  # Neg-first (Dahl 1979)
        else:
            real = self.realize("affix", 1.5)
        return {"grammaticalized": True, "values": ["affirmative", "negative"],
                "default": "affirmative", "zero": ["affirmative"], **real,
                "slot": "inner" if self.rng.random() < 0.5 else "outer",
                "source": self.sources["negation"]}

    def build_agreement(self, number: Dict, case: Dict) -> Dict:
        if self.isolating:
            self.sources["agreement"] = "língua isolante: sem concordância"
            return not_grammaticalized(self.sources["agreement"])
        mult = {
            "head_marking": {"5": 3, "1": 0.3, "2": 0.7},
            "dependent_marking": {"1": 1.6, "2": 1.3, "5": 0.6},
            "double_marking": {"5": 1.5},
        }.get(self.locus, {})
        if self.synthesis == "polysynthetic":
            mult = {**mult, "5": mult.get("5", 1) * 4, "1": 0.1}
        a = self.wals_pick("agreement", "102A", mult, given=("26A", AFFIX_POSITION_26A[self.affix_pos]))
        if a == "1":
            return not_grammaticalized(self.sources["agreement"])

        args = {"2": ["A"], "3": ["P"], "4": ["A_or_P"], "5": ["A", "P"]}[a]
        al_mult = {"3": 3, "6": 2} if case.get("alignment") == "ergative_absolutive" else None
        alignment = AGREEMENT_ALIGNMENT[self.wals_pick("agreement", "100A", al_mult, given=("102A", a))]

        clus = self.wals_pick("agreement", "39A", {"1": 0, "2": 0})
        clusivity = {"3": "none", "4": "inclusive_only", "5": "inclusive_exclusive"}[clus]
        numbers = (number["values"] if number.get("grammaticalized")
                   else ["singular", "plural"])  # pronomes quase sempre têm número
        kind = "clitic" if self.rng.random() < 0.15 else "affix"
        arguments = {}
        for arg in args:
            name = "A" if arg == "A_or_P" else arg
            arguments[name] = self.realize(kind, bias=1.8)
        return {
            "grammaticalized": True,
            "arguments": arguments,
            "hierarchical_slot": a == "4",
            "alignment": alignment,
            "persons": ["1", "2", "3"],
            "clusivity": clusivity,
            "numbers": numbers,
            "person_number": ("separate" if self.fusion == "agglutinative" and self.rng.random() < 0.25
                              else "cumulative"),
            "zero": self.zero("3.singular", 0.5),
            "source": self.sources["agreement"],
        }

    # ── fusão e ordem ────────────────────────────────────────────────────
    def _units(self, cats: Dict, domain: str) -> Dict[str, Dict]:
        """Unidades afixais lineares de um domínio: nome → {rank, realization, position}."""
        units = {}
        for name, rank in RANK[domain].items():
            if name.startswith("agreement_"):
                ag = cats.get("agreement", {})
                arg = ag.get("arguments", {}).get(name.split("_")[1])
                if ag.get("grammaticalized") and arg and arg["realization"] in BOUND:
                    units[name] = {"rank": rank, **arg}
                continue
            c = cats.get(name, {})
            if c.get("grammaticalized") and c.get("realization") in BOUND:
                units[name] = {"rank": rank, "realization": c["realization"], "position": c["position"]}
        if domain == "verb":
            neg = cats.get("negation", {})
            marker = neg.get("markers", {}).get("affix") if neg.get("realization") == "double" else (
                neg if neg.get("realization") in BOUND else None)
            if marker:
                units["negation"] = {"rank": 0.5 if neg["slot"] == "inner" else 5.5,
                                     "realization": marker["realization"], "position": marker["position"]}
        if domain == "noun":
            d = cats.get("definiteness", {})
            for m in d.get("markers", {}).values() if d.get("grammaticalized") else []:
                if m["realization"] in BOUND:
                    units["definiteness"] = {"rank": RANK["noun"]["definiteness"], **m}
                    break
        return units

    def build_cumulation(self, cats: Dict) -> Dict[str, List[List[str]]]:
        """Quais categorias se fundem num único afixo (cumulação)."""
        bundles: Dict[str, List[List[str]]] = {"noun": [], "verb": []}
        if self.isolating:
            return bundles
        noun, verb = self._units(cats, "noun"), self._units(cats, "verb")

        # Classes nominais pareadas com número (bantu): independe da fusão
        if "gender" in noun and "number" in noun and cats["gender"].get("paired_with_number"):
            bundles["noun"].append(["gender", "number"])

        if self.fusion == "fusional":
            if "number" in noun and "case" in noun and self.rng.random() < 0.85:
                existing = next((b for b in bundles["noun"] if "number" in b), None)
                if existing:
                    existing.append("case")
                elif "gender" in noun and self.rng.random() < 0.5:
                    bundles["noun"].append(["gender", "number", "case"])
                else:
                    bundles["noun"].append(["number", "case"])
            if "definiteness" in noun and bundles["noun"] and self.rng.random() < 0.3:
                bundles["noun"][-1].append("definiteness")
            tam = [c for c in ("aspect", "tense", "mood") if c in verb]
            if len(tam) >= 2 and self.rng.random() < 0.7:
                b = list(tam)
                if "agreement_A" in verb and self.rng.random() < 0.5:
                    b.append("agreement_A")  # estilo latim: -ō = 1sg.pres.ind
                bundles["verb"].append(b)
        elif self.fusion == "agglutinative":
            if "tense" in verb and "aspect" in verb and self.rng.random() < 0.15:
                bundles["verb"].append(["aspect", "tense"])

        # Harmoniza posição e tipo dos membros de cada pacote
        for domain, units in (("noun", noun), ("verb", verb)):
            for b in bundles[domain]:
                outer = max(b, key=lambda m: units[m]["rank"])
                for m in b:
                    units[m]["position"] = units[outer]["position"]
                    units[m]["realization"] = "affix"
                    self._set_position(cats, m, units[outer]["position"])
        return bundles

    @staticmethod
    def _set_position(cats: Dict, unit: str, position: str) -> None:
        if unit.startswith("agreement_"):
            arg = cats["agreement"]["arguments"][unit.split("_")[1]]
            arg.update(realization="affix", position=position)
        elif unit == "definiteness":
            for m in cats["definiteness"]["markers"].values():
                if m["realization"] in BOUND:
                    m.update(realization="affix", position=position)
        else:
            cats[unit].update(realization="affix", position=position)

    def build_slots(self, cats: Dict, bundles: Dict) -> Dict:
        """Ordem linear dos afixos, da periferia para a raiz e da raiz para a periferia."""
        out = {}
        for domain in ("noun", "verb"):
            units = self._units(cats, domain)
            groups = [list(b) for b in bundles[domain]]
            grouped = {m for b in groups for m in b}
            groups += [[u] for u in units if u not in grouped]
            slots = []
            for g in groups:
                rank = max(units[m]["rank"] for m in g)
                slots.append({"name": "+".join(sorted(g, key=lambda m: units[m]["rank"])),
                              "categories": g, "rank": rank,
                              "position": units[g[0]]["position"],
                              "realization": units[g[0]]["realization"]})
            prefixes = sorted([s for s in slots if s["position"] == "prefix"], key=lambda s: -s["rank"])
            suffixes = sorted([s for s in slots if s["position"] == "suffix"], key=lambda s: s["rank"])
            template = [s["name"] for s in prefixes] + ["ROOT"] + [s["name"] for s in suffixes]

            nonlinear, particles = [], []
            for name, c in cats.items():
                if not c.get("grammaticalized") or RANK_DOMAIN.get(name) != domain:
                    continue
                if c.get("realization") in NONLINEAR:
                    nonlinear.append({"category": name, "realization": c["realization"]})
                for m in ([c] if "markers" not in c else c["markers"].values()):
                    if m.get("realization") in ("particle", "auxiliary", "article",
                                                "demonstrative_article", "numeral_one", "word"):
                        particles.append({"category": name, "realization": m["realization"],
                                          "position": m["position"]})
            out[domain] = {
                "prefixes": [{k: s[k] for k in ("name", "categories", "realization")} for s in prefixes],
                "suffixes": [{k: s[k] for k in ("name", "categories", "realization")} for s in suffixes],
                "template": "-".join(template),
                "nonlinear": nonlinear,
                "free_markers": particles,
            }
        return out

    def build_inflection_classes(self, cats: Dict) -> Dict:
        if self.isolating:
            return {"noun": 0, "verb": 0}
        if self.fusion != "fusional":
            return {"noun": 1, "verb": 1}
        n = int(self.pick({"2": 25, "3": 35, "4": 25, "5": 15}))
        v = int(self.pick({"2": 40, "3": 35, "4": 25}))
        self.notes.append(f"{n} declinações e {v} conjugações (língua fusional)")
        return {"noun": n, "verb": v}

    # ── geração ──────────────────────────────────────────────────────────
    def generate(self) -> Dict:
        number = self.build_number()
        case = self.build_case()
        gender = self.build_gender(number)
        cats = {
            "number": number,
            "case": case,
            "gender": gender,
            "definiteness": self.build_definiteness(),
            "classifiers": self.build_classifiers(gender),
            "tense": self.build_tense(),
            "aspect": self.build_aspect(),
            "mood": self.build_mood(),
            "evidentiality": self.build_evidentiality(),
            "negation": self.build_negation(),
        }
        cats["agreement"] = self.build_agreement(number, case)
        if gender.get("grammaticalized") and cats["agreement"].get("grammaticalized"):
            gender["agreement_targets"].append("verb")

        bundles = self.build_cumulation(cats)
        slots = self.build_slots(cats, bundles)
        return {
            "categories": cats,
            "cumulation": bundles,
            "slots": slots,
            "inflection_classes": self.build_inflection_classes(cats),
            "metadata": {
                "seed": self.seed,
                "typology": {"synthesis": self.synthesis, "fusion": self.fusion,
                             "locus": self.locus, "affix_position": self.affix_pos},
                "wals": "local" if self.wals.live else "embutido",
                "notes": self.notes,
            },
        }


RANK_DOMAIN = {"number": "noun", "case": "noun", "gender": "noun", "definiteness": "noun",
               "classifiers": "noun", "tense": "verb", "aspect": "verb", "mood": "verb",
               "evidentiality": "verb", "negation": "verb", "agreement": "verb"}


# ═══════════════════════════════════════════════════════════════════════════
# Exibição
# ═══════════════════════════════════════════════════════════════════════════

LABELS = {"number": "Número", "case": "Caso", "gender": "Gênero/classe",
          "definiteness": "Definitude", "classifiers": "Classificadores", "tense": "Tempo",
          "aspect": "Aspecto", "mood": "Modo", "evidentiality": "Evidencialidade",
          "negation": "Negação", "agreement": "Concordância"}


def _describe(c: Dict) -> str:
    if "markers" in c:
        return ", ".join(f"{k}: {m['realization']}" + (f" ({m['position']})" if m.get("position") else "")
                         for k, m in c["markers"].items())
    pos = f" ({c['position']})" if c.get("position") else ""
    return f"{c.get('realization')}{pos}"


def print_summary(data: Dict) -> None:
    cats = data["categories"]
    t = data["metadata"]["typology"]
    print(f"\nTIPOLOGIA: {t['synthesis']}, {t['fusion']}, {t['locus']}, {t['affix_position']}")
    for domain, title in (("noun", "NOME"), ("verb", "VERBO")):
        print(f"\n{title}")
        for name in [n for n, d in RANK_DOMAIN.items() if d == domain]:
            c = cats[name]
            label = LABELS[name].ljust(16)
            if not c["grammaticalized"]:
                extra = f" ({c['relations']})" if c.get("relations") else ""
                print(f"  {label} —{extra}")
                continue
            if name == "agreement":
                args = ", ".join(f"{a}: {r['realization']} ({r['position']})"
                                 for a, r in c["arguments"].items())
                print(f"  {label} {args}; alinhamento {c['alignment']}; "
                      f"clusividade {c['clusivity']}; pessoa×número {c['person_number']}")
                continue
            vals = ", ".join(c["values"])
            zero = f"; Ø = {', '.join(c['zero'])}" if c.get("zero") else ""
            extra = f" [{c['alignment']}]" if name == "case" else ""
            print(f"  {label} {vals}{extra}  → {_describe(c)}{zero}")

    print("\nCUMULAÇÃO")
    for domain, title in (("noun", "nome"), ("verb", "verbo")):
        b = data["cumulation"][domain]
        print(f"  {title}: " + ("; ".join(" × ".join(x) for x in b) if b else "nenhuma (1 traço por afixo)"))

    print("\nMOLDES")
    for domain, title in (("noun", "nome"), ("verb", "verbo")):
        s = data["slots"][domain]
        print(f"  {title}: {s['template']}")
        if s["nonlinear"]:
            print("    não linear: " + ", ".join(f"{x['category']} ({x['realization']})" for x in s["nonlinear"]))
        if s["free_markers"]:
            print("    palavras livres: " + ", ".join(
                f"{x['category']} ({x['realization']}, {x['position']})" for x in s["free_markers"]))

    ic = data["inflection_classes"]
    if ic["noun"] > 1 or ic["verb"] > 1:
        print(f"\nCLASSES FLEXIONAIS: {ic['noun']} declinações, {ic['verb']} conjugações")


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    ap = argparse.ArgumentParser(description="Gera as categorias gramaticais da conlang.")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--morph", type=Path, default=DEFAULT_MORPH)
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true", help="usa só as distribuições embutidas")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    if args.morph.exists():
        morph = json.loads(args.morph.read_text(encoding="utf-8"))
    else:
        print(f"[!] {args.morph} não encontrado; usando língua sintética aglutinante sufixante.")
        morph = {}
    wals = Wals(None if args.no_wals else args.wals)

    result = CategoryBuilder(morph, wals, seed=args.seed).generate()
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print_summary(result)
    print(f"\n[OK] Categorias salvas em '{args.output}'.")


if __name__ == "__main__":
    main()
