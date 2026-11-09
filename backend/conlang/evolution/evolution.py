"""
Módulo — Evolução linguística (etapa 1: mudanças fonéticas).

Simula a história de uma língua: escolhe leis fonéticas reais (lei de Grimm, de
Verner, metafonia, lenição românica, palatalização, tonogênese...) conforme um
perfil e um tempo, aplica-as em ordem cronológica à língua inteira — raízes,
afixos, pronomes e partículas — e gera uma LÍNGUA-FILHA completa numa pasta
nova, com inventário, fonotática, morfologia, léxico e sintaxe refeitos.

    python evolution/evolution.py --language languages/lang-31 --profile germanic --years 1500
    python evolution/evolution.py --language languages/lang-31 --profile romance --years 2000 --rebuild
    python evolution/evolution.py --language languages/lang-31 --laws grimm,verner,umlaut

Perfis: germanic, english, romance, celtic, slavic, indo_iranian, hellenic,
polynesian, sinitic, natural (leis comuns, sorteadas pela frequência).

O tempo é uma aproximação: de 3 a 5 mudanças fonéticas grandes por milênio. É uma
simulação plausível, não uma previsão.

Não altera nenhum outro módulo: lê os JSONs da língua-mãe e usa as funções
públicas dos módulos (PHOIBLE, fonotática, motor, léxico, sintaxe, entrada do
usuário). A língua-mãe não é modificada.

Requer apenas a biblioteca padrão (Python ≥ 3.9) e o phoible.csv do projeto.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
for folder in ("phonemic_inventory", "phonotactics", "morphological_engine", "lexicon", "syntax",
               "custom_input", "generate_language"):
    sys.path.insert(0, str(ROOT / folder))

import laws as L  # noqa: E402
import lexical as LX  # noqa: E402
import phonemic_inventory as inv_mod  # noqa: E402
import phonotactics as pht_mod  # noqa: E402
from morphological_engine import MorphologicalEngine  # noqa: E402
import lexicon as lex_mod  # noqa: E402
import syntax as syn_mod  # noqa: E402
import custom_input as ci  # noqa: E402

PHOIBLE = ROOT / "ipa_database" / "phoible.csv"
TONE_LETTERS = "˥˦˧˨˩"
VOWEL_LETTERS = set("aeiouyɛɔəɨʉɯɪʊæɑɒøœɐɤʌɵɘ")
CORE_CONCEPTS = ["FATHER", "MOTHER", "WATER", "FIRE", "DOG", "FISH", "BIRD", "TREE", "STONE", "SUN", "MOON",
                 "STAR", "NIGHT", "HAND", "FOOT", "HEAD", "EYE", "TOOTH", "HEART", "BLOOD", "NAME", "PERSON",
                 "WOMAN", "CHILD (YOUNG HUMAN)", "EAT", "DRINK", "SEE", "HEAR", "KNOW", "COME", "GIVE", "DIE",
                 "BIG", "SMALL", "GOOD", "NEW", "OLD", "TWO", "THREE"]


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def derive_seed(master: int, step: str) -> int:
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _save(path: Path, data: Dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Fonologia por traços (PHOIBLE)
# ═══════════════════════════════════════════════════════════════════════════

class Phonology:
    """Classifica qualquer som pelos traços do PHOIBLE e troca traços ('p' + contínuo → 'ɸ')."""

    def __init__(self):
        self.stats = inv_mod.load_stats(PHOIBLE)
        self.idx = {f: i for i, f in enumerate(self.stats.features)}
        self._cache: Dict[str, Dict[str, str]] = {}

    def feats(self, s: str) -> Dict[str, str]:
        key = nfd(s)
        if key not in self._cache:
            seg = self.stats.segments.get(key)
            if seg is None:  # som fora do PHOIBLE: usa o símbolo-base
                base = "".join(ch for ch in key if unicodedata.category(ch) not in ("Mn", "Lm"))
                seg = self.stats.segments.get(base[:2]) or self.stats.segments.get(base[:1])
            self._cache[key] = dict(zip(self.stats.features, seg.vector)) if seg else {}
        return self._cache[key]

    def f(self, s: str, name: str) -> str:
        return self.feats(s).get(name, "0")

    def known(self, s: str) -> bool:
        return nfd(s) in self.stats.segments

    def change(self, s: str, changes: Dict[str, str]) -> Optional[str]:
        seg = self.stats.segments.get(nfd(s))
        if seg is None:
            return None
        v = list(seg.vector)
        for k, val in changes.items():
            if k in self.idx:
                v[self.idx[k]] = val
        out = self.stats.by_vector.get(tuple(v))
        return nfd(out) if out and nfd(out) != nfd(s) else None

    # classes
    def vowel(self, s: str) -> bool:
        if self.f(s, "syllabic") == "+":
            return True
        base = "".join(ch for ch in nfd(s) if unicodedata.category(ch) not in ("Mn", "Lm"))
        return bool(base) and base[0] in VOWEL_LETTERS and self.f(s, "consonantal") != "+"

    def stop(self, s):
        return (not self.vowel(s) and self.f(s, "consonantal") == "+" and self.f(s, "sonorant") == "-"
                and self.f(s, "continuant") == "-" and self.f(s, "delayedRelease") != "+")

    def fricative(self, s):
        return not self.vowel(s) and self.f(s, "sonorant") == "-" and self.f(s, "continuant") == "+"

    def obstruent(self, s):
        return not self.vowel(s) and self.f(s, "sonorant") == "-"

    def voiced(self, s):
        return self.f(s, "periodicGlottalSource") == "+"

    def aspirated(self, s):
        return not self.vowel(s) and self.f(s, "spreadGlottis") == "+" and self.f(s, "sonorant") == "-"

    def nasal(self, s):
        return not self.vowel(s) and self.f(s, "nasal") == "+"

    def front(self, s):
        return self.f(s, "front") == "+"

    def front_vowel(self, s):
        return self.vowel(s) and self.front(s)

    def high_front(self, s):
        return self.f(s, "high") == "+" and self.front(s) and (self.vowel(s) or nfd(s) == "j")

    def long(self, s):
        return self.f(s, "long") == "+"

    def labial_cons(self, s):
        return not self.vowel(s) and self.f(s, "labial") == "+"

    def velar(self, s):
        return not self.vowel(s) and self.f(s, "dorsal") == "+" and self.f(s, "back") == "+" \
            and self.f(s, "high") == "+"

    def sonority(self, s):
        if self.vowel(s):
            return 6
        if self.f(s, "sonorant") == "+":
            return 5 if self.f(s, "approximant") == "+" else 4
        return 2 if self.f(s, "continuant") == "+" else 1


# ═══════════════════════════════════════════════════════════════════════════
# Palavra
# ═══════════════════════════════════════════════════════════════════════════

class Word:
    def __init__(self, segs: List[str], tones: Optional[List[str]], P: Phonology, ev: "Evolver",
                 left_edge: bool = True, right_edge: bool = True):
        self.segs, self.tones, self.P, self.ev = list(segs), tones, P, ev
        self.left_edge, self.right_edge = left_edge, right_edge

    def with_segs(self, segs: List[str]) -> "Word":
        w = Word(segs, self.tones, self.P, self.ev, self.left_edge, self.right_edge)
        if self.tones:
            n_old, n_new = len(self.nuclei()), len(w.nuclei())
            if n_new < n_old:
                w.tones = self.tones[:n_new]
            elif n_new > n_old:
                w.tones = self.tones + [self.tones[-1]] * (n_new - n_old)
        return w

    def with_tones(self, tones: List[str]) -> "Word":
        return Word(self.segs, tones, self.P, self.ev, self.left_edge, self.right_edge)

    def nuclei(self) -> List[int]:
        return [i for i, s in enumerate(self.segs) if self.P.vowel(s)]

    def syllable_of(self, i: int) -> Optional[int]:
        nuc = self.nuclei()
        if not nuc:
            return None
        for k, n in enumerate(nuc):
            nxt = nuc[k + 1] if k + 1 < len(nuc) else None
            # uma consoante entre vogais vai para a sílaba seguinte; as demais ficam na coda
            end = len(self.segs) - 1 if nxt is None else (nxt - 2 if nxt - n > 1 else nxt - 1)
            if i <= end:
                return k
        return len(nuc) - 1

    def is_coda(self, i: int) -> bool:
        if self.P.vowel(self.segs[i]):
            return False
        k = self.syllable_of(i)
        return k is not None and i > self.nuclei()[k]

    def between_vowels(self, i: int) -> bool:
        return 0 < i < len(self.segs) - 1 and self.P.vowel(self.segs[i - 1]) and self.P.vowel(self.segs[i + 1])

    def stress(self) -> int:
        """Sílaba tônica pela regra de acento da língua-mãe (penúltima, se não houver)."""
        nuc = self.nuclei()
        n = len(nuc)
        if n <= 1:
            return 0
        rule = self.ev.stress_rule
        heavy = [any(self.is_coda(j) for j in range(i + 1, len(self.segs)) if self.syllable_of(j) == k)
                 or self.P.long(self.segs[i]) for k, i in enumerate(nuc)]
        fixed = {"initial": 0, "second": 1, "third": min(2, n - 1), "antepenultimate": max(0, n - 3),
                 "penultimate": n - 2, "ultimate": n - 1}
        if rule in fixed:
            return fixed[rule]
        if rule == "right_oriented":
            return n - 2 if (n == 2 or heavy[-2]) else n - 3
        if rule == "right_edge":
            return n - 1 if heavy[-1] else n - 2
        if rule == "left_edge":
            return 1 if (not heavy[0] and heavy[1]) else 0
        if rule == "unbounded_left":
            return next((k for k in range(n) if heavy[k]), 0)
        if rule in ("unbounded_right", "combined"):
            return next((k for k in reversed(range(n)) if heavy[k]), n - 1 if rule == "unbounded_right" else n - 2)
        return n - 2

    def variant(self, key: str, options: Sequence) -> object:
        return self.ev.variant(key, options)


# ═══════════════════════════════════════════════════════════════════════════
# Evolução
# ═══════════════════════════════════════════════════════════════════════════

class Evolver:
    def __init__(self, language_dir: Path, profile: str = "natural", years: int = 1000,
                 seed: Optional[int] = None, laws: Optional[List[str]] = None,
                 lexical: bool = True, donor: Optional[Path] = None, borrowing: Optional[str] = None):
        d = language_dir
        self.dir = d
        self.files = {k: _load(d / f"{k}.json") for k in (
            "morphological_typology", "phonemic_inventory", "phonotactics", "grammatical_categories",
            "morphology", "lexicon", "syntax", "manifest", "stress")}
        need = ("phonemic_inventory", "phonotactics", "grammatical_categories", "morphology", "lexicon", "syntax")
        if not all(self.files[k] for k in need):
            raise SystemExit(f"A pasta {d} precisa ter a língua completa (gere-a com o orquestrador).")
        if profile not in L.PROFILES:
            raise SystemExit(f"Perfil desconhecido: {profile}. Opções: {', '.join(L.PROFILES)}")
        self.profile, self.years = profile, years
        master = (self.files["manifest"] or {}).get("seed", 0)
        self.master = master
        self.seed = seed if seed is not None else derive_seed(master, f"evolution:{profile}:{years}")
        self.rng = random.Random(self.seed)
        self.P = Phonology()
        self.stress_rule = (self.files["stress"] or {}).get("rule", "penultimate")
        self._variants: Dict[str, object] = {}
        self.requested = laws
        self.lexical = lexical
        self.rng_lex = random.Random(derive_seed(self.seed, "lexical"))
        self.used_roots = {tuple(e["root"]) for e in self.files["lexicon"]["entries"] if e.get("root")}
        self.donor_dir = donor
        self.donor = None
        if donor:
            dl, di = _load(donor / "lexicon.json"), _load(donor / "phonemic_inventory.json")
            if not (dl and di):
                raise SystemExit(f"A língua doadora {donor} precisa ter léxico e inventário.")
            self.donor = {"lexicon": dl, "symbols": sorted({nfd(x["ipa"]) for x in di["consonants"] + di["vowels"]},
                                                           key=len, reverse=True)}
        self.borrowing = borrowing or ("medium" if donor else "none")
        self.symbols = sorted({nfd(x["ipa"]) for x in self.files["phonemic_inventory"]["consonants"]
                               + self.files["phonemic_inventory"]["vowels"]}, key=len, reverse=True)

    def variant(self, key: str, options: Sequence) -> object:
        if key not in self._variants:
            self._variants[key] = self.rng.choice(list(options))
        return self._variants[key]

    def segments(self, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ -"), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def segments_any(self, form: str) -> List[str]:
        """Segmenta uma forma da língua doadora (com o inventário dela)."""
        symbols = self.donor["symbols"] if self.donor else self.symbols
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ -"), 0
            while i < len(s):
                hit = next((x for x in symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def tones_of(self, form: str) -> Optional[List[str]]:
        t = ["".join(ch for ch in syl if ch in TONE_LETTERS) for syl in nfd(form).split(".")]
        return t if any(t) else None

    # ── aplicação ────────────────────────────────────────────────────────
    def evolve(self, segs: List[str], tones=None, left=True, right=True,
               chain: Optional[List[str]] = None, stages: Optional[List] = None) -> Word:
        w = Word([nfd(s) for s in segs], tones, self.P, self, left, right)  # o projeto usa NFD
        for k, law in enumerate(chain if chain is not None else self.chain):
            new = L.LAWS[law]["fn"](self.P, w)
            if stages is not None and new.segs != w.segs:
                stages.append((k, "".join(w.segs), "".join(new.segs)))
            w = new
        return w

    def map_segment(self, s: str) -> str:
        """Destino de um som isolado (para padrões vocálicos e harmonia)."""
        w = self.evolve([s], left=False, right=False)
        return w.segs[0] if len(w.segs) == 1 else s

    def choose_laws(self) -> List[str]:
        if self.requested:
            bad = [x for x in self.requested if x not in L.LAWS]
            if bad:
                raise SystemExit(f"Leis desconhecidas: {', '.join(bad)}. Veja --list-laws.")
            return list(self.requested)
        rate = self.rng.uniform(3, 5)
        n = max(1, round(self.years / 1000 * rate))
        words = [(self.segments(e["citation"]), self.tones_of(e["citation"]))
                 for e in self.files["lexicon"]["entries"] if e.get("citation") and "-" not in e["citation"]]
        chosen: List[str] = []

        def applies(law: str) -> bool:
            before = [self.evolve(s, t, chain=chosen).segs for s, t in words]
            after = [self.evolve(s, t, chain=chosen + [law]).segs for s, t in words]
            return sum(1 for a, b in zip(before, after) if a != b) >= 3

        for law in L.PROFILES[self.profile]["laws"]:
            if len(chosen) >= n:
                break
            if applies(law):
                chosen.append(law)
        pool = dict(L.NATURAL_WEIGHTS)
        tries = 0
        while len(chosen) < n and pool and tries < 40:
            tries += 1
            law = self.rng.choices(list(pool), list(pool.values()))[0]
            pool.pop(law)
            if law not in chosen and applies(law):
                chosen.append(law)
        return chosen

    # ── língua-filha ─────────────────────────────────────────────────────
    def build(self, out_dir: Path) -> Dict:
        self.chain = self.choose_laws()
        F = json.loads(json.dumps(self.files))  # cópia
        lex, morph, syn = F["lexicon"], F["morphology"], F["syntax"]
        cats, typ = F["grammatical_categories"], F["morphological_typology"] or {}

        # 0. fronteiras de cada raiz na forma de citação da mãe (antes de qualquer troca)
        for e in lex["entries"]:
            if e.get("root"):
                plain = "".join(self.segments(e.get("citation") or "".join(e["root"])))
                e["_edges"] = (plain.startswith("".join(e["root"])), plain.endswith("".join(e["root"])))
        # 0b. evolução do léxico: substituições e mudanças de significado (ainda na mãe)
        lex_events: List[Dict] = []
        if self.lexical:
            parent_eng = MorphologicalEngine.load(self.files["morphology"], self.files["phonemic_inventory"],
                                                  self.files["phonotactics"], cats, typ)
            parent_eng.ph.rng = random.Random(derive_seed(self.seed, "new_roots"))
            lex_events = LX.apply_lexical(self, lex, parent_eng, _load(self.dir / "derivation.json"))

        # 1. raízes do léxico (as fronteiras dependem de a citação ter afixos)
        history = {k: {"examples": [], "count": 0} for k in range(len(self.chain))}
        surface_words: List[List[str]] = []
        cognates = []
        for e in lex["entries"]:
            if not e.get("root"):
                continue
            skeleton = "-" in e.get("form", "")
            root = list(e["root"])
            cit = e.get("citation") or "".join(root)
            left, right = e.pop("_edges", (True, True))
            tones = e.get("tones") or None
            if skeleton:  # esqueleto consonantal: cada consoante muda sozinha, sem perder posições
                e["root"] = [self.map_segment(c) for c in root]
            else:
                w = self.evolve(root, tones, left, right)
                e["root"] = w.segs
                e["tones"] = w.tones or []
            e["_old_citation"] = cit
            # história: a palavra inteira (forma de citação), lei a lei
            if "-" not in cit:
                stages: List = []
                full = self.evolve(self.segments(cit), self.tones_of(cit), stages=stages)
                surface_words.append(full.segs)  # a palavra inteira evoluída ensina a fonotática nova
                for k, a, b in stages:
                    history[k]["count"] += 1
                    if len(history[k]["examples"]) < 4:
                        history[k]["examples"].append({"label": e.get("label") or e["english"], "before": a, "after": b})

        # 2. pronomes, partículas e palavras gramaticais
        for cell, p in lex["pronouns"]["cells"].items():
            w = self.evolve(p["segments"])
            p["segments"], p["form"] = w.segs, "".join(w.segs)
        for fm in morph["free_markers"].values():
            for v, segs in fm["forms"].items():
                fm["forms"][v] = self.evolve(segs).segs
        for k, segs in syn.get("function_words", {}).items():
            syn["function_words"][k] = self.evolve(segs).segs

        # 3. afixos (sufixo: fronteira só à direita; prefixo: só à esquerda)
        for domain, slots in morph["affixes"].items():
            for slot in slots:
                pos = slot.get("position", "suffix")
                for cls, forms in slot["forms"].items():
                    for cell, segs in forms.items():
                        if not segs:
                            continue
                        inner = [x for x in segs if x != "+"]
                        w = self.evolve(inner, left=(pos == "prefix"), right=(pos != "prefix"))
                        forms[cell] = w.segs
        # 4. processos não lineares e harmonia: mapas de sons isolados
        for pats in [morph["nonlinear"].get("patterns", {})] + \
                [p.get("patterns", {}) for dom in morph["nonlinear"]["processes"].values() for p in dom]:
            for key, pat in pats.items():
                pats[key] = [self.map_segment(x) if not x.startswith("C") else x for x in pat]
        for dom in morph["nonlinear"]["processes"].values():  # apofonia: mapas vogal → vogal
            for p in dom:
                for mkey in ("map", "maps", "mapping"):
                    m = p.get(mkey)
                    if isinstance(m, dict):
                        p[mkey] = {self.map_segment(a): ({c: self.map_segment(b) for c, b in v.items()}
                                                         if isinstance(v, dict) else self.map_segment(v))
                                   for a, v in m.items()}
        h = morph.get("harmony", {})
        if h.get("enabled"):
            for key in ("pairs",):
                if isinstance(h.get(key), dict):
                    h[key] = {self.map_segment(a): {g: self.map_segment(b) for g, b in v.items()}
                              if isinstance(v, dict) else self.map_segment(v) for a, v in h[key].items()}
        for kind in ("nouns", "verbs"):
            for item in morph.get("lexicon_sample", {}).get(kind, []):
                if "-" in item.get("form", ""):
                    item["root"] = [self.map_segment(c) for c in item["root"]]
                    item["form"] = "-".join(item["root"])
                    continue
                w = self.evolve(item["root"], item.get("tones") or None)
                item["root"], item["form"], item["tones"] = w.segs, "".join(w.segs), w.tones or []

        # 5. inventário novo
        inventory = self.new_inventory(lex, morph, syn)
        # 6. fonotática nova, aprendida das palavras evoluídas
        rules = pht_mod.build_rules(inventory, seed=derive_seed(self.seed, "phonotactics"),
                                    complexity=F["phonotactics"].get("syllable_complexity"))
        rules["root"] = F["phonotactics"]["root"]  # tipo de raiz herdado (ex: esqueleto consonantal)
        words = []
        for i, e in enumerate(lex["entries"]):
            if e.get("root") and "-" not in e.get("form", "") and any(self.P.vowel(s) for s in e["root"]):
                words.append({"segments": e["root"], "line": i, "form": "".join(e["root"])})
        for p in lex["pronouns"]["cells"].values():
            if any(self.P.vowel(s) for s in p["segments"]):
                words.append({"segments": p["segments"], "line": 0, "form": p["form"]})
        phonemes = {nfd(x["ipa"]) for x in inventory["consonants"] + inventory["vowels"]}
        for segs in surface_words:  # formas de citação evoluídas (com afixos e padrões vocálicos)
            if any(self.P.vowel(s) for s in segs) and all(nfd(s) in phonemes for s in segs):
                words.append({"segments": segs, "line": 0, "form": "".join(segs)})
        for kind in ("nouns", "verbs"):  # as raízes de amostra dos paradigmas também
            for item in morph.get("lexicon_sample", {}).get(kind, []):
                if any(self.P.vowel(s) for s in item["root"]):
                    words.append({"segments": item["root"], "line": 0, "form": item["form"]})
        spec = {"words": words, "warnings": []}
        pht_report = ci.adapt_phonotactics(rules, inventory, spec, "adapt", pht_mod)
        notes = rules.get("metadata", {}).get("notes", [])
        rules.setdefault("metadata", {})["notes"] = [n.replace("palavras do usuário", "palavras evoluídas")
                                                     for n in notes]

        # 6b. empréstimos recentes, já adaptados aos sons e à fonotática da filha
        if self.lexical and self.donor:
            ph = pht_mod.Phonotactics(rules, inventory, seed=derive_seed(self.seed, "loans"))
            lex_events += LX.apply_loans(self, lex, self.donor["lexicon"], self.donor_dir.name, inventory, ph,
                                         LX.BORROWING_RATES.get(self.borrowing, 0.15))

        # 7. motor, léxico e paradigmas refeitos
        morph["metadata"] = {**morph.get("metadata", {}), "evolved": True}
        eng = MorphologicalEngine.load(morph, inventory, rules, cats, typ)
        lb = lex_mod.LexiconBuilder(eng, seed=derive_seed(self.seed, "lexicon"))
        for e in lex["entries"]:
            if not e.get("root"):
                continue
            if e.get("tones"):
                sylls = eng.ph.syllabify(e["root"]) or [e["root"]]
                tones = (e["tones"] + [e["tones"][-1]] * len(sylls))[:len(sylls)]
                e["form"] = ".".join("".join(s) + t for s, t in zip(sylls, tones))
            elif "-" not in e.get("form", ""):
                e["form"] = "".join(e["root"])
            else:
                e["form"] = "-".join(e["root"])
            lb._principal_parts(e)
        invalid = 0
        if morph.get("lexicon_sample", {}).get("nouns"):
            morph["paradigms"] = {"noun": eng.paradigm(morph["lexicon_sample"]["nouns"][0], "noun"),
                                  "verb": eng.paradigm(morph["lexicon_sample"]["verbs"][0], "verb")}
            invalid = sum(1 for p in morph["paradigms"].values() for line in p["cells"] for c in line if not c["valid"])
        by_event = {x["gloss"]: x for x in lex_events}
        for e in lex["entries"]:
            old = e.pop("_old_citation", None)
            e.pop("_lex_event", None)
            ev_ = by_event.get(e["gloss"])
            if ev_:
                e["note"] = LX.note_for(ev_)
                if e.get("formation") in ("compound", "colexified"):
                    e["formation"] = "root"
                ev_["new_form"] = e.get("citation")
            if e["gloss"] in CORE_CONCEPTS and old and e.get("citation"):
                cognates.append({"gloss": e["gloss"], "label": e.get("label") or e["english"],
                                 "before": old, "after": e["citation"],
                                 "cognate": ev_ is None or ev_["type"] == "diminutive",
                                 "change": ev_["type"] if ev_ else None})

        # 8. sintaxe: as mesmas decisões, frases refeitas com as palavras novas
        sb = syn_mod.SyntaxBuilder(eng, lex, typ, syn_mod.Wals(None), syn["metadata"].get("seed"))
        sb.s = {**syn["settings"], **syn.get("function_words", {})}
        examples = sb.examples()
        fw = {k: sb.s[k] for k in ("question_particle", "copula_form") if k in sb.s}
        syn = {**syn, "function_words": fw, "examples": examples}

        # 9. pasta da língua-filha
        out_dir.mkdir(parents=True, exist_ok=True)
        _save(out_dir / "morphological_typology.json", typ)
        _save(out_dir / "grammatical_categories.json", cats)
        _save(out_dir / "phonemic_inventory.json", inventory)
        _save(out_dir / "phonotactics.json", rules)
        _save(out_dir / "morphology.json", morph)
        _save(out_dir / "lexicon.json", lex)
        _save(out_dir / "syntax.json", syn)
        manifest = {**(self.files["manifest"] or {}), "name": out_dir.name,
                    "evolved_from": self.dir.name, "seed": self.master}
        _save(out_dir / "manifest.json", manifest)

        parent_inv = self.files["phonemic_inventory"]
        old_set = {x["ipa"] for x in parent_inv["consonants"] + parent_inv["vowels"]}
        new_set = {x["ipa"] for x in inventory["consonants"] + inventory["vowels"]}
        step_years = self.years / (len(self.chain) + 1)
        result = {
            "parent": self.dir.name, "daughter": out_dir.name, "profile": self.profile,
            "profile_name": ("leis escolhidas pelo usuário" if self.requested else L.PROFILES[self.profile]["name"]),
            "years": self.years,
            "laws": [{"id": law, "order": k + 1, "year": int(round((k + 1) * step_years / 50) * 50),
                      "name": L.LAWS[law]["name"], "family": L.LAWS[law]["family"],
                      "description": L.LAWS[law]["description"], "example": L.LAWS[law]["example"],
                      "words_affected": history[k]["count"], "examples": history[k]["examples"]}
                     for k, law in enumerate(self.chain)],
            "cognates": cognates,
            "lexical": {"enabled": self.lexical, "events": lex_events,
                        "retention": self.retention(lex, lex_events),
                        "donor": self.donor_dir.name if self.donor else None, "borrowing": self.borrowing},
            "inventory": {"lost": sorted(old_set - new_set), "gained": sorted(new_set - old_set),
                          "consonants": len(inventory["consonants"]), "vowels": len(inventory["vowels"]),
                          "tones": len(inventory["tones"])},
            "phonotactics_changes": pht_report.get("changes", []),
            "metadata": {"seed": self.seed, "invalid_paradigm_forms": invalid, "variants": self._variants},
        }
        _save(out_dir / "evolution.json", result)
        return result

    @staticmethod
    def retention(lex: Dict, events: List[Dict]) -> Dict:
        """Quanto da lista Leipzig-Jakarta continua cognato (a medida da glotocronologia)."""
        lost = {x["gloss"] for x in events if x["type"] in ("replacement", "shift", "loan")}
        present = [e["gloss"] for e in lex["entries"] if e["gloss"] in LX.RANK]
        kept = [g for g in present if g not in lost]
        return {"list": "Leipzig-Jakarta", "total": len(present), "retained": len(kept),
                "percent": round(100 * len(kept) / len(present), 1) if present else None}

    def new_inventory(self, lex: Dict, morph: Dict, syn: Dict) -> Dict:
        segs, tones = set(), set()
        for e in lex["entries"]:
            segs.update(e.get("root") or [])
            tones.update(t for t in (e.get("tones") or []) if t)
        for p in lex["pronouns"]["cells"].values():
            segs.update(p["segments"])
        for kind in ("nouns", "verbs"):
            for item in morph.get("lexicon_sample", {}).get(kind, []):
                segs.update(item["root"])
        for fm in morph["free_markers"].values():
            for v in fm["forms"].values():
                segs.update(v)
        for v in syn.get("function_words", {}).values():
            segs.update(v)
        for slots in morph["affixes"].values():
            for slot in slots:
                for forms in slot["forms"].values():
                    for v in forms.values():
                        segs.update(x for x in v if x != "+")
        for pats in [morph["nonlinear"].get("patterns", {})]:
            for pat in pats.values():
                segs.update(x for x in pat if not x.startswith("C"))
        h = morph.get("harmony", {})
        if h.get("enabled") and isinstance(h.get("pairs"), dict):
            for a, v in h["pairs"].items():
                segs.add(a)
                segs.update(v.values() if isinstance(v, dict) else [v])
        old = self.files["phonemic_inventory"]
        old_entries = {nfd(x["ipa"]): x for x in old["consonants"] + old["vowels"]}
        cons, vows = [], []
        for s in sorted({nfd(x) for x in segs}):
            if not s or s in ("+", "-"):
                continue
            if nfd(s) in old_entries:
                entry = old_entries[nfd(s)]
                (vows if "height" in entry else cons).append(entry)
                continue
            seg = self.P.stats.segments.get(nfd(s))
            feats = self.P.feats(s)
            freq = round(self.P.stats.frequency(nfd(s)), 4) if seg else 0.0
            if self.P.vowel(s):
                vows.append({"ipa": nfd(s), "frequency": freq, **inv_mod.classify_vowel(feats), "features": feats})
            else:
                manner, place = inv_mod.classify_consonant(feats)
                cons.append({"ipa": nfd(s), "frequency": freq, "manner": manner, "place": place, "features": feats})
        old_tones = {t["ipa"]: t for t in old.get("tones", [])}
        tone_list = [old_tones.get(t, {"ipa": t, "frequency": 0.0}) for t in sorted(tones)]
        return {"consonants": cons, "vowels": vows, "tones": tone_list,
                "counts": {"consonants": len(cons), "vowels": len(vows), "tones": len(tone_list)},
                "metadata": {**old.get("metadata", {}), "evolved_from": self.dir.name,
                             "evolution": {"profile": self.profile, "years": self.years}}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def write_markdown(path: Path, r: Dict, spell=None, parent_spell=None) -> None:
    sp = spell or (lambda x: x)
    psp = parent_spell or (lambda x: x)
    lines = [f"# Evolução: {r['parent']} → {r['daughter']}", "",
             f"Perfil **{r['profile_name']}**, {r['years']} anos, {len(r['laws'])} leis fonéticas aplicadas em ordem.",
             "É uma simulação plausível, não uma previsão: o tempo é aproximado (3 a 5 mudanças grandes por milênio).",
             "", "## Leis, em ordem cronológica", "",
             "| # | Ano (aprox.) | Lei | O que mudou | Palavras | Exemplo real |", "|---|---|---|---|---|---|"]
    for law in r["laws"]:
        lines.append(f"| {law['order']} | {law['year']} | **{law['name']}** ({law['family']}) | "
                     f"{law['description']} | {law['words_affected']} | {law['example']} |")
    lines += ["", "## Exemplos na língua", ""]
    for law in r["laws"]:
        if law["examples"]:
            ex = "; ".join(f"/{x['before']}/ → /{x['after']}/ '{x['label']}'" for x in law["examples"][:3])
            lines.append(f"- **{law['name']}:** {ex}")
    inv = r["inventory"]
    lines += ["", "## Inventário", "",
              f"- {inv['consonants']} consoantes, {inv['vowels']} vogais, {inv['tones']} tons",
              "- Sons perdidos: " + (" ".join(f"/{s}/" for s in inv["lost"]) or "nenhum"),
              "- Sons novos: " + (" ".join(f"/{s}/" for s in inv["gained"]) or "nenhum")]
    lx = r.get("lexical", {})
    if lx.get("enabled"):
        ret = lx["retention"]
        lines += ["", "## Léxico", ""]
        if ret.get("percent") is not None:
            lines.append(f"- Retenção do vocabulário básico (lista Leipzig-Jakarta): **{ret['percent']}%** "
                         f"({ret['retained']} de {ret['total']} significados continuam com a palavra herdada). "
                         "Pela glotocronologia, espera-se cerca de 86% a cada mil anos.")
        groups = {"replacement": "Palavras substituídas", "diminutive": "Diminutivos que viraram a palavra comum",
                  "shift": "Mudanças de significado", "loan": "Empréstimos"}
        for t, title in groups.items():
            items = [x for x in lx["events"] if x["type"] == t]
            if not items:
                continue
            lines += ["", f"### {title}", ""]
            for x in sorted(items, key=lambda x: x["year"]):
                new = x.get("new_form", "")
                if t == "shift":
                    lines.append(f"- ~{x['year']}: '{x['source_label']}' passa a significar também '{x['label']}' "
                                 f"({x['kind']}): **{sp(new)}** /{new}/ substituiu /{x['old_form']}/. "
                                 f"Exemplo real: {x['example']}")
                elif t == "loan":
                    lines.append(f"- ~{x['year']}: '{x['label']}' **{sp(new)}** /{new}/, de {x['donor']} /{x['donor_form']}/")
                else:
                    ex = f" Exemplo real: {x['example']}" if x.get("example") else ""
                    lines.append(f"- ~{x['year']}: '{x['label']}' /{x['old_form']}/ → **{sp(new)}** /{new}/.{ex}")
    if r["cognates"]:
        lines += ["", "## Cognatos", "", f"| Significado | {r['parent']} | {r['daughter']} | |", "|---|---|---|---|"]
        mark = {None: "cognato", "diminutive": "cognato (com diminutivo)", "replacement": "**não cognato** (substituída)",
                "shift": "**não cognato** (mudança de significado)", "loan": "**não cognato** (empréstimo)"}
        for c in r["cognates"]:
            lines.append(f"| {c['label']} | **{psp(c['before'])}** /{c['before']}/ | **{sp(c['after'])}** /{c['after']}/ "
                         f"| {mark.get(c.get('change'), '')} |")
    if r["metadata"]["invalid_paradigm_forms"]:
        lines += ["", f"Nota: {r['metadata']['invalid_paradigm_forms']} formas dos paradigmas não puderam ser reparadas."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_laws() -> None:
    print("\nLEIS DISPONÍVEIS")
    for k, v in L.LAWS.items():
        print(f"  {k:<24} {v['name']} ({v['family']}): {v['description']}")
    print("\nPERFIS")
    for k, v in L.PROFILES.items():
        print(f"  {k:<14} {v['name']}: " + (", ".join(v["laws"]) if v["laws"] else "leis comuns sorteadas pela frequência"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Simula a evolução fonética de uma língua e gera a língua-filha.")
    ap.add_argument("--language", type=Path, help="pasta da língua-mãe (languages/lang-31)")
    ap.add_argument("--profile", default="natural", choices=list(L.PROFILES), help="tipo de evolução")
    ap.add_argument("--years", type=int, default=1000, help="tempo de evolução, em anos")
    ap.add_argument("--laws", help="lista de leis em ordem, separadas por vírgula (ignora perfil e tempo)")
    ap.add_argument("--name", help="nome da língua-filha (padrão: <mãe>-<perfil>-<anos>)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da língua, do perfil e do tempo)")
    ap.add_argument("--no-lexical", action="store_true", help="só mudanças fonéticas (sem substituições nem empréstimos)")
    ap.add_argument("--donor", type=Path, help="língua doadora de empréstimos (outra pasta de languages/)")
    ap.add_argument("--borrowing", choices=list(LX.BORROWING_RATES), help="intensidade dos empréstimos (padrão: medium com --donor)")
    ap.add_argument("--rebuild", action="store_true",
                    help="roda o orquestrador na filha (ortografia, acento, nomes... e o grammar.md)")
    ap.add_argument("--list-laws", action="store_true", help="lista as leis e os perfis e sai")
    args = ap.parse_args()
    if args.list_laws:
        list_laws()
        return
    if not args.language:
        ap.error("informe --language")

    laws = [x.strip() for x in args.laws.split(",")] if args.laws else None
    ev = Evolver(args.language, args.profile, args.years, args.seed, laws,
                 lexical=not args.no_lexical, donor=args.donor, borrowing=args.borrowing)
    name = args.name or (f"{args.language.name}-custom" if laws else f"{args.language.name}-{args.profile}-{args.years}")
    out = args.language.parent / name
    r = ev.build(out)

    spell = parent_spell = None
    po = _load(args.language / "orthography.json")
    if po:
        sys.path.insert(0, str(ROOT / "orthography"))
        import orthography as ortho_mod
        parent_spell = ortho_mod.Orthography(po).spell
    if args.rebuild:
        import generate_language as gl
        manifest = ev.files["manifest"] or {}
        opts = manifest.get("options", {})
        kwargs = {"out": args.language.parent, "start": "orthography"}
        if opts.get("no_wals"):
            kwargs["no_wals"] = True
        gl.generate(ev.master, name=name, **kwargs)
        o = _load(out / "orthography.json")
        if o:
            sys.path.insert(0, str(ROOT / "orthography"))
            import orthography as ortho_mod
            orth = ortho_mod.Orthography(o)
            spell = orth.spell
    write_markdown(out / "evolution.md", r, spell, parent_spell)

    print(f"\nEVOLUÇÃO — {r['parent']} → {r['daughter']} ({r['profile_name']}, {r['years']} anos)")
    for law in r["laws"]:
        ex = law["examples"][0] if law["examples"] else None
        sample = f"  /{ex['before']}/ → /{ex['after']}/ '{ex['label']}'" if ex else ""
        print(f"  {law['order']}. ~{law['year']:>5}  {law['name']:<32} {law['words_affected']:>4} palavras{sample}")
    inv = r["inventory"]
    print(f"\n  Inventário: {inv['consonants']} consoantes, {inv['vowels']} vogais, {inv['tones']} tons")
    if inv["gained"]:
        print("  Sons novos: " + " ".join(f"/{s}/" for s in inv["gained"]))
    if inv["lost"]:
        print("  Sons perdidos: " + " ".join(f"/{s}/" for s in inv["lost"]))
    lx = r["lexical"]
    if lx["enabled"]:
        counts = {}
        for x in lx["events"]:
            counts[x["type"]] = counts.get(x["type"], 0) + 1
        ret = lx["retention"]
        print(f"\n  Léxico: retenção de {ret['percent']}% do vocabulário básico; "
              + ", ".join(f"{n} {LX.TYPE_PLURAL[t][n != 1]}" for t, n in counts.items()) if counts else
              f"\n  Léxico: retenção de {ret['percent']}% do vocabulário básico")
        for x in lx["events"][:6]:
            if x["type"] == "shift":
                print(f"    ~{x['year']:>5} '{x['source_label']}' → também '{x['label']}' ({x['kind']})")
            else:
                print(f"    ~{x['year']:>5} '{x['label']}': {LX.TYPE_PT[x['type']]} /{x['old_form']}/ → /{x.get('new_form', '')}/")
    print("\n  Cognatos:")
    for c in r["cognates"][:10]:
        tag = "" if c["cognate"] else f"  (não cognato: {LX.TYPE_PT[c['change']]})"
        print(f"    {c['label']:<14} /{c['before']}/ → /{c['after']}/{tag}")
    print(f"\n[OK] Língua-filha em '{out}'" + (" (com grammar.md)" if args.rebuild else
          "; rode com --rebuild para gerar ortografia, acento e o grammar.md"))


if __name__ == "__main__":
    main()
