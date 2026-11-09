"""
Módulo — Fonotática e Estrutura Silábica.

Recebe o inventário fonêmico (phonemic_inventory.json) e define como os sons
se combinam: moldes silábicos, encontros consonantais permitidos, codas,
hiato, sonoridade e formato das raízes. Salva as regras em phonotactics.json
e expõe um gerador de raízes, afixos e um silabificador/validador que o
motor morfológico usará depois.

Entradas:
  ../phonemic_inventory/phonemic_inventory.json          (obrigatória)
  ../morphological_typology/morphological_typology.json  (opcional)
  ../wals/cldf/{languages,values}.csv                    (opcional, WALS 12A)

Requer apenas a biblioteca padrão (Python ≥ 3.9).

Uso:
    python phonotactics.py
    python phonotactics.py --seed 42 --samples 30
    python phonotactics.py --complexity complex
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Caminhos padrão (estrutura conlang/<módulo>/)
# ═══════════════════════════════════════════════════════════════════════════

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_INVENTORY = ROOT / "phonemic_inventory" / "phonemic_inventory.json"
DEFAULT_MORPH = ROOT / "morphological_typology" / "morphological_typology.json"
DEFAULT_WALS = ROOT / "wals" / "cldf"
DEFAULT_OUTPUT = HERE / "phonotactics.json"

Cluster = Tuple[str, ...]

# ═══════════════════════════════════════════════════════════════════════════
# Constantes tipológicas
# ═══════════════════════════════════════════════════════════════════════════

# Escala de sonoridade (maior = mais sonoro)
MANNER_SONORITY = {"stop": 1, "click": 1, "affricate": 1, "fricative": 2,
                   "nasal": 3, "lateral": 4, "rhotic": 4, "approximant": 5}
VOWEL_SONORITY = 6

# P(complexidade silábica | tamanho do inventário consonantal), calculado
# cruzando WALS 1A × 12A (486 línguas). Faixas do WALS 1A.
COMPLEXITY_BY_CONSONANTS = [
    (14, {"simple": 0.30, "moderate": 0.55, "complex": 0.15}),
    (18, {"simple": 0.13, "moderate": 0.69, "complex": 0.18}),
    (25, {"simple": 0.08, "moderate": 0.56, "complex": 0.35}),
    (33, {"simple": 0.05, "moderate": 0.52, "complex": 0.43}),
    (999, {"simple": 0.10, "moderate": 0.41, "complex": 0.49}),
]

WALS_12A = {"1": "simple", "2": "moderate", "3": "complex"}

# Moldes silábicos de partida (pesos perturbados a cada língua)
BASE_TEMPLATES = {
    "simple":   {"CV": 0.75, "V": 0.25},
    "moderate": {"CV": 0.45, "CVC": 0.25, "V": 0.10, "VC": 0.05,
                 "CCV": 0.10, "CCVC": 0.05},
    "complex":  {"CV": 0.30, "CVC": 0.25, "V": 0.05, "VC": 0.05, "CCV": 0.12,
                 "CCVC": 0.10, "CVCC": 0.06, "CCCV": 0.03, "CCVCC": 0.04},
}

# Distribuição do nº de sílabas por raiz
ROOT_LENGTH = {
    "isolating": {1: 0.70, 2: 0.30},
    "simple":    {1: 0.10, 2: 0.50, 3: 0.30, 4: 0.10},
    "moderate":  {1: 0.25, 2: 0.50, 3: 0.20, 4: 0.05},
    "complex":   {1: 0.40, 2: 0.45, 3: 0.15},
}


# ═══════════════════════════════════════════════════════════════════════════
# Auxiliares
# ═══════════════════════════════════════════════════════════════════════════

def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def sonority(entry: Dict) -> int:
    """Sonoridade a partir dos rótulos do inventário."""
    if "manner" not in entry:
        return VOWEL_SONORITY
    if entry["manner"] == "approximant" and entry["features"].get("consonantal") == "+":
        return 4  # aproximantes consonantais (ɻ, ɹ) se comportam como líquidas
    return MANNER_SONORITY.get(entry["manner"], 1)


def is_complex_segment(c: Dict) -> bool:
    """
    Segmentos 'pesados', normalmente barrados em codas e encontros:
    aspiradas, ejetivas/glotalizadas, implosivas, cliques, longas e
    segmentos com articulação secundária ou de contorno (kʷ, tʲ, ⁿd).
    """
    f = c["features"]
    if any("," in v for v in f.values()):
        return True
    if f.get("spreadGlottis") == "+" and c["manner"] != "fricative":
        return True
    if f.get("constrictedGlottis") == "+" and c["place"] != "laryngeal":
        return True
    if c["place"] == "labial-velar" and c["manner"] != "approximant":
        return True  # oclusivas duplamente articuladas (kp, ɡb)
    return any(f.get(k) == "+" for k in ("loweredLarynxImplosive", "click", "long"))


def is_voiced_obstruent(c: Dict) -> bool:
    return (c["manner"] in ("stop", "affricate", "fricative")
            and c["features"].get("periodicGlottalSource") == "+")


def weighted_choice(rng: random.Random, weights: Dict):
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def wals_syllable_structure(wals_dir: Path, glottocode: str) -> Optional[str]:
    """Valor do WALS 12A para uma língua (via Glottocode), se existir."""
    langs, vals = wals_dir / "languages.csv", wals_dir / "values.csv"
    if not (langs.exists() and vals.exists() and glottocode):
        return None
    with open(langs, encoding="utf-8", newline="") as f:
        ids = {r["ID"] for r in csv.DictReader(f) if r["Glottocode"] == glottocode}
    if not ids:
        return None
    with open(vals, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["Parameter_ID"] == "12A" and r["Language_ID"] in ids:
                return WALS_12A.get(r["Value"])
    return None


def read_morph_requirements(path: Path) -> Dict:
    """Traduz a tipologia morfológica em exigências fonotáticas."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    procs = set(data.get("active_processes", []))
    req: Dict = {}
    if data.get("degree_of_synthesis") == "isolating":
        req["max_root_syllables"] = 2
        req["isolating"] = True
    if "transfixation" in procs:
        req["root_shape"] = "consonantal_skeleton"
    if "tonal_morphology" in procs:
        req["tone"] = True
    return req


