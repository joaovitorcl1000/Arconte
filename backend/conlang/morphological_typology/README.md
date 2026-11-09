# Módulo 2 — Tipologia Morfológica

Este módulo define **como** a morfologia da conlang funciona: quantos morfemas cabem em uma palavra, como eles se conectam à raiz e quais processos de formação de palavras estão ativos. O **conteúdo** gramatical (número, caso, tempo, aspecto etc.) fica em um módulo separado.

```
PHOIBLE ──► Fonotática ──► raízes ──► MORFOLOGIA ──► Sintaxe
                                     (este módulo)
```

---

## Os quatro tipos clássicos

| Tipo Morfológico | Como funciona | Exemplos Reais | Comportamento no Código |
|---|---|---|---|
| **Isolante / Analítica** | Praticamente 1 morfema por palavra. Não existem prefixos, sufixos ou conjugações. A gramática depende estritamente da ordem das palavras e de partículas soltas. | Chinês Mandarim, Vietnamita | Raízes puras e curtas (1 ou 2 sílabas). Para indicar tempo ou plural, o código gera palavras soltas adicionais (ex: "eu comer já ontem"). |
| **Aglutinante** | As palavras são formadas colando morfemas como blocos de LEGO. Cada afixo tem um único significado claro e invariável. Palavras podem ficar gigantescas, mas são 100% previsíveis. | Turco, Finlandês, Japonês, Esperanto | `Raiz + [sufixo_plural] + [sufixo_caso] + [sufixo_posse]`. O código encadeia regras modulares sem alterar a raiz. |
| **Fusional / Sintética** | Afixos se fundem com a raiz e um único sufixo carrega múltiplos significados ao mesmo tempo (ex: no latim ou português, *-o* em "falo" indica 1ª pessoa, singular, presente do indicativo, voz ativa, tudo em uma letra). | Português, Espanhol, Russo, Latim, Grego Antigo | Tabelas de declinação e conjugação onde o código altera a desinência (ou a própria raiz) em matrizes multidimensionais. |
| **Polissintética** | Frases inteiras viram uma única palavra hiper-complexa, fundindo sujeito, verbo, objeto e instrumentos. | Nauatle, Inuktitut (Esquimó) | Algoritmos complexos de fusão de raízes. Uma sentença inteira é compilada como um único lexema longo. |

---

## Do modelo clássico ao modelo do código

A tabela acima é útil como referência, mas mistura dois parâmetros independentes. O código segue a tipologia moderna (Sapir, Comrie) e separa a classificação em **dois eixos**:

- **Grau de síntese** — *quantos* morfemas por palavra (isolante → sintética → polissintética)
- **Grau de fusão** — *como* as fronteiras entre morfemas se comportam (nenhuma → aglutinante → fusional)

Isso permite combinações que a tabela clássica esconde, como uma língua polissintética aglutinante (Inuktitut) ou polissintética mais fusional (línguas iroquesas).

| Tipo clássico | `degree_of_synthesis` | `degree_of_fusion` |
|---|---|---|
| Isolante / Analítica | `isolating` | `none` |
| Aglutinante | `synthetic` | `agglutinative` |
| Fusional / Sintética | `synthetic` | `fusional` |
| Polissintética | `polysynthetic` | `agglutinative` ou `fusional` |

---

## Parâmetros da configuração

### `degree_of_synthesis`

| Valor | Descrição | Exemplo |
|---|---|---|
| `isolating` | ~1 morfema por palavra | Mandarim, Vietnamita |
| `synthetic` | Raiz + vários afixos | Latim, Turco, Português |
| `polysynthetic` | Sentença inteira em uma palavra | Inuktitut, Mohawk |

### `degree_of_fusion`

| Valor | Descrição | Exemplo |
|---|---|---|
| `none` | Sem afixos (apenas línguas isolantes) | Vietnamita |
| `agglutinative` | 1 morfema = 1 traço; fronteiras nítidas | Turco: *ev-ler-im-de* "nas minhas casas" |
| `fusional` | 1 morfema = vários traços | Latim: *-ōrum* = genitivo + plural |

### `affix_position` (alinhado ao WALS 26A)

| Valor | Descrição |
|---|---|
| `little_affixation` | Pouca ou nenhuma afixação (obrigatório para isolantes) |
| `strongly_suffixing` | Fortemente sufixante (o tipo mais comum) |
| `weakly_suffixing` | Fracamente sufixante |
| `equal` | Prefixos e sufixos equilibrados |
| `weakly_prefixing` | Fracamente prefixante |
| `strongly_prefixing` | Fortemente prefixante (ex: muitas línguas Bantu) |

### `active_processes`

| Valor | Descrição | Exemplo |
|---|---|---|
| `affixation` | Raiz + prefixo/sufixo | *feliz → in-feliz-mente* |
| `infixation` | Afixo inserido dentro da raiz | Tagalo: *sulat → s-um-ulat* |
| `circumfixation` | Afixo bipartido que cerca a raiz | Alemão: *spiel → ge-spiel-t* |
| `transfixation` | Raiz consonantal + padrão vocálico | Árabe: *k-t-b → kataba, kitāb* |
| `compounding` | Raiz + raiz | *guarda-chuva* |
| `noun_incorporation` | Nome incorporado ao verbo | Obrigatório em polissíntese |
| `reduplication_full` | Repetição total da raiz | Malaio: *orang-orang* "pessoas" |
| `reduplication_partial` | Repetição de sílaba/segmento | Tagalo: *sulat → su-sulat* |
| `apophony` | Alternância vocálica interna | Inglês: *sing → sang → sung* |
| `tonal_morphology` | Tom com função gramatical | Várias línguas africanas |

