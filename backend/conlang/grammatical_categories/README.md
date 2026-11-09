# Módulo — Categorias Gramaticais

Este módulo define o **espaço morfossemântico** da conlang: quais categorias gramaticais existem, quais valores contrastam, como cada uma é realizada, quais se fundem num único afixo e em que ordem os afixos aparecem. É o "o quê" que complementa o "como" da tipologia morfológica.

```
morphological_typology.json ──┐
                              ├──► CATEGORIAS GRAMATICAIS ──► grammatical_categories.json
WALS (opcional) ──────────────┘    (este módulo)                       │
                                                                       ▼
                         phonotactics.json ──────────────────► Motor morfológico
```

---

## Princípios

### 1. Categoria ≠ realização

A **categoria** é o contraste semântico (perfectivo vs. imperfectivo); a **realização** é a forma que ele assume (sufixo, partícula, mudança de raiz...). Assim, uma língua isolante pode ter aspecto expresso por partículas, como o mandarim, sem contradizer a tipologia.

| Realização | Exemplo | Linear? |
|---|---|---|
| `affix` | turco *ev-ler* | Sim (slot no molde) |
| `clitic` | posposições clíticas | Sim (slot no molde) |
| `particle` | mandarim *le* (perfectivo) | Não (palavra livre) |
| `auxiliary` | inglês *will* | Não (palavra livre) |
| `article` / `demonstrative_article` / `numeral_one` | português *o*, *um* | Não (palavra livre) |
| `word` | classificadores numerais | Não (palavra livre) |
| `stem_change` | inglês *sing → sang* | Não linear |
| `tone` | plural por tom | Não linear |
| `reduplication` | malaio *orang-orang* | Não linear |
| `transfix` | árabe *kataba / yaktubu* | Não linear |
| `agreement_only` | gênero visível só na concordância | — |

### 2. Marcas zero

Os valores não marcados normalmente não têm afixo: singular, nominativo/absolutivo, presente, indicativo, afirmativo, 3ª pessoa do singular. Cada categoria indica em `zero` quais valores são Ø. Sem isso, o motor morfológico geraria afixos para tudo.

### 3. Cumulação

Em línguas aglutinantes, cada categoria ocupa seu próprio slot (`ROOT-number-case`). Em línguas fusionais, categorias se fundem num único afixo (`ROOT-number+case`), e o motor gera uma forma para cada combinação de valores, como o latim *-ōrum* (genitivo × plural).

### 4. Ordem dos afixos

Categorias mais relevantes para o significado da raiz ficam mais perto dela:

| Domínio | Da raiz para fora | Fonte |
|---|---|---|
| Verbo | concordância P → aspecto → tempo → modo → evidencialidade → concordância A | Bybee (1985) |
| Nome | gênero/classe → número → definitude → caso | Greenberg, universal 39 |

A negação é sorteada como interna (perto da raiz, como no turco *gel-me-di-m*) ou externa (como o suaíli *ha-*).

---

## Entradas

| Arquivo | Obrigatório | Uso |
|---|---|---|
| `../morphological_typology/morphological_typology.json` | Recomendado | Síntese, fusão, locus, posição dos afixos e processos ativos |
| `../wals/cldf/values.csv` | Não | Distribuições atualizadas do WALS |

Sem a tipologia, o módulo assume uma língua sintética, aglutinante, fortemente sufixante e de marcação no dependente. Usa apenas a biblioteca padrão do Python (≥ 3.9).

### Uso do WALS

Com a pasta `../wals/cldf/` presente, todas as probabilidades são calculadas diretamente do `values.csv`. Sem ela, o módulo usa contagens extraídas do WALS e embutidas no código; o resultado é praticamente o mesmo. Algumas distribuições são **condicionais**, o que mantém as correlações reais entre features:

| Sorteio | Condicionado a | Exemplo da correlação |
|---|---|---|
| Nº de casos (49A) | Prefixação vs. sufixação (26A) | 84% das línguas de pouca afixação não têm caso |
| Marcação de pessoa no verbo (102A) | Prefixação vs. sufixação (26A) | Línguas prefixantes quase sempre marcam A e P |
| Alinhamento do caso (98A) | Ter caso (49A) | Entre línguas com caso, o ergativo sobe para ~30% |
| Alinhamento da concordância (100A) | Argumentos marcados (102A) | — |

