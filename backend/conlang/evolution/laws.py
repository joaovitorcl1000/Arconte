"""
Catálogo de leis fonéticas reais para o módulo de evolução.

Cada lei recebe uma palavra (fonemas + tons por núcleo + fronteiras) e o objeto
de fonologia `P`, que sabe classificar qualquer som pelos traços do PHOIBLE e
trocar traços ("oclusiva surda → fricativa"). As leis são escritas por traços,
para funcionar em qualquer inventário, com mapas explícitos só onde a lei real
tem saídas conhecidas (lei de Grimm: p → f, t → θ, k → x).

Todas as mudanças de uma lei são aplicadas em paralelo na palavra, como nas
regras da fonologia histórica.
"""

from __future__ import annotations

import unicodedata
from typing import Callable, Dict, List, Optional


def _nfd(x: str) -> str:
    return unicodedata.normalize("NFD", x)

# ═══════════════════════════════════════════════════════════════════════════
# Utilidades
# ═══════════════════════════════════════════════════════════════════════════


def rewrite(P, w, fn: Callable[[int], Optional[object]]):
    """
    Aplica `fn` a cada posição (em paralelo). `fn` devolve None (sem mudança),
    um som, uma lista de sons (inclusive vazia, para apagar).
    """
    out: List[str] = []
    changed = False
    for i, s in enumerate(w.segs):
        r = fn(i)
        if r is None:
            out.append(s)
            continue
        changed = True
        if isinstance(r, list):
            out.extend(_nfd(x) for x in r)
        else:
            out.append(_nfd(r))
    return w.with_segs(out) if changed else w


def first(P, mapping: Dict[str, str], seg: str, **features) -> Optional[str]:
    """Saída de um mapa explícito; senão, troca de traços pelo PHOIBLE."""
    if seg in mapping:
        return mapping[seg]
    return P.change(seg, features) if features else None


# ═══════════════════════════════════════════════════════════════════════════
# Leis
# ═══════════════════════════════════════════════════════════════════════════

GRIMM_A = {"p": "f", "t": "θ", "k": "x", "kʷ": "xʷ", "q": "χ", "c": "ç"}
GRIMM_B = {"b": "p", "d": "t", "ɡ": "k", "ɡʷ": "kʷ", "ɢ": "q", "ɟ": "c"}
GRIMM_C = {"bʱ": "b", "dʱ": "d", "ɡʱ": "ɡ", "b̤": "b", "d̤": "d", "ɡ̤": "ɡ", "bʰ": "b", "dʰ": "d", "ɡʰ": "ɡ"}


def grimm(P, w):
    # (1) oclusivas surdas → fricativas, exceto depois de fricativa (sp, st, sk ficam)
    def a(i):
        s = w.segs[i]
        if not (P.stop(s) and not P.voiced(s)) or (i and P.fricative(w.segs[i - 1])):
            return None
        return first(P, GRIMM_A, s, continuant="+", delayedRelease="+", spreadGlottis="-")
    w = rewrite(P, w, a)
    # (2) sonoras → surdas;  (3) sonoras aspiradas → sonoras (ordem que evita fusões)
    w = rewrite(P, w, lambda i: first(P, GRIMM_B, w.segs[i], periodicGlottalSource="-")
                if P.stop(w.segs[i]) and P.voiced(w.segs[i]) and not P.aspirated(w.segs[i]) else None)
    return rewrite(P, w, lambda i: GRIMM_C.get(w.segs[i]) or
                   (P.change(w.segs[i], {"spreadGlottis": "-"}) if P.stop(w.segs[i]) and P.voiced(w.segs[i])
                    and P.aspirated(w.segs[i]) else None))


VERNER = {"f": "β", "θ": "ð", "x": "ɣ", "s": "z", "ɸ": "β", "xʷ": "ɣʷ", "χ": "ʁ"}


