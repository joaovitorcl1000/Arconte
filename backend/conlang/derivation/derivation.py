"""
Módulo — Derivação.

Cria os processos de formação de palavras da conlang e, com eles, palavras
derivadas a partir do léxico — como o '-ubtu' do Vulgarlang em 'liar', 'killer'
e 'visitor':

    agentivo      comer → 'quem come'          diminutivo   cão → 'cãozinho'
    instrumento   cortar → 'objeto de cortar'  aumentativo  cão → 'cão enorme'
    ação          comer → 'o ato de comer'     causativo    morrer → 'fazer morrer'
    lugar         dormir → 'lugar de dormir'   factitivo    grande → 'tornar grande'
    qualidade     grande → 'grandeza'          incoativo    grande → 'ficar grande'
    proprietivo   pedra → 'pedregoso'          privativo    água → 'sem água'

Cada língua tem só parte desses processos, cada um com sua forma: afixo
(prefixo ou sufixo), reduplicação, composição com uma palavra do léxico
('pessoa', 'criança'...), perífrase com 'fazer' nas línguas isolantes, ou padrão
vocálico nas línguas de raízes consonantais (como o árabe 'maktab' 'escritório').

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico (sândi), da ortografia e do acento.

Uso:
    python derivation/derivation.py --language languages/lang-31
    python derivation/derivation.py --language languages/lang-31 --all   # todas as bases possíveis

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "orthography", "stress"):
    sys.path.insert(0, str(ROOT / folder))
from morphological_engine import MorphologicalEngine  # noqa: E402

try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import stress as stress_mod  # noqa: E402
except ImportError:
    stress_mod = None

TONE_LETTERS = "˥˦˧˨˩"

# ═══════════════════════════════════════════════════════════════════════════
# Processos: base → resultado, probabilidade de a língua tê-lo (aproximação a
# partir de Štekauer, Valera & Körtvélyessy 2012) e bases preferidas
# ═══════════════════════════════════════════════════════════════════════════

PROCESSES = {
    "agentive":     {"from": "verb", "to": "noun", "p": 0.85, "gloss": "AG",
                     "prefer": ["HUNT", "SING", "FIGHT", "KILL", "EAT", "SEE", "SEW", "DIG", "PLAY", "RUN",
                                "SWIM", "THINK", "THROW", "WASH", "COUNT", "GIVE", "CARRY", "SAY"]},
    "action":       {"from": "verb", "to": "noun", "p": 0.70, "gloss": "NMLZ",
                     "prefer": ["EAT", "SING", "SLEEP", "FIGHT", "WALK", "RUN", "DIE", "LAUGH", "CRY",
                                "PLAY", "THINK", "SWIM", "FLY (MOVE THROUGH AIR)", "BREATHE"]},
    "diminutive":   {"from": "noun", "to": "noun", "p": 0.60, "gloss": "DIM",
                     "prefer": ["DOG", "BIRD", "FISH", "STONE", "STONE OR ROCK", "HOUSE", "TREE", "RIVER",
                                "CHILD (YOUNG HUMAN)", "STICK", "LEAF", "EGG", "MOUNTAIN", "MOON", "STAR"]},
    "causative":    {"from": "verb", "to": "verb", "p": 0.60, "gloss": "CAUS", "intransitive": True,
                     "prefer": ["DIE", "FALL", "SLEEP", "SIT", "STAND", "LAUGH", "CRY", "RUN", "WALK",
                                "FLOAT", "FLOW", "FREEZE", "SWELL", "BURNING", "COME", "GO"]},
    "quality":      {"from": "adjective", "to": "noun", "p": 0.50, "gloss": "ABST",
                     "prefer": ["GOOD", "BIG", "LONG", "OLD", "NEW", "WARM (OF WEATHER)", "COLD (OF WEATHER)",
                                "WIDE", "HEAVY", "SMALL", "SHARP", "STRAIGHT", "SWEET", "BAD"]},
    "instrument":   {"from": "verb", "to": "noun", "p": 0.40, "gloss": "INSTR",
                     "prefer": ["CUT", "DIG", "SEW", "TIE", "SCRATCH", "HIT", "WASH", "WIPE", "GRIND",
                                "STAB", "SPLIT", "RUB", "PUSH", "PULL", "COUNT", "CARRY"]},
    "place":        {"from": "verb", "to": "noun", "p": 0.35, "gloss": "LOC.NMLZ",
                     "prefer": ["SLEEP", "EAT", "SWIM", "HUNT", "SIT", "PLAY", "WASH", "DIG", "LIE (REST)",
                                "FIGHT", "SING", "WALK"]},
    "augmentative": {"from": "noun", "to": "noun", "p": 0.30, "gloss": "AUG",
                     "prefer": ["DOG", "HOUSE", "STONE", "STONE OR ROCK", "TREE", "FISH", "BIRD", "RIVER",
                                "MOUNTAIN", "HEAD", "FIRE", "WIND"]},
    "inchoative":   {"from": "adjective", "to": "verb", "p": 0.35, "gloss": "INCH",
                     "prefer": ["OLD", "BIG", "WARM (OF WEATHER)", "COLD (OF WEATHER)", "DRY", "WET", "RED",
                                "BLACK", "WHITE", "GOOD", "BAD", "LONG", "HEAVY"]},
    "factitive":    {"from": "adjective", "to": "verb", "p": 0.30, "gloss": "FACT",
                     "prefer": ["BIG", "WARM (OF WEATHER)", "COLD (OF WEATHER)", "DRY", "WET", "STRAIGHT",
                                "SHARP", "SMOOTH", "WIDE", "LONG", "WHITE", "BLACK", "NEW"]},
    "proprietive":  {"from": "noun", "to": "adjective", "p": 0.35, "gloss": "PROP",
                     "prefer": ["STONE", "STONE OR ROCK", "WATER", "SAND", "SALT", "TREE", "FIRE", "HAIR",
                                "BLOOD", "DUST", "GRASS", "ROOT", "FAT (ORGANIC SUBSTANCE)", "SNOW", "WIND"]},
    "privative":    {"from": "noun", "to": "adjective", "p": 0.25, "gloss": "PRIV",
                     "prefer": ["WATER", "TOOTH", "HAIR", "NAME", "EYE", "HOUSE", "CHILD (DESCENDANT)", "HEAD",
                                "BLOOD", "SALT", "FIRE", "HAND"]},
}
ORDER = list(PROCESSES)

# Processos acrescentados depois (os do Vulgarlang que faltavam). Ficam numa lista
# própria e são sorteados à parte, para que as línguas já geradas mantenham
# exatamente os mesmos processos e palavras de antes, só ganhando os novos.
NEW_PROCESSES = {
    "adverbial":    {"from": "adjective", "to": "adverb", "p": 0.45, "gloss": "ADVZ",
                     "prefer": ["GOOD", "BAD", "BIG", "SMALL", "LONG", "SHORT", "NEW", "OLD", "STRAIGHT",
                                "WARM (OF WEATHER)", "COLD (OF WEATHER)", "FAR", "NEAR", "SHARP", "SMOOTH"]},
    "denominal":    {"from": "noun", "to": "verb", "p": 0.40, "gloss": "VBZ",
                     "prefer": ["WATER", "FIRE", "SALT", "NAME", "ROPE", "STONE", "STONE OR ROCK", "HAND",
                                "EYE", "TOOTH", "SAND", "DUST", "BLOOD", "SMOKE (EXHAUST)", "ASH", "FAT (ORGANIC SUBSTANCE)"]},
    "resultative":  {"from": "verb", "to": "adjective", "p": 0.45, "gloss": "RES",
                     "prefer": ["EAT", "CUT", "KILL", "WASH", "TIE", "HIDE", "SPLIT", "SEW", "GRIND", "BITE",
                                "THROW", "FREEZE", "SWELL", "FALL", "DIE", "BURNING", "SEE", "KNOW"]},
    "tendential":   {"from": "verb", "to": "adjective", "p": 0.30, "gloss": "TEND",
                     "prefer": ["LAUGH", "CRY", "SLEEP", "FIGHT", "PLAY", "SING", "THINK", "RUN", "BITE",
                                "SAY", "EAT", "DRINK", "SPIT", "WALK", "HUNT", "STEAL"]},
    "product":      {"from": "verb", "to": "noun", "p": 0.40, "gloss": "RES.NMLZ",
                     "prefer": ["SEW", "DIG", "CUT", "SPLIT", "GRIND", "TIE", "DO OR MAKE", "COUNT", "SAY",
                                "SING", "SPIT", "VOMIT", "BREATHE", "THINK", "WASH", "SCRATCH"]},
    "relational":   {"from": "noun", "to": "adjective", "p": 0.35, "gloss": "REL",
                     "prefer": ["SEA", "SUN", "MOON", "STAR", "MOUNTAIN", "RIVER", "FOREST", "NIGHT", "DAY (NOT NIGHT)",
                                "HOUSE", "EARTH (SOIL)", "WATER", "FIRE", "SKY", "HEART", "HEAD", "BLOOD"]},
}
PROCESSES.update(NEW_PROCESSES)
NEW_ORDER = list(NEW_PROCESSES)

PROCESS_PT = {"agentive": "agentivo ('quem faz')", "action": "ação ('o ato de')",
              "diminutive": "diminutivo", "causative": "causativo ('fazer ...')",
              "quality": "qualidade ('-eza', '-idade')", "instrument": "instrumento ('objeto para')",
              "place": "lugar ('lugar de')", "augmentative": "aumentativo",
              "inchoative": "incoativo ('ficar ...')", "factitive": "factitivo ('tornar ...')",
              "proprietive": "proprietivo ('cheio de', '-oso')", "privative": "privativo ('sem')",
              "adverbial": "advérbio ('-mente')", "denominal": "verbo a partir de nome ('fazer/usar ...')",
              "resultative": "resultativo ('-do', 'comido')", "tendential": "tendência ('-ão', 'brigão')",
              "product": "produto do verbo ('o que se faz')", "relational": "relacional ('-ico', 'marítimo')"}

# Compostos/perífrases com palavras do léxico (comuns em línguas isolantes e em
# gramaticalizações: 'criança' como diminutivo, 'pessoa' como agentivo...)
LEXICAL_HEADS = {"agentive": ["PERSON", "MALE PERSON"], "diminutive": ["CHILD (YOUNG HUMAN)"],
                 "augmentative": ["MOTHER", "BIG"], "causative": ["DO OR MAKE"],
                 "factitive": ["DO OR MAKE"], "privative": ["NOT"]}

POS_ABBR = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv."}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def base_en(e: Dict) -> str:
    w = (e.get("label") or e["english"].split(" (")[0]).split("/")[0].strip()
    return w[3:] if w.startswith("to ") else w


def en_3sg(v: str) -> str:
    head, _, rest = v.partition(" ")
    if head.endswith(("s", "sh", "ch", "x", "o")):
        head += "es"
    elif head.endswith("y") and head[-2:-1] not in "aeiou":
        head = head[:-1] + "ies"
    else:
        head += "s"
    return head + (" " + rest if rest else "")


def en_gerund(v: str) -> str:
    head, _, rest = v.partition(" ")
    if head.endswith("ie"):
        head = head[:-2] + "ying"
    elif head.endswith("e") and not head.endswith(("ee", "ye", "oe")):
        head = head[:-1] + "ing"
    elif (len(head) <= 4 and len(head) >= 3 and head[-1] not in "aeiouwxy"
          and head[-2] in "aeiou" and head[-3] not in "aeiou"):
        head = head + head[-1] + "ing"  # cut → cutting, swim → swimming
    else:
        head += "ing"
    return head + (" " + rest if rest else "")


EN_PARTICIPLE = {"eat": "eaten", "see": "seen", "give": "given", "take": "taken", "know": "known",
                 "bite": "bitten", "hide": "hidden", "fall": "fallen", "sew": "sewn", "throw": "thrown",
                 "hold": "held", "cut": "cut", "hit": "hit", "say": "said", "dig": "dug", "split": "split",
                 "grind": "ground", "freeze": "frozen", "swell": "swollen", "sing": "sung", "drink": "drunk",
                 "think": "thought", "do": "done", "make": "made", "fight": "fought", "sleep": "slept",
                 "come": "come", "go": "gone", "run": "run", "fly": "flown", "steal": "stolen", "blow": "blown",
                 "burning": "burnt", "die": "dead"}


def en_participle(v: str) -> str:
    head, _, rest = v.partition(" ")
    if head in EN_PARTICIPLE:
        head = EN_PARTICIPLE[head]
    elif head.endswith("e"):
        head += "d"
    elif head.endswith("y") and head[-2:-1] not in "aeiou":
        head = head[:-1] + "ied"
    else:
        head += "ed"
    return head + (" " + rest if rest else "")


def meaning(process: str, e: Dict) -> str:
    b = base_en(e)
    if process in NEW_PROCESSES:
        return {
            "adverbial": f"in a {b} way", "denominal": f"to do or use {b}",
            "resultative": en_participle(b), "tendential": f"tending to {b}",
            "product": f"what is {en_participle(b)}", "relational": f"relating to {b}",
        }[process]
    return {
        "agentive": f"one who {en_3sg(b)}", "action": f"act of {en_gerund(b)}",
        "diminutive": f"little {b}", "augmentative": f"huge {b}",
        "causative": f"to make (someone) {b}", "quality": f"{b}ness",
        "instrument": f"thing for {en_gerund(b)}", "place": f"place for {en_gerund(b)}",
        "inchoative": f"to become {b}", "factitive": f"to make {b}",
        "proprietive": f"full of {b}", "privative": f"without {b}",
    }[process]


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class DerivationBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None):
        d = language_dir
        self.inv = _load(d / "phonemic_inventory.json")
        self.rules = _load(d / "phonotactics.json")
        self.catdata = _load(d / "grammatical_categories.json")
        self.morph = _load(d / "morphology.json")
        self.lex = _load(d / "lexicon.json")
        if not all((self.inv, self.rules, self.catdata, self.morph, self.lex)):
            raise SystemExit(f"A pasta {d} precisa ter inventário, fonotática, categorias, "
                             "morfologia e léxico (gere a língua com o orquestrador).")
        self.typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "derivation") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, self.typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation") and e.get("root")}
        self.skeleton = self.eng.skeleton
        self.vowels = {nfd(v["ipa"]) for v in self.inv["vowels"]}
        self.default_tone = (max(self.ph.tones, key=lambda t: self.ph.tones[t]["frequency"])
                             if self.ph.tones else "")
        self.used = self._used_forms(d)
        self.words = {tuple(e["root"]) for e in self.lex["entries"] if e.get("root")}

    def _used_forms(self, d: Path) -> set:
        """Formas que afixos novos não podem repetir: afixos do motor, posse, comparação, partículas."""
        used = set()
        for domain in ("noun", "verb"):
            for slot in self.morph["affixes"][domain]:
                for forms in slot["forms"].values():
                    used |= {tuple(x for x in f if x != "+") for f in forms.values() if f}
        for fm in self.morph["free_markers"].values():
            used |= {tuple(w) for w in fm["forms"].values()}
        poss = _load(d / "possession.json")
        if poss:
            p = poss["settings"]
            used |= {tuple(x for x in f if x != " ") for f in p["pronominal"]["forms"].values()}
            for key in ("affix", "linker"):
                if p["nominal"].get(key):
                    used.add(tuple(p["nominal"][key]))
        comp = _load(d / "comparison.json")
        if comp:
            c = comp["settings"]
            for key in ("standard_marker", "exceed_verb"):
                if c.get(key):
                    used.add(tuple(c[key]))
            for k in ("degree", "superlative", "equative"):
                for key in ("comparative", "form"):
                    if c.get(k, {}).get(key):
                        used.add(tuple(c[k][key]))
        used |= {tuple(e["root"]) for e in self.lex["entries"] if e.get("root")}
        return used

    # ── utilidades ───────────────────────────────────────────────────────
    def new_affix(self, kind: str) -> List[str]:
        for _ in range(60):
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

    def retone(self, segs: List[str], base_tones: List[str], kind: str) -> str:
        """Línguas tonais: a base mantém seus tons; as sílabas novas recebem o tom mais comum."""
        if not (self.rules.get("tone_bearing") and self.ph.tones):
            return "".join(segs)
        sylls = self.ph.syllabify(segs) or [segs]
        extra = len(sylls) - len(base_tones)
        fill = [self.default_tone] * max(0, extra)
        tones = (list(base_tones) + fill) if kind != "prefix" else (fill + list(base_tones))
        return ".".join("".join(s) + (tones[i] if i < len(tones) else self.default_tone)
                        for i, s in enumerate(sylls))

    def show(self, ipa: str) -> Dict:
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = " ".join(self.stress.mark(w) for w in ipa.split(" ")) if self.stress else ipa
        return {"written": written, "ipa": ipa, "pronunciation": pron}

    def stem(self, e: Dict) -> List[str]:
        """Base da derivação: a raiz; em raízes consonantais, a forma de citação."""
        if self.skeleton and e["pos"] in ("noun", "verb", "adjective") and "-" in e["form"]:
            return self._segments(e["citation"])
        return list(e["root"])

    def _segments(self, form: str) -> List[str]:
        syms = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]}, key=len, reverse=True)
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ"), 0
            while i < len(s):
                hit = next((x for x in syms if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def _short(self, gloss: str) -> bool:
        """Palavra curta o bastante para virar segundo elemento produtivo (até 2 sílabas)."""
        e = self.entries.get(gloss)
        return bool(e) and len(self.ph.syllabify(self.stem(e)) or [0, 0, 0]) <= 2

    # ── decisões ─────────────────────────────────────────────────────────
    def decide(self) -> Dict:
        typ = self.catdata["metadata"]["typology"]
        isolating = typ["synthesis"] == "isolating"
        procs = set(self.typology.get("active_processes", []))
        redup = procs & {"reduplication_full", "reduplication_partial"}
        prefixing = typ["affix_position"] in ("weakly_prefixing", "strongly_prefixing")
        equal = typ["affix_position"] == "equal"
        chosen = [p for p in ORDER if self.rng.random() < PROCESSES[p]["p"]]
        while len(chosen) < 4:  # toda língua tem pelo menos alguns processos produtivos
            extra = self.rng.choice([p for p in ORDER if p not in chosen])
            chosen.append(extra)
        chosen = [p for p in ORDER if p in chosen]

        rules: Dict[str, Dict] = {}
        used_patterns: set = set()
        # os processos novos são sorteados com um gerador próprio (ver NEW_PROCESSES)
        rng2 = random.Random(self.seed + 7)
        chosen_new = [p for p in NEW_ORDER if rng2.random() < PROCESSES[p]["p"]]
        for p in chosen + chosen_new:
            spec = PROCESSES[p]
            heads = [h for h in LEXICAL_HEADS.get(p, []) if h in self.entries or (h == "NOT" and "NOT" in self.entries)]
            r = self.rng.random()
            if isolating:
                if heads:
                    rule = {"type": "compound", "head": heads[0]}
                elif redup and p in ("diminutive", "augmentative", "action"):
                    rule = {"type": "reduplication"}
                else:  # morfema livre novo, usado como segundo elemento do composto
                    rule = {"type": "compound_new", "form": self.new_affix("suffix")}
            elif redup and p in ("diminutive", "augmentative") and r < 0.5:
                rule = {"type": "reduplication"}
            elif heads and p in ("agentive", "diminutive") and r < 0.2 and self._short(heads[0]):
                rule = {"type": "compound", "head": heads[0]}  # só com palavras curtas
            elif self.skeleton and spec["from"] == "verb" and spec["to"] == "noun" and r < 0.7:
                pattern = self.eng._new_pattern(used_patterns)
                used_patterns.add(tuple(pattern))
                prefix = self.new_affix("prefix") if self.rng.random() < 0.4 else []
                rule = {"type": "pattern", "pattern": pattern, "prefix": prefix}
            else:
                pos = "prefix" if prefixing else ("suffix" if not equal else self.rng.choice(["prefix", "suffix"]))
                rule = {"type": "affix", "position": pos, "form": self.new_affix(pos)}
            rules[p] = {"from": spec["from"], "to": spec["to"], "gloss": spec["gloss"], **rule}
        self.rules_ = rules
        return rules

    # ── aplicação ────────────────────────────────────────────────────────
    def bases(self, process: str) -> List[Dict]:
        spec = PROCESSES[process]
        want = spec["from"]

        def fits(e: Dict) -> bool:
            if want == "adjective":
                return e["pos"] == "adjective" or e.get("transitivity") == "stative"
            if want == "verb":
                return e["pos"] == "verb" and e.get("transitivity") != "stative" and \
                    (not spec.get("intransitive") or e.get("transitivity") == "intransitive")
            return e["pos"] == want

        preferred = [self.entries[g] for g in spec["prefer"] if g in self.entries and fits(self.entries[g])]
        rest = [e for g, e in sorted(self.entries.items()) if fits(e) and e not in preferred]
        return preferred + rest

    def derive(self, e: Dict, process: str) -> Optional[Dict]:
        """Uma palavra derivada: base + processo."""
        rule = self.rules_[process]
        base = self.stem(e)
        tones = e.get("tones") or []
        t = rule["type"]
        seg = None
        if t == "affix":
            segs = self.attach(base, rule["form"], rule["position"])
            ipa = self.retone(segs, tones, rule["position"])
            aff = "".join(rule["form"])
            seg = f"{aff}-{''.join(base)}" if rule["position"] == "prefix" else f"{''.join(base)}-{aff}"
        elif t == "reduplication":
            procs = set(self.typology.get("active_processes", []))
            if "reduplication_full" in procs or "reduplication_partial" not in procs:
                red = list(base)
            else:
                nuc = next((i for i, s in enumerate(base) if s in self.vowels), 0)
                red = base[:nuc + 1]
            segs = self.attach(base, red, "prefix")
            full = len(red) == len(base)  # total: a cópia leva os tons da base; parcial: tom padrão
            ipa = self.retone(segs, tones + tones, "suffix") if full else self.retone(segs, tones, "prefix")
            seg = f"{''.join(red)}~{''.join(base)}"
        elif t in ("compound", "compound_new"):
            if t == "compound":
                h = self.entries.get(rule["head"])
                if not h:
                    return None
                head = self.stem(h)
            else:
                head = rule["form"]
            head_final = self.lex["settings"].get("compound_head", "final") == "final"
            if rule["to"] == "verb" or process in ("privative",):
                parts = [head, base]  # perífrase: 'fazer morrer', 'não água'
                ipa = " ".join("".join(x) for x in parts)
                seg = ipa
            else:
                parts = [base, head] if head_final else [head, base]
                morphs = [{"segs": list(parts[0]), "role": "root", "label": "", "sep": "-"},
                          {"segs": list(parts[1]), "role": "suffix", "label": "", "sep": "-"}]
                morphs, ok, _ = self.eng.resolve(morphs)
                segs = [s for m in morphs for s in m["segs"]]
                ipa = self.retone(segs, tones, "suffix" if head_final else "prefix")
                seg = "-".join("".join(x) for x in parts)
        elif t == "pattern":
            root = e["root"] if "-" in e["form"] else None
            if not root or len(root) < 3:
                return None
            stem = self.eng._repair_stem(self.eng._instantiate(rule["pattern"], root))
            segs = self.attach(stem, rule["prefix"], "prefix") if rule["prefix"] else stem
            ipa = "".join(segs)
            seg = (f"{''.join(rule['prefix'])}-" if rule["prefix"] else "") + "".join(stem)
        else:
            return None
        plain = ipa.replace(".", "")
        for ch in TONE_LETTERS:
            plain = plain.replace(ch, "")
        collision = tuple(self._segments(plain)) in self.words and " " not in plain
        out = {**self.show(ipa), "seg": seg, "process": process, "pos": rule["to"],
               "base": e["gloss"], "base_written": self.show(e["citation"])["written"],
               "meaning": meaning(process, e), "gloss": f"{base_en(e).replace(' ', '.')}-{rule['gloss']}"}
        if collision:
            out["homophone"] = True
        return out

    def build(self, per_process: Optional[int] = 12) -> Dict:
        rules = self.decide()
        derived: List[Dict] = []
        seen = set()
        for p in rules:
            count = 0
            meanings = set()
            for e in self.bases(p):
                if per_process is not None and count >= per_process:
                    break
                d = self.derive(e, p)
                # sem formas repetidas e sem dois significados iguais (ex: 'stone' e 'stone/rock')
                if not d or d["ipa"] in seen or d["meaning"] in meanings:
                    continue
                seen.add(d["ipa"])
                meanings.add(d["meaning"])
                derived.append(d)
                count += 1
        homophones = sum(1 for d in derived if d.get("homophone"))
        if homophones:
            self.notes.append(f"{homophones} derivada(s) coincidem com palavras do léxico (homofonia)")
        return {"rules": rules, "derived": derived,
                "metadata": {"seed": self.seed, "notes": self.notes,
                             "lexicon_size": len(self.lex["entries"]), "derived_count": len(derived),
                             "per_process": per_process}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def rule_text(r: Dict, sp, entries: Dict) -> str:
    t = r["type"]
    if t == "affix":
        f = sp("".join(r["form"]))
        return f"sufixo -{f}" if r["position"] == "suffix" else f"prefixo {f}-"
    if t == "reduplication":
        return "reduplicação"
    if t == "compound":
        h = entries.get(r["head"])
        word = sp(h["citation"]) if h else r["head"].lower()
        return f"composição com *{word}* ('{base_en(h) if h else r['head'].lower()}')"
    if t == "compound_new":
        return f"composição com o morfema livre *{sp(''.join(r['form']))}*"
    if t == "pattern":
        pat = "".join(r["pattern"])
        pre = f"{sp(''.join(r['prefix']))}-" if r["prefix"] else ""
        return f"padrão vocálico {pre}{pat}"
    return t


def write_markdown(path: Path, data: Dict, sp, entries: Dict) -> None:
    lines = ["# Derivação", "",
             f"{len(data['rules'])} processos produtivos; {data['metadata']['derived_count']} palavras derivadas "
             f"(o léxico base tem {data['metadata']['lexicon_size']}).", "",
             "| Processo | Forma | Classe | Exemplo |", "|---|---|---|---|"]
    by_proc: Dict[str, List[Dict]] = {}
    for d in data["derived"]:
        by_proc.setdefault(d["process"], []).append(d)
    for p, r in data["rules"].items():
        ex = by_proc.get(p, [])
        sample = f"*{ex[0]['base_written']}* → **{ex[0]['written']}** '{ex[0]['meaning']}'" if ex else "—"
        lines.append(f"| {PROCESS_PT[p]} | {rule_text(r, sp, entries)} | "
                     f"{POS_ABBR[r['from']]} → {POS_ABBR[r['to']]} | {sample} |")
    lines += ["", "## Palavras derivadas", "", "Formato: **grafia** /pronúncia/ classe 'significado' ← base", ""]
    for d in sorted(data["derived"], key=lambda x: nfd(x["written"]).lower()):
        lines.append(f"- **{d['written']}** /{d['pronunciation']}/ {POS_ABBR[d['pos']]} '{d['meaning']}' "
                     f"← *{d['base_written']}*" + (" (homófona de uma palavra do léxico)" if d.get("homophone") else ""))
    for n in data["metadata"]["notes"]:
        lines += ["", f"Nota: {n}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera processos de derivação e palavras derivadas.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--per-process", type=int, default=12, help="palavras derivadas por processo")
    ap.add_argument("--all", action="store_true", help="deriva de todas as bases possíveis")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    args = ap.parse_args()

    b = DerivationBuilder(args.language, args.seed)
    data = json.loads(json.dumps(b.build(None if args.all else args.per_process)))
    sp = (lambda x: b.ortho.spell(x)) if b.ortho else (lambda x: x)
    (args.language / "derivation.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "derivation.md", data, sp, b.entries)

    print(f"\nDERIVAÇÃO — {len(data['rules'])} processos, {data['metadata']['derived_count']} palavras novas")
    by_proc: Dict[str, List[Dict]] = {}
    for d in data["derived"]:
        by_proc.setdefault(d["process"], []).append(d)
    for p, r in data["rules"].items():
        print(f"  {PROCESS_PT[p]:<34} {rule_text(r, sp, b.entries)}")
        for d in by_proc.get(p, [])[:2]:
            print(f"      {d['base_written']:<12} → {d['written']:<18} /{d['pronunciation']}/  '{d['meaning']}'")
    for n in data["metadata"]["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Derivação salva em '{args.language / 'derivation.json'}' e 'derivation.md'.")


if __name__ == "__main__":
    main()
