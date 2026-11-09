# Módulo — Sintaxe

Este módulo define a **ordem dos constituintes** da conlang (oração, sintagma nominal, adposições, perguntas, pro-drop) e gera **frases de exemplo com glosa interlinear** no padrão de Leipzig, usando o léxico e o motor morfológico. É o primeiro módulo que produz frases completas.

```
lexicon.json ─────────────────┐
morphology.json ──────────────┤
grammatical_categories.json ──┼──► SINTAXE ──► syntax.json
phonotactics.json ────────────┤   (este módulo)   examples.md
phonemic_inventory.json ──────┤
WALS (opcional) ──────────────┘
```

---

## Entradas

| Arquivo | Obrigatório | Uso |
|---|---|---|
| `../lexicon/lexicon.json` | Sim | Palavras, transitividade, pronomes, configuração dos adjetivos e dos compostos |
| `../morphological_engine/morphology.json` | Sim | Motor recarregado para flexionar as palavras nas frases |
| `../grammatical_categories/grammatical_categories.json` | Sim | Caso e alinhamento, concordância, negação, classificadores |
| `../phonotactics/phonotactics.json` | Sim | Exigido pelo motor; gera partículas novas |
| `../phonemic_inventory/phonemic_inventory.json` | Sim | Exigido pelo motor |
| `../morphological_typology/morphological_typology.json` | Não | Repassado ao motor |
| `../wals/cldf/values.csv` | Não | Distribuições atualizadas do WALS |

Usa apenas a biblioteca padrão do Python (≥ 3.9).

> **Atualize também** `grammatical_categories.py` com a versão entregue junto com este módulo: valores padrão expressos por partícula ou auxiliar passaram a ser sempre Ø. Antes, uma língua isolante podia sair com uma partícula de "singular" depois de cada nome ou de "indicativo" depois de cada verbo, o que é muito raro nas línguas reais.

---

## Decisões sintáticas

### Ordem básica (WALS 81A)

A ordem de sujeito, objeto e verbo é sorteada **condicionada ao tipo de afixação** da tipologia morfológica (WALS 26A × 81A), o que reproduz correlações reais: línguas fortemente sufixantes são majoritariamente SOV; línguas fortemente prefixantes, majoritariamente SVO.

| Afixação | SOV | SVO | VSO | VOS | OVS | Sem ordem dominante |
|---|---|---|---|---|---|---|
| Pouca afixação | 22% | 54% | 11% | 4% | 1% | 9% |
| Fortemente sufixante | 62% | 18% | 3% | 1% | 1% | 16% |
| Fortemente prefixante | 7% | 75% | 13% | 2% | — | 4% |

Quando a língua não tem ordem dominante, o módulo sorteia uma ordem neutra para os exemplos e registra a liberdade de ordem nas notas.

### Demais ordens, condicionadas à ordem básica

| Decisão | WALS | Valores |
|---|---|---|
| Adposições | 85A | posposições, preposições ou nenhuma |
| Genitivo | 86A | antes ou depois do nome |
| Adjetivo | 87A | antes ou depois do nome |
| Demonstrativo | 88A | antes ou depois do nome |
| Numeral | 89A | antes ou depois do nome |
| Oração relativa | 90A | depois do nome, antes do nome, núcleo interno, correlativa, adjunta ou com dois núcleos |
| Perguntas de conteúdo | 93A | palavra interrogativa no início ou *in situ* |

Cada uma é sorteada da distribuição **condicionada à ordem básica** (tabelas cruzadas 81A × 85A–93A). Assim, uma língua SOV tem 92% de chance de ter posposições e 90% de ter genitivo antes do nome, como prevêem as correlações de Greenberg e Dryer, mas exceções continuam possíveis. Quando o WALS indica "sem ordem dominante", o lado é sorteado.

### Perguntas sim/não (WALS 116A e 92A)

| Estratégia | Prob. | Realização nos exemplos |
|---|---|---|
| Partícula | ~63% | Palavra nova glosada `Q`, no início, no fim ou na 2ª posição (92A, condicionado à ordem básica) |
| Morfologia verbal | ~17% | Enclítico interrogativo no verbo (`ver=Q`) |
| Ordem das palavras | ~1% | O verbo vai para o início da frase |
| Só entonação | ~19% | A frase não muda |

