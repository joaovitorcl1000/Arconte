# Módulo — Comparação

Completa a gramática dos adjetivos com **comparativo** ('maior que'), **superlativo** ('o maior') e **equativo** ('tão grande quanto'), como a tabela "Adjectives" do Vulgarlang (*heq-æd* 'bigger', *heq-ax* 'biggest') — mas com as estratégias das línguas reais, e não só a do português e do inglês.

```
plaa  twukuubu   twaawi
plaː  twukuː-bu  twaː-wi
dog   fish-ABL   big-COMPR
'The dog is bigger than the fish.'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico (sândi e flexão), da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── comparison/
│   ├── comparison.py
│   └── README.md
└── languages/lang-31/
    ├── comparison.json     ← gerado
    └── comparison.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python comparison/comparison.py --language languages/lang-31
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS (opcional) |
| `--no-wals` | — | Usa só as distribuições embutidas |

A pasta precisa ter inventário, fonotática, categorias, morfologia, léxico e sintaxe. Com `orthography.json` e `stress.json`, as formas saem escritas e acentuadas.

Os afixos e partículas novos nunca repetem formas que a língua já tem: palavras do léxico, pronomes, afixos nominais e verbais, partículas da sintaxe e, se o módulo de posse já tiver rodado, os possessivos e classificadores dele. Por isso, rode a posse **antes** da comparação (o orquestrador faz isso nessa ordem).

---

## Estratégias do comparativo (WALS 121A)

Sorteadas **condicionadas à ordem básica** da língua (WALS 81A × 121A), que é a correlação mais forte conhecida para comparativos:

| Estratégia | Como funciona | SOV | SVO |
|---|---|---|---|
| **Locativa** | o termo comparado vai num caso de origem ou lugar (ablativo, locativo...) ou com uma adposição: 'o cão é grande do peixe' | 71% | 20% |
| **De superar** | um verbo 'superar': 'o cão é grande, supera o peixe' | 4% | 53% |
| **Conjunta** | duas orações com antônimos: 'o cão é grande, o peixe é pequeno' | 20% | 14% |
| **Partícula** | uma partícula 'que' junto ao termo comparado, como no português | 5% | 14% |

Detalhes de cada uma:

- **Locativa:** usa o primeiro caso disponível entre ablativo, locativo, alativo e essivo; sem nenhum deles, cria uma adposição.
- **De superar:** cria um verbo novo, glosado *exceed*.
- **Conjunta:** usa o antônimo do adjetivo, se ele existir no léxico (*big*/*small*, *good*/*bad*, *old*/*new*...), e a conjunção *and*.
- **Partícula:** cria uma partícula nova, glosada *than*, antes ou depois do termo comparado conforme a língua tenha preposições ou posposições.

### Grau no adjetivo

O adjetivo pode receber uma marca de comparativo, como o *-er* do inglês. A chance depende da estratégia: 60% com partícula (o padrão europeu), 20% na locativa, 5% na de superar e nunca na conjunta.

| Tipo | Exemplo |
|---|---|
| Afixo | *twaa-wi* 'big-COMPR'; prefixo ou sufixo conforme a língua; línguas isolantes nunca têm |
| Palavra | 'more big', como o *mais* do português |
| Nenhum | o adjetivo fica igual; só a construção mostra a comparação |

### Superlativo

| Tipo | Exemplo |
|---|---|
| Afixo | *twaa-il* 'big-SUPL' (só se o comparativo também for afixo) |
| Universal | 'maior que todos', a estratégia mais comum no mundo |
| Palavra | 'the most big' |
| Intensificador | 'very big', quando a língua não distingue superlativo de 'muito' |

### Equativo

'Tão grande quanto': uma partícula nova glosada *as* ou, se a língua tem caso comitativo ou essivo, o termo comparado nesse caso ('grande com o peixe').

### Ordem

Em línguas OV, o termo comparado vem antes do adjetivo ('peixe-ABL grande'); em línguas VO, depois ('grande que peixe'), seguindo as correlações de Greenberg. A cópula entra se a sintaxe da língua tiver uma.

---

## Saídas

### `comparison.md`

```markdown
- Comparativo: locativa (o termo comparado vai num caso ou adposição de origem/lugar)
- Termo comparado no caso ablative
- Grau comparativo no adjetivo: -wi
- Superlativo: afixo -uq
- Equativo: partícula ('como') qon

## Formas do adjetivo

| Grau | Forma | Pronúncia |
|---|---|---|
| Positivo | **twaa** | /twaː/ |
| Comparativo | **twaawi** | /ˈtwaːwi/ |
| Superlativo | **twaauq** | /ˈtwaːuŋ/ |

## Comparativo

**Plaa twukuubu twaawi.**
```

Seguido das três frases (comparativo, superlativo, equativo) com glosa interlinear e, nas estratégias menos familiares, a tradução literal: *(literalmente: 'the dog is big, it exceeds the fish')*.

### `comparison.json`

```json
{
  "settings": {
    "strategy": "locational",
    "standard_case": "ablative",
    "degree": {"type": "affix", "position": "suffix", "comparative": ["w", "i"]},
    "superlative": {"type": "affix", "position": "suffix", "form": ["u", "ŋ"]},
    "equative": {"type": "particle", "form": ["ŋ", "o", "n"]}
  },
  "forms": {"positive": ["..."], "comparative": ["..."], "superlative": ["..."]},
  "sentences": [
    {"key": "comparative", "title": "Comparativo",
     "words": [{"written": "plaa", "ipa": "plaː", "pronunciation": "plaː", "seg": "plaː", "gloss": "dog"}],
     "translation": "The dog is bigger than the fish.", "literal": null}
  ],
  "metadata": {"seed": 1234567, "sources": {"comparative": "WALS 121A|81A=1 (embutido)"},
               "notes": [], "lexemes": {"adjective": "big", "compared": "dog", "standard": "fish"}}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import comparison

b = comparison.ComparisonBuilder(Path("languages/lang-31"))
data = b.build()

big = b.entries["BIG"]
b.adjective(big, "comparative")      # [{'written': 'twaawi', 'gloss': 'big-COMPR', ...}]
b.sentences(b.entries["WOMAN"], b.entries["STONE"], big)
```

---

## Testes

70 línguas geradas (incluindo isolantes, tonais e de raízes consonantais): nenhum erro, todas com frases de exemplo, e a mesma semente gerando o mesmo arquivo. A distribuição seguiu o esperado para línguas majoritariamente SOV: 64% locativa, 19% de superar, 9% partícula e 9% conjunta.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional e seção no `grammar.md`), junto com o módulo de posse
- [ ] Em línguas tonais, adjetivos com afixo de grau perdem o tom lexical
- [ ] Concordância do adjetivo comparado com o nome (gênero, número)
- [ ] Comparação de verbos e advérbios ('corre mais rápido')
- [ ] Formas supletivas ('bom' → 'melhor'), que entram junto com as irregularidades