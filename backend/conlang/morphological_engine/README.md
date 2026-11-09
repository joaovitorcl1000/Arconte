# Módulo — Motor Morfológico

Este é o primeiro módulo que **produz língua de fato**. Os módulos anteriores geram regras; o motor as aplica para criar afixos concretos, palavras gramaticais, formas flexionadas e paradigmas completos, resolvendo o sândi nas fronteiras de morfema.

```
phonemic_inventory.json ─────┐
phonotactics.json ───────────┤  (+ phonotactics.py importado)
grammatical_categories.json ─┼──► MOTOR MORFOLÓGICO ──► morphology.json
morphological_typology.json ─┘        (este módulo)        + paradigmas
        (opcional)
```

---

## Entradas

| Arquivo | Obrigatório | Uso |
|---|---|---|
| `../phonemic_inventory/phonemic_inventory.json` | Sim | Fonemas e traços (para assimilação, harmonia, vogal epentética) |
| `../phonotactics/phonotactics.json` | Sim | Regras silábicas; gerador de raízes e afixos; validador |
| `../phonotactics/phonotactics.py` | Sim | Importado diretamente (classe `Phonotactics`) |
| `../grammatical_categories/grammatical_categories.json` | Sim | Categorias, valores, marcas zero, moldes, cumulação, classes flexionais |
| `../morphological_typology/morphological_typology.json` | Não | Processos ativos (tipo de reduplicação) |

Usa apenas a biblioteca padrão do Python (≥ 3.9).

### Ordem de execução do pipeline

```bash
python morphological_typology/morphological_typology.py --random --seed 8 \
       -o morphological_typology/morphological_typology.json
python phonemic_inventory/phonemic_inventory.py --seed 8
python phonotactics/phonotactics.py --seed 8
python grammatical_categories/grammatical_categories.py --seed 8
python morphological_engine/morphological_engine.py --seed 8
```

As regras referenciam fonemas e categorias específicos: **se um módulo for regerado, todos os seguintes também precisam ser.**

---

## Etapas

### 1. Sândi

Cada língua sorteia suas estratégias de reparo, que dão boa parte da sua "personalidade" sonora:

| Parâmetro | Opções | Probabilidade |
|---|---|---|
| Vogal epentética | a primeira disponível entre /ə ɨ i ɪ e a u/ | — |
| Encontros consonantais ilegais | `epenthesis` (*tan-t* → *tanət*) / `deletion` (*tan-t* → *tat*) | 60% / 40% |
| Lado do apagamento | `left` (fim do radical) / `right` (início do afixo) | 50% / 50% |
| Hiato ilegal | `elision` / `glide` (*j* após vogal anterior, *w* após posterior) / `consonant` (/ʔ/, /h/, /t/ ou /n/) | 45% / 40% / 15% |
| Lado da elisão | `left` (vogal do radical) / `right` (vogal do afixo) | 70% / 30% |
| Assimilação nasal | *n* + *p* → *mp* | 70% das línguas |
| Assimilação de vozeamento | *t* + *b* → *db* | 40% das línguas |

**Algoritmo de reparo** (`resolve`), aplicado só quando `is_valid()` da fonotática rejeita a palavra:

1. Aplica as assimilações habilitadas e testa de novo.
2. Para cada fronteira, da raiz para fora, testa os reparos na ordem de preferência da língua; o primeiro que valida a palavra inteira é aceito.
3. Se nenhum reparo isolado resolve, repara a primeira fronteira problemática e repete.
4. Por fim, tenta epêntese nas bordas da palavra (final, inicial ou ambas).
5. Se nada funciona, a forma sai marcada como inválida (`*` no paradigma).

Reparos nunca apagam um morfema inteiro nem deixam uma raiz sem vogal.

### 2. Harmonia vocálica

| Tipo de língua | Probabilidade |
|---|---|
| Aglutinante | 35% |
| Polissintética | 20% |
| Fusional | 10% |
| Isolante | 0% |

O tipo implementado é **anterior/posterior** (como no turco *ev-ler* / *at-lar*). Cada vogal é pareada com outra de mesmo arredondamento, comprimento e nasalidade, de altura igual ou vizinha. Vogais sem par são neutras. A harmonia só é ativada se houver pelo menos dois pares; senão, fica registrado nas notas.

Os afixos copiam a anterioridade da vogal mais próxima do radical: a última, para sufixos; a primeira, para prefixos.

### 3. Afixos

Para cada slot do molde de `grammatical_categories.json`, o motor gera uma forma por **célula**:

- Num slot simples, uma forma por valor (`PL -ka`).
- Num pacote fusional, uma forma por **combinação** de valores (número × caso = 2 × 6 = 12 desinências).
- Na concordância, uma por pessoa × número, com inclusivo/exclusivo nos não singulares quando a língua tem clusividade.
- Na concordância com pessoa e número separados (`person_number: separate`), um afixo de pessoa seguido de um de número, com fronteira interna tratada pelo sândi.

Regras de geração:

- **Marcas zero:** uma célula é Ø quando todos os seus valores estão nas listas `zero` das categorias.
- **Distinção:** valores diferentes de um mesmo slot recebem formas diferentes. Se o inventário for pequeno demais, o motor cria afixos de duas partes (sempre alternando C/V na junção) e, em último caso, aceita a colisão.
- **Sincretismo:** em pacotes fusionais, 12% das células reaproveitam a forma de outra célula, como o latim *-īs* (dativo e ablativo plural).
- **Prefixos** nunca começam por consoantes proibidas no início de palavra.

### 4. Classes flexionais

Nas línguas fusionais, os slots de pacotes (ex: `number+case`) têm um conjunto de formas **por classe flexional**. Sem pacotes, a classe fica no slot de maior prioridade, nesta ordem: caso, número, concordância A, tempo, modo, aspecto, concordância P.

Cada lexema recebe uma classe aleatória.

### 5. Processos não lineares

| Realização | Como funciona |
|---|---|
| `stem_change` | Cada valor marcado tem um mapa vocálico próprio aplicado à última vogal do radical; toda vogal muda, e de forma diferente em cada valor (*miː* → DU *maː*, PL *mɔː*). Vogais longas usam o mapa da curta correspondente |
| `tone` | Cada valor marcado substitui o tom da última sílaba da raiz |
| `reduplication` | Total (`reduplication_full`) ou primeira sílaba (C)V (`reduplication_partial`), para o primeiro valor marcado; os demais valores recebem sufixos. O reduplicante é um morfema separado, para que o sândi trate a fronteira |
| `transfix` | Raízes consonantais recebem um padrão vocálico por valor (`t-ɡ-b` → NPST *toɡub*, PST *tuɡob*) |

Quando o processo não é viável (tom sem sistema tonal, apofonia com menos de duas vogais, transfixação sem raízes consonantais), o motor usa **sufixos de reserva** e registra o motivo nas notas.

**Raízes consonantais:** em línguas com transfixação, nomes e verbos têm padrões vocálicos padrão (`noun_default`, `verb_default`). Os padrões são validados contra 15 esqueletos de teste; se um radical específico ainda violar a fonotática, recebe epêntese interna ou final.

### 6. Palavras gramaticais livres

Partículas, auxiliares, artigos, numerais "um" usados como artigo e classificadores ganham formas de uma sílaba (ou duas, se o inventário se esgotar), todas distintas entre si. Cada uma aparece antes ou depois da palavra, conforme a posição definida nas categorias. Na negação dupla, a partícula convive com o afixo.

### 7. Flexão

`inflect(lexema, domínio, traços)` monta uma palavra nesta ordem:

1. Radical: raiz ou padrão vocálico, mais os processos não lineares.
2. Prefixos (da periferia para a raiz), reduplicante, **raiz**, sufixos de reserva, sufixos (da raiz para a periferia).
3. Harmonia vocálica nos afixos.
4. Sândi.
5. Tons: as sílabas da raiz mantêm seus tons; as dos afixos recebem o tom mais frequente.
6. Palavras livres antes e depois.

Traços não informados assumem o valor padrão de cada categoria. Passar `agreement_P: None` omite a marca de objeto (verbo intransitivo).

### 8. Paradigmas

| Domínio | Linhas | Colunas |
|---|---|---|
| Nome | caso (ou definitude) | número |
| Verbo | concordância A (ou P, ou um eixo de TAM) | tempo (ou aspecto, ou modo) |

As demais categorias ficam no valor padrão. O paradigma verbal é intransitivo.

---

## Glosas

Seguem as convenções de Leipzig: `SG`, `PL`, `DU`, `NOM`, `ACC`, `ERG`, `ABS`, `GEN`, `DAT`, `LOC`, `PST`, `NPST`, `FUT`, `PFV`, `IPFV`, `IMP`, `IRR`, `NEG`, `DEF`, `INDF` etc. A concordância é glosada como `1SG`, `2PL`, `1INCL.PL`; classes nominais como `CL1`, `CL2`. Valores padrão não aparecem na glosa.

---

## Uso

