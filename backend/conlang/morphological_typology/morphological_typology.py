"""
Módulo 2 — Tipologia Morfológica.

Define *como* a morfologia da conlang funciona (síntese, fusão, posição dos
afixos, processos e locus de marcação). O *conteúdo* gramatical (número, caso,
tempo, aspecto...) fica em um módulo separado.

Requer: pydantic >= 2
Uso:
    python morphological_typology.py                 # assistente interativo
    python morphological_typology.py --random        # sorteio ponderado
    python morphological_typology.py --random --seed 42 -o minha_lingua.json
"""

from __future__ import annotations

import argparse
import random
import warnings
from enum import Enum
from typing import Dict, List, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator


# ═══════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════

class DegreeOfSynthesis(str, Enum):
    """Índice de síntese: quantos morfemas cabem em uma palavra."""
    ISOLATING = "isolating"          # ~1 morfema/palavra (Mandarim, Vietnamita)
    SYNTHETIC = "synthetic"          # Raiz + vários afixos (Latim, Turco, Português)
    POLYSYNTHETIC = "polysynthetic"  # Sentença em uma palavra (Inuktitut, Mohawk)


class DegreeOfFusion(str, Enum):
    """Índice de fusão: como se comportam as fronteiras entre morfemas."""
    NONE = "none"                    # Só para línguas isolantes
    AGGLUTINATIVE = "agglutinative"  # 1 morfema = 1 traço; fronteiras nítidas (Turco)
    FUSIONAL = "fusional"            # 1 morfema = N traços; fronteiras borradas (Latim)


class AffixPosition(str, Enum):
    """Preferência prefixo vs. sufixo, alinhada ao WALS 26A."""
    LITTLE_AFFIXATION = "little_affixation"
    STRONGLY_SUFFIXING = "strongly_suffixing"
    WEAKLY_SUFFIXING = "weakly_suffixing"
    EQUAL = "equal"
    WEAKLY_PREFIXING = "weakly_prefixing"
    STRONGLY_PREFIXING = "strongly_prefixing"

    @property
    def is_suffixing(self) -> bool:
        return self in {AffixPosition.STRONGLY_SUFFIXING, AffixPosition.WEAKLY_SUFFIXING}

    @property
    def is_prefixing(self) -> bool:
        return self in {AffixPosition.STRONGLY_PREFIXING, AffixPosition.WEAKLY_PREFIXING}


class MorphologicalProcess(str, Enum):
    """Processos produtivos de formação de palavras."""
    AFFIXATION = "affixation"                        # Raiz + afixo (prefixo/sufixo)
    INFIXATION = "infixation"                        # Afixo inserido na raiz (Tagalo)
    CIRCUMFIXATION = "circumfixation"                # Afixo bipartido (ge-...-t, Alemão)
    TRANSFIXATION = "transfixation"                  # Raiz-e-padrão (k-t-b → kataba, Árabe)
    COMPOUNDING = "compounding"                      # Raiz + raiz
    NOUN_INCORPORATION = "noun_incorporation"        # Nome incorporado ao verbo
    REDUPLICATION_FULL = "reduplication_full"        # Repetição total (orang-orang)
    REDUPLICATION_PARTIAL = "reduplication_partial"  # Repetição de sílaba/segmento
    APOPHONY = "apophony"                            # Alternância interna (sing → sang)
    TONAL_MORPHOLOGY = "tonal_morphology"            # Tom com função gramatical


class LocusOfMarking(str, Enum):
    """Onde as relações gramaticais são marcadas (WALS 23A–25A)."""
    HEAD_MARKING = "head_marking"
    DEPENDENT_MARKING = "dependent_marking"
    DOUBLE_MARKING = "double_marking"
    NO_MARKING = "no_marking"