def verner(P, w):
    """Fricativas surdas sonorizam quando o acento não está na sílaba anterior."""
    st = w.stress()

    def f(i):
        s = w.segs[i]
        if not (P.fricative(s) and not P.voiced(s)) or i == 0 or i == len(w.segs) - 1:
            return None
        if not (P.voiced(w.segs[i - 1]) and P.voiced(w.segs[i + 1])):
            return None
        prev_syl = w.syllable_of(i - 1)
        if prev_syl is None or prev_syl == st:
            return None
        return first(P, VERNER, s, periodicGlottalSource="+")
    return rewrite(P, w, f)


def umlaut(P, w):
    """Metafonia: vogais posteriores ficam anteriores se a sílaba seguinte tem i ou j (foot → feet)."""
    nuclei = w.nuclei()

    def f(i):
        s = w.segs[i]
        if i not in nuclei or P.front(s):
            return None
        k = nuclei.index(i)
        nxt_end = nuclei[k + 1] if k + 1 < len(nuclei) else None
        window = w.segs[i + 1:(nxt_end + 1) if nxt_end is not None else len(w.segs)]
        if any(P.high_front(x) for x in window):
            return P.change(s, {"front": "+", "back": "-"})
        return None
    return rewrite(P, w, f)


def final_devoicing(P, w):
    if not w.right_edge:
        return w
    n = len(w.segs) - 1
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"periodicGlottalSource": "-"})
                   if i == n and P.obstruent(w.segs[i]) and P.voiced(w.segs[i]) else None)


GVS = {"iː": ["a", "i"], "uː": ["a", "u"], "eː": "iː", "oː": "uː", "ɛː": "eː", "ɔː": "oː", "aː": "eː"}


def great_vowel_shift(P, w):
    return rewrite(P, w, lambda i: GVS.get(w.segs[i]))


def vowel_reduction(P, w):
    """Vogais átonas viram schwa (inglês, russo, português europeu)."""
    st = w.stress()
    nuclei = w.nuclei()
    if len(nuclei) < 2:
        return w
    return rewrite(P, w, lambda i: "ə" if i in nuclei and w.syllable_of(i) != st
                   and not P.long(w.segs[i]) and w.segs[i] not in ("ə", "i", "u") else None)


def lenition_voicing(P, w):
    """Oclusivas surdas sonorizam entre vogais (latim lupus → espanhol lobo)."""
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"periodicGlottalSource": "+"})
                   if P.stop(w.segs[i]) and not P.voiced(w.segs[i]) and w.between_vowels(i) else None)


SPIRANT = {"b": "β", "d": "ð", "ɡ": "ɣ", "ɟ": "ʝ"}


def lenition_spirant(P, w):
    """Oclusivas sonoras viram fricativas entre vogais (espanhol lado [laðo])."""
    return rewrite(P, w, lambda i: first(P, SPIRANT, w.segs[i], continuant="+", delayedRelease="+")
                   if P.stop(w.segs[i]) and P.voiced(w.segs[i]) and w.between_vowels(i) else None)


def lenition_loss(P, w):
    """Fricativas sonoras caem entre vogais (latim legere → português ler)."""
    return rewrite(P, w, lambda i: [] if w.segs[i] in ("ð", "ɣ", "β") and w.between_vowels(i) else None)


PALATAL = {"k": "t̠ʃ", "ɡ": "d̠ʒ", "kʷ": "t̠ʃ", "ɡʷ": "d̠ʒ"}
SLAVIC = {"k": "t̠ʃ", "ɡ": "ʒ", "x": "ʃ"}


def palatalization(P, w):
    """Velares antes de vogal anterior viram africadas (latim centum → italiano cento [t̠ʃ])."""
    return rewrite(P, w, lambda i: PALATAL.get(w.segs[i]) if w.segs[i] in PALATAL
                   and i + 1 < len(w.segs) and P.front_vowel(w.segs[i + 1]) else None)


