# Módulo — Ortografia

Cria uma **grafia prática** para a conlang: escolhe uma letra ou dígrafo para cada fonema, num estilo coerente, garante que a escrita possa ser lida de volta sem ambiguidade e marca os tons com diacríticos. É o equivalente às "regras de ortografia" do Vulgarlang.

```
/t̠ʃupaŋ/  →  chupang   (estilo inglês)
              čupaŋ     (diacríticos)
              cupaq     (econômico)
              chupang   (românico)
```

O módulo **não altera nenhum outro**: só lê os JSONs da língua.

---

## Onde colocar

```
conlang/
├── orthography/
│   ├── orthography.py
│   └── README.md
└── languages/lang-31/
    ├── orthography.json     ← gerado
    └── orthography.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

Com uma língua gerada pelo orquestrador (lê e grava na pasta da língua):

```bash
python orthography/orthography.py --language languages/lang-31
python orthography/orthography.py --language languages/lang-31 --style diacritics
```

Isoladamente, como os demais módulos:

```bash
python orthography/orthography.py --inventory phonemic_inventory/phonemic_inventory.json
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — | Pasta de uma língua (`languages/lang-31`) |
| `--inventory PATH` | `../phonemic_inventory/phonemic_inventory.json` | Inventário, quando usado sem `--language` |
| `--style` | sorteado | `english`, `diacritics`, `economic` ou `romance` |
| `--seed N` | derivada | Semente; com `--language`, é derivada da semente da língua, como nos outros módulos |
| `-o PATH` | `orthography.json` | Arquivo JSON de saída |

Com `--language`, o módulo também usa (se existirem) a fonotática, o léxico, a sintaxe e o manifesto da língua: a fonotática para saber quais sequências de sons realmente ocorrem, e os demais para o dicionário, as frases e o nome da língua.

---

## Estilos

| Estilo | Prob. | /ʃ/ | /t̠ʃ/ | /ŋ/ | /ɲ/ | /j/ | /x/ | Vogal longa |
|---|---|---|---|---|---|---|---|---|
| `english` | 35% | sh | ch | ng | ny | y | kh | aa |
| `diacritics` | 25% | š | č | ŋ | ň | j | x | ā |
| `economic` | 20% | x | c | q | ny | y | h | aa |
| `romance` | 20% | x | ch | ng | nh | i/y | j | aa |

Vogais sem letra própria recebem diacríticos (ɛ → *è*, ə → *ë*, ɨ → *ï* no estilo inglês; ɨ → *y* no de diacríticos, como no polonês). Modificadores viram letras ou marcas: aspiração → *h* (*ph*, *kh*), labialização → *w*, palatalização → *y* ou *j*, nasalidade → til (*ã*), ejetivas → *ʼ*. Diacríticos de articulação fina (dental, apical, retraído) são ignorados, a menos que causem colisão.

### Como as letras são escolhidas

1. Os fonemas mais frequentes escolhem primeiro, então /i/ fica com *i* e /ɪ/ com *ì*.
2. Cada fonema tenta suas grafias na ordem de preferência do estilo; se uma já estiver ocupada, passa para a próxima.
3. Quando nenhuma grafia do estilo está livre, recebe a letra-base com ponto ou traço embaixo (*ṭ*, *ṯ*); em último caso, o próprio símbolo IPA.

---

## Sem ambiguidade

Toda grafia precisa poder ser lida de volta. Se dois fonemas escritos juntos formarem a grafia de um terceiro (s + h = *sh* = /ʃ/), o módulo resolve em duas etapas:

1. **Troca o dígrafo** por outra grafia do mesmo estilo, quando existe (no românico, /ɲ/ passa de *nh* para *ñ* se *n* + *h* puder ocorrer).
2. **Usa um separador** (`·`) só nas palavras em que a sequência ambígua aparece: *n·g* para /n/ + /ɡ/ numa língua onde *ng* é /ŋ/, como o *l·l* do catalão.

