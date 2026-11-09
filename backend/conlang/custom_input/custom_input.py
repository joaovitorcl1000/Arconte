"""
Módulo — Entrada do usuário (palavras e fonemas personalizados).

Lê um arquivo de texto com seções, no espírito dos campos do Vulgarlang:

    [fonemas]
    consoantes: p t k m n s l
    vogais: a e i o u

    [verbos]
    kip  | bite  | transitivo

    [substantivos]
    wad  | dog   | masculino

    [adjetivos]
    nos  | good

    [outras]
    gich | the   | artigo

Todas as seções são opcionais. O que o usuário não informar é sorteado.
Este módulo não roda sozinho: é usado pelo orquestrador (generate_language.py
--custom arquivo.txt), que aplica cada parte na etapa certa:

    inventário  → fonemas declarados (ou fonemas das palavras somados ao sorteio)
    fonotática  → adapta as regras às palavras do usuário (ou as marca como exceção)
    motor       → palavras gramaticais do usuário substituem as partículas sorteadas
    léxico      → as palavras ocupam seus conceitos e ficam travadas

Os significados são casados com os conceitos do Concepticon em inglês
(dog, bite, sea...). Significados sem conceito correspondente viram entradas novas.

Nenhum outro módulo precisa ser alterado: este módulo só lê e ajusta os JSONs
que eles produzem (e usa suas funções públicas).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# Vocabulário do arquivo (português e inglês)
# ═══════════════════════════════════════════════════════════════════════════

SECTIONS = {
    "fonemas": "phonemes", "phonemes": "phonemes",
    "verbos": "verb", "verbs": "verb",
    "substantivos": "noun", "nomes": "noun", "nouns": "noun",
    "adjetivos": "adjective", "adjectives": "adjective",
    "outras": "other", "other": "other", "outros": "other",
    "palavras": "any", "words": "any",
}
PHONEME_KEYS = {"consoantes": "consonants", "consonants": "consonants",
                "vogais": "vowels", "vowels": "vowels", "tons": "tones", "tones": "tones"}
SECTION_CATEGORY = {"verb": "V", "noun": "N", "adjective": "A"}

TRANSITIVITY = {"transitivo": "transitive", "transitive": "transitive", "t": "transitive",
                "intransitivo": "intransitive", "intransitive": "intransitive", "i": "intransitive",
                "bitransitivo": "ditransitive", "ditransitive": "ditransitive",
                "estativo": "stative", "stative": "stative"}
GENDERS = {"masculino": "masculine", "masculine": "masculine", "m": "masculine",
           "feminino": "feminine", "feminine": "feminine", "f": "feminine",
           "neutro": "neuter", "neuter": "neuter", "n": "neuter",
           "animado": "animate", "animate": "animate", "inanimado": "inanimate",
           "inanimate": "inanimate", "humano": "human", "human": "human"}
OTHER_CLASSES = {"artigo": "article", "article": "article", "conjunção": "conjunction",
                 "conjuncao": "conjunction", "conjunction": "conjunction",
                 "pronome": "pronoun", "pronoun": "pronoun", "preposição": "adposition",
                 "preposicao": "adposition", "posposição": "adposition", "adposição": "adposition",
                 "adposition": "adposition", "advérbio": "adverb", "adverbio": "adverb",
                 "adverb": "adverb", "numeral": "numeral", "número": "numeral",
                 "negação": "negation", "negacao": "negation", "negation": "negation",
                 "interjeição": "interjection", "interjeicao": "interjection",
                 "interjection": "interjection", "partícula": "particle", "particula": "particle",
                 "particle": "particle", "demonstrativo": "demonstrative",
                 "demonstrative": "demonstrative", "interrogativo": "interrogative",
                 "interrogative": "interrogative", "quantificador": "quantifier",
                 "quantifier": "quantifier"}

# Significado em inglês → (célula da tabela de pronomes, conceito do Concepticon)
PRONOUN_MEANINGS = {
    "i": ("1.singular", "I"), "me": ("1.singular", "I"),
    "you": ("2.singular", "THOU"), "thou": ("2.singular", "THOU"), "you (sg)": ("2.singular", "THOU"),
    "you (pl)": ("2.plural", "YOU"), "you all": ("2.plural", "YOU"), "y'all": ("2.plural", "YOU"),
    "he": ("3.singular.masculine", "HE"), "him": ("3.singular.masculine", "HE"),
    "she": ("3.singular.feminine", "HE"), "her": ("3.singular.feminine", "HE"),
    "it": ("3.singular", "HE OR SHE OR IT"),
    "we": ("1.plural", "WE"), "us": ("1.plural", "WE"),
    "we (inclusive)": ("1incl.plural", "WE"), "we (exclusive)": ("1excl.plural", "WE"),
    "they": ("3.plural", "THEY"), "them": ("3.plural", "THEY"),
}
# Significados que substituem palavras gramaticais do motor
FUNCTION_MEANINGS = {"not": ("negation", "negative"), "no": ("negation", "negative"),
                     "the": ("definiteness", "definite"), "a": ("definiteness", "indefinite"),
                     "an": ("definiteness", "indefinite")}

ALIASES = {"g": "ɡ", "'": "ʼ"}  # teclas comuns → símbolo IPA usado no PHOIBLE
IGNORED = set("ˈˌ.-")  # acento e separadores silábicos são ignorados


def nfd(s: str) -> str:
    return unicodedata.normalize("NFD", s)


def norm_meaning(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"^to ", "", s)
    return re.sub(r"\s+", " ", s).strip(" ?!.")


def concept_keys(c: Dict) -> Set[str]:
    """Chaves de busca de um conceito: 'to bite' → bite; 'SKIN (HUMAN)' → skin; 'flesh/meat' → flesh, meat."""
    keys = set()
    for raw in (c["english"], c["gloss"]):
        base = re.sub(r"\(.*?\)", "", raw.lower()).strip()
        for part in re.split(r"[/,]| or ", base):
            k = norm_meaning(part)
            if k:
                keys.add(k)
    return keys


# ═══════════════════════════════════════════════════════════════════════════
# Leitura do arquivo
# ═══════════════════════════════════════════════════════════════════════════

def parse(path: Path) -> Dict:
    """Lê o arquivo; erros de formato viram avisos com o número da linha."""
    spec: Dict = {"phonemes": {}, "words": [], "warnings": [], "path": str(path)}
    section = None
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"\[(.+?)\]", line)
        if m:
            name = m.group(1).strip().lower()
            section = SECTIONS.get(name)
            if section is None:
                spec["warnings"].append(f"linha {n}: seção desconhecida [{name}], ignorada")
            continue
        if section is None:
            spec["warnings"].append(f"linha {n}: fora de uma seção, ignorada")
            continue
        if section == "phonemes":
            key, _, value = line.partition(":")
            k = PHONEME_KEYS.get(key.strip().lower())
            if not k:
                spec["warnings"].append(f"linha {n}: use 'consoantes:', 'vogais:' ou 'tons:'")
                continue
            spec["phonemes"][k] = [nfd(ALIASES.get(x, x)) for x in value.split()]
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            spec["warnings"].append(f"linha {n}: formato esperado 'forma | significado'")
            continue
        form, meaning = parts[0], parts[1]
        extra = parts[2].lower() if len(parts) > 2 and parts[2] else None
        word = {"line": n, "raw": form, "meanings": [m.strip() for m in re.split(r"[;,]", meaning) if m.strip()],
                "section": section}
        if " " in form:
            spec["warnings"].append(f"linha {n}: '{form}' tem espaço; use uma palavra por linha")
            continue
        if section == "verb" and extra:
            word["transitivity"] = TRANSITIVITY.get(extra)
            if not word["transitivity"]:
                spec["warnings"].append(f"linha {n}: transitividade '{extra}' desconhecida, ignorada")
        elif section == "noun" and extra:
            m2 = re.fullmatch(r"(?:classe|class)\s*(\d+)", extra)
            word["gender"] = f"class_{m2.group(1)}" if m2 else GENDERS.get(extra)
            if not word["gender"]:
                spec["warnings"].append(f"linha {n}: gênero '{extra}' desconhecido, ignorado")
        elif section == "other":
            word["pos"] = OTHER_CLASSES.get(extra or "", "particle")
            if extra and extra not in OTHER_CLASSES:
                spec["warnings"].append(f"linha {n}: classe '{extra}' desconhecida; usando 'particle'")
        spec["words"].append(word)
    return spec


# ═══════════════════════════════════════════════════════════════════════════
# Fonemas: segmentação e inventário
# ═══════════════════════════════════════════════════════════════════════════

def tokenize(form: str, symbols: Iterable[str]) -> Tuple[Optional[List[str]], str]:
    """
    Divide uma forma IPA em fonemas pelo símbolo mais longo que casa
    (t̠ʃʰ é um fonema, não quatro caracteres). Devolve (fonemas, problema).
    """
    syms = sorted({nfd(s) for s in symbols}, key=len, reverse=True)
    s = "".join(ALIASES.get(ch, ch) for ch in nfd(form) if ch not in IGNORED)
    out, i = [], 0
    while i < len(s):
        hit = next((x for x in syms if s.startswith(x, i)), None)
        if not hit:
            return None, s[i]
        out.append(hit)
        i += len(hit)
    return out, ""


def prepare(spec: Dict, phoible_symbols: Iterable[str]) -> None:
    """Segmenta as palavras; com fonemas declarados, só eles são aceitos."""
    declared = spec["phonemes"].get("consonants", []) + spec["phonemes"].get("vowels", [])
    symbols = set(declared) if declared else set(phoible_symbols)
    kept = []
    for w in spec["words"]:
        segs, bad = tokenize(w["raw"], symbols)
        if segs is None:
            why = (f"'{bad}' não está entre os fonemas declarados" if declared
                   else f"'{bad}' não é um símbolo IPA reconhecido")
            spec["warnings"].append(f"linha {w['line']}: '{w['raw']}' ignorada — {why}")
            continue
        w["segments"] = segs
        w["form"] = "".join(segs)
        kept.append(w)
    spec["words"] = kept


def _entry(stats, ipa: str, inv_mod) -> Dict:
    seg = stats.segments[ipa]
    feats = dict(zip(stats.features, seg.vector))
    e = {"ipa": ipa, "frequency": round(stats.frequency(ipa), 4)}
    if seg.seg_class == "consonant":
        manner, place = inv_mod.classify_consonant(feats)
        return {**e, "manner": manner, "place": place, "features": feats}
    return {**e, **inv_mod.classify_vowel(feats), "features": feats}


def declared_inventory(spec: Dict, stats, inv_mod, seed: int) -> Dict:
    """Inventário montado exatamente com os fonemas declarados pelo usuário."""
    ph = spec["phonemes"]
    unknown = [x for x in ph.get("consonants", []) + ph.get("vowels", []) + ph.get("tones", [])
               if x not in stats.segments]
    if unknown:
        raise SystemExit("Fonemas declarados que não existem no PHOIBLE: " + " ".join(unknown) +
                         "\nVerifique os símbolos IPA (ex: ɡ e não g; ʃ para 'sh').")
    misplaced = [x for x in ph.get("consonants", []) if stats.segments[x].seg_class != "consonant"] + \
                [x for x in ph.get("vowels", []) if stats.segments[x].seg_class != "vowel"]
    if misplaced:
        spec["warnings"].append("fonemas na lista errada (reclassificados): " + " ".join(misplaced))
    phonemes = set(ph.get("consonants", [])) | set(ph.get("vowels", []))
    gen = inv_mod.InventoryGenerator(stats, inv_mod.GeneratorOptions(seed=seed), {})
    nc = sum(1 for x in phonemes if stats.segments[x].seg_class == "consonant")
    inv = gen._export(phonemes, ph.get("tones", []), nc, len(phonemes) - nc, None)
    inv["metadata"]["mode"] = "custom"
    inv["metadata"]["changes"] = ["inventário declarado pelo usuário"]
    return inv


def extend_inventory(inv: Dict, spec: Dict, stats, inv_mod) -> List[str]:
    """Soma ao inventário sorteado os fonemas usados nas palavras do usuário."""
    have = {x["ipa"] for x in inv["consonants"] + inv["vowels"]}
    added = []
    for w in spec["words"]:
        for s in w["segments"]:
            if s not in have and s in stats.segments:
                e = _entry(stats, s, inv_mod)
                (inv["consonants"] if "manner" in e else inv["vowels"]).append(e)
                have.add(s)
                added.append(s)
    if added:
        inv["counts"].update(consonants=len(inv["consonants"]), vowels=len(inv["vowels"]))
        inv["metadata"]["changes"] += [f"+{x} (palavra do usuário)" for x in added]
    return added


# ═══════════════════════════════════════════════════════════════════════════
# Fonotática: adaptar regras às palavras do usuário
# ═══════════════════════════════════════════════════════════════════════════

def _split_cluster(cluster: List[str], son: Dict[str, int]) -> Tuple[List[str], List[str]]:
    """Coda + ataque: o ataque é o maior sufixo com sonoridade crescente (máx. 3)."""
    j = len(cluster)
    while j > 0 and len(cluster) - j < 3:
        cand = cluster[j - 1:]
        if all(son[a] < son[b] for a, b in zip(cand, cand[1:])):
            j -= 1
        else:
            break
    return cluster[:j], cluster[j:]


def syllabify_free(segs: List[str], vowels: Set[str], son: Dict[str, int]) -> Optional[List[Tuple[List, List, List]]]:
    """Silabifica sem regras da língua (só pela sonoridade): [(ataque, núcleo, coda)]."""
    nuclei = [i for i, s in enumerate(segs) if s in vowels]
    if not nuclei:
        return None
    sylls = []
    onset = segs[:nuclei[0]]
    for k, a in enumerate(nuclei):
        nxt = nuclei[k + 1] if k + 1 < len(nuclei) else None
        cluster = segs[a + 1:nxt] if nxt is not None else segs[a + 1:]
        if nxt is None:
            sylls.append((onset, [segs[a]], cluster))
        else:
            coda, next_onset = _split_cluster(cluster, son)
            sylls.append((onset, [segs[a]], coda))
            onset = next_onset
    return sylls


def adapt_phonotactics(rules: Dict, inventory: Dict, spec: Dict, policy: str, pht_mod) -> Dict:
    """
    adapt: a fonotática passa a aceitar os moldes, encontros e codas das palavras
           do usuário, e os moldes delas ganham peso no sorteio das palavras geradas.
    exception: as regras não mudam; palavras inválidas ficam marcadas como exceção.
    """
    report: Dict = {"policy": policy, "changes": [], "exceptions": []}
    words = [w for w in spec["words"]]
    if not words:
        return report
    vowels = {v["ipa"] for v in inventory["vowels"]}
    son = rules["sonority"]

    if policy == "adapt":
        counts: Dict[str, int] = {}
        onsets2, onsets3 = {tuple(c) for c in rules["onsets"]["clusters"]}, \
            {tuple(c) for c in rules["onsets"]["triple"]}
        codas, finals = set(rules["codas"]["single"]), set(rules["codas"]["word_final"])
        coda2 = {tuple(c) for c in rules["codas"]["clusters"]}
        forbidden = set(rules["onsets"]["word_initial_forbidden"])
        before = {"templates": set(rules["templates"]), "o2": set(onsets2), "o3": set(onsets3),
                  "codas": set(codas), "coda2": set(coda2)}
        for w in words:
            sylls = syllabify_free(w["segments"], vowels, son)
            if not sylls:
                spec["warnings"].append(f"linha {w['line']}: '{w['form']}' não tem vogal; "
                                        "entra como exceção")
                continue
            for i, (on, nu, co) in enumerate(sylls):
                if len(on) > 3 or len(co) > 2:
                    continue  # fora do que a fonotática representa: vira exceção
                pat = "C" * len(on) + "V" + "C" * len(co)
                counts[pat] = counts.get(pat, 0) + 1
                if len(on) == 2:
                    onsets2.add(tuple(on))
                elif len(on) == 3:
                    onsets3.add(tuple(on))
                if i == 0 and on and on[0] in forbidden:
                    forbidden.discard(on[0])
                    report["changes"].append(f"/{on[0]}/ passa a ser aceito no início de palavra")
                if i == 0 and not on and rules["onset_required"]:
                    rules["onset_required"] = False
                    report["changes"].append("ataque deixa de ser obrigatório")
                if i > 0 and not on and not sylls[i - 1][2] and not rules["allow_hiatus"]:
                    rules["allow_hiatus"] = True
                    report["changes"].append("hiato passa a ser permitido")
                if len(co) == 1:
                    codas.add(co[0])
                    if i == len(sylls) - 1:
                        finals.add(co[0])
                elif len(co) == 2:
                    coda2.add(tuple(co))
                    codas.update(co)
                    if i == len(sylls) - 1:
                        finals.add(co[-1])

        # mistura os moldes da língua com os das palavras do usuário
        total = sum(counts.values())
        alpha = min(0.5, total / 40)
        mixed = {k: v * (1 - alpha) for k, v in rules["templates"].items()}
        for k, v in counts.items():
            mixed[k] = mixed.get(k, 0) + alpha * v / total
        # fecho: cada molde com coda implica o mesmo molde sem coda (CVC → CV, VC → V),
        # senão prefixos e sufixos curtos criariam sílabas que a língua não aceita
        for pat in list(mixed):
            open_pat = pat.rstrip("C")
            if open_pat not in mixed:
                mixed[open_pat] = 0.02
        s = sum(mixed.values())
        rules["templates"] = {k: round(v / s, 3) for k, v in sorted(mixed.items(), key=lambda x: -x[1])}
        rules["onsets"].update(clusters=[list(c) for c in sorted(onsets2)],
                               triple=[list(c) for c in sorted(onsets3)],
                               word_initial_forbidden=sorted(forbidden))
        rules["codas"].update(single=sorted(codas), word_final=sorted(finals),
                              clusters=[list(c) for c in sorted(coda2)])
        new_t = sorted(set(rules["templates"]) - before["templates"])
        if new_t:
            report["changes"].append("moldes novos: " + ", ".join(new_t))
        for label, old, new in (("encontros no ataque", before["o2"] | before["o3"], onsets2 | onsets3),
                                ("codas", {(c,) for c in before["codas"]}, {(c,) for c in codas}),
                                ("encontros em coda", before["coda2"], coda2)):
            diff = sorted(new - old)
            if diff:
                report["changes"].append(f"{label} novos: " + " ".join("".join(d) for d in diff))
        rules["metadata"]["notes"].append("regras adaptadas às palavras do usuário")
        rules["root"]["syllables"] = rules["root"]["syllables"]  # tamanho das raízes não muda

    eng = pht_mod.Phonotactics(rules, inventory)
    for w in words:
        w["valid"] = eng.is_valid(w["segments"])
        if not w["valid"]:
            report["exceptions"].append(w["form"])
    return report


# ═══════════════════════════════════════════════════════════════════════════
# Motor: palavras gramaticais do usuário
# ═══════════════════════════════════════════════════════════════════════════

def apply_function_words(morphology: Dict, categories: Dict, spec: Dict) -> List[str]:
    """'not', 'the', 'a/an' e 'one' (quando é também o artigo) substituem as formas sorteadas."""
    fm = morphology["free_markers"]
    notes = []
    for w in spec["words"]:
        for m in w["meanings"]:
            key = norm_meaning(m)
            target = FUNCTION_MEANINGS.get(key)
            if key == "one" and fm.get("definiteness", {}).get("realization", {}).get("indefinite") == "numeral_one":
                target = ("definiteness", "indefinite")
            if not target:
                continue
            cat, value = target
            if cat in fm and value in fm[cat]["forms"]:
                fm[cat]["forms"][value] = list(w["segments"])
                notes.append(f"'{m}' = {w['form']} (palavra gramatical do usuário)")
            else:
                real = categories["categories"].get(cat, {}).get("realization", "—")
                notes.append(f"'{m}' = {w['form']}: a gramática não marca '{value}' com uma palavra "
                             f"livre ({cat}: {real}); entra só no dicionário")
    return notes


# ═══════════════════════════════════════════════════════════════════════════
# Léxico: casamento com os conceitos
# ═══════════════════════════════════════════════════════════════════════════

def resolve_lexicon(spec: Dict, active: List[Dict], all_concepts: List[Dict]) -> Dict:
    """
    Liga cada palavra aos conceitos do Concepticon pelo significado em inglês.
    Uma palavra pode ter vários significados ('finger, toe'): ocupa todos.
    """
    index: Dict[str, List[Dict]] = {}
    for c in all_concepts:
        for k in concept_keys(c):
            index.setdefault(k, []).append(c)
    active_ids = {c["id"] for c in active}
    out: Dict = {"by_gloss": {}, "extra_concepts": [], "unmatched": [], "pronouns": {},
                 "function": [], "report": []}
    for w in spec["words"]:
        matched = []
        for m in w["meanings"]:
            key = norm_meaning(m)
            if key in PRONOUN_MEANINGS and w["section"] in ("other", "any"):
                cell, gloss = PRONOUN_MEANINGS[key]
                out["pronouns"][cell] = w
                matched.append(f"pronome {cell}")
                continue
            if key in FUNCTION_MEANINGS:
                out["function"].append(w)
                matched.append("palavra gramatical")
                continue
            cands = index.get(key, [])
            cat = SECTION_CATEGORY.get(w["section"])
            if cat:
                cands = [c for c in cands if c["category"] == cat] or cands
            if not cands:
                continue
            c = next((x for x in cands if x["id"] in active_ids), cands[0])
            if c["id"] not in active_ids and c not in out["extra_concepts"]:
                out["extra_concepts"].append(c)
            out["by_gloss"][c["gloss"]] = w
            matched.append(c["gloss"])
        if not matched:
            out["unmatched"].append(w)
        out["report"].append({"form": w["form"], "meaning": ", ".join(w["meanings"]),
                              "concepts": matched or ["(entrada nova)"],
                              "valid": w.get("valid", True)})
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Léxico: aplicação das palavras do usuário depois que o léxico é gerado
# ═══════════════════════════════════════════════════════════════════════════

USER_NOTE = "palavra do usuário ★"


def _as_skeleton(segs: List[str], consonants: Set[str]) -> Tuple[List[str], bool]:
    """
    Em línguas de raiz consonantal, a palavra do usuário vira esqueleto C1-C2-C3:
    as três primeiras consoantes (ou a última repetida, como no árabe m-d-d).
    """
    cons = [s for s in segs if s in consonants]
    if not cons:
        return segs, False
    while len(cons) < 3:
        cons.append(cons[-1])
    return cons[:3], True


def apply_to_lexicon(data: Dict, builder, resolved: Dict) -> List[str]:
    """
    Substitui no léxico já gerado as entradas dos conceitos do usuário, acrescenta
    as entradas novas, regera palavras geradas que ficaram idênticas às do usuário
    e refaz as formas flexionadas. Usa só funções públicas do LexiconBuilder.
    """
    notes: List[str] = []
    eng = builder.eng
    consonants = set(eng.cons)
    skeleton = eng.skeleton
    entries: List[Dict] = data["entries"]
    by_gloss = {e["gloss"]: e for e in entries}
    gender_vals = builder.gender.get("values", []) if builder.gender.get("grammaticalized") else []
    adj_verbal = data["settings"]["adjectives"] == "verbal"
    changed: List[Dict] = []

    user_words = (list(resolved["by_gloss"].values()) + resolved["unmatched"] +
                  list(resolved["pronouns"].values()) + resolved["function"])
    user_forms = {tuple(w["segments"]) for w in user_words}
    builder.used |= user_forms

    def set_form(e: Dict, w: Dict) -> None:
        segs = list(w["segments"])
        if skeleton and e["pos"] in ("noun", "verb"):
            segs, ok = _as_skeleton(segs, consonants)
            if ok:
                notes.append(f"'{w['form']}' virou a raiz consonantal {'-'.join(segs)} "
                             "(a língua forma palavras por padrões vocálicos)")
        e.update(root=segs, form="-".join(segs) if skeleton and e["pos"] in ("noun", "verb") else w["form"],
                 tones=[], formation="custom", custom=True, note=USER_NOTE)
        e.pop("parts", None)
        e.pop("colexified_with", None)
        changed.append(e)

    def complete(e: Dict, w: Dict, c_category: str) -> None:
        section = w["section"] if w["section"] != "any" else \
            {"N": "noun", "V": "verb", "A": "adjective"}.get(c_category, "other")
        if section == "noun":
            e["pos"] = "noun"
            g = w.get("gender")
            if g and g not in gender_vals:
                if gender_vals:
                    notes.append(f"gênero '{g}' de '{w['form']}' não existe na língua "
                                 f"({', '.join(gender_vals)}); mantido o atribuído automaticamente")
                g = None
            if gender_vals:
                e["gender"] = g or e.get("gender") or builder.assign_gender(
                    {"gloss": e["gloss"], "field": e.get("field", "")})
            if "class" not in e:
                e["class"] = builder.assign_class("noun", e.get("gender"))
        elif section in ("verb", "adjective") and (section == "verb" or adj_verbal):
            e["pos"] = "verb"
            e["transitivity"] = w.get("transitivity") or e.get("transitivity") or \
                ("stative" if section == "adjective" else "intransitive")
            if "class" not in e:
                e["class"] = builder.assign_class("verb", None)
        elif section == "adjective":
            e["pos"] = "adjective"
        elif section == "other" and w.get("pos"):
            e["pos"] = w["pos"]

    # 1. pronomes
    cells = data["pronouns"]["cells"]
    for cell, w in resolved["pronouns"].items():
        key = next((k for k in cells if k == cell), None) or \
            next((k for k in cells if k.startswith(cell + ".")), None) or \
            next((k for k in cells if cell.startswith(k)), None)
        if not key:
            notes.append(f"pronome '{w['form']}' ({cell}) não existe nesta língua; entra só no dicionário")
            resolved["unmatched"].append(w)
            continue
        cells[key] = {"segments": list(w["segments"]), "form": w["form"], "custom": True}
        for e in entries:
            if e.get("cell") == key:
                e.update(root=list(w["segments"]), form=w["form"], tones=[], formation="custom",
                         custom=True, note=USER_NOTE)
                changed.append(e)

    # 2. conceitos do usuário (e colexificações que partiam deles)
    for gloss, w in resolved["by_gloss"].items():
        e = by_gloss.get(gloss)
        if not e:
            continue
        cat = {"noun": "N", "verb": "V", "adjective": "A"}.get(e["pos"], "O")
        complete(e, w, cat)
        set_form(e, w)
        for other in entries:
            if other.get("colexified_with") == gloss:
                other.update(root=list(e["root"]), form=e["form"], tones=[])
                changed.append(other)

    # 3. palavras sem conceito e palavras gramaticais
    for w in resolved["unmatched"] + resolved["function"]:
        meaning = w["meanings"][0]
        if meaning.lower() in ("not", "no") and "NOT" in by_gloss:
            e = by_gloss["NOT"]
            e.update(root=list(w["segments"]), form=w["form"], formation="custom", custom=True,
                     note=USER_NOTE, citation=w["form"], inflections=[])
            continue
        e = {"id": f"custom-{w['line']}", "gloss": meaning.upper(), "english": ", ".join(w["meanings"]),
             "pos": "particle", "skeleton": False, "field": "Custom", "root": [], "form": "",
             "tones": [], "formation": "custom"}
        complete(e, w, {"verb": "V", "noun": "N", "adjective": "A"}.get(w["section"], "O"))
        set_form(e, w)
        entries.append(e)
        by_gloss[e["gloss"]] = e

    # 4. palavras geradas que coincidiram com palavras do usuário
    for e in entries:
        if e.get("custom") or e["formation"] != "root" or tuple(e["root"]) not in user_forms:
            continue
        old = e["form"]
        r = builder.content_root(None)
        e.update(root=r["segments"], form=r["form"], tones=r.get("tones", []))
        changed.append(e)
        notes.append(f"'{e['english']}' era igual a uma palavra do usuário ({old}); regerada")

    # 5. formas de citação e flexões
    for e in {id(x): x for x in changed}.values():
        builder._principal_parts(e)
    return notes
