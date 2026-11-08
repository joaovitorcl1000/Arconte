# Módulo — Fonotática e Estrutura Silábica

Este módulo define **como os sons da conlang se combinam**. Ele recebe o inventário fonêmico e produz as regras da língua (moldes silábicos, encontros consonantais, codas, hiato e formato das raízes), salvas em `phonotactics.json`. Também expõe um gerador de raízes e afixos e um silabificador/validador que o motor morfológico usará depois.

```
phonemic_inventory.json ──┐
                          ├──► FONOTÁTICA ──► phonotactics.json ──► Motor morfológico
morphological_typology.json┘   (este módulo)      + raízes, afixos
        (opcional)                 ▲              + validador
                                   │
                          WALS 12A (opcional)
```

---

## Objetivo

Sem fonotática, o gerador produz sequências aleatórias como `ŋkxtlʼa`. Com ela, as palavras respeitam padrões observados em línguas naturais: toda sílaba tem núcleo vocálico, os encontros consonantais seguem a sonoridade e certas consoantes ficam restritas a certas posições.

---

## Entradas

| Arquivo | Obrigatório | Uso |
|---|---|---|
| `../phonemic_inventory/phonemic_inventory.json` | Sim | Fonemas, frequências, traços e rótulos de modo/ponto; língua de referência |
| `../morphological_typology/morphological_typology.json` | Não | Exigências da morfologia (ver [Integração](#integração-com-a-tipologia-morfológica)) |
| `../wals/cldf/languages.csv` e `values.csv` | Não | Complexidade silábica real (WALS 12A) via `Glottocode` |

O módulo não lê o `phoible.csv`: tudo o que precisa dos traços já vem no inventário. Usa apenas a biblioteca padrão do Python (≥ 3.9).

Para habilitar o WALS:

```bash
cd ~/Arconte/frontend/tools/conlang
git clone https://github.com/cldf-datasets/wals.git
```

Sem o WALS, o módulo funciona normalmente com o sorteio condicionado descrito abaixo.

---

## 1. Complexidade silábica (WALS 12A)

| Categoria | Descrição | Moldes possíveis |
|---|---|---|
| `simple` | Só sílabas abertas | `(C)V` |
| `moderate` | CVC e/ou CCV com 2ª consoante líquida ou glide | `(C)(C)V(C)` |
| `complex` | Encontros mais livres no ataque e na coda | `(C)(C)(C)V(C)(C)` |

A complexidade é decidida nesta ordem:

1. `--complexity`, se informado;
2. o valor do WALS 12A da **língua de referência** do inventário, se o WALS estiver disponível e a língua tiver dado;
3. um **sorteio condicionado ao número de consoantes**, com probabilidades calculadas cruzando o WALS 1A (tamanho do inventário consonantal) com o 12A em 486 línguas:

| Consoantes | Simples | Moderada | Complexa |
|---|---|---|---|
| ≤ 14 | 30% | 55% | 15% |
| 15–18 | 13% | 69% | 18% |
| 19–25 | 8% | 56% | 35% |
| 26–33 | 5% | 52% | 43% |
| ≥ 34 | 10% | 41% | 49% |

Inventários pequenos tendem a sílabas simples, e grandes, a sílabas complexas (Maddieson).

---

## 2. Moldes silábicos

Cada complexidade parte de um conjunto de moldes; os pesos são perturbados aleatoriamente (×0,6 a ×1,4) a cada língua.

| Complexidade | Moldes de partida |
|---|---|
| `simple` | CV, V |
| `moderate` | CV, CVC, V, VC, CCV, CCVC |
| `complex` | CV, CVC, V, VC, CCV, CCVC, CVCC, CCCV, CCVCC |

Ajustes por língua:

- **Tipo moderado:** 40% das línguas têm codas e encontros, 45% só codas, 15% só encontros.
- **Ataque obrigatório:** 30% das línguas simples e 15% das demais. Nesse caso, os moldes sem ataque (V, VC) são removidos.
- **Hiato:** permitido em 30% das línguas com ataque opcional.
- Moldes que o inventário não consegue preencher (ex: CCV sem nenhum encontro possível) são removidos automaticamente.

---

## 3. Sonoridade

A sonoridade é derivada dos rótulos `manner` exportados pelo inventário:

| Sonoridade | Classe | `manner` no inventário |
|---|---|---|
| 6 | Vogais | — |
| 5 | Glides | `approximant` (não consonantal: j, w) |
| 4 | Líquidas | `lateral`, `rhotic`, `approximant` consonantal (ɻ, ɹ) |
| 3 | Nasais | `nasal` |
| 2 | Fricativas | `fricative` |
| 1 | Oclusivas, africadas, cliques | `stop`, `affricate`, `click` |

### Princípio de Sequenciamento de Sonoridade (SSP)

A sonoridade sobe do início da sílaba até o núcleo e desce até o fim:

```
 p  l  a  n        ✔  1 → 4 → 6 → 3
 l  p  a           ✘  4 → 1 → 6  (cai antes do núcleo)
```

A **distância mínima de sonoridade** no ataque é 2 nas línguas moderadas (permite `pl`, proíbe `pn`) e 1 nas complexas.

---

## 4. Encontros no ataque

A base é sempre **obstruinte + líquida/glide** (`pl`, `kr`, `tw`). Extensões são sorteadas por língua:

| Extensão | Exemplo | Probabilidade | Disponível em |
|---|---|---|---|
| Nasal + líquida | `ml`, `nr` | 30% | moderada, complexa |
| Obstruinte + nasal (só /m/, /n/) | `pn`, `kn` | 40% | complexa |
| Oclusiva + fricativa (mesmo vozeamento) | `ps`, `ks` | 35% | complexa |
| s + oclusiva surda (exceção à SSP) | `sp`, `st`, `sk` | 60% | complexa |
| Triplos s + oclusiva surda + líquida/glide | `spl`, `str` | junto com o anterior | complexa |

Filtros aplicados:

- Consoantes laríngeas (/h/, /ʔ/) não entram em encontros.
- Sem coronal + lateral coronal (`*tl`, `*dl`).
- Sem glide homorgânico (`*pw`, `*cj`).
- Sem encontros de pontos idênticos em obstruinte + nasal ou oclusiva + fricativa.
- **Lacunas acidentais:** cada encontro válido é mantido com 85% (moderada) ou 70% (complexa) de chance, como nas línguas reais, que nunca usam todas as combinações possíveis.

### Segmentos pesados

Aspiradas, ejetivas e glotalizadas, implosivas, cliques, consoantes longas, oclusivas labiovelares (/kp/, /ɡb/) e segmentos com articulação secundária ou de contorno (/kʷ/, /tʲ/, /ⁿd/) **podem iniciar sílaba sozinhos**, mas ficam fora de encontros e codas.

---

## 5. Codas

Cada língua sorteia um **perfil de coda**:

| Perfil | Codas permitidas | Moderada | Complexa |
|---|---|---|---|
| `nasals` | Só nasais | 15% | — |
| `sonorants` | Nasais, líquidas (e glides) | 35% | 15% |
| `restricted` | Soantes + parte das obstruintes surdas | 35% | 40% |
| `free` | Todas as consoantes simples | 15% | 45% |

Ajustes:

- Glides como coda (ditongos fonéticos como `aj`, `aw`): 50% das línguas.
- No perfil `free`, 50% das línguas barram obstruintes sonoras em coda (efeito de ensurdecimento final).
- Em 30% das línguas, o **fim de palavra** aceita apenas codas soantes, mais restrito que o meio de palavra.

### Encontros em coda (só línguas complexas)

- **Soante + obstruinte** (`nt`, `lk`, `rs`), com sonoridade decrescente. Em 60% das línguas, nasal + obstruinte exige mesmo ponto de articulação (`mp`, `nt`, `ŋk`).
- **Fricativa + oclusiva** (`st`, `ft`), com mesmo vozeamento: 40% das línguas.
- Cada encontro é mantido com 80% de chance.

---

## 6. Restrições posicionais e entre sílabas

- **Início de palavra:** /ŋ/, /ɳ/ e /ɭ/, se existirem, são proibidos em posição inicial com 60% de chance cada.
- **Lei do contato silábico** (Vennemann): ao gerar palavras, uma coda menos sonora que o ataque seguinte é rejeitada com 50% de chance (`am.ta` é preferido a `at.ma`).
- **Sem geminadas acidentais:** coda e ataque seguinte nunca são a mesma consoante.

---

## 7. Raízes

### Número de sílabas

| Perfil | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Língua isolante | 70% | 30% | — | — |
| Sílabas simples | 10% | 50% | 30% | 10% |
| Sílabas moderadas | 25% | 50% | 20% | 5% |
| Sílabas complexas | 40% | 45% | 15% | — |

Línguas com sílabas simples compensam com raízes mais longas; com sílabas complexas, raízes curtas já carregam muita informação.

### Esqueletos consonantais

Quando a morfologia usa transfixação, as raízes são esqueletos como `k-t-b`, com o **OCP** (Princípio do Contorno Obrigatório) aplicado: C1 ≠ C2 sempre e, em 90% dos casos, C1 e C2 em pontos de articulação diferentes. C2 = C3 é permitido, como nas raízes geminadas do árabe (`m-d-d`).

### Tom

Se o inventário tem tons, cada sílaba recebe um, ponderado pela frequência (ex: `ju˦.pʼa˥˩`).

---

## 8. Afixos

Afixos são curtos e tendem a usar segmentos não marcados, então o peso da frequência é mais forte aqui.

| Tipo | Formatos (probabilidade) |
|---|---|
| Sufixo | CV (40%), V (20%), VC (20%), C (20%) |
| Prefixo | CV (50%), V (25%), CVC (15%), C (10%) |

Formatos impossíveis na língua são removidos: sem codas não há VC, CVC nem sufixo C; sem encontros no ataque não há prefixo C; com ataque obrigatório não há prefixo V. Línguas isolantes não geram afixos.

---

## 9. Silabificação e validação

`syllabify()` silabifica uma sequência de fonemas pelo **Princípio do Ataque Máximo** e devolve `None` se ela violar qualquer regra (ataque, coda, hiato, ataque obrigatório ou molde inexistente).

```python
>>> engine.syllabify(["k", "a", "n", "a"])
[['k', 'a'], ['n', 'a']]
>>> engine.syllabify(["t", "a", "n", "t"])   # língua sem encontros em coda
None
```

É esse validador que o motor morfológico usará para detectar quando a afixação cria sequências ilegais (ex: `tan` + `-t`) e acionar as regras de sândi.

---

## Integração com a tipologia morfológica

| Em `morphological_typology.json` | Efeito |
|---|---|
| `degree_of_synthesis: isolating` | Raízes de 1–2 sílabas; nenhum afixo gerado |
| `transfixation` em `active_processes` | Raízes como esqueletos consonantais |
| `tonal_morphology` em `active_processes` | Aviso se o inventário não tiver tons (gere o inventário de novo) |

---

## Uso

```bash
cd phonotactics

python phonotactics.py                          # sorteio aleatório
python phonotactics.py --seed 42 --samples 30   # reprodutível, 30 raízes de exemplo
python phonotactics.py --complexity complex     # força a complexidade
python phonotactics.py --no-wals --no-morph     # ignora as entradas opcionais
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--complexity {simple,moderate,complex}` | sorteada | Força a complexidade silábica |
| `--samples N` | `20` | Nº de raízes de exemplo |
| `--inventory PATH` | `../phonemic_inventory/phonemic_inventory.json` | Inventário |
| `--morph PATH` | `../morphological_typology/morphological_typology.json` | Tipologia morfológica |
| `--no-morph` | — | Ignora a tipologia morfológica |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS |
| `--no-wals` | — | Ignora o WALS |
| `-o PATH` | `phonotactics.json` | Arquivo de saída |

### Exemplo de saída no terminal

```
ESTRUTURA SILÁBICA: moderate  (WALS 12A (WANTOAT))
  Moldes:  CV 66%  CVC 34%
  ataque obrigatório, sem hiato
  Proibidos no início de palavra: ŋ

CODAS (5): f m n p ŋ

RAÍZES (syllabic):
  ki.nẽ̞n  ke̞.ko  ma.ja  wu.pa  nop.ma  ni.ɡi.pu  fi.wo  jaf.ɡu  juŋ  suf.ko
SUFIXOS:  -i  -m  -ma  -ɡaː  -um  -ku
PREFIXOS: ki-  ni-  jip-  ki-  mum-  kin-
```

### Uso como biblioteca

```python
import json
from phonotactics import (
    build_rules, Phonotactics, read_morph_requirements,
    DEFAULT_INVENTORY, DEFAULT_MORPH, DEFAULT_WALS,
)

inventory = json.loads(DEFAULT_INVENTORY.read_text(encoding="utf-8"))
rules = build_rules(inventory, seed=42,
                    morph_req=read_morph_requirements(DEFAULT_MORPH),
                    wals_dir=DEFAULT_WALS)

engine = Phonotactics(rules, inventory, seed=42)
root = engine.generate_root()              # {"segments", "syllables", "tones", "form"}
suffix = engine.generate_affix("suffix")   # {"segments", "kind", "form"}
engine.is_valid(root["segments"] + suffix["segments"])

# Recarregando regras já salvas
rules = json.loads(open("phonotactics.json", encoding="utf-8").read())
engine = Phonotactics(rules, inventory)
```

---

## Formato de `phonotactics.json`

```json
{
  "syllable_complexity": "moderate",
  "complexity_source": "WALS 12A (WANTOAT)",
  "templates": {"CV": 0.66, "CVC": 0.34},
  "onset_required": true,
  "allow_hiatus": false,
  "min_sonority_distance": 2,
  "sonority": {"p": 1, "f": 2, "m": 3, "l": 4, "j": 5, "a": 6},
  "onsets": {
    "clusters": [["p", "l"], ["k", "r"]],
    "triple": [],
    "word_initial_forbidden": ["ŋ"]
  },
  "codas": {
    "single": ["f", "m", "n", "p", "ŋ"],
    "word_final": ["f", "m", "n", "p", "ŋ"],
    "clusters": []
  },
  "syllable_contact": true,
  "root": {
    "shape": "syllabic",
    "syllables": {"1": 0.25, "2": 0.5, "3": 0.2, "4": 0.05}
  },
  "tone_bearing": false,
  "metadata": {
    "seed": 42,
    "morphology_requirements": {},
    "notes": ["perfil de coda: restricted"]
  },
  "samples": {
    "roots": ["ki.nẽ̞n", "ke̞.ko", "..."],
    "suffixes": ["-i", "-m", "..."],
    "prefixes": ["ki-", "ni-", "..."]
  }
}
```

> Os valores acima são ilustrativos de um sorteio; `root.shape` vale `consonantal_skeleton` quando a morfologia usa transfixação.

---

## Cuidados

- **Fonemas são unidades:** uma palavra é uma lista como `["t̠ʃʰ", "a", "n"]`, nunca uma string. `/t̠ʃʰ/` tem quatro code points e seria quebrado se tratado caractere a caractere.
- **Unicode NFD:** todos os símbolos são normalizados em NFD, como no inventário. Qualquer código que compare símbolos deve fazer o mesmo.
- **Ordem de execução:** gere o inventário antes. Se mudar o inventário, gere a fonotática de novo, já que as regras referenciam fonemas específicos.
- **Sândi não é feito aqui:** afixos vocálicos podem criar hiato ao se juntar a raízes terminadas em vogal. Resolver esses choques é tarefa do motor morfológico.

---

## Limitações e próximos passos

- [ ] Acento (WALS 14A–17A): posição fixa, peso silábico, acento lexical
- [ ] Restrições de coocorrência vocálica (harmonia vocálica)
- [ ] Alofonia (ex: palatalização antes de /i/, ensurdecimento final como regra, não só restrição)
- [ ] Geminadas como contraste fonológico
- [ ] Romanização (ortografia prática para a conlang)

---

## Referências

- Maddieson, I. (2013) — *Syllable Structure*. In Dryer & Haspelmath (eds.), *WALS Online*, cap. 12
- Maddieson, I. (2013) — *Consonant Inventories*. In *WALS Online*, cap. 1
- Clements, G. N. (1990) — *The role of the sonority cycle in core syllabification*
- Vennemann, T. (1988) — *Preference Laws for Syllable Structure and the Explanation of Sound Change*
- McCarthy, J. (1986) — *OCP effects: gemination and antigemination*. Linguistic Inquiry 17(2)
- Dryer, M. S. & Haspelmath, M. (eds.) — *The World Atlas of Language Structures Online*. https://wals.info