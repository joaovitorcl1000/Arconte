"""
Módulo — Léxico.

Transforma as formas sonoras do motor morfológico em um dicionário: atribui
uma palavra a cada conceito de uma lista de vocabulário básico, com classe de
palavra, transitividade, gênero/classe nominal, classe flexional, pronomes
coerentes com a concordância, colexificações, compostos e formas flexionadas.

Listas embutidas (Concepticon):
  leipzig-jakarta  — Tadmor (2009), 100 conceitos ranqueados por estabilidade
  swadesh-200      — Swadesh (1952), 200 conceitos
  all              — união das duas (231 conceitos)
Qualquer outra lista do Concepticon pode ser usada com --concepticon e --list.

Entradas:
  ../phonemic_inventory/phonemic_inventory.json
  ../phonotactics/phonotactics.json
  ../grammatical_categories/grammatical_categories.json
  ../morphological_engine/morphology.json
  ../morphological_typology/morphological_typology.json   (opcional)

Saídas: lexicon.json e dictionary.md

Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python lexicon.py
    python lexicon.py --list swadesh-200 --seed 42
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "phonotactics"))
sys.path.insert(0, str(ROOT / "morphological_engine"))
from morphological_engine import MorphologicalEngine, gloss  # noqa: E402

DEFAULT_INVENTORY = ROOT / "phonemic_inventory" / "phonemic_inventory.json"
DEFAULT_RULES = ROOT / "phonotactics" / "phonotactics.json"
DEFAULT_CATEGORIES = ROOT / "grammatical_categories" / "grammatical_categories.json"
DEFAULT_MORPHOLOGY = ROOT / "morphological_engine" / "morphology.json"
DEFAULT_TYPOLOGY = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_CONCEPTICON = ROOT / "concepticon-data"
DEFAULT_OUTPUT = HERE / "lexicon.json"
DEFAULT_DICTIONARY = HERE / "dictionary.md"

Segs = List[str]

# ═══════════════════════════════════════════════════════════════════════════
# Conceitos (Concepticon): ID | gloss | inglês | categoria | campo semântico |
# listas (L = Leipzig-Jakarta, S = Swadesh 200) | rank de estabilidade (L)
# Categorias: N = coisa/pessoa, V = ação/processo, A = propriedade,
#             Q = número, O = outros (pronomes, palavras funcionais)
# ═══════════════════════════════════════════════════════════════════════════

CONCEPTS_DATA = """221|FIRE|fire|N|The physical world|LS|1
1221|NOSE|nose|N|The body|LS|2
695|GO|to go|V|Motion|L|3
948|WATER|water|N|The physical world|LS|4
674|MOUTH|mouth|N|The body|LS|5
1205|TONGUE|tongue|N|The body|LS|6
946|BLOOD|blood|N|The body|LS|7
1394|BONE|bone|N|The body|LS|7
1215|THOU|2sg pronoun|O|Kinship|LS|9
670|ROOT|root|N|Agriculture and vegetation|LS|9
1446|COME|to come|V|Motion|LS|11
1402|BREAST|breast|N|The body|L|12
658|RAIN (PRECIPITATION)|rain|N|The physical world|L|13
1209|I|1sg pronoun|O|Kinship|LS|14
1405|NAME|name|N|Speech and language|LS|15
1392|LOUSE|louse|N|Animals|LS|15
1257|WING|wing|N|The body|LS|17
2615|FLESH OR MEAT|flesh/meat|N|The body|LS|18
2121|ARM OR HAND|arm/hand|N|The body|L|19
1504|FLY (INSECT)|fly|N|Animals|L|20
1233|NIGHT|night|N|Time|LS|20
1247|EAR|ear|N|The body|LS|22
1333|NECK|neck|N|The body|LS|23
1406|FAR|far|A|Spatial relations|LS|23
2575|DO OR MAKE|to do/make|V|Basic actions and technology|L|25
1252|HOUSE|house|N|The house|L|26
2125|STONE OR ROCK|stone/rock|N|The physical world|L|27
887|BITTER|bitter|A|Sense perception|L|28
1458|SAY|to say|V|Speech and language|LS|28
1380|TOOTH|tooth|N|The body|LS|28
1040|HAIR|hair|N|The body|LS|31
1202|BIG|big|A|Spatial relations|LS|32
1493|ONE|one|Q|Quantity|LS|32
1235|WHO|who?|O|Cognition|LS|34
262|HE OR SHE OR IT|3sg pronoun|O|Kinship|L|34
2133|STRIKE OR BEAT|to hit/beat|V|Basic actions and technology|L|36
2098|FOOT OR LEG|leg/foot|N|The body|L|37
1393|HORN (ANATOMY)|horn|N|The body|L|38
1214|THIS|this|O|Miscellaneous function words|LS|38
227|FISH|fish|N|Animals|LS|38
1174|YESTERDAY|yesterday|O|Time|L|41
1401|DRINK|to drink|V|Food and drink|LS|42
163|BLACK|black|A|Sense perception|LS|42
1838|NAVEL|navel|N|The body|L|42
1442|STAND|to stand|V|Spatial relations|LS|45
1403|BITE|to bite|V|The body|LS|46
1291|BACK|back|N|The body|LS|46
960|WIND|wind|N|The physical world|LS|48
778|SMOKE (EXHAUST)|smoke|N|The physical world|LS|49
1236|WHAT|what?|O|Cognition|LS|50
1801|CHILD (DESCENDANT)|child (kin term)|N|Kinship|L|51
744|EGG|egg|N|Food and drink|LS|52
1447|GIVE|to give|V|Possession|LS|53
1231|NEW|new|A|Time|LS|53
1428|BURNING|to burn (intr.)|V|The physical world|LS|53
1240|NOT|not|O|Miscellaneous function words|LS|56
1035|GOOD|good|A|Emotions and values|LS|56
3626|KNOW|to know|V|Cognition|L|58
1371|KNEE|knee|N|The body|L|59
671|SAND|sand|N|The physical world|LS|59
1355|LAUGH|to laugh|V|Emotions and values|LS|61
1408|HEAR|to hear|V|Sense perception|LS|61
1228|EARTH (SOIL)|soil|N|The physical world|LS|63
628|LEAF|leaf|N|Agriculture and vegetation|LS|64
156|RED|red|A|Sense perception|LS|64
1224|LIVER|liver|N|The body|LS|66
2486|HIDE|to hide|V|Spatial relations|L|67
763|SKIN|skin/hide|N|The body|L|67
1421|SUCK|to suck|V|Food and drink|LS|67
700|CARRY|to carry|V|Motion|L|70
587|ANT|ant|N|Animals|L|71
1210|HEAVY|heavy|A|Sense perception|LS|71
1749|TAKE|to take|V|Possession|L|71
1229|OLD|old|A|Time|LS|74
1336|EAT|to eat|V|Food and drink|LS|75
471|UPPER LEG (THIGH)|thigh|N|The body|L|76
1244|THICK|thick|A|Spatial relations|LS|76
1203|LONG|long|A|Spatial relations|LS|78
175|BLOW (OF WIND)|to blow|V|Motion|LS|79
1803|WOOD|wood|N|The physical world|L|80
1519|RUN|to run|V|Motion|L|81
1280|FALL|to fall|V|Motion|LS|81
1248|EYE|eye|N|The body|LS|83
646|ASH|ash|N|The physical world|LS|84
1220|TAIL|tail|N|The body|LS|84
2009|DOG|dog|N|Animals|LS|84
1839|CRY|to cry/weep|V|Emotions and values|L|87
1917|TIE|to tie|V|Basic actions and technology|LS|88
1409|SEE|to see|V|Sense perception|LS|89
717|SWEET|sweet|A|Sense perception|L|89
1218|ROPE|rope|N|Basic actions and technology|LS|91
1388|SHADE|shade/shadow|N|The physical world|L|91
937|BIRD|bird|N|Animals|LS|91
1274|SALT|salt|N|Food and drink|LS|91
1246|SMALL|small|A|Spatial relations|LS|91
1243|WIDE|wide|A|Spatial relations|LS|96
1430|STAR|star|N|The physical world|LS|97
1460|IN|in|O|Spatial relations|LS|97
1884|HARD|hard|A|Sense perception|L|99
1033|GRIND|to crush/grind|V|Food and drink|L|100
98|ALL|all (of a number)|O|Quantity|S|
1577|AND|and|O|Cognition|S|
619|ANIMAL|animal|N|Animals|S|
1461|AT|at|O|Spatial relations|S|
1292|BAD|bad (deleterious or unsuitable)|A|Emotions and values|S|
1204|BARK|bark|N|Agriculture and vegetation|S|
1157|BECAUSE|because|O|Cognition|S|
1251|BELLY|belly|N|The body|S|
904|BERRY|berry (or fruit)|N|Agriculture and vegetation|S|
1407|BREATHE|to breathe|V|The body|S|
1304|CHILD (YOUNG HUMAN)|child (young person rather than as relationship term)|N|Kinship|S|
1489|CLOUD|cloud|N|The physical world|S|
2483|COLD (OF WEATHER)|cold (of weather)|A|Sense perception|S|
1420|COUNT|to count|V|Quantity|S|
1432|CUT|to cut|V|Basic actions and technology|S|
1225|DAY (NOT NIGHT)|day (opposite of night rather than time measure)|N|Time|S|
1494|DIE|to die|V|The body|S|
1418|DIG|to dig|V|Agriculture and vegetation|S|
1230|DIRTY|dirty|A|Sense perception|S|
1398|DRY|dry (substance)|A|Sense perception|S|
379|BLUNT|dull (knife)|A|Sense perception|S|
2|DUST|dust|N|The physical world|S|
323|FAT (ORGANIC SUBSTANCE)|fat (organic substance)|N|The body|S|
1217|FATHER|father|N|Kinship|S|
1419|FEAR (BE AFRAID)|to fear|V|Emotions and values|S|
1201|FEATHER|feather (larger feathers rather than down)|N|The body|S|
1242|FEW|few|O|Quantity|S|
1423|FIGHT|to fight|V|Warfare and hunting|S|
493|FIVE|five|Q|Quantity|S|
1574|FLOAT|to float|V|Motion|S|
2003|FLOW|to flow|V|Motion|S|
239|FLOWER|flower|N|Agriculture and vegetation|S|
1441|FLY (MOVE THROUGH AIR)|to fly|V|Motion|S|
249|FOG|fog|N|The physical world|S|
1301|FOOT|foot|N|The body|S|
1500|FOUR|four|Q|Quantity|S|
1431|FREEZE|to freeze|V|The physical world|S|
606|GRASS|grass|N|Agriculture and vegetation|S|
1425|GREEN|green|A|Sense perception|S|
1334|GUTS|guts|N|The body|S|
1277|HAND|hand|N|The body|S|
1211|HE|he|O|Kinship|S|
1256|HEAD|head|N|The body|S|
1223|HEART|heart|N|The body|S|
136|HERE|here|O|Miscellaneous function words|S|
1433|HIT|to hit|V|Basic actions and technology|S|
1448|HOLD|to hold (in hand)|V|Possession|S|
1239|HOW|how|O|Cognition|S|
1435|HUNT|to hunt (game)|V|Warfare and hunting|S|
1200|HUSBAND|husband|N|Kinship|S|
617|ICE|ice|N|The physical world|S|
1459|IF|if|O|Cognition|S|
1417|KILL|to kill|V|The body|S|
1410|KNOW (SOMETHING)|to know (facts)|V|Cognition|S|
624|LAKE|lake|N|The physical world|S|
244|LEFT|left (hand)|A|Spatial relations|S|
1297|LEG|leg|N|The body|S|
1411|LIE (REST)|to lie|V|Spatial relations|S|
1422|BE ALIVE|to live|V|The body|S|
2106|MALE PERSON|man (male human)|N|Kinship|S|
1198|MANY|many|O|Quantity|S|
1216|MOTHER|mother|N|Kinship|S|
639|MOUNTAIN|mountain|N|The physical world|S|
1267|NARROW|narrow|A|Spatial relations|S|
1942|NEAR|near|A|Spatial relations|S|
197|OTHER|other|O|Miscellaneous function words|S|
683|PERSON|person|N|Kinship|S|
1413|PLAY|to play|V|Emotions and values|S|
1455|PULL|to pull|V|Basic actions and technology|S|
1452|PUSH|to push|V|Motion|S|
1253|RAIN (RAINING)|to rain|V|The physical world|S|
1725|CORRECT (RIGHT)|right (correct)|A|Emotions and values|S|
1019|RIGHT|right (hand)|A|Spatial relations|S|
666|RIVER|river|N|The physical world|S|
667|ROAD|road (or trail)|N|Motion|S|
1728|ROTTEN|rotten (especially log)|A|Agriculture and vegetation|S|
1449|RUB|to rub|V|Basic actions and technology|S|
1436|SCRATCH|to scratch (as with fingernails to relieve itch)|V|The body|S|
1474|SEA|sea (ocean)|N|The physical world|S|
714|SEED|seed|N|Agriculture and vegetation|S|
1457|SEW|to sew|V|Clothing and grooming|S|
1396|SHARP|sharp (as knife)|A|Sense perception|S|
1645|SHORT|short|A|Spatial relations|S|
1261|SING|to sing|V|Speech and language|S|
1416|SIT|sit|V|Spatial relations|S|
2613|SKIN (HUMAN)|skin (person's)|N|The body|S|
1732|SKY|sky|N|The physical world|S|
1585|SLEEP|sleep|V|The body|S|
1586|SMELL (PERCEIVE)|to smell (perceive odor)|V|Sense perception|S|
1234|SMOOTH|smooth|A|Sense perception|S|
730|SNAKE|snake|N|Animals|S|
784|SNOW|snow|N|The physical world|S|
1241|SOME|some|O|Quantity|S|
1440|SPIT|to spit|V|The body|S|
1437|SPLIT|to split|V|Basic actions and technology|S|
1414|SQUEEZE|to squeeze|V|Basic actions and technology|S|
1434|STAB|to stab (or stick)|V|Basic actions and technology|S|
1295|STICK|stick (of wood)|N|The physical world|S|
857|STONE|stone|N|The physical world|S|
1404|STRAIGHT|straight|A|Spatial relations|S|
1343|SUN|sun|N|The physical world|S|
1573|SWELL|to swell|V|Basic actions and technology|S|
1439|SWIM|to swim|V|Motion|S|
78|THAT|that|O|Miscellaneous function words|S|
1937|THERE|there|O|Miscellaneous function words|S|
817|THEY|they|O|Kinship|S|
2308|THIN|thin|A|Spatial relations|S|
2271|THINK|to think|V|Cognition|S|
492|THREE|three|Q|Quantity|S|
1456|THROW|to throw|V|Motion|S|
906|TREE|tree|N|Agriculture and vegetation|S|
1444|TURN AROUND|to turn (change one's direction)|V|Motion|S|
1498|TWO|two|Q|Quantity|S|
1278|VOMIT|to vomit|V|The body|S|
1443|WALK|to walk|V|Motion|S|
2110|WARM (OF WEATHER)|warm (of weather)|A|The physical world|S|
1453|WASH|to wash|V|Basic actions and technology|S|
1212|WE|we|O|Kinship|S|
1726|WET|wet|A|Sense perception|S|
1238|WHEN|when?|O|Cognition|S|
1237|WHERE|where?|O|Cognition|S|
1335|WHITE|white|A|Sense perception|S|
1199|WIFE|wife|N|Kinship|S|
1454|WIPE|to wipe|V|Basic actions and technology|S|
1340|WITH|with (accompanying)|O|Miscellaneous function words|S|
962|WOMAN|woman|N|Kinship|S|
420|FOREST|woods|N|The physical world|S|
1219|WORM|worm|N|Animals|S|
1213|YOU|ye|O|Kinship|S|
1226|YEAR|year|N|Time|S|
1424|YELLOW|yellow|A|Sense perception|S|"""

ONTOLOGY_TO_CODE = {"Person/Thing": "N", "Action/Process": "V", "Property": "A",
                    "Number": "Q", "Other": "O"}

# Subclasses das palavras "O" (outros)
FUNCTION_CLASSES = {
    "pronoun": {"I", "THOU", "HE", "HE OR SHE OR IT", "WE", "YOU", "THEY"},
    "demonstrative": {"THIS", "THAT"},
    "interrogative": {"WHAT", "WHO", "WHERE", "WHEN", "HOW"},
    "quantifier": {"ALL", "FEW", "MANY", "SOME", "OTHER"},
    "conjunction": {"AND", "IF", "BECAUSE"},
    "adverb": {"HERE", "THERE", "YESTERDAY"},
    "adposition": {"AT", "IN", "WITH"},
    "negation": {"NOT"},
}

PRONOUN_CELLS = {"I": "1.singular", "THOU": "2.singular", "HE": "3.singular",
                 "HE OR SHE OR IT": "3.singular", "WE": "1.plural", "YOU": "2.plural",
                 "THEY": "3.plural"}

# Adposições que podem ser expressas por caso
ADPOSITION_CASES = {"AT": ["locative"], "IN": ["locative", "essive"],
                    "WITH": ["comitative", "instrumental"]}

# Verbos transitivos (o restante é intransitivo); GIVE é bitransitivo
TRANSITIVE = {"BITE", "CARRY", "COUNT", "CUT", "DIG", "DO OR MAKE", "DRINK", "EAT", "GRIND",
              "HEAR", "HIDE", "HIT", "HOLD", "HUNT", "KILL", "KNOW", "KNOW (SOMETHING)", "PULL",
              "PUSH", "RUB", "SAY", "SCRATCH", "SEE", "SEW", "SMELL (PERCEIVE)", "SPLIT",
              "SQUEEZE", "STAB", "STRIKE OR BEAT", "SUCK", "TAKE", "THROW", "TIE", "WASH",
              "WIPE", "FEAR (BE AFRAID)"}
DITRANSITIVE = {"GIVE"}

# Colexificações frequentes entre línguas (CLICS): (conceito-base, conceito, probabilidade)
COLEXIFICATIONS = [
    ("FOOT", "LEG", 0.30), ("SKIN (HUMAN)", "BARK", 0.25), ("TREE", "STICK", 0.20),
    ("DAY (NOT NIGHT)", "SUN", 0.25), ("WOMAN", "WIFE", 0.40), ("MALE PERSON", "HUSBAND", 0.30),
    ("PERSON", "MALE PERSON", 0.15), ("CLOUD", "FOG", 0.25), ("CLOUD", "SKY", 0.10),
    ("HAIR", "FEATHER", 0.20), ("BELLY", "GUTS", 0.20), ("EARTH (SOIL)", "DUST", 0.15),
    ("SEA", "LAKE", 0.15), ("KNOW (SOMETHING)", "THINK", 0.15), ("RIGHT", "CORRECT (RIGHT)", 0.40),
    ("FIRE", "BURNING", 0.15), ("TREE", "WOOD", 0.30),
]

# Compostos plausíveis: (conceito, [modificador, núcleo], probabilidade)
COMPOUNDS = [
    ("BARK", ["TREE", "SKIN (HUMAN)"], 0.30), ("FEATHER", ["BIRD", "HAIR"], 0.30),
    ("RIVER", ["WATER", "ROAD"], 0.20), ("ASH", ["FIRE", "DUST"], 0.20),
    ("SUN", ["DAY (NOT NIGHT)", "EYE"], 0.15), ("ICE", ["HARD", "WATER"], 0.15),
    ("FOREST", ["MANY", "TREE"], 0.10), ("SEED", ["FLOWER", "EGG"], 0.10),
]

HUMAN_MALE = {"MALE PERSON", "FATHER", "HUSBAND"}
HUMAN_FEMALE = {"WOMAN", "MOTHER", "WIFE"}
HUMAN = HUMAN_MALE | HUMAN_FEMALE | {"PERSON", "CHILD (YOUNG HUMAN)", "CHILD (DESCENDANT)"}
LIQUIDS = {"WATER", "BLOOD", "RAIN (PRECIPITATION)", "SEA", "LAKE", "RIVER",
           "FAT (ORGANIC SUBSTANCE)", "SALT", "SAND", "DUST", "ASH", "EARTH (SOIL)"}
LONG = {"ROPE", "STICK", "SNAKE", "TREE", "TAIL", "ROAD", "RIVER", "WORM", "NECK", "LEG",
        "FOOT OR LEG", "HAIR"}

# WALS 118A (adjetivos predicativos) e 44A (gênero em pronomes)
WALS_118A = {"verbal": 151, "nonverbal": 132, "mixed": 103}
WALS_44A = {"1": 18, "2": 42, "3": 61, "6": 254}

POS_ABBR = {"noun": "n.", "verb": "v.", "adjective": "adj.", "pronoun": "pron.",
            "demonstrative": "dem.", "interrogative": "interr.", "quantifier": "quant.",
            "conjunction": "conj.", "adverb": "adv.", "adposition": "adp.",
            "numeral": "num.", "negation": "neg."}
TRANS_ABBR = {"transitive": "t.", "intransitive": "i.", "ditransitive": "bitr.",
              "stative": "estat."}


# ═══════════════════════════════════════════════════════════════════════════
# Leitura de conceitos
# ═══════════════════════════════════════════════════════════════════════════

def load_concepts(list_name: str, concepticon_dir: Optional[Path] = None) -> List[Dict]:
    """Lista embutida ou qualquer lista de um clone local do concepticon-data."""
    embedded = []
    for line in CONCEPTS_DATA.strip().splitlines():
        cid, g, eng, cat, field, lists, rank = (line.split("|") + [""] * 7)[:7]
        embedded.append({"id": cid, "gloss": g, "english": eng, "category": cat,
                         "field": field, "lists": lists,
                         "rank": int(rank) if rank else None})
    ranks = {c["id"]: c["rank"] for c in embedded}

    if list_name == "leipzig-jakarta":
        return sorted([c for c in embedded if "L" in c["lists"]], key=lambda c: c["rank"])
    if list_name == "swadesh-200":
        return [c for c in embedded if "S" in c["lists"]]
    if list_name == "all":
        return embedded

    if not concepticon_dir:
        raise SystemExit(f"Lista '{list_name}' não embutida; informe --concepticon "
                         "(clone de github.com/concepticon/concepticon-data)")
    data = concepticon_dir / "concepticondata"
    catalog = {r["ID"]: r for r in csv.DictReader(
        open(data / "concepticon.tsv", encoding="utf-8"), delimiter="\t")}
    path = data / "conceptlists" / f"{list_name}.tsv"
    if not path.exists():
        raise SystemExit(f"Lista não encontrada: {path}")
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        cid = r.get("CONCEPTICON_ID", "")
        if not cid or cid not in catalog:
            continue
        c = catalog[cid]
        out.append({"id": cid, "gloss": c["GLOSS"], "english": r.get("ENGLISH", c["GLOSS"].lower()),
                    "category": ONTOLOGY_TO_CODE.get(c["ONTOLOGICAL_CATEGORY"], "O"),
                    "field": c["SEMANTICFIELD"], "lists": "", "rank": ranks.get(cid)})
    return out


def function_class(gloss_: str) -> str:
    for cls, members in FUNCTION_CLASSES.items():
        if gloss_ in members:
            return cls
    return "adverb"


def visible_len(s: str) -> int:
    return sum(1 for ch in s if unicodedata.category(ch) != "Mn")


# ═══════════════════════════════════════════════════════════════════════════
# Construtor do léxico
# ═══════════════════════════════════════════════════════════════════════════

class LexiconBuilder:
    def __init__(self, engine: MorphologicalEngine, seed: Optional[int] = None):
        self.eng = engine
        self.ph = engine.ph
        self.cats = engine.cats
        self.rng = random.Random(seed)
        self.seed = seed
        self.used: set = set()
        self.notes: List[str] = []
        self.skeleton = engine.skeleton
        self.gender = self.cats.get("gender", {})

    # ── formas ───────────────────────────────────────────────────────────
    def _n_syllables(self, rank: Optional[int]) -> int:
        dist = self.eng.rules["root"]["syllables"]
        n = int(self.rng.choices(list(dist), [dist[k] for k in dist])[0])
        if rank is not None and rank <= 33 and n > 1 and self.rng.random() < 0.5:
            n -= 1  # lei de Zipf: palavras mais básicas tendem a ser mais curtas
        return n

    def _unique(self, make, accept=lambda r: True, tries: int = 60) -> Dict:
        r = make()
        for _ in range(tries):
            r = make()
            key = tuple(r["segments"])
            if key in self.used and self.rng.random() > 0.03:  # homófonos raros são realistas
                continue
            if not accept(r):
                continue
            break
        self.used.add(tuple(r["segments"]))
        return r

    def content_root(self, rank: Optional[int], final: Optional[str] = None) -> Dict:
        n = self._n_syllables(rank)
        accept = (lambda r: r["segments"][-1] == final or self.rng.random() > 0.7) if final else (lambda r: True)
        return self._unique(lambda: self.ph.generate_root(n), accept)

    def function_word(self, n: int = 1) -> Dict:
        def make():
            sylls = self.ph.generate_syllables(n)
            tones, form = self.ph._with_tones(sylls)
            return {"segments": [s for syl in sylls for s in syl], "syllables": sylls,
                    "tones": tones, "form": form}
        return self._unique(make)

    def word_from(self, segs: Segs) -> Optional[Dict]:
        """Transforma um afixo em palavra válida (para pronomes que ecoam a concordância)."""
        ep = self.eng.spec["sandhi"]["epenthetic_vowel"]
        for cand in (segs, segs + [ep], [ep] + segs):
            if cand and self.ph.is_valid(cand) and tuple(cand) not in self.used:
                self.used.add(tuple(cand))
                return {"segments": cand, "tones": [], "form": "".join(cand)}
        return None

    # ── gênero e classe ──────────────────────────────────────────────────
    def _gender_settings(self) -> Dict:
        g = self.gender
        if not g.get("grammaticalized"):
            return {}
        s: Dict = {}
        vowels = self.eng._short_plain_vowels()
        if (g.get("assignment") == "semantic_and_formal" and len(g["values"]) <= len(vowels)
                and len(g["values"]) <= 4 and not self.skeleton):
            finals = self.rng.sample(vowels, len(g["values"]))
            s["formal_finals"] = dict(zip(g["values"], finals))
        return s

    def assign_gender(self, c: Dict) -> Optional[str]:
        g = self.gender
        if not g.get("grammaticalized"):
            return None
        vals, gl = g["values"], c["gloss"]
        human, male, female = gl in HUMAN, gl in HUMAN_MALE, gl in HUMAN_FEMALE
        animal = c["field"] == "Animals" or gl == "ANIMAL"
        if self.rng.random() < 0.1 and not (male or female):
            return self.rng.choice(vals)  # exceções arbitrárias
        if vals == ["masculine", "feminine"]:
            return "masculine" if male else "feminine" if female else \
                self.rng.choices(vals, [0.55, 0.45])[0]
        if vals == ["masculine", "feminine", "neuter"]:
            if male or female:
                return "masculine" if male else "feminine"
            if human or animal:
                return self.rng.choice(["masculine", "feminine"])
            return self.rng.choices(vals, [0.25, 0.25, 0.5])[0]
        if vals == ["animate", "inanimate"]:
            return "animate" if human or animal else "inanimate"
        if vals == ["human", "animate", "inanimate"]:
            return "human" if human else "animate" if animal else "inanimate"

        cores = g.get("semantic_cores", {})
        wanted = []
        if male:
            wanted += ["male_humans", "humans"]
        if female:
            wanted += ["female_humans", "humans"]
        if human:
            wanted += ["humans", "male_humans"]
        if animal:
            wanted.append("animals")
        if c["field"] == "Agriculture and vegetation":
            wanted.append("plants")
        if gl in LIQUIDS:
            wanted.append("liquids_masses")
        if gl in LONG:
            wanted.append("long_objects")
        if c["field"] in ("Time", "Emotions and values", "Cognition") or gl in {"NAME", "SHADE"}:
            wanted.append("abstract")
        if c["field"] in ("The house", "Basic actions and technology", "Clothing and grooming"):
            wanted.append("artifacts")
        wanted.append("residual")
        for w in wanted:
            for v, core in cores.items():
                if core == w:
                    return v
        return vals[-1]

    def assign_class(self, domain: str, gender: Optional[str]) -> Optional[int]:
        n = max(1, self.eng.catdata["inflection_classes"].get(domain, 1))
        if n == 1:
            return None  # sem classes flexionais
        if gender and self.rng.random() < 0.6:  # declinação correlacionada com gênero
            return self.gender["values"].index(gender) % n
        return self.rng.randrange(n)

    # ── pronomes ─────────────────────────────────────────────────────────
    def build_pronouns(self) -> Dict:
        ag = self.cats.get("agreement", {})
        num = self.cats.get("number", {})
        numbers = (ag.get("numbers") if ag.get("grammaticalized") else
                   num.get("values") if num.get("grammaticalized") else ["singular", "plural"])
        clusivity = ag.get("clusivity") if ag.get("grammaticalized") else \
            self.rng.choices(["none", "inclusive_exclusive", "inclusive_only"], [120, 63, 5])[0]

        third_gender: List[str] = []
        gender_scope = "none"
        g = self.gender
        if g.get("grammaticalized") and g.get("basis") == "sex_based" and g.get("type") == "gender":
            code = self.rng.choices(list(WALS_44A), [WALS_44A[k] * (0.25 if k == "6" else 1)
                                                    for k in WALS_44A])[0]
            if code != "6":
                third_gender = [v for v in g["values"] if v in ("masculine", "feminine", "neuter")]
                gender_scope = "singular_only" if code == "3" else "all_numbers"

        cells: List[str] = []
        for n in numbers:
            persons = ["1", "2", "3"]
            if n != "singular" and clusivity == "inclusive_exclusive":
                persons = ["1incl", "1excl", "2", "3"]
            elif n != "singular" and clusivity == "inclusive_only":
                persons = ["1", "1incl", "2", "3"]
            for p in persons:
                if p == "3" and third_gender and (n == "singular" or gender_scope == "all_numbers"):
                    cells += [f"3.{n}.{gv}" for gv in third_gender]
                else:
                    cells.append(f"{p}.{n}")

        strategy = "suppletive" if self.rng.random() < 0.6 else "suffixed"
        echo = ag.get("grammaticalized") and self.rng.random() < 0.4
        agr_forms = {}
        if echo:  # pronomes que se parecem com os afixos de concordância
            for slot in self.eng.spec["affixes"]["verb"]:
                if slot["categories"] == ["agreement_A"]:
                    for key, segs in slot["forms"]["0"].items():
                        agr_forms[key.split("=", 1)[1]] = [s for s in segs if s != "+"]
        markers = {n: self.function_word(1)["segments"] for n in numbers if n != "singular"}

        table: Dict[str, Dict] = {}
        for cell in cells:
            parts = cell.split(".")
            person, n = parts[0], parts[1]
            base_cell = f"{person.replace('incl', '').replace('excl', '')}.singular"
            if strategy == "suffixed" and n != "singular" and base_cell + (
                    f".{parts[2]}" if len(parts) > 2 else "") in table and "incl" not in person:
                base = table[base_cell + (f".{parts[2]}" if len(parts) > 2 else "")]["segments"]
                w = self.word_from(base + markers[n])
                if w:
                    table[cell] = w
                    continue
            agr_key = f"{person}.{n}"
            if echo and agr_forms.get(agr_key):
                w = self.word_from(agr_forms[agr_key])
                if w:
                    table[cell] = w
                    continue
            table[cell] = self.function_word(1)
        return {"cells": {k: {"segments": v["segments"], "form": v["form"]} for k, v in table.items()},
                "numbers": numbers, "clusivity": clusivity,
                "third_person_gender": third_gender, "gender_scope": gender_scope,
                "plural_strategy": strategy, "echoes_agreement": bool(echo)}

    # ── entradas ─────────────────────────────────────────────────────────
    def _entry(self, c: Dict, pos: str, root: Dict, **extra) -> Dict:
        e = {"id": c["id"], "gloss": c["gloss"], "english": c["english"], "pos": pos,
             "skeleton": self.skeleton and pos in ("noun", "verb", "adjective")
             and root.get("form", "").count("-") > 0,
             "field": c["field"], "root": root["segments"], "form": root["form"],
             "tones": root.get("tones", []), "formation": "root"}
        e.update(extra)
        return e

    def build(self, concepts: List[Dict]) -> Dict:
        adj = self.rng.choices(list(WALS_118A), list(WALS_118A.values()))[0]
        gset = self._gender_settings()
        pronouns = self.build_pronouns()
        fm = self.eng.spec["free_markers"]
        case_vals = self.cats["case"].get("values", []) if self.cats["case"].get("grammaticalized") else []
        entries: Dict[str, Dict] = {}

        for c in concepts:
            gl, cat = c["gloss"], c["category"]
            if cat == "N":
                gender = self.assign_gender(c)
                final = gset.get("formal_finals", {}).get(gender)
                root = self.content_root(c["rank"], final)
                entries[gl] = self._entry(c, "noun", root, gender=gender,
                                          **{"class": self.assign_class("noun", gender)})
            elif cat == "V" or (cat == "A" and (adj == "verbal" or (adj == "mixed" and self.rng.random() < 0.5))):
                trans = ("ditransitive" if gl in DITRANSITIVE else "transitive" if gl in TRANSITIVE
                         else "stative" if cat == "A" else "intransitive")
                root = self.content_root(c["rank"])
                entries[gl] = self._entry(c, "verb", root, transitivity=trans,
                                          **{"class": self.assign_class("verb", None)})
            elif cat == "A":
                entries[gl] = self._entry(c, "adjective", self.content_root(c["rank"]))
            elif cat == "Q":
                if gl == "ONE" and "definiteness" in fm and "indefinite" in fm["definiteness"]["forms"] \
                        and fm["definiteness"]["realization"]["indefinite"] == "numeral_one":
                    segs = fm["definiteness"]["forms"]["indefinite"]
                    root = {"segments": segs, "form": "".join(segs)}
                    entries[gl] = self._entry(c, "numeral", root, formation="grammatical",
                                              note="mesma forma do artigo indefinido")
                else:
                    n = 1 if self.rng.random() < 0.6 else 2
                    entries[gl] = self._entry(c, "numeral", self.function_word(n))
            else:
                fc = function_class(gl)
                if fc == "pronoun":
                    cell = PRONOUN_CELLS[gl]
                    key = next((k for k in pronouns["cells"] if k.startswith(cell)), None)
                    if gl == "WE":
                        key = next((k for k in pronouns["cells"] if k.startswith(("1incl.plural",
                                    "1.plural"))), key)
                    p = pronouns["cells"].get(key) if key else None
                    if p:
                        entries[gl] = self._entry(c, "pronoun", p, formation="pronoun_system", cell=key)
                    continue
                if fc == "negation" and "negation" in fm:
                    segs = fm["negation"]["forms"]["negative"]
                    entries[gl] = self._entry(c, "negation", {"segments": segs, "form": "".join(segs)},
                                              formation="grammatical")
                    continue
                if fc == "negation" and self.cats["negation"]["realization"] in ("affix", "double"):
                    segs = next((s["forms"]["0"].get("negation=negative", []) for s in
                                 self.eng.spec["affixes"]["verb"] if "negation" in s["categories"]), [])
                    if segs:
                        entries[gl] = self._entry(c, "negation", {"segments": segs, "form": "".join(segs)},
                                                  formation="bound", note="expresso por afixo verbal")
                        continue
                if fc == "adposition":
                    case = next((x for x in ADPOSITION_CASES[gl] if x in case_vals), None)
                    if case:
                        entries[gl] = self._entry(c, "adposition", {"segments": [], "form": ""},
                                                  formation="case", expressed_by=case)
                        continue
                n = 2 if fc == "adverb" and self.rng.random() < 0.4 else 1
                entries[gl] = self._entry(c, fc, self.function_word(n))

        self._colexify(entries)
        self._compound(entries)
        for e in entries.values():
            self._principal_parts(e)
        assign_labels(list(entries.values()))
        return {"entries": list(entries.values()), "pronouns": pronouns,
                "settings": {"adjectives": adj, "compound_head": self.compound_head,
                             **({"gender_finals": gset["formal_finals"]} if gset.get("formal_finals") else {})}}

    def _colexify(self, entries: Dict[str, Dict]) -> None:
        for base, target, p in COLEXIFICATIONS:
            if base in entries and target in entries and self.rng.random() < p and \
                    entries[base]["pos"] == entries[target]["pos"]:
                b, t = entries[base], entries[target]
                for k in ("root", "form", "tones", "gender", "class"):
                    if k in b:
                        t[k] = b[k]
                t["formation"] = "colexification"
                t["colexified_with"] = base

    def _compound(self, entries: Dict[str, Dict]) -> None:
        self.compound_head = "final" if self.rng.random() < 0.6 else "initial"
        if self.skeleton:
            self.notes.append("raízes consonantais: compostos não gerados")
            return
        for target, parts, p in COMPOUNDS:
            if target not in entries or entries[target]["formation"] != "root":
                continue
            if not all(x in entries and entries[x]["root"] for x in parts) or self.rng.random() >= p:
                continue
            # a 2ª parte da receita é o núcleo (árvore + pele = 'casca', um tipo de pele)
            head, mod = entries[parts[1]], entries[parts[0]]
            order = [mod, head] if self.compound_head == "final" else [head, mod]
            morphs = [{"segs": list(order[0]["root"]), "role": "root", "label": "", "sep": "-"},
                      {"segs": list(order[1]["root"]), "role": "suffix", "label": "", "sep": "-"}]
            morphs, ok, _ = self.eng.resolve(morphs)
            if not ok:
                continue
            segs = [s for m in morphs for s in m["segs"]]
            t = entries[target]
            t.update(root=segs, form="".join(segs), tones=[], formation="compound",
                     parts=[order[0]["gloss"], order[1]["gloss"]])
            if t["pos"] == "noun" and head.get("gender"):
                t["gender"] = head["gender"]

    def _principal_parts(self, e: Dict) -> None:
        pos = e["pos"]
        if pos not in ("noun", "verb") or not e["root"]:
            # Forma corrida (sem pontos de sílaba), como a das palavras flexionadas;
            # mantém a forma original só para tons (que vêm por sílaba) e raízes consonantais.
            keep = e.get("tones") or "-" in e["form"]
            e["citation"] = e["form"] if keep else "".join(e["root"])
            e["inflections"] = []
            return
        lex = {"root": e["root"], "form": e["form"], "tones": e.get("tones", []),
               "class": e.get("class") or 0, "gender": e.get("gender")}
        domain = pos
        base = self.eng.inflect(lex, domain)
        e["citation"] = base["surface"]  # sem partículas/artigos: só a palavra
        feats: List[Dict[str, str]] = []
        if domain == "noun":
            num = self.cats["number"]
            if num.get("grammaticalized"):
                feats.append({"number": "plural"})
            case = self.cats["case"]
            if case.get("grammaticalized") and len(case["values"]) > 1:
                feats.append({"case": case["values"][1]})
        else:
            ag = self.cats.get("agreement", {})
            if ag.get("grammaticalized") and "A" in ag["arguments"]:
                feats.append({"agreement_A": "1.singular"})
            tense = self.cats["tense"]
            past = next((v for v in tense.get("values", []) if "past" in v and v != "non_past"), None)
            if tense.get("grammaticalized") and past:
                feats.append({"tense": past})
            elif self.cats["aspect"].get("grammaticalized"):
                other = [v for v in self.cats["aspect"]["values"] if v != self.cats["aspect"]["default"]]
                feats.append({"aspect": other[0]})
        e["inflections"] = []
        for f in feats:
            r = self.eng.inflect(lex, domain, f)
            e["inflections"].append({"gloss": r["gloss"], "form": r["phrase"], "valid": r["valid"]})


# ═══════════════════════════════════════════════════════════════════════════
# Dicionário (Markdown) e exibição
# ═══════════════════════════════════════════════════════════════════════════

def short(english: str) -> str:
    """Remove o detalhamento entre parênteses: 'feather (larger feathers...)' → 'feather'."""
    return english.split(" (")[0]


def assign_labels(entries: List[Dict]) -> None:
    """
    Rótulo curto de cada entrada ('child', 'right'). Quando dois conceitos teriam o
    mesmo rótulo, como CHILD (YOUNG HUMAN) e CHILD (DESCENDANT), ambos passam a usar
    o gloss completo do Concepticon: 'child (young human)' e 'child (descendant)'.
    """
    counts: Dict[str, int] = {}
    for e in entries:
        k = short(e["english"]).lower()
        counts[k] = counts.get(k, 0) + 1
    for e in entries:
        k = short(e["english"]).lower()
        e["label"] = e["gloss"].lower() if counts[k] > 1 else short(e["english"])


def label(e: Dict) -> str:
    return e.get("label") or short(e["english"])


def pos_label(e: Dict) -> str:
    lab = POS_ABBR.get(e["pos"], e["pos"])
    if e["pos"] == "verb":
        lab = f"v.{TRANS_ABBR.get(e.get('transitivity', ''), '')}"
    return lab


def entry_line(e: Dict) -> str:
    extra = []
    if e.get("gender"):
        extra.append(gloss(e["gender"]) or e["gender"])
    if e.get("class") is not None and e["pos"] in ("noun", "verb"):
        extra.append(f"classe {e['class'] + 1}")
    meta = f" ({'; '.join(extra)})" if extra else ""
    infl = "; ".join(f"{i['gloss']}: {i['form']}" for i in e.get("inflections", []) if i["gloss"])
    note = ""
    if e["formation"] == "compound":
        note = f" ← composto de '{e['parts'][0].lower()}' + '{e['parts'][1].lower()}'"
    elif e["formation"] == "colexification":
        note = f" = mesma palavra que {e['colexified_with'].lower()}"
    elif e.get("note"):
        note = f" — {e['note']}"
    root = "".join(e["root"]) if not e.get("skeleton") else "-".join(e["root"])
    plain = "".join(ch for ch in e["citation"] if ch not in "˥˦˧˨˩.")  # sem tons nem sílabas
    raiz = f" [raiz {root}]" if e["pos"] in ("noun", "verb") and root and root != plain else ""
    return (f"**{e['citation']}**{raiz} *{pos_label(e)}*{meta} '{label(e)}'"
            + (f" — {infl}" if infl else "") + note)


def write_dictionary(path: Path, data: Dict) -> None:
    lines = ["# Dicionário", ""]
    s = data["settings"]
    lines += [f"- Adjetivos: {s['adjectives']} (WALS 118A)",
              f"- Núcleo dos compostos: {s['compound_head']}"]
    if s.get("gender_finals"):
        lines.append("- Gênero previsível pela vogal final: " +
                     ", ".join(f"{g} → -{v}" for g, v in s["gender_finals"].items()))
    lines += ["", "## Pronomes", "", "| Pessoa | Forma |", "|---|---|"]
    for cell, p in data["pronouns"]["cells"].items():
        lines.append(f"| {gloss(cell)} | {p['form']} |")

    lines += ["", "## Entradas", ""]
    bound = [e for e in data["entries"] if not e["citation"]]
    words = sorted([e for e in data["entries"] if e["citation"]], key=lambda e: e["citation"])
    for e in words:
        lines.append(f"- {entry_line(e)}")
    if bound:
        lines += ["", "## Conceitos expressos sem palavra própria", ""]
        for e in bound:
            how = f"caso {e['expressed_by']}" if e.get("expressed_by") else e.get("note", "")
            lines.append(f"- '{e['english']}' → {how}")

    lines += ["", "## Índice por significado", "", "| Significado | Palavra |", "|---|---|"]
    for e in sorted(data["entries"], key=lambda e: label(e).lower()):
        word = e["citation"] or (f"(caso {e['expressed_by']})" if e.get("expressed_by") else "—")
        lines.append(f"| {label(e)} | {word} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(data: Dict) -> None:
    entries = data["entries"]
    by_pos: Dict[str, int] = {}
    for e in entries:
        by_pos[e["pos"]] = by_pos.get(e["pos"], 0) + 1
    print(f"\nLÉXICO: {len(entries)} entradas — " + ", ".join(f"{k} {v}" for k, v in by_pos.items()))
    s = data["settings"]
    print(f"  adjetivos: {s['adjectives']}; núcleo dos compostos: {s['compound_head']}")
    if s.get("gender_finals"):
        print("  gênero pela vogal final: " + ", ".join(f"{g} -{v}" for g, v in s["gender_finals"].items()))

    p = data["pronouns"]
    print(f"\nPRONOMES (plural: {p['plural_strategy']}"
          + (", ecoam a concordância" if p["echoes_agreement"] else "") + ")")
    print("  " + "  ".join(f"{gloss(k)} {v['form']}" for k, v in p["cells"].items()))

    formations = [e for e in entries if e["formation"] in ("compound", "colexification")]
    if formations:
        print("\nCOMPOSTOS E COLEXIFICAÇÕES")
        for e in formations:
            if e["formation"] == "compound":
                print(f"  {short(e['english'])}: {e['citation']} ← {e['parts'][0].lower()} + {e['parts'][1].lower()}")
            else:
                print(f"  {e['gloss'].lower()} = {e['colexified_with'].lower()}: {e['citation']}")

    print("\nAMOSTRA")
    for e in entries[:20]:
        print("  " + entry_line(e).replace("**", "").replace("*", ""))


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def _load(path: Path, hint: str) -> Dict:
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}\nRode antes: {hint}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera o léxico da conlang.")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--list", default="leipzig-jakarta",
                    help="leipzig-jakarta | swadesh-200 | all | nome de uma lista do Concepticon")
    ap.add_argument("--concepticon", type=Path, default=DEFAULT_CONCEPTICON,
                    help="clone local do concepticon-data (só para listas não embutidas)")
    ap.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    ap.add_argument("--phonotactics", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    ap.add_argument("--morphology", type=Path, default=DEFAULT_MORPHOLOGY)
    ap.add_argument("--morph", type=Path, default=DEFAULT_TYPOLOGY)
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
    args = ap.parse_args()

    inventory = _load(args.inventory, "phonemic_inventory.py")
    rules = _load(args.phonotactics, "phonotactics.py")
    categories = _load(args.categories, "grammatical_categories.py")
    morphology = _load(args.morphology, "morphological_engine.py")
    typology = json.loads(args.morph.read_text(encoding="utf-8")) if args.morph.exists() else {}

    eng = MorphologicalEngine.load(morphology, inventory, rules, categories, typology)
    concepts = load_concepts(args.list, args.concepticon if args.concepticon.exists() else None)
    builder = LexiconBuilder(eng, seed=args.seed)
    data = builder.build(concepts)
    data["metadata"] = {"seed": args.seed, "list": args.list, "notes": builder.notes,
                        "source": "Concepticon (List et al.)"}

    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_dictionary(args.dictionary, data)
    print_summary(data)
    print(f"\n[OK] Léxico salvo em '{args.output}' e dicionário em '{args.dictionary}'.")


if __name__ == "__main__":
    main()
