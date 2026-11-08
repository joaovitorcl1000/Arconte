"""
Módulo — Inventário Fonêmico.

Seleciona, a partir do universo de segmentos do PHOIBLE, o inventário de
consoantes, vogais e tons de UMA conlang, e salva em phonemic_inventory.json
(consumido pela fonotática).

Dois modos de geração:
  feature  — constrói o inventário segmento a segmento, ponderando pela
             frequência translinguística e pela economia de traços
             (Clements 2003): candidatos que formam série com segmentos já
             presentes (vozeamento, aspiração, ejetividade, comprimento,
             nasalidade) são favorecidos, sobretudo se aquele contraste já é
             usado no inventário (p t k + b → d ɡ; a i u + aː → iː uː).
  real     — parte do inventário de uma língua real do PHOIBLE e o modifica.

Em ambos, uma etapa de reparo aplica universais implicacionais
(ex.: /kʰ/ → /k/, /b/ → /p/, /ŋ/ → /n/, /ã/ → /a/).

Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python phonemic_inventory.py                       # modo feature, aleatório
    python phonemic_inventory.py --seed 42
    python phonemic_inventory.py --mode real --seed 7
    python phonemic_inventory.py --consonants 22 --vowels 5 --tones
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Caminhos padrão (estrutura conlang/<módulo>/)
# ═══════════════════════════════════════════════════════════════════════════

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_PHOIBLE = ROOT / "ipa_database" / "phoible.csv"
DEFAULT_MORPH = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_OUTPUT = HERE / "phonemic_inventory.json"
CACHE_PATH = HERE / ".cache" / "phoible_stats.json"
CACHE_VERSION = 1

FIRST_FEATURE_COLUMN = "tone"  # no CSV, os traços vão de "tone" até "click"

# ═══════════════════════════════════════════════════════════════════════════
# Universais implicacionais
# ═══════════════════════════════════════════════════════════════════════════

# Modificadores cuja presença implica a forma sem eles:
# aspiração, labialização, palatalização, velarização, faringalização,
# comprimento, ejetividade, glotalização, nasalidade, voz rangida/soprosa,
# fortis, pré-nasalização.
MARKED_MODIFIERS = set("ʰʷʲˠˤːˑʼˀᵐⁿᵑᶮ") | {"\u0303", "\u0330", "\u0324", "\u0348"}

# Implicações por símbolo que não se deduzem pelos modificadores
SYMBOL_IMPLICATIONS = {"ŋ": "n", "ɲ": "n", "ɳ": "n"}

# Implicações por inversão de traço: (condições, traço a inverter → valor)
FEATURE_IMPLICATIONS = [
    # obstruinte sonora → surda correspondente (b → p, z → s)
    ({"periodicGlottalSource": "+", "sonorant": "-", "syllabic": "-",
      "loweredLarynxImplosive": "-"},
     {"periodicGlottalSource": "-"}),
    # implosiva → oclusiva sonora (ɓ → b)
    ({"loweredLarynxImplosive": "+"}, {"loweredLarynxImplosive": "-"}),
]


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def strip_marked_modifiers(ipa: str) -> str:
    return "".join(ch for ch in ipa if ch not in MARKED_MODIFIERS)


# Traços que definem "séries" (contrastes que atravessam vários pontos de articulação)
SERIES_FEATURES = ["periodicGlottalSource", "spreadGlottis", "constrictedGlottis",
                   "raisedLarynxEjective", "loweredLarynxImplosive", "long", "nasal"]


def skeleton(ipa: str) -> str:
    """Remove todos os diacríticos e modificadores: t̪ → t, sʷ → s, kʰ → k."""
    return "".join(ch for ch in ipa if unicodedata.category(ch) not in ("Mn", "Lm"))


def is_diphthong(ipa: str) -> bool:
    """Vogal com 2+ letras-base (ie, ou, oːu) = ditongo."""
    return sum(1 for ch in ipa if unicodedata.category(ch) == "Ll") >= 2


# ═══════════════════════════════════════════════════════════════════════════
# Estatísticas do PHOIBLE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Segment:
    ipa: str
    seg_class: str              # consonant | vowel | tone
    vector: Tuple[str, ...]     # valores de traços, na ordem de PhoibleStats.features
    n_langs: int = 0


@dataclass
class Language:
    glottocode: str
    name: str
    segments: List[str]


@dataclass
class PhoibleStats:
    features: List[str]
    segments: Dict[str, Segment]
    languages: List[Language]
    partners: Dict[str, Set[str]] = field(default_factory=dict)
    by_vector: Dict[Tuple[str, ...], str] = field(default_factory=dict)

    @property
    def n_languages(self) -> int:
        return len(self.languages)

    def contrast(self, a: str, b: str) -> frozenset:
        """Conjunto de traços em que dois segmentos diferem."""
        va, vb = self.segments[a].vector, self.segments[b].vector
        return frozenset(f for f, x, y in zip(self.features, va, vb) if x != y)

    def frequency(self, ipa: str) -> float:
        return self.segments[ipa].n_langs / self.n_languages

    def feat(self, ipa: str, name: str) -> str:
        return self.segments[ipa].vector[self.features.index(name)]

    # ── índices derivados ────────────────────────────────────────────────
    def build_indexes(self) -> None:
        """Parceiros de série (diferem só em SERIES_FEATURES) e busca por vetor."""
        mask = {self.features.index(f) for f in SERIES_FEATURES}
        buckets: Dict[Tuple, List[str]] = defaultdict(list)
        for ipa, seg in self.segments.items():
            key = (seg.seg_class,) + tuple("*" if i in mask else v
                                           for i, v in enumerate(seg.vector))
            buckets[key].append(ipa)
        self.partners = defaultdict(set)
        for group in buckets.values():
            if len(group) > 1:
                for ipa in group:
                    self.partners[ipa].update(g for g in group if g != ipa)

        best: Dict[Tuple[str, ...], str] = {}
        for ipa, seg in self.segments.items():
            cur = best.get(seg.vector)
            if cur is None or seg.n_langs > self.segments[cur].n_langs:
                best[seg.vector] = ipa
        self.by_vector = best


def build_stats(csv_path: Path) -> PhoibleStats:
    """
    Lê o phoible.csv:
      • ignora segmentos marginais e linhas sem Glottocode;
      • mantém UM inventário por Glottocode (o de menor InventoryID),
        para que línguas com várias fontes não pesem mais;
      • frequência = fração de línguas distintas que têm o segmento.
    """
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        features = cols[cols.index(FIRST_FEATURE_COLUMN):]

        segments: Dict[str, Segment] = {}
        inventories: Dict[int, Dict] = {}
        for row in reader:
            glotto = row["Glottocode"]
            if not glotto or glotto == "NA" or row["Marginal"] == "TRUE":
                continue
            ipa = nfd(row["Phoneme"])
            if ipa not in segments:
                segments[ipa] = Segment(ipa, row["SegmentClass"],
                                        tuple(row[c] for c in features))
            inv_id = int(row["InventoryID"])
            inv = inventories.setdefault(
                inv_id, {"glottocode": glotto, "name": row["LanguageName"], "segments": []})
            inv["segments"].append(ipa)

    chosen: Dict[str, Language] = {}
    for inv_id in sorted(inventories):
        inv = inventories[inv_id]
        if inv["glottocode"] not in chosen:
            chosen[inv["glottocode"]] = Language(
                inv["glottocode"], inv["name"], list(dict.fromkeys(inv["segments"])))

    languages = list(chosen.values())
    for lang in languages:
        for ipa in lang.segments:
            segments[ipa].n_langs += 1

    return PhoibleStats(features, segments, languages)


def load_stats(csv_path: Path, rebuild: bool = False) -> PhoibleStats:
    """Carrega do cache JSON; reconstrói se o CSV mudou ou se pedido."""
    mtime = csv_path.stat().st_mtime
    if CACHE_PATH.exists() and not rebuild:
        try:
            data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            if data.get("version") == CACHE_VERSION and data.get("source_mtime") == mtime:
                stats = PhoibleStats(
                    features=data["features"],
                    segments={k: Segment(k, v["class"], tuple(v["vector"]), v["n_langs"])
                              for k, v in data["segments"].items()},
                    languages=[Language(**l) for l in data["languages"]],
                )
                stats.build_indexes()
                return stats
        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # cache corrompido: reconstrói

    print(f"[..] Processando {csv_path.name} (só na primeira execução)...")
    stats = build_stats(csv_path)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps({
        "version": CACHE_VERSION,
        "source_mtime": mtime,
        "features": stats.features,
        "segments": {k: {"class": s.seg_class, "vector": list(s.vector), "n_langs": s.n_langs}
                     for k, s in stats.segments.items()},
        "languages": [l.__dict__ for l in stats.languages],
    }, ensure_ascii=False), encoding="utf-8")
    stats.build_indexes()
    return stats


# ═══════════════════════════════════════════════════════════════════════════
# Classificação articulatória (rótulos de conveniência a partir dos traços)
# ═══════════════════════════════════════════════════════════════════════════

def _first(v: str) -> str:
    return v.split(",")[0]


def _last(v: str) -> str:
    return v.split(",")[-1]


def classify_consonant(f: Dict[str, str]) -> Tuple[str, str]:
    """Retorna (modo, ponto). Modo usa a fase final; ponto, a inicial."""
    m = {k: _last(v) for k, v in f.items()}
    p = {k: _first(v) for k, v in f.items()}

    if m["click"] == "+":
        manner = "click"
    elif m["nasal"] == "+" and m["sonorant"] == "+":
        manner = "nasal"
    elif m["trill"] == "+" or m["tap"] == "+":
        manner = "rhotic"
    elif m["lateral"] == "+" and m["approximant"] == "+":
        manner = "lateral"
    elif m["approximant"] == "+":
        manner = "approximant"
    elif m["continuant"] == "-" and m["delayedRelease"] == "+":
        manner = "affricate"
    elif m["continuant"] == "+":
        manner = "fricative"
    else:
        manner = "stop"

    if p["labial"] == "+" and p["dorsal"] == "+":
        place = "labial-velar"
    elif p["dorsal"] == "+" and p["front"] == "+":
        place = "palatal"
    elif p["labial"] == "+":
        place = "labial"
    elif p["coronal"] == "+":
        place = "coronal"
    elif p["dorsal"] == "+":
        place = "uvular" if p["back"] == "+" and p["high"] != "+" else "velar"
    else:
        place = "laryngeal"
    return manner, place


def classify_vowel(f: Dict[str, str]) -> Dict[str, object]:
    g = {k: _first(v) for k, v in f.items()}
    height = "high" if g["high"] == "+" else "low" if g["low"] == "+" else "mid"
    backness = "front" if g["front"] == "+" else "back" if g["back"] == "+" else "central"
    return {"height": height, "backness": backness, "rounded": g["round"] == "+",
            "long": g["long"] == "+", "nasal": g["nasal"] == "+"}


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GeneratorOptions:
    mode: str = "feature"            # feature | real
    seed: Optional[int] = None
    n_consonants: Optional[int] = None
    n_vowels: Optional[int] = None
    tones: Optional[bool] = None     # None = sorteia pela proporção real
    allow_diphthongs: bool = False
    min_languages: int = 10          # ignora segmentos em < N línguas
    commonness: float = 2.0          # expoente da frequência (>1 favorece sons comuns)
    economy_weight: float = 1.5      # força da economia de traços
    mutation_rate: float = 0.15      # modo real: fração do inventário trocada
    repair_add: float = 0.75         # violação → adiciona o segmento implicado
    repair_remove: float = 0.20      # violação → remove o segmento marcado
    # restante (0.05) → tolera a lacuna (ex.: árabe tem /b/ sem /p/)


class InventoryGenerator:
    def __init__(self, stats: PhoibleStats, opts: GeneratorOptions,
                 morph_requirements: Optional[Dict] = None):
        self.s = stats
        self.o = opts
        self.req = morph_requirements or {}
        self.rng = random.Random(opts.seed)
        self.log: List[str] = []

    # ── auxiliares ───────────────────────────────────────────────────────
    def _eligible(self, ipa: str) -> bool:
        seg = self.s.segments[ipa]
        if "|" in ipa:  # transcrição ambígua no PHOIBLE (ex: t̪|t)
            return False
        if seg.seg_class == "vowel" and not self.o.allow_diphthongs and is_diphthong(ipa):
            return False
        return True

    def _candidates(self, seg_class: str) -> List[str]:
        return [ipa for ipa, seg in self.s.segments.items()
                if seg.seg_class == seg_class and seg.n_langs >= self.o.min_languages
                and self._eligible(ipa)]

    def _class_of(self, inv: Iterable[str], seg_class: str) -> List[str]:
        return [x for x in inv if self.s.segments[x].seg_class == seg_class]

    def _sample_targets(self) -> Tuple[int, int, Optional[Language]]:
        """Sorteia (nº consoantes, nº vogais) de uma língua real: preserva a correlação."""
        pool = []
        for lang in self.s.languages:
            nc = sum(1 for x in lang.segments if self.s.segments[x].seg_class == "consonant")
            nv = sum(1 for x in lang.segments
                     if self.s.segments[x].seg_class == "vowel" and self._eligible(x))
            if nc >= 6 and nv >= 2:
                pool.append((nc, nv, lang))
        nc, nv, lang = self.rng.choice(pool)
        nc = self.o.n_consonants or nc
        nv = self.o.n_vowels or nv
        nc = max(nc, self.req.get("min_consonants", 0))
        nv = max(nv, self.req.get("min_vowels", 0))
        return nc, nv, lang

    def _used_contrasts(self, inv: Set[str]) -> Set[frozenset]:
        used = set()
        for x in inv:
            for y in self.s.partners.get(x, ()):
                if y in inv:
                    used.add(self.s.contrast(x, y))
        return used

    def _score(self, ipa: str, inv: Set[str], used: Set[frozenset]) -> float:
        """
        frequência × economia × penalidade
          economia: cada parceiro de série presente conta 1, ou 2 se o
                    contraste já é usado em outro par do inventário;
          penalidade: mesmo esqueleto de um segmento presente sem ser
                      parceiro de série (t̪ ao lado de t, s̺ ao lado de s).
        """
        economy = 0
        partners = self.s.partners.get(ipa, set())
        for p in partners:
            if p in inv:
                economy += 2 if self.s.contrast(ipa, p) in used else 1
        score = self.s.frequency(ipa) ** self.o.commonness
        score *= 1.0 + self.o.economy_weight * economy
        sk = skeleton(ipa)
        if any(skeleton(x) == sk and x not in partners for x in inv):
            score *= 0.01
        return score

    def _grow(self, inv: Set[str], seg_class: str, target: int,
              exclude: Set[str] = frozenset()) -> None:
        pool = [c for c in self._candidates(seg_class) if c not in inv and c not in exclude]
        while len(self._class_of(inv, seg_class)) < target and pool:
            used = self._used_contrasts(inv)
            weights = [self._score(c, inv, used) for c in pool]
            pick = self.rng.choices(pool, weights=weights, k=1)[0]
            inv.add(pick)
            pool.remove(pick)

    def _seed_vowels(self) -> List[str]:
        """Triângulo vocálico básico: vogal baixa, alta anterior, alta posterior."""
        def best(cond) -> Optional[str]:
            c = [v for v in self._candidates("vowel")
                 if cond({k: _first(x) for k, x in zip(self.s.features, self.s.segments[v].vector)})
                 and strip_marked_modifiers(v) == v]
            return max(c, key=lambda v: self.s.segments[v].n_langs) if c else None
        seeds = [best(lambda f: f["low"] == "+"),
                 best(lambda f: f["high"] == "+" and f["front"] == "+" and f["round"] != "+"),
                 best(lambda f: f["high"] == "+" and f["back"] == "+" and f["round"] == "+")]
        return [s for s in seeds if s]

    # ── universais implicacionais ────────────────────────────────────────
    def _implied_by(self, ipa: str) -> List[str]:
        seg = self.s.segments[ipa]
        out: List[str] = []

        base = strip_marked_modifiers(ipa)
        if base != ipa and base in self.s.segments:
            out.append(base)

        if ipa in SYMBOL_IMPLICATIONS:
            out.append(SYMBOL_IMPLICATIONS[ipa])

        feats = dict(zip(self.s.features, seg.vector))
        for cond, flip in FEATURE_IMPLICATIONS:
            if all(feats.get(k) == v for k, v in cond.items()):
                new = dict(feats, **flip)
                target = self.s.by_vector.get(tuple(new[f] for f in self.s.features))
                if target and target != ipa:
                    out.append(target)

        return [x for x in dict.fromkeys(out)
                if x in self.s.segments and self.s.segments[x].seg_class == seg.seg_class]

    def _repair(self, inv: Set[str]) -> None:
        tolerated: Set[Tuple[str, str]] = set()
        for _ in range(100):
            changed = False
            for ipa in sorted(inv):
                if ipa not in inv:
                    continue
                for needed in self._implied_by(ipa):
                    if needed in inv or (ipa, needed) in tolerated:
                        continue
                    r = self.rng.random()
                    if r < self.o.repair_add:
                        inv.add(needed)
                        self.log.append(f"+{needed} (implicado por /{ipa}/)")
                    elif r < self.o.repair_add + self.o.repair_remove:
                        inv.discard(ipa)
                        self.log.append(f"-{ipa} (sem /{needed}/)")
                    else:
                        tolerated.add((ipa, needed))
                        self.log.append(f"~{ipa} sem /{needed}/ (lacuna tolerada)")
                    changed = True
                    break
            if not changed:
                return

    # ── tons ─────────────────────────────────────────────────────────────
    def _pick_tones(self, base: Optional[Language] = None) -> List[str]:
        def tones_of(lang: Language) -> List[str]:
            return [x for x in lang.segments if self.s.segments[x].seg_class == "tone"]

        tonal = [l for l in self.s.languages if tones_of(l)]
        want = self.o.tones
        if self.req.get("tones"):
            want = True
        if base is not None:  # modo real: herda o sistema tonal da língua-base
            if want is None:
                want = bool(tones_of(base))
            if want and tones_of(base):
                return tones_of(base)
        if want is None:
            want = self.rng.random() < len(tonal) / self.s.n_languages
        if not want or not tonal:
            return []
        lang = self.rng.choice(tonal)
        self.log.append(f"tons copiados do sistema de {lang.name} ({lang.glottocode})")
        return [x for x in lang.segments if self.s.segments[x].seg_class == "tone"]

    # ── modos ────────────────────────────────────────────────────────────
    def generate(self) -> Dict:
        nc, nv, ref = self._sample_targets()
        inv: Set[str] = set()
        base_lang: Optional[Language] = None
        removed: Set[str] = set()

        if self.o.mode == "real":
            base_lang = self.rng.choice(self.s.languages)
            inv = {x for x in base_lang.segments
                   if self.s.segments[x].seg_class in ("consonant", "vowel") and self._eligible(x)}
            nc = self.o.n_consonants or len(self._class_of(inv, "consonant"))
            nv = self.o.n_vowels or len(self._class_of(inv, "vowel"))
            nc = max(nc, self.req.get("min_consonants", 0))
            nv = max(nv, self.req.get("min_vowels", 0))
            k = max(1, round(self.o.mutation_rate * len(inv)))
            removable = sorted(inv)
            weights = [1.0 - self.s.frequency(x) + 0.05 for x in removable]
            removed = set(self.rng.choices(removable, weights=weights, k=k))
            for x in sorted(removed):
                inv.discard(x)
                self.log.append(f"-{x} (mutação)")
        else:
            nv_seed = self._seed_vowels()[:max(nv, 2)]
            inv.update(nv_seed)

        before = set(inv)
        self._grow(inv, "vowel", nv, exclude=removed)
        self._grow(inv, "consonant", nc, exclude=removed)
        if self.o.mode == "real":
            for x in sorted(inv - before):
                self.log.append(f"+{x} (mutação)")

        self._repair(inv)
        tones = self._pick_tones(base_lang)
        return self._export(inv, tones, nc, nv, base_lang or ref)

    # ── saída ────────────────────────────────────────────────────────────
    def _export(self, inv: Set[str], tones: List[str], nc: int, nv: int,
                ref: Optional[Language]) -> Dict:
        manner_order = ["stop", "affricate", "fricative", "nasal", "rhotic",
                        "lateral", "approximant", "click"]
        place_order = ["labial", "coronal", "palatal", "velar", "labial-velar",
                       "uvular", "laryngeal"]

        consonants, vowels = [], []
        for ipa in inv:
            seg = self.s.segments[ipa]
            feats = dict(zip(self.s.features, seg.vector))
            entry = {"ipa": ipa, "frequency": round(self.s.frequency(ipa), 4)}
            if seg.seg_class == "consonant":
                manner, place = classify_consonant(feats)
                consonants.append({**entry, "manner": manner, "place": place, "features": feats})
            else:
                vowels.append({**entry, **classify_vowel(feats), "features": feats})

        consonants.sort(key=lambda c: (manner_order.index(c["manner"]),
                                       place_order.index(c["place"]), c["ipa"]))
        h = {"high": 0, "mid": 1, "low": 2}
        b = {"front": 0, "central": 1, "back": 2}
        vowels.sort(key=lambda v: (v["long"], v["nasal"], h[v["height"]], b[v["backness"]], v["ipa"]))

        return {
            "consonants": consonants,
            "vowels": vowels,
            "tones": [{"ipa": t, "frequency": round(self.s.frequency(t), 4)} for t in tones],
            "counts": {"consonants": len(consonants), "vowels": len(vowels), "tones": len(tones)},
            "metadata": {
                "mode": self.o.mode,
                "seed": self.o.seed,
                "targets": {"consonants": nc, "vowels": nv},
                "reference_language": ({"name": ref.name, "glottocode": ref.glottocode}
                                       if ref else None),
                "morphology_requirements": self.req,
                "changes": self.log,
                "phoible_languages": self.s.n_languages,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# Integração com a tipologia morfológica
# ═══════════════════════════════════════════════════════════════════════════

def read_morph_requirements(path: Path) -> Dict:
    """Lê morphological_typology.json e traduz em exigências para o inventário."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    procs = set(data.get("active_processes", []))
    req: Dict = {}
    if "tonal_morphology" in procs:
        req["tones"] = True
    if "apophony" in procs:
        req["min_vowels"] = 5       # alternâncias precisam de contrastes vocálicos
    if "transfixation" in procs:
        req["min_consonants"] = 18  # raízes CCC precisam de variedade consonantal
    return req