# Processos que pressupõem morfemas presos (incompatíveis com isolamento estrito)
BOUND_PROCESSES = {
    MorphologicalProcess.AFFIXATION,
    MorphologicalProcess.INFIXATION,
    MorphologicalProcess.CIRCUMFIXATION,
    MorphologicalProcess.TRANSFIXATION,
    MorphologicalProcess.NOUN_INCORPORATION,
}


# ═══════════════════════════════════════════════════════════════════════════
# Modelo de configuração
# ═══════════════════════════════════════════════════════════════════════════

class MorphologicalTypologyConfig(BaseModel):
    """
    Especificação formal da tipologia morfológica.

    Contradições lógicas geram ValueError; combinações apenas raras
    geram UserWarning (permitidas, pois conlangs podem ser exóticas).
    """

    degree_of_synthesis: DegreeOfSynthesis
    degree_of_fusion: DegreeOfFusion
    affix_position: AffixPosition = AffixPosition.STRONGLY_SUFFIXING
    active_processes: List[MorphologicalProcess] = Field(
        default_factory=lambda: [MorphologicalProcess.AFFIXATION,
                                 MorphologicalProcess.COMPOUNDING]
    )
    locus_of_marking: LocusOfMarking = LocusOfMarking.DEPENDENT_MARKING

    # ── Normalização ──────────────────────────────────────────────────────
    @field_validator("active_processes")
    @classmethod
    def _deduplicate(cls, v: List[MorphologicalProcess]) -> List[MorphologicalProcess]:
        return list(dict.fromkeys(v))

    # ── Regras de consistência ────────────────────────────────────────────
    @model_validator(mode="after")
    def _check_consistency(self) -> "MorphologicalTypologyConfig":
        syn, fus, procs = self.degree_of_synthesis, self.degree_of_fusion, set(self.active_processes)
        isolating = syn == DegreeOfSynthesis.ISOLATING

        # Erros: contradições lógicas
        if isolating != (fus == DegreeOfFusion.NONE):
            raise ValueError("Fusão 'none' deve ocorrer se e somente se a língua for isolante.")

        if isolating:
            if procs & BOUND_PROCESSES:
                bad = ", ".join(sorted(p.value for p in procs & BOUND_PROCESSES))
                raise ValueError(f"Língua isolante não admite morfemas presos: {bad}.")
            if self.affix_position != AffixPosition.LITTLE_AFFIXATION:
                raise ValueError("Língua isolante exige affix_position = 'little_affixation'.")
        else:
            if not procs & {MorphologicalProcess.AFFIXATION, MorphologicalProcess.TRANSFIXATION}:
                raise ValueError("Língua sintética precisa de afixação ou transfixação.")
            if self.affix_position == AffixPosition.LITTLE_AFFIXATION:
                raise ValueError("'little_affixation' só é válido para línguas isolantes.")

        if syn == DegreeOfSynthesis.POLYSYNTHETIC and MorphologicalProcess.NOUN_INCORPORATION not in procs:
            raise ValueError("Polissíntese requer incorporação nominal.")

        if procs & {MorphologicalProcess.INFIXATION, MorphologicalProcess.CIRCUMFIXATION} \
                and MorphologicalProcess.AFFIXATION not in procs:
            raise ValueError("Infixação/circunfixação pressupõem afixação ativa.")

        # Avisos: combinações tipologicamente raras
        if MorphologicalProcess.TRANSFIXATION in procs and fus == DegreeOfFusion.AGGLUTINATIVE:
            warnings.warn("Transfixação com fusão aglutinante é rara (o padrão é fusional).")
        if syn == DegreeOfSynthesis.POLYSYNTHETIC and self.locus_of_marking == LocusOfMarking.DEPENDENT_MARKING:
            warnings.warn("Línguas polissintéticas tendem fortemente à marcação no núcleo.")
        if isolating and self.locus_of_marking != LocusOfMarking.NO_MARKING:
            warnings.warn("Línguas isolantes raramente têm marcação morfológica de relações.")

        return self

    # ── Interface com outros módulos ──────────────────────────────────────
    def phonotactics_requirements(self) -> Dict[str, object]:
        """O que este perfil exige do módulo de fonotática."""
        procs = set(self.active_processes)
        req: Dict[str, object] = {}
        if MorphologicalProcess.TRANSFIXATION in procs:
            req["root_shape"] = "consonantal_skeleton"  # ex: CCC
        if MorphologicalProcess.TONAL_MORPHOLOGY in procs:
            req["tone"] = True
        if MorphologicalProcess.APOPHONY in procs:
            req["vowel_alternation_sets"] = True
        if self.degree_of_synthesis == DegreeOfSynthesis.ISOLATING:
            req["max_root_syllables"] = 2
        return req

    def syntax_hints(self) -> Dict[str, str]:
        """Tendências translinguísticas para o módulo de sintaxe (não obrigatórias)."""
        hints: Dict[str, str] = {}
        if self.affix_position.is_suffixing:
            hints["word_order"] = "OV (sufixação correlaciona com verbo final)"
        elif self.affix_position.is_prefixing:
            hints["word_order"] = "VO (prefixação correlaciona com verbo inicial/medial)"
        if self.locus_of_marking == LocusOfMarking.HEAD_MARKING:
            hints["pro_drop"] = "provável (argumentos já marcados no verbo)"
        if self.degree_of_synthesis == DegreeOfSynthesis.ISOLATING:
            hints["word_order_rigidity"] = "alta (ordem carrega a função gramatical)"
        return hints


