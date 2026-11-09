"""
Módulo — Posse e determinantes.

Completa o sintagma nominal da conlang com o que o Vulgarlang mostra nas
tabelas "Possession" e "Articles":

    possessivos       — afixos de posse no nome (cão-MEU) ou palavras livres
                        (meu cão), uma forma para cada pessoa da tabela de pronomes
    posse nominal     — 'o cão do homem': genitivo no possuidor, marca no
                        possuído (como o 'wad-e' do Vulgarlang), ambos ou nenhum
    alienabilidade    — partes do corpo e parentes podem ser possuídos de outro
                        jeito que os demais nomes ('minha mão' ≠ 'minha casa')
    artigos no plural — quando a língua tem artigos livres e número

Decisões sorteadas com o WALS (24A, 57A, 58A, 59A), coerentes com a tipologia
morfológica e com as categorias da língua.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico (sândi e flexão), da ortografia e do acento.

Uso:
    python possession/possession.py --language languages/lang-31

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
from morphological_engine import MorphologicalEngine, gloss  # noqa: E402

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

# ═══════════════════════════════════════════════════════════════════════════
# WALS (nº de línguas), usado quando o WALS local não existe
# ═══════════════════════════════════════════════════════════════════════════

EMBEDDED = {
    "24A": {"1": 78, "2": 98, "3": 22, "4": 32},          # locus da marcação na posse nominal
    "58A": {"1": 43, "2": 201},                            # posse obrigatória
    "59A": {"1": 125, "2": 94, "3": 20, "4": 4},           # classes de posse
}
EMBEDDED_57A_BY_26A = {  # afixos possessivos | prefixação vs. sufixação
    "1": {"1": 4, "2": 37, "3": 2, "4": 59}, "2": {"1": 34, "2": 121, "3": 5, "4": 117},
    "3": {"1": 42, "2": 42, "3": 3, "4": 24}, "4": {"1": 70, "2": 42, "3": 8, "4": 9},
    "5": {"1": 32, "2": 33, "3": 3, "4": 7}, "6": {"1": 18, "2": 7, "3": 4, "4": 14},
}
AFFIX_POSITION_26A = {"little_affixation": "1", "strongly_suffixing": "2", "weakly_suffixing": "3",
                      "equal": "4", "weakly_prefixing": "5", "strongly_prefixing": "6"}

P_ARTICLE_NUMBER = 0.45   # aproximação: artigos livres que distinguem número (como 'the'/'some')
P_ECHO_PRONOUN = 0.5      # afixos possessivos que lembram os pronomes (gramaticalizados deles)

# Nomes possuídos inalienavelmente (campos semânticos do Concepticon)
INALIENABLE_FIELDS = {"The body", "Kinship"}
FOOD_FIELDS = {"Food and drink"}  # animais de estimação não entram como comida

POSSESSIVE_EN = {"1": "my", "2": "your", "3": "his/her/its"}
GENDER_EN = {"masculine": "his", "feminine": "her", "neuter": "its"}


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


def cell_english(cell: str) -> str:
    """'1excl.plural' → 'our (excl.)'; '3.singular.feminine' → 'her'."""
    parts = cell.split(".")
    person, number = parts[0], parts[1]
    g = parts[2] if len(parts) > 2 else None
    p = person[0]
    clus = " (incl.)" if "incl" in person else " (excl.)" if "excl" in person else ""
    if number == "singular":
        return GENDER_EN.get(g, POSSESSIVE_EN[p]) if p == "3" else POSSESSIVE_EN[p]
    base = {"1": "our", "2": "your", "3": "their"}[p]
    num = "" if number == "plural" else f" ({number})"
    return f"{base}{clus}{num}" + (" (pl.)" if p == "2" and number == "plural" else "")


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class PossessionBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None, wals_dir: Optional[Path] = None):
        d = language_dir
        self.inv = _load(d / "phonemic_inventory.json")
        self.rules = _load(d / "phonotactics.json")
        self.catdata = _load(d / "grammatical_categories.json")
        self.morph = _load(d / "morphology.json")
        self.lex = _load(d / "lexicon.json")
        if not all((self.inv, self.rules, self.catdata, self.morph, self.lex)):
            raise SystemExit(f"A pasta {d} precisa ter inventário, fonotática, categorias, "
                             "morfologia e léxico (gere a língua com o orquestrador).")
        self.cats = self.catdata["categories"]
        self.syntax = _load(d / "syntax.json")
        self.typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "possession") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.wals_dir = wals_dir
        self.sources: Dict[str, str] = {}
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, self.typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)  # sorteios próprios
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.pronouns = self.lex["pronouns"]["cells"]
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.vowels = {nfd(v["ipa"]) for v in self.inv["vowels"]}
        self.used = {tuple(self.segments(e["citation"])) for e in self.lex["entries"] if e.get("citation")}
        self.used |= {tuple(p["segments"]) for p in self.pronouns.values()}
        # afixos novos não podem repetir os afixos nominais que a língua já tem
        # (senão '-n' poderia ser ao mesmo tempo genitivo e 'de vocês')
        for slot in self.morph["affixes"]["noun"]:
            for forms in slot["forms"].values():
                self.used |= {tuple(x for x in f if x != "+") for f in forms.values() if f}

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

    def wals(self, fid: str) -> Tuple[Dict[str, int], str]:
        values = self.wals_dir / "values.csv" if self.wals_dir else None
        if values and values.exists():
            with open(values, encoding="utf-8", newline="") as f:
                c = Counter(r["Value"] for r in csv.DictReader(f) if r["Parameter_ID"] == fid)
            if c:
                return dict(c), f"WALS {fid} (n={sum(c.values())})"
        return EMBEDDED[fid], f"WALS {fid} (embutido)"

    def wals_57a(self, affix_code: str) -> Tuple[Dict[str, int], str]:
        values = self.wals_dir / "values.csv" if self.wals_dir else None
        if values and values.exists():
            by: Dict[str, Dict[str, str]] = defaultdict(dict)
            with open(values, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    if r["Parameter_ID"] in ("26A", "57A"):
                        by[r["Language_ID"]][r["Parameter_ID"]] = r["Value"]
            c = Counter(d["57A"] for d in by.values() if d.get("26A") == affix_code and "57A" in d)
            if sum(c.values()) >= 5:
                return dict(c), f"WALS 57A|26A={affix_code} (n={sum(c.values())})"
        return EMBEDDED_57A_BY_26A[affix_code], f"WALS 57A|26A={affix_code} (embutido)"

    def pick(self, key: str, counts: Dict[str, int], src: str, allowed=None) -> str:
        self.sources[key] = src
        keys = sorted(k for k in counts if allowed is None or k in allowed)
        return self.rng.choices(keys, [counts[k] for k in keys])[0]

    def new_affix(self, kind: str) -> List[str]:
        for _ in range(40):
            a = self.ph.generate_affix(kind)["segments"]
            if tuple(a) not in self.used:
                self.used.add(tuple(a))
                return a
        return a

    def new_word(self) -> List[str]:
        for _ in range(60):
            w = self.ph.generate_syllables(1)[0]
            if tuple(w) not in self.used:
                self.used.add(tuple(w))
                return w
        return self.ph.generate_syllables(1)[0]

    def attach(self, base: List[str], affix: List[str], kind: str) -> List[str]:
        """Junta afixo e base com o sândi da língua."""
        if kind == "prefix":
            morphs = [{"segs": list(affix), "role": "prefix", "label": "", "sep": "-"},
                      {"segs": list(base), "role": "root", "label": "", "sep": "-"}]
        else:
            morphs = [{"segs": list(base), "role": "root", "label": "", "sep": "-"},
                      {"segs": list(affix), "role": "suffix", "label": "", "sep": "-"}]
        morphs, _, _ = self.eng.resolve(morphs)
        return [s for m in morphs for s in m["segs"]]

    def show(self, ipa: str) -> Dict:
        """Forma pronta: grafia, IPA e pronúncia com acento."""
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = " ".join(self.stress.mark(w) for w in ipa.split(" ")) if self.stress else ipa
        return {"written": written, "ipa": ipa, "pronunciation": pron}

    def retone(self, segs: List[str], base_surface: str, kind: str) -> str:
        """Em línguas tonais, mantém os tons do nome e dá o tom mais comum às sílabas novas."""
        if not any(ch in TONE_LETTERS for ch in base_surface):
            return "".join(segs)
        base_tones = ["".join(ch for ch in s if ch in TONE_LETTERS) for s in base_surface.split(".")]
        sylls = self.ph.syllabify(segs) or [segs]
        default = max(self.ph.tones, key=lambda t: self.ph.tones[t]["frequency"]) if self.ph.tones else ""
        extra = len(sylls) - len(base_tones)
        tones = (base_tones + [default] * extra) if kind == "suffix" else ([default] * extra + base_tones)
        return ".".join("".join(s) + (tones[i] if i < len(tones) else default) for i, s in enumerate(sylls))

    def noun_form(self, e: Dict, number: str = "singular") -> str:
        lex = {"root": e["root"], "form": e["form"], "tones": e.get("tones", []),
               "class": e.get("class") or 0, "gender": e.get("gender")}
        feats = {"number": number} if self.cats["number"].get("grammaticalized") else {}
        return self.eng.inflect(lex, "noun", feats)["surface"]

    # ── decisões ─────────────────────────────────────────────────────────
    def decide(self) -> Dict:
        typ = self.catdata["metadata"]["typology"]
        isolating = typ["synthesis"] == "isolating"
        affix_code = AFFIX_POSITION_26A.get(typ["affix_position"], "2")
        s: Dict = {}

        # 1. Possessivos pronominais (57A)
        p57 = "4" if isolating else self.pick("possessive_affixes", *self.wals_57a(affix_code))
        if isolating:
            self.sources["possessive_affixes"] = "língua isolante: sem afixos possessivos"
        if p57 == "3":
            p57 = self.rng.choice(["1", "2"])
        if p57 in ("1", "2"):
            kind = "prefix" if p57 == "1" else "suffix"
            echo = self.rng.random() < P_ECHO_PRONOUN
            forms = {}
            for cell, p in self.pronouns.items():
                if echo:  # gramaticalizado do pronome: forma reduzida dele
                    segs = list(p["segments"])
                    nuc = next((i for i, x in enumerate(segs) if x in self.vowels), len(segs) - 1)
                    forms[cell] = segs[:nuc + 1] if kind == "prefix" else segs[nuc:] if len(segs) > 2 else segs
                else:
                    forms[cell] = self.new_affix(kind)
            s["pronominal"] = {"strategy": "affix", "position": kind, "from_pronouns": echo, "forms": forms}
        else:
            case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
            # (em raízes consonantais o pronome não passa pelo padrão vocálico: sem genitivo)
            options = {"genitive": 0.4 if "genitive" in case_vals and not isolating and not self.eng.skeleton else 0,
                       "linker": 0.3, "suppletive": 0.3}
            strat = self.rng.choices(list(options), list(options.values()))[0]
            forms = {}
            linker = self.new_word() if strat == "linker" else None
            for cell, p in self.pronouns.items():
                if strat == "genitive":
                    lex = {"root": p["segments"], "form": p["form"], "tones": [], "class": 0, "gender": None}
                    forms[cell] = self.segments(self.eng.inflect(lex, "noun", {"case": "genitive"})["surface"])
                elif strat == "linker":
                    forms[cell] = list(p["segments"]) + [" "] + linker
                else:
                    forms[cell] = self.new_word()
            gen_pos = self.syntax["settings"]["noun_phrase"]["genitive"] if self.syntax else "before"
            s["pronominal"] = {"strategy": strat, "position": gen_pos, "forms": forms,
                               **({"linker": linker} if linker else {})}

        # 2. Posse nominal: 'o cão do homem' (24A)
        has_gen = "genitive" in (self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else [])
        mult = {"2": 3 if has_gen else 0.2, "3": 1.5 if has_gen else 0.2, "1": 1, "4": 1}
        counts, src = self.wals("24A")
        locus = self.pick("nominal_locus", {k: v * mult.get(k, 1) for k, v in counts.items()}, src)
        locus = {"1": "head", "2": "dependent", "3": "double", "4": "none"}[locus]
        if locus in ("dependent", "double") and not has_gen:
            locus = "head" if locus == "double" else "linker"
        nominal: Dict = {"locus": locus}
        if locus in ("head", "double"):
            pr = s["pronominal"]
            third = next((c for c in pr["forms"] if c.startswith("3.singular")), None)
            if pr["strategy"] == "affix" and third:  # como no turco: adam-ın köpeğ-i
                nominal.update(affix=pr["forms"][third], position=pr["position"], from_3sg=True)
            else:
                pos = "suffix" if affix_code in ("1", "2", "3") else self.rng.choice(["prefix", "suffix"])
                nominal.update(affix=self.new_affix(pos), position=pos, from_3sg=False)
        if locus == "linker":
            nominal["linker"] = s["pronominal"].get("linker") or self.new_word()
        nominal["possessor_position"] = self.syntax["settings"]["noun_phrase"]["genitive"] if self.syntax else "before"
        s["nominal"] = nominal

        # 3. Alienabilidade (59A) e posse obrigatória (58A)
        c59 = self.pick("possessive_classes", *self.wals("59A"))
        classes = {"1": 1, "2": 2, "3": 3, "4": 3}[c59]
        alien: Dict = {"classes": classes}
        if classes >= 2:
            alien["inalienable_fields"] = sorted(INALIENABLE_FIELDS)
            alien["alienable_marker"] = self.new_word()  # classificador ou ligador de posse
            if classes == 3:
                alien["food_fields"] = sorted(FOOD_FIELDS)
                alien["food_marker"] = self.new_word()
            c58 = self.pick("obligatory_possession", *self.wals("58A"))
            if c58 == "1" and s["pronominal"]["strategy"] == "affix":
                alien["obligatory"] = True
                alien["unpossessed_affix"] = self.new_affix(s["pronominal"]["position"])
        s["alienability"] = alien

        # 4. Artigos no plural
        fm = self.morph["free_markers"].get("definiteness")
        num = self.cats["number"]
        if fm and num.get("grammaticalized"):
            if self.rng.random() < P_ARTICLE_NUMBER:
                plural_vals = [v for v in num["values"] if v != "singular"]
                arts = {}
                for value, segs in fm["forms"].items():
                    arts[value] = {"singular": list(segs)}
                    for nv in plural_vals:
                        arts[value][nv] = self.new_word()
                s["articles"] = {"inflect_for_number": True, "forms": arts,
                                 "position": next(iter(fm["positions"].values()))}
            else:
                s["articles"] = {"inflect_for_number": False,
                                 "forms": {v: {"singular": list(segs)} for v, segs in fm["forms"].items()},
                                 "position": next(iter(fm["positions"].values()))}
        else:
            s["articles"] = None
            if not fm:
                self.notes.append("a língua não tem artigos livres; não há artigos para flexionar em número")
        self.settings = s
        return s

    # ── aplicação ────────────────────────────────────────────────────────
    def noun_class(self, e: Dict) -> str:
        a = self.settings["alienability"]
        if a["classes"] >= 2 and e.get("field") in INALIENABLE_FIELDS:
            return "inalienable"
        if a["classes"] == 3 and e.get("field") in FOOD_FIELDS:
            return "food"
        return "alienable" if a["classes"] >= 2 else "general"

    def possess(self, e: Dict, cell: str, number: str = "singular") -> Dict:
        """'meu cão' / 'cão-MEU': o nome possuído por uma pessoa da tabela de pronomes."""
        pr, al = self.settings["pronominal"], self.settings["alienability"]
        base_surface = self.noun_form(e, number)
        base = self.segments(base_surface)
        cls = self.noun_class(e)
        gen_before = self.settings["nominal"]["possessor_position"] == "before"
        if cls in ("alienable", "food"):
            # Posse indireta (como nas línguas oceânicas): a marca do possuidor vai num
            # classificador de posse, e o nome possuído fica sem marca — 'CLF-meu cão'.
            clf = al["alienable_marker"] if cls == "alienable" else al["food_marker"]
            if pr["strategy"] == "affix":
                owner = "".join(self.attach(clf, pr["forms"][cell], pr["position"]))
            else:
                det = "".join(pr["forms"][cell])
                owner = f"{det} {''.join(clf)}" if pr["position"] == "before" else f"{''.join(clf)} {det}"
            words = [owner, base_surface] if gen_before else [base_surface, owner]
        elif pr["strategy"] == "affix":  # posse direta: o afixo vai no próprio nome
            words = [self.retone(self.attach(base, pr["forms"][cell], pr["position"]),
                                 base_surface, pr["position"])]
        else:
            det = "".join(pr["forms"][cell])
            words = [det, base_surface] if pr["position"] == "before" else [base_surface, det]
        ipa = " ".join(w.strip() for w in words if w.strip())
        return {**self.show(ipa), "class": cls}

    def nominal(self, possessor: Dict, possessed: Dict) -> Dict:
        """'o cão da mulher' conforme o locus da marcação."""
        n = self.settings["nominal"]
        pss_surface = self.noun_form(possessed)
        pss = pss_surface
        if n["locus"] in ("head", "double"):
            pss = self.retone(self.attach(self.segments(pss_surface), n["affix"], n["position"]),
                              pss_surface, n["position"])
        psr_lex = {"root": possessor["root"], "form": possessor["form"], "tones": possessor.get("tones", []),
                   "class": possessor.get("class") or 0, "gender": possessor.get("gender")}
        if n["locus"] in ("dependent", "double"):
            psr = self.eng.inflect(psr_lex, "noun", {"case": "genitive"})["surface"]
        else:
            psr = self.noun_form(possessor)
        parts = [psr, pss] if n["possessor_position"] == "before" else [pss, psr]
        if n["locus"] == "linker":
            link = "".join(n["linker"])
            parts = [parts[0], link, parts[1]]
        return self.show(" ".join(parts))

    def build(self) -> Dict:
        s = self.decide()
        e = self.entries
        dog = next((e[g] for g in ("DOG", "FISH", "BIRD", "HOUSE", "STONE") if g in e and e[g]["pos"] == "noun"), None)
        hand = next((e[g] for g in ("HAND", "ARM OR HAND", "EYE", "HEAD") if g in e and e[g]["pos"] == "noun"), None)
        person = next((e[g] for g in ("WOMAN", "MALE PERSON", "PERSON", "CHILD (YOUNG HUMAN)")
                       if g in e and e[g]["pos"] == "noun"), None)
        examples: Dict = {"pronominal": [], "alienability": [], "nominal": None}
        if dog:
            plural = next((v for v in self.cats["number"].get("values", []) if v == "plural"), None) \
                if self.cats["number"].get("grammaticalized") else None
            for cell in self.pronouns:
                ex = {"cell": cell, "english": f"{cell_english(cell)} {short(dog)}",
                      **self.possess(dog, cell)}
                if plural:
                    pl = self.possess(dog, cell, plural)
                    ex["plural"] = {**pl, "english": f"{cell_english(cell)} {short(dog)}s"}
                examples["pronominal"].append(ex)
        if hand and dog and s["alienability"]["classes"] >= 2:
            cell = next(iter(self.pronouns))
            for noun in (hand, dog):
                examples["alienability"].append({"english": f"{cell_english(cell)} {short(noun)}",
                                                 **self.possess(noun, cell)})
        if person and dog:
            examples["nominal"] = {"english": f"the {short(person)}'s {short(dog)}", **self.nominal(person, dog)}
        return {"settings": s, "examples": examples,
                "metadata": {"seed": self.seed, "sources": self.sources, "notes": self.notes,
                             "lexemes": {"possessed": short(dog) if dog else None,
                                         "inalienable": short(hand) if hand else None,
                                         "possessor": short(person) if person else None}}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

STRATEGY_PT = {"affix": "afixos de posse no nome", "genitive": "pronome no caso genitivo",
               "linker": "pronome + partícula de posse (como o 的 do mandarim)",
               "suppletive": "palavras possessivas próprias (como 'my', 'your')"}
LOCUS_PT = {"head": "no possuído (o nome possuído recebe uma marca, como o 'wad-e' do Vulgarlang)",
            "dependent": "no possuidor (caso genitivo)", "double": "nos dois (genitivo + marca no possuído)",
            "none": "nenhuma marca (justaposição)", "linker": "partícula de ligação entre os dois nomes"}


def describe(data: Dict, sp) -> List[str]:
    s = data["settings"]
    pr, n, al = s["pronominal"], s["nominal"], s["alienability"]
    pos = {"prefix": "prefixos", "suffix": "sufixos", "before": "antes do nome", "after": "depois do nome"}
    lines = [f"Possessivos: {STRATEGY_PT[pr['strategy']]} ({pos[pr['position']]})"
             + (", reduzidos dos pronomes" if pr.get("from_pronouns") else "")]
    if pr.get("linker"):
        lines.append(f"Partícula de posse: {sp(''.join(pr['linker']))}")
    lines.append(f"Posse entre nomes: marca {LOCUS_PT[n['locus']]}")
    if n.get("affix"):
        lines.append(f"Marca do possuído: {'-' if n['position'] == 'suffix' else ''}{sp(''.join(n['affix']))}"
                     f"{'-' if n['position'] == 'prefix' else ''}" + (" (o mesmo afixo de 3ª pessoa)" if n.get("from_3sg") else ""))
    if al["classes"] == 1:
        lines.append("Sem distinção de alienabilidade: todo nome é possuído do mesmo jeito")
    else:
        lines.append("Posse inalienável (partes do corpo e parentes) marcada no próprio nome; nos demais, "
                     f"a marca vai no classificador de posse {sp(''.join(al['alienable_marker']))}"
                     + (f", e comida/bebida o classificador {sp(''.join(al['food_marker']))}" if al["classes"] == 3 else ""))
        if al.get("obligatory"):
            lines.append(f"Partes do corpo e parentes são sempre possuídos; sem possuidor, recebem "
                         f"{sp(''.join(al['unpossessed_affix']))} ('de alguém')")
    a = s["articles"]
    if a:
        lines.append("Artigos " + ("flexionam em número" if a["inflect_for_number"] else "não flexionam em número"))
    return lines


def write_markdown(path: Path, data: Dict, sp) -> None:
    ex = data["examples"]
    lines = ["# Posse e determinantes", ""] + [f"- {l}" for l in describe(data, sp)]
    if ex["pronominal"]:
        has_pl = any("plural" in x for x in ex["pronominal"])
        head = ["Pessoa", "Possessivo", "Pronúncia"] + (["Plural"] if has_pl else [])
        lines += ["", "## Possessivos", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for x in ex["pronominal"]:
            row = [f"{gloss('.'.join(x['cell'].split('.')[:2]))} ('{x['english']}')", f"**{x['written']}**",
                   f"/{x['pronunciation']}/"] + ([f"**{x['plural']['written']}**"] if has_pl else [])
            lines.append("| " + " | ".join(row) + " |")
    if ex["alienability"]:
        lines += ["", "## Alienabilidade", ""]
        lines += [f"- **{x['written']}** /{x['pronunciation']}/ — '{x['english']}' ({x['class']})"
                  for x in ex["alienability"]]
    if ex["nominal"]:
        x = ex["nominal"]
        lines += ["", "## Posse entre nomes", "", f"- **{x['written']}** /{x['pronunciation']}/ — '{x['english']}'"]
    a = data["settings"]["articles"]
    if a:
        lines += ["", "## Artigos", ""]
        nums = sorted({n for f in a["forms"].values() for n in f}, key=lambda n: (n != "singular", n))
        lines += ["| Artigo | " + " | ".join(nums) + " |", "|" + "---|" * (len(nums) + 1)]
        for value, forms in a["forms"].items():
            lines.append(f"| {value} | " + " | ".join(f"**{sp(''.join(forms[n]))}**" if n in forms else "—"
                                                    for n in nums) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera possessivos, posse nominal e artigos com número.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    args = ap.parse_args()

    wals = None if args.no_wals or not args.wals.exists() else args.wals
    b = PossessionBuilder(args.language, args.seed, wals)
    data = json.loads(json.dumps(b.build()))
    sp = (lambda x: b.ortho.spell(x)) if b.ortho else (lambda x: x)
    (args.language / "possession.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "possession.md", data, sp)

    print("\nPOSSE E DETERMINANTES")
    for l in describe(data, sp):
        print(f"  {l}")
    for x in data["examples"]["pronominal"][:6]:
        print(f"    {x['written']:<24} /{x['pronunciation']}/  '{x['english']}'")
    for x in data["examples"]["alienability"]:
        print(f"    {x['written']:<24} /{x['pronunciation']}/  '{x['english']}' ({x['class']})")
    if data["examples"]["nominal"]:
        x = data["examples"]["nominal"]
        print(f"    {x['written']:<24} /{x['pronunciation']}/  '{x['english']}'")
    for n in data["metadata"]["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Posse salva em '{args.language / 'possession.json'}' e 'possession.md'.")


if __name__ == "__main__":
    main()