# ═══════════════════════════════════════════════════════════════════════════
# Construção das regras
# ═══════════════════════════════════════════════════════════════════════════

def build_rules(inventory: Dict, *, seed: Optional[int] = None,
                complexity: Optional[str] = None,
                morph_req: Optional[Dict] = None,
                wals_dir: Optional[Path] = None) -> Dict:
    """Sorteia as regras fonotáticas de uma língua a partir do inventário."""
    rng = random.Random(seed)
    morph_req = morph_req or {}
    cons = {nfd(c["ipa"]): c for c in inventory["consonants"]}
    vowels = {nfd(v["ipa"]): v for v in inventory["vowels"]}
    son = {**{k: sonority(c) for k, c in cons.items()}, **{k: VOWEL_SONORITY for k in vowels}}
    simple = {k for k, c in cons.items() if not is_complex_segment(c)}
    log: List[str] = []

    # ── 1. Complexidade silábica ─────────────────────────────────────────
    source = "forced"
    if complexity is None:
        ref = (inventory.get("metadata", {}).get("reference_language") or {})
        if wals_dir is not None:
            complexity = wals_syllable_structure(wals_dir, ref.get("glottocode", ""))
            if complexity:
                source = f"WALS 12A ({ref.get('name')})"
        if complexity is None:
            n = len(cons)
            dist = next(d for limit, d in COMPLEXITY_BY_CONSONANTS if n <= limit)
            complexity = weighted_choice(rng, dist)
            source = f"sorteio condicionado a {n} consoantes (WALS 1A × 12A)"

    # ── 2. Moldes silábicos ──────────────────────────────────────────────
    templates = dict(BASE_TEMPLATES[complexity])
    has_coda = complexity != "simple"
    has_clusters = complexity == "complex"
    if complexity == "moderate":
        # O tipo moderado admite CVC e/ou CCV restrito; nem sempre os dois.
        mode = weighted_choice(rng, {"both": 0.4, "coda_only": 0.45, "cluster_only": 0.15})
        has_coda = mode != "cluster_only"
        has_clusters = mode != "coda_only"
    onset_required = rng.random() < (0.3 if complexity == "simple" else 0.15)
    allow_hiatus = (not onset_required) and rng.random() < 0.3

    for pat in list(templates):
        onset = len(pat) - len(pat.lstrip("C"))
        coda = len(pat) - len(pat.rstrip("C"))
        if (coda and not has_coda) or (onset > 1 and not has_clusters) or \
                (onset == 0 and onset_required):
            del templates[pat]
    templates = {k: v * rng.uniform(0.6, 1.4) for k, v in templates.items()}
    total = sum(templates.values())
    templates = {k: round(v / total, 3) for k, v in templates.items()}

    # ── 3. Encontros no ataque ───────────────────────────────────────────
    # Base: obstruinte + líquida/glide (pl, kr, tw). Extensões sorteadas por
    # língua; nas línguas moderadas a 2ª consoante é sempre líquida ou glide.
    min_dist = 2 if complexity == "moderate" else 1
    onset2: List[Cluster] = []
    onset3: List[Cluster] = []
    clusterable = {k for k in simple if cons[k]["place"] != "laryngeal"}
    obstruent = {k for k in clusterable if son[k] <= 2}
    policy = {
        "nasal_liquid": rng.random() < 0.3,                                  # ml, nr
        "obstruent_nasal": complexity == "complex" and rng.random() < 0.4,   # pn, kn
        "stop_fricative": complexity == "complex" and rng.random() < 0.35,   # ps, ks
    }
    if has_clusters:
        labels = {"nasal_liquid": "nasal+líquida", "obstruent_nasal": "obstruinte+nasal",
                  "stop_fricative": "oclusiva+fricativa"}
        extras = [labels[k] for k, v in policy.items() if v]
        log.append("encontros no ataque: obstruinte+líquida/glide"
                   + (", " + ", ".join(extras) if extras else ""))
        keep = 0.85 if complexity == "moderate" else 0.7
        for c1 in sorted(clusterable):
            for c2 in sorted(clusterable):
                a, b = cons[c1], cons[c2]
                if c1 == c2 or son[c2] - son[c1] < min_dist:
                    continue
                if son[c2] >= 4:
                    ok = c1 in obstruent or (policy["nasal_liquid"] and a["manner"] == "nasal")
                elif b["manner"] == "nasal":
                    ok = (policy["obstruent_nasal"] and c1 in obstruent
                          and b["place"] in ("labial", "coronal") and a["place"] != b["place"])
                else:
                    ok = (policy["stop_fricative"] and a["manner"] == "stop"
                          and b["manner"] == "fricative" and a["place"] != b["place"]
                          and is_voiced_obstruent(a) == is_voiced_obstruent(b))
                if not ok:
                    continue
                if b["manner"] == "lateral" and a["place"] == b["place"] == "coronal":
                    continue  # *tl, *dl
                if (c2 == "w" and a["place"] in ("labial", "labial-velar")) or \
                        (c2 == "j" and a["place"] == "palatal"):
                    continue  # *pw, *cj
                if rng.random() < keep:  # lacunas acidentais
                    onset2.append((c1, c2))

        # s + oclusiva: violação da SSP comum em línguas complexas (sp, st, sk)
        if complexity == "complex" and "s" in simple and rng.random() < 0.6:
            for c2 in sorted(simple):
                if cons[c2]["manner"] == "stop" and not is_voiced_obstruent(cons[c2]) \
                        and cons[c2]["place"] != "laryngeal":
                    onset2.append(("s", c2))  # sp, st, sk
            log.append("encontros s + oclusiva permitidos (exceção à SSP)")
            if "CCCV" in templates:
                onset3 = [("s",) + cl for cl in onset2
                          if cl[0] != "s" and cons[cl[0]]["manner"] == "stop"
                          and not is_voiced_obstruent(cons[cl[0]]) and son[cl[1]] >= 4]

    if has_clusters and not onset2:
        templates = {k: v for k, v in templates.items() if not k.startswith("CC")}
        log.append("nenhum encontro possível com este inventário: moldes CC removidos")
    if "CCCV" in templates and not onset3:
        templates.pop("CCCV")

    # ── 4. Codas ─────────────────────────────────────────────────────────
    codas: List[str] = []
    final_codas: List[str] = []
    coda2: List[Cluster] = []
    if has_coda:
        profile = weighted_choice(rng, {
            "simple":   {},
            "moderate": {"nasals": 0.15, "sonorants": 0.35, "restricted": 0.35, "free": 0.15},
            "complex":  {"sonorants": 0.15, "restricted": 0.40, "free": 0.45},
        }[complexity])
        glides_ok = rng.random() < 0.5
        devoice = rng.random() < 0.5
        for k in sorted(simple):
            c = cons[k]
            m = c["manner"]
            if m == "approximant" and son[k] == 5 and not glides_ok:
                continue
            if profile == "nasals" and m != "nasal":
                continue
            if profile == "sonorants" and son[k] < 3:
                continue
            if profile == "restricted" and son[k] < 3 and (
                    is_voiced_obstruent(c) or m == "affricate" or rng.random() < 0.4):
                continue
            if profile == "free" and devoice and is_voiced_obstruent(c):
                continue
            codas.append(k)
        if not codas:  # garante ao menos as nasais
            codas = [k for k in sorted(simple) if cons[k]["manner"] == "nasal"]
        log.append(f"perfil de coda: {profile}" + (", obstruintes sonoras barradas"
                                                  if devoice and profile == "free" else ""))

        final_codas = list(codas)
        if rng.random() < 0.3:
            restricted = [k for k in codas if son[k] >= 3]
            if restricted and len(restricted) < len(codas):
                final_codas = restricted
                log.append("final de palavra aceita só codas soantes")

        if "CVCC" in templates or "CCVCC" in templates:
            # soante + obstruinte (nt, lk, rs); opcionalmente fricativa + oclusiva (st)
            homorganic = rng.random() < 0.6
            fric_stop = rng.random() < 0.4
            for c1 in codas:
                for c2 in codas:
                    a, b = cons[c1], cons[c2]
                    if c1 == c2 or "laryngeal" in (a["place"], b["place"]):
                        continue
                    if son[c1] >= 3 and son[c2] <= 2:
                        ok = not (homorganic and a["manner"] == "nasal" and a["place"] != b["place"])
                    else:
                        ok = (fric_stop and a["manner"] == "fricative" and b["manner"] == "stop"
                              and is_voiced_obstruent(a) == is_voiced_obstruent(b))
                    if ok and rng.random() < 0.8:
                        coda2.append((c1, c2))
            if not coda2:
                templates = {k: v for k, v in templates.items() if not k.endswith("CC")}

        if not codas:
            templates = {k: v for k, v in templates.items() if not k.endswith("C")}

    total = sum(templates.values())
    templates = {k: round(v / total, 3) for k, v in templates.items()}

    # ── 5. Restrições posicionais ────────────────────────────────────────
    initial_forbidden = []
    for k in ("ŋ", "ɳ", "ɭ"):
        if k in cons and rng.random() < 0.6:
            initial_forbidden.append(k)

    # ── 6. Raízes ────────────────────────────────────────────────────────
    root_len = dict(ROOT_LENGTH[complexity])
    if morph_req.get("max_root_syllables"):
        root_len = dict(ROOT_LENGTH["isolating"])
    root_shape = morph_req.get("root_shape", "syllabic")

    tones = [nfd(t["ipa"]) for t in inventory.get("tones", [])]
    if morph_req.get("tone") and not tones:
        log.append("AVISO: a morfologia exige tom, mas o inventário não tem tons "
                   "(gere o inventário novamente)")

    return {
        "syllable_complexity": complexity,
        "complexity_source": source,
        "templates": templates,
        "onset_required": onset_required,
        "allow_hiatus": allow_hiatus,
        "min_sonority_distance": min_dist,
        "sonority": son,
        "onsets": {
            "clusters": [list(c) for c in onset2],
            "triple": [list(c) for c in onset3],
            "word_initial_forbidden": initial_forbidden,
        },
        "codas": {
            "single": codas,
            "word_final": final_codas,
            "clusters": [list(c) for c in coda2],
        },
        "syllable_contact": True,
        "root": {
            "shape": root_shape,
            "syllables": {str(k): v for k, v in root_len.items()},
        },
        "tone_bearing": bool(tones),
        "metadata": {"seed": seed, "morphology_requirements": morph_req, "notes": log},
    }