Com `--language`, a verificação considera só as sequências que a fonotática permite; uma ambiguidade entre sons que nunca ficam lado a lado é ignorada. A segmentação respeita os limites de sílaba: em *mod.zəl*, o *d* e o *z* são dois fonemas, mesmo que /dz/ exista.

---

## Tons

| Tom | Marca |
|---|---|
| Alto (˦, ˥) | agudo: *á* (agudo duplo *a̋* para o extra-alto, se ambos existem) |
| Médio (˧) | sem marca |
| Baixo (˨, ˩) | grave: *à* (grave duplo *ȁ* para o extra-baixo) |
| Descendente (˥˩, ˦˨...) | circunflexo: *â* |
| Ascendente (˩˥, ˨˦...) | caron: *ǎ* |

A marca vai na primeira vogal da sílaba. Uma marca nunca é usada se já aparece em alguma letra da língua (o grave de *è*, o caron de *š*): nesse caso o tom recebe outra (mácron, breve...), para que tom e letra não se confundam.

---

## Nome da língua

Com `--language`, o autônimo do manifesto é escrito na grafia e ganha uma forma "inglesa", como no Vulgarlang (*wïikho* → *Wïikhoian*):

```
Nome da língua: Akishontangian (nativo: akishontang /akiʃontaŋ/)
```

---

## Saídas

### `orthography.md`

1. Nome da língua e estilo
2. Tabela de correspondências (grafia → IPA)
3. Tons, se houver
4. As frases de exemplo escritas na grafia, com a pronúncia
5. O dicionário inteiro no formato do Vulgarlang: `grafia /pronúncia/ classe 'significado'`

```
- **Ozwuu twukuu ukwu.** /ozwuː twukuː ukwu/ — 'The woman sees the fish.'

- **aakyuu** /aːkjuː/ v. 'to hunt'
- **akixontaq** /akiʃontaŋ/ n. 'person'
```

### `orthography.json`

```json
{
  "style": "economic",
  "graphemes": {"ʃ": "x", "ŋ": "q", "aː": "aa", "...": "..."},
  "vowels": ["i", "u", "a", "..."],
  "tones": {"˦": "́", "˨": "̀"},
  "separator": "·",
  "separator_pairs": [["n", "ɡ"], ["a", "a"]],
  "language_name": {"native": "akixontaq", "english": "Akixontaqian",
                    "ipa": "akiʃontaŋ", "literal": "person"},
  "metadata": {"seed": 1234567, "notes": [], "checked_with_phonotactics": true}
}
```

### Uso como biblioteca

```python
import json, orthography as ortho

inv = json.load(open("languages/lang-31/phonemic_inventory.json"))
spec = ortho.build(inv, style="english", seed=1)
o = ortho.Orthography(spec)

o.spell("t̠ʃupaŋ")            # 'chupang'
o.spell("ma˥.ku˩")            # 'mákù'
o.spell_segments(["k", "p"])  # mais exato quando os fonemas já estão separados
o.decode("chupang")           # ['t̠ʃ', 'u', 'p', 'a', 'ŋ']
```

---

## Testes

223 línguas geradas, cada uma nos quatro estilos (209 mil palavras): todas as palavras escritas foram lidas de volta exatamente como os fonemas originais, inclusive nas línguas tonais. Nenhuma grafia repetida entre fonemas, e a mesma semente gera o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Mostrar a grafia no `grammar.md` e no dicionário principal (exige uma mudança no orquestrador)
- [ ] Acento gráfico, quando houver o módulo de acento
- [ ] Regras dependentes de contexto (como *c/qu* do português)
- [ ] Escolha manual de letras pelo usuário (ex: /ʃ/ = *sch*)
- [ ] Alfabetos não latinos
- `spell()` recebe strings e precisa segmentá-las: numa forma sem pontos de sílaba, *kp* é lido como o fonema /kp/ se ele existir. Quando os fonemas já estão separados, use `spell_segments()`.
