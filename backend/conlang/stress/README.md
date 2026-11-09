# Módulo — Acento

Decide o **sistema de acento** da conlang com distribuições do WALS e marca a sílaba tônica nas palavras, como o "Stress pattern" do Vulgarlang:

```
akiʃontaŋ  →  /ˌakiˈʃontaŋ/
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa o silabificador público do módulo de fonotática.

---

## Onde colocar

```
conlang/
├── stress/
│   ├── stress.py
│   └── README.md
└── languages/lang-31/
    ├── stress.json       ← gerado
    └── stress.md         ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python stress/stress.py --language languages/lang-31
python stress/stress.py --language languages/lang-31 --rule penultimate
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--rule` | sorteada | Força uma regra (lista abaixo) |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua, como nos outros módulos |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS (opcional) |
| `--no-wals` | — | Usa só as distribuições embutidas |

O módulo lê da pasta da língua o inventário (vogais longas e tons), a fonotática (codas e silabificação), o léxico (exemplos e dicionário) e o manifesto (semente).

---

## Sistemas de acento

### 1. Ausente

Em línguas tonais, o acento é sorteado como ausente em 60% dos casos (aproximação: nessas línguas, a proeminência costuma vir do tom). As palavras ficam sem marca.

### 2. Fixo (WALS 14A)

| Regra | Prob. entre as fixas | Exemplo real |
|---|---|---|
| `penultimate` | 39% | polonês, suaíli |
| `initial` | 33% | finlandês, húngaro |
| `ultimate` | 18% | francês, turco |
| `second` | 6% | dakota |
| `antepenultimate` | 4% | macedônio |
| `third` | <1% | — |

### 3. Sensível ao peso (WALS 15A e 16A)

A sílaba tônica depende de quais sílabas são **pesadas**. O que conta como pesado também é sorteado (16A), entre as opções que a língua permite:

| Peso | Condição |
|---|---|
| `long_vowel` | sílaba com vogal longa (exige vogais longas no inventário) |
| `coda` | sílaba com consoante em coda (exige codas na fonotática) |
| `either` | qualquer uma das duas |

| Regra | Como funciona |
|---|---|
| `left_edge` | primeira sílaba; a segunda, se a primeira for leve e a segunda pesada |
| `left_oriented` | primeira sílaba pesada entre as três primeiras; senão, a primeira |
| `right_edge` | última sílaba se for pesada; senão, a penúltima |
| `right_oriented` | penúltima se for pesada; senão, a antepenúltima (a regra do latim) |
| `unbounded_left` | primeira sílaba pesada da palavra; sem nenhuma, a primeira |
| `unbounded_right` | última sílaba pesada da palavra; sem nenhuma, a última |
| `combined` | última sílaba pesada da palavra; sem nenhuma, a penúltima |

Uma língua sem codas e sem vogais longas não pode ter acento sensível ao peso; nesse caso, o módulo escolhe entre os sistemas possíveis e registra a nota.

### 4. Lexical

O acento é **imprevisível**: cada palavra tem sua sílaba tônica, como no russo. A posição é sorteada por palavra, com preferência pela penúltima e pela primeira, mas de forma estável: a mesma palavra recebe sempre o mesmo acento, sem precisar armazenar nada.

### Ritmo (WALS 17A)

Em palavras de quatro sílabas ou mais, acentos secundários (ˌ) podem aparecer a cada duas sílabas:

| Ritmo | Direção |
|---|---|
| `trochaic` | da tônica para o início da palavra (*ˌakiˈʃontaŋ*) |
| `iambic` | da tônica para o fim |
| `none` | sem acento secundário |

---

## Saídas

### Terminal

```
ACENTO — sensível ao peso
  Acento na penúltima se ela for pesada; senão, na antepenúltima (regra do latim);
  sílaba pesada = sílaba com consoante em coda; ritmo trocaico.
    kimʃwiːhuŋ         /ˈkimʃwiːhuŋ/
    klemkopuklaːm      /klemˈkopuklaːm/
```

### `stress.md`

1. Sistema e descrição da regra
2. Exemplos com a divisão silábica e a pronúncia acentuada
3. O dicionário inteiro com acento: `/ˌakiˈʃontaŋ/ 'person'`

### `stress.json`

```json
{
  "system": "weight_sensitive",
  "rule": "right_oriented",
  "heavy": "coda",
  "rhythm": "trochaic",
  "description": "Acento na penúltima se ela for pesada; senão, na antepenúltima (regra do latim); ...",
  "examples": [{"ipa": "kimʃwiːhuŋ", "stressed": "ˈkimʃwiːhuŋ"}],
  "metadata": {"seed": 1234567, "sources": {"14A": "WALS 14A (embutido)"}, "notes": []}
}
```

`system` vale `fixed`, `weight_sensitive`, `lexical` ou `none`.

### Uso como biblioteca

```python
import json, stress

d = "languages/lang-31/"
inv = json.load(open(d + "phonemic_inventory.json"))
rules = json.load(open(d + "phonotactics.json"))

spec = stress.build(inv, rules, seed=1)          # ou rule="penultimate"
st = stress.Stress(spec, inv, rules, seed=1)

st.mark("akiʃontaŋ")                      # 'ˌakiˈʃontaŋ'
st.syllabify("akiʃontaŋ")                 # [['a'], ['k','i'], ['ʃ','o','n'], ['t','a','ŋ']]
st.primary(st.syllabify("akiʃontaŋ"))     # 2
```

Formas tonais (*ma˥.ku˩*) mantêm os tons e a divisão silábica já indicada pelos pontos.

---

## Testes

223 línguas geradas (52 mil palavras): nenhum erro; toda palavra polissilábica recebeu exatamente um acento primário; a marcação nunca altera os fonemas; e a mesma semente gera o mesmo arquivo. Nas línguas de teste, a distribuição ficou em 48% fixo, 34% sensível ao peso, 4% lexical e 14% ausente.

---

## Limitações e próximos passos

- [ ] Mostrar o acento no `grammar.md` e no dicionário principal (próxima etapa, no orquestrador, junto com a ortografia)
- [ ] Acento gráfico na ortografia, nas línguas de acento lexical (como o *é* do espanhol)
- [ ] Acento que se desloca com a flexão (ex: sufixos que atraem o acento)
- [ ] Redução de vogais átonas e outros efeitos fonológicos do acento
- [ ] Acento de frase e entonação
