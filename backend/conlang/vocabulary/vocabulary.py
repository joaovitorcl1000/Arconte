"""
Módulo — Vocabulário ampliado.

Amplia o léxico da conlang com a lista do WOLD (World Loanword Database,
Haspelmath & Tadmor 2009): cerca de 1.460 significados organizados em 24 campos
(corpo, casa, agricultura, sociedade, religião...), mapeados no Concepticon.

Em vez de sortear uma raiz nova para cada significado, o módulo forma as
palavras com os recursos da própria língua, como fazem as línguas reais:

    derivação     alfaiate = 'costurar' + agentivo; faca = 'cortar' + instrumento;
                  cego = 'olho' + privativo; casamento = 'casar' + ação
    composição    'young man' = 'jovem' + 'homem'; 'head louse' = 'cabeça' + 'piolho';
                  'mother's brother' = 'mãe' + 'irmão'
    raiz nova     o que não se forma a partir de nada (como 'dog' ou 'salt')

Os processos de derivação usados são os que a língua tem (derivation.json); se
ela não tiver o processo certo, a palavra vira um composto ('costurar-pessoa')
ou uma raiz nova.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico, da derivação, da ortografia e do acento.

Uso:
    python vocabulary/vocabulary.py --language languages/lang-31
    python vocabulary/vocabulary.py --language languages/lang-31 --include-modern

Requer apenas a biblioteca padrão (Python ≥ 3.9). A lista do WOLD vem no arquivo
wold_1460.tsv, na mesma pasta deste módulo.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "orthography", "stress", "derivation"):
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
try:
    import derivation as deriv_mod  # noqa: E402
except ImportError:
    deriv_mod = None

DEFAULT_LIST = HERE / "concepts.tsv" #"wold_1460.tsv"
TONE_LETTERS = "˥˦˧˨˩"

WOLD_FIELDS = {
    "1": "The physical world", "2": "Kinship", "3": "Animals", "4": "The body", "5": "Food and drink",
    "6": "Clothing and grooming", "7": "The house", "8": "Agriculture and vegetation",
    "9": "Basic actions and technology", "10": "Motion", "11": "Possession", "12": "Spatial relations",
    "13": "Quantity", "14": "Time", "15": "Sense perception", "16": "Emotions and values",
    "17": "Cognition", "18": "Speech and language", "19": "Social and political relations",
    "20": "Warfare and hunting", "21": "Law", "22": "Religion and belief", "23": "Modern world",
    "24": "Miscellaneous function words",
}
FIELD_PT = {
    "The physical world": "mundo físico", "Kinship": "parentesco", "Animals": "animais", "The body": "corpo",
    "Food and drink": "comida e bebida", "Clothing and grooming": "vestuário", "The house": "casa",
    "Agriculture and vegetation": "agricultura e vegetação", "Basic actions and technology": "ações e técnicas",
    "Motion": "movimento", "Possession": "posse", "Spatial relations": "relações espaciais",
    "Quantity": "quantidade", "Time": "tempo", "Sense perception": "percepção", "Emotions and values":
    "emoções e valores", "Cognition": "cognição", "Speech and language": "fala", "Social and political relations":
    "sociedade", "Warfare and hunting": "guerra e caça", "Law": "lei", "Religion and belief": "religião",
    "Modern world": "mundo moderno", "Miscellaneous function words": "palavras gramaticais",
}
POS_WOLD = {"Noun": "noun", "Verb": "verb", "Adjective": "adjective", "Adverb": "adverb", "Function word": "particle"}

# Numerais ficam com o módulo de numerais
NUMERAL_GLOSSES = {"ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
                   "ELEVEN", "TWELVE", "FIFTEEN", "TWENTY", "HUNDRED", "THOUSAND"}

# Significados que as línguas costumam formar por derivação: conceito → (base, processo)
DERIVATIONS = {
    "TAILOR": ("SEW", "agentive"), "TEACHER": ("TEACH", "agentive"), "THIEF": ("STEAL", "agentive"),
    "WITNESS": ("SEE", "agentive"), "POTTER": ("CLAY", "agentive"), "PRISONER": ("CATCH", "agentive"),
    "FARMER": ("PLANT (SOMETHING)", "agentive"), "HUNTER": ("HUNT", "agentive"),
    "WEDDING": ("MARRY", "action"), "MURDER": ("KILL", "action"), "JUDGMENT": ("JUDGE", "action"),
    "BEGINNING": ("BEGIN", "action"), "ANSWER": ("ANSWER", "action"), "DANCE": ("DANCE", "action"),
    "SWELLING": ("SWELL", "product"), "SONG": ("SING", "product"), "DAMAGE": ("DESTROY", "product"),
    "WOUND": ("INJURE", "product"), "DARKNESS": ("DARK", "quality"), "AGE": ("OLD", "quality"),
    "BROKEN (NOT WORKING)": ("BREAK (DESTROY OR GET DESTROYED)", "resultative"),
    "COOKED": ("COOK (SOMETHING)", "resultative"),
    "SALTY": ("SALT", "proprietive"), "DIRTY": ("DUST", "proprietive"),
    "STINKING": ("SMELL (PERCEIVE)", "proprietive"), "NAKED": ("CLOTHES", "privative"),
    "POOR": ("MONEY", "privative"), "BLIND": ("EYE", "privative"), "DEAF": ("EAR", "privative"),
    "BALD": ("HAIR", "privative"), "KNIFE": ("CUT", "instrument"), "BROOM": ("SWEEP", "instrument"),
    "KEY": ("LOCK", "instrument"), "COMB": ("COMB", "instrument"), "HAMMER": ("HIT", "instrument"),
    "SPOON": ("EAT", "instrument"), "BRIDGE": ("CROSS", "instrument"), "BED": ("SLEEP", "place"),
    "MARKET": ("BUY", "place"), "GRAVE": ("BURY", "place"), "SCHOOL": ("STUDY", "place"),
    "TEMPLE": ("PRAY", "place"), "TEACH": ("KNOW", "causative"), "SHOW": ("SEE", "causative"),
    "BURN (SOMETHING)": ("BURNING", "causative"), "HOLY": ("DEITY", "relational"),
    "EARLY": ("MORNING", "relational"), "OFTEN": ("MANY", "adverbial"),
}
# Compostos que o inglês escreve numa palavra só: conceito → (modificador, núcleo)
COMPOUNDS = {
    "FISHHOOK": ("FISH", "HOOK"), "FISHNET": ("FISH", "NET"), "FISH TRAP": ("FISH", "TRAP"),
    "COOKHOUSE": ("COOK (SOMETHING)", "HOUSE"), "WORKSHOP": ("WORK (LABOUR)", "HOUSE"),
    "FISHERMAN": ("FISH", "PERSON"), "HERDSMAN": ("CATTLE", "PERSON"), "SHOEMAKER": ("SHOE", "PERSON"),
    "GRANDFATHER": ("OLD", "FATHER"), "GRANDMOTHER": ("OLD", "MOTHER"), "FIREFLY": ("FIRE", "FLY (INSECT)"),
    "EARRING": ("EAR", "RING"), "BREAKFAST": ("MORNING", "FOOD"), "SANDFLY": ("SAND", "FLY (INSECT)"),
}
# Na falta do processo certo: composto com uma palavra genérica (como 'costurar-pessoa')
FALLBACK_HEAD = {"agentive": "PERSON", "instrument": "THING", "place": "HOUSE", "product": "THING"}

TRANSITIVE_FIELDS = {"Basic actions and technology", "Possession", "Warfare and hunting", "Food and drink",
                     "Agriculture and vegetation", "Law", "Clothing and grooming"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def clean_english(text: str) -> str:
    """'the older brother' → 'older brother'; 'to look for' → 'look for'."""
    t = re.sub(r"^(the|a|to) ", "", text.strip())
    t = re.sub(r"\s*\(.*?\)", "", t)  # 'burn(1)', 'dinner (supper)'
    return t.split("/")[0].split(" or ")[0].strip()


def load_wold(path: Path) -> List[Dict]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    out = []
    for r in rows:
        out.append({"id": r["CONCEPTICON_ID"], "gloss": r["CONCEPTICON_GLOSS"], "english": r["ENGLISH"],
                    "label": clean_english(r["ENGLISH"]), "pos": POS_WOLD.get(r["PART_OF_SPEECH"], "particle"),
                    "field": WOLD_FIELDS.get(r["SEMANTIC_FIELD"], "Miscellaneous function words"),
                    "simplicity": float(r["SIMPLICITY_SCORE"] or 0.5)})
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class VocabularyBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None, list_path: Path = DEFAULT_LIST):
        d = language_dir
        self.dir = d
        self.inv = _load(d / "phonemic_inventory.json")
        self.rules = _load(d / "phonotactics.json")
        self.catdata = _load(d / "grammatical_categories.json")
        self.morph = _load(d / "morphology.json")
        self.lex = _load(d / "lexicon.json")
        if not all((self.inv, self.rules, self.catdata, self.morph, self.lex)):
            raise SystemExit(f"A pasta {d} precisa ter inventário, fonotática, categorias, "
                             "morfologia e léxico (gere a língua com o orquestrador).")
        if not list_path.exists():
            raise SystemExit(f"Não encontrei a lista de conceitos {list_path}")
        typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "vocabulary") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.concepts = load_wold(list_path)

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        # derivação da própria língua (as mesmas regras do derivation.json)
        self.deriv = None
        dj = _load(d / "derivation.json")
        if deriv_mod and dj:
            self.deriv = deriv_mod.DerivationBuilder(d, seed=dj["metadata"]["seed"])
            self.deriv.rules_ = dj["rules"]

        self.adj_verbal = self.lex["settings"].get("adjectives") == "verbal"
        self.head_final = self.lex["settings"].get("compound_head", "final") == "final"
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.known: Dict[str, Dict] = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.used = {tuple(self.segments(e["citation"])) for e in self.lex["entries"] if e.get("citation")}
        if dj:
            self.used |= {tuple(self.segments(x["ipa"].replace(" ", ""))) for x in dj["derived"]}
        nj = _load(d / "numerals.json")
        if nj:
            self.used |= {tuple(self.segments(a["form"])) for a in nj["atoms"].values()}
        self.noun_genders = Counter(e.get("gender") for e in self.lex["entries"]
                                    if e["pos"] == "noun" and e.get("gender"))
        self.noun_classes = Counter(e.get("class") for e in self.lex["entries"]
                                    if e["pos"] == "noun" and e.get("class") is not None)

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

    def show(self, ipa: str) -> Dict:
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = " ".join(self.stress.mark(w) for w in ipa.split(" ")) if self.stress else ipa
        return {"written": written, "pronunciation": pron}

    def citation(self, entry: Dict) -> str:
        if entry["pos"] in ("noun", "verb") and entry.get("root"):
            lex = {"root": entry["root"], "form": entry["form"], "tones": entry.get("tones", []),
                   "class": entry.get("class") or 0, "gender": entry.get("gender")}
            return self.eng.inflect(lex, entry["pos"], {})["surface"]
        return entry["form"].replace(".", "") if not any(ch in TONE_LETTERS for ch in entry["form"]) else entry["form"]

    def pos_of(self, c: Dict) -> Tuple[str, Optional[str]]:
        """Classe na língua (adjetivos podem ser verbos estativos) e transitividade."""
        if c["pos"] == "adjective" and self.adj_verbal:
            return "verb", "stative"
        if c["pos"] == "verb":
            return "verb", "transitive" if c["field"] in TRANSITIVE_FIELDS else "intransitive"
        return c["pos"], None

    def gender_class(self, field: str, head: Optional[Dict] = None) -> Tuple[Optional[str], Optional[int]]:
        if head and head.get("pos") == "noun":
            return head.get("gender"), head.get("class")
        same = Counter(e.get("gender") for e in self.lex["entries"]
                       if e["pos"] == "noun" and e.get("field") == field and e.get("gender"))
        g = (same or self.noun_genders).most_common(1)[0][0] if (same or self.noun_genders) else None
        k = self.noun_classes.most_common(1)[0][0] if self.noun_classes else None
        return g, k

    # ── planejamento ─────────────────────────────────────────────────────
    def plan(self, include_modern: bool) -> Dict[str, Tuple]:
        """Para cada conceito novo: ('derive', base, processo) | ('compound', mod, head) | ('root',)."""
        todo, seen = [], set()
        for c in self.concepts:  # a lista tem alguns conceitos repetidos (ex: DINNER)
            if c["gloss"] in self.known or c["gloss"] in NUMERAL_GLOSSES or c["gloss"] in seen:
                continue
            if not include_modern and c["field"] == "Modern world":
                continue
            seen.add(c["gloss"])
            todo.append(c)
        by_gloss = {c["gloss"]: c for c in self.concepts}
        word_index: Dict[str, str] = {}
        for gl, e in self.known.items():
            word_index.setdefault(clean_english(e.get("label") or e["english"]).lower(), gl)
        for c in self.concepts:
            if " " not in c["label"]:
                word_index.setdefault(c["label"].lower(), c["gloss"])
        available = set(self.known) | {c["gloss"] for c in todo}

        def resolve(word: str) -> Optional[str]:
            w = word.lower().replace("'s", "")
            for cand in (w, w[:-2] if w.endswith("er") else None, w[:-1] if w.endswith("s") else None):
                if cand and cand in word_index and word_index[cand] in available:
                    return word_index[cand]
            return None

        plans: Dict[str, Tuple] = {}
        for c in todo:
            g = c["gloss"]
            if g in DERIVATIONS and DERIVATIONS[g][0] in available and DERIVATIONS[g][0] != g:
                plans[g] = ("derive",) + DERIVATIONS[g]
            elif g in DERIVATIONS and DERIVATIONS[g][0] == g:
                plans[g] = ("root",)  # 'answer' (nome) = 'answer' (verbo): fica como raiz
            elif g in COMPOUNDS and all(x in available for x in COMPOUNDS[g]):
                plans[g] = ("compound",) + COMPOUNDS[g]
            else:
                words = c["label"].split()
                if len(words) == 2:
                    m, h = resolve(words[0]), resolve(words[1])
                    if m and h and g not in (m, h):
                        plans[g] = ("compound", m, h)
                        continue
                plans[g] = ("root",)
        self.todo = todo
        self.by_gloss = by_gloss
        return plans

    # ── realização ───────────────────────────────────────────────────────
    def new_root(self, c: Dict, pos: str) -> Dict:
        # palavras pouco analisáveis e básicas tendem a ser mais curtas (aproximação da lei de Zipf)
        n = self.rng.choices([1, 2, 3], [0.3, 0.5, 0.2] if c["simplicity"] > 0.8 else [0.15, 0.5, 0.35])[0]
        for _ in range(60):
            if self.eng.skeleton and pos in ("noun", "verb"):
                r = self.ph.generate_skeleton()
                segs, form = r["segments"], "-".join(r["segments"])
            elif self.eng.skeleton:
                sylls = self.ph.generate_syllables(n)
                segs = [s for syl in sylls for s in syl]
                form = self.ph._with_tones(sylls)[1]
            else:
                r = self.ph.generate_root(n)
                segs, form = r["segments"], r["form"]
            if tuple(segs) not in self.used:
                break
        self.used.add(tuple(segs))
        return {"root": segs, "form": form, "tones": []}

    def entry(self, c: Dict, pos: str, transitivity: Optional[str], root: List[str], form: str,
              formation: str, source: Dict, head: Optional[Dict] = None, skeleton: bool = False) -> Dict:
        e = {"id": c["id"], "gloss": c["gloss"], "english": c["english"], "label": c["label"], "pos": pos,
             "field": c["field"], "root": root, "form": form, "tones": [], "formation": formation,
             "source": source, "skeleton": skeleton}
        if transitivity:
            e["transitivity"] = transitivity
        if pos == "noun":
            e["gender"], e["class"] = self.gender_class(c["field"], head)
        elif pos == "verb":
            e["class"] = 0
        e["citation"] = self.citation(e) if formation == "root" else form
        e.update(self.show(e["citation"]))
        return e

    def realize(self, c: Dict, plan: Tuple, made: Dict[str, Dict]) -> Optional[Dict]:
        pos, trans = self.pos_of(c)
        lookup = {**self.known, **made}
        kind = plan[0]
        if kind == "derive":
            base_g, process = plan[1], plan[2]
            base = lookup.get(base_g)
            if base is None:
                return None  # a base ainda não foi criada: tenta de novo depois
            if self.deriv and process in self.deriv.rules_:
                d = self.deriv.derive(base, process)
                if d:
                    if d["pos"] == "verb" and not trans:
                        trans = "transitive"
                    e = self.entry(c, pos, trans, self.segments(d["ipa"]), d["ipa"], "derived",
                                   {"base": base_g, "base_written": base.get("written") or self.show(base["citation"])["written"],
                                    "process": process}, head=base if pos == "noun" else None)
                    return e
            head = FALLBACK_HEAD.get(process)
            if head and head in lookup:  # sem o processo: composto com palavra genérica
                return self.compound(c, pos, trans, base_g, head, lookup, note=f"sem {process}")
            plan = ("root",)
        if plan[0] == "compound":
            mod, head = plan[1], plan[2]
            if mod not in lookup or head not in lookup:
                return None
            return self.compound(c, pos, trans, mod, head, lookup)
        taken = {e["citation"] for e in lookup.values()}
        for _ in range(20):  # raízes diferentes podem dar a mesma forma depois da flexão e do sândi
            r = self.new_root(c, pos)
            e = self.entry(c, pos, trans, r["root"], r["form"], "root", {},
                           skeleton=self.eng.skeleton and pos in ("noun", "verb"))
            if e["citation"] not in taken:
                break
        return e

    def compound(self, c: Dict, pos: str, trans: Optional[str], mod_g: str, head_g: str,
                 lookup: Dict[str, Dict], note: Optional[str] = None) -> Dict:
        m, h = lookup[mod_g], lookup[head_g]
        a, b = self.segments(m["citation"]), self.segments(h["citation"])
        parts = [a, b] if self.head_final else [b, a]
        morphs = [{"segs": list(parts[0]), "role": "root", "label": "", "sep": "-"},
                  {"segs": list(parts[1]), "role": "suffix", "label": "", "sep": "-"}]
        morphs, _, _ = self.eng.resolve(morphs)
        segs = [s for x in morphs for s in x["segs"]]
        ipa = "".join(segs)
        forms = [m["citation"], h["citation"]] if self.head_final else [h["citation"], m["citation"]]
        if any(ch in TONE_LETTERS for f in forms for ch in f) and segs == parts[0] + parts[1]:
            ipa = ".".join(forms)  # língua tonal, sem sândi na fronteira: cada parte mantém seus tons
        src = {"modifier": mod_g, "head": head_g,
               "modifier_written": m.get("written") or self.show(m["citation"])["written"],
               "head_written": h.get("written") or self.show(h["citation"])["written"]}
        if note:
            src["note"] = note
        return self.entry(c, pos, trans, segs, ipa, "compound", src, head=h)

    def build(self, include_modern: bool = False) -> Dict:
        plans = self.plan(include_modern)
        made: Dict[str, Dict] = {}
        pending = [c for c in self.todo]
        # raízes primeiro; depois, em rodadas, o que depende delas
        for c in [c for c in pending if plans[c["gloss"]][0] == "root"]:
            made[c["gloss"]] = self.realize(c, ("root",), made)
        pending = [c for c in pending if c["gloss"] not in made]
        for _ in range(4):
            progress = False
            for c in list(pending):
                e = self.realize(c, plans[c["gloss"]], made)
                if e:
                    made[c["gloss"]] = e
                    pending.remove(c)
                    progress = True
            if not progress:
                break
        for c in pending:  # dependências que não se resolveram: raiz nova
            made[c["gloss"]] = self.realize(c, ("root",), made)
        entries = [made[c["gloss"]] for c in self.todo]
        # rótulos únicos: 'knife' e 'knife (for eating)' não podem aparecer ambos como 'knife'
        counts = Counter(e["label"].lower() for e in entries)
        counts.update((e.get("label") or e["english"]).split(" (")[0].lower() for e in self.lex["entries"])
        for e in entries:
            if counts[e["label"].lower()] > 1:
                e["label"] = e["gloss"].lower()
        stats = Counter(e["formation"] for e in entries)
        fields = Counter(e["field"] for e in entries)
        return {"entries": entries,
                "stats": {"total": len(entries), "root": stats["root"], "derived": stats["derived"],
                          "compound": stats["compound"], "by_field": dict(fields)},
                "metadata": {"seed": self.seed, "list": "Haspelmath-2009-1460 (WOLD)",
                             "lexicon_size": len(self.lex["entries"]), "include_modern": include_modern,
                             "used_derivation": self.deriv is not None}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

POS_ABBR = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv.", "particle": "part."}
PROCESS_PT = {"agentive": "agentivo", "action": "ação", "product": "produto", "quality": "qualidade",
              "resultative": "resultativo", "proprietive": "proprietivo", "privative": "privativo",
              "instrument": "instrumento", "place": "lugar", "causative": "causativo",
              "relational": "relacional", "adverbial": "advérbio"}


def origin(e: Dict) -> str:
    s = e["source"]
    if e["formation"] == "derived":
        return f" ← *{s['base_written']}* ({PROCESS_PT.get(s['process'], s['process'])})"
    if e["formation"] == "compound":
        return f" = *{s['modifier_written']}* + *{s['head_written']}*"
    return ""


def write_markdown(path: Path, data: Dict) -> None:
    st = data["stats"]
    lines = ["# Vocabulário ampliado", "",
             f"{st['total']} palavras novas, da lista do WOLD (Haspelmath & Tadmor 2009), além das "
             f"{data['metadata']['lexicon_size']} do léxico básico: {st['derived']} derivadas, "
             f"{st['compound']} compostas e {st['root']} raízes novas.", "",
             "| Campo | Palavras |", "|---|---|"]
    for f, n in sorted(st["by_field"].items(), key=lambda x: -x[1]):
        lines.append(f"| {FIELD_PT.get(f, f)} | {n} |")
    lines += ["", "## Palavras", "",
              "Formato: **grafia** /pronúncia/ classe 'significado' (← base, nas derivadas; = partes, nas compostas)", ""]
    for e in sorted(data["entries"], key=lambda x: nfd(x["written"]).lower()):
        lines.append(f"- **{e['written']}** /{e['pronunciation']}/ *{POS_ABBR.get(e['pos'], e['pos'])}* "
                     f"'{e['label']}'{origin(e)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Amplia o vocabulário da conlang com a lista do WOLD.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--include-modern", action="store_true", help="inclui o campo 'mundo moderno' (carro, rádio...)")
    ap.add_argument("--list", type=Path, default=DEFAULT_LIST, help="lista de conceitos (formato do wold_1460.tsv)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    args = ap.parse_args()

    b = VocabularyBuilder(args.language, args.seed, args.list)
    data = json.loads(json.dumps(b.build(args.include_modern)))
    (args.language / "vocabulary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "vocabulary.md", data)

    st = data["stats"]
    print(f"\nVOCABULÁRIO AMPLIADO — {st['total']} palavras novas "
          f"({st['derived']} derivadas, {st['compound']} compostas, {st['root']} raízes)")
    shown = Counter()
    for e in data["entries"]:
        if e["formation"] != "root" and shown[e["formation"]] < 5:
            shown[e["formation"]] += 1
            print(f"    {e['written']:<22} /{e['pronunciation']}/  '{e['label']}'{origin(e)}".replace("*", ""))
    if not data["metadata"]["used_derivation"]:
        print("  · sem derivation.json: palavras derivadas viraram compostos ou raízes")
    print(f"\n[OK] Vocabulário salvo em '{args.language / 'vocabulary.json'}' e 'vocabulary.md'.")


if __name__ == "__main__":
    main()
