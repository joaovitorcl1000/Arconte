"""
Evolução do léxico (etapa 2 do módulo de evolução).

Três processos, aplicados ao longo do tempo da evolução:

    substituição lexical   palavras somem e são trocadas, a uma taxa que segue a
                           glotocronologia (~14% do vocabulário básico por milênio)
                           e a estabilidade de cada significado: 'fogo', 'nariz' e
                           'água' quase nunca mudam; 'esmagar' e 'duro' mudam muito
    mudança de significado uma palavra passa a significar outra coisa, em mudanças
                           atestadas (latim homo 'ser humano' → francês homme 'homem')
    empréstimos            palavras de outra língua do projeto, adaptadas aos sons
                           e à fonotática da filha (como football → futebol)

As substituições e mudanças de significado acontecem na língua-mãe e depois
passam pelas leis fonéticas; os empréstimos são recentes e entram já adaptados
à língua-filha.
"""

from __future__ import annotations

import math
import unicodedata
from typing import Dict, List, Optional, Tuple

# Lista Leipzig-Jakarta em ordem de estabilidade (Tadmor, Haspelmath & Taylor 2010):
# os primeiros significados são os que as línguas menos substituem.
LEIPZIG_JAKARTA = [
    "FIRE", "NOSE", "GO", "WATER", "MOUTH", "TONGUE", "BLOOD", "BONE", "THOU", "ROOT", "COME", "BREAST",
    "RAIN (PRECIPITATION)", "I", "NAME", "LOUSE", "WING", "FLESH OR MEAT", "ARM OR HAND", "FLY (INSECT)",
    "NIGHT", "EAR", "NECK", "FAR", "DO OR MAKE", "HOUSE", "STONE OR ROCK", "BITTER", "SAY", "TOOTH", "HAIR",
    "BIG", "ONE", "WHO", "HE OR SHE OR IT", "HIT", "FOOT OR LEG", "HORN (ANATOMY)", "THIS", "FISH",
    "YESTERDAY", "DRINK", "BLACK", "NAVEL", "STAND", "BITE", "BACK", "WIND", "SMOKE (EXHAUST)", "WHAT",
    "CHILD (DESCENDANT)", "EGG", "GIVE", "NEW", "BURNING", "NOT", "GOOD", "KNOW", "KNEE", "SAND", "LAUGH",
    "HEAR", "EARTH (SOIL)", "LEAF", "RED", "LIVER", "HIDE", "SKIN", "SUCK", "CARRY", "ANT", "HEAVY", "TAKE",
    "OLD", "EAT", "UPPER LEG (THIGH)", "THICK", "LONG", "BLOW (OF WIND)", "WOOD", "RUN", "FALL", "EYE", "ASH",
    "TAIL", "DOG", "CRY", "TIE", "SEE", "SWEET", "ROPE", "SHADE", "BIRD", "SALT", "SMALL", "WIDE", "STAR",
    "IN", "HARD", "GRIND",
]
RANK = {g: i for i, g in enumerate(LEIPZIG_JAKARTA)}
NUMERALS = {"ONE", "TWO", "THREE", "FOUR", "FIVE"}

# Mudanças de significado atestadas: (origem, destino, tipo, exemplo real)
SEMANTIC_SHIFTS = [
    ("PERSON", "MALE PERSON", "restrição", "latim homo 'ser humano' → francês homme 'homem'"),
    ("MALE PERSON", "HUSBAND", "restrição", "alemão Mann 'homem' → também 'marido'"),
    ("WOMAN", "WIFE", "restrição", "alemão Frau, francês femme: 'mulher' → também 'esposa'"),
    ("SEE", "KNOW", "metáfora", "grego oîda 'eu vi' → 'eu sei'; inglês I see 'entendo'"),
    ("WALK", "GO", "ampliação", "latim ambulare 'passear' → italiano andare 'ir' (etimologia provável)"),
    ("TREE", "WOOD", "metonímia", "gótico triu 'madeira' ~ inglês tree 'árvore'"),
    ("SUN", "DAY (NOT NIGHT)", "metonímia", "chinês 日 rì: 'sol' e 'dia'"),
    ("FOG", "CLOUD", "ampliação", "latim nebula 'névoa' → italiano nuvola 'nuvem'"),
    ("FOOT", "LEG", "ampliação", "grego moderno pódi: 'pé' e 'perna'"),
    ("SKIN", "BARK", "metáfora", "muitas línguas chamam a casca de 'pele da árvore' (CLICS)"),
    ("HAIR", "FEATHER", "metáfora", "várias línguas usam a mesma palavra para 'cabelo' e 'pena' (CLICS)"),
    ("CHILD (YOUNG HUMAN)", "CHILD (DESCENDANT)", "ampliação", "inglês child: 'criança' e 'filho'"),
]
# Substituição por diminutivo expressivo (latim auricula 'orelhinha' → português orelha)
DIMINUTIVE_REPLACEMENTS = {
    "EAR": "latim auricula 'orelhinha' → português orelha, francês oreille",
    "KNEE": "latim genuculum 'joelhinho' → francês genou, português joelho",
    "SUN": "latim soliculum 'solzinho' → francês soleil",
    "BIRD": "latim avicellus 'passarinho' → francês oiseau",
}
# Campos semânticos que mais recebem empréstimos (WOLD)
BORROWABLE_FIELDS = {"Food and drink", "The house", "Agriculture and vegetation", "Clothing and grooming",
                     "Social and political relations", "Religion and belief", "Law", "Warfare and hunting",
                     "Modern world", "Possession"}
