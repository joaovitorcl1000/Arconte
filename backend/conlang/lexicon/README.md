# Módulo — Léxico

Este módulo transforma as formas sonoras do motor morfológico em um **dicionário**: cada conceito de uma lista de vocabulário básico recebe uma palavra, com classe de palavra, transitividade, gênero ou classe nominal, classe flexional e formas flexionadas. Pronomes, numerais e palavras gramaticais saem coerentes com o que os módulos anteriores já decidiram.

```
morphology.json ──────────────┐
grammatical_categories.json ──┤
phonotactics.json ────────────┼──► LÉXICO ──► lexicon.json
phonemic_inventory.json ──────┤   (este módulo)   dictionary.md
listas do Concepticon ────────┘
```

---

## Entradas

| Arquivo | Obrigatório | Uso |
|---|---|---|
| `../morphological_engine/morphology.json` | Sim | Motor recarregado com `MorphologicalEngine.load()` para gerar e flexionar palavras |
| `../grammatical_categories/grammatical_categories.json` | Sim | Gênero, número, caso, concordância, pessoa e clusividade |
| `../phonotactics/phonotactics.json` | Sim | Formato das raízes e nº de sílabas |
| `../phonemic_inventory/phonemic_inventory.json` | Sim | Vogais disponíveis (para gênero formal) |
| `../morphological_typology/morphological_typology.json` | Não | Repassado ao motor |
| `../concepticon-data/` | Não | Clone do Concepticon, só para listas não embutidas |

Os módulos `morphological_engine.py` e `phonotactics.py` são importados das pastas vizinhas. Usa apenas a biblioteca padrão do Python (≥ 3.9).

> **Atualize também** `phonotactics.py` e `morphological_engine.py` com as versões entregues junto com este módulo: a fonotática passou a sortear sempre na mesma ordem (antes, a mesma semente podia gerar resultados diferentes entre execuções, porque a ordem dos conjuntos em Python varia), e o motor passou a aplicar a apofonia também em vogais nasais.

---

## Listas de conceitos

| `--list` | Fonte | Conceitos |
|---|---|---|
| `leipzig-jakarta` (padrão) | Tadmor (2009), ranqueada por estabilidade (resistência a empréstimo) | 100 |
| `swadesh-200` | Swadesh (1952) | 200 |
| `all` | União das duas | 231 |
| outro nome | Qualquer lista do Concepticon (ex: `Swadesh-1955-100`) | variável |

As duas listas principais vêm **embutidas no código**, extraídas do Concepticon com ID, gloss, inglês, categoria ontológica, campo semântico e rank de estabilidade. Para usar outras listas:

```bash
cd ~/Arconte/frontend/tools/conlang
git clone https://github.com/concepticon/concepticon-data.git
python lexicon/lexicon.py --list Swadesh-1955-100
```

Os dados do Concepticon são distribuídos sob licença CC BY 4.0 (List et al.).

---

## Classe de palavra

A classe vem da categoria ontológica do Concepticon:

| Categoria | Classe | Exemplos |
|---|---|---|
| Person/Thing | nome | *fire*, *dog*, *mother* |
| Action/Process | verbo | *eat*, *go*, *die* |
| Property | adjetivo **ou** verbo estativo (ver abaixo) | *big*, *red*, *new* |
| Number | numeral | *one*, *two* |
| Other | subclasse por lista | pronomes, demonstrativos, interrogativos, quantificadores, conjunções, advérbios, adposições, negação |

### Adjetivos (WALS 118A)

| Codificação predicativa | Probabilidade | Efeito |
|---|---|---|
| `verbal` | 39% | Propriedades viram **verbos estativos** e se conjugam |
| `nonverbal` | 34% | Propriedades são adjetivos sem flexão própria |
| `mixed` | 27% | Cada propriedade é sorteada como verbo ou adjetivo |

### Transitividade

Verbos de uma lista fixa (*eat*, *see*, *kill*, *hold*, *know*...) são **transitivos**; *give* é **bitransitivo**; os demais são **intransitivos**. A transitividade é o que o módulo de sintaxe vai usar para decidir quando aparece a concordância de objeto.

---

## Formas das palavras