# ═══════════════════════════════════════════════════════════════════════════
# Motor fonotático (geração e validação)
# ═══════════════════════════════════════════════════════════════════════════

class Phonotactics:
    """
    Aplica as regras de phonotactics.json sobre o inventário.

    Segmentos são sempre strings em NFD tratadas como unidades:
    uma palavra é uma lista como ["t̠ʃʰ", "a", "n"], nunca uma string.
    """

    def __init__(self, rules: Dict, inventory: Dict, seed: Optional[int] = None):
        self.r = rules
        self.rng = random.Random(seed)
        self.cons = {nfd(c["ipa"]): c for c in inventory["consonants"]}
        self.vowels = {nfd(v["ipa"]): v for v in inventory["vowels"]}
        self.tones = {nfd(t["ipa"]): t for t in inventory.get("tones", [])}
        self.son = rules["sonority"]
        self.patterns = set(rules["templates"])
        self.onset2 = {tuple(c) for c in rules["onsets"]["clusters"]}
        self.onset3 = {tuple(c) for c in rules["onsets"]["triple"]}
        self.no_initial = set(rules["onsets"]["word_initial_forbidden"])
        self.coda1 = set(rules["codas"]["single"])
        self.coda_final = set(rules["codas"]["word_final"])
        self.coda2 = {tuple(c) for c in rules["codas"]["clusters"]}

    # ── sorteios ponderados ──────────────────────────────────────────────
    def _freq_pick(self, items: Iterable, power: float = 1.5):
        items = sorted(items)  # ordem fixa: conjuntos variam entre execuções (hash aleatório)
        weights = []
        for it in items:
            segs = it if isinstance(it, tuple) else (it,)
            w = 1.0
            for s in segs:
                entry = self.cons.get(s) or self.vowels.get(s) or self.tones.get(s)
                w *= (entry["frequency"] if entry else 0.1) ** power + 0.01
            weights.append(w)
        return self.rng.choices(items, weights=weights, k=1)[0]

    def _onset(self, n: int, initial: bool) -> List[str]:
        if n == 0:
            return []
        if n == 1:
            pool = [c for c in self.cons if not (initial and c in self.no_initial)]
            return [self._freq_pick(pool)]
        pool = self.onset2 if n == 2 else self.onset3
        return list(self._freq_pick(pool))

    def _coda(self, n: int, final: bool) -> List[str]:
        if n == 0:
            return []
        if n == 1:
            return [self._freq_pick(self.coda_final if final else self.coda1)]
        pool = [c for c in self.coda2 if not final or c[-1] in self.coda_final]
        return list(self._freq_pick(pool)) if pool else []

    def _template(self, initial: bool, final: bool, prev_coda: bool) -> str:
        options = {}
        for pat, w in self.r["templates"].items():
            onset = len(pat) - len(pat.lstrip("C"))
            coda = len(pat) - len(pat.rstrip("C"))
            if onset == 0 and not initial and not (self.r["allow_hiatus"] or prev_coda):
                continue
            if onset == 0 and not initial and prev_coda:
                continue  # VC.V seria ressilabificado como V.CV
            if coda and final and not self.coda_final:
                continue
            if coda == 2 and final and not any(c[-1] in self.coda_final for c in self.coda2):
                continue
            options[pat] = w
        return weighted_choice(self.rng, options)

    # ── geração ──────────────────────────────────────────────────────────
    def generate_syllables(self, n: int) -> List[List[str]]:
        for _ in range(200):
            sylls: List[List[str]] = []
            ok = True
            for i in range(n):
                initial, final = i == 0, i == n - 1
                prev_coda = bool(sylls) and sylls[-1][-1] in self.cons
                pat = self._template(initial, final, prev_coda)
                n_on = len(pat) - len(pat.lstrip("C"))
                n_co = len(pat) - len(pat.rstrip("C"))
                onset = self._onset(n_on, initial)
                nucleus = [self._freq_pick(self.vowels)]
                coda = self._coda(n_co, final)
                if n_co and not coda:
                    ok = False
                    break
                # Lei do contato silábico: evita coda menos sonora que o ataque seguinte
                if sylls and prev_coda and onset:
                    if self.son[sylls[-1][-1]] < self.son[onset[0]] and self.rng.random() < 0.5:
                        ok = False
                        break
                    if sylls[-1][-1] == onset[0]:
                        ok = False  # sem geminadas por acaso
                        break
                sylls.append(onset + nucleus + coda)
            if ok and self.syllabify([s for syl in sylls for s in syl]) is not None:
                return sylls
        raise RuntimeError("não foi possível gerar uma forma válida; revise as regras")

    def _with_tones(self, sylls: List[List[str]]) -> Tuple[List[str], str]:
        if not (self.r["tone_bearing"] and self.tones):
            return [], ".".join("".join(s) for s in sylls)
        tones = [self._freq_pick(self.tones) for _ in sylls]
        return tones, ".".join("".join(s) + t for s, t in zip(sylls, tones))

    def generate_root(self, n_syllables: Optional[int] = None) -> Dict:
        """Gera uma raiz. Com transfixação, devolve um esqueleto consonantal."""
        if self.r["root"]["shape"] == "consonantal_skeleton":
            return self.generate_skeleton()
        if n_syllables is None:
            n_syllables = int(weighted_choice(self.rng, self.r["root"]["syllables"]))
        sylls = self.generate_syllables(n_syllables)
        tones, form = self._with_tones(sylls)
        return {"segments": [s for syl in sylls for s in syl], "syllables": sylls,
                "tones": tones, "form": form}

    def generate_skeleton(self, n: int = 3) -> Dict:
        """
        Raiz consonantal (estilo semítico). Aplica o OCP: C1 ≠ C2 e,
        preferencialmente, C1 e C2 em pontos de articulação diferentes.
        """
        pool = sorted(k for k, c in self.cons.items() if not is_complex_segment(c))
        for _ in range(200):
            root = [self._freq_pick(pool) for _ in range(n)]
            if root[0] == root[1]:
                continue
            if self.cons[root[0]]["place"] == self.cons[root[1]]["place"] and self.rng.random() < 0.9:
                continue
            return {"segments": root, "syllables": [], "tones": [], "form": "-".join(root)}
        raise RuntimeError("inventário pequeno demais para esqueletos consonantais")

    def generate_affix(self, kind: str = "suffix") -> Dict:
        """
        Afixos são curtos e tendem a usar segmentos não marcados
        (por isso o peso da frequência é mais forte aqui).
        """
        shapes = ({"CV": 0.40, "V": 0.20, "VC": 0.20, "C": 0.20} if kind == "suffix"
                  else {"CV": 0.50, "V": 0.25, "CVC": 0.15, "C": 0.10})
        if not self.coda1:
            shapes.pop("VC", None)
            shapes.pop("CVC", None)
            if kind == "suffix":
                shapes.pop("C", None)
        if kind == "prefix" and not self.onset2:
            shapes.pop("C", None)
        if kind == "prefix" and self.r["onset_required"]:
            shapes.pop("V", None)  # prefixo vocálico deixaria a palavra sem ataque
        shape = weighted_choice(self.rng, shapes)

        simple_cons = [k for k, c in self.cons.items() if not is_complex_segment(c)]
        segs: List[str] = []
        for i, slot in enumerate(shape):
            if slot == "V":
                segs.append(self._freq_pick(self.vowels, power=2.5))
            elif shape == "C" and kind == "suffix":
                segs.append(self._freq_pick(self.coda_final or self.coda1, power=2.5))
            elif shape == "C":
                segs.append(self._freq_pick({c[0] for c in self.onset2}, power=2.5))
            elif i == len(shape) - 1 and shape != "C":
                segs.append(self._freq_pick(self.coda1, power=2.5))
            else:
                segs.append(self._freq_pick(simple_cons, power=2.5))
        form = "".join(segs)
        return {"segments": segs, "kind": kind,
                "form": f"-{form}" if kind == "suffix" else f"{form}-"}

    # ── validação ────────────────────────────────────────────────────────
    def _valid_onset(self, cl: Sequence[str], initial: bool) -> bool:
        cl = tuple(cl)
        if len(cl) == 1:
            return cl[0] in self.cons and not (initial and cl[0] in self.no_initial)
        return cl in (self.onset2 if len(cl) == 2 else self.onset3)

    def _valid_coda(self, cl: Sequence[str], final: bool) -> bool:
        cl = tuple(cl)
        if not cl:
            return True
        if len(cl) == 1:
            return cl[0] in (self.coda_final if final else self.coda1)
        return len(cl) == 2 and cl in self.coda2 and (not final or cl[-1] in self.coda_final)

    def syllabify(self, segments: Sequence[str]) -> Optional[List[List[str]]]:
        """
        Silabifica pelo Princípio do Ataque Máximo e devolve None se a palavra
        violar a fonotática. É o validador que o motor morfológico usará para
        detectar quando a afixação cria sequências ilegais (e acionar sândi).
        """
        segs = [nfd(s) for s in segments]
        if any(s not in self.cons and s not in self.vowels for s in segs):
            return None
        nuclei = [i for i, s in enumerate(segs) if s in self.vowels]
        if not nuclei:
            return None

        sylls: List[List[str]] = []
        first = segs[:nuclei[0]]
        if first and not self._valid_onset(first, initial=True):
            return None
        if not first and self.r["onset_required"]:
            return None
        current = first + [segs[nuclei[0]]]

        for a, b in zip(nuclei, nuclei[1:]):
            cluster = segs[a + 1:b]
            if not cluster:
                if not self.r["allow_hiatus"]:
                    return None
                sylls.append(current)
                current = [segs[b]]
                continue
            for j in range(len(cluster)):  # j = tamanho da coda; menor j = ataque máximo
                coda, onset = cluster[:j], cluster[j:]
                if len(onset) <= 3 and self._valid_onset(onset, False) \
                        and self._valid_coda(coda, False):
                    sylls.append(current + coda)
                    current = onset + [segs[b]]
                    break
            else:
                return None

        last = segs[nuclei[-1] + 1:]
        if not self._valid_coda(last, final=True):
            return None
        sylls.append(current + last)

        for syl in sylls:  # o formato precisa existir entre os moldes
            pat = "".join("V" if s in self.vowels else "C" for s in syl)
            if pat not in self.patterns:
                return None
        return sylls

    def is_valid(self, segments: Sequence[str]) -> bool:
        return self.syllabify(segments) is not None


