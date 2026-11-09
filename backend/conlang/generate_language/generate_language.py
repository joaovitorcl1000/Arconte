"""
Orquestrador — gera uma língua completa com uma única semente.

Roda os sete módulos em sequência, deriva a semente de cada um a partir da
semente principal, salva tudo numa pasta própria da língua, valida a cadeia e
monta um documento único (grammar.md) com fonologia, morfologia, sintaxe e
dicionário.

    tipologia → inventário → fonotática → categorias → motor → léxico → sintaxe

Pode ficar em conlang/generate_language.py ou em conlang/generate_language/generate_language.py;
em ambos os casos encontra as pastas dos módulos e salva as línguas em conlang/languages/.

Uso:
    python generate_language/generate_language.py --seed 31
    python generate_language/generate_language.py --seed 31 --synthesis isolating --order SVO
    python generate_language/generate_language.py --seed 31 --from lexicon --list swadesh-200
    python generate_language/generate_language.py   # semente aleatória

Requer pydantic ≥ 2 (só para sortear a tipologia; dispensável com --typology-file).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import re
import sys
import unicodedata
import warnings
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

def _find_root() -> Path:
    """Raiz do projeto: a pasta que contém os módulos (funciona em conlang/ ou conlang/generate_language/)."""
    here = Path(__file__).resolve().parent
    for cand in (here, here.parent):
        if (cand / "phonotactics").is_dir() and (cand / "lexicon").is_dir():
            return cand
    raise SystemExit(f"Não encontrei as pastas dos módulos a partir de {here}.\n"
                     "Coloque generate_language.py em conlang/ ou em conlang/generate_language/.")


ROOT = _find_root()
# Caminho do script a partir da raiz (generate_language.py ou generate_language/generate_language.py),
# usado para mostrar o comando certo no grammar.md
SCRIPT = Path(__file__).resolve().relative_to(ROOT).as_posix()
for folder in ("morphological_typology", "phonemic_inventory", "phonotactics",
               "grammatical_categories", "morphological_engine", "lexicon", "syntax", "custom_input",
               "orthography", "stress", "names", "possession", "comparison", "derivation", "sound_changes", "irregularity",
               "numerals", "vocabulary", "clauses", "translator", "evolution"):
    sys.path.insert(0, str(ROOT / folder))

import phonemic_inventory as inv_mod  # noqa: E402
import phonotactics as pht_mod  # noqa: E402
import grammatical_categories as cat_mod  # noqa: E402
import morphological_engine as eng_mod  # noqa: E402
import lexicon as lex_mod  # noqa: E402
import syntax as syn_mod  # noqa: E402
import custom_input as ci  # noqa: E402

# Ortografia e acento são opcionais: sem as pastas, a língua é gerada só em IPA
try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import stress as stress_mod  # noqa: E402
except ImportError:
    stress_mod = None
try:
    import names as names_mod  # noqa: E402
except ImportError:
    names_mod = None
try:
    import possession as possession_mod  # noqa: E402
except ImportError:
    possession_mod = None
try:
    import comparison as comparison_mod  # noqa: E402
except ImportError:
    comparison_mod = None
try:
    import derivation as derivation_mod  # noqa: E402
except ImportError:
    derivation_mod = None
try:
    import sound_changes as sound_mod  # noqa: E402
except ImportError:
    sound_mod = None
try:
    import irregularity as irregularity_mod  # noqa: E402
except ImportError:
    irregularity_mod = None
try:
    import numerals as numerals_mod  # noqa: E402
except ImportError:
    numerals_mod = None
try:
    import vocabulary as vocabulary_mod  # noqa: E402
except ImportError:
    vocabulary_mod = None
try:
    import clauses as clauses_mod  # noqa: E402
except ImportError:
    clauses_mod = None
try:
    import translator as translator_mod  # noqa: E402
except ImportError:
    translator_mod = None

STEPS = ["typology", "inventory", "phonotactics", "categories", "morphology", "lexicon", "syntax"]
if ortho_mod:
    STEPS.append("orthography")
if stress_mod:
    STEPS.append("stress")
if names_mod:
    STEPS.append("names")
if possession_mod:
    STEPS.append("possession")
if comparison_mod:  # depois da posse: evita repetir as formas que ela criou
    STEPS.append("comparison")
if derivation_mod:  # depois da posse e da comparação, pelo mesmo motivo
    STEPS.append("derivation")
if numerals_mod:  # numerais 6, 7... 100: depois da derivação, para não repetir formas
    STEPS.append("numerals")
if vocabulary_mod:  # usa a derivação e os numerais
    STEPS.append("vocabulary")
if clauses_mod:  # usa o vocabulário (conectivos, adposições) e a posse
    STEPS.append("clauses")
if sound_mod:  # muda também as palavras derivadas e os nomes
    STEPS.append("sound_changes")
if irregularity_mod:  # por último: usa a comparação e as mudanças sonoras
    STEPS.append("irregularity")
FILES = {
    "typology": "morphological_typology.json",
    "inventory": "phonemic_inventory.json",
    "phonotactics": "phonotactics.json",
    "categories": "grammatical_categories.json",
    "morphology": "morphology.json",
    "lexicon": "lexicon.json",
    "syntax": "syntax.json",
    "orthography": "orthography.json",
    "stress": "stress.json",
    "names": "names.json",
    "possession": "possession.json",
    "comparison": "comparison.json",
    "derivation": "derivation.json",
    "sound_changes": "sound_changes.json",
    "irregularity": "irregularity.json",
    "numerals": "numerals.json",
    "vocabulary": "vocabulary.json",
    "clauses": "clauses.json",
}
STEP_LABELS = {"typology": "Tipologia morfológica", "inventory": "Inventário fonêmico",
               "phonotactics": "Fonotática", "categories": "Categorias gramaticais",
               "morphology": "Motor morfológico", "lexicon": "Léxico", "syntax": "Sintaxe",
               "orthography": "Ortografia", "stress": "Acento", "names": "Nomes próprios",
               "possession": "Posse e determinantes", "comparison": "Comparação",
               "derivation": "Derivação", "sound_changes": "Mudanças sonoras",
               "irregularity": "Irregularidades", "numerals": "Sistema numeral",
               "vocabulary": "Vocabulário ampliado", "clauses": "Orações"}

DEFAULT_LANGUAGES = ROOT / "languages"
DEFAULT_WALS = ROOT / "wals" / "cldf"


def derive_seed(master: int, step: str) -> int:
    """Semente de cada módulo, estável e independente das demais."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def visible_len(s: str) -> int:
    return sum(1 for ch in s if unicodedata.category(ch) != "Mn")


# ═══════════════════════════════════════════════════════════════════════════
# Orquestrador
# ═══════════════════════════════════════════════════════════════════════════