BORROWING_RATES = {"none": 0.0, "low": 0.05, "medium": 0.15, "high": 0.30}

TYPE_PT = {"replacement": "substituição", "diminutive": "diminutivo que virou a palavra comum",
           "shift": "mudança de significado", "loan": "empréstimo"}
TYPE_PLURAL = {"replacement": ("substituição", "substituições"), "diminutive": ("diminutivo", "diminutivos"),
               "shift": ("mudança de significado", "mudanças de significado"), "loan": ("empréstimo", "empréstimos")}


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def replacement_rate(gloss: str) -> float:
    """Taxa de substituição por milênio (λ). A média da Leipzig-Jakarta fica perto de 0,17,
    o que dá ~14-16% de palavras trocadas em mil anos, como na glotocronologia."""
    if gloss in RANK:
        return 0.04 + 0.26 * RANK[gloss] / len(LEIPZIG_JAKARTA)
    return 0.22  # fora da lista básica: ~20% em mil anos (retenção típica da Swadesh-200)


# ═══════════════════════════════════════════════════════════════════════════
# Substituição e mudança de significado (na língua-mãe, antes das leis fonéticas)
# ═══════════════════════════════════════════════════════════════════════════

def apply_lexical(ev, lex: Dict, parent_eng, parent_derivation: Optional[Dict]) -> List[Dict]:
    """Escolhe e aplica as mudanças no léxico ainda com as formas da mãe. Devolve os eventos."""
    rng = ev.rng_lex
    entries = {e["gloss"]: e for e in lex["entries"] if e.get("root")}
    events: List[Dict] = []
    touched = set()
    years = ev.years

    # 1. mudanças de significado (no máximo uma por milênio e meio, aproximadamente)
    max_shifts = max(0, round(years / 1500 + rng.random() - 0.3))
    shifts = [s for s in SEMANTIC_SHIFTS if s[0] in entries and s[1] in entries]
    rng.shuffle(shifts)
    for src, dst, kind, example in shifts[:max_shifts]:
        if src in touched or dst in touched:
            continue
        old = entries[dst]["citation"]
        entries[dst]["root"] = list(entries[src]["root"])
        entries[dst]["tones"] = list(entries[src].get("tones") or [])
        entries[dst]["_lex_event"] = {"type": "shift", "from": src}
        touched.update({src, dst})
        events.append({"type": "shift", "gloss": dst, "label": label(entries[dst]), "source": src,
                       "source_label": label(entries[src]), "kind": kind, "example": example,
                       "old_form": old, "year": round(rng.uniform(0.1, 0.9) * years / 50) * 50})

    # 2. substituição lexical, pela estabilidade de cada significado
    dim = (parent_derivation or {}).get("rules", {}).get("diminutive")
    for g, e in sorted(entries.items()):
        if g in touched or g in NUMERALS or e["pos"] in ("pronoun", "negation"):
            continue
        skeleton = "-" in e.get("form", "")  # raiz consonantal (como o árabe k-t-b)
        p = 1 - math.exp(-replacement_rate(g) * years / 1000)
        if rng.random() >= p:
            continue
        old = e["citation"]
        if skeleton:  # a palavra nova também é um esqueleto de consoantes
            new = None
            for _ in range(30):
                cand = parent_eng.ph.generate_skeleton()["segments"]
                if tuple(cand) not in ev.used_roots:
                    new = cand
                    break
            new = new or parent_eng.ph.generate_skeleton()["segments"]
            ev_type, note = "replacement", None
        elif g in DIMINUTIVE_REPLACEMENTS and dim and dim.get("type") == "affix":
            new = attach(parent_eng, e["root"], dim["form"], dim["position"])
            ev_type, note = "diminutive", DIMINUTIVE_REPLACEMENTS[g]
        else:
            n = max(1, min(3, len(parent_eng.ph.syllabify(e["root"]) or [1])))
            new = None
            for _ in range(30):
                cand = parent_eng.ph.generate_root(n)["segments"]
                if tuple(cand) not in ev.used_roots:
                    new = cand
                    break
            new = new or parent_eng.ph.generate_root(n)["segments"]
            ev_type, note = "replacement", None
        ev.used_roots.add(tuple(new))
        e["root"] = new
        e["tones"] = []
        e["_lex_event"] = {"type": ev_type}
        touched.add(g)
        events.append({"type": ev_type, "gloss": g, "label": label(e), "old_form": old,
                       "stability_rank": RANK.get(g), "example": note,
                       "year": round(rng.uniform(0.05, 0.95) * years / 50) * 50})
    return events


