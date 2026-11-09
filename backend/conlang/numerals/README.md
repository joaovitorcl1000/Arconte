# Módulo — Sistema numeral

Cria o **sistema de numerais** da conlang — o "Number base" e o "List numbers" do Vulgarlang —, com as bases das línguas reais e os ordinais.

```
   10  kya                /kja/              (10)
   13  yulqam em kya      /ˈjulŋam em kja/   (3 + 10)
   30  yulqam kya         /ˈjulŋam kja/      (3×10)
   37  le em yulqam kya   /le em ˈjulŋam kja/ (7 + 3×10)
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico (sândi), da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── numerals/
│   ├── numerals.py
│   └── README.md
└── languages/lang-31/
    ├── numerals.json     ← gerado
    └── numerals.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python numerals/numerals.py --language languages/lang-31
python numerals/numerals.py --language languages/lang-31 --base vigesimal --upto 40
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--base` | sorteada | `decimal`, `quinary`, `vigesimal`, `hybrid`, `restricted`, `body_part` |
| `--upto N` | `20` | Lista os numerais de 1 até N, além de exemplos maiores (30, 37, 99, 100, 256, 1000...) |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS (opcional) |
| `--no-wals` | — | Usa só as distribuições embutidas |

---

## Bases (WALS 131A)

| Base | Prob. | Como funciona | Exemplo real |
|---|---|---|---|
| **Decimal** | ~51% | 37 = 3×10 + 7 | português, mandarim |
| **Quinário-decimal** | ~15% | 6–9 formados a partir de 5: 7 = 5+2; 37 = 3×10 + 5+2 | muitas línguas da África e das Américas |
| **Híbrido** | ~11% | base 20 até 99 (90 = 4×20 + 10), decimal a partir de 100 | francês *quatre-vingt-dix* |
| **Vigesimal** | ~10% | base 20 em toda a escala (20, 400, 8.000); 11–19 = 10 + n | maia, iorubá |
| **Restrito** | ~10% | só 1 a 3, 4 ou 5; acima disso, 'muitos' | várias línguas da Amazônia e da Austrália |
| **Partes do corpo** | ~2% | depois de 5, os números são nomes de partes do corpo, contados ao longo dele (mão, braço, pescoço, orelha, olho, nariz, boca, cabeça) | línguas da Nova Guiné |

O quinário-decimal é sorteado como variante do decimal (20% dos decimais), já que o WALS o inclui na categoria "outra base". No sistema de partes do corpo, se o léxico tiver poucas partes do corpo, o módulo usa o restrito.

### Palavras

- Os numerais **1 a 5 do léxico** são reaproveitados; os demais (6–9, 10, 20, 100, 1000...) são palavras novas, de uma ou duas sílabas, diferentes de todas as palavras do léxico.
- No sistema restrito, 'muitos' é a palavra *many* do léxico.

## Composição

Três escolhas sorteadas por língua:

| Escolha | Opções | Prob. |
|---|---|---|
| Multiplicação | 'três-dez' = 30 (multiplicador antes) / 'dez-três' | 75% / 25% |
| Soma | 'trinta-e-sete' (maior antes) / 'sete-e-trinta' (menor antes, como no alemão e no árabe) | 70% / 30% |
| Forma | numa palavra só, com o sândi da língua (como *treze*) / em palavras separadas | 50% / 50% (sempre separadas em línguas isolantes e tonais) |

**Sem ambiguidade:** se a ordem da soma e a da multiplicação forem opostas, 13 ('três dez') e 30 ('três dez') ficariam iguais. Nesse caso, a soma ganha sempre um **conectivo** — a palavra *and* do léxico, se existir —, como em 13 = 'três **e** dez'. Nas outras configurações, o conectivo aparece em 30% das línguas.

## Ordinais (WALS 53A)

| Tipo | Exemplo real |
|---|---|
| 'primeiro' supletivo, os demais derivados | inglês *first*, *fourth* (o mais comum) |
| 'primeiro' e 'segundo' supletivos, os demais derivados | português *primeiro*, *segundo*, *terceiro* |
| todos derivados ('um-ésimo', 'dois-ésimo') | — |
| só 'primeiro' especial, os demais iguais aos cardinais | — |
| iguais aos cardinais | — |
| sem ordinais | — |

Os ordinais derivados usam um afixo (prefixo ou sufixo, conforme a afixação da língua) ou, nas línguas isolantes, uma partícula.

---

## Saídas

### `numerals.md`

```markdown
- Base: decimal (base 10)
- Ordem: multiplicador antes da base ('três-dez' = 30); menor antes ('sete-e-trinta', como no alemão)
- Numerais compostos em palavras separadas, ligados por *em* ('e')
- Ordinais: 'primeiro' ou 'um-ésimo'; os demais derivados

| Número | Numeral | Pronúncia | Composição |
|---|---|---|---|
| 1 | **gro** | /ɡro/ | 1 |
| 13 | **yulqam em kya** | /ˈjulŋam em kja/ | 3 + 10 |
| 30 | **yulqam kya** | /ˈjulŋam kja/ | 3×10 |
```

Seguido da tabela de ordinais (1º a 5º).

### `numerals.json`

```json
{
  "settings": {"base": "decimal", "multiplier_first": true, "high_first": false,
               "connective": ["e", "m"], "compound": false, "ordinal_code": "5",
               "ordinal": {"type": "derived", "affix": ["u"], "position": "suffix", "first": ["k", "o", "n", "h", "uː", "n"]}},
  "atoms": {"1": {"form": "ɡro", "from": "lexicon", "written": "gro", "...": "..."},
            "10": {"form": "kja", "from": "new", "...": "..."}},
  "cardinals": [{"n": 13, "written": "yulqam em kya", "ipa": "julŋam em kja",
                 "pronunciation": "ˈjulŋam em kja", "gloss": "3 + 10", "parts": 3}],
  "ordinals": [{"n": 1, "written": "konhuun", "gloss": "first (supletivo)", "...": "..."}],
  "metadata": {"seed": 1234567, "sources": {"131A": "WALS 131A (embutido)"},
               "notes": ["conectivo obrigatório na soma, para distinguir 13 de 30"], "new_words": 7}
}
```

`atoms` são as palavras simples do sistema (de onde vêm todos os compostos); `from` diz se a palavra veio do léxico ou é nova.

### Uso como biblioteca

```python
from pathlib import Path
import numerals

b = numerals.NumeralBuilder(Path("languages/lang-31"))
data = b.build()            # ou b.build("vigesimal", upto=40)

b.number(1984)              # qualquer número
b.ordinal(3)                # 'terceiro'
```

---

## Testes

70 línguas geradas, cada uma com a base sorteada e com as seis bases forçadas (490 sistemas): nenhum erro, nenhum numeral repetido entre números diferentes, e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional, seção no `grammar.md` e numerais no dicionário)
- [ ] Subtração (latim *duodeviginti* 'dois-de-vinte' = 18) e números acima de 8.000 no vigesimal
- [ ] Numerais distributivos ('dois a dois') e multiplicativos ('duas vezes')
- [ ] Classificadores numerais junto com os números, nas línguas que os têm
- [ ] Concordância do numeral com o gênero do nome