# ═══════════════════════════════════════════════════════════════════════════
# Sorteio ponderado
# ═══════════════════════════════════════════════════════════════════════════
# Pesos aproximados e ilustrativos. AFFIX_POSITION_WEIGHTS segue a ordem de
# grandeza do WALS 26A; recalibre os demais com os CSVs do WALS (20A–26A).

SYNTHESIS_WEIGHTS = {DegreeOfSynthesis.ISOLATING: 0.15,
                     DegreeOfSynthesis.SYNTHETIC: 0.70,
                     DegreeOfSynthesis.POLYSYNTHETIC: 0.15}

FUSION_WEIGHTS = {DegreeOfFusion.AGGLUTINATIVE: 0.60,
                  DegreeOfFusion.FUSIONAL: 0.40}

AFFIX_POSITION_WEIGHTS = {AffixPosition.STRONGLY_SUFFIXING: 0.49,
                          AffixPosition.WEAKLY_SUFFIXING: 0.15,
                          AffixPosition.EQUAL: 0.18,
                          AffixPosition.WEAKLY_PREFIXING: 0.11,
                          AffixPosition.STRONGLY_PREFIXING: 0.07}

LOCUS_WEIGHTS = {
    DegreeOfSynthesis.SYNTHETIC: {LocusOfMarking.DEPENDENT_MARKING: 0.40,
                                  LocusOfMarking.HEAD_MARKING: 0.25,
                                  LocusOfMarking.DOUBLE_MARKING: 0.35},
    DegreeOfSynthesis.POLYSYNTHETIC: {LocusOfMarking.HEAD_MARKING: 0.75,
                                      LocusOfMarking.DOUBLE_MARKING: 0.25},
}

OPTIONAL_PROCESS_PROB = {
    MorphologicalProcess.REDUPLICATION_FULL: 0.30,
    MorphologicalProcess.REDUPLICATION_PARTIAL: 0.25,
    MorphologicalProcess.APOPHONY: 0.10,
    MorphologicalProcess.INFIXATION: 0.05,
    MorphologicalProcess.CIRCUMFIXATION: 0.05,
    MorphologicalProcess.TRANSFIXATION: 0.03,
    MorphologicalProcess.TONAL_MORPHOLOGY: 0.08,
}

E = TypeVar("E")