def first_palatalization(P, w):
    """Primeira palatalização eslava: k ɡ x → t̠ʃ ʒ ʃ antes de vogal anterior."""
    return rewrite(P, w, lambda i: SLAVIC.get(w.segs[i]) if w.segs[i] in SLAVIC
                   and i + 1 < len(w.segs) and P.front_vowel(w.segs[i + 1]) else None)


def syncope(P, w):
    """Vogais átonas internas caem entre consoantes simples (latim calidus → caldo)."""
    nuclei = w.nuclei()
    if len(nuclei) < 3:
        return w
    st = w.stress()
    targets = set()
    for k, i in enumerate(nuclei[1:-1], 1):
        if w.syllable_of(i) == st or P.long(w.segs[i]):
            continue
        if 0 < i < len(w.segs) - 1 and not P.vowel(w.segs[i - 1]) and not P.vowel(w.segs[i + 1]) \
                and (i < 2 or P.vowel(w.segs[i - 2])) and (i + 2 >= len(w.segs) or P.vowel(w.segs[i + 2])):
            targets.add(i)
            break  # uma síncope por palavra
    return rewrite(P, w, lambda i: [] if i in targets else None)


def apocope(P, w):
    """Vogal final átona cai (latim bene → francês bien; português verde → [veɾd])."""
    if not w.right_edge:
        return w
    nuclei = w.nuclei()
    n = len(w.segs) - 1
    if len(nuclei) < 2 or nuclei[-1] != n or w.syllable_of(n) == w.stress() or P.long(w.segs[n]):
        return w
    if n >= 2 and not P.vowel(w.segs[n - 1]) and P.vowel(w.segs[n - 2]):
        return rewrite(P, w, lambda i: [] if i == n else None)
    return w


def nasalization(P, w):
    """Vogal + nasal em coda → vogal nasal (latim manum → português mão)."""
    def f(i):
        s = w.segs[i]
        if P.vowel(s) and i + 1 < len(w.segs) and P.nasal(w.segs[i + 1]) and \
                (i + 2 == len(w.segs) or not P.vowel(w.segs[i + 2])):
            return P.change(s, {"nasal": "+"})
        if P.nasal(s) and i and P.vowel(w.segs[i - 1]) and (i + 1 == len(w.segs) or not P.vowel(w.segs[i + 1])):
            return [] if P.change(w.segs[i - 1], {"nasal": "+"}) else None
        return None
    return rewrite(P, w, f)


def kt_cluster(P, w):
    """kt → jt (latim lactem → português leite) ou → tt (italiano latte)."""
    variant = w.variant("kt", ["j", "t"])
    return rewrite(P, w, lambda i: variant if w.segs[i] in ("k", "ɡ") and i + 1 < len(w.segs)
                   and w.segs[i + 1] == "t" and i and P.vowel(w.segs[i - 1]) else None)


def degemination(P, w):
    return rewrite(P, w, lambda i: [] if i and w.segs[i] == w.segs[i - 1] and not P.vowel(w.segs[i]) else None)


MONO = {("a", "i"): "eː", ("a", "u"): "oː", ("a", "j"): "eː", ("a", "w"): "oː", ("o", "i"): "øː", ("e", "i"): "iː"}


def monophthongization(P, w):
    """Ditongos viram vogais longas (latim aurum → português ouro [o])."""
    out, i, changed = [], 0, False
    while i < len(w.segs):
        pair = tuple(w.segs[i:i + 2])
        if pair in MONO:
            out.append(MONO[pair])
            i += 2
            changed = True
        else:
            out.append(w.segs[i])
            i += 1
    return w.with_segs(out) if changed else w


def diphthongization(P, w):
    """e e o tônicos breves viram ditongos (latim petra → espanhol piedra)."""
    st = w.stress()
    return rewrite(P, w, lambda i: (["j", "e"] if w.segs[i] in ("e", "ɛ") else ["w", "e"])
                   if w.segs[i] in ("e", "ɛ", "o", "ɔ") and w.syllable_of(i) == st and len(w.nuclei()) > 1 else None)