```bash
cd morphological_engine

python morphological_engine.py                         # sorteio aleatório
python morphological_engine.py --seed 8                # reprodutível
python morphological_engine.py --nouns 10 --verbs 10   # léxico de exemplo maior
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--nouns N` | `6` | Nº de nomes no léxico de exemplo |
| `--verbs N` | `6` | Nº de verbos no léxico de exemplo |
| `--inventory PATH` | `../phonemic_inventory/phonemic_inventory.json` | Inventário |
| `--phonotactics PATH` | `../phonotactics/phonotactics.json` | Fonotática |
| `--categories PATH` | `../grammatical_categories/grammatical_categories.json` | Categorias |
| `--morph PATH` | `../morphological_typology/morphological_typology.json` | Tipologia |
| `-o PATH` | `morphology.json` | Arquivo de saída |

### Exemplo de saída no terminal

Língua fusional, sufixante, de marcação no núcleo, com apofonia:

```
SÂNDI
  vogal epentética /ə/; encontros: epenthesis; hiato: elision; assimilação nasal: sim; assimilação de vozeamento: sim

AFIXOS — NOME
  case [classe 1]: ABS Ø, ERG -wi, DAT -i
  case [classe 2]: ABS Ø, ERG -wi, DAT -mu
  case [classe 3]: ABS Ø, ERG -ta, DAT -ki
  number (não linear): stem_change; DU: i→a u→e ʊ→i ...; PL: i→ɔ u→ə ʊ→e ...

AFIXOS — VERBO
  agreement_P: 1SG -sa, 2SG -pu, 3SG -i, 1DU -so, ...
  evidentiality: DIR Ø, INDIR -ɸa
  tense+mood+agreement_A [classe 1]: NPST.IND.1SG -li, NPST.IND.2SG -a, ... (+22)

PALAVRAS GRAMATICAIS
  definiteness: DEF la (depois), INDF lə (depois)
  negation: NEG ɡa (depois)

PARADIGMA NOMINAL: miː, feminine, classe 3
          SG     DU     PL
    ABS   miː    maː    mɔː
    ERG   miːta  maːta  mɔːta
    DAT   miːki  maːki  mɔːki

PARADIGMA VERBAL: pe.ɲe, classe 2
          NPST     PST
    1SG   peɲu     peɲeŋi
    2SG   peɲa     peɲeja
    3SG   peɲeneː  peɲeba
```

Língua com transfixação e concordância prefixal:

```
AFIXOS — VERBO
  agreement_A: 1SG ʂo-, 2SG da-, 3SG Ø, 1PL e-, 2PL di-, 3PL t̠ʃi-
  tense (não linear): transfix; NPST C1oC2uC3, PST C1uC2oC3

PARADIGMA VERBAL: t-ɡ-b, classe 1
          NPST       PST
    1SG   ʂotoɡubi   ʂotuɡobi
    2SG   datoɡubi   datuɡobi
    3SG   toɡubi     tuɡobi
```

### Uso como biblioteca

```python
import json, sys
sys.path.insert(0, "../morphological_engine")
from morphological_engine import MorphologicalEngine

load = lambda p: json.loads(open(p, encoding="utf-8").read())
inventory = load("../phonemic_inventory/phonemic_inventory.json")
rules = load("../phonotactics/phonotactics.json")
categories = load("../grammatical_categories/grammatical_categories.json")
typology = load("../morphological_typology/morphological_typology.json")

# Construir do zero
eng = MorphologicalEngine(inventory, rules, categories, typology, seed=8)
data = eng.build(n_nouns=6, n_verbs=6)

# Ou recarregar uma morfologia já salva
eng = MorphologicalEngine.load(load("morphology.json"), inventory, rules, categories, typology)

# Flexionar qualquer lexema
noun = {"root": ["m", "iː"], "form": "miː", "tones": [], "class": 2, "gender": "feminine"}
eng.inflect(noun, "noun", {"number": "plural", "case": "ergative"})
# → {"surface": "mɔːta", "underlying": "mɔː-ta", "phrase": "mɔːta",
#    "gloss": "PL.ERG", "valid": True, "sandhi": []}

eng.paradigm(noun, "noun")   # tabela completa
```

---

## Formato de `morphology.json`