O que o WALS não cobre é marcado no JSON como aproximação, com a referência (dual, trial, paucal, irrealis, realização da evidencialidade).

---

## Categorias

### Nome

| Categoria | WALS | Valores possíveis |
|---|---|---|
| **Número** | 33A, 34A | singular, plural; + dual (15%), trial (10% dos que têm dual), paucal (5%). Escopo: todos os nomes ou só humanos; obrigatório ou opcional |
| **Caso** | 49A, 98A, 51A | Casos centrais pelo alinhamento + oblíquos pela hierarquia de casos (genitivo e dativo primeiro) |
| **Gênero / classe nominal** | 30A, 31A, 32A | 2–4 gêneros (sexuais ou de animacidade) ou 5–10 classes nominais com núcleos semânticos |
| **Definitude** | 37A, 38A | Marcadores definido e/ou indefinido: artigo, demonstrativo, numeral "um" ou afixo |
| **Classificadores** | 55A | 4–10 classificadores numerais (sempre com um geral), opcionais ou obrigatórios |

**Alinhamento e casos centrais:**

| Alinhamento | Casos centrais | Marca zero |
|---|---|---|
| `neutral` | direct | direct |
| `nominative_accusative` | nominative, accusative | nominative |
| `marked_nominative` | nominative, accusative | accusative |
| `ergative_absolutive` | absolutive, ergative | absolutive |
| `tripartite` | intransitive (S), ergative (A), accusative (P) | intransitive |
| `active_inactive` | agentive, patientive | patientive |

O alinhamento neutro com vários casos é possível e frequente no WALS: os argumentos centrais ficam sem marca e só os oblíquos têm caso.

### Verbo

| Categoria | WALS | Valores possíveis |
|---|---|---|
| **Tempo** | 66A, 67A | passado/não passado, futuro/não futuro ou presente/passado/futuro; passado dividido em 2–4 graus de remoção (recente, hodierno, hesterno, remoto...) |
| **Aspecto** | 65A | perfectivo, imperfectivo; + progressivo (25%), habitual (15%) |
| **Modo** | 70A, 73A, 74A | indicativo + imperativo, optativo, potencial, irrealis |
| **Evidencialidade** | 77A | só indireta (direto/indireto ou direto/inferencial/reportativo) ou direta e indireta (até visual/não visual/inferencial/reportativo) |
| **Negação** | 112A | afirmativo, negativo; por afixo, partícula, auxiliar ou dupla (partícula + afixo) |
| **Concordância** | 102A, 100A, 39A | Argumentos marcados (A, P, ambos ou hierárquico), alinhamento, pessoas 1/2/3, clusividade, números |

Partículas de negação ficam antes do verbo em 75% dos casos (princípio Neg-first, Dahl 1979). A concordância pode codificar pessoa e número num só afixo (`cumulative`) ou em afixos separados (`separate`, 25% das línguas aglutinantes).

---

## Efeitos da tipologia morfológica

| Na tipologia | Efeito |
|---|---|
| `isolating` | Sem caso e sem concordância; gênero quase nunca; classificadores muito mais prováveis; todo afixo vira partícula; mais chance de não ter tempo nem plural |
| `head_marking` | Concordância com A e P mais provável; caso menos provável |
| `dependent_marking` | Caso mais provável; concordância menos provável |
| `polysynthetic` | Concordância com A e P quase obrigatória |
| `affix_position` | Define a chance de cada categoria ser prefixo ou sufixo. O caso continua fortemente sufixal mesmo em línguas prefixantes; a concordância tende mais a prefixo |
| `apophony` | Plural e passado podem ser feitos por mudança de raiz |
| `tonal_morphology` | Plural e tempo/aspecto podem ser tonais |
| `reduplication_*` | Plural e aspecto podem ser feitos por reduplicação |
| `transfixation` | Aspecto (70%) e tempo (30%) feitos por padrão vocálico, como no árabe |

---

## Cumulação

