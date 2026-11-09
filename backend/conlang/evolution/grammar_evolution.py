"""
Evolução da gramática (etapa 3 do módulo de evolução).

Roda sobre uma língua-filha já criada pelas etapas 1 e 2 (evolution.py) e aplica
as mudanças gramaticais que acompanham a história real das línguas:

    erosão            afixos que as leis fonéticas apagaram levam a categoria junto
                      (o latim perdeu os casos quando as terminações se desgastaram);
                      afixos que ficaram iguais viram sincretismo
    gramaticalização  palavras viram gramática (Heine & Kuteva 2002):
                        demonstrativo → artigo definido   (latim ille → francês le)
                        'um' → artigo indefinido          (latim unus → un)
                        'ir' → futuro                     (inglês going to, francês je vais)
                        partícula → afixo                 (latim cantare habeo → cantarei)
    ordem             deriva da ordem básica (o latim SOV virou SVO nas românicas);
                      as adposições acompanham mais devagar
    irregularidades   formas antigas que as leis fonéticas transformaram de outro jeito
                      (inglês foot/feet, alemão Hund [hʊnt] / Hunde [hʊndə])

Não altera nenhum outro módulo nem as etapas 1 e 2: lê e reescreve só os JSONs
da língua-filha.

Uso:
    python evolution/grammar_evolution.py --language languages/lang-31-germanic-1500
    python evolution/grammar_evolution.py --language languages/lang-31-germanic-1500 --rebuild

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
for folder in ("phonotactics", "morphological_engine", "syntax", "generate_language", "orthography"):
    sys.path.insert(0, str(ROOT / folder))

from morphological_engine import MorphologicalEngine, gloss as mgloss  # noqa: E402
import syntax as syn_mod  # noqa: E402
import evolution as evo_mod  # noqa: E402

TONE_LETTERS = "˥˦˧˨˩"

# Taxas por milênio (aproximações a partir de estudos de mudança gramatical)
RATES = {
    "particle_to_affix": 0.35,   # partículas junto ao verbo/nome viram afixos
    "article_definite": 0.25,    # demonstrativo → artigo definido
    "article_indefinite": 0.6,   # dado o definido, 'um' → indefinido
    "future_go": 0.30,           # 'ir' → futuro
}
# Deriva da ordem básica, por milênio (Dryer; Gell-Mann & Ruhlen 2011: SOV → SVO é a mais comum)
ORDER_DRIFT = {"SOV": [("SVO", 0.12)], "VSO": [("SVO", 0.10)], "VOS": [("SVO", 0.10)],
               "OVS": [("SOV", 0.20)], "OSV": [("SOV", 0.20)], "SVO": [("SOV", 0.02)]}
FREQUENT = ["GO", "COME", "GIVE", "SEE", "SAY", "EAT", "DO OR MAKE", "TAKE", "KNOW", "DIE", "SIT", "STAND",
            "HEAR", "DRINK", "PERSON", "CHILD (YOUNG HUMAN)", "WOMAN", "MALE PERSON", "EYE", "HAND", "FOOT",
            "TOOTH", "HOUSE", "HEAD", "DOG", "FIRE", "WATER", "MOTHER", "FATHER", "NAME", "GOOD", "BIG"]
SKIP_AFFIXATION = {"definiteness", "classifiers"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _save(path: Path, data: Dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def chance(rate: float, years: int) -> float:
    return 1 - math.exp(-rate * years / 1000)


def cell_key(cats: List[str], values: List[str]) -> str:
    return "|".join(f"{c}={v}" for c, v in zip(cats, values))


class GrammarEvolver:
    def __init__(self, daughter: Path, seed: Optional[int] = None):
        self.dir = daughter
        self.evo = _load(daughter / "evolution.json")
        if not self.evo:
            raise SystemExit(f"{daughter} não tem evolution.json: crie a língua-filha com evolution.py primeiro.")
        self.parent_dir = daughter.parent / self.evo["parent"]
        names = ("morphological_typology", "phonemic_inventory", "phonotactics", "grammatical_categories",
                 "morphology", "lexicon", "syntax")
        # Cópia do estado das etapas 1 e 2: rodar a etapa 3 de novo parte sempre dela
        # (o resultado não se acumula e a mesma semente dá o mesmo resultado).
        # Se o evolution.json não tem a chave "grammar", os arquivos atuais vêm direto das
        # etapas 1 e 2 (a filha acabou de ser criada ou refeita): o retrato é renovado.
        snap = daughter / ".before_grammar"
        if "grammar" not in self.evo or not snap.exists():
            snap.mkdir(exist_ok=True)
            for k in names:
                if (daughter / f"{k}.json").exists():
                    (snap / f"{k}.json").write_text((daughter / f"{k}.json").read_text(encoding="utf-8"),
                                                    encoding="utf-8")
        self.f = {k: _load(snap / f"{k}.json") for k in names}
        self.p = {k: _load(self.parent_dir / f"{k}.json") for k in ("morphology", "lexicon")}
        if not all(self.f[k] for k in names[1:]):
            raise SystemExit(f"A pasta {daughter} está incompleta.")
        self.years = self.evo["years"]
        self.seed = seed if seed is not None else derive_seed(self.evo["metadata"]["seed"], "grammar")
        self.rng = random.Random(self.seed)
        inv = self.f["phonemic_inventory"]
        self.phonemes = {nfd(x["ipa"]) for x in inv["consonants"] + inv["vowels"]}
        self.vowels = {nfd(x["ipa"]) for x in inv["vowels"]}
        self.symbols = sorted(self.phonemes, key=len, reverse=True)
        self.events: List[Dict] = []

    # ── utilidades ───────────────────────────────────────────────────────
    def segments(self, form: str) -> List[str]:
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ -"), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def reduce(self, segs: List[str]) -> List[str]:
        """Redução fonética da gramaticalização: a palavra encolhe para a primeira sílaba (CV)."""
        nuc = next((i for i, s in enumerate(segs) if s in self.vowels), None)
        return segs[:nuc + 1] if nuc is not None and len(segs) > nuc + 1 else list(segs)

    def entry(self, gloss: str) -> Optional[Dict]:
        return next((e for e in self.f["lexicon"]["entries"] if e["gloss"] == gloss and e.get("citation")), None)

    def event(self, kind: str, year_frac: Tuple[float, float], **data) -> None:
        y = round(self.rng.uniform(*year_frac) * self.years / 50) * 50
        self.events.append({"type": kind, "year": y, **data})

    def rebuild_template(self, domain: str) -> None:
        sl = self.f["grammatical_categories"]["slots"][domain]
        sl["template"] = "-".join([p["name"] for p in sl["prefixes"]] + ["ROOT"] + [s["name"] for s in sl["suffixes"]])

    # ── 1. erosão: categorias perdidas e sincretismos ────────────────────
    def erosion(self) -> None:
        cats = self.f["grammatical_categories"]["categories"]
        parent_slots = {(d, s["name"]): s for d, slots in self.p["morphology"]["affixes"].items() for s in slots}
        for domain, slots in self.f["morphology"]["affixes"].items():
            for slot in list(slots):
                if len(slot["categories"]) != 1:
                    continue
                cat = slot["categories"][0]
                c = cats.get(cat, {})
                default = c.get("default")
                old = parent_slots.get((domain, slot["name"]))
                if not old:
                    continue
                cells = {cls: {k: v for k, v in forms.items() if not k.endswith(f"={default}")}
                         for cls, forms in slot["forms"].items()}
                old_cells = {cls: {k: v for k, v in forms.items() if not k.endswith(f"={default}")}
                             for cls, forms in old["forms"].items()}
                had = any(v for forms in old_cells.values() for v in forms.values())
                has = any(v for forms in cells.values() for v in forms.values())
                if had and not has:  # todos os afixos marcados se apagaram: a categoria some
                    slots.remove(slot)
                    sl = self.f["grammatical_categories"]["slots"][domain]
                    for key in ("prefixes", "suffixes"):
                        sl[key] = [x for x in sl[key] if x["name"] != slot["name"]]
                    self.rebuild_template(domain)
                    cats[cat] = {"grammaticalized": False,
                                 "source": f"perdida por erosão fonética ({self.evo['daughter']})"}
                    self.event("category_lost", (0.5, 0.95), category=cat,
                               note=f"os afixos de {cat} se apagaram com as mudanças fonéticas",
                               example="latim: as terminações de caso se desgastaram e as línguas românicas perderam os casos")
                    continue
                # sincretismo: valores que eram distintos e ficaram iguais
                for cls, forms in cells.items():
                    old_forms = old_cells.get(cls, {})
                    seen: Dict[str, str] = {}
                    for k, v in forms.items():
                        sig = "".join(v)
                        if not v:
                            continue
                        if sig in seen and "".join(old_forms.get(seen[sig], [])) != "".join(old_forms.get(k, [])):
                            a, b = seen[sig].split("=")[-1], k.split("=")[-1]
                            self.event("syncretism", (0.4, 0.95), category=cat, values=[a, b], form=sig,
                                       note=f"{mgloss(a) or a} e {mgloss(b) or b} passaram a ter a mesma forma (-{sig})",
                                       example="inglês antigo: dativo e acusativo se fundiram (him)")
                        seen.setdefault(sig, k)

    # ── 2. gramaticalização ──────────────────────────────────────────────
    def articles(self) -> None:
        cats = self.f["grammatical_categories"]["categories"]
        if cats.get("definiteness", {}).get("grammaticalized"):
            return
        this, one = self.entry("THIS") or self.entry("THAT"), self.entry("ONE")
        if not this or self.rng.random() >= chance(RATES["article_definite"], self.years):
            return
        pos = self.f["syntax"]["settings"]["noun_phrase"].get("demonstrative", "before")
        values = ["unmarked", "definite"]
        forms = {"definite": self.reduce(self.segments(this["citation"]))}
        if one and self.rng.random() < RATES["article_indefinite"]:
            values.append("indefinite")
            forms["indefinite"] = self.reduce(self.segments(one["citation"]))
        cats["definiteness"] = {"grammaticalized": True, "values": values, "default": "unmarked",
                                "zero": ["unmarked"],
                                "markers": {v: {"realization": "article", "position": pos} for v in forms},
                                "realization": "article", "position": pos,
                                "source": "gramaticalização: demonstrativo → artigo (Heine & Kuteva 2002)"}
        self.f["morphology"]["free_markers"]["definiteness"] = {
            "forms": forms, "positions": {v: pos for v in forms}, "realization": {v: "article" for v in forms}}
        self.f["grammatical_categories"]["slots"]["noun"]["free_markers"].append(
            {"category": "definiteness", "realization": "article", "position": pos})
        self.event("grammaticalization", (0.2, 0.6), source="THIS", target="definite article",
                   form="".join(forms["definite"]),
                   note=f"o demonstrativo '{this['label'] if this.get('label') else 'this'}' virou artigo definido",
                   example="latim ille 'aquele' → francês le, português o")
        if "indefinite" in forms:  # o indefinido vem depois do definido, como nas línguas reais
            start = self.events[-1]["year"] / max(1, self.years) + 0.05
            self.event("grammaticalization", (min(start, 0.9), 0.95), source="ONE", target="indefinite article",
                       form="".join(forms["indefinite"]), note="o numeral 'um' virou artigo indefinido",
                       example="latim unus 'um' → francês un, português um")

    def future(self) -> None:
        cats = self.f["grammatical_categories"]["categories"]
        go = self.entry("GO") or self.entry("COME")
        tense = cats.get("tense", {})
        if not go or "future" in tense.get("values", []):
            return
        if self.rng.random() >= chance(RATES["future_go"], self.years):
            return
        ov = self.f["syntax"]["settings"]["word_order"]["object_before_verb"]
        pos = "after" if ov else "before"
        form = self.reduce(self.segments(go["citation"]))
        if tense.get("grammaticalized"):
            tense["values"].append("future")
        else:
            cats["tense"] = {"grammaticalized": True, "values": ["present", "future"], "default": "present",
                             "zero": ["present"], "realization": "particle", "position": pos,
                             "source": "gramaticalização: 'ir' → futuro (Heine & Kuteva 2002)"}
        fm = self.f["morphology"]["free_markers"].setdefault("tense", {"forms": {}, "positions": {}, "realization": {}})
        fm["forms"]["future"] = form
        fm["positions"]["future"] = pos
        fm["realization"]["future"] = "particle"
        vf = self.f["grammatical_categories"]["slots"]["verb"]["free_markers"]
        if not any(x["category"] == "tense" for x in vf):
            vf.append({"category": "tense", "realization": "particle", "position": pos})
        self.event("grammaticalization", (0.4, 0.9), source=go["gloss"], target="future", form="".join(form),
                   note=f"o verbo '{go.get('label') or 'go'}' virou marcador de futuro",
                   example="inglês going to; francês je vais chanter; crioulos")

    def particle_to_affix(self) -> None:
        cats = self.f["grammatical_categories"]["categories"]
        morph = self.f["morphology"]
        for cat in list(morph["free_markers"]):
            if cat in SKIP_AFFIXATION or self.rng.random() >= chance(RATES["particle_to_affix"], self.years):
                continue
            fm = morph["free_markers"].pop(cat)
            domain = "verb" if cat in ("tense", "aspect", "mood", "evidentiality", "negation") else "noun"
            first_pos = next(iter(fm["positions"].values()), "after")
            position = "suffix" if first_pos == "after" else "prefix"
            c = cats.get(cat, {})
            forms = {cell_key([cat], [v]): self.reduce(segs) for v, segs in fm["forms"].items()}
            for v in c.get("values", []):
                forms.setdefault(cell_key([cat], [v]), [])
            slot = {"name": cat, "categories": [cat], "position": position, "realization": "affix",
                    "class_dependent": False, "forms": {"0": forms}}
            slots = morph["affixes"][domain]
            if position == "suffix":
                slots.append(slot)
            else:
                slots.insert(0, slot)
            sl = self.f["grammatical_categories"]["slots"][domain]
            sl["free_markers"] = [x for x in sl["free_markers"] if x["category"] != cat]
            item = {"name": cat, "categories": [cat], "realization": "affix"}
            (sl["suffixes"].append(item) if position == "suffix" else sl["prefixes"].insert(0, item))
            self.rebuild_template(domain)
            if c:
                c["realization"], c["position"] = "affix", position
            self.event("affixation", (0.5, 0.95), category=cat, position=position,
                       forms={k.split("=")[-1]: "".join(v) for k, v in forms.items() if v},
                       note=f"as partículas de {cat} se fundiram ao {'verbo' if domain == 'verb' else 'nome'} como "
                            f"{'sufixos' if position == 'suffix' else 'prefixos'}",
                       example="latim cantare habeo 'tenho a cantar' → português cantarei")
            typ = self.f["morphological_typology"] or {}
            meta = self.f["grammatical_categories"]["metadata"]["typology"]
            if meta.get("synthesis") == "isolating":
                meta["synthesis"] = "synthetic"
                meta["fusion"] = "agglutinative"
                for k in ("degree_of_synthesis", "synthesis"):
                    if k in typ:
                        typ[k] = "synthetic"
                for k in ("degree_of_fusion", "fusion"):
                    if k in typ:
                        typ[k] = "agglutinative"
                self.event("typology", (0.8, 1.0), note="a língua deixou de ser isolante: o ciclo tipológico "
                           "avançou de isolante para aglutinante",
                           example="ciclo tipológico (Hodge 1970): isolante → aglutinante → fusional → isolante")

    # ── 3. ordem das palavras ────────────────────────────────────────────
    def word_order(self) -> None:
        st = self.f["syntax"]["settings"]
        wo = st["word_order"]
        if wo.get("free"):
            return
        for target, rate in ORDER_DRIFT.get(wo["clause"], []):
            if self.rng.random() < chance(rate, self.years):
                old = wo["clause"]
                wo["clause"] = target
                wo["object_before_verb"] = target.index("O") < target.index("V")
                self.event("word_order", (0.3, 0.9), old=old, new=target,
                           note=f"a ordem básica mudou de {old} para {target}",
                           example="latim (SOV) → línguas românicas (SVO); inglês antigo → inglês moderno")
                want = "postpositions" if wo["object_before_verb"] else "prepositions"
                if st.get("adpositions") != want and self.years >= 1500 and self.rng.random() < 0.5:
                    st["adpositions"] = want
                    self.event("word_order", (0.7, 1.0), old=None, new=want,
                               note=f"as adposições acompanharam a nova ordem ({'preposições' if want == 'prepositions' else 'posposições'})",
                               example="as adposições mudam mais devagar que a ordem da oração (Dryer 1992)")
                break

    # ── 4. irregularidades da evolução das palavras inteiras ─────────────
    def irregulars(self, limit: Optional[int] = None) -> None:
        # quanto mais tempo, mais formas antigas sobrevivem como irregulares (de 2 a 10)
        limit = limit if limit is not None else max(2, min(10, round(self.years / 250)))
        chain = [law["id"] for law in self.evo["laws"]]
        if not chain or not self.p["lexicon"]:
            return
        ev = evo_mod.Evolver(self.parent_dir, self.evo["profile"], self.years, laws=chain, lexical=False)
        ev.chain = chain
        parent = {e["gloss"]: e for e in self.p["lexicon"]["entries"] if e.get("inflections")}
        count = 0
        for g in FREQUENT:
            e = self.entry(g)
            pe = parent.get(g)
            if not e or not pe or e.get("note") or count >= limit:
                continue
            for pi in pe["inflections"]:
                if any(ch in TONE_LETTERS for ch in pi["form"]) or " " in pi["form"]:
                    continue
                di = next((x for x in e.get("inflections", []) if x["gloss"] == pi["gloss"]), None)
                if not di:
                    continue
                full = ev.evolve(ev.segments(pi["form"])).segs
                if "".join(full) == di["form"] or not all(nfd(s) in self.phonemes for s in full):
                    continue
                root = "".join(e.get("root") or [])
                if "".join(full).startswith(root) and di["form"].startswith(root):
                    continue  # diferença só no afixo: não torna a palavra irregular
                old = di["form"]
                di["form"], di["irregular"] = "".join(full), True
                e["note"] = (e.get("note") + "; " if e.get("note") else "") + f"{pi['gloss']} irregular, herdado"
                self.event("irregular", (0.6, 1.0), gloss=g, label=e.get("label") or g, tag=pi["gloss"],
                           regular=old, irregular=di["form"],
                           note=f"'{e.get('label') or g}' {pi['gloss']}: a forma antiga evoluiu inteira e ficou irregular",
                           example="inglês antigo fōt / fēt → foot / feet")
                count += 1
                break

    # ── execução ─────────────────────────────────────────────────────────
    def run(self) -> Dict:
        self.erosion()
        self.articles()
        self.future()
        self.particle_to_affix()
        self.word_order()
        self.irregulars()
        f = self.f
        # sintaxe: frases refeitas com a gramática nova
        eng = MorphologicalEngine.load(f["morphology"], f["phonemic_inventory"], f["phonotactics"],
                                       f["grammatical_categories"], f["morphological_typology"] or {})
        if f["morphology"].get("lexicon_sample", {}).get("nouns"):
            f["morphology"]["paradigms"] = {"noun": eng.paradigm(f["morphology"]["lexicon_sample"]["nouns"][0], "noun"),
                                            "verb": eng.paradigm(f["morphology"]["lexicon_sample"]["verbs"][0], "verb")}
        sb = syn_mod.SyntaxBuilder(eng, f["lexicon"], f["morphological_typology"] or {}, syn_mod.Wals(None),
                                   f["syntax"]["metadata"].get("seed"))
        sb.s = {**f["syntax"]["settings"], **f["syntax"].get("function_words", {})}
        f["syntax"]["examples"] = sb.examples()
        for k in ("morphological_typology", "grammatical_categories", "morphology", "lexicon", "syntax"):
            if f[k] is not None:
                _save(self.dir / f"{k}.json", f[k])
        self.events.sort(key=lambda x: x["year"])
        self.evo["grammar"] = {"events": self.events, "seed": self.seed}
        _save(self.dir / "evolution.json", self.evo)
        return self.evo


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

TYPE_PT = {"category_lost": "Perda de categoria", "syncretism": "Sincretismo", "grammaticalization": "Gramaticalização",
           "affixation": "Partícula que virou afixo", "typology": "Ciclo tipológico", "word_order": "Ordem das palavras",
           "irregular": "Irregularidade herdada"}


def markdown_section(evo: Dict, spell=None) -> List[str]:
    sp = spell or (lambda x: x)
    events = evo.get("grammar", {}).get("events", [])
    lines = ["## Gramática", ""]
    if not events:
        return lines + ["Nenhuma mudança gramatical neste período (a gramática pode ficar estável por séculos)."]
    lines += ["| Ano (aprox.) | Mudança | O que aconteceu | Paralelo real |", "|---|---|---|---|"]
    for x in events:
        what = x["note"]
        if x["type"] == "grammaticalization" and x.get("form"):
            what += f": **{sp(x['form'])}** /{x['form']}/"
        if x["type"] == "irregular":
            what += f": ~~{sp(x['regular'])}~~ → **{sp(x['irregular'])}** /{x['irregular']}/"
        if x["type"] == "affixation" and x.get("forms"):
            what += ": " + ", ".join(f"{mgloss(v) or v} -{f}" for v, f in x["forms"].items())
        lines.append(f"| {x['year']} | {TYPE_PT[x['type']]} | {what} | {x['example']} |")
    return lines


def write_markdown(daughter: Path, evo: Dict, spell=None) -> None:
    """Acrescenta (ou substitui) a seção 'Gramática' no evolution.md da filha."""
    path = daughter / "evolution.md"
    text = path.read_text(encoding="utf-8") if path.exists() else f"# Evolução: {evo['parent']} → {evo['daughter']}\n"
    if "\n## Gramática" in text:
        head, _, rest = text.partition("\n## Gramática")
        nxt = rest.find("\n## ")
        text = head + ("" if nxt < 0 else rest[nxt:])
    marker = "\n## Inventário"
    section = "\n" + "\n".join(markdown_section(evo, spell)) + "\n"
    text = text.replace(marker, section + marker, 1) if marker in text else text.rstrip() + "\n" + section
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Evolui a gramática de uma língua-filha (etapa 3).")
    ap.add_argument("--language", type=Path, required=True, help="pasta da língua-filha (criada por evolution.py)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da evolução)")
    ap.add_argument("--rebuild", action="store_true", help="refaz ortografia, módulos opcionais e o grammar.md")
    args = ap.parse_args()

    g = GrammarEvolver(args.language, args.seed)
    evo = g.run()
    spell = None
    if args.rebuild:
        import generate_language as gl
        manifest = _load(args.language / "manifest.json") or {}
        kwargs = {"out": args.language.parent, "start": "orthography"}
        if (manifest.get("options") or {}).get("no_wals"):
            kwargs["no_wals"] = True
        gl.generate(manifest.get("seed"), name=args.language.name, **kwargs)
    o = _load(args.language / "orthography.json")
    if o:
        import orthography as ortho_mod
        spell = ortho_mod.Orthography(o).spell
    write_markdown(args.language, evo, spell)

    events = evo["grammar"]["events"]
    print(f"\nEVOLUÇÃO DA GRAMÁTICA — {evo['daughter']} ({evo['years']} anos)")
    if not events:
        print("  Nenhuma mudança gramatical neste período.")
    for x in events:
        extra = f" ({x['form']})" if x.get("form") else ""
        if x["type"] == "irregular":
            extra = f": {x['regular']} → {x['irregular']}"
        print(f"  ~{x['year']:>5}  {TYPE_PT[x['type']]:<26} {x['note']}{extra}")
    print(f"\n[OK] Gramática evoluída em '{args.language}'"
          + (" (com grammar.md refeito)" if args.rebuild else "; rode com --rebuild para refazer o grammar.md"))


if __name__ == "__main__":
    main()
