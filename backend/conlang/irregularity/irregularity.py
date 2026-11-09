"""
Módulo — Irregularidades.

Dá à conlang as irregularidades das línguas reais, concentradas, como nelas,
nas palavras mais frequentes:

    supletivismo     — uma raiz totalmente diferente em parte do paradigma
                       (ir → fui; pessoa → gente; bom → melhor)
    apofonia         — a vogal da raiz muda no lugar do afixo (sing → sang;
                       foot → feet)
    plural zero      — o plural é igual ao singular (sheep → sheep)
    alternâncias     — efeitos das mudanças sonoras que atingem só algumas
                       formas do paradigma (alemão Hund [hunt] / Hunde [hundə])

A quantidade depende da língua: fusionais têm muitas irregularidades;
aglutinantes, poucas; isolantes, quase nenhuma.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
do motor morfológico, das mudanças sonoras, da ortografia e do acento.

Uso:
    python irregularity/irregularity.py --language languages/lang-31

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
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("phonotactics", "morphological_engine", "orthography", "stress", "sound_changes"):
    sys.path.insert(0, str(ROOT / folder))
from morphological_engine import MorphologicalEngine, gloss as mgloss  # noqa: E402

try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import stress as stress_mod  # noqa: E402
except ImportError:
    stress_mod = None
try:
    import sound_changes as sound_mod  # noqa: E402
except ImportError:
    sound_mod = None

TONE_LETTERS = "˥˦˧˨˩"

# Palavras mais frequentes, em ordem: são as que tendem a ser irregulares
# (Bybee 1985: a frequência protege formas antigas da regularização)
FREQUENT = {
    "verb": ["GO", "COME", "GIVE", "SEE", "SAY", "EAT", "DO OR MAKE", "TAKE", "KNOW", "DIE", "SIT",
             "STAND", "HEAR", "DRINK", "HOLD", "SLEEP", "KILL", "FALL", "BE ALIVE", "LIE (REST)"],
    "noun": ["PERSON", "CHILD (YOUNG HUMAN)", "WOMAN", "MALE PERSON", "EYE", "HAND", "ARM OR HAND",
             "FOOT", "TOOTH", "DAY (NOT NIGHT)", "HOUSE", "HEAD", "WATER", "FIRE", "DOG", "TREE",
             "MOTHER", "FATHER", "NAME", "STONE"],
    "adjective": ["GOOD", "BAD", "BIG", "SMALL", "MANY", "OLD", "LONG", "FAR", "NEAR", "NEW"],
}

# Quantas palavras irregulares, por grau de fusão (aproximação)
COUNT_BY_FUSION = {"fusional": (6, 10), "agglutinative": (2, 5), "none": (0, 2)}

TYPE_WEIGHTS = {
    "verb": {"suppletion": 0.5, "ablaut": 0.5},
    "noun": {"suppletion": 0.3, "ablaut": 0.35, "zero": 0.35},
}

TYPE_PT = {"suppletion": "supletivismo", "ablaut": "apofonia", "zero": "plural zero",
           "suppletive_comparative": "comparativo supletivo"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def short(e: Dict) -> str:
    label = (e.get("label") or e["english"].split(" (")[0]).split("/")[0]
    return label[3:] if label.startswith("to ") else label


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class IrregularityBuilder:
    def __init__(self, language_dir: Path, seed: Optional[int] = None):
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
        self.cats = self.catdata["categories"]
        typology = _load(d / "morphological_typology.json") or {}
        self.comparison = _load(d / "comparison.json")
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "irregularity") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.notes: List[str] = []

        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.catdata, typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(self.seed + 1)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation") and e.get("root")}
        self.used = {tuple(e["root"]) for e in self.lex["entries"] if e.get("root")}
        self.fusion = self.catdata["metadata"]["typology"]["fusion"]
        self.skeleton = self.eng.skeleton
        self.vowels = {nfd(v["ipa"]) for v in self.inv["vowels"]}
        self.short_vowels = list(self.eng._short_plain_vowels())

    # ── utilidades ───────────────────────────────────────────────────────
    def segments(self, form: str) -> List[str]:
        syms = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]}, key=len, reverse=True)
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ"), 0
            while i < len(s):
                hit = next((x for x in syms if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    @staticmethod
    def lexeme(e: Dict, root: Optional[List[str]] = None) -> Dict:
        r = root if root is not None else e["root"]
        return {"root": r, "form": "".join(r), "tones": e.get("tones", []),
                "class": e.get("class") or 0, "gender": e.get("gender")}

    def show(self, ipa: str) -> Dict:
        written = self.ortho.spell(ipa) if self.ortho else ipa
        pron = " ".join(self.stress.mark(w) for w in ipa.split(" ")) if self.stress else ipa
        return {"written": written, "ipa": ipa, "pronunciation": pron}

    def phrase(self, e: Dict, domain: str, feats: Dict, root: Optional[List[str]] = None) -> str:
        return self.eng.inflect(self.lexeme(e, root), domain, feats)["phrase"]

    def new_root(self, like: List[str]) -> List[str]:
        """Raiz nova (para o supletivismo), do tamanho aproximado da original."""
        if self.skeleton:
            for _ in range(40):
                r = self.ph.generate_skeleton()["segments"]
                if tuple(r) not in self.used:
                    self.used.add(tuple(r))
                    return r
            return r
        n = max(1, min(2, len(self.ph.syllabify(like) or [like])))
        for _ in range(60):
            r = self.ph.generate_root(n)["segments"]
            if tuple(r) not in self.used:
                self.used.add(tuple(r))
                return r
        return r

    def ablaut(self, root: List[str]) -> Optional[List[str]]:
        """Troca a última vogal da raiz por outra (sing → sang)."""
        if self.skeleton or len(self.short_vowels) < 2:
            return None
        idx = max((i for i, s in enumerate(root) if s.replace("ː", "") in self.short_vowels), default=None)
        if idx is None:
            return None
        old = root[idx]
        base = old.replace("ː", "")
        new = self.rng.choice([v for v in self.short_vowels if v != base])
        if old != base and new + "ː" in self.vowels:
            new += "ː"
        return root[:idx] + [new] + root[idx + 1:]

    # ── qual parte do paradigma é irregular ──────────────────────────────
    def verb_feature(self) -> Optional[Tuple[str, str]]:
        """Tempo passado (como 'went'), senão perfectivo, senão outro valor marcado."""
        for cat, prefer in (("tense", "past"), ("aspect", "perfective"), ("aspect", None), ("mood", None)):
            c = self.cats.get(cat, {})
            if not c.get("grammaticalized") or c.get("realization") not in ("affix", "clitic"):
                continue
            vals = [v for v in c["values"] if v != c["default"]]
            pick = next((v for v in vals if prefer and prefer in v), vals[0] if vals else None)
            if pick:
                return cat, pick
        return None

    def noun_feature(self) -> Optional[Tuple[str, str]]:
        c = self.cats.get("number", {})
        if not c.get("grammaticalized") or c.get("realization") not in ("affix", "clitic", "stem_change",
                                                                         "reduplication", "tone"):
            return None
        vals = [v for v in c["values"] if v != c["default"]]
        return ("number", "plural" if "plural" in vals else vals[0]) if vals else None

    # ── construção ───────────────────────────────────────────────────────
    def build(self) -> Dict:
        lo, hi = COUNT_BY_FUSION.get(self.fusion, (2, 5))
        if self.catdata["metadata"]["typology"]["synthesis"] == "isolating":
            lo, hi = COUNT_BY_FUSION["none"]
        target = self.rng.randint(lo, hi)
        vf, nf = self.verb_feature(), self.noun_feature()
        comp = self.comparison["settings"] if self.comparison else None
        comp_ok = bool(comp and comp["degree"]["type"] in ("affix", "word"))

        # candidatos, alternando classes, sempre dos mais frequentes para os menos
        queues = {"verb": [g for g in FREQUENT["verb"] if g in self.entries and vf
                           and self.entries[g]["pos"] == "verb"],
                  "noun": [g for g in FREQUENT["noun"] if g in self.entries and nf
                           and self.entries[g]["pos"] == "noun"],
                  "adjective": [g for g in FREQUENT["adjective"] if g in self.entries and comp_ok
                                and (self.entries[g]["pos"] == "adjective"
                                     or self.entries[g].get("transitivity") == "stative")]}
        irregulars: List[Dict] = []
        order = ["verb", "noun", "adjective"]
        i = 0
        while len(irregulars) < target and any(queues.values()):
            pos = order[i % 3]
            i += 1
            if not queues[pos]:
                continue
            gloss = queues[pos].pop(0)
            item = self.make(self.entries[gloss], pos, vf if pos == "verb" else nf, comp)
            if item:
                irregulars.append(item)
        if not irregulars:
            self.notes.append("nenhuma irregularidade: a língua tem pouca ou nenhuma flexão "
                              "(como as línguas isolantes)")
        alternations = self.alternations(vf, nf)
        return {"irregulars": irregulars, "alternations": alternations,
                "settings": {"target": target, "verb_feature": vf, "noun_feature": nf},
                "metadata": {"seed": self.seed, "notes": self.notes,
                             "irregular_count": len(irregulars), "alternation_count": len(alternations)}}

    def make(self, e: Dict, pos: str, feat: Optional[Tuple[str, str]], comp: Optional[Dict]) -> Optional[Dict]:
        """Uma palavra irregular: tipo, parte afetada do paradigma, forma regular e irregular."""
        base = {"gloss": e["gloss"], "label": short(e), "pos": pos, "citation": e["citation"]}
        if pos == "adjective":
            return self.comparative(e, comp, base)
        cat, value = feat
        domain = pos
        weights = dict(TYPE_WEIGHTS[pos])
        if self.skeleton:
            weights.pop("ablaut", None)
        kind = self.rng.choices(list(weights), list(weights.values()))[0]
        feats = {cat: value}
        regular = self.phrase(e, domain, feats)
        if kind == "suppletion":
            root = self.new_root(e["root"])
            irregular = self.phrase(e, domain, feats, root)
            extra = {"root": root}
        elif kind == "ablaut":
            root = self.ablaut(e["root"])
            if not root:
                return None
            # a mudança de vogal substitui o afixo: 'sang', não 'sanged'
            default = self.cats[cat]["default"]
            irregular = self.phrase(e, domain, {cat: default}, root)
            extra = {"root": root, "replaces_affix": True}
        else:  # plural zero
            default = self.cats[cat]["default"]
            irregular = self.phrase(e, domain, {cat: default})
            extra = {}
        if irregular == regular:
            return None
        label = f"{short(e).replace(' ', '.')}-{mgloss(value)}"
        return {**base, "type": kind, "features": feats, "label_gloss": label,
                "regular": self.show(regular), "irregular": self.show(irregular), **extra}

    def comparative(self, e: Dict, comp: Optional[Dict], base: Dict) -> Optional[Dict]:
        """Comparativo supletivo: 'bom' → 'melhor' em vez de 'bom-COMPR'."""
        if not comp:
            return None
        d = comp["degree"]
        adj = self.segments(e["citation"]) if self.skeleton else list(e["root"])
        if d["type"] == "affix":
            morphs = ([{"segs": list(d["comparative"]), "role": "prefix", "label": "", "sep": "-"},
                       {"segs": adj, "role": "root", "label": "", "sep": "-"}] if d["position"] == "prefix" else
                      [{"segs": adj, "role": "root", "label": "", "sep": "-"},
                       {"segs": list(d["comparative"]), "role": "suffix", "label": "", "sep": "-"}])
            morphs, _, _ = self.eng.resolve(morphs)
            regular = "".join(s for m in morphs for s in m["segs"])
        else:
            regular = f"{''.join(d['comparative'])} {e['citation']}"
        root = self.new_root(e["root"])
        irregular = "".join(root)
        out = {**base, "type": "suppletive_comparative", "features": {"degree": "comparative"},
               "label_gloss": f"{short(e)}.COMPR", "regular": self.show(regular),
               "irregular": self.show(irregular), "root": root}
        sup = comp["superlative"]
        if sup["type"] == "affix":  # o superlativo usa a mesma raiz supletiva: best = bett-est
            morphs = ([{"segs": list(sup["form"]), "role": "prefix", "label": "", "sep": "-"},
                       {"segs": root, "role": "root", "label": "", "sep": "-"}] if sup["position"] == "prefix" else
                      [{"segs": root, "role": "root", "label": "", "sep": "-"},
                       {"segs": list(sup["form"]), "role": "suffix", "label": "", "sep": "-"}])
            morphs, _, _ = self.eng.resolve(morphs)
            out["superlative"] = self.show("".join(s for m in morphs for s in m["segs"]))
        return out

    # ── alternâncias criadas pelas mudanças sonoras ──────────────────────
    def alternations(self, vf, nf, limit: int = 8) -> List[Dict]:
        """
        Aplica as mudanças sonoras às formas flexionadas: quando uma regra atinge o
        radical em uma forma e não em outra, surge uma alternância (Hund/Hunde).
        """
        sc_data = _load(self.dir / "sound_changes.json")
        if not (sc_data and sound_mod and sc_data.get("rules")):
            return []
        sc = sound_mod.SoundChanger(self.dir)
        rules = []
        for r in sc_data["rules"]:
            try:
                rules.append(sound_mod.Rule(r["text"], sc.symbols, r["source"]))
            except ValueError:
                continue
        out: List[Dict] = []
        for pos, feat in (("noun", nf), ("verb", vf)):
            if not feat:
                continue
            cat, value = feat
            default = self.cats[cat]["default"]
            for e in [x for x in self.entries.values() if x["pos"] == pos][:80]:
                forms = []
                for v in (default, value):
                    under = self.eng.inflect(self.lexeme(e), pos, {cat: v})["surface"]
                    changed, applied = sc.evolve(under, rules)
                    forms.append({"value": v, "underlying": under, "phonetic": changed, "rules": applied})
                # alternância: o radical (comparado fonema a fonema) sai diferente nas duas
                # formas depois das mudanças; mudanças só no afixo não contam
                n = len(e["root"]) if not self.skeleton else 0
                stems = [sc.split(f["phonetic"])[0][:n] for f in forms]
                if n and forms[0]["rules"] != forms[1]["rules"] and stems[0] != stems[1]:
                    out.append({"gloss": e["gloss"], "label": short(e), "pos": pos, "category": cat,
                                "forms": [{**f, "written": self.show(f["underlying"])["written"]} for f in forms]})
                if len([x for x in out if x["pos"] == pos]) >= limit // 2:
                    break
        return out


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

POS_PT = {"verb": "verbo", "noun": "nome", "adjective": "adjetivo"}


def write_markdown(path: Path, data: Dict) -> None:
    m = data["metadata"]
    lines = ["# Irregularidades", "",
             f"{m['irregular_count']} palavras irregulares, todas entre as mais frequentes da língua"
             + (f"; {m['alternation_count']} alternâncias criadas pelas mudanças sonoras" if m["alternation_count"] else "")
             + ".", ""]
    if data["irregulars"]:
        lines += ["## Palavras irregulares", "",
                  "| Palavra | Tipo | Forma | Regular seria | Irregular |", "|---|---|---|---|---|"]
        for x in data["irregulars"]:
            extra = f"; superlativo **{x['superlative']['written']}**" if x.get("superlative") else ""
            lines.append(f"| '{x['label']}' ({POS_PT[x['pos']]}) | {TYPE_PT[x['type']]} | {x['label_gloss']} | "
                         f"~~{x['regular']['written']}~~ | **{x['irregular']['written']}** "
                         f"/{x['irregular']['pronunciation']}/{extra} |")
    if data["alternations"]:
        lines += ["", "## Alternâncias das mudanças sonoras", "",
                  "As regras de mudança sonora atingem o radical em uma forma e não na outra:", ""]
        for a in data["alternations"]:
            parts = [f"{mgloss(f['value']) or f['value']} *{f['written']}* /{f['underlying']}/ [{f['phonetic']}]"
                     for f in a["forms"]]
            lines.append(f"- '{a['label']}': " + " · ".join(parts))
    for n in m["notes"]:
        lines += ["", f"Nota: {n}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera as irregularidades da conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    args = ap.parse_args()

    b = IrregularityBuilder(args.language, args.seed)
    data = json.loads(json.dumps(b.build()))
    (args.language / "irregularity.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "irregularity.md", data)

    m = data["metadata"]
    print(f"\nIRREGULARIDADES — {m['irregular_count']} palavras irregulares, "
          f"{m['alternation_count']} alternâncias")
    for x in data["irregulars"]:
        sup = f", superlativo {x['superlative']['written']}" if x.get("superlative") else ""
        print(f"  '{x['label']}' {TYPE_PT[x['type']]:<22} {x['label_gloss']:<16} "
              f"{x['regular']['written']} → {x['irregular']['written']}{sup}")
    for a in data["alternations"][:4]:
        print(f"  alternância '{a['label']}': " + " · ".join(f"[{f['phonetic']}]" for f in a["forms"]))
    for n in m["notes"]:
        print(f"  · {n}")
    print(f"\n[OK] Irregularidades salvas em '{args.language / 'irregularity.json'}' e 'irregularity.md'.")


if __name__ == "__main__":
    main()