| Situação | Pacote | Probabilidade |
|---|---|---|
| Classes nominais pareadas com número (estilo bantu), qualquer fusão | gênero × número | 70% das línguas com 5+ classes |
| Fusional, número e caso afixais | número × caso | 85% |
| Fusional, com gênero afixal | gênero × número × caso | 50% dos casos acima |
| Fusional, definitude afixal | entra no pacote nominal | 30% |
| Fusional, 2+ categorias de TAM afixais | aspecto × tempo × modo | 70% |
| Fusional, com concordância A afixal | TAM × concordância A (latim *-ō*) | 50% dos casos acima |
| Aglutinante | aspecto × tempo | 15% |
| Isolante | nenhum | — |

Os membros de um pacote recebem a mesma posição (a do membro mais externo), já que formam um único afixo.

---

## Classes flexionais

| Fusão | Declinações (nome) | Conjugações (verbo) |
|---|---|---|
| Isolante | 0 | 0 |
| Aglutinante | 1 | 1 |
| Fusional | 2–5 | 2–4 |

O motor morfológico deve gerar um conjunto de desinências para cada classe.

---

## Uso

```bash
cd grammatical_categories

python grammatical_categories.py              # sorteio aleatório
python grammatical_categories.py --seed 42    # reprodutível
python grammatical_categories.py --no-wals    # só distribuições embutidas
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--morph PATH` | `../morphological_typology/morphological_typology.json` | Tipologia morfológica |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS |
| `--no-wals` | — | Ignora o WALS local |
| `-o PATH` | `grammatical_categories.json` | Arquivo de saída |

### Exemplos de saída no terminal

Língua sintética fusional sufixante:

```
NOME
  Número           singular, plural  → affix (suffix); Ø = singular
  Caso             direct, genitive, dative, instrumental, comitative, allative [neutral]  → affix (suffix); Ø = direct
  Gênero/classe    class_1, class_2, class_3, class_4, class_5  → affix (suffix)
  Definitude       unmarked, definite, indefinite  → definite: demonstrative_article (after), indefinite: article (after); Ø = unmarked

VERBO
  Tempo            non_future, future  → affix (suffix)
  Aspecto          perfective, imperfective  → affix (suffix); Ø = perfective
  Modo             indicative, imperative, irrealis  → affix (suffix); Ø = indicative
  Evidencialidade  direct, inferential, reportative  → clitic (suffix); Ø = direct
  Negação          affirmative, negative  → affix (suffix); Ø = affirmative

CUMULAÇÃO
  nome: gender × number × case
  verbo: aspect × tense × mood

MOLDES
  nome: ROOT-gender+number+case
  verbo: ROOT-aspect+tense+mood-evidentiality-negation

CLASSES FLEXIONAIS: 4 declinações, 3 conjugações
```

Língua isolante tonal:

```
NOME
  Número           singular, plural  → tone; Ø = singular
  Caso             — (word_order_and_adpositions)
  Classificadores  general, flat, building, human, long_thin, volume, small_round, vehicle  → word (after)

VERBO
  Tempo            non_past, past  → auxiliary (after); Ø = non_past
  Negação          affirmative, negative  → particle (before); Ø = affirmative

MOLDES
  nome: ROOT
    não linear: number (tone)
  verbo: ROOT
    palavras livres: tense (auxiliary, after), negation (particle, before)
```

### Uso como biblioteca

```python
import json
from grammatical_categories import CategoryBuilder, Wals, DEFAULT_MORPH, DEFAULT_WALS

morph = json.loads(DEFAULT_MORPH.read_text(encoding="utf-8"))
result = CategoryBuilder(morph, Wals(DEFAULT_WALS), seed=42).generate()

print(result["slots"]["verb"]["template"])
print(result["categories"]["case"].get("values"))
```

---

## Formato de `grammatical_categories.json`

