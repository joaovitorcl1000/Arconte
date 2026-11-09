"""
Módulo — Sistema numeral.

Cria o sistema de numerais da conlang — o "Number base" e o "List numbers" do
Vulgarlang —, com as bases das línguas reais (WALS 131A) e ordinais (WALS 53A):

    decimal              37 = 3×10 + 7                 (português, mandarim)
    quinário-decimal     7 = 5+2; 37 = 3×10 + 5+2      (muitas línguas da África e das Américas)
    vigesimal            37 = 20 + 10+7                (maia, basco antigo)
    híbrido              90 = 4×20 + 10; 100 é decimal (francês 'quatre-vingt-dix')
    restrito             1, 2, 3 e 'muitos'            (várias línguas da Amazônia e da Austrália)
    partes do corpo      números contados ao longo do corpo (línguas da Nova Guiné)

Também decide a ordem dos elementos (dez-três ou três-dez; trinta-e-sete ou
sete-e-trinta), se os numerais compostos viram uma palavra só (com o sândi da
língua) e como se formam os ordinais ('primeiro', 'terceiro').

Os numerais 1 a 5 do léxico são reaproveitados; os demais são palavras novas.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico, da ortografia e do acento.

Uso:
    python numerals/numerals.py --language languages/lang-31
    python numerals/numerals.py --language languages/lang-31 --base vigesimal

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

DEFAULT_WALS = ROOT / "wals" / "cldf"
TONE_LETTERS = "˥˦˧˨˩"

# WALS 131A (bases numerais) e 53A (ordinais), nº de línguas
EMBEDDED_131A = {"1": 125, "2": 22, "3": 20, "4": 5, "5": 4, "6": 20}
EMBEDDED_53A = {"1": 33, "2": 3, "3": 12, "4": 41, "5": 54, "6": 110, "7": 61, "8": 7}
BASE_131A = {"1": "decimal", "2": "hybrid", "3": "vigesimal", "4": "quinary", "5": "body_part", "6": "restricted"}
P_QUINARY_INSIDE_DECIMAL = 0.2  # decimais com 6–9 formados a partir de 5 (aproximação)

LEXICON_NUMERALS = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE"}
BODY_SEQUENCE = ["HAND", "ARM OR HAND", "NECK", "EAR", "EYE", "NOSE", "MOUTH", "HEAD"]

BASE_PT = {"decimal": "decimal (base 10)", "quinary": "quinário-decimal (6–9 a partir de 5)",
           "vigesimal": "vigesimal (base 20)", "hybrid": "híbrido vigesimal-decimal (base 20 até 99, decimal depois)",
           "restricted": "restrito (poucos numerais, depois 'muitos')",
           "body_part": "partes do corpo (números contados ao longo do corpo)"}
EN_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
              9: "nine", 10: "ten", 20: "twenty", 100: "hundred", 400: "four hundred", 1000: "thousand",
              8000: "eight thousand"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class NumeralBuilder:
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
        typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "numerals") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.wals_dir = wals_dir
        self.sources: Dict[str, str] = {}
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.tonal = bool(self.rules.get("tone_bearing") and self.ph.tones)
        self.isolating = self.catdata["metadata"]["typology"]["synthesis"] == "isolating"
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.used = {tuple(self.segments(e["citation"])) for e in self.lex["entries"] if e.get("citation")}
        self.words: Dict[int, Dict] = {}   # átomos: número → palavra

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

    def wals(self, fid: str, embedded: Dict[str, int]) -> Dict[str, int]:
        values = self.wals_dir / "values.csv" if self.wals_dir else None
        if values and values.exists():
            with open(values, encoding="utf-8", newline="") as f:
                c = Counter(r["Value"] for r in csv.DictReader(f) if r["Parameter_ID"] == fid)
            if c:
                self.sources[fid] = f"WALS {fid} (n={sum(c.values())})"
                return dict(c)
        self.sources[fid] = f"WALS {fid} (embutido)"
        return embedded

    def pick(self, counts: Dict[str, int]) -> str:
        keys = sorted(counts)
        return self.rng.choices(keys, [counts[k] for k in keys])[0]

    def new_word(self, syllables: int = 1) -> Dict:
        for _ in range(60):
            r = self.ph.generate_root(syllables) if not self.eng.skeleton else None
            if r is None:  # raízes consonantais: numerais são palavras livres comuns
                sylls = self.ph.generate_syllables(syllables)
                tones, form = self.ph._with_tones(sylls)
                r = {"segments": [s for syl in sylls for s in syl], "form": form}
            if tuple(r["segments"]) not in self.used:
                self.used.add(tuple(r["segments"]))
                return {"segments": r["segments"], "form": r["form"].replace(".", "") if not self.tonal else r["form"]}
        return {"segments": r["segments"], "form": r["form"]}

    def atom(self, n: int) -> Dict:
        """Palavra simples para um número (do léxico, se existir; senão, nova)."""
        if n not in self.words:
            e = self.entries.get(LEXICON_NUMERALS.get(n, ""))
            if e:
                self.words[n] = {"segments": self.segments(e["citation"]), "form": e["citation"], "from": "lexicon"}
            else:
                syl = 1 if n < 10 or self.rng.random() < 0.6 else 2
                self.words[n] = {**self.new_word(syl), "from": "new"}
        return self.words[n]

    def show(self, ipa: str) -> Dict:
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = " ".join(self.stress.mark(w) for w in ipa.split(" ")) if self.stress else ipa
        return {"written": written, "ipa": ipa, "pronunciation": pron}

    # ── decisões ─────────────────────────────────────────────────────────
    def decide(self, base: Optional[str] = None) -> Dict:
        if base is None:
            base = BASE_131A[self.pick(self.wals("131A", EMBEDDED_131A))]
            if base == "decimal" and self.rng.random() < P_QUINARY_INSIDE_DECIMAL:
                base = "quinary"
        ordinal_code = self.pick(self.wals("53A", EMBEDDED_53A))
        r = self.rng
        s = {
            "base": base,
            # 30 = 'três-dez' (multiplicador antes) ou 'dez-três'
            "multiplier_first": r.random() < 0.75,
            # 37 = 'trinta-e-sete' (maior antes) ou 'sete-e-trinta' (como no alemão e no árabe)
            "high_first": r.random() < 0.7,
            # palavra 'e' entre as partes somadas
            "connective": None,
            # numerais compostos numa palavra só (como 'treze') ou em palavras separadas
            "compound": (not self.isolating and not self.tonal and r.random() < 0.5),
            "ordinal_code": ordinal_code,
        }
        # Se a ordem da soma e a da multiplicação forem opostas, 13 ('três dez') e 30
        # ('três dez') ficariam iguais; nesse caso a soma ganha sempre um conectivo.
        collision = s["multiplier_first"] != s["high_first"]
        if collision or r.random() < 0.3:
            conj = self.entries.get("AND")
            s["connective"] = (self.segments(conj["citation"]) if conj else self.new_word()["segments"])
            if collision:
                self.notes.append("conectivo obrigatório na soma, para distinguir 13 de 30")
        if base == "restricted":
            s["limit"] = r.choice([3, 4, 5])
            s["many"] = self.entries["MANY"]["citation"] if "MANY" in self.entries else "".join(self.new_word()["segments"])
        if base == "body_part":
            parts = [g for g in BODY_SEQUENCE if g in self.entries]
            if len(parts) < 3:
                self.notes.append("o léxico tem poucas partes do corpo: usando sistema restrito")
                s["base"] = "restricted"
                s["limit"] = 5
                s["many"] = self.entries["MANY"]["citation"] if "MANY" in self.entries else "".join(self.new_word()["segments"])
            else:
                s["body_parts"] = parts
                s["limit"] = 5 + len(parts)
                s["many"] = self.entries["MANY"]["citation"] if "MANY" in self.entries else "".join(self.new_word()["segments"])
        # ordinais
        oc = ordinal_code
        if oc == "1":
            s["ordinal"] = {"type": "none"}
        elif oc == "2":
            s["ordinal"] = {"type": "same"}
        else:
            ordinal = {"type": "derived"}
            if self.isolating:
                ordinal["marker"] = self.new_word()["segments"]
                ordinal["position"] = "before" if r.random() < 0.5 else "after"
            else:
                pos = "prefix" if self.catdata["metadata"]["typology"]["affix_position"] in (
                    "weakly_prefixing", "strongly_prefixing") else "suffix"
                ordinal["affix"] = self.ph.generate_affix(pos)["segments"]
                ordinal["position"] = pos
            if oc in ("3", "5", "6", "7"):
                ordinal["first"] = self.new_word(2)["segments"]  # 'primeiro' supletivo
            if oc == "7":
                ordinal["second"] = self.new_word(2)["segments"]
            if oc == "3":
                ordinal["only_first"] = True  # 'primeiro, dois, três'
            s["ordinal"] = ordinal
        self.settings = s
        return s

    # ── composição ───────────────────────────────────────────────────────
    def decompose(self, n: int) -> List[Tuple]:
        """Número → lista de partes: ('atom', k) | ('mul', k, base) | ('add', [...])."""
        b = self.settings["base"]
        if b in ("restricted", "body_part"):
            return [("atom", n)] if n <= self.settings["limit"] else [("many",)]
        if b == "vigesimal":
            powers = [8000, 400, 20]
        elif b == "hybrid":
            powers = [1000, 100, 20] if n >= 100 else [20]
        else:
            powers = [1000, 100, 10]
        parts: List[Tuple] = []
        rest = n
        for p in powers:
            if rest >= p:
                k, rest = divmod(rest, p)
                parts.append(("mul", k, p))
        if rest:
            if rest > 10 and b in ("vigesimal", "hybrid"):  # 11–19: dez + n
                parts.append(("mul", 1, 10))
                rest -= 10
            if rest > 5 and b == "quinary":
                parts.append(("five_plus", rest - 5))
            else:
                parts.append(("atom", rest))
        return parts

    def render_part(self, part: Tuple) -> Tuple[List[List[str]], str]:
        """Uma parte → palavras (listas de fonemas) e glosa."""
        kind = part[0]
        if kind == "atom":
            return [self.atom(part[1])["segments"]], str(part[1])
        if kind == "many":
            return [self.segments(self.settings["many"])], "many"
        if kind == "five_plus":
            return [self.atom(5)["segments"], self.atom(part[1])["segments"]], f"5+{part[1]}"
        k, base = part[1], part[2]
        base_w = self.atom(base)["segments"]
        if k == 1:
            return [base_w], str(base)
        if k < 10 and not (self.settings["base"] == "quinary" and k > 5):
            mult_words = [self.atom(k)["segments"]]
        else:  # multiplicador composto: 7 = 5+2 (quinário), 15 = 10+5 (vigesimal)
            mult_words = [w for p in self.decompose(k) for w in self.render_part(p)[0]]
        words = mult_words + [base_w] if self.settings["multiplier_first"] else [base_w] + mult_words
        return words, f"{k}×{base}"

    def number(self, n: int) -> Dict:
        """Forma de um número qualquer, com glosa da composição."""
        s = self.settings
        if s["base"] == "body_part" and 5 < n <= s["limit"]:
            e = self.entries[s["body_parts"][n - 6]]
            ipa = e["citation"]
            return {"n": n, **self.show(ipa), "gloss": f"'{e['english'].split(' (')[0]}'", "parts": 1}
        parts = self.decompose(n)
        rendered = [self.render_part(p) for p in parts]
        if not s["high_first"]:
            rendered = list(reversed(rendered))
        words: List[List[str]] = []
        glosses = []
        for i, (ws, g) in enumerate(rendered):
            if i and s.get("connective"):
                words.append(list(s["connective"]))
            words += ws
            glosses.append(g)
        if s["compound"] and len(words) > 1:
            morphs = [{"segs": list(w), "role": "root" if i == 0 else "suffix", "label": "", "sep": "-"}
                      for i, w in enumerate(words)]
            morphs, _, _ = self.eng.resolve(morphs)
            ipa = "".join(x for m in morphs for x in m["segs"])
        else:
            ipa = " ".join(self.join_tonal(w) for w in words)
        return {"n": n, **self.show(ipa), "gloss": " + ".join(glosses), "parts": len(words)}

    def join_tonal(self, segs: List[str]) -> str:
        """Em línguas tonais, recupera a forma com tons da palavra simples."""
        for w in self.words.values():
            if w["segments"] == segs:
                return w["form"].replace(".", "") if not self.tonal else w["form"]
        return "".join(segs)

    def ordinal(self, n: int) -> Optional[Dict]:
        o = self.settings["ordinal"]
        if o["type"] == "none":
            return None
        card = self.number(n)
        if o["type"] == "same" or (o.get("only_first") and n != 1):
            return {**card, "n": n}
        if n == 1 and o.get("first"):
            return {"n": 1, **self.show("".join(o["first"])), "gloss": "first (supletivo)"}
        if n == 2 and o.get("second"):
            return {"n": 2, **self.show("".join(o["second"])), "gloss": "second (supletivo)"}
        if "affix" in o:
            last = card["ipa"].split(" ")
            segs = self.segments(last[-1] if o["position"] == "suffix" else last[0])
            morphs = ([{"segs": segs, "role": "root", "label": "", "sep": "-"},
                       {"segs": list(o["affix"]), "role": "suffix", "label": "", "sep": "-"}]
                      if o["position"] == "suffix" else
                      [{"segs": list(o["affix"]), "role": "prefix", "label": "", "sep": "-"},
                       {"segs": segs, "role": "root", "label": "", "sep": "-"}])
            morphs, _, _ = self.eng.resolve(morphs)
            w = "".join(x for m in morphs for x in m["segs"])
            ipa = " ".join(last[:-1] + [w]) if o["position"] == "suffix" else " ".join([w] + last[1:])
            return {"n": n, **self.show(ipa), "gloss": f"{n}-ORD"}
        m = "".join(o["marker"])
        ipa = f"{m} {card['ipa']}" if o["position"] == "before" else f"{card['ipa']} {m}"
        return {"n": n, **self.show(ipa), "gloss": f"ORD {n}"}

    # ── construção ───────────────────────────────────────────────────────
    def build(self, base: Optional[str] = None, upto: int = 20) -> Dict:
        s = self.decide(base)
        listing = list(range(1, upto + 1))
        extra = [30, 37, 40, 50, 60, 80, 90, 99, 100, 256, 1000]
        if s["base"] in ("restricted", "body_part"):
            listing = list(range(1, s["limit"] + 2))
            extra = [20]
        cardinals = [self.number(n) for n in listing + [x for x in extra if x not in listing]]
        ordinals = [o for o in (self.ordinal(n) for n in range(1, 6)) if o]
        atoms = {str(k): {"form": v["form"], "from": v["from"], **self.show(v["form"].replace(".", "") if not self.tonal else v["form"])}
                 for k, v in sorted(self.words.items())}
        return {"settings": s, "atoms": atoms, "cardinals": cardinals, "ordinals": ordinals,
                "metadata": {"seed": self.seed, "sources": self.sources, "notes": self.notes,
                             "new_words": sum(1 for v in self.words.values() if v["from"] == "new")}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

ORDINAL_PT = {"1": "sem ordinais (usa-se o cardinal ou uma perífrase)",
              "2": "ordinais iguais aos cardinais ('dois' = 'segundo')",
              "3": "só 'primeiro' é especial; os demais são iguais aos cardinais",
              "4": "todos derivados ('um-ésimo', 'dois-ésimo')",
              "5": "'primeiro' ou 'um-ésimo'; os demais derivados",
              "6": "'primeiro' supletivo; os demais derivados (como no inglês: first, fourth)",
              "7": "'primeiro' e 'segundo' supletivos; os demais derivados (como no português)",
              "8": "formação variada"}


def describe(data: Dict, sp) -> List[str]:
    s = data["settings"]
    lines = [f"Base: {BASE_PT[s['base']]}"]
    if s["base"] not in ("restricted", "body_part"):
        lines.append("Ordem: " + ("multiplicador antes da base ('três-dez' = 30)" if s["multiplier_first"]
                                   else "base antes do multiplicador ('dez-três' = 30)")
                     + "; " + ("maior antes ('trinta-e-sete')" if s["high_first"]
                               else "menor antes ('sete-e-trinta', como no alemão)"))
        lines.append("Numerais compostos " + ("numa palavra só" if s["compound"] else "em palavras separadas")
                     + (f", ligados por *{sp(''.join(s['connective']))}* ('e')" if s.get("connective") else ""))
    else:
        lines.append(f"Numerais até {s['limit']}; acima disso, *{sp(s['many'])}* ('muitos')"
                     if s.get("many") else f"Numerais até {s['limit']}")
    lines.append("Ordinais: " + ORDINAL_PT[s["ordinal_code"]])
    return lines


def write_markdown(path: Path, data: Dict, sp) -> None:
    lines = ["# Sistema numeral", ""] + [f"- {l}" for l in describe(data, sp)]
    lines += ["", "## Numerais", "", "| Número | Numeral | Pronúncia | Composição |", "|---|---|---|---|"]
    for c in data["cardinals"]:
        lines.append(f"| {c['n']} | **{c['written']}** | /{c['pronunciation']}/ | {c['gloss']} |")
    if data["ordinals"]:
        lines += ["", "## Ordinais", "", "| Número | Ordinal | Pronúncia |", "|---|---|---|"]
        for o in data["ordinals"]:
            lines.append(f"| {o['n']}º | **{o['written']}** | /{o['pronunciation']}/ |")
    for n in data["metadata"]["notes"]:
        lines += ["", f"Nota: {n}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera o sistema numeral da conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--base", choices=list(BASE_PT), help="força a base (sorteada se omitida)")
    ap.add_argument("--upto", type=int, default=20, help="lista os numerais de 1 até N (além de exemplos maiores)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    ap.add_argument("--no-wals", action="store_true")
    args = ap.parse_args()

    wals = None if args.no_wals or not args.wals.exists() else args.wals
    b = NumeralBuilder(args.language, args.seed, wals)
    data = json.loads(json.dumps(b.build(args.base, args.upto)))
    sp = (lambda x: b.ortho.spell(x)) if b.ortho else (lambda x: x)
    (args.language / "numerals.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "numerals.md", data, sp)

    print("\nSISTEMA NUMERAL")
    for l in describe(data, sp):
        print(f"  {l}")
    show = [c for c in data["cardinals"] if c["n"] in (1, 2, 5, 6, 7, 10, 11, 13, 20, 30, 37, 99, 100, 1000)]
    for c in show:
        print(f"    {c['n']:>5}  {c['written']:<30} /{c['pronunciation']}/  ({c['gloss']})")
    for o in data["ordinals"][:3]:
        print(f"    {o['n']:>4}º  {o['written']:<30} /{o['pronunciation']}/")
    for n in data["metadata"]["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Numerais salvos em '{args.language / 'numerals.json'}' e 'numerals.md'.")


if __name__ == "__main__":
    main()