class LanguageBuilder:
    def __init__(self, seed: int, out_dir: Path, opts: argparse.Namespace):
        self.seed = seed
        self.out = out_dir
        self.o = opts
        self.seeds = {s: derive_seed(seed, s) for s in STEPS}
        self.data: Dict[str, Dict] = {}
        self.wals_dir = None if opts.no_wals or not opts.wals.exists() else opts.wals
        self.log: List[str] = []
        self.engine: Optional[eng_mod.MorphologicalEngine] = None
        self.custom: Optional[Dict] = None
        self.custom_report: Dict = {}
        if opts.custom:
            path = Path(opts.custom)
            if not path.exists():
                raise SystemExit(f"Arquivo de palavras não encontrado: {path}")
            self.stats = inv_mod.load_stats(opts.phoible)
            self.custom = ci.parse(path)
            ci.prepare(self.custom, self.stats.segments.keys())

    # ── utilidades ───────────────────────────────────────────────────────
    def path(self, step: str) -> Path:
        return self.out / FILES[step]

    def save(self, step: str, data: Dict) -> None:
        self.data[step] = data
        self.path(step).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, step: str) -> Dict:
        p = self.path(step)
        if not p.exists():
            raise SystemExit(f"--from exige os resultados anteriores, mas falta {p}.\n"
                             f"Gere a língua inteira primeiro (sem --from).")
        self.data[step] = json.loads(p.read_text(encoding="utf-8"))
        return self.data[step]

    def say(self, step: str, summary: str) -> None:
        line = f"  [{STEPS.index(step) + 1}/{len(STEPS)}] {STEP_LABELS[step]:<24} {summary}"
        print(line)

    # ── etapas ───────────────────────────────────────────────────────────
    def run_typology(self) -> str:
        if self.o.typology_file:
            typ = json.loads(Path(self.o.typology_file).read_text(encoding="utf-8"))
            self.save("typology", typ)
            return f"{typ['degree_of_synthesis']}, {typ['degree_of_fusion']} (arquivo)"
        try:
            import morphological_typology as typ_mod
        except ImportError:
            raise SystemExit("A tipologia precisa do pydantic: pip install pydantic "
                             "(ou use --typology-file com um JSON pronto).")
        want = {k: v for k, v in {
            "degree_of_synthesis": self.o.synthesis, "degree_of_fusion": self.o.fusion,
            "affix_position": self.o.affix_position, "locus_of_marking": self.o.locus}.items() if v}
        base = self.seeds["typology"]
        cfg = None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for i in range(5000):  # amostragem por rejeição: mantém o perfil plausível
                c = json.loads(typ_mod.sample_config(base + i).model_dump_json())
                if all(c[k] == v for k, v in want.items()):
                    cfg = c
                    break
        if cfg is None:
            raise SystemExit(f"Nenhuma tipologia plausível atende a {want}. "
                             "Verifique a combinação (ex: isolante não pode ser fusional).")
        self.save("typology", cfg)
        procs = ", ".join(p for p in cfg["active_processes"] if p not in ("affixation", "compounding"))
        return (f"{cfg['degree_of_synthesis']}, {cfg['degree_of_fusion']}, {cfg['affix_position']}, "
                f"{cfg['locus_of_marking']}" + (f" (+ {procs})" if procs else ""))

    def run_inventory(self) -> str:
        stats = inv_mod.load_stats(self.o.phoible)
        declared = self.custom and (self.custom["phonemes"].get("consonants") or
                                    self.custom["phonemes"].get("vowels"))
        if declared:
            inv = ci.declared_inventory(self.custom, stats, inv_mod, self.seeds["inventory"])
        else:
            req = inv_mod.read_morph_requirements(self.path("typology"))
            opts = inv_mod.GeneratorOptions(mode=self.o.inventory_mode, seed=self.seeds["inventory"],
                                            n_consonants=self.o.consonants, n_vowels=self.o.vowels,
                                            tones=self.o.tones)
            inv = inv_mod.InventoryGenerator(stats, opts, req).generate()
        inv = json.loads(json.dumps(inv))
        if self.custom:
            added = ci.extend_inventory(inv, self.custom, stats, inv_mod)
            self.custom_report["inventory"] = {"declared": bool(declared), "added": added}
        self.save("inventory", inv)
        c = inv["counts"]
        ref = inv["metadata"].get("reference_language") or {}
        return (f"{c['consonants']} consoantes, {c['vowels']} vogais, {c['tones']} tons"
                + (f" (ref.: {ref.get('name')})" if ref else ""))

    def run_phonotactics(self) -> str:
        inv = self.data["inventory"]
        req = pht_mod.read_morph_requirements(self.path("typology"))
        rules = pht_mod.build_rules(inv, seed=self.seeds["phonotactics"], complexity=self.o.complexity,
                                    morph_req=req, wals_dir=self.wals_dir)
        if self.custom:
            self.custom_report["phonotactics"] = ci.adapt_phonotactics(
                rules, inv, self.custom, self.o.custom_policy, pht_mod)
        eng = pht_mod.Phonotactics(rules, inv, seed=self.seeds["phonotactics"])
        rules["samples"] = {"roots": [eng.generate_root()["form"] for _ in range(20)],
                            "suffixes": [eng.generate_affix("suffix")["form"] for _ in range(6)],
                            "prefixes": [eng.generate_affix("prefix")["form"] for _ in range(6)]}
        self.save("phonotactics", rules)
        tpl = "/".join(sorted(rules["templates"], key=lambda k: -rules["templates"][k])[:4])
        return f"{rules['syllable_complexity']} ({tpl})"

    def run_categories(self) -> str:
        cats = cat_mod.CategoryBuilder(self.data["typology"], cat_mod.Wals(self.wals_dir),
                                       seed=self.seeds["categories"]).generate()
        cats = json.loads(json.dumps(cats))
        self.save("categories", cats)
        active = [k for k, v in cats["categories"].items() if v.get("grammaticalized")]
        return f"{len(active)} categorias: " + ", ".join(active)

    def _engine(self, fresh: bool = False) -> eng_mod.MorphologicalEngine:
        if fresh:
            return eng_mod.MorphologicalEngine(self.data["inventory"], self.data["phonotactics"],
                                               self.data["categories"], self.data["typology"],
                                               seed=self.seeds["morphology"])
        if self.engine is None:
            self.engine = eng_mod.MorphologicalEngine.load(
                self.data["morphology"], self.data["inventory"], self.data["phonotactics"],
                self.data["categories"], self.data["typology"])
        return self.engine

    def run_morphology(self) -> str:
        data = json.loads(json.dumps(self._engine(fresh=True).build(6, 6)))
        if self.custom:
            self.custom_report["morphology"] = ci.apply_function_words(
                data, self.data["categories"], self.custom)
        self.save("morphology", data)
        self.engine = None
        n = sum(len(f) for s in data["affixes"]["noun"] + data["affixes"]["verb"]
                for f in s["forms"].values())
        templates = " | ".join(self.data["categories"]["slots"][d]["template"] for d in ("noun", "verb"))
        return f"{n} células de afixo; moldes {templates}"

    def run_lexicon(self) -> str:
        concepts = lex_mod.load_concepts(self.o.list, self.o.concepticon if self.o.concepticon.exists() else None)
        resolved = None
        if self.custom:
            ph = pht_mod.Phonotactics(self.data["phonotactics"], self.data["inventory"])
            for w in self.custom["words"]:
                w["valid"] = ph.is_valid(w["segments"])
            all_concepts = concepts + [c for c in lex_mod.load_concepts("all")
                                       if c["id"] not in {x["id"] for x in concepts}]
            resolved = ci.resolve_lexicon(self.custom, concepts, all_concepts)
            concepts = concepts + resolved["extra_concepts"]
            self.custom_report["lexicon"] = resolved["report"]
        lb = lex_mod.LexiconBuilder(self._engine(), seed=self.seeds["lexicon"])
        data = lb.build(concepts)
        if resolved:  # o léxico é gerado normalmente; depois entram as palavras do usuário
            self.custom_report["lexicon_notes"] = ci.apply_to_lexicon(data, lb, resolved)
        data["metadata"] = {"seed": self.seeds["lexicon"], "list": self.o.list, "notes": lb.notes,
                            "source": "Concepticon (List et al.)"}
        data = json.loads(json.dumps(data))
        self.save("lexicon", data)
        lex_mod.write_dictionary(self.out / "dictionary.md", data)
        return f"{len(data['entries'])} entradas ({self.o.list})"

    def run_syntax(self) -> str:
        wals = syn_mod.Wals(self.wals_dir)
        base = self.seeds["syntax"]
        data = None
        for i in range(2000 if self.o.order else 1):  # amostragem por rejeição para --order
            d = syn_mod.build(self._engine(), self.data["lexicon"], self.data["typology"], wals, base + i)
            if not self.o.order or d["settings"]["word_order"]["clause"] == self.o.order:
                data = d
                break
        if data is None:
            raise SystemExit(f"Não foi possível obter a ordem {self.o.order} com esta tipologia.")
        data = json.loads(json.dumps(data))
        self.save("syntax", data)
        syn_mod.write_examples(self.out / "examples.md", data)
        s = data["settings"]
        return f"{s['word_order']['clause']}, {s['adpositions']}, {len(data['examples'])} frases"

    def run_orthography(self) -> str:
        spec = ortho_mod.build(self.data["inventory"], style=self.o.style,
                               seed=self.seeds["orthography"], rules=self.data["phonotactics"])
        name = ortho_mod.language_name(ortho_mod.Orthography(spec), self.autonym())
        if name:
            spec["language_name"] = name
        self.save("orthography", spec)
        ortho_mod.write_markdown(self.out / "orthography.md", spec, self.ortho(),
                                 self.data["lexicon"], self.data["syntax"], name)
        n = len(spec["separator_pairs"])
        extra = f", separador em {n} sequência{'s' if n > 1 else ''}" if n else ""
        return f"estilo {spec['style']}" + (f" — {name['english']}" if name else "") + extra

    def run_stress(self) -> str:
        spec = stress_mod.build(self.data["inventory"], self.data["phonotactics"],
                                seed=self.seeds["stress"], rule=self.o.stress_rule, wals_dir=self.wals_dir)
        self.data["stress"] = spec
        st = self.stresser()
        words = [e["citation"] for e in self.data["lexicon"]["entries"]
                 if e.get("citation") and "-" not in e["citation"]]
        spec["examples"] = [{"ipa": w, "stressed": st.mark(w)} for w in words
                            if len(st.syllabify(w)) > 1][:20]
        self.save("stress", spec)
        stress_mod.write_markdown(self.out / "stress.md", spec, st, self.data["lexicon"])
        return f"{spec['system']} ({spec['rule']}" + (f", peso: {spec['heavy']}" if spec["heavy"] else "") + ")"

    def _ensure_manifest(self) -> None:
        """Nomes, posse e comparação leem a semente da língua no manifesto (para o acento);
        na primeira geração ele ainda não existe, então gravamos um provisório."""
        mpath = self.out / "manifest.json"
        current = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
        if current.get("seed") != self.seed:
            mpath.write_text(json.dumps({"seed": self.seed}, ensure_ascii=False), encoding="utf-8")

    def run_possession(self) -> str:
        self._ensure_manifest()
        b = possession_mod.PossessionBuilder(self.out, seed=self.seeds["possession"], wals_dir=self.wals_dir)
        data = json.loads(json.dumps(b.build()))
        self.save("possession", data)
        possession_mod.write_markdown(self.out / "possession.md", data, self.spell)
        s = data["settings"]
        return (f"possessivos: {s['pronominal']['strategy']}; posse nominal: {s['nominal']['locus']}; "
                f"{s['alienability']['classes']} classe(s) de posse")

    def run_comparison(self) -> str:
        self._ensure_manifest()
        b = comparison_mod.ComparisonBuilder(self.out, seed=self.seeds["comparison"], wals_dir=self.wals_dir)
        data = json.loads(json.dumps(b.build()))
        self.save("comparison", data)
        comparison_mod.write_markdown(self.out / "comparison.md", data, self.spell)
        s = data["settings"]
        return f"{s['strategy']}; grau: {s['degree']['type']}; superlativo: {s['superlative']['type']}"

    def run_derivation(self) -> str:
        self._ensure_manifest()
        b = derivation_mod.DerivationBuilder(self.out, seed=self.seeds["derivation"])
        per = None if self.o.derive_all else self.o.derive_per_process
        data = json.loads(json.dumps(b.build(per)))
        self.save("derivation", data)
        derivation_mod.write_markdown(self.out / "derivation.md", data, self.spell, b.entries)
        return f"{len(data['rules'])} processos, {data['metadata']['derived_count']} palavras derivadas"

    def run_sound_changes(self) -> str:
        self._ensure_manifest()
        sc = sound_mod.SoundChanger(self.out, seed=self.seeds["sound_changes"])
        data = json.loads(json.dumps(sc.run(self.o.sound_change, natural=not self.o.no_natural_changes,
                                            reflect_spelling=self.o.reflect_spelling)))
        self.save("sound_changes", data)
        sound_mod.write_markdown(self.out / "sound_changes.md", data)
        m = data["metadata"]
        n = len(data["rules"])
        return f"{n} regra{'s' if n != 1 else ''}, {m['changed_words']} de {m['total_words']} palavras mudaram"

    def run_irregularity(self) -> str:
        self._ensure_manifest()
        b = irregularity_mod.IrregularityBuilder(self.out, seed=self.seeds["irregularity"])
        data = json.loads(json.dumps(b.build()))
        self.save("irregularity", data)
        irregularity_mod.write_markdown(self.out / "irregularity.md", data)
        m = data["metadata"]
        return (f"{m['irregular_count']} palavra{'s' if m['irregular_count'] != 1 else ''} irregular"
                f"{'es' if m['irregular_count'] != 1 else ''}, {m['alternation_count']} alternância"
                f"{'s' if m['alternation_count'] != 1 else ''}")

    def run_numerals(self) -> str:
        self._ensure_manifest()
        b = numerals_mod.NumeralBuilder(self.out, seed=self.seeds["numerals"], wals_dir=self.wals_dir)
        data = json.loads(json.dumps(b.build(self.o.number_base, self.o.numbers_upto)))
        self.save("numerals", data)
        numerals_mod.write_markdown(self.out / "numerals.md", data, self.spell)
        return f"{numerals_mod.BASE_PT[data['settings']['base']]}, {data['metadata']['new_words']} palavras novas"

    def run_vocabulary(self) -> str:
        self._ensure_manifest()
        if not vocabulary_mod.DEFAULT_LIST.exists():  # a lista do WOLD vem num arquivo à parte
            self.save("vocabulary", {"entries": [], "stats": {"total": 0, "root": 0, "derived": 0, "compound": 0,
                                                              "by_field": {}},
                                     "metadata": {"missing_list": str(vocabulary_mod.DEFAULT_LIST)}})
            return f"pulado: falta {vocabulary_mod.DEFAULT_LIST.name} na pasta vocabulary/"
        b = vocabulary_mod.VocabularyBuilder(self.out, seed=self.seeds["vocabulary"])
        data = json.loads(json.dumps(b.build(self.o.include_modern)))
        self.save("vocabulary", data)
        vocabulary_mod.write_markdown(self.out / "vocabulary.md", data)
        st = data["stats"]
        return f"{st['total']} palavras ({st['derived']} derivadas, {st['compound']} compostas, {st['root']} raízes)"

    def run_clauses(self) -> str:
        self._ensure_manifest()
        b = clauses_mod.ClauseBuilder(self.out, seed=self.seeds["clauses"], wals_dir=self.wals_dir)
        data = json.loads(json.dumps(b.build()))
        self.save("clauses", data)
        clauses_mod.write_markdown(self.out / "clauses.md", data, self.spell)
        s = data["settings"]
        return (f"passiva: {'sim' if s['passive']['present'] else 'não'}; "
                f"{len(s['demonstratives']['terms'])} grau(s) de demonstrativo; {len(data['sentences'])} frases")

    def irregulars(self) -> Dict[str, Dict]:
        """Conceito → forma irregular, para o dicionário."""
        data = self.data.get("irregularity")
        return {x["gloss"]: x for x in data["irregulars"]} if data else {}

    def phonetic(self) -> Dict[str, Dict]:
        """Forma do dicionário → pronúncia depois das mudanças sonoras (só as que mudaram)."""
        data = self.data.get("sound_changes")
        if not data:
            return {}
        out = {}
        for x in data["entries"] + data.get("derived", []):
            if x["rules"]:
                out[x["underlying"]] = x
        return out

    def run_names(self) -> str:
        self._ensure_manifest()
        g = names_mod.NameGenerator(self.out, seed=self.seeds["names"])
        people = [g.full_person() for _ in range(self.o.people)]
        places = [g.place() for _ in range(self.o.places)]
        data = {"settings": dict(g.settings), "people": people, "places": places,
                "metadata": {"seed": g.seed, "spelled": g.ortho is not None, "stressed": g.stress is not None}}
        self.save("names", json.loads(json.dumps(data)))
        names_mod.write_markdown(self.out / "names.md", g, people, places)
        ex = ", ".join(x["name"] for x in ([people[0]["given"]] if people else []) + places[:1])
        return f"{len(people)} pessoas, {len(places)} lugares" + (f" (ex.: {ex})" if ex else "")

    def ortho(self):
        """Ortografia da língua, se a etapa existir."""
        spec = self.data.get("orthography")
        return ortho_mod.Orthography(spec) if (ortho_mod and spec) else None

    def stresser(self):
        """Acento da língua, se a etapa existir."""
        spec = self.data.get("stress")
        if not (stress_mod and spec):
            return None
        return stress_mod.Stress(spec, self.data["inventory"], self.data["phonotactics"], self.seeds["stress"])

    def spell(self, ipa: str) -> str:
        o = self.ortho()
        return o.spell(ipa) if o and ipa else ipa

    def pron(self, ipa: str) -> str:
        st = self.stresser()
        return st.mark(ipa) if st and ipa else ipa

    # ── execução ─────────────────────────────────────────────────────────
    def build(self, start: str = "typology") -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        if self.custom:
            shutil.copyfile(self.custom["path"], self.out / "custom.txt")
            if STEPS.index(start) > STEPS.index("inventory"):
                inv = self.load("inventory")
                have = {x["ipa"] for x in inv["consonants"] + inv["vowels"]}
                missing = sorted({s for w in self.custom["words"] for s in w["segments"]} - have)
                if missing:
                    raise SystemExit("As palavras do usuário usam fonemas fora do inventário "
                                     f"({' '.join(missing)}). Use --from inventory.")
        runners: Dict[str, Callable[[], str]] = {
            "typology": self.run_typology, "inventory": self.run_inventory,
            "phonotactics": self.run_phonotactics, "categories": self.run_categories,
            "morphology": self.run_morphology, "lexicon": self.run_lexicon, "syntax": self.run_syntax,
            "orthography": self.run_orthography, "stress": self.run_stress, "names": self.run_names,
            "possession": self.run_possession, "comparison": self.run_comparison,
            "derivation": self.run_derivation, "sound_changes": self.run_sound_changes,
            "irregularity": self.run_irregularity, "numerals": self.run_numerals,
            "vocabulary": self.run_vocabulary, "clauses": self.run_clauses,
        }
        first = STEPS.index(start)
        for step in STEPS[:first]:
            self.load(step)
            self.say(step, "(mantido)")
        for step in STEPS[first:]:
            self.say(step, runners[step]())

    # ── validação ────────────────────────────────────────────────────────
    def validate(self) -> Dict:
        inv = self.data["inventory"]
        phonemes = {nfd(x["ipa"]) for x in inv["consonants"] + inv["vowels"]}
        bad_phonemes = sorted({s for e in self.data["lexicon"]["entries"] for s in e["root"]
                               if nfd(s) not in phonemes})
        invalid = [f"{e['english']} {i['gloss']}" for e in self.data["lexicon"]["entries"]
                   for i in e.get("inflections", []) if not i["valid"]]
        for p in self.data["morphology"]["paradigms"].values():
            invalid += [c["underlying"] for line in p["cells"] for c in line if not c["valid"]]
        notes = []
        for step, key in (("inventory", None), ("phonotactics", "notes"), ("categories", "notes"),
                          ("morphology", "notes"), ("lexicon", "notes"), ("syntax", "notes")):
            if key:
                notes += [f"{STEP_LABELS[step]}: {n}" for n in self.data[step]["metadata"].get(key, [])]
        if self.data.get("orthography"):
            notes += [f"Ortografia: {n}" for n in self.data["orthography"]["metadata"].get("notes", [])]
        if self.data.get("stress"):
            notes += [f"Acento: {n}" for n in self.data["stress"]["metadata"].get("notes", [])]
        if self.data.get("derivation"):
            notes += [f"Derivação: {n}" for n in self.data["derivation"]["metadata"].get("notes", [])]
        if self.data.get("irregularity"):
            notes += [f"Irregularidades: {n}" for n in self.data["irregularity"]["metadata"].get("notes", [])]
        for step, label in (("numerals", "Numerais"), ("clauses", "Orações")):
            if self.data.get(step):
                notes += [f"{label}: {n}" for n in self.data[step]["metadata"].get("notes", [])]
        if self.data.get("sound_changes"):
            m = self.data["sound_changes"]["metadata"]
            notes += [f"Mudanças sonoras: regra ignorada — {e}" for e in m.get("errors", [])]
            notes += [f"Mudanças sonoras: {w}" for w in m.get("warnings", [])]
        unreadable = []
        o = self.ortho()
        if o:  # toda palavra escrita precisa ser lida de volta como os mesmos fonemas
            tl = set(ortho_mod.TONE_LETTERS)
            for e in self.data["lexicon"]["entries"]:
                c = e.get("citation")
                if not c or "-" in c:
                    continue
                for w in c.split(" "):
                    segs = [t for syl in w.split(".") for t in o.tokenize("".join(ch for ch in syl if ch not in tl))]
                    if o.decode(o.spell(w)) != segs:
                        unreadable.append(w)
        return {"foreign_phonemes": bad_phonemes, "invalid_forms": invalid, "notes": notes,
                "unreadable_spellings": unreadable, "ok": not bad_phonemes and not unreadable}

    def autonym(self) -> Dict:
        """Nome nativo: muitas línguas chamam a si mesmas de 'pessoa(s)' ou 'gente'."""
        if getattr(self, "_autonym", None):
            return self._autonym
        self._autonym = self._find_autonym()
        return self._autonym

    def _find_autonym(self) -> Dict:
        entries = {e["gloss"]: e for e in self.data["lexicon"]["entries"]}
        for g in ("PERSON", "MALE PERSON", "WOMAN"):
            e = entries.get(g)
            if e and e.get("citation"):
                return {"form": e["citation"], "literal": lex_mod.short(e["english"])}
        eng = self._engine()
        r = eng.ph.generate_root(2)
        return {"form": r["form"].replace(".", ""), "literal": None}


