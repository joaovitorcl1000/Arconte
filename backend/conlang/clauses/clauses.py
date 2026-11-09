"""
Módulo — Orações.

Completa a gramática da frase com o que uma língua precisa além da oração simples:

    voz e valência      passiva ('o peixe foi comido pelo cão'), antipassiva (em
                        línguas ergativas), reflexivo ('lavou-se'), recíproco ('olharam-se')
    demonstrativos      sistema de distância: 'este / aquele', ou 'este / esse / aquele',
                        com os advérbios 'aqui / aí / lá'
    imperativo          'venha!' e proibitivo 'não coma!'
    orações complexas   coordenação ('e', 'ou', 'mas'), completivas ('sei que...'),
                        condicionais ('se...'), causais ('porque...')
    possessivos         independentes: 'o cão é meu'
    adposições          relações espaciais: 'debaixo de', 'atrás de', 'dentro de'...

Decisões sorteadas com o WALS (41A, 70A, 71A, 106A, 107A, 108A) e coerentes com a
ordem das palavras (em línguas OV, subordinadas vêm antes e o subordinador no fim).

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico, da sintaxe, da ortografia e do acento.

Uso:
    python clauses/clauses.py --language languages/lang-31

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
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "syntax", "orthography", "stress"):
    sys.path.insert(0, str(ROOT / folder))
from morphological_engine import MorphologicalEngine, gloss as mgloss  # noqa: E402
import syntax as syn_mod  # noqa: E402

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

EMBEDDED = {
    "41A": {"1": 7, "2": 126, "3": 88, "4": 9, "5": 4},          # contrastes de distância nos demonstrativos
    "70A": {"1": 292, "2": 43, "3": 2, "4": 89, "5": 122},       # imperativo morfológico
    "71A": {"1": 113, "2": 182, "3": 55, "4": 146},              # proibitivo
    "106A": {"1": 16, "2": 99, "3": 16, "4": 44},                # recíprocos
    "107A": {"1": 162, "2": 211},                                # passiva
    "108A": {"1": 18, "2": 30, "3": 146},                        # antipassiva
}
DISTANCES = {"1": ["neutral"], "2": ["proximal", "distal"], "3": ["proximal", "medial", "distal"],
             "4": ["proximal", "medial", "distal", "remote"], "5": ["proximal", "medial", "distal", "remote"]}
DIST_EN = {"neutral": ("this/that", "here/there"), "proximal": ("this", "here"), "medial": ("that (near you)", "there (near you)"),
           "distal": ("that", "there"), "remote": ("that (far away)", "over there (far away)")}
DIST_PT = {"neutral": "neutro", "proximal": "perto de quem fala", "medial": "perto de quem ouve",
           "distal": "longe", "remote": "muito longe"}

SPATIAL = [("BELOW OR UNDER", "under"), ("ABOVE", "above"), ("INSIDE", "inside"), ("BEHIND", "behind"),
           ("IN FRONT OF", "in front of"), ("NEAR", "near")]
CONNECTIVES = [("OR", "or"), ("BUT", "but"), ("IF", "if"), ("BECAUSE", "because"), ("WHEN", "when")]


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def W(form: str, gloss: str, seg: Optional[str] = None) -> Dict:
    return {"form": form, "seg": seg if seg is not None else form, "gloss": gloss}


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class ClauseBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None, wals_dir: Optional[Path] = None):
        d = language_dir
        self.dir = d
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
        self.typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "clauses") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.wals_dir = wals_dir
        self.sources: Dict[str, str] = {}
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, self.typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        # a sintaxe da língua, com as decisões já tomadas (ordem, casos, concordância)
        self.sb = syn_mod.SyntaxBuilder(self.eng, self.lex, self.typology, syn_mod.Wals(None), self.seed)
        self.sb.s = self.syntax["settings"]
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.vocab = {e["gloss"]: e for e in (_load(d / "vocabulary.json") or {}).get("entries", [])}
        self.possession = _load(d / "possession.json")
        self.typ = self.catdata["metadata"]["typology"]
        self.isolating = self.typ["synthesis"] == "isolating"
        self.prefixing = self.typ["affix_position"] in ("weakly_prefixing", "strongly_prefixing")
        self.ov = self.syntax["settings"]["word_order"]["object_before_verb"]
        self.prepositions = self.syntax["settings"]["adpositions"] == "prepositions"
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.used = self._used_forms(d)

    def _used_forms(self, d: Path) -> set:
        used = {tuple(self.segments(e["citation"])) for e in self.lex["entries"] if e.get("citation")}
        used |= {tuple(self.segments(e["citation"])) for e in self.vocab.values()}
        for domain in ("noun", "verb"):
            for slot in self.morph["affixes"][domain]:
                for forms in slot["forms"].values():
                    used |= {tuple(x for x in f if x != "+") for f in forms.values() if f}
        for fm in self.morph["free_markers"].values():
            used |= {tuple(w) for w in fm["forms"].values()}
        for v in self.syntax.get("function_words", {}).values():
            used.add(tuple(v))
        def walk(x):  # listas de fonemas guardadas pelos outros módulos (afixos, partículas)
            if isinstance(x, list) and x and all(isinstance(v, str) for v in x):
                used.add(tuple(v for v in x if v != " "))
            elif isinstance(x, dict):
                for v in x.values():
                    walk(v)
        for name in ("possession", "comparison", "derivation", "numerals"):
            data = _load(d / f"{name}.json")
            if data:
                walk(data.get("settings", {}))
                walk(data.get("rules", {}))
        return used

    # ── utilidades ───────────────────────────────────────────────────────
    def segments(self, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ "), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def wals(self, fid: str) -> Dict[str, int]:
        values = self.wals_dir / "values.csv" if self.wals_dir else None
        if values and values.exists():
            with open(values, encoding="utf-8", newline="") as f:
                c = Counter(r["Value"] for r in csv.DictReader(f) if r["Parameter_ID"] == fid)
            if c:
                self.sources[fid] = f"WALS {fid} (n={sum(c.values())})"
                return dict(c)
        self.sources[fid] = f"WALS {fid} (embutido)"
        return EMBEDDED[fid]

    def pick(self, fid: str) -> str:
        counts = self.wals(fid)
        keys = sorted(counts)
        return self.rng.choices(keys, [counts[k] for k in keys])[0]

    def new_word(self, syllables: int = 1) -> List[str]:
        for _ in range(60):
            w = [x for syl in self.ph.generate_syllables(syllables) for x in syl]
            if tuple(w) not in self.used:
                self.used.add(tuple(w))
                return w
        return w

    def new_affix(self, kind: str) -> List[str]:
        for _ in range(60):
            a = self.ph.generate_affix(kind)["segments"]
            if tuple(a) not in self.used:
                self.used.add(tuple(a))
                return a
        return a

    def word_for(self, gloss: str, syllables: int = 1) -> Tuple[List[str], str]:
        """Palavra do léxico ou do vocabulário ampliado; senão, uma nova."""
        e = self.entries.get(gloss) or self.vocab.get(gloss)
        if e and e.get("citation"):
            return self.segments(e["citation"]), "lexicon" if gloss in self.entries else "vocabulary"
        return self.new_word(syllables), "new"

    def attach(self, base: List[str], affix: List[str], kind: str) -> str:
        if kind == "prefix":
            morphs = [{"segs": list(affix), "role": "prefix", "label": "", "sep": "-"},
                      {"segs": list(base), "role": "root", "label": "", "sep": "-"}]
        else:
            morphs = [{"segs": list(base), "role": "root", "label": "", "sep": "-"},
                      {"segs": list(affix), "role": "suffix", "label": "", "sep": "-"}]
        morphs, _, _ = self.eng.resolve(morphs)
        return "".join(s for m in morphs for s in m["segs"])

    def affix_word(self, w: Dict, affix: List[str], kind: str, gloss: str) -> Dict:
        """Acrescenta um afixo a uma palavra já flexionada (com o sândi da língua)."""
        form = self.attach(self.segments(w["form"]), affix, kind)
        a = "".join(affix)
        seg = f"{a}-{w['seg']}" if kind == "prefix" else f"{w['seg']}-{a}"
        gl = f"{gloss}-{w['gloss']}" if kind == "prefix" else f"{w['gloss']}-{gloss}"
        return W(form, gl, seg)

    def show(self, words: List[Dict]) -> Dict:
        ipa = " ".join(w["form"] for w in words)
        written = " ".join(self.ortho.spell(w["form"]) if self.ortho else w["form"] for w in words)
        return {"written": written[:1].upper() + written[1:], "ipa": ipa}

    def lexeme(self, glosses: List[str], pos: str, cond=lambda e: True) -> Optional[Dict]:
        return next((self.entries[g] for g in glosses if g in self.entries
                     and self.entries[g]["pos"] == pos and self.entries[g].get("root") and cond(self.entries[g])), None)

    # ── decisões ─────────────────────────────────────────────────────────
    def decide(self) -> Dict:
        r = self.rng
        s: Dict = {}
        affix_pos = "prefix" if self.prefixing else "suffix"
        verb_side = "before" if not self.ov else "after"  # partículas verbais: do lado do complemento

        # 1. Passiva (107A) e antipassiva (108A)
        if self.pick("107A") == "1":
            if self.isolating or r.random() < 0.3:
                pas = {"present": True, "type": "particle", "form": self.new_word(), "position": verb_side}
            else:
                pas = {"present": True, "type": "affix", "form": self.new_affix(affix_pos), "position": affix_pos}
            case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
            agent_case = next((c for c in ("instrumental", "ablative", "ergative") if c in case_vals), None)
            if r.random() < 0.6:
                pas["agent"] = ({"type": "case", "case": agent_case} if agent_case
                                else {"type": "adposition", "form": self.new_word()})
            else:
                pas["agent"] = {"type": "none"}
            s["passive"] = pas
        else:
            s["passive"] = {"present": False}
        alignment = self.cats["case"].get("alignment", "")
        if "ergative" in alignment and self.pick("108A") != "3" and not self.isolating:
            s["antipassive"] = {"present": True, "form": self.new_affix(affix_pos), "position": affix_pos}
        else:
            s["antipassive"] = {"present": False}

        # 2. Reflexivo e recíproco (106A)
        if not self.isolating and r.random() < 0.4:
            refl = {"type": "affix", "form": self.new_affix(affix_pos), "position": affix_pos}
        else:
            refl = {"type": "pronoun", "form": self.new_word(r.choice([1, 2]))}
        s["reflexive"] = refl
        rc = self.pick("106A")
        if rc == "4":
            s["reciprocal"] = {"type": "same_as_reflexive"}
        elif rc == "1":
            s["reciprocal"] = {"type": "none"}
        else:
            s["reciprocal"] = ({"type": "affix", "form": self.new_affix(affix_pos), "position": affix_pos}
                               if refl["type"] == "affix" or (not self.isolating and r.random() < 0.3)
                               else {"type": "pronoun", "form": self.new_word(2)})

        # 3. Demonstrativos (41A)
        terms = DISTANCES[self.pick("41A")]
        dems, advs = {}, {}
        lex_dem = {"proximal": "THIS", "distal": "THAT", "neutral": "THIS"}
        lex_adv = {"proximal": "HERE", "distal": "THERE", "neutral": "HERE"}
        for t in terms:
            dems[t], src_d = self.word_for(lex_dem.get(t, "__none__"))
            advs[t], src_a = self.word_for(lex_adv.get(t, "__none__"))
        s["demonstratives"] = {"terms": terms, "forms": dems, "adverbs": advs}

        # 4. Imperativo (70A) e proibitivo (71A)
        imp = self.pick("70A")
        if imp == "5" or self.isolating:
            s["imperative"] = {"type": "none"}  # usa-se a 2ª pessoa do indicativo
        else:
            s["imperative"] = ({"type": "bare"} if r.random() < 0.5 else
                               {"type": "affix", "form": self.new_affix(affix_pos), "position": affix_pos})
            s["imperative"]["number"] = {"1": "both", "2": "singular", "3": "plural", "4": "neutral"}[imp]
        pro = self.pick("71A")
        s["prohibitive"] = ({"type": "special", "form": self.new_word()} if pro in ("2", "4")
                            else {"type": "normal"})

        # 5. Conectivos e subordinação
        conn = {}
        for gloss, en in CONNECTIVES:
            conn[en] = self.word_for(gloss)[0]
        conn["and"] = self.word_for("AND")[0]
        comp = None if r.random() < 0.3 else self.new_word()  # 'que' (às vezes zero, como no inglês)
        s["connectives"] = conn
        s["complementizer"] = comp
        # em línguas OV, o subordinador fica no fim da subordinada, que vem antes da principal
        s["subordinator_position"] = "final" if self.ov else "initial"

        # 6. Possessivos independentes ('meu', 'é meu')
        s["independent_possessive"] = self.independent_possessive_rule()

        # 7. Adposições espaciais
        case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
        gov = next((c for c in ("locative", "genitive") if c in case_vals), None)
        s["adpositions"] = {"position": "before" if self.prepositions else "after", "governed_case": gov,
                            "forms": {en: self.word_for(g)[0] for g, en in SPATIAL}}
        self.settings = s
        return s

    def independent_possessive_rule(self) -> Dict:
        p = self.possession["settings"]["pronominal"] if self.possession else None
        if p and p["strategy"] == "affix":
            # como nas línguas oceânicas: uma base 'coisa-de' que recebe o afixo possessivo
            return {"type": "base_affix", "base": self.new_word(), "position": p["position"]}
        if p:
            return {"type": "same_as_determiner"}
        case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
        if "genitive" in case_vals:
            return {"type": "genitive_pronoun"}
        return {"type": "particle", "form": self.new_word()}

    # ── peças ────────────────────────────────────────────────────────────
    def np(self, e: Dict, role: str, verb=None, number="singular") -> List[Dict]:
        return self.sb.noun_phrase(e, role, verb, number=number)

    def verb(self, e: Dict, transitive: bool, subj="3.singular", obj="3.singular", extra=None) -> List[Dict]:
        feats = {**self.sb.verb_agreement(transitive, self.sb.agreement_value(*subj.split(".")),
                                          self.sb.agreement_value(*obj.split(".")) if obj else None),
                 **(extra or {})}
        return self.sb.verb_words(e, feats)

    def main_verb_index(self, words: List[Dict], verb_gloss: str) -> int:
        return next((i for i, w in enumerate(words) if verb_gloss in w["gloss"]), len(words) - 1)

    def clause(self, S, V, O=None, R=None, loc=None) -> List[Dict]:
        seq = self.sb.clause({"S": S, "V": V, "O": O, "R": R}, loc)
        return [w for c in seq if c for w in c]

    def possessive_word(self, cell: str) -> Optional[Dict]:
        rule = self.settings["independent_possessive"]
        p = self.sb.pronoun(cell)
        if not p:
            return None
        gl = f"{mgloss('.'.join(cell.split('.')[:2]))}.POSS"
        if rule["type"] == "base_affix":
            aff = self.possession["settings"]["pronominal"]["forms"].get(p["gloss"])
            if aff is None:
                return None
            form = self.attach(rule["base"], aff, rule["position"])
            return W(form, gl, f"{''.join(rule['base'])}-{''.join(aff)}" if rule["position"] == "suffix"
                     else f"{''.join(aff)}-{''.join(rule['base'])}")
        if rule["type"] == "same_as_determiner":
            f = self.possession["settings"]["pronominal"]["forms"].get(p["gloss"])
            return W("".join(f).strip(), gl) if f else None
        if rule["type"] == "genitive_pronoun":
            r = self.eng.inflect({"root": p["root"], "form": p["form"], "tones": [], "class": 0, "gender": None},
                                 "noun", {"case": "genitive"})
            return W(r["surface"], gl, r["underlying"])
        return W(p["form"] + " " + "".join(rule["form"]), gl)

    # ── frases ───────────────────────────────────────────────────────────
    def sentences(self) -> List[Dict]:
        s = self.settings
        out: List[Dict] = []
        L = self.lexeme
        dog = L(["DOG"], "noun")
        fish = L(["FISH", "BIRD"], "noun")
        woman = L(["WOMAN", "PERSON"], "noun")
        child = L(["CHILD (YOUNG HUMAN)", "CHILD (DESCENDANT)"], "noun")
        tree = L(["TREE", "HOUSE", "STONE"], "noun")
        eat = L(["EAT", "BITE"], "verb", lambda e: e.get("transitivity") != "stative")
        see = L(["SEE", "HEAR"], "verb", lambda e: e.get("transitivity") != "stative")
        wash = L(["WASH", "SEE"], "verb", lambda e: e.get("transitivity") != "stative")
        sleep = L(["SLEEP", "SIT", "LIE (REST)"], "verb")
        come = L(["COME", "GO", "WALK"], "verb")
        know = L(["KNOW", "THINK", "SEE"], "verb")
        if not all((dog, fish, woman, child, eat, see, sleep)):
            self.notes.append("o léxico não tem as palavras básicas para todas as frases de exemplo")

        def add(key, title, words, translation, literal=None):
            if words:
                out.append({"key": key, "title": title, "words": words, "translation": translation,
                            "literal": literal, **self.show(words)})

        # 1. Passiva
        if s["passive"]["present"] and fish and eat:
            pas = s["passive"]
            V = self.verb(eat, False)
            if pas["type"] == "affix":
                i = self.main_verb_index(V, syn_mod.lex_gloss(eat))
                V[i] = self.affix_word(V[i], pas["form"], pas["position"], "PASS")
            else:
                part = W("".join(pas["form"]), "PASS")
                V = V + [part] if pas["position"] == "after" else [part] + V
            S = self.np(fish, "S", eat)
            loc = None
            agent = pas["agent"]
            if agent["type"] != "none" and dog:
                if agent["type"] == "case":
                    loc = self.sb.noun_word(dog, {"case": agent["case"]})
                else:
                    a = W("".join(agent["form"]), "by")
                    n = self.np(dog, "S")
                    loc = [a] + n if self.prepositions else n + [a]
            add("passive", "Passiva", self.clause(S, V, loc=loc),
                f"The {syn_mod.en_base(fish)} is eaten" + (f" by the {syn_mod.en_base(dog)}." if loc else "."))
        if s["antipassive"]["present"] and woman and eat:
            ap = s["antipassive"]
            V = self.verb(eat, False)
            i = self.main_verb_index(V, syn_mod.lex_gloss(eat))
            V[i] = self.affix_word(V[i], ap["form"], ap["position"], "ANTIP")
            add("antipassive", "Antipassiva", self.clause(self.np(woman, "S", eat), V),
                f"The {syn_mod.en_base(woman)} eats (something).",
                "o objeto sai da oração, e o agente passa ao caso do sujeito intransitivo")
        # 2. Reflexivo e recíproco
        refl = s["reflexive"]
        if woman and wash:
            if refl["type"] == "affix":
                V = self.verb(wash, False)
                i = self.main_verb_index(V, syn_mod.lex_gloss(wash))
                V[i] = self.affix_word(V[i], refl["form"], refl["position"], "REFL")
                words = self.clause(self.np(woman, "S", wash), V)
            else:
                pro = {"root": refl["form"], "form": "".join(refl["form"]), "tones": [], "pos": "noun",
                       "gloss": "SELF", "english": "self", "class": 0}
                O = self.sb.noun_word(pro, {"case": self.sb.case_for("P")} if self.sb.case_for("P") else {})
                O = [{**w, "gloss": w["gloss"].replace("self", "REFL")} for w in O]
                words = self.clause(self.np(woman, "A"), self.verb(wash, True), O=O)
            add("reflexive", "Reflexivo", words,
                f"The {syn_mod.en_base(woman)} {syn_mod.en_3sg(syn_mod.en_base(wash))} herself.")
        rec = s["reciprocal"]
        if dog and see and rec["type"] != "none":
            pl = "plural" if self.cats["number"].get("grammaticalized") else "singular"
            form = refl if rec["type"] == "same_as_reflexive" else rec
            if form["type"] == "affix":
                V = self.verb(see, False, subj=f"3.{pl}")
                i = self.main_verb_index(V, syn_mod.lex_gloss(see))
                V[i] = self.affix_word(V[i], form["form"], form["position"], "RECP")
                words = self.clause(self.np(dog, "S", see, number=pl), V)
            else:
                O = [W("".join(form["form"]), "RECP")]
                words = self.clause(self.np(dog, "A", number=pl), self.verb(see, True, subj=f"3.{pl}"), O=O)
            add("reciprocal", "Recíproco", words,
                f"The {syn_mod.en_plural(syn_mod.en_base(dog))} see each other.")
        # 3. Demonstrativos
        dm = s["demonstratives"]
        if dog:
            for t in dm["terms"][:3]:
                dem = {"citation": "".join(dm["forms"][t]), "form": "".join(dm["forms"][t]),
                       "english": DIST_EN[t][0].split(" (")[0], "gloss": "DEM", "label": DIST_EN[t][0]}
                words = self.sb.noun_phrase(dog, "S", dem=dem)
                words = [{**w, "gloss": f"DEM.{t[:4].upper()}"} if w["form"] == dem["form"] else w for w in words]
                base, _, paren = DIST_EN[t][0].partition(" (")
                add(f"demonstrative_{t}", f"Demonstrativo ({DIST_PT[t]})", words,
                    f"{base} {syn_mod.en_base(dog)}" + (f" ({paren}" if paren else ""))
        # 4. Imperativo e proibitivo
        imp = s["imperative"]
        if come:
            if imp["type"] == "none":
                V = self.verb(come, False, subj="2.singular")
                note = "sem imperativo próprio: usa-se a 2ª pessoa"
            else:
                stem = come["citation"] if (self.eng.skeleton or not come.get("root")) else "".join(come["root"])
                base = W(stem, f"{syn_mod.lex_gloss(come)}.IMP")
                V = [self.affix_word({**base, "gloss": syn_mod.lex_gloss(come)}, imp["form"], imp["position"], "IMP")
                     if imp["type"] == "affix" else base]
                note = None
            add("imperative", "Imperativo", V, "Come!", note)
        if eat and fish:
            O = self.np(fish, "P")
            pro = s["prohibitive"]
            if pro["type"] == "special":
                if imp["type"] in ("bare", "affix"):
                    stem = eat["citation"] if self.eng.skeleton else "".join(eat["root"])
                    V = [W(stem, f"{syn_mod.lex_gloss(eat)}.IMP")]
                    if imp["type"] == "affix":
                        V = [self.affix_word({**V[0], "gloss": syn_mod.lex_gloss(eat)}, imp["form"], imp["position"], "IMP")]
                else:
                    V = self.verb(eat, True, subj="2.singular")
                neg = W("".join(pro["form"]), "PROH")
                V = [neg] + V
            else:
                extra = {"negation": "negative"} if self.cats.get("negation", {}).get("grammaticalized") else {}
                V = self.verb(eat, True, subj="2.singular", extra=extra)
            add("prohibitive", "Proibitivo", self.clause(None, V, O=O),
                f"Don't eat the {syn_mod.en_base(fish)}!")
        # 5. Orações complexas
        conn = s["connectives"]
        final = s["subordinator_position"] == "final"
        c1 = self.clause(self.np(dog, "S", sleep), self.verb(sleep, False)) if dog and sleep else None
        c2 = (self.clause(self.np(child, "A"), self.verb(eat, True), O=self.np(fish, "P"))
              if child and eat and fish else None)
        if c1 and c2:
            add("coordination_and", "Coordenação ('e')", c1 + [W("".join(conn["and"]), "and")] + c2,
                f"The dog sleeps and the {syn_mod.en_base(child)} eats the {syn_mod.en_base(fish)}.")
            add("coordination_but", "Coordenação ('mas')", c1 + [W("".join(conn["but"]), "but")] + c2,
                f"The dog sleeps, but the {syn_mod.en_base(child)} eats the {syn_mod.en_base(fish)}.")
            cond = W("".join(conn["if"]), "if")
            sub = (c1 + [cond]) if final else ([cond] + c1)
            add("conditional", "Condicional ('se')", sub + c2,
                f"If the dog sleeps, the {syn_mod.en_base(child)} eats the {syn_mod.en_base(fish)}.")
            because = W("".join(conn["because"]), "because")
            sub = (c1 + [because]) if final else ([because] + c1)
            words = (sub + c2) if final else (c2 + sub)
            add("causal", "Causal ('porque')", words,
                f"The {syn_mod.en_base(child)} eats the {syn_mod.en_base(fish)} because the dog sleeps.")
        i = self.sb.pronoun("1.singular")
        if c1 and know and i:
            comp = s["complementizer"]
            sub = list(c1)
            if comp:
                cw = W("".join(comp), "COMP")
                sub = sub + [cw] if final else [cw] + sub
            S = self.sb.subject(self.np(i, "A"), True)
            V = self.verb(know, True, subj="1.singular")
            add("complement", "Completiva ('que')", self.clause(S, V, O=sub),
                f"I {syn_mod.en_base(know)} that the dog sleeps.",
                None if comp else "sem complementizador, como em 'I know the dog sleeps'")
        # 6. Possessivo independente
        mine = self.possessive_word("1.singular")
        if dog and mine:
            S = self.np(dog, "S")
            cop = self.syntax.get("function_words", {}).get("copula_form")
            pred = [mine]
            if self.syntax["settings"].get("copula") == "word" and cop:
                c = W("".join(cop), "COP")
                pred = pred + [c] if self.ov else [c] + pred
            add("independent_possessive", "Possessivo independente", S + pred, "The dog is mine.")
        # 7. Adposição espacial
        adp = s["adpositions"]
        if dog and sleep and tree:
            a = W("".join(adp["forms"]["under"]), "under")
            feats = {"case": adp["governed_case"]} if adp["governed_case"] else {}
            n = self.sb.noun_word(tree, feats)
            loc = [a] + n if adp["position"] == "before" else n + [a]
            add("adposition", "Adposição espacial", self.clause(self.np(dog, "S", sleep), self.verb(sleep, False), loc=loc),
                f"The dog sleeps under the {syn_mod.en_base(tree)}.")
        return out

    def build(self) -> Dict:
        s = self.decide()
        sentences = self.sentences()
        sp = (lambda x: self.ortho.spell(x)) if self.ortho else (lambda x: x)
        tables = {
            "demonstratives": [{"term": t, "demonstrative": sp("".join(s["demonstratives"]["forms"][t])),
                                "adverb": sp("".join(s["demonstratives"]["adverbs"][t])),
                                "english": DIST_EN[t]} for t in s["demonstratives"]["terms"]],
            "connectives": {k: sp("".join(v)) for k, v in s["connectives"].items()},
            "adpositions": {k: sp("".join(v)) for k, v in s["adpositions"]["forms"].items()},
            "independent_possessives": [],
        }
        for cell in self.lex["pronouns"]["cells"]:
            w = self.possessive_word(cell)
            if w:
                tables["independent_possessives"].append({"cell": cell, "written": sp(w["form"]), "ipa": w["form"]})
        return {"settings": s, "tables": tables, "sentences": sentences,
                "metadata": {"seed": self.seed, "sources": self.sources, "notes": self.notes}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def describe(data: Dict, sp) -> List[str]:
    s = data["settings"]
    pos = {"prefix": "prefixo", "suffix": "sufixo", "before": "antes do verbo", "after": "depois do verbo"}
    lines = []
    p = s["passive"]
    if p["present"]:
        f = sp("".join(p["form"]))
        how = f"{pos[p['position']]} {'-' + f if p['position'] == 'suffix' else f + '-' if p['position'] == 'prefix' else f}"
        ag = p["agent"]
        agent = ("agente omitido" if ag["type"] == "none" else f"agente no caso {ag['case']}" if ag["type"] == "case"
                 else f"agente com a adposição {sp(''.join(ag['form']))}")
        lines.append(f"Passiva: {how}; {agent}")
    else:
        lines.append("Sem passiva (como em muitas línguas: usa-se uma oração ativa com sujeito genérico)")
    if s["antipassive"]["present"]:
        lines.append(f"Antipassiva: afixo {sp(''.join(s['antipassive']['form']))}")
    r = s["reflexive"]
    lines.append("Reflexivo: " + (f"afixo {sp(''.join(r['form']))}" if r["type"] == "affix"
                                   else f"pronome {sp(''.join(r['form']))} ('si mesmo')"))
    rc = s["reciprocal"]
    lines.append("Recíproco: " + {"same_as_reflexive": "igual ao reflexivo (como o 'se' do português)",
                                   "none": "sem construção própria"}.get(rc["type"], f"{'afixo' if rc['type'] == 'affix' else 'pronome'} {sp(''.join(rc.get('form', [])))}"))
    n = len(s["demonstratives"]["terms"])
    lines.append("Demonstrativos: " + ("sem contraste de distância" if n == 1 else f"{n} graus de distância"))
    imp = s["imperative"]
    lines.append("Imperativo: " + {"none": "sem forma própria (2ª pessoa do indicativo)", "bare": "radical puro ('vem!')"}.get(
        imp["type"], f"afixo {sp(''.join(imp.get('form', [])))}"))
    pr = s["prohibitive"]
    lines.append("Proibitivo: " + (f"partícula própria {sp(''.join(pr['form']))}" if pr["type"] == "special"
                                    else "negação comum"))
    comp = s["complementizer"]
    lines.append(f"Subordinação: subordinador no {'fim' if s['subordinator_position'] == 'final' else 'início'} "
                 "da subordinada; " + (f"complementizador {sp(''.join(comp))} ('que')" if comp else "sem complementizador"))
    return lines


def interlinear(sent: Dict) -> List[str]:
    return syn_mod.interlinear(sent) + ([f"({sent['literal']})"] if sent.get("literal") else [])


def write_markdown(path: Path, data: Dict, sp) -> None:
    t = data["tables"]
    lines = ["# Orações", ""] + [f"- {l}" for l in describe(data, sp)]
    lines += ["", "## Demonstrativos", "", "| Distância | Demonstrativo | Advérbio |", "|---|---|---|"]
    for d in t["demonstratives"]:
        lines.append(f"| {DIST_PT[d['term']]} | **{d['demonstrative']}** '{d['english'][0]}' | "
                     f"**{d['adverb']}** '{d['english'][1]}' |")
    if t["independent_possessives"]:
        lines += ["", "## Possessivos independentes", "", "| Pessoa | Forma |", "|---|---|"]
        for p in t["independent_possessives"]:
            lines.append(f"| {mgloss('.'.join(p['cell'].split('.')[:2]))} | **{p['written']}** |")
    lines += ["", "## Conectivos e adposições", "",
              "| Palavra | Forma |", "|---|---|"]
    for k, v in list(t["connectives"].items()) + list(t["adpositions"].items()):
        lines.append(f"| '{k}' | **{v}** |")
    for sent in data["sentences"]:
        lines += ["", f"## {sent['title']}", "", f"**{sent['written']}.**", "", "```"] + interlinear(sent) + ["```"]
    for n in data["metadata"]["notes"]:
        lines += ["", f"Nota: {n}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera voz, demonstrativos, imperativo e orações complexas.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    args = ap.parse_args()

    wals = None if args.no_wals or not args.wals.exists() else args.wals
    b = ClauseBuilder(args.language, args.seed, wals)
    data = json.loads(json.dumps(b.build()))
    sp = (lambda x: b.ortho.spell(x)) if b.ortho else (lambda x: x)
    (args.language / "clauses.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "clauses.md", data, sp)

    print("\nORAÇÕES")
    for l in describe(data, sp):
        print(f"  {l}")
    for sent in data["sentences"]:
        print(f"\n  {sent['title']}")
        for l in interlinear(sent):
            print(f"    {l}")
    for n in data["metadata"]["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Orações salvas em '{args.language / 'clauses.json'}' e 'clauses.md'.")


if __name__ == "__main__":
    main()
