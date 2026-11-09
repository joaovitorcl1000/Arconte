"""
Módulo — Nomes próprios (pessoas, famílias e lugares).

Gera nomes que soam como a conlang e, quando possível, significam algo nela:

    pessoas  — nomes opacos (sem significado) ou descritivos ("Pássaro-Veloz"),
               com terminações de gênero quando a língua as tem
    famílias — patronímicos ("filho de X") e sobrenomes descritivos
    lugares  — compostos ("Pedra-Negra"), sintagmas ("Rio Escuro"), lugares com
               sufixo de povoado, formas no caso locativo e nomes antigos opacos

Tudo respeita a fonotática e o sândi da língua, e é escrito na ortografia e
acentuado quando os módulos de ortografia e acento existirem.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
dos módulos (motor morfológico, ortografia, acento).

Uso:
    python names/names.py --language languages/lang-31
    python names/names.py --language languages/lang-31 --people 30 --places 30

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

# Conceitos usados para montar nomes com significado.
# Lugares: núcleo geográfico (rio, montanha...) + qualidade, material ou animal.
PLACE_HEADS = ["RIVER", "LAKE", "SEA", "MOUNTAIN", "STONE OR ROCK", "STONE", "FOREST", "TREE", "ROAD",
               "HOUSE", "SAND", "WATER", "GRASS", "EARTH (SOIL)"]
PLACE_QUALITIES = ["BIG", "SMALL", "LONG", "BLACK", "WHITE", "RED", "GREEN", "YELLOW", "OLD", "NEW",
                   "COLD (OF WEATHER)", "WARM (OF WEATHER)", "DRY", "WET", "FAR", "WIDE", "NARROW"]
PLACE_NOUN_MODIFIERS = ["STONE", "SALT", "SAND", "ICE", "SNOW", "FIRE", "WIND", "SUN", "STAR", "FOG",
                        "ASH", "TREE", "FLOWER", "GRASS", "ROOT", "BIRD", "DOG", "FISH", "SNAKE", "BONE"]
# Pessoas: qualidade + elemento da natureza, animal ou parte do corpo.
PERSON_QUALITIES = ["BIG", "SMALL", "LONG", "BLACK", "WHITE", "RED", "GREEN", "YELLOW", "OLD", "NEW",
                    "GOOD", "SHARP", "HARD", "SWEET", "WARM (OF WEATHER)", "COLD (OF WEATHER)", "HEAVY"]
PERSON_HEADS = ["FIRE", "STAR", "SUN", "MOON", "WIND", "STONE", "TREE", "FLOWER", "RIVER", "CLOUD",
                "SNOW", "SEA", "BIRD", "SNAKE", "DOG", "FISH", "HEART", "EYE", "HAND", "WING", "FEATHER"]
GEO = ["RIVER", "SEA", "LAKE", "MOUNTAIN", "STONE", "STONE OR ROCK", "SAND", "EARTH (SOIL)", "TREE",
       "FOREST", "WATER", "FIRE", "SKY", "STAR", "SUN", "MOON", "CLOUD", "ICE", "SNOW", "ROAD",
       "HOUSE", "WIND", "SALT", "DUST", "ASH", "FOG", "NIGHT", "DAY (NOT NIGHT)", "GRASS", "ROOT",
       "LEAF", "FLOWER", "WOOD", "SMOKE (EXHAUST)"]
NATURE = ["FIRE", "STAR", "SUN", "MOON", "WIND", "STONE", "TREE", "FLOWER", "LEAF", "RIVER", "SKY",
          "CLOUD", "SNOW", "ICE", "NIGHT", "DAY (NOT NIGHT)", "WATER", "ROOT", "SEED", "SEA"]
ANIMALS = ["BIRD", "DOG", "FISH", "SNAKE", "WORM", "LOUSE", "ANT", "ANIMAL", "FLY (INSECT)"]
BODY = ["HEART", "EYE", "HAND", "HEAD", "WING", "FEATHER", "TOOTH", "HORN (ANATOMY)", "BONE", "TONGUE"]
QUALITIES = ["BIG", "SMALL", "LONG", "SHORT", "BLACK", "WHITE", "RED", "GREEN", "YELLOW", "OLD",
             "NEW", "GOOD", "COLD (OF WEATHER)", "WARM (OF WEATHER)", "DRY", "WET", "FAR", "NEAR",
             "HEAVY", "SHARP", "STRAIGHT", "SWEET", "THICK", "THIN", "WIDE", "HARD", "SMOOTH"]

PLACE_TEMPLATES = {"compound": 0.30, "phrase": 0.20, "settlement": 0.20, "locative": 0.10, "opaque": 0.20}
PERSON_MEANINGFUL = 0.35  # fração dos nomes de pessoa com significado transparente


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def short(e: Dict) -> str:
    label = (e.get("label") or e["english"].split(" (")[0]).split("/")[0]
    return label[3:] if label.startswith("to ") else label


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


# ═══════════════════════════════════════════════════════════════════════════
# Gerador
# ═══════════════════════════════════════════════════════════════════════════

class NameGenerator:
    def __init__(self, language_dir: Path, seed: Optional[int] = None):
        d = language_dir
        self.inv = _load(d / "phonemic_inventory.json")
        self.rules = _load(d / "phonotactics.json")
        self.cats = _load(d / "grammatical_categories.json")
        self.morph = _load(d / "morphology.json")
        self.lex = _load(d / "lexicon.json")
        if not all((self.inv, self.rules, self.cats, self.morph, self.lex)):
            raise SystemExit(f"A pasta {d} precisa ter inventário, fonotática, categorias, "
                             "morfologia e léxico (gere a língua com o orquestrador).")
        self.syntax = _load(d / "syntax.json")
        typology = _load(d / "morphological_typology.json") or {}
        manifest = _load(d / "manifest.json")
        if seed is None:
            seed = derive_seed(manifest["seed"], "names") if manifest else 0
        self.seed = seed
        self.rng = random.Random(seed)
        self.eng = MorphologicalEngine.load(self.morph, self.inv, self.rules, self.cats, typology)
        self.ph = self.eng.ph
        self.ph.rng = random.Random(seed + 1)  # sorteios próprios, independentes do léxico

        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules, derive_seed(manifest["seed"], "stress"))
                       if (stress_mod and s_spec and manifest) else None)

        self.entries = {e["gloss"]: e for e in self.lex["entries"] if e.get("citation")}
        self.used = {self._plain(e["citation"]) for e in self.lex["entries"] if e.get("citation")}
        self.symbols = sorted({nfd(x["ipa"]) for x in self.inv["consonants"] + self.inv["vowels"]},
                              key=len, reverse=True)
        self.vowels = {nfd(v["ipa"]) for v in self.inv["vowels"]}
        self.head_final = self.lex["settings"].get("compound_head", "final") == "final"
        self.adj_after = bool(self.syntax and self.syntax["settings"]["noun_phrase"]["adjective"] == "after")
        self.settings = self._settings()

    # ── utilidades fonológicas ───────────────────────────────────────────
    @staticmethod
    def _plain(form: str) -> str:
        return "".join(ch for ch in nfd(form) if ch not in TONE_LETTERS + ".ˈˌ")

    def segments(self, form: str) -> List[str]:
        """Forma de citação → fonemas (respeitando pontos de sílaba, se houver)."""
        out = []
        for syl in nfd(form).split("."):
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                out.append(hit or s[i])
                i += len(hit) if hit else 1
        return out

    def join(self, parts: List[List[str]]) -> Optional[List[str]]:
        """Junta morfemas aplicando o sândi da língua; None se não houver forma válida."""
        morphs = [{"segs": list(p), "role": "root" if i == 0 else "suffix", "label": "", "sep": "-"}
                  for i, p in enumerate(parts) if p]
        morphs, ok, _ = self.eng.resolve(morphs)
        return [s for m in morphs for s in m["segs"]] if ok else None

    def euphony(self, segs: List[str]) -> float:
        """Nomes soam melhor com mais soantes e menos encontros consonantais."""
        son = self.rules["sonority"]
        sonorous = sum(1 for s in segs if son.get(s, 1) >= 3) / max(1, len(segs))
        clusters = sum(1 for a, b in zip(segs, segs[1:]) if a not in self.vowels and b not in self.vowels)
        return sonorous - 0.3 * clusters - 0.4 * self.hiatus(segs) + self.rng.random() * 0.4

    def hiatus(self, segs: List[str]) -> int:
        """Vogais em sequência (ia, aːaː): possíveis, mas pouco agradáveis em nomes."""
        return sum(1 for a, b in zip(segs, segs[1:]) if a in self.vowels and b in self.vowels)

    def finish(self, segs: List[str], words: int = 1) -> Dict:
        """IPA, pronúncia com acento e grafia com maiúscula de uma forma pronta."""
        ipa = "".join(segs)
        if self.rules.get("tone_bearing") and self.ph.tones:
            sylls = self.ph.syllabify(segs)
            if sylls:
                ipa = self.ph._with_tones(sylls)[1]
        pron = self.stress.mark(ipa) if self.stress else ipa
        written = self.ortho.spell(ipa) if self.ortho else ipa.replace(".", "")
        written = " ".join(w[:1].upper() + w[1:] for w in written.split(" "))
        tonal = any(ch in TONE_LETTERS for ch in ipa)  # formas tonais mantêm os pontos de sílaba
        return {"name": written, "ipa": ipa if tonal else ipa.replace(".", ""), "pronunciation": pron}

    # ── configuração da língua ───────────────────────────────────────────
    def _settings(self) -> Dict:
        """Morfemas e estratégias próprios de cada língua (sorteados uma vez)."""
        r = self.rng
        s: Dict = {}
        g = self.cats["categories"].get("gender", {})
        finals = self.lex["settings"].get("gender_finals")
        if finals and "masculine" in finals and "feminine" in finals:
            s["gender_endings"] = {"male": [finals["masculine"]], "female": [finals["feminine"]],
                                   "source": "vogais finais do gênero gramatical"}
        elif r.random() < 0.5:
            vowels = sorted(self.eng._short_plain_vowels())
            if len(vowels) >= 2:
                m, f = r.sample(vowels, 2)
                s["gender_endings"] = {"male": [m], "female": [f], "source": "convenção dos nomes"}

        child = self.entries.get("CHILD (DESCENDANT)") or self.entries.get("CHILD (YOUNG HUMAN)")
        case_vals = self.cats["categories"]["case"].get("values", []) \
            if self.cats["categories"]["case"].get("grammaticalized") else []
        options = {"compound_child": 0.4 if child else 0, "genitive": 0.35 if "genitive" in case_vals else 0,
                   "suffix": 0.25, "none": 0.15}
        strategy = r.choices(list(options), list(options.values()))[0]
        s["patronymic"] = {"strategy": strategy}
        if strategy == "suffix":
            s["patronymic"]["morpheme"] = self.ph.generate_affix("suffix")["segments"]
        if strategy == "compound_child":
            s["patronymic"]["word"] = child["gloss"]

        s["settlement_suffix"] = self.ph.generate_affix("suffix")["segments"]
        s["locative_case"] = next((c for c in ("locative", "essive", "allative") if c in case_vals), None)
        return s

    # ── pessoas ──────────────────────────────────────────────────────────
    def _opaque(self, syllables: Tuple[int, int] = (2, 3), ending: Optional[str] = None) -> List[str]:
        best, best_score = None, -9.0
        for _ in range(30):
            n = self.rng.randint(*syllables)
            segs = self.ph.generate_root(n)["segments"]
            if self.eng.skeleton:  # raízes consonantais: usa sílabas livres
                segs = [x for syl in self.ph.generate_syllables(n) for x in syl]
            if ending:
                segs = segs[:-1] + [ending] if segs[-1] in self.vowels else segs + [ending]
                if not self.ph.is_valid(segs):
                    continue
            if self._plain("".join(segs)) in self.used or self._looks_patronymic(segs):
                continue
            score = self.euphony(segs)
            if score > best_score:
                best, best_score = segs, score
        return best or self.ph.generate_root(2)["segments"]

    def _looks_patronymic(self, segs: List[str]) -> bool:
        """Nomes próprios não devem terminar como o sufixo patronímico (evita 'Kropyam' = 'filho de Kropy')."""
        suf = self.settings.get("patronymic", {}).get("morpheme") if hasattr(self, "settings") else None
        return bool(suf) and len(segs) > len(suf) and segs[-len(suf):] == suf

    def _pick(self, glosses: List[str], used: Optional[set] = None) -> Optional[Dict]:
        pool = [self.entries[g] for g in glosses if g in self.entries and (not used or g not in used)]
        return self.rng.choice(pool) if pool else None

    def _compound(self, modifier: Dict, head: Dict) -> Optional[Tuple[List[str], str]]:
        a, b = self.segments(modifier["citation"]), self.segments(head["citation"])
        parts = [a, b] if self.head_final else [b, a]
        segs = self.join(parts)
        if not segs:
            return None
        meaning = f"{short(modifier)} {short(head)}"
        return segs, meaning

    def _short_pick(self, glosses: List[str], tries: int = 4) -> Optional[Dict]:
        """Entre alguns conceitos sorteados, o de forma mais curta (topônimos tendem a ser curtos)."""
        cands = [c for c in (self._pick(glosses) for _ in range(tries)) if c]
        return min(cands, key=lambda e: len(self.segments(e["citation"])) + self.rng.random() * 2) if cands else None

    def best_compound(self, modifiers: List[str], heads: List[str],
                      tries: int = 5) -> Optional[Tuple[List[str], str, Dict, Dict]]:
        """Testa alguns pares e fica com o composto mais curto (nomes longos demais soam artificiais)."""
        best, best_score = None, 1e9
        for _ in range(tries):
            h = self._pick(heads)
            m = self._pick(modifiers, used={h["gloss"]} if h else None)
            if not (h and m):
                return None
            c = self._compound(m, h)
            if not c or self._plain("".join(c[0])) in self.used:
                continue  # nunca repete um nome nem uma palavra do dicionário
            score = len(c[0]) + 3 * self.hiatus(c[0]) + self.rng.random() * 3
            if score < best_score:
                best, best_score = (c[0], c[1], m, h), score
        return best

    def person(self, gender: Optional[str] = None) -> Dict:
        """Um nome de pessoa: opaco ou descritivo, com terminação de gênero quando houver."""
        endings = self.settings.get("gender_endings")
        if gender is None:
            gender = self.rng.choice(["male", "female"]) if endings else "any"
        ending = self.rng.choice(endings[gender]) if endings and gender in endings else None
        out: Optional[Dict] = None
        if self.rng.random() < PERSON_MEANINGFUL:
            c = self.best_compound(PERSON_QUALITIES, PERSON_HEADS)
            if c and not self._looks_patronymic(c[0]):
                if True:
                    segs, meaning, q, h = c
                    if ending and segs[-1] != ending:
                        alt = segs[:-1] + [ending] if segs[-1] in self.vowels else segs + [ending]
                        segs = alt if self.ph.is_valid(alt) else segs
                    if self._plain("".join(segs)) not in self.used:  # a terminação pode recriar um nome
                        out = {**self.finish(segs), "meaning": meaning,
                               "etymology": f"{short(q)} + {short(h)}"}
        if out is None:
            out = {**self.finish(self._opaque(ending=ending)), "meaning": None, "etymology": None}
        out["gender"] = gender
        out["_segs"] = self.segments(out["ipa"])
        self.used.add(self._plain(out["ipa"]))
        return out

    def surname(self, father: Optional[Dict] = None) -> Dict:
        """Patronímico ('filho de X') ou sobrenome descritivo."""
        st = self.settings["patronymic"]["strategy"]
        if father and st != "none":
            fsegs = father["_segs"]
            if st == "genitive":
                lex = {"root": fsegs, "form": "".join(fsegs), "tones": [], "class": 0, "gender": None}
                form = self.eng.inflect(lex, "noun", {"case": "genitive"})["surface"]
                segs = self.segments(form)
            elif st == "suffix":
                segs = self.join([fsegs, self.settings["patronymic"]["morpheme"]])
            else:
                child = self.entries[self.settings["patronymic"]["word"]]
                segs = self.join([fsegs, self.segments(child["citation"])] if self.head_final
                                 else [self.segments(child["citation"]), fsegs])
            if segs:
                return {**self.finish(segs), "meaning": f"child of {father['name']}", "type": "patronymic"}
        c = self.best_compound(PLACE_QUALITIES, PLACE_HEADS)
        if c:
            return {**self.finish(c[0]), "meaning": c[1], "type": "descriptive"}
        return {**self.finish(self._opaque((2, 3))), "meaning": None, "type": "opaque"}

    def full_person(self, gender: Optional[str] = None) -> Dict:
        given = self.person(gender)
        father = self.person("male" if self.settings.get("gender_endings") else None)
        fam = self.surname(father)
        given.pop("_segs", None)
        return {"given": given, "family": fam,
                "full": f"{given['name']} {fam['name']}" if fam else given["name"]}

    # ── lugares ──────────────────────────────────────────────────────────
    def place(self, template: Optional[str] = None) -> Dict:
        """Um nome de lugar, num dos cinco modelos."""
        t = template or self.rng.choices(list(PLACE_TEMPLATES), list(PLACE_TEMPLATES.values()))[0]
        if t == "locative" and not self.settings["locative_case"]:
            t = "compound"
        geo = self._short_pick(PLACE_HEADS)
        mod = self._pick(PLACE_QUALITIES, used={geo["gloss"]} if geo else None)
        result: Optional[Dict] = None
        if t == "compound":
            c = self.best_compound(PLACE_QUALITIES + PLACE_NOUN_MODIFIERS, PLACE_HEADS)
            if c:
                result = {**self.finish(c[0]), "meaning": c[1]}
        elif t == "phrase" and geo and mod:
            q = mod
            a, b = self.segments(geo["citation"]), self.segments(q["citation"])
            words = [b, a] if not self.adj_after else [a, b]
            parts = [self.finish(w) for w in words]
            result = {"name": " ".join(p["name"] for p in parts), "ipa": " ".join(p["ipa"] for p in parts),
                      "pronunciation": " ".join(p["pronunciation"] for p in parts),
                      "meaning": f"{short(q)} {short(geo)}"}
        elif t == "settlement":
            base = self._short_pick(PLACE_HEADS + PLACE_NOUN_MODIFIERS)
            stem = self.segments(base["citation"]) if base else self._opaque((1, 2))
            segs = self.join([stem, self.settings["settlement_suffix"]])
            if segs:
                result = {**self.finish(segs),
                          "meaning": f"{short(base)}-town" if base else "town"}
        elif t == "locative" and geo:
            lex = {"root": self.segments(geo["citation"]), "form": geo["citation"], "tones": [],
                   "class": geo.get("class") or 0, "gender": geo.get("gender")}
            form = self.eng.inflect(lex, "noun", {"case": self.settings["locative_case"]})["surface"]
            result = {**self.finish(self.segments(form)), "meaning": f"at the {short(geo)}"}
        if result is not None and self._plain(result["ipa"]) in self.used:
            result = None  # já existe um lugar (ou palavra) com esse nome
        if result is None:
            t = "opaque"
            result = {**self.finish(self._opaque((2, 3))), "meaning": None}
        result["template"] = t
        self.used.add(self._plain(result["ipa"]))
        return result


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

TEMPLATE_PT = {"compound": "composto", "phrase": "sintagma", "settlement": "povoado",
               "locative": "locativo", "opaque": "antigo (sem significado)"}
GENDER_PT = {"male": "masc.", "female": "fem.", "any": "—"}
PATRONYMIC_PT = {"compound_child": "nome do pai + palavra para 'filho'",
                 "genitive": "nome do pai no genitivo ('de X')",
                 "suffix": "nome do pai + sufixo patronímico", "none": "sem patronímicos"}


def describe(g: NameGenerator) -> List[str]:
    s = g.settings
    lines = []
    if s.get("gender_endings"):
        e = s["gender_endings"]
        sp = (lambda x: g.ortho.spell(x)) if g.ortho else (lambda x: x)
        lines.append(f"Nomes masculinos terminam em -{sp(e['male'][0])}, femininos em -{sp(e['female'][0])} "
                     f"({e['source']})")
    else:
        lines.append("Nomes sem marca de gênero")
    p = s["patronymic"]
    extra = f" (-{''.join(p['morpheme'])})" if p.get("morpheme") else ""
    lines.append(f"Sobrenomes: {PATRONYMIC_PT[p['strategy']]}{extra}")
    suf = "".join(s["settlement_suffix"])
    lines.append(f"Sufixo de povoado: -{g.ortho.spell(suf) if g.ortho else suf} /-{suf}/")
    return lines


def write_markdown(path: Path, g: NameGenerator, people: List[Dict], places: List[Dict]) -> None:
    lines = ["# Nomes próprios", ""] + [f"- {l}" for l in describe(g)]
    lines += ["", "## Pessoas", "", "| Nome | Pronúncia | Gênero | Significado | Sobrenome | Significado |",
              "|---|---|---|---|---|---|"]
    for p in people:
        gv, fm = p["given"], p["family"]
        lines.append(f"| **{gv['name']}** | /{gv['pronunciation']}/ | {GENDER_PT[gv['gender']]} | "
                     f"{gv['meaning'] or '—'} | {fm['name']} | {fm['meaning'] or '—'} |")
    lines += ["", "## Lugares", "", "| Nome | Pronúncia | Tipo | Significado |", "|---|---|---|---|"]
    for pl in places:
        lines.append(f"| **{pl['name']}** | /{pl['pronunciation']}/ | {TEMPLATE_PT[pl['template']]} | "
                     f"{pl['meaning'] or '—'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera nomes de pessoas e lugares na conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--people", type=int, default=20, help="quantidade de pessoas")
    ap.add_argument("--places", type=int, default=20, help="quantidade de lugares")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    args = ap.parse_args()

    g = NameGenerator(args.language, args.seed)
    people = [g.full_person() for _ in range(args.people)]
    places = [g.place() for _ in range(args.places)]
    data = {"settings": {k: v for k, v in g.settings.items()}, "people": people, "places": places,
            "metadata": {"seed": g.seed, "spelled": g.ortho is not None, "stressed": g.stress is not None}}
    (args.language / "names.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "names.md", g, people, places)

    print("\nNOMES PRÓPRIOS")
    for l in describe(g):
        print(f"  {l}")
    print("\n  Pessoas:")
    for p in people[:10]:
        gv, fm = p["given"], p["family"]
        m = f" '{gv['meaning']}'" if gv["meaning"] else ""
        print(f"    {p['full']:<28} /{gv['pronunciation']}/{m}")
    print("\n  Lugares:")
    for pl in places[:10]:
        m = f" '{pl['meaning']}'" if pl["meaning"] else ""
        print(f"    {pl['name']:<28} /{pl['pronunciation']}/ ({TEMPLATE_PT[pl['template']]}){m}")
    print(f"\n[OK] Nomes salvos em '{args.language / 'names.json'}' e 'names.md'.")


if __name__ == "__main__":
    main()
