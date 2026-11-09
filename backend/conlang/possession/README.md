# Módulo — Posse e determinantes

Completa o sintagma nominal da conlang com o que o Vulgarlang mostra nas tabelas "Possession" e "Articles": **possessivos** ('meu', 'teu'...), **posse entre nomes** ('o cão da mulher'), **alienabilidade** ('minha mão' ≠ 'minha casa') e **artigos no plural**.

```
puum plaa      /puːm plaː/       'my dog'      (classificador de posse + nome)
iiyugyuwim     /iːˈjuɡjuwim/     'my hand'     (posse direta no nome)
ozwuun plaa    /ˈozwuːn plaː/    'the woman's dog'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico (sândi e flexão), da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── possession/
│   ├── possession.py
│   └── README.md
└── languages/lang-31/
    ├── possession.json     ← gerado
    └── possession.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python possession/possession.py --language languages/lang-31
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS (opcional) |
| `--no-wals` | — | Usa só as distribuições embutidas |

A pasta precisa ter inventário, fonotática, categorias, morfologia e léxico. Com `orthography.json` e `stress.json`, as formas saem escritas e acentuadas.

---

## Decisões

### 1. Possessivos (WALS 57A)

Sorteados **condicionados ao tipo de afixação** da língua (WALS 26A × 57A): línguas sufixantes tendem a ter sufixos possessivos; línguas de pouca afixação, possessivos livres. Línguas isolantes nunca têm afixos.

| Estratégia | Exemplo real | Forma |
|---|---|---|
| Afixos de posse | turco *ev-im* 'minha casa' | prefixo ou sufixo no nome, um por pessoa da tabela de pronomes |
| Pronome no genitivo | finlandês *minu-n* 'de mim' | o pronome flexionado no caso genitivo da língua |
| Pronome + partícula | mandarim *wǒ de* | pronome + uma partícula de posse nova |
| Palavras próprias | inglês *my*, *your* | uma palavra possessiva nova para cada pessoa |

Há uma forma para **cada célula da tabela de pronomes**, incluindo dual, paucal, inclusivo/exclusivo e gênero na 3ª pessoa, quando a língua os tem. Em metade das línguas com afixos, eles são **reduzidos dos próprios pronomes** (como os afixos reais costumam ser, gramaticalizados a partir deles).

### 2. Posse entre nomes (WALS 24A)

| Locus | 'o cão da mulher' |
|---|---|
| No possuidor | *mulher-GEN cão* (caso genitivo; só se a língua tem genitivo) |
| No possuído | *mulher cão-POSS*, como o *wad-e* do Vulgarlang; se a língua tem afixos possessivos, a marca é o próprio afixo de 3ª pessoa, como no turco *adam-ın köpeğ-i* |
| Nos dois | *mulher-GEN cão-POSS* |
| Partícula de ligação | *mulher LIG cão* (quando não há genitivo) |
| Nenhuma | *mulher cão* (justaposição) |

A ordem possuidor/possuído segue a posição do genitivo decidida na sintaxe.

### 3. Alienabilidade (WALS 59A) e posse obrigatória (58A)

| Classes | Comportamento |
|---|---|
| 1 | Todo nome é possuído do mesmo jeito |
| 2 | **Inalienáveis** (partes do corpo e parentes) recebem a marca de posse diretamente; **alienáveis** (os demais) usam um **classificador de posse**, e é o classificador que recebe a marca: *CLF-meu cão*, como nas línguas oceânicas |
| 3 | Como acima, com um segundo classificador para comida e bebida |

Em algumas línguas com alienabilidade e afixos possessivos, partes do corpo e parentes são **sempre possuídos**: sem possuidor definido, recebem um afixo de 'de alguém' (como 'mão-de-alguém' em várias línguas indígenas americanas).

### 4. Artigos no plural

Se a língua tem artigos livres e número gramatical, em 45% dos casos os artigos **flexionam em número** (*the/some* do Vulgarlang): cada artigo ganha uma forma nova para cada número não singular. Nos demais, o artigo é invariável. Línguas sem artigos livres (sem artigo, ou com artigo afixal) não têm esta seção.

---

## Saídas

### `possession.md`

```markdown
- Possessivos: afixos de posse no nome (sufixos)
- Posse entre nomes: marca no possuidor (caso genitivo)
- Posse inalienável (partes do corpo e parentes) marcada no próprio nome; nos demais,
  a marca vai no classificador de posse puu

## Possessivos

| Pessoa | Possessivo | Pronúncia | Plural |
|---|---|---|---|
| 1SG ('my dog') | **puum plaa** | /puːm plaː/ | **puum plaami** |
| 2SG ('your dog') | **puulo plaa** | /ˈpuːlo plaː/ | **puulo plaami** |

## Alienabilidade

- **iiyugyuwim** /iːˈjuɡjuwim/ — 'my hand' (inalienable)
- **puum plaa** /puːm plaː/ — 'my dog' (alienable)

## Posse entre nomes

- **ozwuun plaa** /ˈozwuːn plaː/ — 'the woman's dog'

## Artigos

| Artigo | singular | plural |
|---|---|---|
| definite | **fli** | **kuujs** |
```

### `possession.json`

```json
{
  "settings": {
    "pronominal": {"strategy": "affix", "position": "suffix", "from_pronouns": false,
                   "forms": {"1.singular": ["m"], "2.singular": ["l", "o"], "...": "..."}},
    "nominal": {"locus": "dependent", "possessor_position": "before"},
    "alienability": {"classes": 2, "inalienable_fields": ["Kinship", "The body"],
                     "alienable_marker": ["p", "uː"]},
    "articles": null
  },
  "examples": {
    "pronominal": [{"cell": "1.singular", "english": "my dog", "written": "puum plaa",
                    "ipa": "puːm plaː", "pronunciation": "puːm plaː", "class": "alienable",
                    "plural": {"...": "..."}}],
    "alienability": ["..."],
    "nominal": {"english": "the woman's dog", "written": "ozwuun plaa", "...": "..."}
  },
  "metadata": {"seed": 1234567, "sources": {"possessive_affixes": "WALS 57A|26A=2 (embutido)"},
               "notes": [], "lexemes": {"possessed": "dog", "inalienable": "hand", "possessor": "woman"}}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import possession

b = possession.PossessionBuilder(Path("languages/lang-31"))
data = b.build()                            # decide e gera os exemplos

dog = b.entries["DOG"]
b.possess(dog, "2.plural")                  # 'your (pl.) dog'
b.possess(dog, "1.singular", "plural")      # 'my dogs'
b.nominal(b.entries["WOMAN"], dog)          # 'the woman's dog'
```

---

## Testes

60 línguas geradas (incluindo isolantes, tonais, de raízes consonantais e com gênero): nenhum erro, todas as estratégias aparecendo (afixos em 82% das línguas, como esperado para línguas majoritariamente sufixantes), e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional e seção no `grammar.md`), junto com o módulo de comparação
- [ ] O afixo possessivo vai sempre por fora da flexão do nome (*cão-PL-MEU*); a ordem real varia entre línguas (no turco, *ev-ler-im-de*: plural, posse, caso)
- [ ] Em línguas tonais, classificadores e possessivos novos ainda não recebem tom próprio
- [ ] Pronomes possessivos independentes ('é meu', 'o meu')
- [ ] Concordância do possessivo com o gênero do possuído (como *meu*/*minha*)