### Outras decisões

| Decisão | Regra |
|---|---|
| **Pro-drop** | Sujeitos pronominais são omitidos em 90% das línguas com concordância de sujeito no verbo e em 35% das demais (WALS 101A) |
| **Cópula** | Se os adjetivos são verbais, predicados adjetivais se conjugam como verbos; senão, cópula zero (50%) ou uma palavra própria glosada `COP`, antes do adjetivo em VO e depois em OV |
| **Negação** | Herdada das categorias: afixo, partícula (antes ou depois do verbo), auxiliar ou dupla |
| **Compostos** | Verifica se a ordem dos compostos do léxico é harmônica com a do genitivo (núcleo final ↔ genitivo antes do nome) e avisa quando não é |

---

## Montagem das frases

### Ordem dentro do sintagma nominal

Os modificadores seguem o **universal 20 de Greenberg**: antes do nome, na ordem demonstrativo – numeral – adjetivo – nome; depois do nome, na ordem espelhada nome – adjetivo – numeral – demonstrativo. O genitivo fica na periferia do sintagma, do lado definido pelo 86A. Quando a língua tem classificadores, eles acompanham o numeral (sempre se forem obrigatórios, em 50% das frases se forem opcionais), escolhidos pela semântica do nome: humano, animal, objeto longo ou geral.

Artigos e partículas de número entram ao lado do nome, na posição definida nas categorias.

### Caso por função

| Alinhamento | S (intransitivo) | A (agente) | P (paciente) |
|---|---|---|---|
| nominativo-acusativo | NOM | NOM | ACC |
| ergativo-absolutivo | ABS | ERG | ABS |
| tripartido | INTR | ERG | ACC |
| ativo-inativo | AGT (verbos agentivos como *ir*, *correr*) ou PAT | AGT | PAT |
| neutro | DIR | DIR | DIR |