- **Nomes, verbos e adjetivos** usam `generate_root()` da fonotática, com o nº de sílabas sorteado da distribuição da língua. Pela **lei de Zipf**, os 33 conceitos mais estáveis da lista Leipzig-Jakarta têm 50% de chance de perder uma sílaba.
- **Palavras gramaticais** (pronomes, demonstrativos, conjunções, interrogativos) têm uma sílaba; advérbios e numerais, uma ou duas.
- **Homófonos:** formas repetidas são rejeitadas, exceto com 3% de chance, já que alguma homofonia é realista.
- **Raízes consonantais:** em línguas com transfixação, nomes e verbos recebem esqueletos (`k-t-b`); a forma de citação aplica o padrão vocálico padrão.

### Reaproveitamento do que já existe

| Conceito | Quando reaproveita |
|---|---|
| *not* | Usa a partícula de negação do motor; se a negação for afixal, registra o afixo e marca o conceito como "expresso por afixo verbal" |
| *one* | Usa a forma do artigo indefinido quando ele deriva do numeral "um" (WALS 38A) |
| *at*, *in*, *with* | Se a língua tem caso locativo, essivo, comitativo ou instrumental, o conceito é **expresso pelo caso** e não ganha palavra própria |

---

## Gênero e classe nominal

A atribuição segue a semântica, como nas línguas reais:

| Sistema | Regra |
|---|---|
| masculino/feminino | homem, pai, marido → M; mulher, mãe, esposa → F; o resto: 55% M |
| masculino/feminino/neutro | humanos e animais → M ou F; o resto: 50% N |
| animado/inanimado | humanos e animais → animado |
| humano/animado/inanimado | por categoria |
| 4+ classes nominais | pelo núcleo semântico de cada classe: humanos, animais, plantas, líquidos e massas, objetos longos, abstratos (tempo, nome, sombra), artefatos; o que não se encaixa vai para a classe residual |

Em 10% dos nomes (exceto homem/mulher e parentes) o gênero é arbitrário, como em qualquer língua.

