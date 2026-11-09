"""
Módulo — Mudanças sonoras.

Aplica regras de mudança sonora às palavras da conlang, como o campo "Sound
changes" do Vulgarlang, na mesma notação:

    a > e                 todo a vira e
    a > e / _k            a vira e antes de k
    a > e / #_            a vira e no início da palavra
    C > ∅ / _#            consoantes caem no fim da palavra
    {p,b} > m / V_V       p ou b viram m entre vogais
    {p,t,k} > {b,d,ɡ} / V_V   cada uma vira a correspondente da segunda lista
    ∅ > e / #_s           insere e antes de s no início da palavra

As regras podem vir do usuário (--rule, --rules-file) e/ou ser sorteadas entre
mudanças comuns nas línguas do mundo (sonorização entre vogais, ensurdecimento
final, palatalização, assimilação nasal...), sempre testadas contra o léxico
para só entrarem as que de fato mudam alguma palavra.

O resultado é a pronúncia fonética: a forma subjacente /.../ continua sendo a do
dicionário, e a forma depois das mudanças aparece entre colchetes [...], como no
Vulgarlang ("Show changes in square brackets"). Com --reflect-spelling, a grafia
passa a seguir a forma nova, e sons que não existiam ganham letras próprias.

Não altera nenhum outro módulo: lê os JSONs da língua e usa as funções públicas
da ortografia e do acento.

Uso:
    python sound_changes/sound_changes.py --language languages/lang-31
    python sound_changes/sound_changes.py --language languages/lang-31 --rule "a > e / _k" --no-natural
    python sound_changes/sound_changes.py --language languages/lang-31 --rules-file minhas_regras.txt

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in ("orthography", "stress", "phonotactics"):
    sys.path.insert(0, str(ROOT / folder))
try:
    import orthography as ortho_mod  # noqa: E402
except ImportError:
    ortho_mod = None
try:
    import stress as stress_mod  # noqa: E402
except ImportError:
    stress_mod = None

TONE_LETTERS = "˥˦˧˨˩"
NULL = {"∅", "0", "Ø"}

# Classes de sons (letras maiúsculas na notação)
CLASS_PT = {"C": "consoante", "V": "vogal", "P": "oclusiva", "F": "fricativa", "N": "nasal",
            "L": "líquida", "G": "semivogal"}
STOPS = set("pbtdkɡgqɢcɟʔʈɖ")
FRICATIVES = set("fvszʃʒxɣχʁhɦθðçʝβɸħʕɬɮɕʑʂʐ")
NASALS = set("mnŋɲɳɱɴ")
LIQUIDS = set("lrɾɹɻɽɭʎʀɺ")
GLIDES = set("jwɥɰ")
VOWEL_LETTERS = set("aeiouyɛɔəɨʉɯɪʊæɑɒøœɐɤʌɵɘ")

# Pares para as mudanças naturais
VOICING = {"p": "b", "t": "d", "k": "ɡ", "q": "ɢ", "c": "ɟ", "f": "v", "s": "z", "ʃ": "ʒ",
           "t̠ʃ": "d̠ʒ", "θ": "ð", "x": "ɣ"}
DEVOICING = {v: k for k, v in VOICING.items()}
SPIRANT = {"b": "β", "d": "ð", "ɡ": "ɣ"}
PALATAL = {"k": "t̠ʃ", "ɡ": "d̠ʒ", "t": "t̠ʃ", "s": "ʃ"}
RAISING = {"e": "i", "o": "u", "ɛ": "e", "ɔ": "o"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


# ═══════════════════════════════════════════════════════════════════════════
# Notação das regras
# ═══════════════════════════════════════════════════════════════════════════

Element = Tuple[str, object]  # ("seg", "k") | ("set", ["p","b"]) | ("class", "V") | ("bound", "#")


class Rule:
    """Uma regra 'alvo > substituição / ambiente', aplicada em paralelo na palavra."""

    def __init__(self, text: str, symbols: Sequence[str], source: str = "user", description: str = ""):
        self.text = text.strip()
        self.source = source
        self.description = description
        self.symbols = sorted({nfd(s) for s in symbols}, key=len, reverse=True)
        body, _, env = nfd(self.text).partition("/")
        if ">" not in body:
            raise ValueError(f"regra sem '>': {text}")
        tgt, _, rep = body.partition(">")
        self.target = self._element(tgt.strip(), allow_null=True)
        self.replacement = self._element(rep.strip(), allow_null=True)
        env = env.strip() or "_"
        if env.count("_") != 1:
            raise ValueError(f"o ambiente precisa de exatamente um '_': {text}")
        left, _, right = env.partition("_")
        self.left = self._sequence(left.strip())
        self.right = self._sequence(right.strip())
        if self.target[0] == "null" and self.replacement[0] == "null":
            raise ValueError(f"regra vazia: {text}")
        if self.target[0] == "set" and self.replacement[0] == "set" and \
                len(self.target[1]) != len(self.replacement[1]):
            raise ValueError(f"as duas listas precisam ter o mesmo tamanho: {text}")

    # ── leitura ──────────────────────────────────────────────────────────
    def _segs(self, text: str) -> List[str]:
        out, i = [], 0
        while i < len(text):
            if text[i] == " ":
                i += 1
                continue
            hit = next((x for x in self.symbols if text.startswith(x, i)), None)
            if hit is None:  # símbolo fora do inventário: um caractere-base com seus diacríticos
                j = i + 1
                while j < len(text) and unicodedata.category(text[j]) in ("Mn", "Lm"):
                    j += 1
                hit = text[i:j]
            out.append(hit)
            i += len(hit)
        return out

    def _element(self, text: str, allow_null: bool = False) -> Element:
        if allow_null and (text in NULL or text == ""):
            return ("null", None)
        if text.startswith("{") and text.endswith("}"):
            items = [nfd(x.strip()) for x in text[1:-1].split(",") if x.strip()]
            return ("set", items)
        if text in CLASS_PT:
            return ("class", text)
        segs = self._segs(text)
        if len(segs) != 1:
            raise ValueError(f"'{text}' deveria ser um único som, uma lista {{a,b}} ou uma classe (C, V...)")
        return ("seg", segs[0])

    def _sequence(self, text: str) -> List[Element]:
        out: List[Element] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == " ":
                i += 1
            elif ch == "#":
                out.append(("bound", "#"))
                i += 1
            elif ch == "{":
                j = text.index("}", i)
                out.append(self._element(text[i:j + 1]))
                i = j + 1
            elif ch in CLASS_PT:
                out.append(("class", ch))
                i += 1
            else:
                seg = self._segs(text[i:])[0]
                out.append(("seg", seg))
                i += len(seg)
        return out

    # ── aplicação ────────────────────────────────────────────────────────
    def apply(self, segs: List[str], classify) -> List[str]:
        n = len(segs)

        def match(el: Element, i: int) -> bool:
            kind, val = el
            if kind == "bound":
                return i == -1 or i == n
            if i < 0 or i >= n:
                return False
            s = segs[i]
            if kind == "seg":
                return s == val
            if kind == "set":
                return s in val
            return classify(s, val)

        def left_ok(i: int) -> bool:  # contexto que termina na posição i-1
            j = i - 1
            for el in reversed(self.left):
                if el[0] == "bound":
                    if j != -1:
                        return False
                    continue
                if not match(el, j):
                    return False
                j -= 1
            return True

        def right_ok(i: int) -> bool:  # contexto que começa na posição i
            j = i
            for el in self.right:
                if el[0] == "bound":
                    if j != n:
                        return False
                    continue
                if not match(el, j):
                    return False
                j += 1
            return True

        out: List[str] = []
        if self.target[0] == "null":  # inserção
            ins = self.replacement[1] if self.replacement[0] == "seg" else None
            for i in range(n + 1):
                if ins and left_ok(i) and right_ok(i):
                    out.append(ins)
                if i < n:
                    out.append(segs[i])
            return out
        for i, s in enumerate(segs):
            if match(self.target, i) and left_ok(i) and right_ok(i + 1):
                kind, val = self.replacement
                if kind == "null":
                    continue
                if kind == "set" and self.target[0] == "set":
                    out.append(val[self.target[1].index(s)])
                elif kind == "seg":
                    out.append(val)
                else:
                    out.append(s)
            else:
                out.append(s)
        return out


# ═══════════════════════════════════════════════════════════════════════════
# Aplicação à língua
# ═══════════════════════════════════════════════════════════════════════════

class SoundChanger:
    def __init__(self, language_dir: Path, seed: Optional[int] = None):
        d = language_dir
        self.dir = d
        self.inv = _load(d / "phonemic_inventory.json")
        self.lex = _load(d / "lexicon.json")
        if not (self.inv and self.lex):
            raise SystemExit(f"A pasta {d} precisa ter inventário e léxico (gere a língua com o orquestrador).")
        self.rules_ph = _load(d / "phonotactics.json")
        manifest = _load(d / "manifest.json")
        master = manifest["seed"] if manifest else None
        self.seed = seed if seed is not None else (derive_seed(master, "sound_changes") if master is not None else 0)
        self.rng = random.Random(self.seed)
        self.manner = {nfd(c["ipa"]): c["manner"] for c in self.inv["consonants"]}
        self.vowels = {nfd(v["ipa"]): v for v in self.inv["vowels"]}
        self.phonemes = set(self.manner) | set(self.vowels)
        self.symbols = sorted(self.phonemes | {nfd(x) for x in list(VOICING) + list(VOICING.values())
                                                + list(SPIRANT.values()) + list(PALATAL.values())},
                              key=len, reverse=True)
        o_spec, s_spec = _load(d / "orthography.json"), _load(d / "stress.json")
        self.o_spec = o_spec
        self.ortho = ortho_mod.Orthography(o_spec) if (ortho_mod and o_spec) else None
        self.stress = (stress_mod.Stress(s_spec, self.inv, self.rules_ph, derive_seed(master, "stress"))
                       if (stress_mod and s_spec and master is not None) else None)
        self.words = [e for e in self.lex["entries"] if e.get("citation") and "-" not in e["citation"]]

    # ── classes ──────────────────────────────────────────────────────────
    def is_vowel(self, s: str) -> bool:
        if s in self.vowels:
            return True
        if s in self.manner:
            return False
        base = "".join(ch for ch in nfd(s) if unicodedata.category(ch) not in ("Mn", "Lm"))
        return bool(base) and base[0] in VOWEL_LETTERS

    def classify(self, s: str, cls: str) -> bool:
        if cls == "V":
            return self.is_vowel(s)
        if cls == "C":
            return not self.is_vowel(s)
        m = self.manner.get(s)
        base = "".join(ch for ch in nfd(s) if unicodedata.category(ch) not in ("Mn", "Lm"))[:1]
        if cls == "P":
            return m in ("stop", "affricate") if m else base in STOPS
        if cls == "F":
            return m == "fricative" if m else base in FRICATIVES
        if cls == "N":
            return m == "nasal" if m else base in NASALS
        if cls == "L":
            return m in ("lateral", "rhotic") if m else base in LIQUIDS
        if cls == "G":
            return (m == "approximant" and s in GLIDES) if m else base in GLIDES
        return False

    # ── formas ───────────────────────────────────────────────────────────
    def split(self, form: str) -> Tuple[List[str], List[str]]:
        """Forma de citação → (fonemas, tons por sílaba)."""
        tones, segs = [], []
        for syl in nfd(form).split("."):
            tones.append("".join(ch for ch in syl if ch in TONE_LETTERS))
            s, i = "".join(ch for ch in syl if ch not in TONE_LETTERS + "ˈˌ"), 0
            while i < len(s):
                hit = next((x for x in self.symbols if s.startswith(x, i)), None)
                if hit is None:
                    j = i + 1
                    while j < len(s) and unicodedata.category(s[j]) in ("Mn", "Lm"):
                        j += 1
                    hit = s[i:j]
                segs.append(hit)
                i += len(hit)
        return segs, [t for t in tones if t] if any(tones) else []

    def syllables(self, segs: List[str]) -> List[List[str]]:
        """Silabificação simples (uma consoante entre vogais vai para a sílaba seguinte)."""
        nuclei = [i for i, s in enumerate(segs) if self.is_vowel(s)]
        if not nuclei:
            return [segs]
        sylls, start = [], 0
        for a, b in zip(nuclei, nuclei[1:]):
            cut = b - 1 if b - a > 1 else b
            sylls.append(segs[start:cut])
            start = cut
        sylls.append(segs[start:])
        return sylls

    def _join_simple(self, segs: List[str], tones: List[str]) -> str:
        """Fonemas → forma tonal; se o nº de sílabas mudou, a forma sai sem tons."""
        nuclei = [i for i, s in enumerate(segs) if self.is_vowel(s)]
        if len(nuclei) != len(tones):
            return nfc("".join(segs))
        bounds = []
        for a, b in zip(nuclei, nuclei[1:]):
            cluster = b - a - 1
            bounds.append(b - 1 if cluster >= 1 else b)  # uma consoante vai para a sílaba seguinte
        sylls, start = [], 0
        for cut in bounds:
            sylls.append(segs[start:cut])
            start = cut
        sylls.append(segs[start:])
        return nfc(".".join("".join(s) + tones[i] for i, s in enumerate(sylls)))

    def evolve(self, form: str, rules: List[Rule], stages: Optional[Dict[int, Tuple[str, str]]] = None
               ) -> Tuple[str, List[int]]:
        """Aplica as regras em ordem. Em `stages`, guarda o antes/depois de cada regra que agiu."""
        segs, tones = self.split(form)
        applied = []
        for k, r in enumerate(rules):
            new = r.apply(segs, self.classify)
            if new != segs:
                applied.append(k)
                if stages is not None:
                    stages[k] = (nfc("".join(segs)), nfc("".join(new)))
                segs = new
        return (self._join_simple(segs, tones) if tones else nfc("".join(segs))), applied

    # ── mudanças naturais ────────────────────────────────────────────────
    def natural_rules(self, max_rules: int = 4) -> List[Rule]:
        """Sorteia mudanças comuns nas línguas do mundo que de fato afetem o léxico."""
        ph = self.phonemes
        vow = sorted(v for v in self.vowels)
        front = sorted(v for v, e in self.vowels.items() if e["backness"] == "front")
        cands: List[Tuple[str, str, float]] = []

        def setstr(xs):
            return xs[0] if len(xs) == 1 else "{" + ",".join(xs) + "}"
        vl = [k for k in ("p", "t", "k", "q") if nfd(k) in ph and VOICING[k] != k]
        if vl:
            cands.append((f"{setstr(vl)} > {setstr([VOICING[k] for k in vl])} / V_V",
                          "sonorização entre vogais (como no espanhol: lupus → lobo)", 1.0))
        vd = [k for k in ("b", "d", "ɡ") if nfd(k) in ph]
        if vd:
            cands.append((f"{setstr(vd)} > {setstr([SPIRANT[k] for k in vd])} / V_V",
                          "espirantização entre vogais (como no espanhol: lado [laðo])", 0.8))
        fd = [k for k in DEVOICING if nfd(k) in ph and k in ("b", "d", "ɡ", "v", "z", "ʒ", "d̠ʒ")]
        if fd:
            cands.append((f"{setstr(fd)} > {setstr([DEVOICING[k] for k in fd])} / _#",
                          "ensurdecimento final (como no alemão: Hund [hʊnt])", 0.9))
        pal = [k for k in ("k", "ɡ") if nfd(k) in ph]
        if pal and front:
            cands.append((f"{setstr(pal)} > {setstr([PALATAL[k] for k in pal])} / _{setstr(front)}",
                          "palatalização antes de vogal anterior (como no italiano: cento [t̠ʃɛnto])", 0.9))
        if "n" in ph:
            for tgt, env, desc in (("m", "{p,b}", "n > m antes de labial"), ("ŋ", "{k,ɡ}", "n > ŋ antes de velar")):
                env_items = [x for x in env[1:-1].split(",") if nfd(x) in ph]
                if env_items:
                    cands.append((f"n > {tgt} / _{setstr(env_items)}", f"assimilação nasal ({desc})", 0.7))
        if "h" in ph:
            cands.append(("h > ∅ / V_V", "queda de h entre vogais", 0.6))
        if "s" in ph:
            cands.append(("s > h / V_V", "debucalização (como no espanhol caribenho: mismo [mihmo])", 0.4))
        for v, w in RAISING.items():
            if v in ph and w in ph and v in ("e", "o"):
                cands.append((f"{v} > {w} / _#", f"elevação de vogal final ({v} > {w}, como no português: leite [lejt͡ʃi])", 0.5))
        if len(vow) >= 3:
            cands.append(("V > ∅ / VC_#", "queda da vogal final depois de sílaba aberta (apócope)", 0.3))

        chosen: List[Rule] = []
        pool = list(cands)
        self.rng.shuffle(pool)
        pool.sort(key=lambda x: -x[2] * self.rng.random())
        for text, desc, _ in pool:
            if len(chosen) >= max_rules:
                break
            try:
                r = Rule(text, self.symbols, "natural", desc)
            except ValueError:
                continue
            changed = sum(1 for e in self.words if self.evolve(e["citation"], chosen + [r])[0]
                          != self.evolve(e["citation"], chosen)[0])
            if changed >= 3:  # só entra se mudar pelo menos três palavras
                chosen.append(r)
        n = self.rng.randint(2, max_rules)
        return chosen[:n]

    # ── grafia dos sons novos ────────────────────────────────────────────
    def extended_orthography(self, new_sounds: Sequence[str]):
        if not (self.ortho and ortho_mod):
            return None, {}
        spec = json.loads(json.dumps(self.o_spec))
        taken = set(spec["graphemes"].values())
        added = {}
        for s in new_sounds:
            cands, _ = ortho_mod.candidates(s, spec["style"], self.is_vowel(s))
            g = next((c for c in cands if c not in taken), s)
            spec["graphemes"][s] = g
            if self.is_vowel(s):
                spec["vowels"].append(s)
            taken.add(g)
            added[s] = g
        return ortho_mod.Orthography(spec), added

    # ── execução ─────────────────────────────────────────────────────────
    def run(self, user_rules: Sequence[str], natural: bool = True, reflect_spelling: bool = False) -> Dict:
        rules: List[Rule] = []
        errors = []
        if natural:
            rules += self.natural_rules()
        for text in user_rules:
            if not text.strip() or text.strip().startswith("#"):
                continue
            try:
                rules.append(Rule(text, self.symbols, "user", "regra do usuário"))
            except ValueError as ex:
                errors.append(str(ex))
        warnings = []

        entries, examples = [], {k: [] for k in range(len(rules))}
        changed_n = 0
        for e in self.words:
            stages: Dict[int, Tuple[str, str]] = {}
            new, applied = self.evolve(e["citation"], rules, stages)
            entries.append({"gloss": e["gloss"], "label": e.get("label") or e["english"].split(" (")[0],
                            "pos": e["pos"], "underlying": e["citation"], "changed": new, "rules": applied})
            if applied:
                changed_n += 1
                for k in applied:  # o exemplo mostra o efeito desta regra, não o resultado final
                    if len(examples[k]) < 4:
                        before, after = stages[k]
                        examples[k].append({"before": before, "after": after, "word": e["citation"],
                                            "label": entries[-1]["label"]})

        extra = {}
        for key, file in (("derived", "derivation.json"), ("names", "names.json")):
            data = _load(self.dir / file)
            if not data:
                continue
            items = []
            if key == "derived":
                forms = [(d["ipa"], d["meaning"]) for d in data["derived"] if " " not in d["ipa"]]
            else:
                forms = [(p["given"]["ipa"], "given name") for p in data["people"]] + \
                        [(p["ipa"], p.get("meaning") or "place") for p in data["places"] if " " not in p["ipa"]]
            for ipa, label in forms:
                new, applied = self.evolve(ipa, rules)
                items.append({"underlying": ipa, "changed": new, "label": label, "rules": applied})
            extra[key] = items

        all_forms = [x["changed"] for x in entries] + [x["changed"] for v in extra.values() for x in v]
        new_sounds = sorted({s for f in all_forms for s in self.split(f)[0] if s not in self.phonemes and s.strip()})
        ortho2, added = self.extended_orthography(new_sounds) if reflect_spelling else (None, {})

        def spell(ipa: str, changed: bool) -> str:
            o = ortho2 if (changed and ortho2) else self.ortho
            return o.spell(ipa) if o else ipa

        def pron(ipa: str, base: Optional[str] = None) -> str:
            """Pronúncia com acento. O acento é calculado na forma antiga e mantido na mesma
            sílaba depois das mudanças, como acontece historicamente."""
            if not self.stress:
                return ipa
            base = base or ipa
            b_sylls = self.stress.syllabify(base)
            p = self.stress.primary(b_sylls, base)
            segs, tones = self.split(ipa)
            sylls = self.syllables(segs)
            if p is None or len(sylls) < 2:
                return ipa
            if len(sylls) != len(b_sylls):  # sílaba perdida: o acento recalcula na forma nova
                if any(s not in self.phonemes and self.is_vowel(s) for s in segs):
                    return ipa
                return self.stress.mark(ipa)
            sec = set(self.stress.secondaries(len(sylls), p))
            out = []
            for i, syl in enumerate(sylls):
                mark = "ˈ" if i == p else "ˌ" if i in sec else ""
                out.append(mark + "".join(syl) + (tones[i] if i < len(tones) else ""))
            return nfc("".join(out))

        for x in entries + [x for v in extra.values() for x in v]:
            x["written"] = spell(x["underlying"], False)
            x["changed_written"] = spell(x["changed"], True) if reflect_spelling else x["written"]
            x["phonetic"] = pron(x["changed"], x["underlying"])

        for k, r in enumerate(rules):
            if not any(k in x["rules"] for x in entries):
                warnings.append(f"'{nfc(r.text)}' não mudou nenhuma palavra (os sons existem na língua? "
                                "as regras usam IPA, não a grafia)")
        return {
            "rules": [{"text": nfc(r.text), "source": r.source, "description": r.description,
                       "changed_words": sum(1 for x in entries if k in x["rules"]),
                       "examples": [{**ex, "before_written": spell(ex["before"], False),
                                     "after_phonetic": pron(ex["after"], ex["word"])} for ex in examples[k]]}
                      for k, r in enumerate(rules)],
            "entries": entries, **extra,
            "new_sounds": new_sounds, "new_graphemes": added,
            "settings": {"natural": natural, "reflect_spelling": reflect_spelling},
            "metadata": {"seed": self.seed, "changed_words": changed_n, "total_words": len(entries),
                         "errors": errors, "warnings": warnings},
        }


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

def write_markdown(path: Path, data: Dict) -> None:
    m = data["metadata"]
    lines = ["# Mudanças sonoras", "",
             f"{len(data['rules'])} regras, aplicadas em ordem; {m['changed_words']} de {m['total_words']} "
             "palavras mudaram. A forma do dicionário fica entre barras /.../, e a pronúncia depois das "
             "mudanças, entre colchetes [...].", ""]
    if data["settings"]["reflect_spelling"]:
        lines += ["A grafia segue a pronúncia nova."
                  + (" Sons novos: " + ", ".join(f"[{s}] = {g}" for s, g in data["new_graphemes"].items())
                     if data["new_graphemes"] else ""), ""]
    elif data["new_sounds"]:
        lines += ["Sons novos criados pelas mudanças: " + " ".join(f"[{s}]" for s in data["new_sounds"]), ""]
    lines += ["| # | Regra | Origem | Palavras afetadas | Exemplo |", "|---|---|---|---|---|"]
    for i, r in enumerate(data["rules"], 1):
        ex = r["examples"][0] if r["examples"] else None
        sample = f"*{ex['before_written']}* /{ex['before']}/ → [{ex['after_phonetic']}] '{ex['label']}'" if ex else "—"
        origin = "natural" if r["source"] == "natural" else "usuário"
        lines.append(f"| {i} | `{r['text']}` | {origin} | {r['changed_words']} | {sample} |")
        if r["description"] and r["source"] == "natural":
            lines.append(f"| | {r['description']} | | | |")
    for e in data["metadata"]["errors"]:
        lines += ["", f"Regra ignorada: {e}"]
    for w in data["metadata"].get("warnings", []):
        lines += ["", f"Aviso: {w}"]
    changed = [x for x in data["entries"] if x["rules"]]
    if changed:
        lines += ["", "## Palavras que mudaram", "", "Formato: **grafia** /forma do dicionário/ [pronúncia] 'significado'", ""]
        for x in sorted(changed, key=lambda x: nfd(x["changed_written"]).lower()):
            lines.append(f"- **{x['changed_written']}** /{x['underlying']}/ [{x['phonetic']}] '{x['label']}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Aplica mudanças sonoras às palavras da conlang.")
    ap.add_argument("--language", type=Path, required=True, help="pasta de uma língua (languages/lang-31)")
    ap.add_argument("--rule", action="append", default=[], help="regra do usuário (pode repetir)")
    ap.add_argument("--rules-file", type=Path, help="arquivo com uma regra por linha")
    ap.add_argument("--no-natural", action="store_true", help="não sorteia mudanças naturais")
    ap.add_argument("--reflect-spelling", action="store_true", help="a grafia segue a pronúncia nova")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    args = ap.parse_args()

    user = list(args.rule)
    if args.rules_file:
        user += args.rules_file.read_text(encoding="utf-8").splitlines()
    sc = SoundChanger(args.language, args.seed)
    data = sc.run(user, natural=not args.no_natural, reflect_spelling=args.reflect_spelling)
    (args.language / "sound_changes.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.language / "sound_changes.md", data)

    m = data["metadata"]
    print(f"\nMUDANÇAS SONORAS — {len(data['rules'])} regras; {m['changed_words']} de {m['total_words']} palavras mudaram")
    for i, r in enumerate(data["rules"], 1):
        origin = "natural" if r["source"] == "natural" else "usuário"
        print(f"  {i}. {r['text']:<28} ({origin}, {r['changed_words']} palavras)")
        if r["source"] == "natural":
            print(f"     {r['description']}")
        for ex in r["examples"][:2]:
            print(f"       {ex['before_written']:<14} /{ex['before']}/ → [{ex['after_phonetic']}]  '{ex['label']}'")
    if data["new_sounds"]:
        print("  Sons novos: " + " ".join(f"[{s}]" for s in data["new_sounds"]))
    for e in m["errors"]:
        print(f"  [!] Regra ignorada: {e}")
    for w in m.get("warnings", []):
        print(f"  [!] {w}")
    print(f"\n[OK] Mudanças salvas em '{args.language / 'sound_changes.json'}' e 'sound_changes.md'.")


if __name__ == "__main__":
    main()