def final_vowel_raising(P, w):
    if not w.right_edge:
        return w
    n = len(w.segs) - 1
    return rewrite(P, w, lambda i: {"e": "i", "o": "u"}.get(w.segs[i]) if i == n and len(w.nuclei()) > 1 else None)


def celtic_p_loss(P, w):
    """Perda do p no céltico (latim pater ~ irlandês antigo athair)."""
    return rewrite(P, w, lambda i: [] if w.segs[i] == "p" and (i == 0 and w.left_edge or w.between_vowels(i)) else None)


CELTIC = {"b": "β", "d": "ð", "ɡ": "ɣ", "m": "β̃", "p": "ɸ", "t": "θ", "k": "x", "s": "h"}


def celtic_lenition(P, w):
    """Lenição céltica: consoantes simples entre vogais enfraquecem (galês, irlandês)."""
    return rewrite(P, w, lambda i: (CELTIC.get(w.segs[i]) if w.segs[i] != "m" else "v")
                   if w.segs[i] in CELTIC and w.between_vowels(i) else None)


def grassmann(P, w):
    """Lei de Grassmann: a primeira de duas aspiradas perde a aspiração (grego, sânscrito)."""
    asp = [i for i, s in enumerate(w.segs) if P.aspirated(s)]
    if len(asp) < 2:
        return w
    target = asp[0]
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"spreadGlottis": "-"}) if i == target else None)


def ruki(P, w):
    """Regra ruki: s → ʃ depois de r, u, k, i (indo-iraniano, eslavo)."""
    return rewrite(P, w, lambda i: "ʃ" if w.segs[i] == "s" and i and
                   (w.segs[i - 1] in ("r", "ɾ", "k", "u", "uː", "i", "iː")) else None)


def s_to_h(P, w):
    """s → h no início da palavra e entre vogais (latim septem ~ grego hepta)."""
    return rewrite(P, w, lambda i: "h" if w.segs[i] == "s" and
                   ((i == 0 and w.left_edge and len(w.segs) > 1 and P.vowel(w.segs[1])) or w.between_vowels(i)) else None)


def rhotacism(P, w):
    """Rotacismo: s → r entre vogais (latim arcaico *flosis → floris)."""
    return rewrite(P, w, lambda i: "r" if w.segs[i] in ("s", "z") and w.between_vowels(i) else None)


def open_syllables(P, w):
    """Lei das sílabas abertas (eslavo comum): consoantes em coda caem."""
    def f(i):
        s = w.segs[i]
        if P.vowel(s):
            return None
        nxt = w.segs[i + 1] if i + 1 < len(w.segs) else None
        if nxt is None:
            return [] if w.right_edge and len(w.nuclei()) >= 1 else None
        if not P.vowel(nxt) and i and P.vowel(w.segs[i - 1]) and P.sonority(s) >= P.sonority(nxt):
            return []
        return None
    return rewrite(P, w, f)


def final_consonant_loss(P, w):
    """Consoantes finais caem (proto-polinésio *taŋis → havaiano kani)."""
    if not w.right_edge or len(w.nuclei()) == 0:
        return w
    n = len(w.segs) - 1
    return rewrite(P, w, lambda i: [] if i == n and not P.vowel(w.segs[i]) else None)


def k_to_glottal(P, w):
    return rewrite(P, w, lambda i: "ʔ" if w.segs[i] == "k" else None)


def glottal_loss(P, w):
    return rewrite(P, w, lambda i: [] if w.segs[i] == "ʔ" and (w.between_vowels(i) or (i == 0 and w.left_edge)) else None)


def h_loss(P, w):
    return rewrite(P, w, lambda i: [] if w.segs[i] == "h" and (w.between_vowels(i) or (i == 0 and w.left_edge and len(w.segs) > 1)) else None)