**Gênero formal:** quando a atribuição é `semantic_and_formal` e há até 4 gêneros, cada gênero recebe uma vogal final característica, e 70% dos nomes daquele gênero terminam nela (como o *-o*/*-a* do português).

**Classes flexionais:** nas línguas fusionais, a declinação se correlaciona com o gênero em 60% dos casos (como a 1ª declinação latina, majoritariamente feminina).

---

## Pronomes

A tabela completa de pronomes é gerada a partir do sistema de pessoa:

- **Pessoas e números:** os mesmos da concordância verbal (ou do número nominal, ou singular/plural).
- **Clusividade:** a mesma da concordância; sem concordância, é sorteada (WALS 39A).
- **Gênero na 3ª pessoa** (WALS 44A): só em línguas de gênero sexual; pode valer só para o singular (*ele/ela*) ou para todos os números (*eles/elas*).
- **Formação do plural:** supletiva (60%, cada pessoa tem sua forma, como *eu/nós*) ou sufixada (40%, singular + marca de plural).
- **Eco da concordância:** em 40% das línguas com concordância, os pronomes são construídos a partir dos afixos de pessoa, como acontece em muitas línguas reais.

Os pronomes das listas (*I*, *thou*, *he*, *we*, *you*, *they*) são ligados às células da tabela; *we* prefere o inclusivo quando existe.

---

## Colexificações e compostos

**Colexificações** são pares de conceitos que muitas línguas expressam com a mesma palavra (base de dados CLICS). Quando os dois conceitos estão na lista, a probabilidade de compartilharem a forma é:

| Par | Prob. | Par | Prob. |
|---|---|---|---|
| mulher = esposa | 40% | certo = direito | 40% |
| pé = perna | 30% | árvore = madeira | 30% |
| homem = marido | 30% | pele = casca | 25% |
| dia = sol | 25% | nuvem = neblina | 25% |
| árvore = graveto | 20% | cabelo = pena | 20% |
| barriga = entranhas | 20% | terra = poeira | 15% |
| mar = lago | 15% | saber = pensar | 15% |
| fogo = queimar | 15% | pessoa = homem | 15% |
| nuvem = céu | 10% | | |

**Compostos** são formados juntando duas raízes com o sândi do motor:

| Conceito | Composição | Prob. |
|---|---|---|
| casca | árvore + pele | 30% |
| pena | pássaro + cabelo | 30% |
| rio | água + caminho | 20% |
| cinza | fogo + poeira | 20% |
| sol | dia + olho ("olho do dia", como o malaio *matahari*) | 15% |
| gelo | duro + água | 15% |
| floresta | muitos + árvore | 10% |
| semente | flor + ovo | 10% |

A ordem núcleo-modificador é sorteada por língua (núcleo final em 60%); o módulo de sintaxe pode harmonizá-la depois com a ordem do genitivo. Compostos herdam o gênero do núcleo. Em línguas com raízes consonantais, compostos não são gerados.

---

## Formas flexionadas

Cada nome e verbo recebe uma **forma de citação** (a forma padrão gerada pelo motor, sem partículas nem artigos) e até duas formas principais:

| Classe | Formas principais |
|---|---|
| Nome | plural; segundo caso da lista (acusativo, ergativo...) |
| Verbo | 1ª pessoa do singular; passado (ou o aspecto marcado, se não houver tempo) |

Quando a raiz difere da forma de citação (ex: verbos citados na 3ª pessoa), o dicionário mostra a raiz entre colchetes.

---

## Uso

```bash
cd lexicon

python lexicon.py                              # Leipzig-Jakarta, 100 conceitos
python lexicon.py --list swadesh-200 --seed 42
python lexicon.py --list all                   # 231 conceitos
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--list NOME` | `leipzig-jakarta` | Lista de conceitos |
| `--concepticon PATH` | `../concepticon-data` | Clone do Concepticon (listas não embutidas) |
| `--inventory`, `--phonotactics`, `--categories`, `--morphology`, `--morph` | pastas vizinhas | Entradas |
| `-o PATH` | `lexicon.json` | Arquivo JSON |
| `--dictionary PATH` | `dictionary.md` | Dicionário em Markdown |

### Exemplo de saída no terminal

Língua fusional sufixante com 8 classes nominais e adjetivos verbais:

```
LÉXICO: 100 entradas — noun 50, verb 40, pronoun 3, numeral 1, interrogative 2, demonstrative 1, adverb 1, negation 1, adposition 1
  adjetivos: verbal; núcleo dos compostos: final

PRONOMES (plural: suppletive, ecoam a concordância)
  1SG ni  2SG me  3SG ɡi  1PL klaː  2PL muː  3PL ku

AMOSTRA
  kupwa [raiz kup] n. (CL8; classe 2) 'fire' — PL: kupsaː; ACC: kupmuː
  pal v.i. (classe 1) 'to go' — 1SG: pala
  mup [raiz mu] n. (CL8; classe 1) 'water' — PL: mul; ACC: mumi
  sunmi [raiz sun] n. (CL3; classe 2) 'bone' — PL: sunwi; ACC: sunba
  bĩs v.i. (classe 2) 'to come' — 1SG: bĩsik
```

Língua isolante tonal (plural por partícula):

```
  ɡur˨.wi˥ n. 'fire' — PL: ɡur˨.wi˥ xli
  taː˦ n. 'nose' — PL: taː˦ xli
  ʃa˦ v.i. 'to go'
```

### Estrutura do `dictionary.md`

1. Configurações da língua (adjetivos, núcleo dos compostos, vogais de gênero).
2. Tabela de pronomes.
3. Entradas em ordem alfabética da forma de citação:

```
- **banmo** *v.t.* (classe 1) 'to bite' — 1SG: banma
- **bisjemji** [raiz bisjem] *n.* (CL1; classe 1) 'child' — PL: bisjemi; ACC: bisjemak
- **bjuːm** *neg.* 'not'
```

4. Conceitos expressos sem palavra própria (ex: *in* → caso locativo).
5. Índice por significado (inglês → palavra).

### Uso como biblioteca

```python
import json, sys
sys.path.insert(0, "../morphological_engine")
sys.path.insert(0, "../lexicon")
from morphological_engine import MorphologicalEngine
from lexicon import LexiconBuilder, load_concepts

load = lambda p: json.loads(open(p, encoding="utf-8").read())
eng = MorphologicalEngine.load(
    load("../morphological_engine/morphology.json"),
    load("../phonemic_inventory/phonemic_inventory.json"),
    load("../phonotactics/phonotactics.json"),
    load("../grammatical_categories/grammatical_categories.json"))

data = LexiconBuilder(eng, seed=31).build(load_concepts("swadesh-200"))
water = next(e for e in data["entries"] if e["gloss"] == "WATER")

lex = {"root": water["root"], "form": water["form"], "tones": water["tones"],
       "class": water["class"] or 0, "gender": water.get("gender")}
eng.inflect(lex, "noun", {"number": "plural"})["surface"]
```

---

## Formato de `lexicon.json`

```json
{
  "entries": [
    {
      "id": "948",
      "gloss": "WATER",
      "english": "water",
      "pos": "noun",
      "field": "The physical world",
      "skeleton": false,
      "root": ["m", "u"],
      "form": "mu",
      "tones": [],
      "formation": "root",
      "gender": "class_8",
      "class": 0,
      "citation": "mup",
      "inflections": [
        {"gloss": "PL", "form": "mul", "valid": true},
        {"gloss": "ACC", "form": "mumi", "valid": true}
      ]
    },
    {
      "id": "1204", "gloss": "BARK", "pos": "noun", "formation": "compound",
      "parts": ["TREE", "SKIN (HUMAN)"], "...": "..."
    },
    {
      "id": "1460", "gloss": "IN", "pos": "adposition", "formation": "case",
      "expressed_by": "locative", "root": [], "citation": "", "...": "..."
    }
  ],
  "pronouns": {
    "cells": {"1.singular": {"segments": ["n", "i"], "form": "ni"}, "...": "..."},
    "numbers": ["singular", "plural"],
    "clusivity": "none",
    "third_person_gender": [],
    "gender_scope": "none",
    "plural_strategy": "suppletive",
    "echoes_agreement": true
  },
  "settings": {"adjectives": "verbal", "compound_head": "final"},
  "metadata": {"seed": 31, "list": "leipzig-jakarta", "notes": [],
               "source": "Concepticon (List et al.)"}
}
```

Valores de `formation`:

| Valor | Significado |
|---|---|
| `root` | Raiz nova |
| `compound` | Composto (`parts` lista as partes na ordem da palavra) |
| `colexification` | Mesma forma de outro conceito (`colexified_with`) |
| `pronoun_system` | Célula da tabela de pronomes (`cell`) |
| `grammatical` | Reaproveita uma palavra gramatical do motor |
| `bound` | Expresso por afixo (`note`) |
| `case` | Expresso por caso (`expressed_by`) |

`class` é `null` em línguas sem classes flexionais.

---

## Testes

Pipeline completo com 120 línguas aleatórias e a lista `all` (231 conceitos):

- nenhum erro de execução;
- 30.720 formas flexionadas, todas válidas pela fonotática;
- 1,3% de homofonia entre raízes (o alvo é ≤ 3%);
- mesma semente → arquivos idênticos byte a byte, mesmo com `PYTHONHASHSEED` diferente.

---

## Cuidados

- **Pipeline sincronizado:** o léxico depende do `morphology.json`, que depende de todos os módulos anteriores. Regerou algo antes? Regere o léxico.
- **Glosas em inglês:** os significados seguem o Concepticon (`english`, `gloss`). O `id` permite cruzar com qualquer outra lista ou tradução.
- **Forma de citação:** é a forma padrão do motor (ex: 3ª pessoa do singular do não passado), não necessariamente a raiz nua.

---

## Limitações e próximos passos

- [ ] Glosas em português (tradução dos conceitos do Concepticon)
- [ ] Derivação produtiva (agentivos, diminutivos, causativos) para expandir o léxico além da lista
- [ ] Mais colexificações e compostos, extraídos diretamente do CLICS
- [ ] Sistema numeral completo (base decimal/vigesimal, WALS 131A)
- [ ] Empréstimos e camadas lexicais
- [ ] Nomes próprios e topônimos
- [ ] Ortografia prática (romanização)

---

## Referências

- Tadmor, U. (2009) — *Loanwords in the world's languages: findings and results*. In Haspelmath & Tadmor (eds.), *Loanwords in the World's Languages*
- Swadesh, M. (1952) — *Lexico-statistic dating of prehistoric ethnic contacts*. Proceedings of the American Philosophical Society 96
- List, J.-M. et al. — *Concepticon*. https://concepticon.clld.org
- Rzymski, C. et al. (2020) — *The Database of Cross-Linguistic Colexifications (CLICS³)*. Scientific Data 7
- Zipf, G. K. (1949) — *Human Behavior and the Principle of Least Effort*
- Corbett, G. (1991) — *Gender*. Cambridge University Press
- Stassen, L. (1997) — *Intransitive Predication*. Oxford University Press
- Siewierska, A. (2004) — *Person*. Cambridge University Press