# ═══════════════════════════════════════════════════════════════════════════
# Documento único da língua (grammar.md)
# ═══════════════════════════════════════════════════════════════════════════

def md_table(header: List[str], rows: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


PLACES = ["labial", "coronal", "palatal", "velar", "labial-velar", "uvular", "laryngeal"]
MANNERS = ["stop", "affricate", "fricative", "nasal", "rhotic", "lateral", "approximant", "click"]
PLACE_PT = {"labial": "Labial", "coronal": "Coronal", "palatal": "Palatal", "velar": "Velar",
            "labial-velar": "Labiovelar", "uvular": "Uvular", "laryngeal": "Laríngea"}
MANNER_PT = {"stop": "Oclusiva", "affricate": "Africada", "fricative": "Fricativa", "nasal": "Nasal",
             "rhotic": "Rótica", "lateral": "Lateral", "approximant": "Aproximante", "click": "Clique"}


def phonology_section(inv: Dict, rules: Dict) -> List[str]:
    cons = inv["consonants"]
    places = [p for p in PLACES if any(c["place"] == p for c in cons)]
    manners = [m for m in MANNERS if any(c["manner"] == m for c in cons)]
    rows = [[MANNER_PT[m]] + [" ".join(c["ipa"] for c in cons if c["manner"] == m and c["place"] == p)
                              for p in places] for m in manners]
    out = ["## Fonologia", "", f"### Consoantes ({len(cons)})", ""]
    out += md_table(["", *[PLACE_PT[p] for p in places]], rows)

    vow = inv["vowels"]
    heights, backs = ["high", "mid", "low"], ["front", "central", "back"]
    hp = {"high": "Alta", "mid": "Média", "low": "Baixa"}
    bp = {"front": "Anterior", "central": "Central", "back": "Posterior"}
    vrows = [[hp[h]] + [" ".join(v["ipa"] for v in vow if v["height"] == h and v["backness"] == b)
                        for b in backs] for h in heights if any(v["height"] == h for v in vow)]
    out += ["", f"### Vogais ({len(vow)})", ""] + md_table(["", *[bp[b] for b in backs]], vrows)
    if inv["tones"]:
        out += ["", f"### Tons ({len(inv['tones'])})", "", " ".join(t["ipa"] for t in inv["tones"])]

    tpl = sorted(rules["templates"].items(), key=lambda x: -x[1])
    out += ["", "### Estrutura silábica", "",
            f"- Complexidade: **{rules['syllable_complexity']}** ({rules['complexity_source']})",
            "- Moldes: " + ", ".join(f"{k} ({v:.0%})" for k, v in tpl),
            f"- Ataque {'obrigatório' if rules['onset_required'] else 'opcional'}; "
            f"hiato {'permitido' if rules['allow_hiatus'] else 'proibido'}"]
    cl = ["".join(c) for c in rules["onsets"]["clusters"]]
    if cl:
        out.append(f"- Encontros no ataque ({len(cl)}): " + " ".join(cl[:40]) + (" …" if len(cl) > 40 else ""))
    co = rules["codas"]
    out.append("- Codas: " + (" ".join(co["single"]) if co["single"] else "nenhuma (sílabas abertas)"))
    if co["single"] and co["word_final"] != co["single"]:
        out.append("- Codas no fim de palavra: " + " ".join(co["word_final"]))
    if rules["onsets"]["word_initial_forbidden"]:
        out.append("- Proibidos no início de palavra: " + " ".join(rules["onsets"]["word_initial_forbidden"]))
    return out


def morphology_section(b: LanguageBuilder) -> List[str]:
    typ, cats, morph = b.data["typology"], b.data["categories"], b.data["morphology"]
    g = eng_mod.gloss
    out = ["## Morfologia", "",
           f"- Tipo: {typ['degree_of_synthesis']}, {typ['degree_of_fusion']}, {typ['affix_position']}, "
           f"{typ['locus_of_marking']}",
           "- Processos: " + ", ".join(typ["active_processes"])]
    s = morph["sandhi"]
    out.append(f"- Sândi: vogal epentética /{s['epenthetic_vowel']}/; encontros por {s['cluster']}; "
               f"hiato por {s['hiatus']}")
    if morph["harmony"].get("enabled"):
        pairs = sorted({"/".join(sorted(set(p.values()))) for p in morph["harmony"]["pairs"].values()})
        out.append("- Harmonia vocálica anterior/posterior: " + " ".join(pairs))

    out += ["", "### Categorias gramaticais", ""]
    rows = []
    for name, c in cats["categories"].items():
        if not c.get("grammaticalized"):
            continue
        if name == "agreement":
            vals = ", ".join(f"{a}" for a in c["arguments"]) + f" ({c['alignment']})"
            real = ", ".join(f"{a}: {r['realization']} {r['position'] or ''}".strip()
                             for a, r in c["arguments"].items())
        else:
            vals = ", ".join(c["values"]) + (f" ({c['alignment']})" if name == "case" else "")
            real = c.get("realization", "") + (f" ({c['position']})" if c.get("position") else "")
        rows.append([cat_mod.LABELS.get(name, name), vals, real, ", ".join(c.get("zero", [])) or "—"])
    out += md_table(["Categoria", "Valores", "Realização", "Ø"], rows)
    out += ["", f"- Molde do nome: `{cats['slots']['noun']['template']}`",
            f"- Molde do verbo: `{cats['slots']['verb']['template']}`"]
    ic = cats["inflection_classes"]
    if ic["noun"] > 1 or ic["verb"] > 1:
        out.append(f"- Classes flexionais: {ic['noun']} declinações, {ic['verb']} conjugações")

    for domain, title in (("noun", "Afixos nominais"), ("verb", "Afixos verbais")):
        slots = morph["affixes"][domain]
        if not slots:
            continue
        out += ["", f"### {title}", ""]
        for slot in slots:
            for cls, forms in slot["forms"].items():
                label = slot["name"] + (f" — classe {int(cls) + 1}" if slot["class_dependent"] else "")
                out += [f"**{label}**", ""]
                rows = []
                for key, segs in forms.items():
                    vals = [kv.split("=", 1)[1] for kv in key.split("|")]
                    cell = ".".join(x for x in (g(v) for v in vals) if x) or "(padrão)"
                    rows.append([cell, eng_mod._affix_str(segs, slot["position"], slot["realization"])])
                out += md_table(["Célula", "Forma"], rows) + [""]
    nl = [p for d in ("noun", "verb") for p in morph["nonlinear"]["processes"][d]]
    if nl:
        out += ["### Processos não lineares", ""]
        for p in nl:
            out.append(f"- {p['category']}: {p['realization']}")
    if morph["free_markers"]:
        out += ["", "### Palavras gramaticais", ""]
        for cat, fm in morph["free_markers"].items():
            out.append(f"- {cat}: " + ", ".join(
                f"{g(v) if cat != 'classifiers' else v} *{''.join(w)}* "
                f"({'antes' if fm['positions'][v] == 'before' else 'depois'})" for v, w in fm["forms"].items()))
    return out


def paradigm_md(p: Dict) -> List[str]:
    g = eng_mod.gloss
    cols = p["columns"][1] if p["columns"] else [""]
    rows = p["rows"][1] if p["rows"] else [""]
    header = [""] + [g(c) or c or "forma" for c in cols]
    body = [[g(r) or r] + [c["phrase"] + ("" if c["valid"] else " *") for c in line]
            for r, line in zip(rows, p["cells"])]
    return md_table(header, body)


def paradigms_section(b: LanguageBuilder) -> List[str]:
    eng = b._engine()
    entries = {e["gloss"]: e for e in b.data["lexicon"]["entries"]}
    out = ["## Paradigmas", ""]
    for domain, prefs, title in (("noun", ["DOG", "WOMAN", "FISH", "BIRD"], "Nome"),
                                 ("verb", ["SEE", "EAT", "HEAR", "COME"], "Verbo")):
        e = next((entries[x] for x in prefs if x in entries and entries[x]["pos"] == domain), None) or \
            next((x for x in b.data["lexicon"]["entries"] if x["pos"] == domain and x["root"]), None)
        if not e:
            continue
        lex = {"root": e["root"], "form": e["form"], "tones": e.get("tones", []),
               "class": e.get("class") or 0, "gender": e.get("gender")}
        out += [f"### {title}: *{e['citation']}* '{lex_mod.short(e['english'])}'", ""]
        out += paradigm_md(eng.paradigm(lex, domain)) + [""]
    pro = b.data["lexicon"]["pronouns"]
    out += ["### Pronomes", ""]
    out += md_table(["Pessoa", "Forma"], [[eng_mod.gloss(k), f"*{v['form']}*"] for k, v in pro["cells"].items()])
    return out


def custom_section(b: LanguageBuilder) -> List[str]:
    rep, spec = b.custom_report, b.custom
    out = [f"Arquivo: `custom.txt` — política: **{b.o.custom_policy}**", ""]
    inv = rep.get("inventory", {})
    if inv.get("declared"):
        out.append("- Inventário: declarado pelo usuário")
    elif inv.get("added"):
        out.append("- Fonemas adicionados ao inventário: " + " ".join(inv["added"]))
    for c in rep.get("phonotactics", {}).get("changes", []):
        out.append(f"- Fonotática: {c}")
    for n in rep.get("morphology", []):
        out.append(f"- Palavras gramaticais: {n}")
    for n in rep.get("lexicon_notes", []):
        out.append(f"- Léxico: {n}")
    rows = [[f"*{r['form']}*", r["meaning"], ", ".join(r["concepts"]),
             "ok" if r["valid"] else "exceção fonotática"] for r in rep.get("lexicon", [])]
    if rows:
        out += [""] + md_table(["Forma", "Significado", "Conceito", "Situação"], rows)
    if spec["warnings"]:
        out += ["", "Avisos do arquivo:"] + [f"- {w}" for w in spec["warnings"]]
    return out


def orthography_section(b: LanguageBuilder) -> List[str]:
    spec = b.data["orthography"]
    out = ["### Ortografia", "", f"- Estilo: {ortho_mod.STYLE_PT[spec['style']]}"]
    if spec["separator_pairs"]:
        out.append(f"- Separador `{spec['separator']}` entre sons que, escritos juntos, "
                   "formariam outra letra")
    rows = [[f"**{g}**", f"/{ipa}/"] for ipa, g in sorted(spec["graphemes"].items(),
                                                        key=lambda x: (nfd(x[1]).lower(), x[0]))]
    out += [""] + md_table(["Grafia", "IPA"], rows)
    if spec["tones"]:
        out += ["", "Tons: " + ", ".join(f"{t} = {ortho_mod.TONE_NAMES.get(m, m)}"
                                          for t, m in spec["tones"].items())]
    return out


def stress_section(b: LanguageBuilder) -> List[str]:
    spec = b.data["stress"]
    out = ["### Acento", "", f"- Sistema: **{stress_mod.SYSTEM_PT[spec['system']]}**",
           f"- {spec['description']}"]
    if spec.get("examples"):
        out.append("- Exemplos: " + ", ".join(f"/{x['stressed']}/" for x in spec["examples"][:6]))
    return out


def embedded_section(b: LanguageBuilder, filename: str, stop_at: Optional[str] = None) -> List[str]:
    """Reaproveita o .md gerado pelo módulo: tira o título e desce um nível os cabeçalhos.
    Com `stop_at`, para antes desse cabeçalho (ex: listas de palavras que já vão no dicionário)."""
    path = b.out / filename
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[1:]:  # a 1ª linha é o título do módulo
        if stop_at and line.startswith(stop_at):
            break
        out.append("#" + line if line.startswith("## ") else line)
    while out and not out[0].strip():
        out.pop(0)
    return out


def names_section(b: LanguageBuilder) -> List[str]:
    data = b.data["names"]
    s = data["settings"]
    out = []
    if s.get("gender_endings"):
        e = s["gender_endings"]
        out.append(f"- Nomes masculinos terminam em -{b.spell(e['male'][0])}, "
                   f"femininos em -{b.spell(e['female'][0])}")
    else:
        out.append("- Nomes sem marca de gênero")
    p = s["patronymic"]
    extra = f" (-{b.spell(''.join(p['morpheme']))})" if p.get("morpheme") else ""
    out.append(f"- Sobrenomes: {names_mod.PATRONYMIC_PT[p['strategy']]}{extra}")
    suf = "".join(s["settlement_suffix"])
    out.append(f"- Sufixo de povoado: -{b.spell(suf)} /-{suf}/")
    rows = [[f"**{x['given']['name']} {x['family']['name']}**", f"/{x['given']['pronunciation']}/",
             x["given"]["meaning"] or "—", x["family"]["meaning"] or "—"] for x in data["people"]]
    out += ["", "### Pessoas", ""] + md_table(["Nome", "Pronúncia", "Significado", "Sobrenome"], rows)
    rows = [[f"**{x['name']}**", f"/{x['pronunciation']}/", names_mod.TEMPLATE_PT[x["template"]],
             x["meaning"] or "—"] for x in data["places"]]
    out += ["", "### Lugares", ""] + md_table(["Nome", "Pronúncia", "Tipo", "Significado"], rows)
    return out

def verb_stem(b: LanguageBuilder, e: Dict) -> Optional[str]:
    """Radical do verbo para o verbete ('-diinplunung-'), quando a língua marca pessoa no verbo.
    Como nos dicionários de suaíli ou georgiano, o verbo é citado pelo radical, e a forma
    flexionada vira uma das formas principais. Nas demais línguas, devolve None."""
    if e.get("pos") != "verb" or e.get("skeleton") or not e.get("root"):
        return None
    slots = b.data["morphology"]["affixes"].get("verb", [])
    person = [s for s in slots if any(c.startswith("agreement") for c in s.get("categories", []))]
    if not person:
        return None
    root = "".join(e["root"])
    if root == "".join(ch for ch in e["citation"] if ch not in "˥˦˧˨˩."):
        return None
    pre = any(s.get("position") == "prefix" for s in slots)
    suf = any(s.get("position") == "suffix" for s in slots)
    return ("-" if pre else "") + root + ("-" if suf else "")

def dictionary_line(b: LanguageBuilder, e: Dict) -> str:
    """Formato do Vulgarlang: grafia /pronúncia com acento/ classe 'significado' ..."""
    line = lex_mod.entry_line(e)
    if not (b.ortho() or b.stresser()):
        return line
    head = f"**{e['citation']}**"
    rest = line[len(head):] if line.startswith(head) else line
    for i in e.get("inflections", []):  # formas flexionadas também na grafia
        if i["gloss"]:
            rest = rest.replace(f"{i['gloss']}: {i['form']}", f"{i['gloss']}: {b.spell(i['form'])}", 1)
    ph = b.phonetic().get(e["citation"])
    head = b.spell(e["citation"])
    if ph and ph.get("changed_written") and b.o.reflect_spelling:
        head = ph["changed_written"]  # a grafia segue a pronúncia nova
    phon = f" [{ph['phonetic']}]" if ph else ""
    irr = b.irregulars().get(e["gloss"])
    if irr:  # forma irregular no lugar da regular: 'go — PST: went (irregular)'
        sup = f"; superlativo **{irr['superlative']['written']}**" if irr.get("superlative") else ""
        tag = irr["label_gloss"].split("-")[-1].split(".")[-1]
        new = f"**{tag}: {irr['irregular']['written']}** (irregular{sup})"
        old = next((f"{i['gloss']}: {b.spell(i['form'])}" for i in e.get("inflections", [])
                    if i["gloss"] == tag), None)
        rest = rest.replace(old, new, 1) if old and old in rest else rest + f" — {new}"

    stem = verb_stem(b, e)
    if stem:  # verbo citado pelo radical; a forma flexionada vira a primeira forma principal
        bare = stem.strip("-")
        written = "-" * stem.startswith("-") + b.spell(bare) + "-" * stem.endswith("-")
        rest = re.sub(r" \[raiz [^\]]*\]", "", rest, count=1)
        lab = f"'{lex_mod.label(e)}'"
        cit = f"citação: {head} /{b.pron(e['citation'])}/{phon}"
        rest = rest.replace(lab + " — ", f"{lab} — {cit}; ", 1) if lab + " — " in rest else rest.replace(lab, f"{lab} — {cit}", 1)
        return f"**{written}** /{b.pron(bare)}/" + rest
    return f"**{head}** /{b.pron(e['citation'])}/{phon}" + rest


def derived_line(b: LanguageBuilder, d: Dict) -> str:
    """Palavra derivada no formato do dicionário, com a base de onde veio."""
    ph = b.phonetic().get(d["ipa"])
    head = ph["changed_written"] if (ph and b.o.reflect_spelling) else d["written"]
    phon = f" [{ph['phonetic']}]" if ph else ""
    pos = {"noun": "n.", "verb": "v.", "adjective": "adj."}.get(d["pos"], d["pos"])
    return (f"**{head}** /{d['pronunciation']}/{phon} *{pos}* '{d['meaning']}' "
            f"← *{d['base_written']}*")


def write_grammar(b: LanguageBuilder, name: str, auto: Dict, validation: Dict) -> Path:
    lang = b.data.get("orthography", {}).get("language_name")
    lines = [f"# {lang['english'] if lang else name}", ""]
    if lang:
        lines += [f"Pasta: `languages/{name}/`", ""]
    lit = f" (literalmente '{auto['literal']}')" if auto.get("literal") else ""
    native = f"**{b.spell(auto['form'])}** /{b.pron(auto['form'])}/" if (b.ortho() or b.stresser()) \
        else f"**{auto['form']}**"
    lines += [f"Nome nativo: {native}{lit}", "",
              f"Semente: `{b.seed}` — gere de novo, a partir de `{ROOT.name}/`, com "
              f"`python {SCRIPT} --seed {b.seed}`", "",
              "A mesma semente com os mesmos dados (PHOIBLE, WALS e listas de conceitos) "
              "gera sempre a mesma língua.", ""]
    lines += phonology_section(b.data["inventory"], b.data["phonotactics"]) + [""]
    if b.data.get("orthography"):
        lines += orthography_section(b) + [""]
    if b.data.get("stress"):
        lines += stress_section(b) + [""]
    if b.data.get("sound_changes"):  # a lista de palavras que mudaram já aparece no dicionário
        lines += ["### Mudanças sonoras", ""] + [
            ("#" + l if l.startswith("### ") else l)
            for l in embedded_section(b, "sound_changes.md", "## Palavras que mudaram")] + [""]
    lines += morphology_section(b) + [""]
    lines += paradigms_section(b) + [""]
    if b.data.get("possession"):  # como no Vulgarlang: posse e adjetivos depois dos paradigmas
        lines += ["## Posse e determinantes", ""] + embedded_section(b, "possession.md") + [""]
    if b.data.get("comparison"):
        lines += ["## Comparação", ""] + embedded_section(b, "comparison.md") + [""]
    if b.data.get("derivation"):  # a lista de palavras derivadas vai para o dicionário
        lines += ["## Derivação", ""] + embedded_section(b, "derivation.md", "## Palavras derivadas") + [""]
    if b.data.get("irregularity"):
        lines += ["## Irregularidades", ""] + embedded_section(b, "irregularity.md") + [""]
    if b.data.get("numerals"):  # como o "List numbers" do Vulgarlang
        lines += ["## Sistema numeral", ""] + embedded_section(b, "numerals.md") + [""]
    lines += ["## Sintaxe", ""] + [f"- {l}" for l in syn_mod.describe(b.data["syntax"]["settings"])]
    for i, ex in enumerate(b.data["syntax"]["examples"], 1):
        lines += ["", f"### {i}. {ex['title']}", ""]
        if b.ortho():  # a frase escrita na grafia da língua, antes da glosa
            written = " ".join(b.spell(w["form"]) for w in ex["words"])
            lines += [f"**{written[:1].upper() + written[1:]}.**", ""]
        lines += ["```"] + syn_mod.interlinear(ex) + ["```"]
    if b.data.get("clauses"):  # voz, demonstrativos, imperativo, orações complexas
        lines += ["", "## Orações", ""] + embedded_section(b, "clauses.md")
    if getattr(b, "translations", None):
        lines += ["", "## Traduções", ""]
        for r in b.translations:
            lines += [f"### {r['english']}", "", f"**{r['written']}**", "", "```"] + syn_mod.interlinear(r) + ["```", ""]
            if r["unknown"]:
                lines += [f"Sem tradução: {', '.join(r['unknown'])}", ""]

    lex = b.data["lexicon"]
    derived = b.data.get("derivation", {}).get("derived", [])
    vocab = b.data.get("vocabulary", {}).get("entries", [])
    num_atoms = [(int(n), a) for n, a in b.data.get("numerals", {}).get("atoms", {}).items() if a.get("from") == "new"]
    extras = [f"{len(derived)} palavras derivadas" if derived else "",
              f"{len(vocab)} do vocabulário ampliado (WOLD)" if vocab else "",
              f"{len(num_atoms)} numerais" if num_atoms else ""]
    extras = [x for x in extras if x]
    lines += ["", "## Dicionário", "",
              f"{len(lex['entries'])} entradas, lista `{lex['metadata']['list']}` do Concepticon"
              + (", mais " + ", ".join(extras) if extras else "") + ".", ""]
    if b.ortho() or b.stresser():
        fmt = "Formato: **grafia** /pronúncia/"
        if b.data.get("sound_changes"):
            fmt += " [pronúncia depois das mudanças sonoras, quando muda]"
        lines += [fmt + " classe 'significado'" + (" ← base, nas derivadas" if derived else ""), ""]
    rows = [(nfd(b.spell(verb_stem(b, e).strip("-") if verb_stem(b, e) else e["citation"])).lower(),
             dictionary_line(b, e))
            for e in lex["entries"] if e["citation"]]
    rows += [(nfd(d["written"]).lower(), derived_line(b, d)) for d in derived]
    for e in vocab:  # vocabulário ampliado: palavras novas, com a origem (← base, = partes)
        pos = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv.", "particle": "part."}.get(e["pos"], e["pos"])
        rows.append((nfd(e["written"]).lower(), f"**{e['written']}** /{e['pronunciation']}/ *{pos}* "
                     f"'{e['label']}'{vocabulary_mod.origin(e)}"))
    for n, a in num_atoms:
        rows.append((nfd(a["written"]).lower(), f"**{a['written']}** /{a['pronunciation']}/ *num.* "
                     f"'{numerals_mod.EN_NUMBERS.get(n, str(n))}'"))
    lines += [f"- {line}" for _, line in sorted(rows, key=lambda r: r[0])]
    bound = [e for e in lex["entries"] if not e["citation"]]
    if bound:
        lines += ["", "Expressos sem palavra própria: " + "; ".join(
            f"'{e['english']}' → " + (f"caso {e['expressed_by']}" if e.get("expressed_by") else e.get("note", ""))
            for e in bound)]

    if b.data.get("names"):
        lines += ["", "## Nomes próprios", ""] + names_section(b)

    if b.custom:
        lines += ["", "## Palavras do usuário", ""] + custom_section(b)

    lines += ["", "## Validação", ""]
    lines.append("- Fonemas fora do inventário: " + (", ".join(validation["foreign_phonemes"]) or "nenhum"))
    lines.append(f"- Formas que o sândi não reparou: {len(validation['invalid_forms'])}")
    if b.ortho():
        lines.append(f"- Grafias que não podem ser lidas de volta: {len(validation['unreadable_spellings'])}")
    if validation["notes"]:
        lines += ["- Avisos dos módulos:"] + [f"  - {n}" for n in validation["notes"]]
    path = b.out / "grammar.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Gera uma língua completa com uma única semente.")
    ap.add_argument("--seed", type=int, help="semente principal (aleatória se omitida)")
    ap.add_argument("--name", help="nome da pasta/língua (padrão: lang-<semente>)")
    ap.add_argument("--out", type=Path, default=DEFAULT_LANGUAGES, help="pasta das línguas")
    ap.add_argument("--from", dest="start", choices=STEPS, default="typology",
                    help="regera a partir desta etapa, mantendo as anteriores")

    g = ap.add_argument_group("restrições da tipologia")
    g.add_argument("--synthesis", choices=["isolating", "synthetic", "polysynthetic"])
    g.add_argument("--fusion", choices=["none", "agglutinative", "fusional"])
    g.add_argument("--affix-position", choices=["little_affixation", "strongly_suffixing",
                                                 "weakly_suffixing", "equal", "weakly_prefixing",
                                                 "strongly_prefixing"])
    g.add_argument("--locus", choices=["head_marking", "dependent_marking", "double_marking", "no_marking"])
    g.add_argument("--typology-file", help="usa um morphological_typology.json pronto")

    g = ap.add_argument_group("restrições da fonologia")
    g.add_argument("--inventory-mode", choices=["feature", "real"], default="feature")
    g.add_argument("--consonants", type=int)
    g.add_argument("--vowels", type=int)
    t = g.add_mutually_exclusive_group()
    t.add_argument("--tones", dest="tones", action="store_true", default=None)
    t.add_argument("--no-tones", dest="tones", action="store_false")
    g.add_argument("--complexity", choices=["simple", "moderate", "complex"])

    g = ap.add_argument_group("léxico e sintaxe")
    g.add_argument("--list", default="all", help="leipzig-jakarta | swadesh-200 | all | lista do Concepticon")
    g.add_argument("--order", choices=["SOV", "SVO", "VSO", "VOS", "OVS", "OSV"])

    g = ap.add_argument_group("ortografia e acento")
    g.add_argument("--style", choices=ortho_mod.STYLES if ortho_mod else None,
                   help="estilo da grafia (sorteado se omitido)")
    g.add_argument("--stress-rule", choices=list(stress_mod.RULES_PT) if stress_mod else None,
                   help="regra de acento (sorteada se omitida)")

    g = ap.add_argument_group("derivação e mudanças sonoras")
    g.add_argument("--derive-per-process", type=int, default=12, help="palavras derivadas por processo")
    g.add_argument("--derive-all", action="store_true", help="deriva de todas as bases possíveis")
    g.add_argument("--sound-change", action="append", default=[],
                   help="regra de mudança sonora do usuário, ex: \"a > e / _k\" (pode repetir)")
    g.add_argument("--no-natural-changes", action="store_true", help="não sorteia mudanças sonoras naturais")
    g.add_argument("--reflect-spelling", action="store_true", help="a grafia segue a pronúncia depois das mudanças")

    g = ap.add_argument_group("numerais, vocabulário e tradução")
    g.add_argument("--number-base", choices=["decimal", "quinary", "vigesimal", "hybrid", "restricted", "body_part"],
                   help="base dos numerais (sorteada se omitida)")
    g.add_argument("--numbers-upto", type=int, default=20, help="lista os numerais de 1 até N")
    g.add_argument("--include-modern", action="store_true", help="vocabulário do 'mundo moderno' (carro, rádio...)")
    g.add_argument("--translate", type=Path, help="arquivo de frases em inglês para traduzir (uma por linha)")

    g = ap.add_argument_group("evolução")
    g.add_argument("--evolve", action="append", default=[], metavar="PERFIL:ANOS",
                   help="gera uma língua-filha, ex: romance:1500 (pode repetir)")
    g.add_argument("--no-evolve-grammar", action="store_true", help="filhas sem a etapa 3 (gramática)")
    g.add_argument("--family", type=int, metavar="RAMOS", help="gera uma família com N ramos principais")

    g = ap.add_argument_group("nomes próprios")
    g.add_argument("--people", type=int, default=20, help="quantidade de nomes de pessoa")
    g.add_argument("--places", type=int, default=20, help="quantidade de nomes de lugar")

    g = ap.add_argument_group("palavras e fonemas do usuário")
    g.add_argument("--custom", help="arquivo com [fonemas], [verbos], [substantivos], [adjetivos], [outras]")
    g.add_argument("--custom-policy", choices=["adapt", "exception"], default="adapt",
                   help="adapt: a fonotática aprende com as palavras; exception: viram irregulares")

    g = ap.add_argument_group("dados")
    g.add_argument("--phoible", type=Path, default=inv_mod.DEFAULT_PHOIBLE)
    g.add_argument("--wals", type=Path, default=DEFAULT_WALS)
    g.add_argument("--no-wals", action="store_true")
    g.add_argument("--concepticon", type=Path, default=lex_mod.DEFAULT_CONCEPTICON)
    return ap.parse_args(argv)