# ═══════════════════════════════════════════════════════════════════════════
# Exibição
# ═══════════════════════════════════════════════════════════════════════════

def _visible_len(text: str) -> int:
    """Comprimento na tela: diacríticos combinantes não ocupam coluna."""
    return sum(1 for ch in text if unicodedata.category(ch) != "Mn")


def _pad(text: str, width: int) -> str:
    return text + " " * max(0, width - _visible_len(text))


def print_summary(result: Dict) -> None:
    cons = result["consonants"]
    places = [p for p in ["labial", "coronal", "palatal", "velar", "labial-velar",
                          "uvular", "laryngeal"] if any(c["place"] == p for c in cons)]
    manners = list(dict.fromkeys(c["manner"] for c in cons))
    cells = [" ".join(c["ipa"] for c in cons if c["manner"] == m and c["place"] == p)
             for m in manners for p in places]
    width = max([len(p) for p in places] + [_visible_len(c) for c in cells]) + 2

    print(f"\nCONSOANTES ({len(cons)})")
    print(" " * width + "".join(p.ljust(width) for p in places))
    for m in manners:
        row = m.ljust(width)
        for p in places:
            cell = " ".join(c["ipa"] for c in cons if c["manner"] == m and c["place"] == p)
            row += _pad(cell, width)
        print(row.rstrip())

    print(f"\nVOGAIS ({len(result['vowels'])})")
    print("  " + "  ".join(v["ipa"] for v in result["vowels"]))
    if result["tones"]:
        print(f"\nTONS ({len(result['tones'])})")
        print("  " + "  ".join(t["ipa"] for t in result["tones"]))

    meta = result["metadata"]
    if meta["reference_language"]:
        label = "Base" if meta["mode"] == "real" else "Tamanho inspirado em"
        print(f"\n{label}: {meta['reference_language']['name']}")
    if meta["changes"]:
        print("Alterações: " + ", ".join(meta["changes"]))


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    ap = argparse.ArgumentParser(description="Gera o inventário fonêmico da conlang.")
    ap.add_argument("--mode", choices=["feature", "real"], default="feature")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--consonants", type=int, help="força o nº de consoantes")
    ap.add_argument("--vowels", type=int, help="força o nº de vogais")
    tone = ap.add_mutually_exclusive_group()
    tone.add_argument("--tones", dest="tones", action="store_true", default=None)
    tone.add_argument("--no-tones", dest="tones", action="store_false")
    ap.add_argument("--diphthongs", action="store_true", help="permite ditongos como fonemas")
    ap.add_argument("--mutation", type=float, default=0.15, help="modo real: taxa de mutação")
    ap.add_argument("--economy", type=float, default=1.5, help="peso da economia de traços")
    ap.add_argument("--commonness", type=float, default=2.0,
                    help="expoente da frequência (1 = proporcional; maior = sons mais comuns)")
    ap.add_argument("--phoible", type=Path, default=DEFAULT_PHOIBLE)
    ap.add_argument("--morph", type=Path, default=DEFAULT_MORPH)
    ap.add_argument("--no-morph", action="store_true", help="ignora a tipologia morfológica")
    ap.add_argument("--rebuild-cache", action="store_true")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    stats = load_stats(args.phoible, rebuild=args.rebuild_cache)
    req = {} if args.no_morph else read_morph_requirements(args.morph)
    opts = GeneratorOptions(
        mode=args.mode, seed=args.seed,
        n_consonants=args.consonants, n_vowels=args.vowels, tones=args.tones,
        allow_diphthongs=args.diphthongs, mutation_rate=args.mutation,
        economy_weight=args.economy, commonness=args.commonness,
    )
    result = InventoryGenerator(stats, opts, req).generate()

    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print_summary(result)
    print(f"\n[OK] Inventário salvo em '{args.output}'.")


if __name__ == "__main__":
    main()