```json
{
  "sandhi": {
    "epenthetic_vowel": "ə",
    "cluster": "epenthesis",
    "deletion_side": "left",
    "hiatus": "elision",
    "elision_side": "left",
    "glides": {"front": "j", "back": "w"},
    "hiatus_consonant": "ʔ",
    "nasal_assimilation": true,
    "voicing_assimilation": true
  },
  "harmony": {
    "enabled": true,
    "type": "backness",
    "pairs": {"i": {"front": "i", "back": "ɯ"}, "...": "..."},
    "neutral": ["ə"]
  },
  "affixes": {
    "noun": [
      {
        "name": "case",
        "categories": ["case"],
        "position": "suffix",
        "realization": "affix",
        "class_dependent": true,
        "forms": {
          "0": {"case=absolutive": [], "case=ergative": ["w", "i"], "case=dative": ["i"]},
          "1": {"...": "..."}
        }
      }
    ],
    "verb": ["..."]
  },
  "nonlinear": {
    "processes": {
      "noun": [{"category": "number", "realization": "stem_change",
                "vowel_maps": {"dual": {"i": "a", "...": "..."}, "plural": {"...": "..."}},
                "fallback_affixes": {}}],
      "verb": []
    },
    "patterns": {}
  },
  "free_markers": {
    "definiteness": {"forms": {"definite": ["l", "a"]},
                     "positions": {"definite": "after"},
                     "realization": {"definite": "article"}}
  },
  "lexicon_sample": {
    "nouns": [{"root": ["m", "iː"], "form": "miː", "tones": [], "class": 2, "gender": "feminine"}],
    "verbs": ["..."]
  },
  "paradigms": {
    "noun": {"lexeme": "miː", "rows": ["case", ["absolutive", "ergative", "dative"]],
             "columns": ["number", ["singular", "dual", "plural"]],
             "cells": [[{"surface": "miː", "underlying": "miː", "phrase": "miː",
                         "gloss": "", "valid": true, "sandhi": []}, "..."]]},
    "verb": {"...": "..."}
  },
  "metadata": {"seed": 8, "fusion": "fusional", "consonantal_roots": false, "notes": []}
}
```

As chaves das células seguem o formato `categoria=valor|categoria=valor`, na ordem das categorias do slot (ex: `number=plural|case=genitive`). Listas vazias são marcas zero. Segmentos são sempre listas de fonemas em NFD; o símbolo `+` dentro de uma forma marca a fronteira entre afixo de pessoa e de número.

---

## Testes

O pipeline completo foi testado com 300 línguas aleatórias (tipologias variadas, metade com inventário baseado em língua real), gerando 28.144 formas flexionadas:

- nenhum erro de execução;
- 0,05% de formas que o sândi não conseguiu reparar (marcadas com `*`);
- recarregar o `morphology.json` com `load()` reproduz exatamente os mesmos paradigmas.

---

## Cuidados

- **Pipeline sincronizado:** todos os JSONs devem vir da mesma cadeia de geração. Um `phonotactics.json` gerado para outro inventário referencia fonemas inexistentes.
- **Importação:** o motor espera `phonotactics.py` em `../phonotactics/`. Se mudar a estrutura de pastas, ajuste o `sys.path` no início do arquivo.
- **Fonemas como unidades:** formas são listas como `["t̠ʃ", "a"]`. Para exibir, junte com `"".join(...)`, removendo o `+` interno.
- **Formas inválidas:** são raras, mas existem; consulte `valid` antes de usar uma forma em outro módulo.

---

## Limitações e próximos passos

- [ ] Léxico com significados (raízes ainda são só formas sonoras)
- [ ] Morfologia derivacional: nominalização, causativo, diminutivo, aplicativo
- [ ] Composição de raízes (`compounding` já existe na tipologia)
- [ ] Incorporação nominal efetiva nas línguas polissintéticas
- [ ] Outros tipos de harmonia (arredondamento, ATR, altura)
- [ ] Alomorfia condicionada lexicalmente e formas supletivas (ex: *ir/fui*)
- [ ] Acento e sua interação com o sândi
- [ ] Concordância de adjetivos, artigos e demonstrativos em gênero/número/caso

---

## Referências

- Comrie, B., Haspelmath, M. & Bickel, B. — *The Leipzig Glossing Rules*. Max Planck Institute for Evolutionary Anthropology
- McCarthy, J. (1981) — *A prosodic theory of nonconcatenative morphology*. Linguistic Inquiry 12(3)
- Kenstowicz, M. (1994) — *Phonology in Generative Grammar*. Blackwell
- Casali, R. (1997) — *Vowel elision in hiatus contexts*. Language 73(3)
- Clements, G. N. & Sezer, E. (1982) — *Vowel and consonant disharmony in Turkish*
- Baerman, M., Brown, D. & Corbett, G. (2005) — *The Syntax-Morphology Interface: A Study of Syncretism*. Cambridge University Press