def generate(seed: Optional[int] = None, name: Optional[str] = None, **options) -> Path:
    """
    Uso como biblioteca. As opções seguem os nomes da linha de comando:
        generate(31, name="elfico", synthesis="isolating", order="SVO", tones=False)
    Devolve a pasta da língua.
    """
    argv: List[str] = [] if seed is None else ["--seed", str(seed)]
    if name:
        argv += ["--name", name]
    for key, value in options.items():
        flag = "--from" if key == "start" else "--" + key.replace("_", "-")
        if key == "tones" and value is False:
            argv.append("--no-tones")
        elif isinstance(value, (list, tuple)):  # opções repetíveis: --sound-change, --evolve
            for v in value:
                argv += [flag, str(v)]
        elif value is True:
            argv.append(flag)
        elif value not in (None, False):
            argv += [flag, str(value)]
    return run(parse_args(argv))


def main() -> None:
    run(parse_args())


def run(args: argparse.Namespace) -> Path:
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1_000_000)
    name = args.name or f"lang-{seed}"
    out_dir = args.out / name
    print(f"\nGerando '{name}' (semente {seed}) em {out_dir}/")

    b = LanguageBuilder(seed, out_dir, args)
    try:
        b.build(args.start)
    except SystemExit:
        if out_dir.exists() and not any(out_dir.iterdir()):
            out_dir.rmdir()  # não deixa pasta vazia para trás
        raise
    validation = b.validate()
    auto = b.autonym()
    if b.data.get("vocabulary", {}).get("metadata", {}).get("missing_list"):
        validation["notes"].append("Vocabulário: falta vocabulary/wold_1460.tsv; o vocabulário ampliado não foi gerado")
    if args.translate and translator_mod:
        t = translator_mod.Translator(out_dir)
        sentences = [x.strip() for l in Path(args.translate).read_text(encoding="utf-8").splitlines()
                     for x in re.split(r"(?<=[.!?])\s+", l) if x.strip()]
        b.translations = [t.translate(x) for x in sentences]
        (out_dir / "translations.md").unlink(missing_ok=True)
        translator_mod.save(out_dir / "translations.md", b.translations)
        print(f"  Traduções: {len(b.translations)} frases (translations.md)")
    grammar = write_grammar(b, name, auto, validation)
    dest = ROOT / "LLM_refinement" / name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(grammar, dest / "grammar.md")

    manifest = {
        "name": name, "seed": seed, "seeds": b.seeds, "autonym": auto,
        "options": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()
                    if k not in ("phoible", "wals", "concepticon", "out")},
        "files": [FILES[s] for s in STEPS] + ["dictionary.md", "examples.md", "grammar.md"]
                 + (["orthography.md"] if "orthography" in STEPS else [])
                 + (["stress.md"] if "stress" in STEPS else [])
                 + (["names.md"] if "names" in STEPS else [])
                 + (["possession.md"] if "possession" in STEPS else [])
                 + (["comparison.md"] if "comparison" in STEPS else [])
                 + (["derivation.md"] if "derivation" in STEPS else [])
                 + (["sound_changes.md"] if "sound_changes" in STEPS else [])
                 + (["irregularity.md"] if "irregularity" in STEPS else [])
                 + (["numerals.md"] if "numerals" in STEPS else [])
                 + (["vocabulary.md"] if "vocabulary" in STEPS else [])
                 + (["clauses.md"] if "clauses" in STEPS else [])
                 + (["translations.md"] if getattr(b, "translations", None) else []),
        "language_name": b.data.get("orthography", {}).get("language_name"),
        "validation": validation,
        "custom": ({"file": "custom.txt", "policy": args.custom_policy, "report": b.custom_report,
                    "warnings": b.custom["warnings"]} if b.custom else None),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    lit = f" ('{auto['literal']}')" if auto.get("literal") else ""
    lang = b.data.get("orthography", {}).get("language_name")
    if lang:
        print(f"\n  Língua: {lang['english']} — nativamente {lang['native']} /{b.pron(auto['form'])}/{lit}")
    else:
        print(f"\n  Nome nativo: {auto['form']}{lit}")
    if validation.get("unreadable_spellings"):
        print(f"  [!] {len(validation['unreadable_spellings'])} grafias ambíguas")
    if validation["foreign_phonemes"]:
        print("  [!] Fonemas fora do inventário: " + ", ".join(validation["foreign_phonemes"]))
    if validation["invalid_forms"]:
        print(f"  [!] {len(validation['invalid_forms'])} formas que o sândi não reparou")
    for n in validation["notes"]:
        print(f"  · {n}")
    if b.custom:
        r = b.custom_report
        n_ok = sum(1 for x in r.get("lexicon", []) if x["valid"])
        print(f"  ★ Palavras do usuário: {len(r.get('lexicon', []))} ({n_ok} válidas pela fonotática)")
        for c in r.get("phonotactics", {}).get("changes", []):
            print(f"    · {c}")
        for w in b.custom["warnings"]:
            print(f"    [!] {w}")
    print(f"\n[OK] Língua completa em {out_dir}/ — comece por {grammar.name}")
    if args.evolve or args.family:
        evolve_after(args, seed, name, out_dir)
    return out_dir