def liquid_merger(P, w):
    return rewrite(P, w, lambda i: "l" if w.segs[i] in ("r", "ɾ", "ɹ") else None)


def obstruent_devoicing(P, w):
    """Perda do contraste de sonoridade nas obstruintes (b d ɡ → p t k)."""
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"periodicGlottalSource": "-"})
                   if P.obstruent(w.segs[i]) and P.voiced(w.segs[i]) else None)


def coda_glottalization(P, w):
    """Oclusivas em coda viram oclusiva glotal (cantonês, birmanês)."""
    return rewrite(P, w, lambda i: "ʔ" if P.stop(w.segs[i]) and not P.voiced(w.segs[i])
                   and w.is_coda(i) and w.segs[i] != "ʔ" else None)


def tonogenesis(P, w):
    """
    Tonogênese (chinês, vietnamita): codas glotais caem e deixam tom ascendente;
    codas fricativas caem e deixam tom descendente; as demais sílabas ficam com
    tom médio (o vietnamita e o chinês médio passaram por isso).
    """
    if w.tones and any(w.tones):
        return w
    nuclei = w.nuclei()
    if not nuclei:
        return w
    tones = []
    drop = set()
    for k, i in enumerate(nuclei):
        end = (nuclei[k + 1] - 1) if k + 1 < len(nuclei) else len(w.segs) - 1
        coda = [j for j in range(i + 1, end + 1) if w.is_coda(j)]
        last = coda[-1] if coda else None
        if last is not None and w.segs[last] == "ʔ":
            tones.append("˧˥")
            drop.add(last)
        elif last is not None and P.fricative(w.segs[last]):
            tones.append("˥˩")
            drop.add(last)
        else:
            tones.append("˧")
    w2 = rewrite(P, w, lambda i: [] if i in drop else None)
    return w2.with_tones(tones)


def nasal_assimilation(P, w):
    def f(i):
        if w.segs[i] != "n" or i + 1 >= len(w.segs):
            return None
        nxt = w.segs[i + 1]
        if P.labial_cons(nxt):
            return "m"
        if P.velar(nxt):
            return "ŋ"
        return None
    return rewrite(P, w, f)


def length_loss(P, w):
    """Perda do contraste de quantidade vocálica (latim vulgar)."""
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"long": "-", "short": "-"}) or w.segs[i].replace("ː", "")
                   if P.long(w.segs[i]) else None)


def aspiration_loss(P, w):
    return rewrite(P, w, lambda i: P.change(w.segs[i], {"spreadGlottis": "-"}) if P.aspirated(w.segs[i]) else None)


def cluster_simplification(P, w):
    """Três consoantes seguidas: a do meio cai (latim *ponctus...)."""
    return rewrite(P, w, lambda i: [] if 0 < i < len(w.segs) - 1 and not P.vowel(w.segs[i - 1])
                   and not P.vowel(w.segs[i]) and not P.vowel(w.segs[i + 1]) else None)


# ═══════════════════════════════════════════════════════════════════════════
# Catálogo
# ═══════════════════════════════════════════════════════════════════════════

