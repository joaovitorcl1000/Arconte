# Módulo — Vocabulário ampliado

Amplia o léxico da conlang com a lista do **WOLD** (World Loanword Database, Haspelmath & Tadmor 2009): cerca de 1.460 significados em 24 campos semânticos, mapeados no Concepticon. Somado ao léxico básico, às derivadas e aos numerais, a língua passa de ~400 para ~1.600 palavras.

Em vez de sortear uma raiz nova para cada significado, o módulo forma parte das palavras **com os recursos da própria língua**, como as línguas reais fazem:

```
yiiwa          /ˈjiːwa/        'tailor'      ← yii 'sew' (agentivo)
globomsĩmgo    /ˌɡlobomˈsĩmɡo/ 'wedding'     ← globomsĩm 'marry' (ação)
mamal          /ˈmamal/        'darkness'    ← mam 'dark' (qualidade)
uundruozwuu    /uːnˈdruozwuː/  'young woman' = uundru 'young' + ozwuu 'woman'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico, da derivação, da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── vocabulary/
│   ├── vocabulary.py
│   ├── wold_1460.tsv       ← a lista de conceitos (precisa ficar junto)
│   └── README.md
└── languages/lang-31/
    ├── vocabulary.json     ← gerado
    └── vocabulary.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9). O `wold_1460.tsv` é um recorte da lista `Haspelmath-2009-1460` do Concepticon (ID, gloss, inglês, classe, campo semântico e pontuações do WOLD).

---

## Uso

```bash
python vocabulary/vocabulary.py --language languages/lang-31
python vocabulary/vocabulary.py --language languages/lang-31 --include-modern
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--include-modern` | — | Inclui o campo "mundo moderno" (carro, rádio, eletricidade...), deixado de fora por padrão, como o "sci-fi vocab" do Vulgarlang |
| `--list PATH` | `wold_1460.tsv` | Outra lista de conceitos no mesmo formato |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |

A pasta precisa ter inventário, fonotática, categorias, morfologia e léxico. Com `derivation.json`, as palavras derivadas usam os processos da língua; com `orthography.json` e `stress.json`, saem escritas e acentuadas. Rode este módulo **depois** da derivação e dos numerais.

---

## Como cada palavra é formada

Os significados que já estão no léxico básico (cerca de 200) e os numerais (que ficam com o módulo de numerais) são pulados. Para os demais:

### 1. Derivação

Cerca de 50 significados que as línguas costumam formar por derivação têm a base e o processo indicados:

| Processo | Exemplos |
|---|---|
| Agentivo | tailor ← sew; teacher ← teach; thief ← steal; witness ← see; farmer ← plant |
| Ação | wedding ← marry; murder ← kill; judgment ← judge; beginning ← begin |
| Produto | song ← sing; wound ← injure; swelling ← swell; damage ← destroy |
| Qualidade | darkness ← dark; age ← old |
| Resultativo | broken ← break; cooked ← cook |
| Proprietivo / privativo | salty ← salt; dirty ← dust; blind ← eye; deaf ← ear; naked ← clothes; poor ← money |
| Instrumento | knife ← cut; broom ← sweep; key ← lock; hammer ← hit; bridge ← cross |
| Lugar | bed ← sleep; market ← buy; grave ← bury; school ← study; temple ← pray |
| Causativo | teach ← know; show ← see; burn (algo) ← burn (intransitivo) |
| Relacional / advérbio | holy ← deity; early ← morning; often ← many |

A derivação usa **os processos que a língua tem** (do `derivation.json`), com as mesmas formas. Se a língua não tiver o processo certo:

- agentivo, instrumento, lugar e produto viram **compostos com uma palavra genérica** ('costurar-pessoa', 'cortar-coisa', 'dormir-casa');
- os demais viram **raízes novas**.

### 2. Composição

- **Expressões de duas palavras** do inglês, quando as duas partes existem na língua: *young man*, *old woman*, *older brother* (*older* → *old*), *head louse*, *mother's brother*, *high tide*...
- **Compostos que o inglês escreve juntos:** *fishhook* = fish + hook; *firefly* = fire + fly; *earring* = ear + ring; *grandfather* = old + father; *fisherman* = fish + person...

A ordem segue a dos compostos da língua (núcleo no fim ou no começo), e as partes se unem pelo sândi. Nas línguas tonais, se a fronteira não sofre sândi, cada parte mantém seus tons.

### 3. Raiz nova

Todo o resto. O tamanho segue uma aproximação da lei de Zipf: significados mais básicos e menos analisáveis (pela pontuação de simplicidade do WOLD) tendem a ter menos sílabas. Nenhuma raiz nova coincide com uma palavra já existente, nem depois da flexão e do sândi.

### Classe, gênero e transitividade

- **Classe:** a do WOLD; adjetivos viram verbos estativos nas línguas de adjetivos verbais.
- **Gênero e classe nominal:** compostos e derivados herdam os do núcleo ou da base; raízes novas recebem os mais comuns no mesmo campo semântico.
- **Transitividade dos verbos novos:** estimada pelo campo semântico (ações, posse, guerra, comida → transitivos; movimento, emoções → intransitivos).

---

## Saídas

### Terminal

```
VOCABULÁRIO AMPLIADO — 1188 palavras novas (18 derivadas, 52 compostas, 1118 raízes)
    drayune                /ˈdrajune/      'low tide' = dra + yune
    mamal                  /ˈmamal/        'darkness' ← mam (qualidade)
    uundrupraasye          /uːnˈdrupraːsje/ 'young man' = uundru + praasye
    yiiwa                  /ˈjiːwa/        'tailor' ← yii (agentivo)
