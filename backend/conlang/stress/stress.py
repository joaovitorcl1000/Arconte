"""
Módulo — Acento.

Decide o sistema de acento da conlang com distribuições do WALS (14A–17A) e
marca a sílaba tônica nas palavras:  akiʃontaŋ → /akiˈʃontaŋ/

    fixo              — sempre na mesma sílaba (inicial, penúltima, final...)
    sensível ao peso  — sílabas pesadas (com coda ou vogal longa) atraem o acento
    lexical           — imprevisível: cada palavra tem o seu
    ausente           — comum em línguas tonais

Não altera nenhum outro módulo: só lê os JSONs da língua (e usa o silabificador
público do módulo de fonotática).

Uso:
    python stress/stress.py --language languages/lang-31
    python stress/stress.py --language languages/lang-31 --rule penultimate

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
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "phonotactics"))
try:
    from phonotactics import Phonotactics  # silabificador público; opcional
except ImportError:  # pragma: no cover
    Phonotactics = None

DEFAULT_WALS = ROOT / "wals" / "cldf"
TONE_LETTERS = "˥˦˧˨˩"
PRIMARY, SECONDARY = "ˈ", "ˌ"

# ═══════════════════════════════════════════════════════════════════════════
# WALS (nº de línguas), usado quando o WALS local não existe
# ═══════════════════════════════════════════════════════════════════════════

EMBEDDED = {
    "14A": {"1": 220, "2": 92, "3": 16, "4": 1, "5": 12, "6": 110, "7": 51},       # posição fixa
    "15A": {"1": 37, "2": 2, "3": 65, "4": 27, "5": 54, "6": 8, "7": 26, "8": 281},  # peso
    "16A": {"1": 261, "2": 65, "3": 18, "4": 35, "5": 41, "6": 38, "7": 42},        # fatores de peso
    "17A": {"1": 153, "2": 31, "3": 4, "4": 37, "5": 98},                          # ritmo
}
FIXED_14A = {"2": "initial", "3": "second", "4": "third", "5": "antepenultimate",
             "6": "penultimate", "7": "ultimate"}
WEIGHT_15A = {"1": "left_edge", "2": "left_oriented", "3": "right_edge", "4": "right_oriented",
              "5": "unbounded", "6": "combined", "7": "lexical"}
HEAVY_16A = {"2": "long_vowel", "3": "coda", "4": "either", "5": "either", "7": "either"}
RHYTHM_17A = {"1": "trochaic", "2": "iambic", "3": "trochaic", "4": "none", "5": "none"}

P_NO_STRESS_TONAL = 0.6  # aproximação: em línguas tonais o acento costuma ser fraco ou ausente

RULES_PT = {
    "initial": "na primeira sílaba", "second": "na segunda sílaba", "third": "na terceira sílaba",
    "antepenultimate": "na antepenúltima sílaba", "penultimate": "na penúltima sílaba",
    "ultimate": "na última sílaba",
    "left_edge": "na primeira sílaba, ou na segunda se a primeira for leve e a segunda pesada",
    "left_oriented": "na primeira sílaba pesada entre as três primeiras; senão, na primeira",
    "right_edge": "na última sílaba se ela for pesada; senão, na penúltima",
    "right_oriented": "na penúltima se ela for pesada; senão, na antepenúltima (regra do latim)",
    "unbounded_left": "na primeira sílaba pesada da palavra; sem nenhuma, na primeira",
    "unbounded_right": "na última sílaba pesada da palavra; sem nenhuma, na última",
    "combined": "na última sílaba pesada da palavra; sem nenhuma, na penúltima",
    "lexical": "imprevisível: cada palavra tem sua sílaba tônica",
    "none": "sem acento (a proeminência vem do tom)",
}
HEAVY_PT = {"long_vowel": "vogal longa", "coda": "consoante em coda",
            "either": "vogal longa ou consoante em coda"}
RHYTHM_PT = {"trochaic": "trocaico (acentos secundários a cada duas sílabas, da tônica para o início)",
             "iambic": "iâmbico (acentos secundários a cada duas sílabas, da tônica para o fim)",
             "none": "sem acento secundário"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def wals_counts(fid: str, wals_dir: Optional[Path]) -> Tuple[Dict[str, int], str]:
    values = wals_dir / "values.csv" if wals_dir else None
    if values and values.exists():
        with open(values, encoding="utf-8", newline="") as f:
            c = Counter(r["Value"] for r in csv.DictReader(f) if r["Parameter_ID"] == fid)
        if c:
            return dict(c), f"WALS {fid} (n={sum(c.values())})"
    return EMBEDDED[fid], f"WALS {fid} (embutido)"


# ═══════════════════════════════════════════════════════════════════════════
# Decisão do sistema
# ═══════════════════════════════════════════════════════════════════════════

def build(inventory: Dict, rules: Optional[Dict], *, seed: Optional[int] = None,
          rule: Optional[str] = None, wals_dir: Optional[Path] = None) -> Dict:
    """Sorteia (ou recebe em `rule`) o sistema de acento, coerente com sílabas e tons."""
    rng = random.Random(seed)
    sources, notes = {}, []

    def pick(fid: str, allowed: Optional[Sequence[str]] = None) -> str:
        counts, src = wals_counts(fid, wals_dir)
        sources[fid] = src
        keys = sorted(k for k in counts if allowed is None or k in allowed)
        return rng.choices(keys, [counts[k] for k in keys])[0]

    has_long = any(v.get("long") for v in inventory["vowels"])
    has_coda = bool(rules and rules["codas"]["single"])
    heavy_options = [k for k, v in HEAVY_16A.items()
                     if (v == "long_vowel" and has_long) or (v == "coda" and has_coda)
                     or (v == "either" and (has_long or has_coda))]
    tonal = bool(inventory.get("tones"))

    system, weight, rhythm = "fixed", None, "none"
    if rule:
        chosen = rule
    elif tonal and rng.random() < P_NO_STRESS_TONAL:
        chosen = "none"
        sources["tone"] = "língua tonal: acento ausente (aproximação)"
    else:
        f14 = pick("14A")
        if f14 in FIXED_14A:
            chosen = FIXED_14A[f14]
        else:
            allowed = [k for k in WEIGHT_15A if k == "7" or heavy_options]
            chosen = WEIGHT_15A[pick("15A", allowed)]
            if not heavy_options and chosen != "lexical":
                chosen = "lexical"
            if chosen == "unbounded":
                chosen = rng.choice(["unbounded_left", "unbounded_right"])
        if not heavy_options and chosen in WEIGHT_15A.values():
            notes.append("sem sílabas pesadas na língua: o acento não pode depender do peso")

    if chosen in FIXED_14A.values():
        system = "fixed"
    elif chosen == "lexical":
        system = "lexical"
    elif chosen == "none":
        system = "none"
    else:
        system = "weight_sensitive"
        if not heavy_options:
            raise SystemExit(f"A regra '{chosen}' exige sílabas pesadas, mas a língua não tem "
                             "codas nem vogais longas.")
        weight = HEAVY_16A[pick("16A", heavy_options)]

    if system != "none":
        rhythm = RHYTHM_17A[pick("17A")]

    return {"system": system, "rule": chosen, "heavy": weight, "rhythm": rhythm,
            "description": describe_rule(chosen, weight, rhythm),
            "metadata": {"seed": seed, "sources": sources, "notes": notes}}


def describe_rule(rule: str, heavy: Optional[str], rhythm: str) -> str:
    text = f"Acento {RULES_PT[rule]}"
    if heavy:
        text += f"; sílaba pesada = sílaba com {HEAVY_PT[heavy]}"
    if rule != "none":
        text += f"; ritmo {RHYTHM_PT[rhythm]}"
    return text + "."


# ═══════════════════════════════════════════════════════════════════════════
# Aplicação
# ═══════════════════════════════════════════════════════════════════════════

class Stress:
    """Aplica o sistema de acento: sílabas → posição da tônica; IPA → IPA com ˈ e ˌ."""

    def __init__(self, spec: Dict, inventory: Dict, rules: Optional[Dict] = None,
                 seed: Optional[int] = None):
        self.spec = spec
        self.seed = seed if seed is not None else spec["metadata"].get("seed") or 0
        self.vowels = {nfd(v["ipa"]): v for v in inventory["vowels"]}
        self.symbols = sorted({nfd(x["ipa"]) for x in inventory["consonants"] + inventory["vowels"]},
                              key=len, reverse=True)
        self.ph = Phonotactics(rules, inventory) if (Phonotactics and rules) else None

    # ── segmentação e silabificação ──────────────────────────────────────
    def tokenize(self, s: str) -> List[str]:
        s, out, i = nfd(s), [], 0
        while i < len(s):
            hit = next((x for x in self.symbols if s.startswith(x, i)), None)
            out.append(hit or s[i])
            i += len(hit) if hit else 1
        return out

    def syllabify(self, ipa: str) -> List[List[str]]:
        """Sílabas da palavra. Pontos já presentes (formas tonais) são respeitados."""
        clean = "".join(ch for ch in nfd(ipa) if ch not in TONE_LETTERS + PRIMARY + SECONDARY)
        if "." in clean:
            return [self.tokenize(s) for s in clean.split(".") if s]
        segs = self.tokenize(clean)
        if self.ph:
            sylls = self.ph.syllabify(segs)
            if sylls:
                return sylls
        return self._fallback(segs)

    def _fallback(self, segs: List[str]) -> List[List[str]]:
        """Sem regras da língua: uma consoante intervocálica vai para a sílaba seguinte."""
        nuclei = [i for i, s in enumerate(segs) if s in self.vowels]
        if not nuclei:
            return [segs]
        sylls, start = [], 0
        for a, b in zip(nuclei, nuclei[1:]):
            cut = b - 1 if b - a > 1 else b
            sylls.append(segs[start:cut])
            start = cut
        sylls.append(segs[start:])
        return sylls

    def heavy(self, syl: List[str]) -> bool:
        h = self.spec["heavy"]
        nuc = next((i for i, s in enumerate(syl) if s in self.vowels), None)
        if nuc is None:
            return False
        long_v = bool(self.vowels[syl[nuc]].get("long"))
        coda = nuc < len(syl) - 1
        return {"long_vowel": long_v, "coda": coda, "either": long_v or coda}.get(h, False)

    # ── posição do acento ────────────────────────────────────────────────
    def primary(self, sylls: List[List[str]], word: str = "") -> Optional[int]:
        n, rule = len(sylls), self.spec["rule"]
        if rule == "none" or n == 0:
            return None
        if n == 1:
            return 0
        H = [self.heavy(s) for s in sylls]
        fixed = {"initial": 0, "second": 1, "third": min(2, n - 1),
                 "antepenultimate": max(0, n - 3), "penultimate": n - 2, "ultimate": n - 1}
        if rule in fixed:
            return fixed[rule]
        if rule == "left_edge":
            return 1 if (not H[0] and H[1]) else 0
        if rule == "left_oriented":
            return next((i for i in range(min(3, n)) if H[i]), 0)
        if rule == "right_edge":
            return n - 1 if H[-1] else n - 2
        if rule == "right_oriented":
            return n - 2 if (n == 2 or H[-2]) else n - 3
        if rule == "unbounded_left":
            return next((i for i in range(n) if H[i]), 0)
        if rule == "unbounded_right":
            return next((i for i in reversed(range(n)) if H[i]), n - 1)
        if rule == "combined":
            return next((i for i in reversed(range(n)) if H[i]), n - 2)
        if rule == "lexical":  # imprevisível, mas estável: depende só da palavra e da semente
            h = int(hashlib.sha256(f"{self.seed}:{word}".encode()).hexdigest()[:8], 16)
            weights = [3 if i == n - 2 else 2 if i == 0 else 1 for i in range(n)]
            r, acc = h % sum(weights), 0
            for i, w in enumerate(weights):
                acc += w
                if r < acc:
                    return i
        return 0

    def secondaries(self, n: int, p: Optional[int]) -> List[int]:
        """Acentos secundários a cada duas sílabas a partir da tônica (palavras de 4+ sílabas)."""
        if p is None or n < 4 or self.spec["rhythm"] == "none":
            return []
        if self.spec["rhythm"] == "trochaic":  # da tônica para o início da palavra
            out = list(range(p - 2, -1, -2))
        else:                                   # iâmbico: da tônica para o fim
            out = list(range(p + 2, n, 2))
        return sorted(out)

    def mark(self, ipa: str) -> str:
        """IPA → IPA com acento: 'akiʃontaŋ' → 'akiˈʃontaŋ'. Mantém os tons, se houver."""
        if not ipa or "-" in ipa:
            return ipa
        out = []
        for word in ipa.split(" "):
            sylls = self.syllabify(word)
            p = self.primary(sylls, word)
            sec = set(self.secondaries(len(sylls), p))
            tones = [t for t in ("".join(ch for ch in s if ch in TONE_LETTERS)
                                 for s in nfd(word).split("."))] if "." in word else []
            parts = []
            for i, syl in enumerate(sylls):
                mark = PRIMARY if (i == p and len(sylls) > 1) else SECONDARY if i in sec else ""
                tone = tones[i] if i < len(tones) else ""
                parts.append(mark + "".join(syl) + tone)
            out.append("".join(parts))
        return unicodedata.normalize("NFC", " ".join(out))


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PT = {"fixed": "fixo", "weight_sensitive": "sensível ao peso", "lexical": "lexical",
             "none": "ausente"}


def short_label(e: Dict) -> str:
    return e.get("label") or e["english"].split(" (")[0]


def write_markdown(path: Path, spec: Dict, st: Stress, lexicon: Optional[Dict]) -> None:
    lines = ["# Acento", "", f"- Sistema: **{SYSTEM_PT[spec['system']]}**",
             f"- {spec['description']}"]
    for n in spec["metadata"]["notes"]:
        lines.append(f"- Nota: {n}")
    if lexicon and spec["system"] != "none":
        words = [e for e in lexicon["entries"] if e.get("citation") and "-" not in e["citation"]]
        multi = [e for e in words if len(st.syllabify(e["citation"])) > 1][:12]
        lines += ["", "## Exemplos", "", "| Palavra | Sílabas | Pronúncia | Significado |", "|---|---|---|---|"]
        for e in multi:
            sy = ".".join("".join(s) for s in st.syllabify(e["citation"]))
            lines.append(f"| {e['citation']} | {sy} | /{st.mark(e['citation'])}/ | {short_label(e)} |")
    if lexicon:
        lines += ["", "## Dicionário com acento", ""]
        rows = sorted((e for e in lexicon["entries"] if e.get("citation")), key=lambda e: e["citation"])
        lines += [f"- /{st.mark(e['citation'])}/ '{short_label(e)}'" for e in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Decide e aplica o acento da conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--rule", choices=list(RULES_PT), help="força uma regra (sorteada se omitida)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    args = ap.parse_args()

    d = args.language
    inventory = _load(d / "phonemic_inventory.json")
    if inventory is None:
        raise SystemExit(f"Não encontrei {d / 'phonemic_inventory.json'}")
    rules, lexicon, manifest = _load(d / "phonotactics.json"), _load(d / "lexicon.json"), _load(d / "manifest.json")
    seed = args.seed if args.seed is not None else (derive_seed(manifest["seed"], "stress") if manifest else None)
    wals = None if args.no_wals or not args.wals.exists() else args.wals

    spec = build(inventory, rules, seed=seed, rule=args.rule, wals_dir=wals)
    st = Stress(spec, inventory, rules, seed)
    if lexicon:
        multi = [e["citation"] for e in lexicon["entries"]
                 if e.get("citation") and "-" not in e["citation"] and len(st.syllabify(e["citation"])) > 1]
        spec["examples"] = [{"ipa": w, "stressed": st.mark(w)} for w in multi[:20]]
    (d / "stress.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(d / "stress.md", spec, st, lexicon)

    print(f"\nACENTO — {SYSTEM_PT[spec['system']]}")
    print(f"  {spec['description']}")
    for n in spec["metadata"]["notes"]:
        print(f"  · {n}")
    for ex in spec.get("examples", [])[:10]:
        print(f"    {ex['ipa']:<18} /{ex['stressed']}/")
    print(f"\n[OK] Acento salvo em '{d / 'stress.json'}' e 'stress.md'.")


if __name__ == "__main__":
    main()
