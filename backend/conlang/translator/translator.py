"""
Módulo — Tradutor (inglês → conlang).

Traduz frases simples em inglês para a conlang, aplicando a gramática dela — não
só palavra por palavra, como o "Smart Translation" do Vulgarlang:

    ordem das palavras, casos, concordância, pro-drop, tempo (presente, passado,
    futuro), negação, plural, artigos, demonstrativos, numerais, adjetivos,
    possessivos ('my dog', 'the woman's dog'), perguntas (sim/não e de conteúdo),
    imperativo e proibitivo, passiva, comparativo e superlativo, coordenação
    ('and', 'but', 'or') e subordinação ('because', 'if', 'that'), formas
    irregulares — tudo como a língua decidiu nos outros módulos.

Funciona em qualquer língua gerada pelo orquestrador, inclusive nas línguas
evoluídas e nas famílias. Palavras sem tradução ficam entre ‹ › e são listadas.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor, da sintaxe, da comparação e da ortografia.

Uso:
    python translator/translator.py --language languages/lang-31 "The woman sees the big dog."
    python translator/translator.py --language languages/lang-31 --file frases.txt --save
    python translator/translator.py --language languages/lang-31          # modo interativo

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "syntax", "orthography", "stress", "comparison", "derivation"):
    sys.path.insert(0, str(ROOT / folder))
from morphological_engine import MorphologicalEngine, gloss as mgloss  # noqa: E402
import syntax as syn_mod  # noqa: E402

try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import comparison as comp_mod  # noqa: E402
except ImportError:
    comp_mod = None
try:
    import derivation as deriv_mod  # noqa: E402
except ImportError:
    deriv_mod = None


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def W(form: str, gloss: str, seg: Optional[str] = None) -> Dict:
    return {"form": form, "seg": seg if seg is not None else form, "gloss": gloss}


# ═══════════════════════════════════════════════════════════════════════════
# Inglês
# ═══════════════════════════════════════════════════════════════════════════

IRREGULAR_PLURAL = {"men": "man", "women": "woman", "children": "child", "feet": "foot", "teeth": "tooth",
                    "mice": "mouse", "geese": "goose", "people": "person", "lice": "louse", "oxen": "ox",
                    "fish": "fish", "sheep": "sheep", "deer": "deer", "leaves": "leaf", "wives": "wife",
                    "knives": "knife", "wolves": "wolf", "lives": "life"}
IRREGULAR_PAST = {"went": "go", "came": "come", "saw": "see", "ate": "eat", "drank": "drink", "gave": "give",
                  "took": "take", "knew": "know", "said": "say", "made": "make", "did": "do", "had": "have",
                  "slept": "sleep", "sat": "sit", "stood": "stand", "ran": "run", "swam": "swim", "flew": "fly",
                  "fell": "fall", "bit": "bite", "held": "hold", "threw": "throw", "found": "find",
                  "thought": "think", "told": "tell", "heard": "hear", "got": "get", "became": "become",
                  "began": "begin", "blew": "blow", "burnt": "burn", "dug": "dig", "fought": "fight",
                  "froze": "freeze", "ground": "grind", "hid": "hide", "hit": "hit", "lay": "lie",
                  "sang": "sing", "spat": "spit", "split": "split", "struck": "strike", "sewed": "sew",
                  "swelled": "swell", "cut": "cut", "brought": "bring", "bought": "buy", "caught": "catch",
                  "left": "leave", "lost": "lose", "met": "meet", "paid": "pay", "sold": "sell", "sent": "send",
                  "spoke": "speak", "stole": "steal", "taught": "teach", "won": "win", "wrote": "write",
                  "laughed": "laugh", "cried": "cry", "died": "die", "lied": "lie"}
IRREGULAR_PARTICIPLE = {"gone": "go", "seen": "see", "eaten": "eat", "drunk": "drink", "given": "give",
                        "taken": "take", "known": "know", "done": "do", "made": "make", "fallen": "fall",
                        "bitten": "bite", "thrown": "throw", "hidden": "hide", "frozen": "freeze", "sung": "sing",
                        "flown": "fly", "swum": "swim", "stolen": "steal", "written": "write", "spoken": "speak",
                        "born": "bear", "killed": "kill", "found": "find", "held": "hold", "heard": "hear",
                        "said": "say", "told": "tell", "cut": "cut", "hit": "hit", "dug": "dig", "sewn": "sew",
                        "blown": "blow", "burnt": "burn", "split": "split", "struck": "strike"}
COMPARATIVE = {"better": "good", "best": "good", "worse": "bad", "worst": "bad", "more": "many", "most": "many",
               "less": "few", "least": "few", "further": "far", "farther": "far"}
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
           "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
           "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
           "fifty": 50, "hundred": 100, "thousand": 1000}
PRONOUNS = {"i": ("1", "singular"), "me": ("1", "singular"), "you": ("2", "singular"), "he": ("3", "singular"),
            "him": ("3", "singular"), "she": ("3", "singular"), "her": ("3", "singular"), "it": ("3", "singular"),
            "we": ("1", "plural"), "us": ("1", "plural"), "they": ("3", "plural"), "them": ("3", "plural")}
PRONOUN_GENDER = {"he": "masculine", "him": "masculine", "she": "feminine", "her": "feminine", "it": "neuter"}
POSSESSIVES = {"my": ("1", "singular"), "your": ("2", "singular"), "his": ("3", "singular"),
               "her": ("3", "singular"), "its": ("3", "singular"), "our": ("1", "plural"),
               "their": ("3", "plural")}
DEMONSTRATIVES = {"this": ("THIS", "singular"), "these": ("THIS", "plural"), "that": ("THAT", "singular"),
                  "those": ("THAT", "plural")}
WH = {"what": "WHAT", "who": "WHO", "whom": "WHO", "where": "WHERE", "when": "WHEN", "how": "HOW"}
BE = {"am": "present", "is": "present", "are": "present", "was": "past", "were": "past", "be": "present",
      "been": "past"}
AUX_DO = {"do": "present", "does": "present", "did": "past"}
PREPOSITIONS = {"in": "IN", "at": "AT", "with": "WITH", "on": "ABOVE", "under": "BELOW OR UNDER",
                "behind": "BEHIND", "near": "NEAR", "inside": "INSIDE", "above": "ABOVE", "below": "BELOW OR UNDER",
                "to": "TO", "from": "FROM", "by": "BY", "for": "FOR", "into": "IN", "of": "OF"}
CONJ = {"and": "and", "but": "but", "or": "or"}
SUBORD = {"because": "because", "if": "if", "when": "when"}
NEGATION = {"not", "n't", "never", "no"}
# Quando o inglês tem uma palavra para dois conceitos, o sentido mais comum
PREFERRED = {"child": "CHILD (YOUNG HUMAN)", "man": "MALE PERSON", "right": "RIGHT", "back": "BACK",
             "fly": "FLY (MOVE THROUGH AIR)", "lie": "LIE (REST)", "burn": "BURNING", "day": "DAY (NOT NIGHT)",
             "skin": "SKIN", "earth": "EARTH (SOIL)", "smoke": "SMOKE (EXHAUST)", "rain": "RAIN (PRECIPITATION)",
             "stone": "STONE", "leg": "LEG", "foot": "FOOT", "hand": "HAND", "knife": "KNIFE"}
# Derivação inglesa → processo de derivação da língua ('hunter' = 'hunt' + agentivo)
EN_DERIVATION = [("ers", "agentive", "verb"), ("er", "agentive", "verb"), ("ors", "agentive", "verb"),
                 ("or", "agentive", "verb"), ("ness", "quality", "adjective"), ("ly", "adverbial", "adjective"),
                 ("less", "privative", "noun"), ("ful", "proprietive", "noun"), ("y", "proprietive", "noun"),
                 ("ing", "action", "verb"), ("ment", "action", "verb"), ("ion", "action", "verb")]


def tokenize(text: str) -> List[str]:
    text = text.replace("’", "'").replace("n't", " n't").replace("'s", " 's")
    return [t for t in re.findall(r"n't|'s|[A-Za-z]+|\d+|[?!.,;]", text)]


# ═══════════════════════════════════════════════════════════════════════════
# Dicionário inglês → conlang
# ═══════════════════════════════════════════════════════════════════════════

class Dictionary:
    """Índice das palavras da língua pelo inglês (léxico, vocabulário ampliado, numerais)."""

    def __init__(self, lexicon: Dict, vocabulary: Optional[Dict]):
        self.by_word: Dict[str, List[Dict]] = {}
        entries = [e for e in lexicon["entries"] if e.get("citation")]
        entries += [e for e in (vocabulary or {}).get("entries", []) if e.get("citation")]
        for e in entries:
            for w in self.keys(e):
                self.by_word.setdefault(w, []).append(e)
        self.by_gloss = {e["gloss"]: e for e in entries}

    @staticmethod
    def keys(e: Dict) -> List[str]:
        texts = [e.get("label") or "", e.get("english") or ""]
        out = []
        for t in texts:
            for part in re.split(r"[/,;]| or ", t):
                p = re.sub(r"\s*\(.*?\)", "", part).strip().lower()
                p = re.sub(r"^(to|the|a) ", "", p)
                if p and p not in out:
                    out.append(p)
        return out

    def find(self, word: str, pos: Optional[Tuple[str, ...]] = None) -> Optional[Dict]:
        cands = self.by_word.get(word.lower(), [])
        pref_gloss = PREFERRED.get(word.lower())
        if pref_gloss and any(e["gloss"] == pref_gloss for e in cands) and \
                (not pos or self.by_gloss[pref_gloss]["pos"] in pos):
            return self.by_gloss[pref_gloss]
        if pos:
            pref = [e for e in cands if e["pos"] in pos or (("adjective" in pos) and e.get("transitivity") == "stative")]
            cands = pref or cands
        if not cands:
            return None
        # rótulo exato primeiro; depois as palavras do léxico básico (mais frequentes)
        return sorted(cands, key=lambda e: ((e.get("label") or "").lower() not in (word, f"to {word}"),
                                            e.get("source") is not None))[0]


def lemma_noun(w: str) -> List[str]:
    w = w.lower()
    if w in IRREGULAR_PLURAL:
        return [IRREGULAR_PLURAL[w]]
    out = [w]
    if w.endswith("ies"):
        out.append(w[:-3] + "y")
    if w.endswith("ves"):
        out += [w[:-3] + "f", w[:-3] + "fe"]
    if w.endswith("es"):
        out.append(w[:-2])
    if w.endswith("s") and not w.endswith("ss"):
        out.append(w[:-1])
    return out


def lemma_verb(w: str) -> List[Tuple[str, str]]:
    """Lemas possíveis e o tempo: [('go', 'past'), ...]."""
    w = w.lower()
    out = [(w, "present")]
    if w in IRREGULAR_PAST:
        out.insert(0, (IRREGULAR_PAST[w], "past"))
    if w.endswith("ied"):
        out.append((w[:-3] + "y", "past"))
    if w.endswith("ed"):
        out += [(w[:-2], "past"), (w[:-1], "past")]
        if len(w) > 4 and w[-3] == w[-4]:
            out.append((w[:-3], "past"))
    if w.endswith("ies"):
        out.append((w[:-3] + "y", "present"))
    if w.endswith("es"):
        out.append((w[:-2], "present"))
    if w.endswith("s") and not w.endswith("ss"):
        out.append((w[:-1], "present"))
    if w.endswith("ing"):
        out += [(w[:-3], "progressive"), (w[:-3] + "e", "progressive")]
        if len(w) > 5 and w[-4] == w[-5]:
            out.append((w[:-4], "progressive"))
    return out


def lemma_adj(w: str) -> List[Tuple[str, Optional[str]]]:
    """('big', 'comparative'), ('big', 'superlative'), ('big', None)."""
    w = w.lower()
    if w in COMPARATIVE:
        return [(COMPARATIVE[w], "superlative" if w.endswith("st") else "comparative")]
    out = [(w, None)]
    for suf, deg in (("est", "superlative"), ("er", "comparative")):
        if w.endswith(suf):
            base = w[:-len(suf)]
            out += [(base, deg), (base + "e", deg)]
            if base.endswith("i"):
                out.append((base[:-1] + "y", deg))
            if len(base) > 2 and base[-1] == base[-2]:
                out.append((base[:-1], deg))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Análise da frase inglesa
# ═══════════════════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, d: Dictionary, derive=None):
        self.d = d
        self.derive = derive  # função (base, processo) → entrada derivada, ou None

    def is_verb(self, w: str) -> Optional[Tuple[Dict, str]]:
        for lem, tense in lemma_verb(w):
            e = self.d.find(lem, ("verb",))
            if e and e["pos"] == "verb" and e.get("transitivity") != "stative":
                return e, tense
        return None

    def adjective(self, w: str) -> Optional[Tuple[Dict, Optional[str]]]:
        for lem, deg in lemma_adj(w):
            e = self.d.find(lem, ("adjective",))
            if e and (e["pos"] == "adjective" or e.get("transitivity") == "stative"):
                return e, deg
        return None

    def derived(self, w: str, want: str) -> Optional[Dict]:
        """'hunter' = 'hunt' + agentivo, com os processos de derivação da própria língua."""
        if not self.derive:
            return None
        lw = w.lower()
        for suf, process, base_pos in EN_DERIVATION:
            if not lw.endswith(suf) or len(lw) <= len(suf) + 2:
                continue
            stem = lw[: -len(suf)]
            for cand in (stem, stem + "e", stem[:-1] if len(stem) > 2 and stem[-1] == stem[-2] else None,
                         stem[:-1] + "y" if stem.endswith("i") else None):
                if not cand:
                    continue
                if base_pos == "verb":
                    hit = self.is_verb(cand)
                    base = hit[0] if hit else None
                elif base_pos == "adjective":
                    hit = self.adjective(cand)
                    base = hit[0] if hit else None
                else:
                    hit = self.noun(cand) if cand != lw else None
                    base = hit[0] if hit else None
                if base:
                    e = self.derive(base, process)
                    if e and (want == "any" or e["pos"] == want):
                        return e
        return None

    def noun(self, w: str) -> Optional[Tuple[Dict, str]]:
        for i, lem in enumerate(lemma_noun(w)):
            e = self.d.find(lem, ("noun",))
            if e and e["pos"] == "noun":
                plural = (lem != w.lower()) or w.lower() in IRREGULAR_PLURAL and w.lower() not in ("fish", "sheep", "deer")
                return e, "plural" if plural else "singular"
        return None

    # ── sintagma nominal ─────────────────────────────────────────────────
    def np(self, toks: List[str]) -> Optional[Dict]:
        toks = [t for t in toks if t not in (",",)]
        if not toks:
            return None
        if len(toks) == 1 and toks[0].lower() in PRONOUNS:
            p, n = PRONOUNS[toks[0].lower()]
            return {"pronoun": True, "person": p, "number": n, "gender": PRONOUN_GENDER.get(toks[0].lower()),
                    "text": toks[0]}
        if len(toks) == 1 and toks[0].lower() in WH:
            return {"wh": WH[toks[0].lower()], "text": toks[0]}
        np: Dict = {"det": None, "dem": None, "poss": None, "possessor": None, "num": None, "adjs": [],
                    "head": None, "number": "singular", "unknown": [], "text": " ".join(toks)}
        if "'s" in toks:  # 'the woman's dog'
            k = toks.index("'s")
            np["possessor"] = self.np(toks[:k])
            toks = toks[k + 1:]
        for t in toks[:-1]:
            lw = t.lower()
            if lw in ("the",):
                np["det"] = "definite"
            elif lw in ("a", "an"):
                np["det"] = "indefinite"
            elif lw in DEMONSTRATIVES:
                np["dem"], num = DEMONSTRATIVES[lw]
                np["number"] = num
            elif lw in POSSESSIVES:
                np["poss"] = POSSESSIVES[lw]
            elif lw in NUMBERS or lw.isdigit():
                np["num"] = NUMBERS.get(lw) or int(lw)
            else:
                a = self.adjective(lw)
                if a:
                    np["adjs"].append(a[0])
                else:
                    n = self.noun(lw)  # substantivo como modificador: tratado como adjetivo de origem
                    (np["adjs"].append(n[0]) if n else np["unknown"].append(t))
        last = toks[-1]
        n = self.noun(last)
        if not n:  # palavra derivada ('hunters', 'teacher')
            plural = last.lower().endswith("s") and not last.lower().endswith("ss")
            for cand in ([last[:-1]] if plural else []) + [last]:
                e = self.derived(cand, "noun")
                if e:
                    n = (e, "plural" if plural and cand != last else "singular")
                    break
        if n:
            np["head"], np["number"] = n[0], ("plural" if n[1] == "plural" or (np["num"] or 1) > 1 else np["number"])
        else:
            np["head_text"] = last
            np["unknown"].append(last)
        return np

    # ── oração ───────────────────────────────────────────────────────────
    def clause(self, toks: List[str], question: bool = False) -> Dict:
        low = [t.lower() for t in toks]
        c: Dict = {"tense": "present", "negative": False, "question": question, "subject": None, "object": None,
                   "recipient": None, "pps": [], "verb": None, "copula": None, "imperative": False,
                   "passive": False, "agent": None, "wh": None, "unknown": [], "aspect": None}
        if low and low[0] in WH and question:
            c["wh"] = WH[low[0]]
            toks, low = toks[1:], low[1:]
        # auxiliares e negação
        i = 0
        aux_front = None
        while i < len(low) and (low[i] in AUX_DO or low[i] in BE or low[i] in ("will", "shall", "can")) and question \
                and i == 0:
            aux_front = low[i]
            i += 1
            break
        rest = list(zip(toks, low))
        if aux_front:
            if aux_front in AUX_DO:
                c["tense"] = AUX_DO[aux_front]
            elif aux_front in ("will", "shall"):
                c["tense"] = "future"
            rest = rest[1:]
        # localizar o verbo
        verb_idx, be_idx = None, None
        for k, (t, l) in enumerate(rest):
            if l in NEGATION:
                c["negative"] = True
                continue
            if l in ("will", "shall"):
                c["tense"] = "future"
                continue
            if l in AUX_DO:
                c["tense"] = AUX_DO[l] if c["tense"] != "future" else "future"
                continue
            if l in BE and be_idx is None and verb_idx is None:
                be_idx = k
                if aux_front is None:
                    c["tense"] = BE[l] if c["tense"] != "future" else "future"
                continue
            if verb_idx is None:
                if l in IRREGULAR_PARTICIPLE and be_idx is not None:
                    v = self.d.find(IRREGULAR_PARTICIPLE[l], ("verb",))
                    if v and v["pos"] == "verb":
                        c["verb"], c["passive"], verb_idx = v, True, k
                        continue
                hit = self.is_verb(l)
                if hit and (k > 0 or not self.noun(l) or low[0] in ("do", "don't", "please")):
                    v, tense = hit
                    if tense == "progressive":
                        c["aspect"] = "progressive"
                    elif be_idx is not None and tense == "past":
                        c["passive"] = True
                    elif tense == "past" and c["tense"] != "future":
                        c["tense"] = "past"
                    c["verb"], verb_idx = v, k
                    continue
        words = [t for t, _ in rest]
        lows = [l for _, l in rest]
        skip = NEGATION | set(AUX_DO) | {"will", "shall"}
        if c["verb"] is not None:
            subj = [w for w, l in rest[:verb_idx] if l not in skip and l not in BE]
            after = [w for w, l in rest[verb_idx + 1:]]
            if not subj and not question:
                c["imperative"] = True
            c["subject"] = self.np(subj) if subj else None
            self._objects(c, after)
            # pergunta de conteúdo: a palavra interrogativa ocupa o argumento que falta
            if c["wh"] in ("WHAT", "WHO"):
                if c["subject"] is None:
                    c["subject"] = {"wh": c["wh"], "text": c["wh"].lower()}
                elif c["object"] is None and c["verb"].get("transitivity") != "intransitive":
                    c["object"] = {"wh": c["wh"], "text": c["wh"].lower()}
                c["wh_in_place"] = True
        elif be_idx is not None:  # cópula: X is big / X is a dog / X is in the house
            subj = [w for w, l in rest[:be_idx] if l not in skip]
            pred = [w for w, l in rest[be_idx + 1:] if l not in skip]
            if question and not subj and pred:  # 'Is the dog big?'
                subj, pred = self._split_subject(pred)
            c["subject"] = self.np(subj) if subj else None
            c["copula"] = self._predicate(pred)
        else:
            c["unknown"] += words
        return c

    def _split_subject(self, toks: List[str]) -> Tuple[List[str], List[str]]:
        for k in range(1, len(toks)):
            if self.noun(toks[k - 1]) and (self.adjective(toks[k]) or toks[k].lower() in PREPOSITIONS):
                return toks[:k], toks[k:]
        return toks[:-1], toks[-1:]

    def _objects(self, c: Dict, toks: List[str]) -> None:
        groups, cur, prep = [], [], None
        for t in toks:
            l = t.lower()
            if l in PREPOSITIONS:
                groups.append((prep, cur))
                cur, prep = [], l
            else:
                cur.append(t)
        groups.append((prep, cur))
        for prep, g in groups:
            if not g:
                continue
            if prep is None:
                # 'gives the child the fish': dois sintagmas sem preposição → recipiente + objeto
                split = None
                for k in range(1, len(g)):
                    if g[k].lower() in ("the", "a", "an", "my", "your", "his", "her", "our", "their") and self.noun(g[k - 1]):
                        split = k
                if split and c["verb"]["gloss"] in ("GIVE",):
                    c["recipient"], c["object"] = self.np(g[:split]), self.np(g[split:])
                else:
                    c["object"] = self.np(g)
            elif prep == "to" and c["verb"] and c["verb"]["gloss"] in ("GIVE", "SAY"):
                c["recipient"] = self.np(g)
            elif prep == "by" and c["passive"]:
                c["agent"] = self.np(g)
            else:
                c["pps"].append((prep, self.np(g)))

    def _predicate(self, toks: List[str]) -> Dict:
        low = [t.lower() for t in toks]
        if not toks:
            return {"type": "none"}
        if "than" in low:  # comparativo
            k = low.index("than")
            adj = next((self.adjective(t) for t in toks[:k] if self.adjective(t)), None)
            if low[0] == "more" and k > 1:
                adj = (self.adjective(toks[1])[0], "comparative") if self.adjective(toks[1]) else adj
            if adj:
                return {"type": "comparative", "adj": adj[0], "standard": self.np(toks[k + 1:])}
        if low[0] == "as" and "as" in low[1:]:
            k = low.index("as", 1)
            adj = self.adjective(toks[1])
            if adj:
                return {"type": "equative", "adj": adj[0], "standard": self.np(toks[k + 1:])}
        if low[0] == "the" and len(toks) == 2:
            a = self.adjective(toks[1])
            if a and a[1] == "superlative":
                return {"type": "superlative", "adj": a[0]}
        if low[0] == "the" and len(toks) == 3 and low[1] == "most":
            a = self.adjective(toks[2])
            if a:
                return {"type": "superlative", "adj": a[0]}
        if len(toks) == 1 and toks[0].lower() in ("mine", "yours", "his", "hers", "ours", "theirs"):
            cell = {"mine": "1.singular", "yours": "2.singular", "his": "3.singular", "hers": "3.singular",
                    "ours": "1.plural", "theirs": "3.plural"}[low[0]]
            return {"type": "possessive", "cell": cell}
        if low[0] in PREPOSITIONS:
            return {"type": "location", "prep": low[0], "np": self.np(toks[1:])}
        if len(toks) == 1 or (len(toks) == 2 and low[0] in ("very",)):
            a = self.adjective(toks[-1])
            if a:
                return {"type": "adjective", "adj": a[0]}
        return {"type": "noun", "np": self.np(toks)}

    # ── frase ────────────────────────────────────────────────────────────
    def sentence(self, text: str) -> Dict:
        toks = tokenize(text)
        question = "?" in toks
        toks = [t for t in toks if t not in ("?", "!", ".", ";")]
        low = [t.lower() for t in toks]
        # coordenação e subordinação (no máximo duas orações)
        for k, l in enumerate(low):
            if k == 0:
                if l in SUBORD:  # 'If the dog sleeps, the child eats'
                    if "," in toks:
                        j = toks.index(",")
                        return {"type": "subordinate", "conj": SUBORD[l], "first": "sub",
                                "sub": self.clause(toks[1:j]), "main": self.clause(toks[j + 1:], question)}
                continue
            if l in CONJ or (l in SUBORD) or (l == "that" and self._verb_before(low[:k], ("know", "think", "say", "see", "hear"))):
                left, right = [t for t in toks[:k] if t != ","], [t for t in toks[k + 1:] if t != ","]
                if self._has_verb(left) and self._has_verb(right):
                    if l in CONJ:
                        return {"type": "coordinate", "conj": CONJ[l], "clauses": [self.clause(left), self.clause(right, question)]}
                    if l == "that":
                        return {"type": "complement", "main": self.clause(left, question), "sub": self.clause(right)}
                    return {"type": "subordinate", "conj": SUBORD[l], "first": "main",
                            "main": self.clause(left, question), "sub": self.clause(right)}
        return {"type": "simple", "clause": self.clause(toks, question)}

    def _has_verb(self, toks: List[str]) -> bool:
        return any(self.is_verb(t.lower()) or t.lower() in BE for t in toks)

    def _verb_before(self, low: List[str], lemmas: Tuple[str, ...]) -> bool:
        return any(lem in lemmas for t in low for lem, _ in lemma_verb(t))


# ═══════════════════════════════════════════════════════════════════════════
# Geração na conlang
# ═══════════════════════════════════════════════════════════════════════════

class Translator:
    def __init__(self, language_dir: Path):
        d = language_dir
        need = ("phonemic_inventory", "phonotactics", "grammatical_categories", "morphology", "lexicon", "syntax")
        self.f = {k: _load(d / f"{k}.json") for k in need + ("morphological_typology", "vocabulary", "numerals",
                                                              "clauses", "comparison", "possession",
                                                              "irregularity", "orthography")}
        if not all(self.f[k] for k in need):
            raise SystemExit(f"A pasta {d} precisa ter a língua completa (gere-a com o orquestrador).")
        self.dir = d
        self.cats = self.f["grammatical_categories"]["categories"]
        self.eng = MorphologicalEngine.load(self.f["morphology"], self.f["phonemic_inventory"], self.f["phonotactics"],
                                            self.f["grammatical_categories"], self.f["morphological_typology"] or {})
        self.sb = syn_mod.SyntaxBuilder(self.eng, self.f["lexicon"], self.f["morphological_typology"] or {},
                                        syn_mod.Wals(None), self.f["syntax"]["metadata"].get("seed"))
        self.sb.s = {**self.f["syntax"]["settings"], **self.f["syntax"].get("function_words", {})}
        self.ortho = ortho_mod.Orthography(self.f["orthography"]) if (ortho_mod and self.f["orthography"]) else None
        self.dict = Dictionary(self.f["lexicon"], self.f["vocabulary"])
        self.derivation = None
        dj = _load(d / "derivation.json")
        if deriv_mod and dj:
            self.derivation = deriv_mod.DerivationBuilder(d, seed=dj["metadata"]["seed"])
            self.derivation.rules_ = dj["rules"]
            self.derived_list = {(x["base"], x["process"]): x for x in dj["derived"]}
        self.parser = Parser(self.dict, self.derive if self.derivation else None)
        self.ov = self.sb.s["word_order"]["object_before_verb"]
        self.preps = self.sb.s["adpositions"] == "prepositions"
        self.symbols = sorted({nfd(x["ipa"]) for x in self.f["phonemic_inventory"]["consonants"]
                               + self.f["phonemic_inventory"]["vowels"]}, key=len, reverse=True)
        self.irregular = {}
        for x in (self.f["irregularity"] or {}).get("irregulars", []):
            self.irregular[(x["gloss"], json.dumps(x["features"], sort_keys=True))] = x
        self.unknown: List[str] = []
        self.notes: List[str] = []

    # ── palavras ─────────────────────────────────────────────────────────
    def derive(self, base: Dict, process: str) -> Optional[Dict]:
        """Entrada derivada pela língua (do derivation.json ou derivada na hora)."""
        if process not in self.derivation.rules_:
            return None
        x = self.derived_list.get((base["gloss"], process)) or self.derivation.derive(base, process)
        if not x or " " in x["ipa"]:
            return None
        segs = self.segments(x["ipa"])
        pos = x["pos"]
        e = {"gloss": f"{base['gloss']}.{process.upper()}", "english": x.get("gloss") or x["meaning"],
             "label": x["meaning"],
             "pos": pos, "root": segs, "form": x["ipa"], "tones": [], "citation": x["ipa"],
             "class": base.get("class") or 0 if pos != "noun" else 0, "gender": None, "field": base.get("field")}
        self.notes.append(f"'{x['meaning']}' formado com a derivação da língua ({process})")
        return e

    def unknown_word(self, text: str) -> Dict:
        self.unknown.append(text)
        return W(f"‹{text}›", text.upper())

    def pronoun_cell(self, person: str, number: str, gender: Optional[str] = None) -> Optional[Dict]:
        cells = self.f["lexicon"]["pronouns"]["cells"]
        for cand in ([f"{person}.{number}.{gender}"] if gender else []) + [f"{person}.{number}",
                                                                           f"{person}excl.{number}",
                                                                           f"{person}incl.{number}"]:
            key = next((k for k in cells if k == cand or k.startswith(cand + ".")), None)
            if key:
                return self.sb.pronoun(key)
        return self.sb.pronoun(f"{person}.singular")

    def numeral(self, n: int) -> Dict:
        for c in (self.f["numerals"] or {}).get("cardinals", []):
            if c["n"] == n:
                return W(c["ipa"], str(n))
        e = self.dict.by_gloss.get({1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE"}.get(n, ""))
        return self.sb.plain_word(e) if e else self.unknown_word(str(n))

    def number_value(self, number: str) -> Optional[str]:
        c = self.cats["number"]
        if not c.get("grammaticalized"):
            return None
        return number if number in c["values"] else ("plural" if number != "singular" and "plural" in c["values"]
                                                     else c["values"][0])

    def agr(self, np: Optional[Dict]) -> str:
        if not np:
            return self.sb.agreement_value("3", "singular")
        if np.get("pronoun"):
            return self.sb.agreement_value(np["person"], np["number"])
        return self.sb.agreement_value("3", np.get("number", "singular"))

    # ── sintagma nominal ─────────────────────────────────────────────────
    def np_words(self, np: Optional[Dict], role: str, verb: Optional[Dict] = None) -> List[Dict]:
        if not np:
            return []
        if np.get("wh"):
            e = self.dict.by_gloss.get(np["wh"])
            return [self.sb.plain_word(e)] if e else [self.unknown_word(np["text"])]
        case = self.sb.case_for(role, verb)
        if np.get("pronoun"):
            p = self.pronoun_cell(np["person"], np["number"], np.get("gender"))
            return self.sb.noun_word(p, {"case": case} if case else {})
        head = np.get("head")
        feats: Dict = {}
        nv = self.number_value(np["number"])
        if nv:
            feats["number"] = nv
        if case:
            feats["case"] = case
        df = self.cats.get("definiteness", {})
        if df.get("grammaticalized") and np.get("det") in df.get("values", []):
            feats["definiteness"] = np["det"]
        words = self.sb.noun_word(head, feats) if head else [self.unknown_word(np.get("head_text", "?"))]
        words = self.apply_irregular(head, {"number": feats.get("number")}, words) if head else words
        pre, post = [], []
        npo = self.sb.s["noun_phrase"]
        mods = []
        if np.get("dem"):
            e = self.dict.by_gloss.get(np["dem"])
            if e:
                mods.append(("demonstrative", [self.sb.plain_word(e)]))
        if np.get("num"):
            words_n = [self.numeral(np["num"])]
            cl = self.sb.classifier(head) if head else None
            if cl:
                words_n = words_n + [cl]
            mods.append(("numeral", words_n))
        for a in np.get("adjs", []):
            mods.append(("adjective", [self.sb.plain_word(a)]))
        for kind, ws in mods:
            (pre if npo[kind] == "before" else post).append(ws)
        post.reverse()
        out = [w for g in pre for w in g] + words + [w for g in post for w in g]
        if np.get("unknown"):
            extra = [self.unknown_word(u) for u in np["unknown"] if u != np.get("head_text")]
            out = extra + out
        if np.get("possessor"):
            pw = self.np_words(np["possessor"], "POSS")
            out = pw + out if npo["genitive"] == "before" else out + pw
        if np.get("poss"):
            out = self.possessive(out, np["poss"], head)
        return out

    def possessive(self, words: List[Dict], poss: Tuple[str, str], head: Optional[Dict]) -> List[Dict]:
        """'my dog': afixo de posse, palavra possessiva ou classificador, conforme o módulo de posse."""
        p = self.f["possession"]
        cell_p = self.pronoun_cell(*poss)
        gl = mgloss(".".join(cell_p["gloss"].split(".")[:2])) if cell_p else "POSS"
        if not p:
            pw = self.np_words({"pronoun": True, "person": poss[0], "number": poss[1]}, "POSS")
            return pw + words if self.sb.s["noun_phrase"]["genitive"] == "before" else words + pw
        st = p["settings"]
        pr, al = st["pronominal"], st["alienability"]
        form = pr["forms"].get(cell_p["gloss"]) if cell_p else None
        if form is None:
            return words
        inalienable = head and head.get("field") in al.get("inalienable_fields", [])
        gen_before = st["nominal"]["possessor_position"] == "before"
        if pr["strategy"] == "affix":
            aff = [x for x in form if x != " "]
            if al.get("classes", 1) >= 2 and not inalienable:  # classificador de posse leva o afixo
                clf = al["alienable_marker"]
                w = W(self.attach(clf, aff, pr["position"]), f"CLF.POSS-{gl}" if pr["position"] == "suffix" else f"{gl}-CLF.POSS")
                return [w] + words if gen_before else words + [w]
            main = next((i for i, w in enumerate(words) if not w["gloss"].isupper()), 0)
            w = words[main]
            new = self.attach(self.segments(w["form"]), aff, pr["position"])
            a = "".join(aff)
            words[main] = W(new, f"{w['gloss']}-{gl}" if pr["position"] == "suffix" else f"{gl}-{w['gloss']}",
                            f"{w['seg']}-{a}" if pr["position"] == "suffix" else f"{a}-{w['seg']}")
            return words
        det = W("".join(form).strip(), f"{gl}.POSS")
        return [det] + words if pr["position"] == "before" else words + [det]

    def attach(self, base: List[str], affix: List[str], kind: str) -> str:
        morphs = ([{"segs": list(affix), "role": "prefix", "label": "", "sep": "-"},
                   {"segs": list(base), "role": "root", "label": "", "sep": "-"}] if kind == "prefix" else
                  [{"segs": list(base), "role": "root", "label": "", "sep": "-"},
                   {"segs": list(affix), "role": "suffix", "label": "", "sep": "-"}])
        morphs, _, _ = self.eng.resolve(morphs)
        return "".join(s for m in morphs for s in m["segs"])

    def segments(self, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in "˥˦˧˨˩ˈˌ"), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def apply_irregular(self, e: Optional[Dict], feats: Dict, words: List[Dict]) -> List[Dict]:
        if not e:
            return words
        for key_feats in (feats,):
            k = (e["gloss"], json.dumps({a: b for a, b in key_feats.items() if b}, sort_keys=True))
            x = self.irregular.get(k)
            if x:
                main = next((i for i, w in enumerate(words) if not w["gloss"].isupper()), 0)
                words[main] = W(x["irregular"]["ipa"], words[main]["gloss"], x["irregular"]["ipa"])
                self.notes.append(f"forma irregular de '{x['label']}'")
        return words

    # ── verbo ────────────────────────────────────────────────────────────
    def tense_feats(self, tense: str) -> Dict:
        if tense == "past":
            f, label = self.sb.tense_feats(True)
            if label != "past":
                self.notes.append("a língua não marca o passado; o verbo fica no presente")
            return f
        if tense == "future":
            t = self.cats.get("tense", {})
            if t.get("grammaticalized") and "future" in t.get("values", []):
                return {"tense": "future"}
            self.notes.append("a língua não tem futuro gramatical; o verbo fica no presente")
        return {}

    def verb_words(self, c: Dict, transitive: bool, subj_agr: str, obj_agr: Optional[str]) -> List[Dict]:
        v = c["verb"]
        feats = {**self.tense_feats(c["tense"]),
                 **self.sb.verb_agreement(transitive, subj_agr, obj_agr)}
        if c["negative"] and self.cats.get("negation", {}).get("grammaticalized"):
            feats["negation"] = "negative"
        if c.get("aspect") == "progressive":
            a = self.cats.get("aspect", {})
            if a.get("grammaticalized") and "imperfective" in a.get("values", []):
                feats["aspect"] = "imperfective"
        words = self.sb.verb_words(v, feats)
        tf = {k: feats[k] for k in ("tense", "aspect") if k in feats}
        words = self.apply_irregular(v, tf, words)
        if c["negative"] and not self.cats.get("negation", {}).get("grammaticalized"):
            e = self.dict.by_gloss.get("NOT")
            if e:
                words = [self.sb.plain_word(e)] + words
        return words

    # ── oração ───────────────────────────────────────────────────────────
    def clause_words(self, c: Dict) -> List[Dict]:
        self.unknown += c.get("unknown", [])
        if c["copula"] is not None:
            return self.copula(c)
        if c["verb"] is None:
            return [self.unknown_word(u) for u in c.get("unknown", [])] or []
        if c["imperative"]:
            return self.imperative(c)
        if c["passive"]:
            return self.passive(c)
        v = c["verb"]
        transitive = c["object"] is not None or bool(c["recipient"])
        subj_role = "A" if transitive else "S"
        S = self.np_words(c["subject"], subj_role, v)
        if c["subject"] and c["subject"].get("pronoun"):
            S = self.sb.subject(S, True) or []
        O = self.np_words(c["object"], "P", v) if c["object"] else None
        R = self.np_words(c["recipient"], "R", v) if c["recipient"] else None
        V = self.verb_words(c, transitive, self.agr(c["subject"]), self.agr(c["object"]) if c["object"] else None)
        loc = self.pps(c["pps"])
        seq = self.sb.clause({"S": S or None, "O": O, "R": R, "V": V}, loc or None)
        seq = self.question(c, seq, V)
        return [w for g in seq if g for w in g]

    def pps(self, pps: List[Tuple[str, Dict]]) -> List[Dict]:
        out = []
        spatial = (self.f["clauses"] or {}).get("settings", {}).get("adpositions", {})
        for prep, np in pps:
            gl = PREPOSITIONS.get(prep, prep.upper())
            if prep in ("in", "at", "into", "inside") and self.sb.case_for("LOC"):
                out += self.np_words(np, "LOC")
                continue
            if prep == "with" and "instrumental" in self.cats["case"].get("values", []) and self.cats["case"].get("grammaticalized"):
                out += self.sb.noun_word(np["head"], {"case": "instrumental"}) if np and np.get("head") else self.np_words(np, "S")
                continue
            word = None
            en = {"under": "under", "below": "under", "above": "above", "on": "above", "behind": "behind",
                  "near": "near", "inside": "inside"}.get(prep)
            if en and spatial.get("forms", {}).get(en):
                word = W("".join(spatial["forms"][en]), en)
            elif self.dict.by_gloss.get(gl):
                word = self.sb.plain_word(self.dict.by_gloss[gl])
            gov = spatial.get("governed_case") if en else None
            n = (self.sb.noun_word(np["head"], {"case": gov, **({"number": self.number_value(np["number"])}
                                                                 if self.number_value(np["number"]) else {})})
                 if gov and np and np.get("head") else self.np_words(np, "S"))
            if word is None:
                word = self.unknown_word(prep)
            before = (spatial.get("position") == "before") if spatial else self.preps
            out += ([word] + n) if before else (n + [word])
        return out

    def question(self, c: Dict, seq: List[List[Dict]], V: List[Dict]) -> List[List[Dict]]:
        if not c["question"]:
            return seq
        if c.get("wh") and c.get("wh_in_place"):  # já está no lugar do argumento
            if self.sb.s["content_questions"] == "initial":
                k = next((i for i, g in enumerate(seq) if g and any(w["gloss"] in ("what", "who") for w in g)), None)
                if k is not None:
                    return [seq[k]] + seq[:k] + seq[k + 1:]
            return seq
        if c.get("wh"):
            e = self.dict.by_gloss.get(c["wh"])
            wh = [self.sb.plain_word(e)] if e else [self.unknown_word(c["wh"].lower())]
            if self.sb.s["content_questions"] == "initial":
                return [wh] + seq
            # in situ: no lugar do argumento perguntado (objeto, se faltar; senão, sujeito)
            vi = next((i for i, g in enumerate(seq) if g is V), len(seq))
            pos = vi if self.ov else vi + 1
            return seq[:pos] + [wh] + seq[pos:]
        return self.sb.polar(seq, V)

    def copula(self, c: Dict) -> List[Dict]:
        p = c["copula"]
        subj = c["subject"]
        S = self.np_words(subj, "S")
        if subj and subj.get("pronoun"):
            S = self.sb.subject(S, True) or S
        t = p["type"]
        if t in ("comparative", "superlative", "equative") and comp_mod and self.f["comparison"] and subj and subj.get("head"):
            b = comp_mod.ComparisonBuilder(self.dir)
            b.settings = self.f["comparison"]["settings"]
            std = p.get("standard") or {}
            y = std.get("head") or subj["head"]
            for s in b.sentences(subj["head"], y, p["adj"]):
                if s["key"] == t:
                    return [W(w["ipa"], w["gloss"], w["seg"]) for w in s["words"]]
        cop = self.sb.s.get("copula_form")
        if t == "adjective":
            a = p["adj"]
            if a.get("transitivity") == "stative":  # adjetivo verbal: conjuga como verbo
                V = self.verb_words({**c, "verb": a}, False, self.agr(subj), None)
                seq = self.sb.clause({"S": S or None, "V": V}, None)
                seq = self.question(c, seq, V)
                return [w for g in seq if g for w in g]
            pred = [self.sb.plain_word(a)]
        elif t == "location":
            pred = self.pps([(p["prep"], p["np"])])
        elif t == "possessive":
            pred = [self.independent_possessive(p["cell"])]
        elif t == "noun":
            pred = self.np_words(p["np"], "S")
        else:
            pred = []
        if c["negative"]:
            e = self.dict.by_gloss.get("NOT")
            if e:
                pred = [self.sb.plain_word(e)] + pred
        if self.sb.s.get("copula") == "word" and cop:
            cw = W("".join(cop), "COP")
            pred = pred + [cw] if self.ov else [cw] + pred
        seq = [S, pred] if S else [pred]
        seq = self.question(c, seq, pred)
        return [w for g in seq if g for w in g]

    def independent_possessive(self, cell: str) -> Dict:
        cl = (self.f["clauses"] or {}).get("tables", {}).get("independent_possessives", [])
        x = next((p for p in cl if p["cell"].startswith(cell)), None)
        if x:
            return W(x["ipa"], f"{mgloss(cell)}.POSS")
        p = self.pronoun_cell(*cell.split("."))
        return W(p["form"], f"{mgloss(cell)}.POSS") if p else self.unknown_word(cell)

    def imperative(self, c: Dict) -> List[Dict]:
        cl = (self.f["clauses"] or {}).get("settings", {})
        imp, pro = cl.get("imperative", {"type": "none"}), cl.get("prohibitive", {"type": "normal"})
        v = c["verb"]
        O = self.np_words(c["object"], "P", v) if c["object"] else None
        if imp.get("type") in ("bare", "affix") and not (c["negative"] and pro.get("type") == "normal"):
            stem = v["citation"] if (self.eng.skeleton or not v.get("root")) else "".join(v["root"])
            word = W(stem, f"{syn_mod.lex_gloss(v)}.IMP")
            if imp["type"] == "affix":
                word = W(self.attach(self.segments(stem), imp["form"], imp["position"]),
                         f"{syn_mod.lex_gloss(v)}-IMP", f"{stem}-{''.join(imp['form'])}")
            V = [word]
        else:
            V = self.verb_words({**c, "tense": "present"}, O is not None, self.sb.agreement_value("2", "singular"),
                                self.agr(c["object"]) if c["object"] else None)
        if c["negative"] and pro.get("type") == "special":
            V = [W("".join(pro["form"]), "PROH")] + V
        seq = self.sb.clause({"S": None, "O": O, "V": V}, self.pps(c["pps"]) or None)
        return [w for g in seq if g for w in g]

    def passive(self, c: Dict) -> List[Dict]:
        pas = (self.f["clauses"] or {}).get("settings", {}).get("passive", {"present": False})
        v = c["verb"]
        subj = c["subject"]
        if not pas.get("present"):
            # sem passiva: oração ativa (com o agente, se houver; senão, sujeito genérico)
            self.notes.append("a língua não tem passiva; a frase foi traduzida como ativa")
            act = {**c, "passive": False, "subject": c.get("agent"), "object": subj}
            if act["subject"] is None:
                act["subject"] = {"pronoun": True, "person": "3", "number": "plural"}
            return self.clause_words(act)
        S = self.np_words(subj, "S", v)
        V = self.verb_words(c, False, self.agr(subj), None)
        if pas["type"] == "affix":
            main = next((i for i, w in enumerate(V) if not w["gloss"].isupper()), 0)
            w = V[main]
            a = "".join(pas["form"])
            V[main] = W(self.attach(self.segments(w["form"]), pas["form"], pas["position"]),
                        f"{w['gloss']}-PASS" if pas["position"] == "suffix" else f"PASS-{w['gloss']}",
                        f"{w['seg']}-{a}" if pas["position"] == "suffix" else f"{a}-{w['seg']}")
        else:
            part = W("".join(pas["form"]), "PASS")
            V = V + [part] if pas["position"] == "after" else [part] + V
        loc = None
        agent = pas.get("agent", {})
        if c.get("agent") and agent.get("type") == "case":
            loc = self.sb.noun_word(c["agent"]["head"], {"case": agent["case"]}) if c["agent"].get("head") else None
        elif c.get("agent") and agent.get("type") == "adposition":
            a = W("".join(agent["form"]), "by")
            n = self.np_words(c["agent"], "S")
            loc = [a] + n if self.preps else n + [a]
        seq = self.sb.clause({"S": S or None, "V": V}, loc)
        seq = self.question(c, seq, V)
        return [w for g in seq if g for w in g]

    # ── frase ────────────────────────────────────────────────────────────
    def connective(self, name: str) -> Dict:
        cl = (self.f["clauses"] or {}).get("settings", {})
        segs = cl.get("connectives", {}).get(name)
        if segs:
            return W("".join(segs), name)
        e = self.dict.by_gloss.get({"and": "AND", "but": "BUT", "or": "OR", "if": "IF", "because": "BECAUSE",
                                    "when": "WHEN"}.get(name, ""))
        return self.sb.plain_word(e) if e else self.unknown_word(name)

    def translate(self, text: str) -> Dict:
        self.unknown, self.notes = [], []
        p = self.parser.sentence(text)
        final = self.ov  # subordinador no fim da subordinada nas línguas OV
        if p["type"] == "simple":
            words = self.clause_words(p["clause"])
        elif p["type"] == "coordinate":
            a, b = (self.clause_words(c) for c in p["clauses"])
            words = a + [self.connective(p["conj"])] + b
        elif p["type"] == "complement":
            sub = self.clause_words(p["sub"])
            comp = (self.f["clauses"] or {}).get("settings", {}).get("complementizer")
            if comp:
                cw = W("".join(comp), "COMP")
                sub = sub + [cw] if final else [cw] + sub
            main = p["main"]
            mv = main["verb"]
            if mv is None:
                words = self.clause_words(main) + sub
            else:
                S = self.np_words(main["subject"], "A", mv)
                if main["subject"] and main["subject"].get("pronoun"):
                    S = self.sb.subject(S, True) or []
                V = self.verb_words(main, True, self.agr(main["subject"]), self.sb.agreement_value("3", "singular"))
                seq = self.sb.clause({"S": S or None, "O": sub, "V": V}, None)
                words = [w for g in seq if g for w in g]
        else:  # subordinada adverbial: 'because', 'if', 'when'
            main, sub = self.clause_words(p["main"]), self.clause_words(p["sub"])
            cw = self.connective(p["conj"])
            sub = sub + [cw] if final else [cw] + sub
            sub_first = final or p["conj"] == "if"  # condicional costuma vir antes em qualquer ordem
            words = sub + main if sub_first else main + sub
        words = [w for w in words if w]
        written = " ".join(self.ortho.spell(w["form"]) if self.ortho and not w["form"].startswith("‹")
                           else w["form"] for w in words)
        written = written[:1].upper() + written[1:]
        punct = "?" if "?" in text else ("!" if "!" in text else ".")
        return {"english": text.strip(), "words": words, "written": written + punct,
                "ipa": " ".join(w["form"] for w in words), "translation": text.strip(),
                "unknown": sorted(set(self.unknown)), "notes": sorted(set(self.notes)), "parse": p["type"]}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def show(r: Dict) -> List[str]:
    lines = [r["written"], ""] + ["    " + l for l in syn_mod.interlinear(r)]
    if r["unknown"]:
        lines.append(f"    Sem tradução: {', '.join(r['unknown'])}")
    for n in r["notes"]:
        lines.append(f"    Nota: {n}")
    return lines


def save(path: Path, results: List[Dict]) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else "# Traduções\n"
    blocks = []
    for r in results:
        blocks += ["", f"## {r['english']}", "", f"**{r['written']}**", "", "```"] + syn_mod.interlinear(r) + ["```"]
        if r["unknown"]:
            blocks.append(f"\nSem tradução: {', '.join(r['unknown'])}")
        for n in r["notes"]:
            blocks.append(f"\nNota: {n}")
    path.write_text(old.rstrip() + "\n" + "\n".join(blocks) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Traduz frases do inglês para a conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta da língua (languages/lang-31)")
    ap.add_argument("text", nargs="*", help="frase(s) em inglês")
    ap.add_argument("--file", type=Path, help="arquivo com uma frase por linha")
    ap.add_argument("--save", action="store_true", help="acrescenta as traduções ao translations.md da língua")
    args = ap.parse_args()

    t = Translator(args.language)
    def split(text: str) -> List[str]:  # um texto pode ter várias frases
        return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    sentences = [x for t in args.text for x in split(t)]
    if args.file:
        sentences += [x for l in args.file.read_text(encoding="utf-8").splitlines() for x in split(l)]
    results = []
    if not sentences:  # modo interativo
        print(f"Tradutor inglês → {args.language.name} (linha vazia para sair)")
        while True:
            try:
                s = input("> ").strip()
            except EOFError:
                break
            if not s:
                break
            for x in split(s):
                r = t.translate(x)
                results.append(r)
                print("\n".join(show(r)) + "\n")
    else:
        for s in sentences:
            r = t.translate(s)
            results.append(r)
            print("\n".join(show(r)) + "\n")
    if args.save and results:
        save(args.language / "translations.md", results)
        print(f"[OK] Traduções acrescentadas a '{args.language / 'translations.md'}'.")


if __name__ == "__main__":
    main()