def evolve_after(args: argparse.Namespace, seed: int, name: str, out_dir: Path) -> None:
    """Línguas-filhas (--evolve) e famílias (--family), depois da língua-mãe pronta."""
    sys.path.insert(0, str(ROOT / "evolution"))
    try:
        import evolution as evo_mod
        import grammar_evolution as gram_mod
    except ImportError:
        print("  [!] Pasta evolution/ não encontrada: --evolve e --family foram ignorados")
        return
    for spec in args.evolve:
        profile, _, years = spec.partition(":")
        years = int(years or 1000)
        daughter = f"{name}-{profile}-{years}"
        print(f"\nEvoluindo '{name}' → '{daughter}' ({profile}, {years} anos)")
        ev = evo_mod.Evolver(out_dir, profile, years)
        result = ev.build(args.out / daughter)
        if not args.no_evolve_grammar:
            result = gram_mod.GrammarEvolver(args.out / daughter).run()
        generate(seed, name=daughter, out=args.out, start="orthography", no_wals=args.no_wals,
                 translate=args.translate)
        spell = lambda d: (__import__("orthography").Orthography(json.loads((d / "orthography.json").read_text(  # noqa: E731
            encoding="utf-8"))).spell if (d / "orthography.json").exists() else None)
        evo_mod.write_markdown(args.out / daughter / "evolution.md", result, spell(args.out / daughter), spell(out_dir))
        if not args.no_evolve_grammar:
            gram_mod.write_markdown(args.out / daughter, result, spell(args.out / daughter))
        laws = ", ".join(x["name"] for x in result["laws"])
        print(f"  Leis: {laws}")
    if args.family:
        import family as fam_mod
        print(f"\nFamília de '{name}' ({args.family} ramos)")
        fb = fam_mod.FamilyBuilder(out_dir, branches=args.family, grammar=not args.no_evolve_grammar)
        root = fb.build(rebuild=False)
        cmp = fam_mod.Comparison(root)
        data = {"cognates": cmp.cognate_table(fam_mod.CORE), "correspondences": cmp.correspondences(),
                "distances": cmp.distances()}
        fam_dir = args.out / f"{name}-familia"
        fam_dir.mkdir(exist_ok=True)
        fam_mod.write_family(fam_dir / "family.md", root, cmp, data)
        tree = [{"name": n.name, "parent": n.parent.name if n.parent else None, "profile": n.profile,
                 "years": n.years, "folder": n.dir.name, "laws": [x["id"] for x in (n.evo or {}).get("laws", [])]}
                for n in root.all()]
        (fam_dir / "family.json").write_text(json.dumps(
            {"proto": root.name, "seed": fb.seed, "tree": tree, "cognates": data["cognates"],
             "correspondences": {"languages": data["correspondences"][0], "rows": data["correspondences"][1]},
             "distances": {"languages": data["distances"][0], "matrix": data["distances"][1]}},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print("\n".join("  " + l for l in fam_mod.ascii_tree(root)))
        print(f"  Família em {fam_dir}/ (para a grafia e o grammar.md de cada língua, use evolution/family.py --rebuild)")


if __name__ == "__main__":
    main()