def _weighted(rng: random.Random, weights: Dict[E, float]) -> E:
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def sample_config(seed: Optional[int] = None) -> MorphologicalTypologyConfig:
    """Gera um perfil morfológico aleatório e tipologicamente plausível."""
    rng = random.Random(seed)
    synthesis = _weighted(rng, SYNTHESIS_WEIGHTS)

    if synthesis == DegreeOfSynthesis.ISOLATING:
        procs = [MorphologicalProcess.COMPOUNDING]
        for p in (MorphologicalProcess.REDUPLICATION_FULL, MorphologicalProcess.TONAL_MORPHOLOGY):
            if rng.random() < 0.4:
                procs.append(p)
        return MorphologicalTypologyConfig(
            degree_of_synthesis=synthesis,
            degree_of_fusion=DegreeOfFusion.NONE,
            affix_position=AffixPosition.LITTLE_AFFIXATION,
            active_processes=procs,
            locus_of_marking=LocusOfMarking.NO_MARKING,
        )

    fusion = _weighted(rng, FUSION_WEIGHTS)
    procs = [MorphologicalProcess.AFFIXATION, MorphologicalProcess.COMPOUNDING]
    if synthesis == DegreeOfSynthesis.POLYSYNTHETIC:
        procs.append(MorphologicalProcess.NOUN_INCORPORATION)
    for proc, prob in OPTIONAL_PROCESS_PROB.items():
        if proc == MorphologicalProcess.TRANSFIXATION and fusion != DegreeOfFusion.FUSIONAL:
            continue
        if rng.random() < prob:
            procs.append(proc)

    return MorphologicalTypologyConfig(
        degree_of_synthesis=synthesis,
        degree_of_fusion=fusion,
        affix_position=_weighted(rng, AFFIX_POSITION_WEIGHTS),
        active_processes=procs,
        locus_of_marking=_weighted(rng, LOCUS_WEIGHTS[synthesis]),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Assistente interativo
# ═══════════════════════════════════════════════════════════════════════════

def _ask_choice(title: str, options: Sequence[tuple[E, str]], default: int = 1) -> E:
    print(f"\n{title}")
    for i, (_, label) in enumerate(options, 1):
        print(f"  {i} - {label}")
    while True:
        raw = input(f"Opção (1-{len(options)}) [{default}]: ").strip()
        if not raw:
            return options[default - 1][0]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print("  ! Opção inválida, tente novamente.")


def _ask_yes_no(question: str, default: bool = False) -> bool:
    hint = "S/n" if default else "s/N"
    while True:
        raw = input(f"  {question} ({hint}): ").strip().lower()
        if not raw:
            return default
        if raw in {"s", "sim", "y", "yes"}:
            return True
        if raw in {"n", "nao", "não", "no"}:
            return False
        print("  ! Responda 's' ou 'n'.")


def run_cli() -> MorphologicalTypologyConfig:
    print("\n" + "=" * 56)
    print("  DEFINIÇÃO DE TIPOLOGIA MORFOLÓGICA")
    print("=" * 56)

    synthesis = _ask_choice("[1] GRAU DE SÍNTESE", [
        (DegreeOfSynthesis.ISOLATING, "Isolante      (~1 morfema; palavras invariáveis)"),
        (DegreeOfSynthesis.SYNTHETIC, "Sintética     (raiz + múltiplos afixos)"),
        (DegreeOfSynthesis.POLYSYNTHETIC, "Polissintética (sentenças em uma palavra)"),
    ], default=2)

    if synthesis == DegreeOfSynthesis.ISOLATING:
        procs = [MorphologicalProcess.COMPOUNDING]
        print("\n[2] PROCESSOS (língua isolante: sem afixos)")
        if _ask_yes_no("Reduplicação total (ex: plural/intensidade)?", True):
            procs.append(MorphologicalProcess.REDUPLICATION_FULL)
        if _ask_yes_no("Tom com função gramatical?"):
            procs.append(MorphologicalProcess.TONAL_MORPHOLOGY)
        return MorphologicalTypologyConfig(
            degree_of_synthesis=synthesis,
            degree_of_fusion=DegreeOfFusion.NONE,
            affix_position=AffixPosition.LITTLE_AFFIXATION,
            active_processes=procs,
            locus_of_marking=LocusOfMarking.NO_MARKING,
        )

    fusion = _ask_choice("[2] GRAU DE FUSÃO", [
        (DegreeOfFusion.AGGLUTINATIVE, "Aglutinante (1 morfema = 1 traço; ex: Turco)"),
        (DegreeOfFusion.FUSIONAL, "Fusional    (afixos com múltiplos traços; ex: Latim)"),
    ], default=1)

    affix_pos = _ask_choice("[3] POSIÇÃO DOS AFIXOS (WALS 26A)", [
        (AffixPosition.STRONGLY_SUFFIXING, "Fortemente sufixante (mais comum)"),
        (AffixPosition.WEAKLY_SUFFIXING, "Fracamente sufixante"),
        (AffixPosition.EQUAL, "Equilibrado"),
        (AffixPosition.WEAKLY_PREFIXING, "Fracamente prefixante"),
        (AffixPosition.STRONGLY_PREFIXING, "Fortemente prefixante (ex: muitas línguas Bantu)"),
    ], default=1)

    default_locus = 2 if synthesis == DegreeOfSynthesis.POLYSYNTHETIC else 1
    locus = _ask_choice("[4] LOCUS DE MARCAÇÃO", [
        (LocusOfMarking.DEPENDENT_MARKING, "No dependente (casos nos nomes)"),
        (LocusOfMarking.HEAD_MARKING, "No núcleo     (concordância no verbo)"),
        (LocusOfMarking.DOUBLE_MARKING, "Dupla marcação"),
    ], default=default_locus)

    procs = [MorphologicalProcess.AFFIXATION, MorphologicalProcess.COMPOUNDING]
    if synthesis == DegreeOfSynthesis.POLYSYNTHETIC:
        procs.append(MorphologicalProcess.NOUN_INCORPORATION)
        print("\n> Incorporação nominal ativada (obrigatória em polissíntese).")

    print("\n[5] PROCESSOS ADICIONAIS")
    optional = [
        (MorphologicalProcess.REDUPLICATION_FULL, "Reduplicação total?"),
        (MorphologicalProcess.REDUPLICATION_PARTIAL, "Reduplicação parcial?"),
        (MorphologicalProcess.INFIXATION, "Infixação?"),
        (MorphologicalProcess.CIRCUMFIXATION, "Circunfixação?"),
        (MorphologicalProcess.APOPHONY, "Apofonia (sing → sang)?"),
        (MorphologicalProcess.TONAL_MORPHOLOGY, "Tom com função gramatical?"),
    ]
    if fusion == DegreeOfFusion.FUSIONAL:
        optional.append((MorphologicalProcess.TRANSFIXATION, "Transfixação / raiz-e-padrão (Árabe)?"))
    for proc, question in optional:
        if _ask_yes_no(question):
            procs.append(proc)

    return MorphologicalTypologyConfig(
        degree_of_synthesis=synthesis,
        degree_of_fusion=fusion,
        affix_position=affix_pos,
        active_processes=procs,
        locus_of_marking=locus,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Entrada
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Configura a tipologia morfológica da conlang.")
    parser.add_argument("-o", "--output", default="morphological_typology.json")
    parser.add_argument("--random", action="store_true", help="sorteia um perfil em vez de perguntar")
    parser.add_argument("--seed", type=int, default=None, help="semente para reprodutibilidade")
    args = parser.parse_args()

    config = sample_config(args.seed) if args.random else run_cli()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print("\n" + config.model_dump_json(indent=2))
    if req := config.phonotactics_requirements():
        print(f"\n→ Requisitos para a fonotática: {req}")
    if hints := config.syntax_hints():
        print(f"→ Sugestões para a sintaxe:     {hints}")
    print(f"\n[OK] Configuração salva em '{args.output}'.")


if __name__ == "__main__":
    main()
