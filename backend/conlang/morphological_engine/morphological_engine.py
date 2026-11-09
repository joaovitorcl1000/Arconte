"""
Módulo — Motor Morfológico.

Junta todos os módulos anteriores e produz língua de fato: gera os afixos de
cada célula de cada slot, as marcas zero, os processos não lineares (mudança
de raiz, tom, reduplicação, transfixação), as palavras gramaticais livres
(partículas, artigos, auxiliares, classificadores), resolve o sândi nas
fronteiras de morfema e monta paradigmas completos.

Entradas (todas obrigatórias, exceto a tipologia):
  ../phonemic_inventory/phonemic_inventory.json
  ../phonotactics/phonotactics.json        (+ o módulo phonotactics.py)
  ../grammatical_categories/grammatical_categories.json
  ../morphological_typology/morphological_typology.json  (opcional)

Saída: morphology.json

Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python morphological_engine.py
    python morphological_engine.py --seed 42 --nouns 8 --verbs 8
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "phonotactics"))
from phonotactics import Phonotactics, is_complex_segment, nfd  # noqa: E402

DEFAULT_INVENTORY = ROOT / "phonemic_inventory" / "phonemic_inventory.json"
DEFAULT_RULES = ROOT / "phonotactics" / "phonotactics.json"
DEFAULT_CATEGORIES = ROOT / "grammatical_categories" / "grammatical_categories.json"
DEFAULT_MORPH = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_OUTPUT = HERE / "morphology.json"

Segs = List[str]

# ═══════════════════════════════════════════════════════════════════════════
# Glosas (convenções de Leipzig)
# ═══════════════════════════════════════════════════════════════════════════

GLOSS = {
    "singular": "SG", "plural": "PL", "dual": "DU", "trial": "TRI", "paucal": "PAUC",
    "nominative": "NOM", "accusative": "ACC", "absolutive": "ABS", "ergative": "ERG",
    "intransitive": "INTR", "agentive": "AGT", "patientive": "PAT", "direct": "DIR",
    "genitive": "GEN", "dative": "DAT", "locative": "LOC", "instrumental": "INS",
    "ablative": "ABL", "comitative": "COM", "allative": "ALL", "vocative": "VOC",
    "partitive": "PART", "essive": "ESS", "translative": "TRANSL", "abessive": "ABE",
    "comparative": "COMPR", "perlative": "PERL", "definite": "DEF", "indefinite": "INDF",
    "unmarked": "", "present": "PRS", "past": "PST", "future": "FUT", "non_past": "NPST",
    "non_future": "NFUT", "recent_past": "REC", "remote_past": "REM",
    "hodiernal_past": "HOD", "hesternal_past": "HEST", "immediate_past": "IMM",
    "perfective": "PFV", "imperfective": "IPFV", "progressive": "PROG", "habitual": "HAB",
    "indicative": "IND", "imperative": "IMP", "optative": "OPT", "potential": "POT",
    "irrealis": "IRR", "indirect": "INDIR", "inferential": "INFR", "reportative": "REP",
    "visual": "VIS", "nonvisual": "NVIS", "affirmative": "", "negative": "NEG",
    "masculine": "M", "feminine": "F", "neuter": "N", "animate": "AN",
    "inanimate": "INAN", "human": "HUM",
}

NOUN_CATS = ["gender", "number", "definiteness", "case"]
VERB_CATS = ["aspect", "tense", "mood", "evidentiality", "negation"]


def gloss(value: str) -> str:
    if value.startswith("class_"):
        return "CL" + value.split("_")[1]
    if "." in value:  # concordância: "1incl.plural" → 1INCL.PL
        person, number = value.split(".", 1)
        sep = "." if not person.isdigit() else ""
        return person.upper() + sep + GLOSS.get(number, number.upper())
    return GLOSS.get(value, value.upper()[:4])


def visible_len(s: str) -> int:
    return sum(1 for ch in s if unicodedata.category(ch) != "Mn")


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - visible_len(s))


# ═══════════════════════════════════════════════════════════════════════════
# Motor
# ═══════════════════════════════════════════════════════════════════════════

class MorphologicalEngine:
    """
    Constrói (build) e aplica (inflect) a morfologia de uma língua.

    O resultado de build() é serializável; MorphologicalEngine.load() recria
    o motor a partir do morphology.json para uso por módulos posteriores.
    """

    def __init__(self, inventory: Dict, rules: Dict, categories: Dict,
                 typology: Optional[Dict] = None, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.seed = seed
        self.inventory = inventory
        self.rules = rules
        self.cats = categories["categories"]
        self.catdata = categories
        self.typology = typology or {}
        self.ph = Phonotactics(rules, inventory, seed=seed)
        self.cons = self.ph.cons
        self.vowels = self.ph.vowels
        self.tones = list(self.ph.tones)
        self.fusion = categories["metadata"]["typology"]["fusion"]
        self.skeleton = rules["root"]["shape"] == "consonantal_skeleton"
        self.notes: List[str] = []
        self.spec: Dict = {}

    # ══ auxiliares fonológicos ═══════════════════════════════════════════
    def is_vowel(self, s: str) -> bool:
        return s in self.vowels

    def is_cons(self, s: str) -> bool:
        return s in self.cons

    def _short_plain_vowels(self) -> List[str]:
        v = [k for k, e in self.vowels.items() if not e["long"] and not e["nasal"]]
        return v or list(self.vowels)

    def _choose_epenthetic(self) -> str:
        for cand in ("ə", "ɨ", "i", "ɪ", "e", "a", "u"):
            if cand in self.vowels:
                return cand
        return max(self.vowels, key=lambda v: self.vowels[v]["frequency"])

    def _homorganic_nasal(self, c: str) -> Optional[str]:
        place = self.cons[c]["place"]
        for k, e in self.cons.items():
            if e["manner"] == "nasal" and e["place"] == place and not is_complex_segment(e):
                return k
        return None

    def _voicing_counterpart(self, c: str, voiced: bool) -> Optional[str]:
        f = dict(self.cons[c]["features"])
        f["periodicGlottalSource"] = "+" if voiced else "-"
        for k, e in self.cons.items():
            if e["features"] == f:
                return k
        return None

    def _is_obstruent(self, c: str) -> bool:
        return self.cons[c]["manner"] in ("stop", "affricate", "fricative")

    def _is_voiced(self, c: str) -> bool:
        return self.cons[c]["features"].get("periodicGlottalSource") == "+"

    # ══ 1. Configuração da língua: sândi e harmonia ══════════════════════
    def _build_sandhi(self) -> Dict:
        r = self.rng
        glide_j = "j" if "j" in self.cons else None
        glide_w = "w" if "w" in self.cons else None
        hiatus_c = next((c for c in ("ʔ", "h", "t", "n") if c in self.cons), None)
        sandhi = {
            "epenthetic_vowel": self._choose_epenthetic(),
            "cluster": "epenthesis" if r.random() < 0.6 else "deletion",
            "deletion_side": "left" if r.random() < 0.5 else "right",
            "hiatus": r.choices(["elision", "glide", "consonant"], [0.45, 0.4, 0.15])[0],
            "elision_side": "left" if r.random() < 0.7 else "right",
            "glides": {"front": glide_j, "back": glide_w},
            "hiatus_consonant": hiatus_c,
            "nasal_assimilation": r.random() < 0.7,
            "voicing_assimilation": r.random() < 0.4,
        }
        if sandhi["hiatus"] == "glide" and not (glide_j or glide_w):
            sandhi["hiatus"] = "consonant" if hiatus_c else "elision"
        if sandhi["hiatus"] == "consonant" and not hiatus_c:
            sandhi["hiatus"] = "elision"
        return sandhi

    def _build_harmony(self) -> Dict:
        synthesis = self.catdata["metadata"]["typology"]["synthesis"]
        p = {"agglutinative": 0.35, "fusional": 0.10}.get(self.fusion, 0.0)
        if synthesis == "polysynthetic":
            p = max(p, 0.2)
        if synthesis == "isolating" or self.rng.random() >= p:
            return {"enabled": False}
        height = {"high": 0, "mid": 1, "low": 2}
        group = lambda v: "front" if self.vowels[v]["backness"] == "front" else "back"
        pairs: Dict[str, Dict[str, str]] = {}
        for v, e in self.vowels.items():
            best, best_d = None, 9
            for w, f in self.vowels.items():
                if group(v) == group(w) or e["rounded"] != f["rounded"] or \
                        e["long"] != f["long"] or e["nasal"] != f["nasal"]:
                    continue
                d = abs(height[e["height"]] - height[f["height"]])
                if d <= 1 and d < best_d:
                    best, best_d = w, d
            if best:
                pairs[v] = {group(v): v, group(best): best}
        if len({frozenset(x.values()) for x in pairs.values()}) < 2:
            self.notes.append("harmonia vocálica sorteada, mas o inventário não tem pares suficientes")
            return {"enabled": False}
        neutral = sorted(set(self.vowels) - set(pairs))
        return {"enabled": True, "type": "backness", "pairs": pairs, "neutral": neutral}

    def harmonize(self, affix: Segs, stem: Segs, kind: str) -> Segs:
        h = self.spec.get("harmony", {})
        if not h.get("enabled"):
            return affix
        pairs = h["pairs"]
        order = reversed(stem) if kind == "suffix" else iter(stem)
        trigger = next((s for s in order if s in pairs), None)
        if trigger is None:
            return affix
        g = "front" if self.vowels[trigger]["backness"] == "front" else "back"
        return [pairs[s].get(g, s) if s in pairs else s for s in affix]

    # ══ 2. Valores de cada unidade de slot ═══════════════════════════════
    def agreement_cells(self) -> List[str]:
        ag = self.cats.get("agreement", {})
        if not ag.get("grammaticalized"):
            return []
        cells = []
        for num in ag["numbers"]:
            persons = list(ag["persons"])
            if num != "singular":
                if ag["clusivity"] == "inclusive_exclusive":
                    persons = ["1incl", "1excl"] + persons[1:]
                elif ag["clusivity"] == "inclusive_only":
                    persons = ["1", "1incl"] + persons[1:]
            cells += [f"{p}.{num}" for p in persons]
        return cells

    def unit_values(self, unit: str) -> List[str]:
        if unit.startswith("agreement_"):
            return self.agreement_cells()
        c = self.cats[unit]
        if unit == "definiteness":
            bound = [k for k, m in c["markers"].items() if m["realization"] in ("affix", "clitic")]
            return ["unmarked"] + bound
        return list(c["values"])

    def unit_default(self, unit: str) -> str:
        if unit.startswith("agreement_"):
            return "3.singular"
        if unit == "definiteness":
            return "unmarked"
        return self.cats[unit]["default"]

    def is_zero(self, unit: str, value: str) -> bool:
        if unit.startswith("agreement_"):
            return value in self.cats["agreement"].get("zero", [])
        c = self.cats[unit]
        if unit == "definiteness":
            m = c["markers"].get(value)
            return value == "unmarked" or not m or m["realization"] not in ("affix", "clitic")
        return value in c.get("zero", [])

    @staticmethod
    def cell_key(units: Sequence[str], values: Sequence[str]) -> str:
        return "|".join(f"{u}={v}" for u, v in zip(units, values))

    # ══ 3. Afixos ════════════════════════════════════════════════════════
    def _new_affix(self, kind: str, used: set) -> Segs:
        segs: Segs = []
        for _ in range(40):
            segs = self.ph.generate_affix(kind)["segments"]
            if kind == "prefix" and segs[0] in self.ph.no_initial:
                continue  # o prefixo inicia a palavra: respeita as restrições iniciais
            if tuple(segs) not in used:
                return segs
        for _ in range(80):  # inventário pequeno: afixos de duas partes
            a = self.ph.generate_affix(kind)["segments"]
            b = self.ph.generate_affix(kind)["segments"]
            if self.is_vowel(a[-1]) == self.is_vowel(b[0]):
                continue  # junção interna precisa alternar C/V (sem hiato nem encontro)
            segs = a + b
            if tuple(segs) not in used:
                return segs
        return segs  # aceita a colisão (sincretismo)

    def _slot_forms(self, slot: Dict, kind: str) -> Dict[str, Segs]:
        units = slot["categories"]
        separate = (len(units) == 1 and units[0].startswith("agreement_")
                    and self.cats["agreement"].get("person_number") == "separate")
        forms: Dict[str, Segs] = {}
        used: set = set()
        if separate:  # pessoa e número em afixos separados dentro do mesmo slot
            persons, numbers = {}, {}
            for cell in self.agreement_cells():
                p, n = cell.split(".", 1)
                for table, key, z in ((persons, p, p == "3"), (numbers, n, n == "singular")):
                    if key not in table:
                        table[key] = [] if z else self._new_affix(kind, used)
                        used.add(tuple(table[key]))
            for cell in self.agreement_cells():
                p, n = cell.split(".", 1)
                # "+" marca a fronteira interna: o sândi a trata como fronteira de morfema
                joint = ["+"] if persons[p] and numbers[n] else []
                forms[self.cell_key(units, [cell])] = persons[p] + joint + numbers[n]
            return forms

        p_syncretism = 0.12 if self.fusion == "fusional" and len(units) > 1 else 0.0
        for combo in itertools.product(*(self.unit_values(u) for u in units)):
            key = self.cell_key(units, combo)
            if all(self.is_zero(u, v) for u, v in zip(units, combo)):
                forms[key] = []
                continue
            if used and self.rng.random() < p_syncretism:
                forms[key] = list(self.rng.choice(sorted(used)))
                continue
            segs = self._new_affix(kind, used)
            used.add(tuple(segs))
            forms[key] = segs
        return forms

    def _build_affixes(self) -> Dict:
        ic = self.catdata["inflection_classes"]
        out = {}
        for domain in ("noun", "verb"):
            sl = self.catdata["slots"][domain]
            slots = ([dict(s, position="prefix") for s in sl["prefixes"]]
                     + [dict(s, position="suffix") for s in sl["suffixes"]])
            n_classes = max(1, ic.get(domain, 1))
            class_dep = [n_classes > 1 and len(s["categories"]) > 1 for s in slots]
            if n_classes > 1 and slots and not any(class_dep):
                # sem pacotes: a classe flexional fica no slot de caso/número ou TAM/concordância
                priority = ["case", "number", "agreement_A", "tense", "mood", "aspect", "agreement_P"]
                ranked = sorted(range(len(slots)), key=lambda i: min(
                    (priority.index(c) for c in slots[i]["categories"] if c in priority), default=99))
                class_dep[ranked[0]] = True
            result = []
            for s, dep in zip(slots, class_dep):
                kind = s["position"]
                classes = range(n_classes) if dep else range(1)
                result.append({
                    "name": s["name"], "categories": s["categories"], "position": kind,
                    "realization": s["realization"], "class_dependent": dep,
                    "forms": {str(c): self._slot_forms(s, kind) for c in classes},
                })
            out[domain] = result
        return out

    # ══ 4. Processos não lineares ════════════════════════════════════════
    def _instantiate(self, pattern: List[str], skeleton: Segs) -> Segs:
        return [skeleton[int(t[1]) - 1] if t.startswith("C") and t[1:].isdigit() else t
                for t in pattern]

    def _new_pattern(self, used: set) -> List[str]:
        vowels = self._short_plain_vowels()
        longs = [k for k, e in self.vowels.items() if e["long"] and not e["nasal"]]
        samples = [self.ph.generate_skeleton()["segments"] for _ in range(15)]
        shapes = {("C1", "V", "C2", "V", "C3"): 0.4, ("C1", "V", "C2", "C3", "V"): 0.15,
                  ("C1", "L", "C2", "V", "C3"): 0.15, ("V", "C1", "C2", "V", "C3"): 0.1,
                  ("C1", "V", "C2", "V", "C3", "V"): 0.2}
        pattern: List[str] = []
        for _ in range(200):
            shape = self.rng.choices(list(shapes), list(shapes.values()))[0]
            if "L" in shape and not longs:
                continue
            pattern = [self.rng.choice(vowels) if t == "V" else self.rng.choice(longs) if t == "L"
                       else t for t in shape]
            if tuple(pattern) in used:
                continue
            if all(self.ph.is_valid(self._instantiate(pattern, sk)) for sk in samples):
                return pattern
        return pattern

    def _build_nonlinear(self) -> Dict:
        out: Dict[str, List[Dict]] = {"noun": [], "verb": []}
        patterns: Dict = {}
        if self.skeleton:
            used: set = set()
            for domain in ("noun", "verb"):
                p = self._new_pattern(used)
                used.add(tuple(p))
                patterns[f"{domain}_default"] = p
            patterns["_used"] = used

        for domain in ("noun", "verb"):
            for item in self.catdata["slots"][domain]["nonlinear"]:
                cat, kind = item["category"], item["realization"]
                c = self.cats[cat]
                marked = [v for v in c["values"] if v != c["default"]]
                entry: Dict = {"category": cat, "realization": kind, "fallback_affixes": {}}
                used_aff: set = set()

                if kind == "stem_change":
                    vowels = self._short_plain_vowels()
                    if len(vowels) < 2:
                        kind = entry["realization"] = "fallback"
                    else:
                        maps: Dict[str, Dict[str, str]] = {}
                        for v in marked:
                            perm = vowels[:]
                            for _ in range(500):
                                self.rng.shuffle(perm)
                                if any(a == b for a, b in zip(vowels, perm)):
                                    continue  # toda vogal precisa mudar
                                if all(perm[i] != m[x] for m in maps.values()
                                       for i, x in enumerate(vowels)):
                                    break  # e mudar de forma diferente em cada valor
                            maps[v] = dict(zip(vowels, perm))
                        entry["vowel_maps"] = maps
                elif kind == "tone":
                    if len(self.tones) >= 2 and self.rules.get("tone_bearing"):
                        entry["tones"] = {v: self.rng.choice(self.tones) for v in marked}
                    else:
                        kind = entry["realization"] = "fallback"
                        self.notes.append(f"{cat}: tom sem sistema tonal no inventário; usando sufixos")
                elif kind == "reduplication":
                    procs = set(self.typology.get("active_processes", []))
                    entry["type"] = "full" if "reduplication_full" in procs or \
                        "reduplication_partial" not in procs else "partial"
                    entry["value"] = marked[0] if marked else None
                    for v in marked[1:]:
                        entry["fallback_affixes"][v] = self._new_affix("suffix", used_aff)
                        used_aff.add(tuple(entry["fallback_affixes"][v]))
                elif kind == "transfix":
                    if not self.skeleton:
                        kind = entry["realization"] = "fallback"
                    else:
                        entry["patterns"] = {}
                        for v in c["values"]:
                            p = (patterns[f"{domain}_default"] if v == c["default"]
                                 else self._new_pattern(patterns["_used"]))
                            patterns["_used"].add(tuple(p))
                            entry["patterns"][v] = p

                if kind == "fallback":
                    for v in marked:
                        entry["fallback_affixes"][v] = self._new_affix("suffix", used_aff)
                        used_aff.add(tuple(entry["fallback_affixes"][v]))
                out[domain].append(entry)
        patterns.pop("_used", None)
        return {"processes": out, "patterns": patterns}

    # ══ 5. Palavras gramaticais livres ═══════════════════════════════════
    def _function_word(self, used: set) -> Segs:
        for _ in range(60):
            w = self.ph.generate_syllables(1)[0]
            if tuple(w) not in used:
                return w
        return self.ph.generate_syllables(2)[0] + self.ph.generate_syllables(1)[0]

    def _build_free_markers(self) -> Dict:
        out: Dict[str, Dict] = {}
        used: set = set()
        for domain in ("noun", "verb"):
            for item in self.catdata["slots"][domain]["free_markers"]:
                cat, real, pos = item["category"], item["realization"], item["position"]
                c = self.cats[cat]
                entry = out.setdefault(cat, {"forms": {}, "positions": {}, "realization": {}})
                if cat == "definiteness":
                    values = [k for k, m in c["markers"].items() if m["realization"] == real]
                elif cat == "negation":
                    values = ["negative"]
                elif cat == "classifiers":
                    values = c["values"]
                else:
                    values = [v for v in c["values"] if v not in c.get("zero", [])]
                for v in values:
                    w = self._function_word(used)
                    used.add(tuple(w))
                    entry["forms"][v] = w
                    entry["positions"][v] = pos
                    entry["realization"][v] = real
        return out

    # ══ 6. Sândi ═════════════════════════════════════════════════════════
    def _variants(self, morphs: List[Dict], i: int) -> List[List[Dict]]:
        """Reparos possíveis na fronteira entre morphs[i] e morphs[i+1], em ordem de preferência."""
        s = self.spec["sandhi"]
        L, R = morphs[i]["segs"], morphs[i + 1]["segs"]
        if not L or not R:
            return []
        ep = s["epenthetic_vowel"]

        def make(new_l: Segs, new_r: Segs, extra: Optional[Segs] = None) -> List[Dict]:
            m = [dict(x) for x in morphs]
            m[i]["segs"], m[i + 1]["segs"] = new_l, (extra or []) + new_r
            return m

        def keeps(seg_list: Segs, role: str) -> bool:
            if not seg_list:
                return False
            return role != "root" or any(x in self.vowels for x in seg_list) or self.skeleton

        out: List[List[Dict]] = []
        if self.is_cons(L[-1]) and self.is_cons(R[0]):
            epen = make(L, R, [ep])
            dels = []
            if keeps(L[:-1], morphs[i]["role"]):
                dels.append(make(L[:-1], R))
            if keeps(R[1:], morphs[i + 1]["role"]):
                dels.append(make(L, R[1:]))
            if s["deletion_side"] == "right":
                dels.reverse()
            out = [epen] + dels if s["cluster"] == "epenthesis" else dels + [epen]
        elif self.is_vowel(L[-1]) and self.is_vowel(R[0]):
            front = self.vowels[L[-1]]["backness"] == "front"
            glide = s["glides"]["front" if front else "back"] or s["glides"]["back" if front else "front"]
            options = {"glide": [make(L, R, [glide])] if glide else [],
                       "consonant": [make(L, R, [s["hiatus_consonant"]])] if s["hiatus_consonant"] else [],
                       "elision": []}
            el = []
            if keeps(L[:-1], morphs[i]["role"]):
                el.append(make(L[:-1], R))
            if keeps(R[1:], morphs[i + 1]["role"]):
                el.append(make(L, R[1:]))
            if s["elision_side"] == "right":
                el.reverse()
            options["elision"] = el
            order = [s["hiatus"]] + [k for k in ("elision", "glide", "consonant") if k != s["hiatus"]]
            out = [v for k in order for v in options[k]]
        return out

    def _assimilate(self, morphs: List[Dict]) -> List[Dict]:
        s = self.spec["sandhi"]
        m = [dict(x, segs=list(x["segs"])) for x in morphs]
        for i in range(len(m) - 1):
            L, R = m[i]["segs"], m[i + 1]["segs"]
            if not L or not R or not (self.is_cons(L[-1]) and self.is_cons(R[0])):
                continue
            a, b = L[-1], R[0]
            if s["nasal_assimilation"] and self.cons[a]["manner"] == "nasal" and \
                    self.cons[b]["manner"] in ("stop", "affricate"):
                n = self._homorganic_nasal(b)
                if n:
                    L[-1] = n
            elif s["voicing_assimilation"] and self._is_obstruent(a) and self._is_obstruent(b) \
                    and self._is_voiced(a) != self._is_voiced(b):
                c = self._voicing_counterpart(a, self._is_voiced(b))
                if c:
                    L[-1] = c
        return m

    def resolve(self, morphs: List[Dict]) -> Tuple[List[Dict], bool, List[str]]:
        """Aplica sândi até a palavra ser válida pela fonotática."""
        flat = lambda m: [x for y in m for x in y["segs"]]
        log: List[str] = []
        if self.ph.is_valid(flat(morphs)):
            return morphs, True, log
        a = self._assimilate(morphs)
        if flat(a) != flat(morphs):
            log.append("assimilação")
            morphs = a
            if self.ph.is_valid(flat(morphs)):
                return morphs, True, log

        root = next(i for i, x in enumerate(morphs) if x["role"] == "root")
        bounds = sorted(range(len(morphs) - 1), key=lambda i: min(abs(i - root), abs(i + 1 - root)))
        for _ in range(len(bounds) + 1):
            fixed = False
            for i in bounds:  # um reparo que valida a palavra inteira
                for v in self._variants(morphs, i):
                    if self.ph.is_valid(flat(v)):
                        return v, True, log + ["sândi"]
            for i in bounds:  # senão, repara a primeira fronteira problemática e continua
                vs = self._variants(morphs, i)
                if vs and not self._junction_ok(morphs, i):
                    morphs, fixed = vs[0], True
                    log.append("sândi")
                    break
            if not fixed:
                break

        ep = self.spec["sandhi"]["epenthetic_vowel"]
        w = flat(morphs)
        for pre, post in ((False, True), (True, False), (True, True)):  # epêntese nas bordas
            cand = ([ep] if pre else []) + w + ([ep] if post else [])
            if self.ph.is_valid(cand):
                m = [dict(x) for x in morphs]
                if post:
                    m[-1] = dict(m[-1], segs=m[-1]["segs"] + [ep])
                if pre:
                    m[0] = dict(m[0], segs=[ep] + m[0]["segs"])
                return m, True, log + ["epêntese de borda"]
        return morphs, False, log + ["forma inválida"]

    def _junction_ok(self, morphs: List[Dict], i: int) -> bool:
        L, R = morphs[i]["segs"], morphs[i + 1]["segs"]
        if not L or not R:
            return True
        if self.is_vowel(L[-1]) and self.is_vowel(R[0]):
            return self.rules["allow_hiatus"]
        if self.is_cons(L[-1]) and self.is_cons(R[0]):
            return L[-1] in self.ph.coda1 or (L[-1], R[0]) in self.ph.onset2
        return True

    # ══ 7. Léxico de exemplo ═════════════════════════════════════════════
    def _lexeme(self, domain: str) -> Dict:
        root = self.ph.generate_root()
        n_classes = max(1, self.catdata["inflection_classes"].get(domain, 1))
        entry = {"root": root["segments"], "form": root["form"], "tones": root.get("tones", []),
                 "class": self.rng.randrange(n_classes)}
        g = self.cats.get("gender", {})
        if domain == "noun" and g.get("grammaticalized"):
            entry["gender"] = self.rng.choice(g["values"])
        return entry

    # ══ 8. Flexão ════════════════════════════════════════════════════════
    def _stem(self, entry: Dict, domain: str, feats: Dict) -> Tuple[Segs, Optional[str], List[Segs], Segs]:
        """
        Radical após processos não lineares.
        Devolve (radical, tom, sufixos de reserva, reduplicante). O reduplicante é
        um morfema à parte, para que o sândi trate a fronteira com a raiz.
        """
        stem = list(entry["root"])
        nl = self.spec["nonlinear"]
        if self.skeleton:
            pattern = nl["patterns"].get(f"{domain}_default")
            for p in nl["processes"][domain]:
                if p["realization"] == "transfix":
                    pattern = p["patterns"].get(feats.get(p["category"]), pattern)
            stem = self._repair_stem(self._instantiate(pattern, stem))
        tone, fallback, redup = None, [], []
        for p in nl["processes"][domain]:
            v = feats.get(p["category"])
            if v is None or v == self.cats[p["category"]]["default"]:
                continue
            if v in p.get("fallback_affixes", {}):
                fallback.append(p["fallback_affixes"][v])
                continue
            if p["realization"] == "stem_change":
                vmap = p["vowel_maps"][v]
                base = lambda s: s.replace("ː", "")  # vogais longas usam o mapa da curta
                idx = max((i for i, s in enumerate(stem) if base(s) in vmap), default=None)
                if idx is not None:
                    old = stem[idx]
                    new = vmap[base(old)]
                    if old != base(old) and new + "ː" in self.vowels:
                        new += "ː"
                    stem[idx] = new
            elif p["realization"] == "reduplication" and v == p.get("value"):
                if p["type"] == "full":
                    redup = list(stem)
                else:  # primeira sílaba (C)V
                    first_v = next((i for i, s in enumerate(stem) if s in self.vowels), 0)
                    redup = stem[:first_v + 1]
            elif p["realization"] == "tone":
                tone = p["tones"].get(v)
        return stem, tone, fallback, redup

    def _repair_stem(self, stem: Segs) -> Segs:
        """Radical de raiz consonantal que viola a fonotática: epêntese interna/final."""
        if self.ph.is_valid(stem):
            return stem
        ep = self.spec["sandhi"]["epenthetic_vowel"]
        split = []
        for i, x in enumerate(stem):
            split.append(x)
            if i + 1 < len(stem) and self.is_cons(x) and self.is_cons(stem[i + 1]):
                split.append(ep)
        for cand in (split, split + [ep], stem + [ep]):
            if self.ph.is_valid(cand):
                return cand
        return stem

    def defaults(self, domain: str) -> Dict[str, str]:
        units = NOUN_CATS if domain == "noun" else VERB_CATS
        d = {u: self.unit_default(u) for u in units if self.cats.get(u, {}).get("grammaticalized")}
        if domain == "verb" and self.cats.get("agreement", {}).get("grammaticalized"):
            for arg in self.cats["agreement"]["arguments"]:
                d[f"agreement_{arg}"] = "3.singular"
        return d

    def inflect(self, entry: Dict, domain: str, features: Optional[Dict[str, str]] = None) -> Dict:
        feats = {**self.defaults(domain), **(features or {})}
        if domain == "noun" and entry.get("gender"):
            feats["gender"] = entry["gender"]
        stem, tone, fallback, redup = self._stem(entry, domain, feats)

        morphs: List[Dict] = []
        slots = self.spec["affixes"][domain]
        for s in [x for x in slots if x["position"] == "prefix"]:
            self._add_affix(morphs, s, feats, entry, stem)
        if redup:
            morphs.append({"segs": redup, "role": "prefix", "label": "RED", "sep": "-"})
        morphs.append({"segs": stem, "role": "root", "label": "√", "sep": "-"})
        for segs in fallback:
            morphs.append({"segs": self.harmonize(segs, stem, "suffix"), "role": "suffix",
                           "label": "", "sep": "-"})
        for s in [x for x in slots if x["position"] == "suffix"]:
            self._add_affix(morphs, s, feats, entry, stem)

        underlying = self._join(morphs)
        morphs, valid, log = self.resolve(morphs)
        surface_segs = [x for m in morphs for x in m["segs"]]
        surface = self._with_tones(surface_segs, entry, morphs, tone)

        before, after = [], []
        for cat, fm in self.spec["free_markers"].items():
            v = feats.get(cat)
            if cat == "negation" and v != "negative":
                continue
            if v in fm["forms"]:
                (before if fm["positions"][v] == "before" else after).append("".join(fm["forms"][v]))
        glosses = [gloss(v) for k, v in feats.items()
                   if v is not None and k != "gender" and v != self.unit_default(k) and gloss(v)]
        return {
            "surface": surface,
            "underlying": underlying,
            "phrase": " ".join(before + [surface] + after),
            "gloss": ".".join(glosses),
            "valid": valid,
            "sandhi": log,
        }

    def _add_affix(self, morphs: List[Dict], slot: Dict, feats: Dict, entry: Dict, stem: Segs) -> None:
        values = [feats.get(u, self.unit_default(u)) for u in slot["categories"]]
        if None in values:  # ex.: agreement_P=None num verbo intransitivo
            return
        key = self.cell_key(slot["categories"], values)
        cls = str(entry.get("class", 0)) if slot["class_dependent"] else "0"
        segs = slot["forms"].get(cls, slot["forms"]["0"]).get(key, [])
        if segs:
            role = "prefix" if slot["position"] == "prefix" else "suffix"
            parts, cur = [], []
            for x in segs:
                if x == "+":
                    parts.append(cur)
                    cur = []
                else:
                    cur.append(x)
            parts.append(cur)
            for part in parts:
                morphs.append({"segs": self.harmonize(part, stem, role), "role": role,
                               "label": slot["name"],
                               "sep": "=" if slot["realization"] == "clitic" else "-"})

    @staticmethod
    def _join(morphs: List[Dict]) -> str:
        out = ""
        for i, m in enumerate(morphs):
            if i:
                out += m["sep"] if m["role"] == "suffix" else morphs[i - 1]["sep"] if morphs[i - 1]["role"] == "prefix" else "-"
            out += "".join(m["segs"])
        return out

    def _with_tones(self, segs: Segs, entry: Dict, morphs: List[Dict], tone: Optional[str]) -> str:
        if not (self.rules.get("tone_bearing") and self.tones):
            return "".join(segs)
        sylls = self.ph.syllabify(segs)
        if not sylls:
            return "".join(segs)
        prefix_v = sum(1 for m in morphs if m["role"] == "prefix" for s in m["segs"] if s in self.vowels)
        root_tones = list(entry.get("tones") or [])
        default = max(self.tones, key=lambda t: self.ph.tones[t]["frequency"])
        if tone and root_tones:
            root_tones[-1] = tone
        out = []
        for i, syl in enumerate(sylls):
            j = i - prefix_v
            t = root_tones[j] if 0 <= j < len(root_tones) else default
            out.append("".join(syl) + t)
        return ".".join(out)

    # ══ 9. Paradigmas ════════════════════════════════════════════════════
    def _dims(self, domain: str) -> Tuple[Optional[Tuple[str, List[str]]], Optional[Tuple[str, List[str]]]]:
        g = lambda c: self.cats.get(c, {}).get("grammaticalized")
        if domain == "noun":
            rows = next(((c, self.cats[c]["values"]) for c in ("case", "definiteness") if g(c)), None)
            cols = ("number", self.cats["number"]["values"]) if g("number") else None
        else:
            ag = self.cats.get("agreement", {})
            rows = None
            if ag.get("grammaticalized"):
                arg = "A" if "A" in ag["arguments"] else next(iter(ag["arguments"]))
                rows = (f"agreement_{arg}", self.agreement_cells())
            cand = [c for c in ("tense", "aspect", "mood") if g(c)]
            if rows is None and len(cand) > 1:
                rows = (cand[-1], self.cats[cand[-1]]["values"])
                cand = cand[:-1]
            cols = (cand[0], self.cats[cand[0]]["values"]) if cand else None
        return rows, cols

    def paradigm(self, entry: Dict, domain: str) -> Dict:
        rows, cols = self._dims(domain)
        rlist = rows[1] if rows else [""]
        clist = cols[1] if cols else [""]
        cells = []
        for rv in rlist:
            line = []
            for cv in clist:
                f = {}
                if rows:
                    f[rows[0]] = rv
                if cols:
                    f[cols[0]] = cv
                if domain == "verb" and "agreement_P" in self.defaults("verb") and \
                        (not rows or rows[0] != "agreement_P"):
                    f["agreement_P"] = None  # paradigma intransitivo: sem marca de objeto
                line.append(self.inflect(entry, domain, f))
            cells.append(line)
        return {"lexeme": entry["form"], "rows": [rows[0], rlist] if rows else None,
                "columns": [cols[0], clist] if cols else None, "cells": cells}

    # ══ Construção completa ══════════════════════════════════════════════
    def build(self, n_nouns: int = 6, n_verbs: int = 6) -> Dict:
        self.spec = {"sandhi": self._build_sandhi()}
        self.spec["harmony"] = self._build_harmony()
        self.spec["affixes"] = self._build_affixes()
        self.spec["nonlinear"] = self._build_nonlinear()
        self.spec["free_markers"] = self._build_free_markers()
        lexicon = {"nouns": [self._lexeme("noun") for _ in range(n_nouns)],
                   "verbs": [self._lexeme("verb") for _ in range(n_verbs)]}
        self.spec["lexicon_sample"] = lexicon
        paradigms = {"noun": self.paradigm(lexicon["nouns"][0], "noun"),
                     "verb": self.paradigm(lexicon["verbs"][0], "verb")}
        invalid = sum(1 for p in paradigms.values() for line in p["cells"] for c in line if not c["valid"])
        if invalid:
            self.notes.append(f"{invalid} formas dos paradigmas não puderam ser reparadas")
        return {**self.spec, "paradigms": paradigms,
                "metadata": {"seed": self.seed, "fusion": self.fusion,
                             "consonantal_roots": self.skeleton, "notes": self.notes}}

    @classmethod
    def load(cls, morphology: Dict, inventory: Dict, rules: Dict, categories: Dict,
             typology: Optional[Dict] = None) -> "MorphologicalEngine":
        """Recria o motor a partir de um morphology.json salvo, para flexionar novas palavras."""
        eng = cls(inventory, rules, categories, typology, seed=morphology["metadata"]["seed"])
        eng.spec = {k: morphology[k] for k in ("sandhi", "harmony", "affixes", "nonlinear",
                                               "free_markers", "lexicon_sample")}
        return eng


# ═══════════════════════════════════════════════════════════════════════════
# Exibição
# ═══════════════════════════════════════════════════════════════════════════

def _affix_str(segs: Segs, position: str, realization: str) -> str:
    if not segs:
        return "Ø"
    sep = "=" if realization == "clitic" else "-"
    w = "".join(segs).replace("+", "·")
    return f"{sep}{w}" if position == "suffix" else f"{w}{sep}"


def print_table(p: Dict) -> None:
    rows = p["rows"][1] if p["rows"] else [""]
    cols = p["columns"][1] if p["columns"] else [""]
    cells = [[c["phrase"] + ("" if c["valid"] else " *") for c in line] for line in p["cells"]]
    rlabels = [gloss(r) or r for r in rows]
    w0 = max([visible_len(r) for r in rlabels] + [4]) + 2
    widths = [max([visible_len(gloss(c) or c)] + [visible_len(line[j]) for line in cells]) + 2
              for j, c in enumerate(cols)]
    if p["columns"]:
        print("    " + " " * w0 + "".join(pad(gloss(c) or c, widths[j]) for j, c in enumerate(cols)))
    for r, line in zip(rlabels, cells):
        print("    " + pad(r, w0) + "".join(pad(x, widths[j]) for j, x in enumerate(line)))


def print_summary(eng: MorphologicalEngine, data: Dict) -> None:
    s, h = data["sandhi"], data["harmony"]
    print("\nSÂNDI")
    print(f"  vogal epentética /{s['epenthetic_vowel']}/; encontros: {s['cluster']}"
          f"{' (' + s['deletion_side'] + ')' if s['cluster'] == 'deletion' else ''}; "
          f"hiato: {s['hiatus']}; assimilação nasal: {'sim' if s['nasal_assimilation'] else 'não'}; "
          f"assimilação de vozeamento: {'sim' if s['voicing_assimilation'] else 'não'}")
    if h.get("enabled"):
        pairs = sorted({"/".join(sorted(set(p.values()))) for p in h["pairs"].values()})
        print(f"  harmonia vocálica anterior/posterior: {' '.join(pairs)}")

    for domain, title in (("noun", "NOME"), ("verb", "VERBO")):
        print(f"\nAFIXOS — {title}")
        slots = data["affixes"][domain]
        if not slots:
            print("  (nenhum)")
        for slot in slots:
            for cls, forms in slot["forms"].items():
                label = slot["name"] + (f" [classe {int(cls) + 1}]" if slot["class_dependent"] else "")
                items = []
                for key, segs in list(forms.items())[:14]:
                    vals = [kv.split("=", 1)[1] for kv in key.split("|")]
                    g = ".".join(x for x in (gloss(v) for v in vals) if x) or "∅"
                    items.append(f"{g} {_affix_str(segs, slot['position'], slot['realization'])}")
                more = f" … (+{len(forms) - 14})" if len(forms) > 14 else ""
                print(f"  {label}: " + ", ".join(items) + more)
        for p in data["nonlinear"]["processes"][domain]:
            desc = p["realization"]
            if p["realization"] == "stem_change":
                desc += "; " + "; ".join(f"{gloss(v)}: " + " ".join(f"{a}→{b}" for a, b in m.items())
                                         for v, m in p["vowel_maps"].items())
            elif p["realization"] == "reduplication":
                desc += f" {p['type']} = {gloss(p['value'])}"
            elif p["realization"] == "tone":
                desc += "; " + ", ".join(f"{gloss(v)} {t}" for v, t in p["tones"].items())
            elif p["realization"] == "transfix":
                desc += "; " + ", ".join(f"{gloss(v)} {''.join(pt)}" for v, pt in p["patterns"].items())
            if p["fallback_affixes"]:
                desc += "; " + ", ".join(f"{gloss(v)} -{''.join(a)}" for v, a in p["fallback_affixes"].items())
            print(f"  {p['category']} (não linear): {desc}")

    if data["free_markers"]:
        print("\nPALAVRAS GRAMATICAIS")
        for cat, fm in data["free_markers"].items():
            items = ", ".join(f"{gloss(v) if cat != 'classifiers' else v} {''.join(w)}"
                              f" ({'antes' if fm['positions'][v] == 'before' else 'depois'})"
                              for v, w in fm["forms"].items())
            print(f"  {cat}: {items}")

    pats = data["nonlinear"]["patterns"]
    if pats:
        print("\nPADRÕES (raízes consonantais): " + ", ".join(f"{k}: {''.join(v)}" for k, v in pats.items()))

    for domain, title in (("noun", "PARADIGMA NOMINAL"), ("verb", "PARADIGMA VERBAL")):
        p = data["paradigms"][domain]
        entry = data["lexicon_sample"][domain + "s"][0]
        extra = f", classe {entry['class'] + 1}" if max(1, data.get("_classes", {}).get(domain, 1)) > 1 else ""
        gender = f", {entry['gender']}" if entry.get("gender") else ""
        print(f"\n{title}: {p['lexeme']}{gender}{extra}")
        print_table(p)

    if data["metadata"]["notes"]:
        print("\nNotas: " + "; ".join(data["metadata"]["notes"]))


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def _load(path: Path, hint: str) -> Dict:
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}\nRode antes: {hint}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera a morfologia concreta da conlang.")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--nouns", type=int, default=6, help="nº de nomes no léxico de exemplo")
    ap.add_argument("--verbs", type=int, default=6, help="nº de verbos no léxico de exemplo")
    ap.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    ap.add_argument("--phonotactics", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    ap.add_argument("--morph", type=Path, default=DEFAULT_MORPH)
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    inventory = _load(args.inventory, "phonemic_inventory.py")
    rules = _load(args.phonotactics, "phonotactics.py")
    categories = _load(args.categories, "grammatical_categories.py")
    typology = json.loads(args.morph.read_text(encoding="utf-8")) if args.morph.exists() else {}

    eng = MorphologicalEngine(inventory, rules, categories, typology, seed=args.seed)
    data = eng.build(args.nouns, args.verbs)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["_classes"] = categories["inflection_classes"]
    print_summary(eng, data)
    print(f"\n[OK] Morfologia salva em '{args.output}'.")


if __name__ == "__main__":
    main()