```json
{
  "categories": {
    "number": {
      "grammaticalized": true,
      "values": ["singular", "plural"],
      "default": "singular",
      "zero": ["singular"],
      "realization": "affix",
      "position": "suffix",
      "scope": "all_nouns",
      "obligatory": true,
      "source": "WALS 34A (n=291); WALS 33A (n=1066); dual/trial/paucal: aproximação (Corbett 2000)"
    },
    "case": {
      "grammaticalized": true,
      "alignment": "ergative_absolutive",
      "values": ["absolutive", "ergative", "genitive", "dative", "locative"],
      "default": "absolutive",
      "zero": ["absolutive"],
      "realization": "affix",
      "position": "suffix",
      "source": "..."
    },
    "definiteness": {
      "grammaticalized": true,
      "values": ["unmarked", "definite"],
      "markers": {"definite": {"realization": "affix", "position": "suffix"}},
      "...": "..."
    },
    "agreement": {
      "grammaticalized": true,
      "arguments": {"A": {"realization": "affix", "position": "prefix"},
                    "P": {"realization": "affix", "position": "prefix"}},
      "alignment": "accusative",
      "persons": ["1", "2", "3"],
      "clusivity": "inclusive_exclusive",
      "numbers": ["singular", "plural"],
      "person_number": "cumulative",
      "zero": ["3.singular"]
    },
    "aspect": {"grammaticalized": false, "source": "WALS 65A (n=222)"}
  },
  "cumulation": {
    "noun": [["number", "case"]],
    "verb": [["aspect", "tense", "mood"]]
  },
  "slots": {
    "noun": {
      "prefixes": [],
      "suffixes": [{"name": "number+case", "categories": ["number", "case"], "realization": "affix"}],
      "template": "ROOT-number+case",
      "nonlinear": [],
      "free_markers": [{"category": "definiteness", "realization": "article", "position": "before"}]
    },
    "verb": {"template": "agreement_A-ROOT-aspect+tense+mood", "...": "..."}
  },
  "inflection_classes": {"noun": 3, "verb": 2},
  "metadata": {
    "seed": 42,
    "typology": {"synthesis": "synthetic", "fusion": "fusional",
                 "locus": "dependent_marking", "affix_position": "strongly_suffixing"},
    "wals": "local",
    "notes": ["3 declinações e 2 conjugações (língua fusional)"]
  }
}
```

> Os valores acima são ilustrativos. Prefixos são listados da periferia para a raiz; sufixos, da raiz para a periferia.

### Como o motor morfológico usa este arquivo

1. Lê `slots.<domínio>.template` para saber a ordem dos afixos.
2. Para cada slot, gera uma forma por valor (ou por **combinação** de valores, se for um pacote), chamando `generate_affix()` da fonotática, exceto para os valores em `zero`.
3. Repete o passo 2 para cada classe flexional, nas línguas fusionais.
4. Trata `nonlinear` (mudança de raiz, tom, reduplicação, transfixo) e `free_markers` (partículas, artigos, auxiliares) separadamente.
5. Valida cada forma com `is_valid()` da fonotática e aplica sândi quando necessário.

---

## Cuidados

- **Tipologia antiga:** se o `morphological_typology.json` foi gerado antes da reescrita do módulo (com `dominant_affix_position` e valores como `suffixing`), o módulo assume uma língua fortemente sufixante. Gere a tipologia de novo.
- **Ordem de execução:** tipologia → categorias. Se a tipologia mudar, gere as categorias de novo.
- **Probabilidades independentes:** além das tabelas condicionais listadas acima, as categorias são sorteadas de forma independente entre si. Combinações raras podem aparecer, o que é aceitável para uma conlang.

---

## Limitações e próximos passos

- [ ] Posse (afixos possessivos, posse alienável vs. inalienável — WALS 58A–59A)
- [ ] Valência (causativo, passiva, aplicativo, antipassiva — WALS 107A–111A)
- [ ] Concordância de adjetivos e demonstrativos com detalhamento por categoria
- [ ] Sistemas cindidos (ex: ergatividade só no passado ou só com nomes plenos)
- [ ] Mais correlações condicionais (ex: evidencialidade × família/região, gênero × concordância)

---

## Referências

- Dryer, M. S. & Haspelmath, M. (eds.) — *The World Atlas of Language Structures Online*. https://wals.info
- Bybee, J. (1985) — *Morphology: A Study of the Relation between Meaning and Form*
- Greenberg, J. (1963) — *Some universals of grammar with particular reference to the order of meaningful elements*
- Corbett, G. (1991) — *Gender*; (2000) — *Number*. Cambridge University Press
- Blake, B. (1994) — *Case*. Cambridge University Press
- Aikhenvald, A. (2004) — *Evidentiality*. Oxford University Press
- Palmer, F. R. (2001) — *Mood and Modality*, 2ª ed.
- Dahl, Ö. (1979) — *Typology of sentence negation*. Linguistics 17