def attach(eng, base: List[str], affix: List[str], position: str) -> List[str]:
    morphs = ([{"segs": list(affix), "role": "prefix", "label": "", "sep": "-"},
               {"segs": list(base), "role": "root", "label": "", "sep": "-"}] if position == "prefix" else
              [{"segs": list(base), "role": "root", "label": "", "sep": "-"},
               {"segs": list(affix), "role": "suffix", "label": "", "sep": "-"}])
    morphs, _, _ = eng.resolve(morphs)
    return [s for m in morphs for s in m["segs"]]


def label(e: Dict) -> str:
    return (e.get("label") or e["english"].split(" (")[0]).split("/")[0]


# ═══════════════════════════════════════════════════════════════════════════
# Empréstimos (recentes: entram já adaptados à língua-filha)
# ═══════════════════════════════════════════════════════════════════════════

def nearest(P, seg: str, phonemes: List[str], vowel: bool) -> str:
    """O som da filha mais parecido, pela distância de traços do PHOIBLE."""
    if seg in phonemes:
        return seg
    f = P.feats(seg)
    pool = [p for p in phonemes if P.vowel(p) == vowel] or phonemes
    return min(pool, key=lambda p: (sum(1 for k, v in f.items() if P.feats(p).get(k) != v), p))


def adapt(P, ph, segs: List[str], phonemes: List[str], epenthetic: str) -> List[str]:
    """Troca sons estrangeiros e insere vogais epentéticas até a palavra ser válida (futebol)."""
    out = [nearest(P, s, phonemes, P.vowel(s)) for s in segs]
    for _ in range(6):
        if ph.is_valid(out):
            return out
        # vogal epentética depois da primeira consoante que não forma sílaba válida com a seguinte
        for i in range(len(out) - 1):
            if not P.vowel(out[i]) and not P.vowel(out[i + 1]):
                out = out[:i + 1] + [epenthetic] + out[i + 1:]
                break
        else:
            if not P.vowel(out[-1]):
                out = out + [epenthetic]
            else:
                break
    return out


def apply_loans(ev, lex: Dict, donor: Dict, donor_name: str, inventory: Dict, ph, rate: float) -> List[Dict]:
    if not donor or rate <= 0:
        return []
    P, rng = ev.P, ev.rng_lex
    donor_entries = {e["gloss"]: e for e in donor["entries"] if e.get("citation")}
    phonemes = [nfd(x["ipa"]) for x in inventory["consonants"] + inventory["vowels"]]
    vowels = sorted(inventory["vowels"], key=lambda v: -v.get("frequency", 0))
    epenthetic = nfd(vowels[0]["ipa"]) if vowels else "a"
    events = []
    for e in lex["entries"]:
        g = e["gloss"]
        if not e.get("root") or e.get("_lex_event") or g not in donor_entries or "-" in e.get("form", ""):
            continue
        p = rate if e.get("field") in BORROWABLE_FIELDS else rate * 0.15  # o vocabulário básico resiste
        if g in RANK:
            p *= 0.3
        if rng.random() >= p:
            continue
        src = donor_entries[g]
        segs = ev.segments_any(src["citation"])
        new = adapt(P, ph, segs, phonemes, epenthetic)
        old = e.get("citation")
        e["root"], e["tones"] = new, []
        e["_lex_event"] = {"type": "loan", "donor": donor_name, "donor_form": src["citation"]}
        events.append({"type": "loan", "gloss": g, "label": label(e), "old_form": old,
                       "donor": donor_name, "donor_form": src["citation"], "adapted": "".join(new),
                       "year": round(rng.uniform(0.7, 1.0) * ev.years / 50) * 50})
    return events


def note_for(event: Dict) -> str:
    """Nota curta para o dicionário da filha."""
    t = event["type"]
    if t == "shift":
        return f"antes significava '{event['source_label']}' ({event['kind']})"
    if t == "diminutive":
        return "de um antigo diminutivo"
    if t == "loan":
        return f"empréstimo de {event['donor']} ({event['donor_form']})"
    return "substituiu uma palavra antiga"
