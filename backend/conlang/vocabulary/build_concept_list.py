"""
Monta uma lista combinada de conceitos a partir do Concepticon.

Une as listas de conceitos mais usadas na linguística comparativa, que o
Concepticon mapeia para os mesmos identificadores, e grava um único arquivo no
formato do wold_1460.tsv (que o módulo de vocabulário lê com --list):

    swadesh          Swadesh (1952), 200 conceitos — o vocabulário básico clássico
    leipzig_jakarta  Tadmor (2009), 100 — os significados mais estáveis, com a ordem
    wold             Haspelmath & Tadmor (2009), 1.460 — vocabulário geral com classe,
                     campo semântico e pontuações
    ids              Key & Comrie (2016), 1.310 — Intercontinental Dictionary Series,
                     o padrão para vocabulário geral comparado (com glosas em português)
    northeuralex     Dellert et al. (2017), 1.016 — vocabulário comparado da Eurásia

Cada conceito aparece uma vez. Além das colunas do formato do WOLD, o arquivo
traz em quais listas o conceito aparece, a posição na Leipzig-Jakarta e a glosa
em português (do IDS), quando houver.

Uso:
    python vocabulary/build_concept_list.py                       # baixa do GitHub do Concepticon
    python vocabulary/build_concept_list.py --concepticon ../concepticon-data   # clone local
    python vocabulary/build_concept_list.py --lists wold,ids --out vocabulary/geral.tsv

Depois:
    python vocabulary/vocabulary.py --language languages/lang-31 --list vocabulary/concepts.tsv

Requer apenas a biblioteca padrão (Python ≥ 3.9) e, sem --concepticon, acesso à internet.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/concepticon/concepticon-data/master/concepticondata"

# nome curto → arquivo no Concepticon, em ordem de prioridade (quem vem antes define inglês e classe)
LISTS = {
    "swadesh": "Swadesh-1952-200",
    "leipzig_jakarta": "Tadmor-2009-100",
    "wold": "Haspelmath-2009-1460",
    "ids": "Key-2016-1310",
    "northeuralex": "Dellert-2017-1016",
}
DESCRIPTION = {
    "swadesh": "Swadesh (1952), 200 conceitos",
    "leipzig_jakarta": "Tadmor, Haspelmath & Taylor (2010), lista Leipzig-Jakarta, 100 conceitos",
    "wold": "Haspelmath & Tadmor (2009), World Loanword Database, 1.460 conceitos",
    "ids": "Key & Comrie (2016), Intercontinental Dictionary Series, 1.310 conceitos",
    "northeuralex": "Dellert et al. (2017), NorthEuraLex, 1.016 conceitos",
}

# Campos semânticos do WOLD (os mesmos nomes do Concepticon) → número usado pelo módulo de vocabulário
WOLD_FIELDS = {
    "The physical world": "1", "Kinship": "2", "Animals": "3", "The body": "4", "Food and drink": "5",
    "Clothing and grooming": "6", "The house": "7", "Agriculture and vegetation": "8",
    "Basic actions and technology": "9", "Motion": "10", "Possession": "11", "Spatial relations": "12",
    "Quantity": "13", "Time": "14", "Sense perception": "15", "Emotions and values": "16", "Cognition": "17",
    "Speech and language": "18", "Social and political relations": "19", "Warfare and hunting": "20",
    "Law": "21", "Religion and belief": "22", "Modern world": "23", "Miscellaneous function words": "24",
}
# Categoria ontológica do Concepticon → classe de palavra
ONTOLOGY_POS = {"Person/Thing": "Noun", "Action/Process": "Verb", "Property": "Adjective",
                "Number": "Function word", "Other": "Function word"}
# Classe do NorthEuraLex ('Auge::N') → classe de palavra
NELEX_POS = {"N": "Noun", "V": "Verb", "A": "Adjective", "ADV": "Adverb"}

COLUMNS = ["NUMBER", "CONCEPTICON_ID", "CONCEPTICON_GLOSS", "ENGLISH", "PART_OF_SPEECH", "SEMANTIC_FIELD",
           "SIMPLICITY_SCORE", "AGE_SCORE", "PORTUGUESE", "LISTS", "N_LISTS", "LEIPZIG_JAKARTA_RANK"]


def read_tsv(name: str, local: Optional[Path]) -> List[Dict[str, str]]:
    """Lê uma lista do Concepticon (clone local ou GitHub)."""
    if local:
        path = local / "concepticondata" / f"{name}.tsv"
        if not path.exists():
            path = local / f"{name}.tsv"
        text = path.read_text(encoding="utf-8")
    else:
        url = f"{RAW}/{name}.tsv"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                text = r.read().decode("utf-8")
        except Exception as ex:  # noqa: BLE001
            raise SystemExit(f"Não consegui baixar {url}: {ex}\n"
                             "Sem internet, clone o repositório concepticon-data e use --concepticon.")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def build(lists: List[str], local: Optional[Path], log=print) -> List[Dict[str, str]]:
    log("Lendo o catálogo do Concepticon...")
    catalog = {r["ID"]: r for r in read_tsv("concepticon", local)}
    concepts: Dict[str, Dict] = {}
    for short in lists:
        rows = read_tsv(f"conceptlists/{LISTS[short]}", local)
        n = 0
        for r in rows:
            cid = (r.get("CONCEPTICON_ID") or "").strip()
            if not cid:
                continue
            c = concepts.setdefault(cid, {"CONCEPTICON_ID": cid, "lists": [], "order": len(concepts)})
            if short in c["lists"]:
                continue
            c["lists"].append(short)
            n += 1
            c.setdefault("CONCEPTICON_GLOSS", r.get("CONCEPTICON_GLOSS") or catalog.get(cid, {}).get("GLOSS", ""))
            if short == "wold":  # o WOLD tem classe, campo e pontuações próprios: tem prioridade
                c["ENGLISH"] = r.get("ENGLISH") or c.get("ENGLISH")
                c["PART_OF_SPEECH"] = r.get("PART_OF_SPEECH") or c.get("PART_OF_SPEECH")
                c["SEMANTIC_FIELD"] = r.get("SEMANTIC_FIELD") or c.get("SEMANTIC_FIELD")
                c["SIMPLICITY_SCORE"] = r.get("SIMPLICITY_SCORE") or ""
                c["AGE_SCORE"] = r.get("AGE_SCORE") or ""
            if short == "leipzig_jakarta":
                c["LEIPZIG_JAKARTA_RANK"] = r.get("RANK") or ""
            if short == "ids":
                c["PORTUGUESE"] = (r.get("PORTUGUESE") or "").strip()
                c.setdefault("ids_chapter", r.get("CHAPTER"))
            if short == "northeuralex":
                pos = (r.get("NELEX_ID") or "").split("::")[-1]
                c.setdefault("nelex_pos", NELEX_POS.get(pos))
            c.setdefault("ENGLISH", r.get("ENGLISH") or "")
        log(f"  {short:<16} {n:>5} conceitos  ({DESCRIPTION[short]})")

    out = []
    for c in sorted(concepts.values(), key=lambda x: x["order"]):
        cat = catalog.get(c["CONCEPTICON_ID"], {})
        field = c.get("SEMANTIC_FIELD") or WOLD_FIELDS.get(cat.get("SEMANTICFIELD", ""), "") or (c.get("ids_chapter") or "")
        pos = c.get("PART_OF_SPEECH") or c.get("nelex_pos") or ONTOLOGY_POS.get(cat.get("ONTOLOGICAL_CATEGORY", ""), "Noun")
        english = (c.get("ENGLISH") or cat.get("GLOSS", "").lower()).strip()
        if pos == "Verb" and not english.startswith("to "):
            english = "to " + english  # mesmo formato do WOLD ('to bite')
        out.append({
            "CONCEPTICON_ID": c["CONCEPTICON_ID"], "CONCEPTICON_GLOSS": c["CONCEPTICON_GLOSS"], "ENGLISH": english,
            "PART_OF_SPEECH": pos, "SEMANTIC_FIELD": field or "24",
            "SIMPLICITY_SCORE": c.get("SIMPLICITY_SCORE", ""), "AGE_SCORE": c.get("AGE_SCORE", ""),
            "PORTUGUESE": c.get("PORTUGUESE", ""), "LISTS": ",".join(c["lists"]), "N_LISTS": str(len(c["lists"])),
            "LEIPZIG_JAKARTA_RANK": c.get("LEIPZIG_JAKARTA_RANK", ""),
        })
    for i, r in enumerate(out, 1):
        r["NUMBER"] = str(i)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Monta uma lista combinada de conceitos a partir do Concepticon.")
    ap.add_argument("--lists", default=",".join(LISTS),
                    help=f"listas a unir, separadas por vírgula (padrão: todas: {', '.join(LISTS)})")
    ap.add_argument("--concepticon", type=Path, help="clone local do concepticon-data (sem internet)")
    ap.add_argument("--out", type=Path, default=HERE / "concepts.tsv", help="arquivo de saída")
    args = ap.parse_args()

    lists = [x.strip() for x in args.lists.split(",") if x.strip()]
    bad = [x for x in lists if x not in LISTS]
    if bad:
        sys.exit(f"Listas desconhecidas: {', '.join(bad)}. Opções: {', '.join(LISTS)}")
    rows = build(lists, args.concepticon)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    by_n = Counter(int(r["N_LISTS"]) for r in rows)
    pos = Counter(r["PART_OF_SPEECH"] for r in rows)
    pt = sum(1 for r in rows if r["PORTUGUESE"])
    print(f"\n{len(rows)} conceitos únicos em '{args.out}'")
    print("  em quantas listas aparecem: " + ", ".join(f"{k} lista(s): {by_n[k]}" for k in sorted(by_n, reverse=True)))
    print("  classes: " + ", ".join(f"{k}: {v}" for k, v in pos.most_common()))
    print(f"  com glosa em português (IDS): {pt}")
    print(f"\nPara usar: python vocabulary/vocabulary.py --language languages/<língua> --list {args.out}")


if __name__ == "__main__":
    main()