### `locus_of_marking` (WALS 23A–25A)

| Valor | Descrição |
|---|---|
| `dependent_marking` | Relações marcadas no dependente (casos nos nomes; padrão indo-europeu) |
| `head_marking` | Relações marcadas no núcleo (concordância no verbo) |
| `double_marking` | Marcação em ambos |
| `no_marking` | Sem marcação morfológica (típico de isolantes) |

---

## Regras de consistência

O modelo se valida sozinho, independentemente de como a configuração foi criada (CLI, sorteio ou JSON carregado manualmente).

**Erros** (contradições lógicas, a configuração é rejeitada):

- Fusão `none` se e somente se a língua for `isolating`
- Línguas isolantes não admitem morfemas presos (afixação, infixação, circunfixação, transfixação, incorporação)
- Línguas isolantes exigem `affix_position = little_affixation`, e só elas podem usá-lo
- Línguas sintéticas precisam de afixação ou transfixação
- Línguas polissintéticas exigem `noun_incorporation`
- Infixação e circunfixação pressupõem afixação ativa

**Avisos** (combinações raras, mas permitidas, já que uma conlang pode ser exótica de propósito):

- Transfixação com fusão aglutinante
- Polissíntese com marcação no dependente
- Língua isolante com algum tipo de marcação morfológica

---

## Interface com outros módulos

O módulo é isolado na configuração, mas expõe dois métodos para integração:

**`phonotactics_requirements()`** — o que a fonotática precisa fornecer:

| Condição | Requisito |
|---|---|
| `transfixation` ativa | Raízes como esqueletos consonantais (ex: CCC) |
| `tonal_morphology` ativa | Sistema tonal |
| `apophony` ativa | Conjuntos de alternância vocálica |
| Língua isolante | Raízes de no máximo 2 sílabas |

**`syntax_hints()`** — tendências translinguísticas (sugestões, não obrigações):

| Condição | Tendência |
|---|---|
| Sufixante | Ordem OV (verbo final) |
| Prefixante | Ordem VO |
| Marcação no núcleo | Pro-drop provável |
| Isolante | Ordem de palavras rígida |

---

## Uso

**Requisito:** Python ≥ 3.9 e pydantic ≥ 2

```bash
pip install pydantic
```

```bash
# Assistente interativo
python morphological_typology.py

# Sorteio ponderado
python morphological_typology.py --random

# Sorteio reprodutível com arquivo de saída
python morphological_typology.py --random --seed 42 -o minha_lingua.json
```

### Uso como biblioteca

```python
from morphological_typology import (
    MorphologicalTypologyConfig, sample_config,
    DegreeOfSynthesis, DegreeOfFusion, MorphologicalProcess,
)

# Perfil sorteado
config = sample_config(seed=42)

# Perfil manual (estilo turco)
turco = MorphologicalTypologyConfig(
    degree_of_synthesis=DegreeOfSynthesis.SYNTHETIC,
    degree_of_fusion=DegreeOfFusion.AGGLUTINATIVE,
    active_processes=[MorphologicalProcess.AFFIXATION,
                      MorphologicalProcess.COMPOUNDING],
)

# Carregar de JSON (validação automática)
with open("minha_lingua.json") as f:
    config = MorphologicalTypologyConfig.model_validate_json(f.read())

print(config.phonotactics_requirements())
print(config.syntax_hints())
```

### Exemplo de saída

```json
{
  "degree_of_synthesis": "synthetic",
  "degree_of_fusion": "fusional",
  "affix_position": "strongly_suffixing",
  "active_processes": [
    "affixation",
    "compounding",
    "transfixation"
  ],
  "locus_of_marking": "dependent_marking"
}
```

```
→ Requisitos para a fonotática: {'root_shape': 'consonantal_skeleton'}
→ Sugestões para a sintaxe:     {'word_order': 'OV (sufixação correlaciona com verbo final)'}
```

---

## Sorteio ponderado

O modo `--random` sorteia os parâmetros em cascata (síntese → fusão → posição → locus → processos), condicionando cada escolha às anteriores para manter o perfil plausível.

> **Atenção:** os pesos são aproximados. Os de `affix_position` seguem a ordem de grandeza do WALS 26A; os demais são ilustrativos e devem ser recalibrados com os CSVs do WALS.

---

## Features do WALS relacionadas

| Feature | Tema |
|---|---|
| 20A | Fusão de formativos flexionais |
| 21A | Exponência de formativos flexionais |
| 22A | Síntese flexional do verbo |
| 23A–25A | Locus de marcação |
| 26A | Prefixação vs. sufixação |
| 27A | Reduplicação |

Todas estão disponíveis em `github.com/cldf-datasets/wals` e podem ser cruzadas com o PHOIBLE via `Glottocode`.

---

## Próximos passos

- [ ] Recalibrar os pesos de sorteio com dados reais do WALS
- [ ] Módulo de categorias gramaticais (número, caso, gênero, pessoa, TAM, evidencialidade)
- [ ] Geração das tabelas de afixos a partir de tipologia + categorias
- [ ] Camada de coerência entre módulos (morfologia ↔ sintaxe ↔ fonotática)

---

## Referências

- Sapir, E. (1921) — *Language: An Introduction to the Study of Speech*
- Comrie, B. (1989) — *Language Universals and Linguistic Typology*, 2ª ed.
- Nichols, J. (1986) — *Head-marking and dependent-marking grammar*. Language 62(1)
- Dryer, M. S. & Haspelmath, M. (eds.) — *The World Atlas of Language Structures Online*. https://wals.info