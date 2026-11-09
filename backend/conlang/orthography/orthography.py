"""
Módulo — Ortografia (romanização prática).

Cria uma grafia para a conlang a partir do inventário fonêmico: escolhe uma
letra (ou dígrafo) para cada fonema, num estilo coerente, garante que a escrita
possa ser lida de volta sem ambiguidade e marca os tons com diacríticos.

    t̠ʃupaŋ → chupang (estilo inglês) · čupaŋ (diacríticos) · cupaq (econômico)

Não altera nenhum outro módulo: só lê os JSONs que eles produzem.

Uso com uma língua gerada pelo orquestrador (lê e grava na pasta da língua):
    python orthography/orthography.py --language languages/lang-31
    python orthography/orthography.py --language languages/lang-31 --style diacritics

Uso isolado, como os demais módulos:
    python orthography/orthography.py --inventory phonemic_inventory/phonemic_inventory.json

Requer apenas a biblioteca padrão (Python ≥ 3.9).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_INVENTORY = ROOT / "phonemic_inventory" / "phonemic_inventory.json"
DEFAULT_OUTPUT = HERE / "orthography.json"

STYLES = ["english", "diacritics", "economic", "romance"]
STYLE_PT = {"english": "inglês (dígrafos: sh, ch, ng)",
            "diacritics": "diacríticos (š, č, ŋ, vogais longas com mácron)",
            "economic": "econômico (letras reaproveitadas: x, c, q)",
            "romance": "românico (nh, lh, ch, til nas nasais)"}

TONE_LETTERS = "˥˦˧˨˩"
TONE_LEVEL = {"˥": 5, "˦": 4, "˧": 3, "˨": 2, "˩": 1}
SEPARATOR = "·"

# Combinantes (Unicode NFD)
ACUTE, GRAVE, MACRON, CIRCUMFLEX, CARON = "\u0301", "\u0300", "\u0304", "\u0302", "\u030C"
DOUBLE_ACUTE, DOUBLE_GRAVE, BREVE, INV_BREVE = "\u030B", "\u030F", "\u0306", "\u0311"
TILDE, DOT_BELOW, MACRON_BELOW, RING_BELOW = "\u0303", "\u0323", "\u0331", "\u0325"

# ═══════════════════════════════════════════════════════════════════════════
# Letras-base por estilo: símbolo IPA (sem diacríticos) → candidatos, em ordem
# de preferência. Fonemas mais frequentes escolhem primeiro; se um candidato já
# estiver ocupado, o próximo é usado.
# ═══════════════════════════════════════════════════════════════════════════

COMMON = {c: [c] for c in "pbtdkmnfvszlrwhaeiouq"}
COMMON.update({"ɡ": ["g"], "ɾ": ["r"], "ɹ": ["r"], "ʀ": ["r"], "ɻ": ["r", "rr"], "ɽ": ["r", "rr"],
               "ʋ": ["v", "w"], "ɱ": ["m"], "ɖ": ["d"], "ʈ": ["t"], "ɳ": ["n"], "ɭ": ["l"],
               "ɺ": ["l", "r"], "ɦ": ["h"], "ɐ": ["a"], "ɰ": ["w"], "ʍ": ["wh", "hw"],
               "ɥ": ["yw", "w"], "ȵ": ["ny", "ñ"], "ȶ": ["ty", "c"], "ȴ": ["ly", "ľ"]})

STYLE_TABLES: Dict[str, Dict[str, List[str]]] = {
    "english": {
        "ʃ": ["sh"], "ʒ": ["zh"], "tʃ": ["ch"], "dʒ": ["j"], "ts": ["ts", "tz"], "dz": ["dz"],
        "θ": ["th"], "ð": ["dh"], "ŋ": ["ng"], "ɲ": ["ny"], "ʎ": ["ly"], "x": ["kh"], "ɣ": ["gh"],
        "χ": ["qh", "kh"], "ʁ": ["rh", "gh"], "ħ": ["hh", "ḥ"], "ʕ": ["ʿ"], "ʔ": ["'"], "j": ["y"],
        "ç": ["hy"], "ʝ": ["y", "yh"], "β": ["bh", "v"], "ɸ": ["f", "ph"], "c": ["ky", "c"],
        "ɟ": ["gy"], "ɕ": ["sy", "sh"], "ʑ": ["zy", "zh"], "ʂ": ["sh", "rs"], "ʐ": ["zh", "rz"],
        "ɬ": ["lh", "hl"], "ɮ": ["lz"], "ɓ": ["b'", "bb"], "ɗ": ["d'", "dd"], "ʄ": ["j'"],
        "ɠ": ["g'"], "kp": ["kp"], "ɡb": ["gb"], "ŋm": ["ngm"], "cç": ["ky"],
        "ɛ": ["è", "e"], "ɔ": ["ò", "o"], "ə": ["ë"], "ɨ": ["ï"], "ʉ": ["ü"], "y": ["ü"],
        "ø": ["ö"], "œ": ["œ"], "æ": ["æ"], "ɑ": ["a", "â"], "ɒ": ["å"], "ʌ": ["ŭ"],
        "ɯ": ["ı"], "ɤ": ["ë", "ə"], "ɪ": ["i", "ì"], "ʊ": ["u", "ù"], "ɵ": ["ö"], "ɘ": ["ë"],
    },
    "diacritics": {
        "ʃ": ["š"], "ʒ": ["ž"], "tʃ": ["č"], "dʒ": ["dž", "ǧ"], "ts": ["c"], "dz": ["dz", "ʒ"],
        "θ": ["þ"], "ð": ["đ"], "ŋ": ["ŋ"], "ɲ": ["ň", "ñ"], "ʎ": ["ľ"], "x": ["x", "ch"],
        "ɣ": ["ğ"], "χ": ["ẋ"], "ʁ": ["ř"], "ħ": ["ḥ"], "ʕ": ["ʿ"], "ʔ": ["'"], "j": ["j"],
        "ç": ["ç"], "ʝ": ["ĵ"], "β": ["ƀ"], "ɸ": ["ƒ"], "c": ["ť", "ć"], "ɟ": ["ď", "đ"],
        "ɕ": ["ś"], "ʑ": ["ź"], "ʂ": ["ṣ"], "ʐ": ["ẓ"], "ɬ": ["ł"], "ɮ": ["ɮ"], "ɓ": ["ɓ"],
        "ɗ": ["ɗ"], "ʄ": ["ʄ"], "ɠ": ["ɠ"], "kp": ["kp"], "ɡb": ["gb"], "ŋm": ["ŋm"], "cç": ["ć"],
        "ɛ": ["ė", "è"], "ɔ": ["ȯ", "ò"], "ə": ["ë"], "ɨ": ["y", "ï"], "ʉ": ["ü"], "y": ["ü"],
        "ø": ["ö"], "œ": ["œ"], "æ": ["ä"], "ɑ": ["a", "å"], "ɒ": ["å"], "ʌ": ["ŭ"],
        "ɯ": ["ı"], "ɤ": ["ë"], "ɪ": ["i", "ĭ"], "ʊ": ["u", "ŭ"], "ɵ": ["ö"], "ɘ": ["ë"],
    },
    "economic": {
        "ʃ": ["x", "sh"], "ʒ": ["j", "zh"], "tʃ": ["c", "ch"], "dʒ": ["j", "dj"], "ts": ["z", "ts"],
        "dz": ["dz"], "θ": ["c", "th"], "ð": ["dh"], "ŋ": ["q", "ng"], "ɲ": ["ny"], "ʎ": ["ly"],
        "x": ["h", "kh"], "ɣ": ["gh"], "χ": ["kh"], "ʁ": ["gh"], "ħ": ["hh"], "ʕ": ["'"],
        "ʔ": ["q", "'"], "j": ["y"], "ç": ["hy"], "ʝ": ["y"], "β": ["v", "bh"], "ɸ": ["f"],
        "c": ["c", "ky"], "ɟ": ["j", "gy"], "ɕ": ["x", "sy"], "ʑ": ["j", "zy"], "ʂ": ["x", "sh"],
        "ʐ": ["j", "zh"], "ɬ": ["lh"], "ɮ": ["lz"], "ɓ": ["b"], "ɗ": ["d"], "ʄ": ["j"],
        "ɠ": ["g"], "kp": ["kp"], "ɡb": ["gb"], "ŋm": ["ngm"], "cç": ["c"],
        "ɛ": ["e", "è"], "ɔ": ["o", "ò"], "ə": ["e", "ë"], "ɨ": ["i", "ï"], "ʉ": ["u", "ü"],
        "y": ["u", "ü"], "ø": ["o", "ö"], "œ": ["ö"], "æ": ["a", "ä"], "ɑ": ["a", "â"],
        "ɒ": ["o", "å"], "ʌ": ["a", "ŭ"], "ɯ": ["u", "ı"], "ɤ": ["e", "ë"], "ɪ": ["i", "ì"],
        "ʊ": ["u", "ù"], "ɵ": ["o", "ö"], "ɘ": ["e", "ë"],
    },
    "romance": {
        "ʃ": ["x", "ch"], "ʒ": ["j", "zh"], "tʃ": ["ch", "tx"], "dʒ": ["dj", "gi"], "ts": ["ts", "ç"],
        "dz": ["dz"], "θ": ["z", "th"], "ð": ["dh"], "ŋ": ["ng"], "ɲ": ["nh", "ñ"], "ʎ": ["lh", "ll"],
        "x": ["j", "kh"], "ɣ": ["gh"], "χ": ["jh"], "ʁ": ["rh"], "ħ": ["hh"], "ʕ": ["'"],
        "ʔ": ["'"], "j": ["i", "y"], "ç": ["hi"], "ʝ": ["y"], "β": ["b", "bh"], "ɸ": ["f"],
        "c": ["qu", "ky"], "ɟ": ["gu", "gy"], "ɕ": ["xi"], "ʑ": ["zi"], "ʂ": ["x", "rs"],
        "ʐ": ["rz"], "ɬ": ["lh", "hl"], "ɮ": ["lz"], "ɓ": ["b'"], "ɗ": ["d'"], "ʄ": ["dj'"],
        "ɠ": ["g'"], "kp": ["kp"], "ɡb": ["gb"], "ŋm": ["ngm"], "cç": ["qu"],
        "ɛ": ["é", "è"], "ɔ": ["ó", "ò"], "ə": ["ë"], "ɨ": ["ï"], "ʉ": ["ü"], "y": ["ü"],
        "ø": ["ö"], "œ": ["œ"], "æ": ["ä"], "ɑ": ["a", "â"], "ɒ": ["ò"], "ʌ": ["ã", "ŭ"],
        "ɯ": ["ü"], "ɤ": ["ë"], "ɪ": ["i", "ì"], "ʊ": ["u", "ù"], "ɵ": ["ö"], "ɘ": ["ë"],
    },
}

# Modificadores que alteram a grafia; os demais diacríticos (dental, apical...) são ignorados
MODIFIERS = {"ʰ": "aspirated", "ʷ": "labialized", "ʲ": "palatalized", "ˠ": "velarized",
             "ˤ": "pharyngealized", "ː": "long", "\u0303": "nasal", "ʼ": "ejective",
             "ˀ": "glottalized", "\u0325": "voiceless", "\u030A": "voiceless",
             "\u0324": "breathy", "\u0330": "creaky", "ⁿ": "prenasal", "ᵐ": "prenasal",
             "ᵑ": "prenasal"}
IGNORED_MARKS = {"\u0320", "\u031F", "\u031E", "\u031D", "\u032A", "\u033A", "\u033B",
                 "\u0339", "\u031C", "\u032F", "\u0329", "\u0361", "\u035C", "\u0348", "\u0349"}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def derive_seed(master: int, step: str) -> int:
    """Mesma derivação do orquestrador: semente própria da etapa."""
    return int(hashlib.sha256(f"{master}:{step}".encode()).hexdigest()[:8], 16)


# ═══════════════════════════════════════════════════════════════════════════
# Construção da ortografia
# ═══════════════════════════════════════════════════════════════════════════

def decompose(ipa: str) -> Tuple[str, List[str]]:
    """Separa o fonema em base e modificadores: 'kʷʰ' → ('k', ['labialized', 'aspirated'])."""
    base, mods = "", []
    for ch in nfd(ipa):
        if ch in MODIFIERS:
            mods.append(MODIFIERS[ch])
        elif ch in IGNORED_MARKS:
            continue
        elif unicodedata.category(ch) == "Mn":
            continue
        else:
            base += ch
    return base, mods


def base_candidates(base: str, style: str) -> List[str]:
    table = STYLE_TABLES[style]
    if base in table:
        return list(table[base])
    if base in COMMON:
        return list(COMMON[base])
    if len(base) > 1:  # combinação (pré-nasalizadas, africadas raras): letra a letra
        parts = [base_candidates(ch, style)[0] for ch in base]
        return ["".join(parts)]
    return [base]  # sem correspondência: mantém o símbolo IPA


def apply_modifiers(letters: str, mods: Sequence[str], style: str, is_vowel: bool) -> str:
    out = letters
    for m in mods:
        if m == "aspirated":
            out += "h"
        elif m == "labialized":
            out += "w"
        elif m == "palatalized":
            out += "j" if style == "diacritics" else "y"
        elif m in ("velarized", "pharyngealized"):
            out = out[0] + DOT_BELOW + out[1:]
        elif m == "long":
            if is_vowel and style == "diacritics":
                out = out[0] + MACRON + out[1:]
            else:
                out = out[0] + out
        elif m == "nasal":
            out = out[0] + TILDE + out[1:]
        elif m in ("ejective", "glottalized"):
            out += "ʼ"
        elif m == "voiceless":
            out = ("h" + out) if style in ("english", "economic") else out[0] + RING_BELOW + out[1:]
        elif m == "breathy":
            out += "h"
        elif m == "creaky":
            out = out[0] + "\u0330" + out[1:]
        elif m == "prenasal":
            out = ("m" if out[:1] in "pb" else "ng" if out[:1] in "kg" else "n") + out
    return nfc(out)


def candidates(ipa: str, style: str, is_vowel: bool) -> Tuple[List[str], int]:
    """Grafias possíveis, em ordem; devolve também quantas são do próprio estilo."""
    base, mods = decompose(ipa)
    cands = list(dict.fromkeys(apply_modifiers(b, mods, style, is_vowel)
                               for b in base_candidates(base, style)))
    n_style = len(cands)
    first = base_candidates(base, style)[0]
    # alternativas genéricas para resolver colisões: ponto e traço sob a letra
    for mark in (DOT_BELOW, MACRON_BELOW):
        cands.append(apply_modifiers(first[0] + mark + first[1:], mods, style, is_vowel))
    cands.append(nfc(ipa))
    return list(dict.fromkeys(cands)), n_style


class Orthography:
    """Grafia de uma língua: fonema → letras, tom → diacrítico, e a função spell()."""

    def __init__(self, spec: Dict):
        self.spec = spec
        self.graphemes: Dict[str, str] = spec["graphemes"]
        self.tones: Dict[str, str] = spec.get("tones", {})
        self.vowels: Set[str] = set(spec["vowels"])
        self.symbols = sorted(self.graphemes, key=lambda x: len(nfd(x)), reverse=True)
        self.decoder = sorted(((nfd(v), k) for k, v in self.graphemes.items()),
                              key=lambda x: len(x[0]), reverse=True)
        self.tone_marks = {ch for m in self.tones.values() for ch in nfd(m)}

    # ── segmentação ──────────────────────────────────────────────────────
    def tokenize(self, ipa: str) -> List[str]:
        s, out, i = nfd(ipa), [], 0
        while i < len(s):
            hit = next((x for x in self.symbols if s.startswith(nfd(x), i)), None)
            if hit is None:
                out.append(s[i])  # símbolo fora do inventário: passa adiante
                i += 1
            else:
                out.append(hit)
                i += len(nfd(hit))
        return out

    def decode(self, written: str) -> List[str]:
        """Grafia → fonemas, pela grafia mais longa que casa (o separador é ignorado)."""
        raw = "".join(ch for ch in nfd(written) if ch not in self.tone_marks)  # tons não são fonemas
        out, i = [], 0
        while i < len(raw):
            if raw[i] == SEPARATOR:
                i += 1
                continue
            hit = next(((w, p) for w, p in self.decoder if raw.startswith(w, i)), None)
            if hit is None:
                out.append(raw[i])
                i += 1
            else:
                out.append(hit[1])
                i += len(hit[0])
        return out

    # ── escrita ──────────────────────────────────────────────────────────
    def _spell_segments(self, segs: List[str]) -> str:
        parts = [self.graphemes.get(s, s) for s in segs]
        written = ""
        for k, p in enumerate(parts):  # separador onde a leitura ficaria ambígua
            if k and self.decode(written + p) != segs[:k + 1]:
                written += SEPARATOR
            written += p
        return written

    def _spell_syllable(self, syl: str) -> str:
        tone = "".join(ch for ch in syl if ch in TONE_LETTERS)
        body = "".join(ch for ch in syl if ch not in TONE_LETTERS)
        segs = self.tokenize(body)
        written = self._spell_segments(segs)
        mark = self.tones.get(tone, "") if tone else ""
        if mark:
            idx = next((i for i, s in enumerate(segs) if s in self.vowels), None)
            if idx is not None:
                pos = len(nfd(self._spell_segments(segs[:idx])))
                w = nfd(written)
                written = w[:pos + 1] + mark + w[pos + 1:]
        return written

    def spell_segments(self, segments: Sequence[str]) -> str:
        """Lista de fonemas → grafia. Mais exato que spell(), que precisa segmentar a string."""
        return nfc(self._spell_segments(list(segments)))

    def spell(self, ipa: str) -> str:
        """IPA → grafia. Aceita 'ma˥.ku˩' (tons), 'makun' e esqueletos 'k-t-b'."""
        if not ipa:
            return ""
        if "-" in ipa:
            return "-".join(self.spell(p) for p in ipa.split("-"))
        words = ipa.split(" ")
        out = []
        for w in words:
            if any(ch in TONE_LETTERS for ch in w):
                written, segs = "", []
                for syl in w.split("."):  # separador também entre sílabas (a˦.a˦ ≠ aː)
                    part = self._spell_syllable(syl)
                    syl_segs = self.tokenize("".join(ch for ch in syl if ch not in TONE_LETTERS))
                    if written and self.decode(written + part) != segs + syl_segs:
                        written += SEPARATOR
                    written += part
                    segs += syl_segs
                out.append(written)
            else:
                # pontos de sílaba, quando existem, delimitam a segmentação (d.z ≠ dz)
                segs = [t for syl in w.split(".") for t in self.tokenize(syl)]
                out.append(self._spell_segments(segs))
        return nfc(" ".join(out))


TONE_FALLBACKS = [MACRON, BREVE, INV_BREVE, "\u030D", "\u0307", "\u0308", "\u0310"]


def _tone_marks(tones: List[str], rng: random.Random, forbidden: Set[str] = frozenset()) -> Dict[str, str]:
    """
    Tons → diacríticos: agudo (alto), grave (baixo), circunflexo (descendente),
    caron (ascendente). Marcas já usadas em alguma letra (o grave de 'è', o caron
    de 'š', o mácron de 'ā') ficam proibidas, para que tom e letra nunca se confundam.
    """
    if not tones:
        return {}
    levels = {t: [TONE_LEVEL[c] for c in t if c in TONE_LEVEL] for t in tones}
    level_tones = [t for t in tones if len(levels[t]) == 1]
    has5, has4 = any(levels[t] == [5] for t in level_tones), any(levels[t] == [4] for t in level_tones)
    has2, has1 = any(levels[t] == [2] for t in level_tones), any(levels[t] == [1] for t in level_tones)
    unmarked = next((t for t in level_tones if levels[t] == [3]), None)
    marks: Dict[str, str] = {}
    used: Set[str] = set()
    for t in sorted(tones, key=lambda x: (len(levels[x]), x)):
        lv = levels[t]
        if t == unmarked:
            marks[t] = ""
            continue
        if len(lv) == 1:
            v = lv[0]
            options = ([DOUBLE_ACUTE, ACUTE] if v == 5 and has4 else [ACUTE] if v >= 4 else
                       [DOUBLE_GRAVE, GRAVE] if v == 1 and has2 else [GRAVE] if v <= 2 else [MACRON])
        elif len(lv) == 2:
            options = [CIRCUMFLEX, INV_BREVE] if lv[0] > lv[1] else [CARON, BREVE]
        else:
            options = [BREVE, INV_BREVE]
        options += TONE_FALLBACKS
        mark = next((m for m in options if m not in used and m not in forbidden), "")
        marks[t] = mark
        used.add(mark)
    return marks


def can_follow(a: str, b: str, rules: Optional[Dict], vowels: Set[str]) -> bool:
    """Os fonemas a e b podem aparecer em sequência? (Sem regras, assume que sim.)"""
    if not rules:
        return True
    av, bv = a in vowels, b in vowels
    if av and bv:
        return bool(rules.get("allow_hiatus"))
    if av or bv:
        return True
    codas = set(rules["codas"]["single"])
    onset2 = {tuple(c) for c in rules["onsets"]["clusters"]}
    coda2 = {tuple(c) for c in rules["codas"]["clusters"]}
    return a in codas or (a, b) in onset2 or (a, b) in coda2


def build(inventory: Dict, *, style: Optional[str] = None, seed: Optional[int] = None,
          rules: Optional[Dict] = None) -> Dict:
    """Sorteia (ou usa) um estilo e atribui uma grafia única a cada fonema."""
    rng = random.Random(seed)
    if style is None:
        style = rng.choices(STYLES, [0.35, 0.25, 0.2, 0.2])[0]
    cons = [c["ipa"] for c in inventory["consonants"]]
    vows = [v["ipa"] for v in inventory["vowels"]]
    freq = {x["ipa"]: x.get("frequency", 0) for x in inventory["consonants"] + inventory["vowels"]}
    vset = set(vows)
    order = sorted(cons + vows, key=lambda p: (-freq[p], p))  # o mais comum escolhe primeiro

    built = {p: candidates(p, style, p in vset) for p in order}
    cands = {p: built[p][0] for p in order}
    n_style = {p: built[p][1] for p in order}
    choice = {p: 0 for p in order}
    notes: List[str] = []

    def assign() -> Dict[str, str]:
        g, taken = {}, set()
        for p in order:
            while choice[p] < len(cands[p]) - 1 and cands[p][choice[p]] in taken:
                choice[p] += 1
            g[p] = cands[p][choice[p]]
            taken.add(g[p])
        return g

    graphemes = assign()
    # Ambiguidade: se a+b escritos juntos forem lidos como outro fonema (s+h = sh),
    # o fonema do dígrafo passa para a próxima grafia possível.
    for _ in range(40):
        ortho = Orthography({"graphemes": graphemes, "vowels": vows})
        conflict = None
        for a in order:
            for b in order:
                if not can_follow(a, b, rules, vset):
                    continue
                read = ortho.decode(graphemes[a] + graphemes[b])
                if read != [a, b]:
                    culprit = next((p for p in read if p not in (a, b) and len(nfd(graphemes[p])) > 1), None)
                    # só troca por outra grafia do mesmo estilo; senão, fica o separador
                    if culprit and choice[culprit] + 1 < n_style[culprit]:
                        conflict = culprit
                        break
            if conflict:
                break
        if not conflict:
            break
        old = graphemes[conflict]
        choice[conflict] += 1
        graphemes = assign()
        notes.append(f"/{conflict}/: '{old}' seria ambíguo; usando '{graphemes[conflict]}'")

    ortho = Orthography({"graphemes": graphemes, "vowels": vows})
    separator_pairs = [[a, b] for a in order for b in order
                       if can_follow(a, b, rules, vset) and ortho.decode(graphemes[a] + graphemes[b]) != [a, b]]
    letter_marks = {ch for g in graphemes.values() for ch in nfd(g) if unicodedata.category(ch) == "Mn"}
    tones = _tone_marks([t["ipa"] for t in inventory.get("tones", [])], rng, letter_marks)
    return {"style": style, "graphemes": graphemes, "vowels": vows, "tones": tones,
            "separator": SEPARATOR, "separator_pairs": separator_pairs,
            "metadata": {"seed": seed, "notes": notes,
                         "checked_with_phonotactics": rules is not None}}


# ═══════════════════════════════════════════════════════════════════════════
# Saídas
# ═══════════════════════════════════════════════════════════════════════════

POS_ABBR = {"noun": "n.", "verb": "v.", "adjective": "adj.", "pronoun": "pron.", "demonstrative": "dem.",
            "interrogative": "interr.", "quantifier": "quant.", "conjunction": "conj.", "adverb": "adv.",
            "adposition": "adp.", "numeral": "num.", "negation": "neg.", "article": "art.",
            "particle": "part.", "interjection": "interj."}
TONE_NAMES = {ACUTE: "agudo", GRAVE: "grave", MACRON: "mácron", CIRCUMFLEX: "circunflexo",
              CARON: "caron", DOUBLE_ACUTE: "agudo duplo", DOUBLE_GRAVE: "grave duplo",
              BREVE: "breve", INV_BREVE: "breve invertido", "": "sem marca"}


def language_name(ortho: Orthography, autonym: Optional[Dict]) -> Optional[Dict]:
    """Nome da língua: autônimo escrito na grafia, mais uma forma 'inglesa' (Wïikho → Wïikhoian)."""
    if not autonym or not autonym.get("form"):
        return None
    native = ortho.spell(autonym["form"])
    cap = native[:1].upper() + native[1:]
    base = nfd(cap)[-1:]
    english = cap + ("n" if base.lower() in "aeiouy" else "ian")
    return {"native": native, "english": english, "ipa": autonym["form"],
            "literal": autonym.get("literal")}


def short_label(e: Dict) -> str:
    return e.get("label") or e["english"].split(" (")[0]


def write_markdown(path: Path, spec: Dict, ortho: Orthography, lexicon: Optional[Dict],
                   syntax: Optional[Dict], name: Optional[Dict]) -> None:
    lines = ["# Ortografia", ""]
    if name:
        lit = f", literalmente '{name['literal']}'" if name.get("literal") else ""
        lines += [f"Nome da língua: **{name['english']}** — nativamente *{name['native']}* "
                  f"/{name['ipa']}/{lit}", ""]
    lines += [f"- Estilo: {STYLE_PT[spec['style']]}",
              f"- Separador para sequências ambíguas: `{spec['separator']}`"
              + (f" ({len(spec['separator_pairs'])} sequências)" if spec["separator_pairs"] else " (nunca necessário)")]
    lines += ["", "## Correspondências", "", "| Grafia | IPA |", "|---|---|"]
    for ipa, g in sorted(spec["graphemes"].items(), key=lambda x: (nfd(x[1]).lower(), x[0])):
        lines.append(f"| {g} | /{ipa}/ |")
    if spec["tones"]:
        lines += ["", "## Tons", "", "| Tom | Marca | Exemplo |", "|---|---|---|"]
        v = next(iter(spec["vowels"]), "a")
        for t, m in spec["tones"].items():
            lines.append(f"| {t} | {TONE_NAMES.get(m, m)} | {nfc(ortho.spell(v)[:1] + m + ortho.spell(v)[1:])} |")
    if syntax:
        lines += ["", "## Frases", ""]
        for ex in syntax["examples"]:
            written = " ".join(ortho.spell(w["form"]) for w in ex["words"])
            written = written[:1].upper() + written[1:] + "."
            ipa = " ".join(w["form"] for w in ex["words"])
            lines += [f"- **{written}** /{ipa}/ — '{ex['translation']}'"]
    if lexicon:
        lines += ["", "## Dicionário", "", "Formato: grafia /pronúncia/ classe 'significado'", ""]
        rows = []
        for e in lexicon["entries"]:
            if not e.get("citation"):
                continue
            rows.append((ortho.spell(e["citation"]), e))
        for w, e in sorted(rows, key=lambda x: nfd(x[0]).lower()):
            lines.append(f"- **{w}** /{e['citation']}/ {POS_ABBR.get(e['pos'], e['pos'])} '{short_label(e)}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(spec: Dict, ortho: Orthography, lexicon: Optional[Dict], name: Optional[Dict]) -> None:
    print(f"\nORTOGRAFIA — estilo {STYLE_PT[spec['style']]}")
    special = [(i, g) for i, g in spec["graphemes"].items() if nfd(g) != nfd(i)]
    print("  " + "  ".join(f"/{i}/ {g}" for i, g in sorted(special, key=lambda x: nfd(x[1]))))
    if spec["tones"]:
        print("  Tons: " + "  ".join(f"{t} {TONE_NAMES.get(m, m)}" for t, m in spec["tones"].items()))
    if spec["separator_pairs"]:
        print(f"  Separador '{spec['separator']}' em {len(spec['separator_pairs'])} sequências ambíguas")
    for n in spec["metadata"]["notes"]:
        print(f"  · {n}")
    if name:
        print(f"\n  Nome da língua: {name['english']} (nativo: {name['native']} /{name['ipa']}/)")
    if lexicon:
        print("\n  Exemplos:")
        sample = [e for e in lexicon["entries"] if e.get("citation")][:12]
        for e in sample:
            print(f"    {ortho.spell(e['citation']):<16} /{e['citation']}/  '{short_label(e)}'")


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def _load(path: Path) -> Optional[Dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Cria a ortografia (romanização) da conlang.")
    ap.add_argument("--language", type=Path, help="pasta de uma língua gerada (ex: languages/lang-31)")
    ap.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY,
                    help="phonemic_inventory.json (usado sem --language)")
    ap.add_argument("--style", choices=STYLES, help="estilo da grafia (sorteado se omitido)")
    ap.add_argument("--seed", type=int, help="semente (padrão: derivada da semente da língua)")
    ap.add_argument("-o", "--output", type=Path, help="arquivo JSON de saída")
    args = ap.parse_args()

    lexicon = syntax = manifest = rules = None
    if args.language:
        d = args.language
        inventory = _load(d / "phonemic_inventory.json")
        if inventory is None:
            raise SystemExit(f"Não encontrei {d / 'phonemic_inventory.json'}")
        rules, lexicon = _load(d / "phonotactics.json"), _load(d / "lexicon.json")
        syntax, manifest = _load(d / "syntax.json"), _load(d / "manifest.json")
        out = args.output or d / "orthography.json"
        md = d / "orthography.md"
    else:
        inventory = _load(args.inventory)
        if inventory is None:
            raise SystemExit(f"Não encontrei {args.inventory}")
        out = args.output or DEFAULT_OUTPUT
        md = out.with_suffix(".md")

    seed = args.seed
    if seed is None and manifest:
        seed = derive_seed(manifest["seed"], "orthography")

    spec = build(inventory, style=args.style, seed=seed, rules=rules)
    ortho = Orthography(spec)
    name = language_name(ortho, manifest.get("autonym") if manifest else None)
    if name:
        spec["language_name"] = name
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md, spec, ortho, lexicon, syntax, name)
    print_summary(spec, ortho, lexicon, name)
    print(f"\n[OK] Ortografia salva em '{out}' e '{md.name}'.")


if __name__ == "__main__":
    main()