O recipiente de *dar* recebe dativo, alativo ou locativo (o primeiro que existir); o possuidor, genitivo; o adjunto locativo, locativo, essivo ou alativo. Sem caso locativo, o local é expresso pela adposição do léxico (*in*/*at*) na posição do 85A.

### Concordância verbal

| Verbo | Concordância |
|---|---|
| Transitivo | A no slot de A; P no slot de P |
| Intransitivo, alinhamento ergativo | S no slot de P |
| Intransitivo, demais alinhamentos | S no slot de A; slot de P vazio |

A pessoa e o número vêm do argumento: 3ª pessoa com o número do nome, ou a célula do pronome.

### Posição dos constituintes

- **Recipiente:** em línguas OV, antes do objeto (S R O V); em VO, depois do objeto (S V O R).
- **Adjunto locativo:** antes do verbo em OV; no fim da oração em VO.
- **Palavra interrogativa:** substitui o objeto *in situ* ou vai para o início.

### Glosa interlinear

Cada exemplo tem até quatro linhas, no padrão de Leipzig:

1. forma de superfície (com tons, se houver);
2. forma segmentada em morfemas (omitida quando idêntica à 1ª);
3. glosa morfema a morfema, **alinhada com a segmentação**;
4. tradução.

A glosa é refeita a partir da montagem do motor, então cada hífen da linha 2 corresponde a um hífen da linha 3. Morfemas de forma zero não aparecem. Processos não lineares vão colados à raiz com barra invertida (`sleep\PST` para apofonia), clíticos com `=`, e afixos fundidos têm os traços unidos por ponto (`CL8.SG.ACC`).

---

## Frases de exemplo

| Chave | Construção | Tradução-modelo |
|---|---|---|
| `intransitive` | Oração intransitiva | *The child sleeps.* |
| `transitive` | Oração transitiva | *The woman sees the fish.* |
| `past` | Passado (ou perfectivo), objeto plural | *The dog ate the fish.* |
| `ditransitive` | Oração bitransitiva | *The woman gives the fish to the child.* |
| `pronouns` | Pronomes, com pro-drop | *I see you.* |
| `noun_phrase` | Demonstrativo + numeral + adjetivo + nome | *These two big dogs come.* |
| `possession` | Genitivo | *The woman's dog sleeps.* |
| `location` | Adjunto locativo | *The child sleeps in the house.* |
| `predicate_adjective` | Predicado adjetival | *The fish is big.* |
| `negation` | Negação | *The child does not sleep.* |
| `polar_question` | Pergunta sim/não | *Does the woman see the fish?* |
| `content_question` | Pergunta com "o quê" | *What does the woman see?* |

Os lexemas são escolhidos por preferência (ex: *child*, *woman*, *dog*, *fish*, *sleep*, *see*, *give*); se a lista de conceitos não tiver algum, o módulo usa outro da mesma classe (um nome animado, um verbo transitivo...). Um exemplo só é omitido se não houver nenhum lexema adequado. Quando a língua não tem passado nem perfectivo, o exemplo `past` sai no presente e o título avisa.

As traduções usam uma morfologia inglesa mínima (plurais e passados irregulares mais comuns).

---

## Uso

```bash
cd syntax

python syntax.py               # sorteio aleatório
python syntax.py --seed 31     # reprodutível
python syntax.py --no-wals     # só distribuições embutidas
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--lexicon`, `--morphology`, `--categories`, `--phonotactics`, `--inventory`, `--morph` | pastas vizinhas | Entradas |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS |
| `--no-wals` | — | Ignora o WALS local |
| `-o PATH` | `syntax.json` | Arquivo JSON |
| `--examples PATH` | `examples.md` | Frases de exemplo em Markdown |

### Exemplo de saída no terminal

Língua fusional, fortemente sufixante, de marcação no dependente, com 8 classes nominais:

```
SINTAXE
  Ordem básica: SOV
  Adposições: posposições
  Genitivo antes do nome; adjetivo antes do nome; demonstrativo antes do nome; numeral depois do nome
  Oração relativa: depois do nome
  Perguntas sim/não: morfologia verbal; perguntas de conteúdo: no início
  Pro-drop: sim; cópula: nenhuma
  Compostos: núcleo final (harmônico com o genitivo)

Oração transitiva
  pit̪õjapõ          jãmpimmuː        kinwa
  pit̪õja-põ         jãmpim-muː       kinwa
  woman-CL2.SG.NOM  fish-CL8.SG.ACC  see
  'The woman sees the fish.'

Pronomes (sujeito omitido: pro-drop)
  memi            kinwak
  me-mi           kinwa-k
  2SG-CL8.SG.ACC  see-1SG
  'I see you.'

Sintagma nominal (demonstrativo, numeral, adjetivo)
  kaːk  nuːme  wipninuːs       no   bĩsim
  kaːk  nuːme  wipnin-uːs      no   bĩs-m
  this  big    dog-CL8.PL.NOM  two  come-3PL
  'These two big dogs come.'
```

Língua polissintética, fortemente prefixante, de marcação no núcleo:

```
Pronomes (sujeito omitido: pro-drop)
  nuʔojujutu       kai
  nu-ʔo-ju-jutu    kai
  1SG-IND-2SG-see  2SG
  'I see you.'

Negação
  suwim  ʔomipumun
  suwim  ʔo-mi-pumun
  child  IND-NEG-sleep
  'The child does not sleep.'

Pergunta sim/não
  lupum  ʔojutuka    pulsii
  lupum  ʔo-jutu=ka  pulsii
  woman  IND-see=Q   fish
  'Does the woman see the fish?'
```

O `examples.md` traz o resumo das decisões e todas as frases, cada uma num bloco de código para preservar o alinhamento.

### Uso como biblioteca

```python
import json, sys
sys.path.insert(0, "../morphological_engine")
sys.path.insert(0, "../syntax")
from morphological_engine import MorphologicalEngine
import syntax

load = lambda p: json.loads(open(p, encoding="utf-8").read())
eng = MorphologicalEngine.load(
    load("../morphological_engine/morphology.json"),
    load("../phonemic_inventory/phonemic_inventory.json"),
    load("../phonotactics/phonotactics.json"),
    load("../grammatical_categories/grammatical_categories.json"))
lexicon = load("../lexicon/lexicon.json")

data = syntax.build(eng, lexicon, typology={}, wals=syntax.Wals(syntax.DEFAULT_WALS), seed=31)
for ex in data["examples"]:
    print("\n".join(syntax.interlinear(ex)))
```

---

## Formato de `syntax.json`

```json
{
  "settings": {
    "word_order": {"clause": "SOV", "free": false, "object_before_verb": true},
    "adpositions": "postpositions",
    "noun_phrase": {"genitive": "before", "adjective": "before", "demonstrative": "before",
                    "numeral": "after", "relative_clause": "after_noun"},
    "polar_questions": {"strategy": "verb_morphology"},
    "content_questions": "initial",
    "pro_drop": true,
    "copula": "none",
    "negation": {"realization": "particle", "position": "before"},
    "compounds": {"head": "final", "harmonic_with_genitive": true}
  },
  "function_words": {"question_particle": ["j", "i"]},
  "examples": [
    {
      "key": "transitive",
      "title": "Oração transitiva",
      "words": [
        {"form": "pit̪õjapõ", "seg": "pit̪õja-põ", "gloss": "woman-CL2.SG.NOM"},
        {"form": "jãmpimmuː", "seg": "jãmpim-muː", "gloss": "fish-CL8.SG.ACC"},
        {"form": "kinwa", "seg": "kinwa", "gloss": "see"}
      ],
      "translation": "The woman sees the fish."
    }
  ],
  "metadata": {
    "seed": 31,
    "sources": {"word_order": "WALS 81A|26A=2 (n=355)", "...": "..."},
    "notes": [],
    "wals": "local"
  }
}
```

`copula` vale `none` quando os adjetivos são verbais, `zero` ou `word` nos demais casos. `function_words` guarda as palavras gramaticais criadas por este módulo (partícula interrogativa, cópula), todas distintas das palavras do léxico e das partículas do motor.

---

## Testes

Pipeline completo (tipologia → inventário → fonotática → categorias → motor → léxico → sintaxe) com 200 combinações de língua e fonte do WALS (100 línguas aleatórias, cada uma com o WALS local e com o embutido), gerando 2.400 frases:

- nenhum erro de execução;
- nenhuma palavra com segmentação e glosa desalinhadas;
- mesma semente → mesmos arquivos.

---

## Cuidados

- **Pipeline sincronizado:** a sintaxe lê o léxico e o motor. Regerou algum módulo anterior? Regere o léxico e a sintaxe.
- **Ordem livre:** quando `free` é `true`, os exemplos mostram só a ordem neutra sorteada; a língua admite outras.
- **Traduções aproximadas:** a morfologia inglesa é mínima e serve só para identificar o sentido.

---

## Limitações e próximos passos

- [ ] Orações relativas e subordinadas nos exemplos (a posição já é decidida, mas não é gerada)
- [ ] Concordância de adjetivos, demonstrativos e numerais com o nome
- [ ] Ordens alternativas para línguas de ordem livre (tópico e foco)
- [ ] Marcação diferencial de objeto (caso só para objetos animados ou definidos)
- [ ] Ergatividade cindida e alinhamento hierárquico na montagem das frases
- [ ] Imperativos, orações coordenadas e verbos seriais
- [ ] Harmonizar automaticamente a ordem dos compostos com a do genitivo

---

## Referências

- Dryer, M. S. & Haspelmath, M. (eds.) — *The World Atlas of Language Structures Online*. https://wals.info
- Greenberg, J. (1963) — *Some universals of grammar with particular reference to the order of meaningful elements*
- Dryer, M. S. (1992) — *The Greenbergian word order correlations*. Language 68(1)
- Cinque, G. (2005) — *Deriving Greenberg's Universal 20 and its exceptions*. Linguistic Inquiry 36(3)
- Comrie, B., Haspelmath, M. & Bickel, B. — *The Leipzig Glossing Rules*
- Dixon, R. M. W. (1994) — *Ergativity*. Cambridge University Press
- Payne, T. (1997) — *Describing Morphosyntax: A Guide for Field Linguists*. Cambridge University Press