# ═══════════════════════════════════════════════════════════════════════════
# Exibição
# ═══════════════════════════════════════════════════════════════════════════

def print_summary(rules: Dict, samples: Dict) -> None:
    print(f"\nESTRUTURA SILÁBICA: {rules['syllable_complexity']}  ({rules['complexity_source']})")
    tpl = sorted(rules["templates"].items(), key=lambda x: -x[1])
    print("  Moldes:  " + "  ".join(f"{k} {v:.0%}" for k, v in tpl))
    flags = []
    flags.append("ataque obrigatório" if rules["onset_required"] else "ataque opcional")
    flags.append("hiato permitido" if rules["allow_hiatus"] else "sem hiato")
    print("  " + ", ".join(flags))

    on = rules["onsets"]
    if on["clusters"]:
        cl = ["".join(c) for c in on["clusters"]]
        more = f" … (+{len(cl) - 24})" if len(cl) > 24 else ""
        print(f"\nENCONTROS NO ATAQUE ({len(cl)}): " + " ".join(cl[:24]) + more)
    if on["triple"]:
        print("  Triplos: " + " ".join("".join(c) for c in on["triple"]))
    if on["word_initial_forbidden"]:
        print("  Proibidos no início de palavra: " + " ".join(on["word_initial_forbidden"]))

    co = rules["codas"]
    if co["single"]:
        print(f"\nCODAS ({len(co['single'])}): " + " ".join(co["single"]))
        if co["word_final"] != co["single"]:
            print("  No fim de palavra: " + " ".join(co["word_final"]))
        if co["clusters"]:
            print("  Encontros em coda: " + " ".join("".join(c) for c in co["clusters"][:20]))
    else:
        print("\nCODAS: nenhuma (sílabas abertas)")

    print(f"\nRAÍZES ({rules['root']['shape']}):")
    print("  " + "  ".join(r["form"] for r in samples["roots"]))
    if samples["suffixes"]:
        print("SUFIXOS:  " + "  ".join(a["form"] for a in samples["suffixes"]))
        print("PREFIXOS: " + "  ".join(a["form"] for a in samples["prefixes"]))
    if rules["metadata"]["notes"]:
        print("\nNotas: " + "; ".join(rules["metadata"]["notes"]))


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    ap = argparse.ArgumentParser(description="Gera a fonotática da conlang.")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--complexity", choices=["simple", "moderate", "complex"],
                    help="força a complexidade silábica (WALS 12A)")
    ap.add_argument("--samples", type=int, default=20, help="nº de raízes de exemplo")
    ap.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    ap.add_argument("--morph", type=Path, default=DEFAULT_MORPH)
    ap.add_argument("--no-morph", action="store_true")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS,
                    help="pasta cldf/ do WALS (opcional)")
    ap.add_argument("--no-wals", action="store_true")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    if not args.inventory.exists():
        raise SystemExit(f"Inventário não encontrado: {args.inventory}\n"
                         "Rode antes: python ../phonemic_inventory/phonemic_inventory.py")
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    morph_req = {} if args.no_morph else read_morph_requirements(args.morph)
    wals = None if args.no_wals or not args.wals.exists() else args.wals

    rules = build_rules(inventory, seed=args.seed, complexity=args.complexity,
                        morph_req=morph_req, wals_dir=wals)
    engine = Phonotactics(rules, inventory, seed=args.seed)
    n_affixes = 0 if morph_req.get("isolating") else 6  # língua isolante: sem afixos
    samples = {
        "roots": [engine.generate_root() for _ in range(args.samples)],
        "suffixes": [engine.generate_affix("suffix") for _ in range(n_affixes)],
        "prefixes": [engine.generate_affix("prefix") for _ in range(n_affixes)],
    }
    rules["samples"] = {k: [x["form"] for x in v] for k, v in samples.items()}

    args.output.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    print_summary(rules, samples)
    print(f"\n[OK] Fonotática salva em '{args.output}'.")


if __name__ == "__main__":
    main()