LAWS: Dict[str, Dict] = {
    "grimm": {"fn": grimm, "name": "Lei de Grimm", "family": "germânica",
              "description": "p t k → f θ x; b d ɡ → p t k; bʱ dʱ ɡʱ → b d ɡ",
              "example": "latim pater, piscis ~ inglês father, fish"},
    "verner": {"fn": verner, "name": "Lei de Verner", "family": "germânica",
               "description": "fricativas surdas sonorizam quando o acento não está na sílaba anterior",
               "example": "gótico broþar 'irmão' mas fadar 'pai' (ð)"},
    "umlaut": {"fn": umlaut, "name": "Metafonia (umlaut)", "family": "germânica",
               "description": "vogal posterior fica anterior se a sílaba seguinte tem i ou j",
               "example": "*fōtiz → inglês antigo fēt (foot → feet)"},
    "final_devoicing": {"fn": final_devoicing, "name": "Ensurdecimento final", "family": "germânica",
                        "description": "obstruintes sonoras ficam surdas no fim da palavra",
                        "example": "alemão Hund [hʊnt], Hunde [hʊndə]"},
    "great_vowel_shift": {"fn": great_vowel_shift, "name": "Grande Mudança Vocálica", "family": "inglesa",
                          "description": "vogais longas sobem (eː → iː, oː → uː) e as altas viram ditongos (iː → ai)",
                          "example": "inglês médio [miːs] 'mice' → [mais]"},
    "vowel_reduction": {"fn": vowel_reduction, "name": "Redução de átonas", "family": "universal",
                        "description": "vogais átonas viram schwa (ə)",
                        "example": "inglês sofa [ˈsoʊfə]; russo moloko [məlɐˈko]"},
    "lenition_voicing": {"fn": lenition_voicing, "name": "Lenição: sonorização", "family": "românica",
                         "description": "p t k → b d ɡ entre vogais",
                         "example": "latim lupus, vita → espanhol lobo, vida"},
    "lenition_spirant": {"fn": lenition_spirant, "name": "Lenição: espirantização", "family": "românica",
                         "description": "b d ɡ → β ð ɣ entre vogais",
                         "example": "espanhol lado [ˈlaðo]"},
    "lenition_loss": {"fn": lenition_loss, "name": "Lenição: queda", "family": "românica",
                      "description": "β ð ɣ caem entre vogais",
                      "example": "latim legere → português ler"},
    "palatalization": {"fn": palatalization, "name": "Palatalização românica", "family": "românica",
                       "description": "k ɡ → t̠ʃ d̠ʒ antes de vogal anterior",
                       "example": "latim centum [k] → italiano cento [t̠ʃ]"},
    "first_palatalization": {"fn": first_palatalization, "name": "Primeira palatalização eslava", "family": "eslava",
                             "description": "k ɡ x → t̠ʃ ʒ ʃ antes de vogal anterior",
                             "example": "*kelo → russo čelo 'testa'"},
    "syncope": {"fn": syncope, "name": "Síncope", "family": "universal",
                "description": "vogal átona interna cai entre consoantes simples",
                "example": "latim calidus → italiano caldo"},
    "apocope": {"fn": apocope, "name": "Apócope", "family": "universal",
                "description": "vogal final átona cai",
                "example": "latim bene → francês bien; inglês antigo nama → name [neɪm]"},
    "nasalization": {"fn": nasalization, "name": "Nasalização", "family": "românica",
                     "description": "vogal + nasal em coda → vogal nasal",
                     "example": "latim manum → português mão; latim bonum → francês bon [bɔ̃]"},
    "kt_cluster": {"fn": kt_cluster, "name": "Mudança de kt", "family": "românica",
                   "description": "kt → jt ou tt",
                   "example": "latim lactem → português leite, italiano latte"},
    "degemination": {"fn": degemination, "name": "Degeminação", "family": "universal",
                     "description": "consoantes duplas viram simples",
                     "example": "latim gutta → espanhol gota"},
    "monophthongization": {"fn": monophthongization, "name": "Monotongação", "family": "universal",
                           "description": "ai au → eː oː",
                           "example": "latim aurum → português ouro [ˈoru]"},
    "diphthongization": {"fn": diphthongization, "name": "Ditongação", "family": "românica",
                         "description": "e o tônicos → je we",
                         "example": "latim petra, porta → espanhol piedra, puerta"},
    "final_vowel_raising": {"fn": final_vowel_raising, "name": "Elevação de vogal final", "family": "românica",
                            "description": "e o finais → i u",
                            "example": "português leite [ˈlejt͡ʃi], muito [ˈmũjtu]"},
    "celtic_p_loss": {"fn": celtic_p_loss, "name": "Perda do p céltico", "family": "céltica",
                      "description": "p cai no início da palavra e entre vogais",
                      "example": "latim pater ~ irlandês antigo athair"},
    "celtic_lenition": {"fn": celtic_lenition, "name": "Lenição céltica", "family": "céltica",
                        "description": "consoantes simples entre vogais enfraquecem (b → β, m → v, s → h)",
                        "example": "galês ei fam 'sua mãe' (mam 'mãe')"},
    "grassmann": {"fn": grassmann, "name": "Lei de Grassmann", "family": "indo-iraniana / grega",
                  "description": "de duas aspiradas na palavra, a primeira perde a aspiração",
                  "example": "grego *tʰrikʰ- → tʰrikʰ- / trikʰós 'cabelo'"},
    "ruki": {"fn": ruki, "name": "Regra ruki", "family": "indo-iraniana",
             "description": "s → ʃ depois de r, u, k, i",
             "example": "sânscrito vṛkṣa- (ṣ < s depois de k)"},
    "s_to_h": {"fn": s_to_h, "name": "s → h", "family": "grega / iraniana",
               "description": "s → h no início da palavra e entre vogais",
               "example": "latim septem ~ grego hepta; sânscrito sapta ~ avéstico hapta"},
    "rhotacism": {"fn": rhotacism, "name": "Rotacismo", "family": "itálica",
                  "description": "s → r entre vogais",
                  "example": "latim flōs, flōris (de *flōsis)"},
    "open_syllables": {"fn": open_syllables, "name": "Lei das sílabas abertas", "family": "eslava",
                       "description": "consoantes em coda caem; todas as sílabas terminam em vogal",
                       "example": "proto-eslavo *sūnus → sъnъ 'filho'"},
    "final_consonant_loss": {"fn": final_consonant_loss, "name": "Queda de consoantes finais", "family": "polinésia",
                             "description": "consoantes no fim da palavra caem",
                             "example": "proto-austronésio *taŋis → havaiano kani 'chorar'"},
    "k_to_glottal": {"fn": k_to_glottal, "name": "k → ʔ", "family": "polinésia",
                     "description": "k vira oclusiva glotal",
                     "example": "proto-polinésio *waka → havaiano waʻa 'canoa'"},
    "glottal_loss": {"fn": glottal_loss, "name": "Queda de ʔ", "family": "polinésia",
                     "description": "a oclusiva glotal cai entre vogais e no início",
                     "example": "taitiano"},
    "h_loss": {"fn": h_loss, "name": "Queda de h", "family": "universal",
               "description": "h cai entre vogais e no início da palavra",
               "example": "latim habere → espanhol haber [aˈβeɾ]"},
    "liquid_merger": {"fn": liquid_merger, "name": "Fusão de líquidas", "family": "polinésia",
                      "description": "r e l se fundem em l",
                      "example": "proto-polinésio *r, *l → havaiano l"},
    "obstruent_devoicing": {"fn": obstruent_devoicing, "name": "Perda da sonoridade", "family": "polinésia / chinesa",
                            "description": "b d ɡ → p t k: as obstruintes perdem o contraste de sonoridade",
                            "example": "chinês médio *d- → mandarim t-"},
    "coda_glottalization": {"fn": coda_glottalization, "name": "Glotalização de codas", "family": "chinesa",
                            "description": "p t k em coda → ʔ",
                            "example": "chinês médio *-k → dialetos wu e min -ʔ"},
    "tonogenesis": {"fn": tonogenesis, "name": "Tonogênese", "family": "chinesa / vietnamita",
                    "description": "codas ʔ caem e deixam tom ascendente; codas fricativas deixam tom descendente",
                    "example": "vietnamita: tons nasceram de -ʔ e -h do proto-vietico"},
    "nasal_assimilation": {"fn": nasal_assimilation, "name": "Assimilação nasal", "family": "universal",
                           "description": "n → m antes de labial, n → ŋ antes de velar",
                           "example": "latim *inperare → imperare"},
    "length_loss": {"fn": length_loss, "name": "Perda da quantidade vocálica", "family": "românica",
                    "description": "vogais longas viram breves",
                    "example": "latim clássico → latim vulgar"},
    "aspiration_loss": {"fn": aspiration_loss, "name": "Perda da aspiração", "family": "universal",
                        "description": "consoantes aspiradas perdem a aspiração",
                        "example": "grego antigo pʰ → grego moderno f (via fricativa)"},
    "cluster_simplification": {"fn": cluster_simplification, "name": "Simplificação de encontros", "family": "universal",
                               "description": "em três consoantes seguidas, a do meio cai",
                               "example": "inglês castle [ˈkæsl̩] (t mudo)"},
}