```

### `vocabulary.md`

1. Resumo e quantidade de palavras por campo semântico
2. Todas as palavras novas no formato do dicionário, com a origem: `**yiiwa** /ˈjiːwa/ *n.* 'tailor' ← *yii* (agentivo)`

### `vocabulary.json`

```json
{
  "entries": [
    {"id": "...", "gloss": "TAILOR", "english": "the tailor", "label": "tailor", "pos": "noun",
     "field": "Clothing and grooming", "root": ["j", "iː", "w", "a"], "form": "jiːwa",
     "formation": "derived", "source": {"base": "SEW", "base_written": "yii", "process": "agentive"},
     "gender": null, "class": null, "citation": "jiːwa", "written": "yiiwa", "pronunciation": "ˈjiːwa"}
  ],
  "stats": {"total": 1188, "root": 1118, "derived": 18, "compound": 52, "by_field": {"The body": 123, "...": "..."}},
  "metadata": {"seed": 1234567, "list": "Haspelmath-2009-1460 (WOLD)", "lexicon_size": 231,
               "include_modern": false, "used_derivation": true}
}
```

As entradas têm o mesmo formato das do `lexicon.json` (raiz, forma, citação, classe, gênero), para que outros módulos — como o tradutor — possam usá-las da mesma forma.

### Uso como biblioteca

```python
from pathlib import Path
import vocabulary

b = vocabulary.VocabularyBuilder(Path("languages/lang-31"))
data = b.build(include_modern=False)
tailor = next(e for e in data["entries"] if e["gloss"] == "TAILOR")
```

---

## Testes

40 línguas geradas (incluindo tonais e de raízes consonantais), 47 mil palavras novas: nenhum erro, praticamente nenhuma forma repetida (1 em 47 mil), rótulos únicos, e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional e palavras no dicionário do `grammar.md`)
- [ ] Ampliar a lista de derivações previstas (hoje cerca de 50) e reconhecer mais padrões do inglês
- [ ] Colexificações também no vocabulário ampliado (como 'árvore' = 'madeira')
- [ ] Mudanças sonoras e irregularidades também nas palavras novas (hoje aplicadas ao léxico básico, às derivadas e aos nomes)
- [ ] Outras listas grandes do Concepticon, até chegar às ~4.000 palavras do Vulgarlang