# Perfis: leis em ordem cronológica plausível
PROFILES: Dict[str, Dict] = {
    "germanic": {"name": "germânico", "laws": ["grimm", "verner", "umlaut", "final_devoicing",
                                               "vowel_reduction", "apocope", "degemination"]},
    "english": {"name": "inglês", "laws": ["grimm", "verner", "umlaut", "vowel_reduction", "apocope",
                                           "great_vowel_shift", "h_loss", "cluster_simplification"]},
    "romance": {"name": "românico", "laws": ["length_loss", "palatalization", "lenition_voicing", "kt_cluster",
                                             "syncope", "lenition_spirant", "diphthongization", "degemination",
                                             "apocope", "nasalization", "lenition_loss", "final_vowel_raising"]},
    "celtic": {"name": "céltico", "laws": ["celtic_p_loss", "celtic_lenition", "apocope", "syncope",
                                           "s_to_h", "nasal_assimilation"]},
    "slavic": {"name": "eslavo", "laws": ["first_palatalization", "monophthongization", "ruki",
                                          "open_syllables", "vowel_reduction", "final_devoicing"]},
    "indo_iranian": {"name": "indo-iraniano", "laws": ["grassmann", "ruki", "s_to_h", "aspiration_loss",
                                                       "monophthongization"]},
    "hellenic": {"name": "grego", "laws": ["grassmann", "s_to_h", "h_loss", "aspiration_loss",
                                           "vowel_reduction"]},
    "polynesian": {"name": "polinésio", "laws": ["final_consonant_loss", "obstruent_devoicing", "s_to_h",
                                                 "k_to_glottal", "liquid_merger", "h_loss", "glottal_loss"]},
    "sinitic": {"name": "chinês / sudeste asiático", "laws": ["coda_glottalization", "tonogenesis",
                                                              "obstruent_devoicing", "length_loss",
                                                              "final_consonant_loss"]},
    "natural": {"name": "natural", "laws": []},
}

# Perfil natural: leis comuns nas línguas do mundo, com peso aproximado de frequência
NATURAL_WEIGHTS = {
    "nasal_assimilation": 0.9, "lenition_voicing": 0.8, "palatalization": 0.8, "final_devoicing": 0.6,
    "apocope": 0.6, "syncope": 0.5, "vowel_reduction": 0.5, "monophthongization": 0.5, "h_loss": 0.5,
    "degemination": 0.5, "cluster_simplification": 0.4, "final_vowel_raising": 0.4, "lenition_spirant": 0.4,
    "diphthongization": 0.3, "nasalization": 0.3, "umlaut": 0.3, "s_to_h": 0.3, "length_loss": 0.3,
    "aspiration_loss": 0.3, "rhotacism": 0.2, "open_syllables": 0.2, "final_consonant_loss": 0.2,
    "obstruent_devoicing": 0.2, "lenition_loss": 0.2, "coda_glottalization": 0.15, "tonogenesis": 0.1,
}
