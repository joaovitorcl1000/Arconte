# Kwunytwun

Pasta: `languages/teste31/`

Nome nativo: **kwunytwu** /ˈkwuɲtwu/ (literalmente 'person')

Semente: `31` — gere de novo, a partir de `conlang/`, com `python generate_language/generate_language.py --seed 31`

A mesma semente com os mesmos dados (PHOIBLE, WALS e listas de conceitos) gera sempre a mesma língua.

## Fonologia

### Consoantes (24)

|  | Labial | Coronal | Palatal | Velar | Labiovelar | Laríngea |
|---|---|---|---|---|---|---|
| Oclusiva | b p pʰ | d t |  | k kʰ kː ɡ |  |  |
| Fricativa |  | s z ð ɬ ʃ θ |  |  |  | h |
| Nasal | m | n | ɲ | ŋ |  |  |
| Rótica |  | r |  |  |  |  |
| Lateral |  | l |  |  |  |  |
| Aproximante |  |  | j |  | w |  |

### Vogais (9)

|  | Anterior | Central | Posterior |
|---|---|---|---|
| Alta | i ĩ iː |  | u uː |
| Média | e |  | o |
| Baixa |  | a aː |  |

### Estrutura silábica

- Complexidade: **moderate** (sorteio condicionado a 24 consoantes (WALS 1A × 12A))
- Moldes: CV (38%), CVC (20%), CCV (15%), V (13%), CCVC (8%), VC (6%)
- Ataque opcional; hiato permitido
- Encontros no ataque (36): bj bl br dj dr dw kj kl kr kw pj pl pr sj sr tj tr tw zj zr zw ðj ðr ðw ɡj ɡl ɡr ɡw ɬr ɬw ʃj ʃr ʃw θj θr θw
- Codas: l m n r ŋ ɲ

### Ortografia

- Estilo: econômico (letras reaproveitadas: x, c, q)
- Separador `·` entre sons que, escritos juntos, formariam outra letra

| Grafia | IPA |
|---|---|
| **a** | /a/ |
| **aa** | /aː/ |
| **b** | /b/ |
| **c** | /θ/ |
| **d** | /d/ |
| **dh** | /ð/ |
| **e** | /e/ |
| **g** | /ɡ/ |
| **h** | /h/ |
| **i** | /i/ |
| **ii** | /iː/ |
| **ĩ** | /ĩ/ |
| **k** | /k/ |
| **kh** | /kʰ/ |
| **kk** | /kː/ |
| **l** | /l/ |
| **lh** | /ɬ/ |
| **m** | /m/ |
| **n** | /n/ |
| **ny** | /ɲ/ |
| **o** | /o/ |
| **p** | /p/ |
| **ph** | /pʰ/ |
| **q** | /ŋ/ |
| **r** | /r/ |
| **s** | /s/ |
| **t** | /t/ |
| **u** | /u/ |
| **uu** | /uː/ |
| **w** | /w/ |
| **x** | /ʃ/ |
| **y** | /j/ |
| **z** | /z/ |

### Acento

- Sistema: **sensível ao peso**
- Acento na penúltima se ela for pesada; senão, na antepenúltima (regra do latim); sílaba pesada = sílaba com consoante em coda; ritmo trocaico (acentos secundários a cada duas sílabas, da tônica para o início).
- Exemplos: /ˈbuiː/, /ˈsenka/, /ˈlapjiŋ/, /ˈŋumkjĩ/, /ˈjapil/, /ˈzempja/

### Mudanças sonoras

3 regras, aplicadas em ordem; 22 de 228 palavras mudaram. A forma do dicionário fica entre barras /.../, e a pronúncia depois das mudanças, entre colchetes [...].

Sons novos criados pelas mudanças: [ɣ] [β]

| # | Regra | Origem | Palavras afetadas | Exemplo |
|---|---|---|---|---|
| 1 | `{p,t,k} > {b,d,ɡ} / V_V` | natural | 9 | *yapil* /japil/ → [ˈjabil] 'name' |
| | sonorização entre vogais (como no espanhol: lupus → lobo) | | | |
| 2 | `{b,d,ɡ} > {β,ð,ɣ} / V_V` | natural | 10 | *yabil* /jabil/ → [ˈjaβil] 'name' |
| | espirantização entre vogais (como no espanhol: lado [laðo]) | | | |
| 3 | `e > i / _#` | natural | 14 | *e* /e/ → [i] 'blood' |
| | elevação de vogal final (e > i, como no português: leite [lejt͡ʃi]) | | | |


## Morfologia

- Tipo: synthetic, agglutinative, strongly_suffixing, dependent_marking
- Processos: affixation, compounding, reduplication_full
- Sândi: vogal epentética /i/; encontros por deletion; hiato por elision

### Categorias gramaticais

| Categoria | Valores | Realização | Ø |
|---|---|---|---|
| Número | singular, paucal, plural | affix (suffix) | singular |
| Caso | direct, genitive, locative, instrumental, ablative, allative, essive (neutral) | affix (suffix) | direct |
| Tempo | present, past, future | affix (suffix) | present |
| Aspecto | perfective, imperfective, progressive | affix (suffix) | perfective |
| Modo | indicative, imperative, potential | affix (suffix) | indicative |
| Evidencialidade | direct, inferential, reportative | clitic (suffix) | direct |
| Negação | affirmative, negative | affix (suffix) | affirmative |

- Molde do nome: `ROOT-number-case`
- Molde do verbo: `ROOT-negation-aspect-tense-mood-evidentiality`

### Afixos nominais

**number**

| Célula | Forma |
|---|---|
| SG | Ø |
| PAUC | -n |
| PL | -mi |

**case**

| Célula | Forma |
|---|---|
| DIR | Ø |
| GEN | -n |
| LOC | -un |
| INS | -ni |
| ABL | -bu |
| ALL | -ka |
| ESS | -m |


### Afixos verbais

**negation**

| Célula | Forma |
|---|---|
| (padrão) | Ø |
| NEG | -ɡu |

**aspect**

| Célula | Forma |
|---|---|
| PFV | Ø |
| IPFV | -ŋu |
| PROG | -n |

**tense**

| Célula | Forma |
|---|---|
| PRS | Ø |
| PST | -pu |
| FUT | -pi |

**mood**

| Célula | Forma |
|---|---|
| IND | Ø |
| IMP | -a |
| POT | -ŋ |

**evidentiality**

| Célula | Forma |
|---|---|
| DIR | Ø |
| INFR | =mu |
| REP | =im |


## Paradigmas

### Nome: *sjun* 'dog'

|  | SG | PAUC | PL |
|---|---|---|---|
| DIR | sjun | sjun | sjunmi |
| GEN | sjun | sjunnin | sjunmin |
| LOC | sjunun | sjunnun | sjunmiun |
| INS | sjunni | sjunni | sjunmini |
| ABL | sjunbu | sjumbu | sjunmibu |
| ALL | sjunka | sjuŋka | sjunmika |
| ESS | sjum | sjunnim | sjunmim |

### Verbo: *alŋo* 'to see'

|  | PRS | PST | FUT |
|---|---|---|---|
| IND | alŋo | alŋopu | alŋopi |
| IMP | alŋoa | alŋopua | alŋopia |
| POT | alŋoŋ | alŋopuŋ | alŋopiŋ |

### Pronomes

| Pessoa | Forma |
|---|---|
| 1SG | *ka* |
| 2SG | *ɡwiɲ* |
| 3SG | *u* |
| 1INCL.PAUC | *buːɲ* |
| 1EXCL.PAUC | *im* |
| 2PAUC | *a* |
| 3PAUC | *aː* |
| 1INCL.PL | *wĩ* |
| 1EXCL.PL | *mu* |
| 2PL | *an* |
| 3PL | *sa* |

## Posse e determinantes

- Possessivos: afixos de posse no nome (sufixos)
- Posse entre nomes: marca no possuidor (caso genitivo)
- Posse inalienável (partes do corpo e parentes) marcada no próprio nome; nos demais, a marca vai no classificador de posse pom

### Possessivos

| Pessoa | Possessivo | Pronúncia | Plural |
|---|---|---|---|
| 1SG ('my dog') | **pomol syun** | /ˈpomol sjun/ | **pomol syunmi** |
| 2SG ('your dog') | **pomin syun** | /ˈpomin sjun/ | **pomin syunmi** |
| 3SG ('his/her/its dog') | **pomri syun** | /ˈpomri sjun/ | **pomri syunmi** |
| 1INCL.PAUC ('our (incl.) (paucal) dog') | **pomsu syun** | /ˈpomsu sjun/ | **pomsu syunmi** |
| 1EXCL.PAUC ('our (excl.) (paucal) dog') | **pomil syun** | /ˈpomil sjun/ | **pomil syunmi** |
| 2PAUC ('your (paucal) dog') | **pompuu syun** | /ˈpompuː sjun/ | **pompuu syunmi** |
| 3PAUC ('their (paucal) dog') | **pomti syun** | /ˈpomti sjun/ | **pomti syunmi** |
| 1INCL.PL ('our (incl.) dog') | **pomi syun** | /ˈpomi sjun/ | **pomi syunmi** |
| 1EXCL.PL ('our (excl.) dog') | **pomlu syun** | /ˈpomlu sjun/ | **pomlu syunmi** |
| 2PL ('your (pl.) dog') | **pomwa syun** | /ˈpomwa sjun/ | **pomwa syunmi** |
| 3PL ('their dog') | **pomte syun** | /ˈpomte sjun/ | **pomte syunmi** |

### Alienabilidade

- **twool** /ˈtwool/ — 'my hand' (inalienable)
- **pomol syun** /ˈpomol sjun/ — 'my dog' (alienable)

### Posse entre nomes

- **tyulĩn syun** /ˈtjulĩn sjun/ — 'the woman's dog'

## Comparação

- Comparativo: locativa (o termo comparado vai num caso ou adposição de origem/lugar)
- Termo comparado no caso ablative
- Grau comparativo no adjetivo: -em
- Superlativo: afixo -yii
- Equativo: partícula ('como') tyony

### Formas do adjetivo

| Grau | Forma | Pronúncia |
|---|---|---|
| Positivo | **hukla** | /ˈhukla/ |
| Comparativo | **huklaem** | /ˈhuklaem/ |
| Superlativo | **huklayii** | /ˈhuklajiː/ |

### Comparativo

**Syun bibu huklaem.**

```
syun  bibu      huklaem
sjun  bi-bu     hukla-em
dog   fish-ABL  big-COMPR
'The dog is bigger than the fish.'
```

### Superlativo

**Syun huklayii.**

```
syun  huklayii
sjun  hukla-jiː
dog   big-SUPL
'The dog is the biggest.'
```

### Equativo

**Syun bi tyony hukla.**

```
syun  bi    tyony  hukla
sjun  bi    tjoɲ   hukla
dog   fish  as     big
'The dog is as big as the fish.'
```

## Derivação

8 processos produtivos; 96 palavras derivadas (o léxico base tem 231).

| Processo | Forma | Classe | Exemplo |
|---|---|---|---|
| agentivo ('quem faz') | composição com *kwunytwu* ('person') | v. → n. | *iq* → **iqkwunytwu** 'hunter' |
| ação ('o ato de') | sufixo -go | v. → n. | *upyon* → **upyongo** 'meal' |
| qualidade ('-eza', '-idade') | sufixo -al | adj. → n. | *bun* → **bunal** 'goodness' |
| incoativo ('ficar ...') | sufixo -dhi | adj. → v. | *upru* → **uprudhi** 'to age' |
| factitivo ('tornar ...') | sufixo -we (depois de consoante: -iwe) | adj. → v. | *hukla* → **huklawe** 'to enlarge' |
| proprietivo ('cheio de', '-oso') | sufixo -so | n. → adj. | *tyu* → **tyuso** 'stony' |
| tendência ('-ão', 'brigão') | sufixo -qi | v. → adj. | *banuuny* → **banuunyqi** 'cheerful' |
| produto do verbo ('o que se faz') | sufixo -nii (depois de consoante: -inii) | v. → n. | *ĩpi* → **ĩpinii** 'garment' |


## Irregularidades

2 palavras irregulares, todas entre as mais frequentes da língua; 8 alternâncias criadas pelas mudanças sonoras.

### Palavras irregulares

| Palavra | Tipo | Forma | Regular seria | Irregular |
|---|---|---|---|---|
| 'go' (verbo) | apofonia | go-PST | ~~senkapu~~ | **senke** /ˈsenke/ |
| 'person' (nome) | plural zero | person-PL | ~~kwunytwumi~~ | **kwunytwu** /ˈkwuɲtwu/ |

### Alternâncias das mudanças sonoras

As regras de mudança sonora atingem o radical em uma forma e não na outra:

- 'blood': SG *e* /e/ [i] · PL *emi* /emi/ [emi]
- 'root': SG *le* /le/ [li] · PL *lemi* /lemi/ [lemi]
- 'breast': SG *he* /he/ [hi] · PL *hemi* /hemi/ [hemi]
- 'ear': SG *ke* /ke/ [ki] · PL *kemi* /kemi/ [kemi]
- 'take': PRS *yake* /jake/ [jaɣi] · PST *yakepu* /jakepu/ [jaɣeβu]
- 'run': PRS *byaae* /bjaːe/ [bjaːi] · PST *byaaepu* /bjaːepu/ [bjaːeβu]
- 'cry': PRS *sonyxĩge* /soɲʃĩɡe/ [soɲʃĩɣi] · PST *sonyxĩgepu* /soɲʃĩɡepu/ [soɲʃĩɣeβu]
- 'know (something)': PRS *gwiinke* /ɡwiːnke/ [ɡwiːnki] · PST *gwiinkepu* /ɡwiːnkepu/ [ɡwiːnkeβu]

## Sistema numeral

- Base: decimal (base 10)
- Ordem: multiplicador antes da base ('três-dez' = 30); menor antes ('sete-e-trinta', como no alemão)
- Numerais compostos em palavras separadas, ligados por *ne* ('e')
- Ordinais: 'primeiro' ou 'um-ésimo'; os demais derivados

### Numerais

| Número | Numeral | Pronúncia | Composição |
|---|---|---|---|
| 1 | **tyaa** | /tjaː/ | 1 |
| 2 | **ul** | /ul/ | 2 |
| 3 | **xwe** | /ʃwe/ | 3 |
| 4 | **qo** | /ŋo/ | 4 |
| 5 | **sebyaa** | /ˈsebjaː/ | 5 |
| 6 | **som** | /som/ | 6 |
| 7 | **qu** | /ŋu/ | 7 |
| 8 | **tam** | /tam/ | 8 |
| 9 | **zo** | /zo/ | 9 |
| 10 | **sii** | /siː/ | 10 |
| 11 | **tyaa ne sii** | /tjaː ne siː/ | 1 + 10 |
| 12 | **ul ne sii** | /ul ne siː/ | 2 + 10 |
| 13 | **xwe ne sii** | /ʃwe ne siː/ | 3 + 10 |
| 14 | **qo ne sii** | /ŋo ne siː/ | 4 + 10 |
| 15 | **sebyaa ne sii** | /ˈsebjaː ne siː/ | 5 + 10 |
| 16 | **som ne sii** | /som ne siː/ | 6 + 10 |
| 17 | **qu ne sii** | /ŋu ne siː/ | 7 + 10 |
| 18 | **tam ne sii** | /tam ne siː/ | 8 + 10 |
| 19 | **zo ne sii** | /zo ne siː/ | 9 + 10 |
| 20 | **ul sii** | /ul siː/ | 2×10 |
| 30 | **xwe sii** | /ʃwe siː/ | 3×10 |
| 37 | **qu ne xwe sii** | /ŋu ne ʃwe siː/ | 7 + 3×10 |
| 40 | **qo sii** | /ŋo siː/ | 4×10 |
| 50 | **sebyaa sii** | /ˈsebjaː siː/ | 5×10 |
| 60 | **som sii** | /som siː/ | 6×10 |
| 80 | **tam sii** | /tam siː/ | 8×10 |
| 90 | **zo sii** | /zo siː/ | 9×10 |
| 99 | **zo ne zo sii** | /zo ne zo siː/ | 9 + 9×10 |
| 100 | **gon** | /ɡon/ | 100 |
| 256 | **som ne sebyaa sii ne ul gon** | /som ne ˈsebjaː siː ne ul ɡon/ | 6 + 5×10 + 2×100 |
| 1000 | **nyanybyin** | /ˈɲaɲbjin/ | 1000 |

### Ordinais

| Número | Ordinal | Pronúncia |
|---|---|---|
| 1º | **konhuun** | /ˈkonhuːn/ |
| 2º | **ulu** | /ˈulu/ |
| 3º | **xweu** | /ˈʃweu/ |
| 4º | **qou** | /ˈŋou/ |
| 5º | **sebyaau** | /ˈsebjaːu/ |

Nota: conectivo obrigatório na soma, para distinguir 13 de 30

## Sintaxe

- Ordem básica: SOV
- Adposições: posposições
- Genitivo antes do nome; adjetivo depois do nome; demonstrativo depois do nome; numeral depois do nome
- Oração relativa: núcleo interno
- Perguntas sim/não: partícula no fim; perguntas de conteúdo: no início
- Pro-drop: não; cópula: zero
- Compostos: núcleo final (harmônico com o genitivo)

### 1. Oração intransitiva

**Am lulim.**

```
am     lulim
child  sleep
'The child sleeps.'
```

### 2. Oração transitiva

**Tyulĩ bi alqo.**

```
tjulĩ  bi    alŋo
woman  fish  see
'The woman sees the fish.'
```

### 3. Passado, objeto plural

**Syun bimi upyonpu.**

```
sjun  bimi     upjonpu
sjun  bi-mi    upjon-pu
dog   fish-PL  eat-PST
'The dog ate the fish.'
```

### 4. Oração bitransitiva

**Tyulĩ amka bi maam.**

```
tjulĩ  amka       bi    maːm
tjulĩ  am-ka      bi    maːm
woman  child-ALL  fish  give
'The woman gives the fish to the child.'
```

### 5. Pronomes

**Ka gwiny alqo.**

```
ka   ɡwiɲ  alŋo
1SG  2SG   see
'I see you.'
```

### 6. Sintagma nominal (demonstrativo, numeral, adjetivo)

**Syunmi hukla ul ar klaam.**

```
sjunmi   hukla  ul   ar    klaːm
sjun-mi  hukla  ul   ar    klaːm
dog-PL   big    two  this  come
'These two big dogs come.'
```

### 7. Posse (genitivo)

**Tyulĩn syun lulim.**

```
tjulĩn     sjun  lulim
tjulĩ-n    sjun  lulim
woman-GEN  dog   sleep
'The woman's dog sleeps.'
```

### 8. Adjunto locativo

**Am gwaaqumun lulim.**

```
am     ɡwaːŋumun   lulim
am     ɡwaːŋum-un  lulim
child  house-LOC   sleep
'The child sleeps in the house.'
```

### 9. Predicado adjetival (cópula zero)

**Bi hukla.**

```
bi    hukla
fish  big
'The fish is big.'
```

### 10. Negação

**Am lulimgu.**

```
am     lulimɡu
am     lulim-ɡu
child  sleep-NEG
'The child does not sleep.'
```

### 11. Pergunta sim/não

**Tyulĩ bi alqo tyum.**

```
tjulĩ  bi    alŋo  tjum
woman  fish  see   Q
'Does the woman see the fish?'
```

### 12. Pergunta de conteúdo (palavra interrogativa no início)

**Twu tyulĩ alqo.**

```
twu   tjulĩ  alŋo
what  woman  see
'What does the woman see?'
```

## Orações

- Passiva: sufixo -nya; agente no caso instrumental
- Reflexivo: afixo on
- Recíproco: afixo r
- Demonstrativos: 2 graus de distância
- Imperativo: afixo uun
- Proibitivo: partícula própria waq
- Subordinação: subordinador no fim da subordinada; complementizador hem ('que')

### Demonstrativos

| Distância | Demonstrativo | Advérbio |
|---|---|---|
| perto de quem fala | **ar** 'this' | **pyi** 'here' |
| longe | **li** 'that' | **ulam** 'there' |

### Possessivos independentes

| Pessoa | Forma |
|---|---|
| 1SG | **kilol** |
| 2SG | **kilin** |
| 3SG | **kilri** |
| 1INCL.PAUC | **kilsu** |
| 1EXCL.PAUC | **kilil** |
| 2PAUC | **kilpuu** |
| 3PAUC | **kilti** |
| 1INCL.PL | **kili** |
| 1EXCL.PL | **killu** |
| 2PL | **kilwa** |
| 3PL | **kilte** |

### Conectivos e adposições

| Palavra | Forma |
|---|---|
| 'or' | **caa** |
| 'but' | **klii** |
| 'if' | **om** |
| 'because' | **pru** |
| 'when' | **kya** |
| 'and' | **ne** |
| 'under' | **prisuq** |
| 'above' | **yan** |
| 'inside' | **saka** |
| 'behind' | **gyakul** |
| 'in front of' | **klapa** |
| 'near' | **wia** |

### Passiva

**Bi syunni upyonnya.**

```
bi    sjunni   upjonɲa
bi    sjun-ni  upjon-ɲa
fish  dog-INS  eat-PASS
'The fish is eaten by the dog.'
```

### Reflexivo

**Tyulĩ dyapyaon.**

```
tjulĩ  djapjaon
tjulĩ  djapja-on
woman  wash-REFL
'The woman washes herself.'
```

### Recíproco

**Syunmi alqor.**

```
sjunmi   alŋor
sjun-mi  alŋo-r
dog-PL   see-RECP
'The dogs see each other.'
```

### Demonstrativo (perto de quem fala)

**Syun ar.**

```
sjun  ar
dog   DEM.PROX
'this dog'
```

### Demonstrativo (longe)

**Syun li.**

```
sjun  li
dog   DEM.DIST
'that dog'
```

### Imperativo

**Klaamuun.**

```
klaːmuːn
klaːm-uːn
come-IMP
'Come!'
```

### Proibitivo

**Bi waq upyonuun.**

```
bi    waŋ   upjonuːn
bi    waŋ   upjon-uːn
fish  PROH  eat-IMP
'Don't eat the fish!'
```

### Coordenação ('e')

**Syun lulim ne am bi upyon.**

```
sjun  lulim  ne   am     bi    upjon
dog   sleep  and  child  fish  eat
'The dog sleeps and the child eats the fish.'
```

### Coordenação ('mas')

**Syun lulim klii am bi upyon.**

```
sjun  lulim  kliː  am     bi    upjon
dog   sleep  but   child  fish  eat
'The dog sleeps, but the child eats the fish.'
```

### Condicional ('se')

**Syun lulim om am bi upyon.**

```
sjun  lulim  om  am     bi    upjon
dog   sleep  if  child  fish  eat
'If the dog sleeps, the child eats the fish.'
```

### Causal ('porque')

**Syun lulim pru am bi upyon.**

```
sjun  lulim  pru      am     bi    upjon
dog   sleep  because  child  fish  eat
'The child eats the fish because the dog sleeps.'
```

### Completiva ('que')

**Ka syun lulim hem syaq.**

```
ka   sjun  lulim  hem   sjaŋ
1SG  dog   sleep  COMP  know
'I know that the dog sleeps.'
```

### Possessivo independente

**Syun kilol.**

```
sjun  kilol
sjun  kil-ol
dog   1SG.POSS
'The dog is mine.'
```

### Adposição espacial

**Syun mimkyu·un prisuq lulim.**

```
sjun  mimkjuun   prisuŋ  lulim
sjun  mimkju-un  prisuŋ  lulim
dog   tree-LOC   under   sleep
'The dog sleeps under the tree.'
```

## Dicionário

231 entradas, lista `all` do Concepticon, mais 96 palavras derivadas, 1533 do vocabulário ampliado (WOLD), 7 numerais.

Formato: **grafia** /pronúncia/ [pronúncia depois das mudanças sonoras, quando muda] classe 'significado' ← base, nas derivadas

- **a** /a/ *n.* 'grandson'
- **aa** /aː/ *v.* 'sweep'
- **aagilingwe** /ˌaːɡiˈlinɡwe/ *n.* 'broom' = *aa* + *gilingwe*
- **aai** /ˈaːi/ *n.* 'mushroom'
- **aakwa** /ˈaːkwa/ *v.* 'fart'
- **aalzeo** /ˈaːlzeo/ *n.* 'plot'
- **aam** /aːm/ *n.* 'island'
- **aambram** /ˈaːmbram/ *n.* 'hair' — PL: aambrammi; GEN: aambran
- **aane** /ˈaːne/ *part.* 'how much'
- **aantwe** /ˈaːntwe/ *adj.* 'pointed'
- **aanypoq** /ˈaːɲpoŋ/ *n.* 'chair'
- **aapran** /ˈaːpran/ *v.* 'marry'
- **aaprango** /aːˈpranɡo/ *n.* 'wedding' ← *aapran* (ação)
- **aara** /ˈaːra/ *n.* 'support, rest'
- **aartimsi** /aːrˈtimsi/ *v.* 'smoke (emit smoke)'
- **aasiqdyiin** /aːˈsiŋdjiːn/ *v.* 'perspire'
- **aasuukyul** /ˈaːsuːkjul/ *n.* 'laughter'
- **aatyaa** /ˈaːtjaː/ *n.* 'remains'
- **aawuu** /ˈaːwuː/ *n.* 'enemy'
- **abya** /ˈabja/ *adj.* 'sad'
- **adwin** /ˈadwin/ *n.* 'apple'
- **agel** /ˈaɡel/ *n.* 'vagina'
- **aglaur** /ˈaɡlaur/ *n.* 'need, necessity'
- **aki** /ˈaki/ [ˈaɣi] *adj.* 'thin'
- **akim** /ˈakim/ *adj.* 'clear'
- **akkoqdwo** /aˈkːoŋdwo/ *v.* 'condemn'
- **akril** /ˈakril/ *adj.* 'blind'
- **akyaa** /ˈakjaː/ *n.* 'garden-house'
- **al** /al/ *n.* 'dove'
- **alga** /ˈalɡa/ *v.t.* 'to dig' — PST: algapu
- **algakwunytwu** /ˌalɡaˈkwuɲtwu/ *n.* 'digger' ← *alga*
- **alganii** /ˈalɡaniː/ *n.* 'hole' ← *alga*
- **alkliiqzal** /alˈkliːŋzal/ *n.* 'perjury'
- **alotwaar** /ˈalotwaːr/ *n.* 'butter'
- **alpin** /ˈalpin/ *n.* 'need'
- **alqo** /ˈalŋo/ *v.t.* 'to see' — PST: alqopu
- **alqokwunytwu** /ˌalŋoˈkwuɲtwu/ *n.* 'witness' ← *alqo* (agentivo)
- **altiim** /ˈaltiːm/ *n.* 'November'
- **aluwi** /ˈaluwi/ *adj.* 'holy'
- **alyer** /ˈaljer/ *n.* 'boar'
- **alyu** /ˈalju/ *adj.* 'drunk'
- **al·hilpiim** /alˈhilpiːm/ *n.* 'waist'
- **am** /am/ *n.* 'child (young human)' — PL: ammi; GEN: an
- **amdo** /ˈamdo/ *n.* 'jewel'
- **ami** /ˈami/ *n.* 'guard'
- **ampyo** /ˈampjo/ *v.* 'shiver'
- **amsyi** /ˈamsji/ *v.* 'increase'
- **amu** /ˈamu/ *adj.* 'wet'
- **amudhi** /ˈamuði/ *v.* 'to become wet' ← *amu*
- **amuklii** /ˈamukliː/ *n.* 'bear'
- **amuwe** /ˈamuwe/ [ˈamuwi] *v.* 'to make wet' ← *amu*
- **an** /an/ *pron.* 'ye'
- **andam** /ˈandam/ *v.* 'sail'
- **angyi** /ˈanɡji/ *v.i.* 'to play' — PST: angyipu
- **angyigo** /ˈanɡjiɡo/ [ˈanɡjiɣo] *n.* 'act of playing' ← *angyi*
- **angyikwunytwu** /ˌanɡjiˈkwuɲtwu/ *n.* 'player' ← *angyi*
- **anmam** /ˈanmam/ *n.* 'news'
- **anon** /ˈanon/ *v.* 'grow'
- **any** /aɲ/ *v.* 'go'
- **anyel** /ˈaɲel/ *adj.* 'evil'
- **aq** /aŋ/ *n.* 'larch'
- **aqam** /ˈaŋam/ *n.* 'ointment'
- **aqtyelrir** /aŋˈtjelrir/ *n.* 'cup'
- **ar** /ar/ *dem.* 'this'
- **arlokya** /ˈarlokja/ *v.* 'gather'
- **asi** /ˈasi/ *v.* 'lie (mislead)'
- **asimim** /ˈasimim/ *n.* 'fault'
- **asin** /ˈasin/ *n.* 'sling'
- **ato** /ˈato/ *n.* 'side'
- **atumtro** /aˈtumtro/ *v.* 'whisper'
- **aunyu** /ˈauɲu/ *n.* 'cart'
- **awi** /ˈawi/ *v.* 'become'
- **awum** /ˈawum/ *n.* 'ladder'
- **axa** /ˈaʃa/ *n.* 'bow'
- **axule** /ˈaʃule/ *n.* 'village'
- **aya** /ˈaja/ *adv.* 'forward'
- **ayiim** /ˈajiːm/ *n.* 'room'
- **ayum** /ˈajum/ *n.* 'queen'
- **azaq** /ˈazaŋ/ *n.* 'famine'
- **ba** /ba/ *n.* 'branch'
- **baa** /baː/ *v.* 'look for'
- **baany** /baːɲ/ *n.* 'candle'
- **baayi·il** /ˈbaːjiil/ *n.* 'autumn'
- **bakloq** /ˈbakloŋ/ *n.* 'tail' — PL: bakloqmi; GEN: baklon
- **bano** /ˈbano/ *n.* 'palm of the hand'
- **bantwa** /ˈbantwa/ *n.* 'ash' — PL: bantwami; GEN: bantwan
- **banuuny** /ˈbanuːɲ/ *v.i.* 'to laugh' — PST: banuunypu
- **banuunygo** /baˈnuːɲɡo/ *n.* 'laughter' ← *banuuny*
- **banuunyqi** /baˈnuːɲŋi/ *adj.* 'cheerful' ← *banuuny*
- **banydi** /ˈbaɲdi/ *n.* 'size'
- **bawa** /ˈbawa/ *n.* 'kidney'
- **ba·aa** /ˈbaaː/ *n.* 'month'
- **ba·asan** /ˈbaasan/ *n.* 'campfire'
- **be** /be/ *adj.* 'stingy'
- **bekol** /ˈbekol/ *n.* 'midday'
- **bekontyu** /beˈkontju/ *n.* 'butterfly'
- **belkwa** /ˈbelkwa/ *n.* 'rudder'
- **benurnu** /beˈnurnu/ *v.* 'melt'
- **beqa** /ˈbeŋa/ *v.* 'ripen'
- **beu** /ˈbeu/ *n.* 'cotton'
- **bi** /bi/ *n.* 'fish' — PL: bimi; GEN: bin
- **bibyiinun** /ˈbibjiːnun/ *n.* 'fish poison' = *bi* + *byiinun*
- **bii** /biː/ *n.* 'raft'
- **biibri** /ˈbiːbri/ *n.* 'testicles'
- **biinyaiq** /ˈbiːɲaiŋ/ *n.* 'March'
- **bikuun** /ˈbikuːn/ *adj.* 'firm, solid'
- **bikwunytwu** /biˈkwuɲtwu/ *n.* 'fisherman' = *bi* + *kwunytwu*
- **bilga** /ˈbilɡa/ *n.* 'desire'
- **bili** /ˈbili/ *v.* 'destroy'
- **biliiuu** /ˈbiliːuː/ *n.* 'flea'
- **bilinii** /ˈbiliniː/ *v.* 'damage' ← *bili* (produto)
- **bimuumi** /ˈbimuːmi/ *n.* 'fishnet' = *bi* + *muumi*
- **binliikro** /ˈbinliːkro/ *n.* 'shade/shadow' — PL: binliikromi; GEN: binliikron
- **biqtiima** /ˈbiŋtiːma/ *v.* 'hollow out'
- **biramdri·i** /biˈramdrii/ *n.* 'fishhook' = *bi* + *ramdri·i*
- **birmelpla** /birˈmelpla/ *n.* 'monkey'
- **biwamdye** /biˈwamdje/ *v.* 'be annoyed'
- **biwone** /ˈbiwone/ *n.* 'fish trap' = *bi* + *wone*
- **biyo** /ˈbijo/ *adj.* 'broken (not working)'
- **bĩ** /bĩ/ *n.* 'stranger'
- **blanmo** /ˈblanmo/ *n.* 'termites'
- **blauq** /ˈblauŋ/ *n.* 'whetstone'
- **blimlo** /ˈblimlo/ *adj.* 'sour'
- **blin** /blin/ *n.* 'blame'
- **bli·i** /ˈblii/ *n.* 'throat'
- **blĩo** /ˈblĩo/ *n.* 'bark' — PL: blĩomi; GEN: blĩon
- **bluny** /bluɲ/ *n.* 'oil'
- **blupla** /ˈblupla/ *n.* 'acorn'
- **bo** /bo/ *n.* 'sibling'
- **bokyiiny** /ˈbokjiːɲ/ *part.* 'seventy'
- **bomninyno** /bomˈniɲno/ *v.* 'untie'
- **bopla** /ˈbopla/ *part.* 'how much?'
- **bordrum** /ˈbordrum/ *v.* 'pick'
- **bordrumkyebiyi** /ˌbordrumˈkjebiji/ *v.* 'pick up' = *bordrum* + *kyebiyi*
- **bra** /bra/ *v.* 'decrease'
- **braĩ** /ˈbraĩ/ *n.* 'wind' — PL: braĩmi; GEN: braĩn
- **braĩso** /ˈbraĩso/ *adj.* 'full of wind' ← *braĩ*
- **bran** /bran/ *n.* 'friend'
- **bre** /bre/ *v.* 'deny'
- **brigyoma** /ˈbriɡjoma/ *v.* 'rush'
- **bri·ĩmtwaam** /briˈĩmtwaːm/ *part.* 'she'
- **brumsirga** /brumˈsirɡa/ *n.* 'weapons'
- **bruukanyda** /bruːˈkaɲda/ *n.* 'gate'
- **bruumgwunqam** /bruːmˈɡwunŋam/ *v.* 'peel'
- **bu** /bu/ *n.* 'river' — PL: bumi; GEN: bun
- **budrauun** /ˈbudrauːn/ *v.* 'set'
- **bugruul** /ˈbuɡruːl/ *v.* 'lay'
- **buii** /ˈbuiː/ *n.* 'fire' — PL: buiimi; GEN: buiin
- **buiio** /ˈbuiːo/ *n.* 'firefly' = *buii* + *o*
- **buiiso** /ˈbuiːso/ *adj.* 'fiery' ← *buii*
- **bum** /bum/ *n.* 'uncle'
- **bumnyun** /ˈbumɲun/ *n.* 'banyan'
- **bun** /bun/ *adj.* 'good'
- **bunal** /ˈbunal/ *n.* 'goodness' ← *bun*
- **bunykyuqu** /ˈbuɲkjuŋu/ *n.* 'spindle'
- **buom** /ˈbuom/ *adv.* 'once (in the past)'
- **buqnyo** /ˈbuŋɲo/ *v.* 'translate'
- **butiu** /ˈbutiu/ *n.* 'matter'
- **buu** /buː/ *v.* 'be born'
- **byaae** /ˈbjaːe/ [ˈbjaːi] *v.i.* 'to run' — PST: byaaepu
- **byaaego** /ˈbjaːeɡo/ [ˈbjaːeɣo] *n.* 'result of running' ← *byaae*
- **byaaekwunytwu** /ˌbjaːeˈkwuɲtwu/ *n.* 'runner' ← *byaae*
- **byaaeqi** /ˈbjaːeŋi/ *adj.* 'tending to run' ← *byaae*
- **byanpar** /ˈbjanpar/ *n.* 'chimney'
- **byaq** /bjaŋ/ *n.* 'sinew'
- **byedoqbyiny** /bjeˈdoŋbjiɲ/ *n.* 'twig'
- **byem** /bjem/ *part.* 'only'
- **byezyi** /ˈbjezji/ *v.i.* 'to blow' — PST: byezyipu
- **byi** /bji/ *v.* 'accuse'
- **byiba** /ˈbjiba/ *v.* 'cheat'
- **byiinu** /ˈbjiːnu/ *adv.* 'yesterday'
- **byiinun** /ˈbjiːnun/ *n.* 'poison'
- **byotwi** /ˈbjotwi/ *n.* 'berry' — PL: byotwimi; GEN: byotwin
- **byu** /bju/ *n.* 'granddaughter'
- **byurinxa** /bjuˈrinʃa/ *n.* 'Wednesday'
- **byutu** /ˈbjutu/ *v.* 'divide'
- **byuu** /bjuː/ *v.* 'move (affect emotionally)'
- **byuumaaqpul** /bjuːˈmaːŋpul/ *adj.* 'hard'
- **byuumhuuny** /ˈbjuːmhuːɲ/ *n.* 'wine'
- **byuyuq** /ˈbjujuŋ/ *n.* 'heat'
- **caa** /θaː/ *part.* 'or'
- **cuur** /θuːr/ *v.i.* 'to swell' — PST: cuurpu
- **cuurinii** /ˈθuːriniː/ *n.* 'swelling' ← *cuur* (produto)
- **cwubli·i** /ˈθwublii/ *n.* 'parents'
- **da** /da/ *n.* 'mosquito'
- **dalkam** /ˈdalkam/ *n.* 'cormorant'
- **dami** /ˈdami/ *n.* 'plant (vegetation)'
- **dankreploq** /ˈdankreploŋ/ *n.* 'rib'
- **daxawa** /ˈdaʃawa/ *n.* 'lie (falsehood)'
- **de** /de/ *n.* 'king'
- **den** /den/ *n.* 'mortar binder'
- **deqi·ii** /ˈdeŋiiː/ *adj.* 'light (weight)'
- **deti** /ˈdeti/ *n.* 'pike'
- **dhrekye** /ˈðrekje/ *adv.* 'hither'
- **dhyili** /ˈðjili/ *n.* 'fat' — PL: dhyilimi; GEN: dhyilin
- **dhyiliso** /ˈðjiliso/ *adj.* 'full of fat' ← *dhyili*
- **di** /di/ *v.* 'be silent'
- **dige** /ˈdiɡe/ *n.* 'money'
- **diir** /diːr/ *part.* 'without'
- **dikyi** /ˈdikji/ *n.* 'coat'
- **dinla** /ˈdinla/ *part.* 'thirty'
- **disumun** /ˈdisumun/ *adj.* 'familiar'
- **dizunbla** /diˈzunbla/ *n.* 'meaning'
- **do** /do/ *n.* 'pain'
- **doie** /ˈdoie/ *n.* 'February'
- **dosyil** /ˈdosjil/ *adj.* 'lame'
- **douqim** /ˈdouŋim/ *adj.* 'tired'
- **dozwu** /ˈdozwu/ *n.* 'towel'
- **dra** /dra/ *n.* 'middle'
- **dragwi** /ˈdraɡwi/ *n.* 'reef'
- **dram** /dram/ *adj.* 'fresh'
- **driimhabyi** /ˈdriːmhabji/ *v.* 'step'
- **driinywun** /ˈdriːɲwun/ *part.* 'fifty'
- **drul** /drul/ *v.* 'comb (verb)'
- **drulsrĩn** /ˈdrulsrĩn/ *n.* 'saw'
- **druxyom** /ˈdruʃjom/ *adj.* 'ugly'
- **druziio** /ˈdruziːo/ *n.* 'July'
- **du** /du/ *n.* 'crocodile'
- **dulkkamne** /dulˈkːamne/ *n.* 'pupil'
- **dumxyenyyu** /dumˈʃjeɲju/ *n.* 'amount'
- **dusyi** /ˈdusji/ *n.* 'post'
- **duulkony** /ˈduːlkoɲ/ *n.* 'blacksmith'
- **duun** /duːn/ *adj.* 'cooked'
- **duyu** /ˈduju/ *v.* 'love'
- **duzra** /ˈduzra/ *v.* 'decorate'
- **dwaanyuumnii** /dwaːˈɲuːmniː/ *v.* 'retreat'
- **dwalyal** /ˈdwaljal/ *n.* 'flame'
- **dwaqbiq** /ˈdwaŋbiŋ/ *part.* 'at'
- **dwaqbiqyonzim** /ˌdwaŋbiŋˈjonzim/ *adv.* 'at first' = *dwaqbiq* + *yonzim*
- **dwi** /dwi/ *n.* 'mule'
- **dwiikukaaq** /ˈdwiːkukaːŋ/ *n.* 'bunch'
- **dwiny** /dwiɲ/ *v.t.* 'to pull' — PST: dwinypu
- **dwĩ** /dwĩ/ *n.* 'tone'
- **dwu** /dwu/ *n.* 'outrigger'
- **dwuudĩnqii** /dwuːˈdĩnŋiː/ *n.* 'moustache'
- **dya** /dja/ *n.* 'religion'
- **dyakyue** /ˈdjakjue/ *n.* 'border'
- **dyapya** /ˈdjapja/ *v.t.* 'to wash' — PST: dyapyapu
- **dyapyakwunytwu** /ˌdjapjaˈkwuɲtwu/ *n.* 'thing that washes' ← *dyapya*
- **dyi** /dji/ *v.* 'announce'
- **dyii** /djiː/ *v.* 'call'
- **dyino** /ˈdjino/ *v.* 'talk'
- **dyoki·i** /ˈdjokii/ *v.* 'beat'
- **dyonkyu** /ˈdjonkju/ *n.* 'ox'
- **dyu** /dju/ *adj.* 'yellow'
- **dyunyu** /ˈdjuɲu/ *n.* 'pan'
- **e** /e/ [i] *n.* 'blood' — PL: emi; GEN: en
- **ebawan** /ˈebawan/ *n.* 'deity'
- **edyĩ** /ˈedjĩ/ *n.* 'brother'
- **edyun** /ˈedjun/ *v.i.* 'to burn' — PST: edyunpu
- **ehu** /ˈehu/ *n.* 'sorcerer'
- **ekla** /ˈekla/ *n.* 'gift'
- **ekwo** /ˈekwo/ *n.* 'beehive'
- **el** /el/ *n.* 'dew'
- **elgyahii** /ˈelɡjahiː/ *n.* 'eyelash'
- **elkhi** /ˈelkʰi/ *adj.* 'male (of animal)'
- **elyum** /ˈeljum/ *v.* 'dribble'
- **ema** /ˈema/ *n.* 'lead (chemical element)'
- **emi** /ˈemi/ *v.i.* 'to turn' — PST: emipu
- **emtimbir** /emˈtimbir/ *n.* 'kid'
- **en** /en/ *adj.* 'raw'
- **enaaru** /ˈenaːru/ *adj.* 'open (state)'
- **endan·yu** /enˈdanju/ *v.t.* 'to crush/grind' — PST: endan·yupu
- **endan·yunii** /enˈdanjuniː/ *n.* 'flour' ← *endan·yu*
- **eniim** /ˈeniːm/ *n.* 'shark'
- **enpre** /ˈenpre/ *v.* 'forge'
- **eny** /eɲ/ *n.* 'part'
- **enyinhi** /eˈɲinhi/ *v.* 'escape'
- **en·yin** /ˈenjin/ *n.* 'threshing-floor'
- **epiltii** /eˈpiltiː/ *part.* 'last (final)'
- **eplu·u** /ˈepluu/ *v.* 'tan'
- **epo** /ˈepo/ *n.* 'lagoon'
- **epra** /ˈepra/ *v.* 'hire'
- **epuĩ** /ˈepuĩ/ *part.* 'again'
- **eq** /eŋ/ *n.* 'pitchfork'
- **eqhi** /ˈeŋhi/ *n.* 'goat'
- **esu** /ˈesu/ *n.* 'dandruff'
- **etwi** /ˈetwi/ *adj.* 'red'
- **etwidhi** /ˈetwiði/ *v.* 'to blush' ← *etwi*
- **ewi** /ˈewi/ *n.* 'valley'
- **eya** /ˈeja/ *n.* 'wolf'
- **ezya** /ˈezja/ *n.* 'tear (of eye)'
- **ga** /ɡa/ *n.* 'banana'
- **gaa** /ɡaː/ *n.* 'grapevine'
- **gaka** /ˈɡaka/ *n.* 'ball'
- **gam** /ɡam/ *n.* 'puzzle'
- **gamimkyu** /ɡaˈmimkju/ *n.* 'banana tree' = *ga* + *mimkyu*
- **gaqmemtyii** /ɡaŋˈmemtjiː/ *part.* 'next'
- **gaue** /ˈɡaue/ *n.* 'bead'
- **ge** /ɡe/ [ɡi] *interr.* 'who?'
- **gelplen** /ˈɡelplen/ *n.* 'sort'
- **geny** /ɡeɲ/ *interr.* 'how'
- **gi** /ɡi/ *adj.* 'deep'
- **gidin** /ˈɡidin/ *v.* 'cook'
- **gidingwaaqum** /ɡiˈdinɡwaːŋum/ *n.* 'cookhouse' = *gidin* + *gwaaqum*
- **giilglu** /ˈɡiːlɡlu/ *adj.* 'wise'
- **giimta** /ˈɡiːmta/ *n.* 'potato'
- **giipaanymi** /ɡiːˈpaːɲmi/ *n.* 'sugar'
- **giitra** /ˈɡiːtra/ *n.* 'Monday'
- **gilingwe** /ɡiˈlinɡwe/ *n.* 'thing'
- **gilyuq** /ˈɡiljuŋ/ *n.* 'stepmother'
- **gimhu** /ˈɡimhu/ *adj.* 'pregnant'
- **ginlum** /ˈɡinlum/ *adj.* 'warm'
- **ginlumal** /ˈɡinlumal/ *n.* 'warmth' ← *ginlum*
- **ginlumdhi** /ɡinˈlumði/ *v.* 'to warm up' ← *ginlum*
- **ginlumiwe** /ɡinˈlumiwe/ [ɡinˈlumiwi] *v.* 'to heat' ← *ginlum*
- **girmo** /ˈɡirmo/ *n.* 'men's house'
- **gisen** /ˈɡisen/ *n.* 'mush'
- **gitohuny** /ˈɡitohuɲ/ *n.* 'pumpkin'
- **gixuuqu** /ˈɡiʃuːŋu/ *adj.* 'deaf'
- **gĩlbiglu** /ˈɡĩlbiɡlu/ *v.* 'wake'
- **gĩlbiglukyebiyi** /ɡĩlˌbiɡluˈkjebiji/ *v.* 'wake up' = *gĩlbiglu* + *kyebiyi*
- **gla** /ɡla/ *v.i.* 'sit' — PST: glapu
- **glamwii** /ˈɡlamwiː/ *n.* 'flesh'
- **glankwute** /ˈɡlankwute/ *v.* 'speak'
- **glany** /ɡlaɲ/ *v.i.* 'to freeze' — PST: glanypu
- **glanyosin** /ˈɡlaɲosin/ *part.* 'forty'
- **glauum** /ˈɡlauːm/ *v.* 'sit down' = *gla* + *uum*
- **gle** /ɡle/ *n.* 'leash'
- **glenygyo** /ˈɡleɲɡjo/ *adj.* 'straight'
- **glii** /ɡliː/ *v.* 'boast'
- **gliidyi** /ˈɡliːdji/ *v.* 'finish'
- **gliimiiqkyo** /ɡliːˈmiːŋkjo/ *n.* 'ring'
- **glinmin** /ˈɡlinmin/ *n.* 'vegetables'
- **glo** /ɡlo/ *adj.* 'gentle'
- **gloi** /ˈɡloi/ *n.* 'way'
- **glolkyeq** /ˈɡlolkjeŋ/ *v.* 'sparkle, twinkle'
- **glul** /ɡlul/ *n.* 'edge'
- **glumem** /ˈɡlumem/ *adj.* 'wrong'
- **glumpi·in** /ˈɡlumpiin/ *v.* 'call by name'
- **gol** /ɡol/ *v.* 'shriek'
- **gon** /ɡon/ *num.* 'hundred'
- **gonpor** /ˈɡonpor/ *n.* 'iron'
- **goqbyil** /ˈɡoŋbjil/ *n.* 'fork'
- **gra** /ɡra/ *n.* 'fingernail or toenail'
- **granaamsu** /ɡraˈnaːmsu/ *n.* 'cross'
- **granaamsugilingwe** /ˌɡranaːmˌsuɡiˈlinɡwe/ *n.* 'bridge' = *granaamsu* + *gilingwe*
- **gre** /ɡre/ *n.* 'pen'
- **grepopu** /ˈɡrepopu/ *v.* 'feel (tactually)'
- **gri** /ɡri/ *n.* 'rabbit'
- **gro** /ɡro/ *v.i.* 'to stand' — PST: gropu
- **grokyebiyi** /ɡroˈkjebiji/ *v.* 'stand up' = *gro* + *kyebiyi*
- **grony** /ɡroɲ/ *v.* 'land (descend)'
- **gru** /ɡru/ *v.* 'kick'
- **grum** /ɡrum/ *v.* 'flee'
- **gu** /ɡu/ *neg.* 'not' — expresso por afixo verbal
- **gugliq** /ˈɡuɡliŋ/ *n.* 'beer'
- **gukyim** /ˈɡukjim/ *n.* 'scorpion'
- **gul** /ɡul/ *n.* 'camel'
- **gum** /ɡum/ *adj.* 'guilty'
- **gumdo** /ˈɡumdo/ *v.* 'cough'
- **guony** /ˈɡuoɲ/ *v.t.* 'to scratch' — PST: guonypu
- **guq** /ɡuŋ/ *n.* 'spider web'
- **guqmal** /ˈɡuŋmal/ *n.* 'grasshopper'
- **guua** /ˈɡuːa/ *v.t.* 'to hear' — PST: guuapu
- **guuya** /ˈɡuːja/ *n.* 'ocean'
- **guyimnel** /ɡuˈjimnel/ *v.* 'protect'
- **gwa** /ɡwa/ *n.* 'grass' — PL: gwami; GEN: gwan
- **gwaa** /ɡwaː/ *v.* 'swallow'
- **gwaaqum** /ˈɡwaːŋum/ *n.* 'house' — PL: gwaaqummi; GEN: gwaaqun
- **gwaarsya** /ˈɡwaːrsja/ *n.* 'claw'
- **gwabyilsu** /ɡwaˈbjilsu/ *n.* 'ghost'
- **gwakoya** /ˈɡwakoja/ *n.* 'bruise'
- **gwaqmi** /ˈɡwaŋmi/ *v.i.* 'to think' — PST: gwaqmipu
- **gwaqmikwunytwu** /ˌɡwaŋmiˈkwuɲtwu/ *n.* 'one who thinks' ← *gwaqmi*
- **gwaqminii** /ˈɡwaŋminiː/ *n.* 'what is thought' ← *gwaqmi*
- **gwaso** /ˈɡwaso/ *adj.* 'full of grass' ← *gwa*
- **gwe** /ɡwe/ *v.* 'whistle'
- **gwebrokha** /ˈɡwebrokʰa/ *adj.* 'nasty, dire'
- **gwedyurmu** /ɡweˈdjurmu/ *n.* 'deceit'
- **gwen** /ɡwen/ *n.* 'bull'
- **gwenqon** /ˈɡwenŋon/ *n.* 'club'
- **gwenum** /ˈɡwenum/ *n.* 'poncho'
- **gwi** /ɡwi/ *adj.* 'certain'
- **gwiinke** /ˈɡwiːnke/ [ˈɡwiːnki] *v.t.* 'know (something)' — PST: gwiinkepu
- **gwiklim** /ˈɡwiklim/ *n.* 'tax'
- **gwilwir** /ˈɡwilwir/ *n.* 'yam'
- **gwim** /ɡwim/ *n.* 'nose' — PL: gwimmi; GEN: gwin
- **gwina** /ˈɡwina/ *v.* 'thresh'
- **gwinboq** /ˈɡwinboŋ/ *n.* 'mistake'
- **gwiny** /ɡwiɲ/ *pron.* '2sg pronoun'
- **gwireu** /ˈɡwireu/ *adj.* 'strong, mighty, powerful'
- **gwo** /ɡwo/ *n.* 'speech'
- **gwonyka** /ˈɡwoɲka/ *n.* 'olive'
- **gworyitwii** /ˈɡworjitwiː/ *v.* 'kiss'
- **gwu** /ɡwu/ *v.* 'tumble'
- **gwuku·u** /ˈɡwukuu/ *v.* 'shake'
- **gwunbye** /ˈɡwunbje/ *v.* 'knit'
- **gyacuu** /ˈɡjaθuː/ *n.* 'spade'
- **gyakul** /ˈɡjakul/ *part.* 'behind'
- **gyanginygol** /ɡjanˈɡiɲɡol/ *v.* 'want'
- **gyarzyinpri** /ɡjarˈzjinpri/ *n.* 'bolt of lightning'
- **gyeltraaĩ** /ˈɡjeltraːĩ/ *n.* 'disease'
- **gyeti** /ˈɡjeti/ *part.* 'why?'
- **gyi** /ɡji/ *n.* 'daughter-in-law (of woman)'
- **gyiiguul** /ˈɡjiːɡuːl/ *n.* 'spear'
- **gyiiqkar** /ˈɡjiːŋkar/ *n.* 'paw'
- **gyoqplobyi** /ˈɡjoŋplobji/ *n.* 'tip'
- **gyoqpyolphu** /ɡjoŋˈpjolpʰu/ *part.* 'we (exclusive)'
- **gyosa** /ˈɡjosa/ *v.* 'steal'
- **gyosakwunytwu** /ˌɡjosaˈkwuɲtwu/ *n.* 'thief' ← *gyosa* (agentivo)
- **gyosyi** /ˈɡjosji/ *n.* 'elephant'
- **gyu** /ɡju/ *adj.* 'slim'
- **gyubloryo** /ɡjuˈblorjo/ *adj.* 'dark'
- **gyubloryoal** /ɡjuˈblorjoal/ *n.* 'darkness' ← *gyubloryo* (qualidade)
- **gyumdyi** /ˈɡjumdji/ *adj.* 'true'
- **gyunkyel** /ˈɡjunkjel/ *adv.* 'thither'
- **gyunpaqu** /ˈɡjunpaŋu/ *adj.* 'foreign'
- **gyusye** /ˈɡjusje/ *adj.* 'alone'
- **gyuu** /ɡjuː/ *n.* 'blister'
- **gyuubu** /ˈɡjuːbu/ *v.* 'mow'
- **gyuwi** /ˈɡjuwi/ *n.* 'road' — PL: gyuwimi; GEN: gyuwin
- **ha** /ha/ *adj.* 'low'
- **haam** /haːm/ *n.* 'mosque'
- **haile** /ˈhaile/ *n.* 'low tide' = *ha* + *ile*
- **haim** /ˈhaim/ *v.* 'break (cleave)'
- **hanlaa** /ˈhanlaː/ *n.* 'call (appeal)'
- **hapersya** /haˈpersja/ *n.* 'earlobe'
- **haphorbo** /haˈpʰorbo/ *v.* 'fill'
- **he** /he/ [hi] *n.* 'breast' — PL: hemi; GEN: hen
- **hekiplo** /ˈhekiplo/ *n.* 'breath'
- **hemnu** /ˈhemnu/ *n.* 'death'
- **hemyoq** /ˈhemjoŋ/ *n.* 'noose'
- **hen** /hen/ *v.* 'arrive'
- **hen·yu** /ˈhenju/ *n.* 'gold'
- **hepli** /ˈhepli/ *n.* 'boot'
- **heq** /heŋ/ *v.* 'imitate'
- **hera·aar** /ˈheraaːr/ *n.* 'boat'
- **herpaal** /ˈherpaːl/ *n.* 'sailcloth'
- **hesaa** /ˈhesaː/ *part.* 'no'
- **hi** /hi/ *n.* 'wave'
- **hii** /hiː/ *n.* 'udder'
- **hiiqgye** /ˈhiːŋɡje/ *n.* 'port'
- **hiiyiqpyu** /hiːˈjiŋpju/ *n.* 'armour'
- **him** /him/ *n.* 'temples'
- **hipin** /ˈhipin/ *n.* 'physician'
- **hitu** /ˈhitu/ *n.* 'dinner'
- **hiuua** /ˈhiuːa/ *adv.* 'already'
- **hiyiim** /ˈhijiːm/ *n.* 'strength'
- **ho** /ho/ *adj.* 'ripe'
- **hoi** /ˈhoi/ *n.* 'married woman'
- **hoiipo** /ˈhoiːpo/ *v.* 'harm, injure, damage'
- **hoimphem** /hoˈimpʰem/ *n.* 'tool'
- **hon** /hon/ *n.* 'owl'
- **hoxuum** /ˈhoʃuːm/ *n.* 'crow'
- **hu** /hu/ *n.* 'mind'
- **hudyi** /ˈhudji/ *n.* 'wife' — PL: hudyimi; GEN: hudyin
- **hukla** /ˈhukla/ *adj.* 'big'
- **hukladhi** /ˈhuklaði/ *v.* 'to grow' ← *hukla*
- **huklawe** /ˈhuklawe/ [ˈhuklawi] *v.* 'to enlarge' ← *hukla*
- **hukla·al** /ˈhuklaal/ *n.* 'size' ← *hukla*
- **hute** /ˈhute/ *adj.* 'clean'
- **huu** /huː/ *n.* 'son-in-law (of man)'
- **huulkhipyo** /ˈhuːlkʰipjo/ *part.* 'between'
- **i** /i/ *n.* 'charcoal'
- **ia** /ˈia/ *n.* 'scar'
- **ibyipe** /ˈibjipe/ *n.* 'vine'
- **idiyaa** /ˈidijaː/ *n.* 'victory'
- **idyol** /ˈidjol/ *v.* 'smoke (inhale)'
- **ii** /iː/ *n.* 'scale'
- **iiam** /ˈiːam/ *n.* 'flesh/meat' — PL: iiammi; GEN: iian
- **iibro** /ˈiːbro/ *n.* 'booty'
- **iiiio** /ˈiːiːo/ *v.* 'injure'
- **iiiionii** /iːˈiːoniː/ *n.* 'wound' ← *iiiio* (produto)
- **iikum** /ˈiːkum/ [ˈiːɣum] *v.t.* 'to smell' — PST: iikumpu
- **iikumso** /iːˈkumso/ *adj.* 'stinking' ← *iikum* (proprietivo)
- **iilwanydii** /iːlˈwaɲdiː/ *n.* 'widow'
- **iimxwo** /ˈiːmʃwo/ *adj.* 'closed'
- **iimya** /ˈiːmja/ *v.i.* 'to flow' — PST: iimyapu
- **iin** /iːn/ *n.* 'carcass'
- **iinkel** /ˈiːnkel/ *n.* 'trough'
- **iipyum** /ˈiːpjum/ *n.* 'oar'
- **iiq** /iːŋ/ *n.* 'egg' — PL: iiqmi; GEN: iin
- **iiu** /ˈiːu/ *n.* 'hell'
- **ikalel** /ˈikalel/ *n.* 'deer'
- **iki** /ˈiki/ *v.* 'add'
- **ikiim** /ˈikiːm/ *n.* 'paddy'
- **ikluu** /ˈikluː/ *adj.* 'left'
- **ikul** /ˈikul/ *v.* 'cast'
- **ikyi** /ˈikji/ *n.* 'wasp'
- **il** /il/ *v.* 'earn'
- **ile** /ˈile/ *n.* 'tide'
- **ilo** /ˈilo/ *n.* 'beam'
- **im** /im/ *n.* 'pot'
- **imkri·il** /ˈimkriil/ *n.* 'boy'
- **imli** /ˈimli/ *n.* 'demon'
- **imolpyer** /iˈmolpjer/ *n.* 'time'
- **impehi** /ˈimpehi/ *v.* 'hide (conceal)'
- **implaa** /ˈimplaː/ *v.* 'crouch'
- **imyu** /ˈimju/ *n.* 'millet'
- **imzwinykho** /imˈzwiɲkʰo/ *n.* 'half'
- **in** /in/ *v.* 'kneel'
- **inbli** /ˈinbli/ *n.* 'flour'
- **inklu** /ˈinklu/ *n.* 'rape'
- **innya** /ˈinɲa/ *adj.* 'new'
- **innyawe** /ˈinɲawe/ [ˈinɲawi] *v.* 'to make new' ← *innya*
- **innya·al** /ˈinɲaal/ *n.* 'newness' ← *innya*
- **inpo** /ˈinpo/ *v.* 'swing (something)'
- **inqebyi** /ˈinŋebji/ *v.* 'dare'
- **insyur** /ˈinsjur/ *n.* 'peace'
- **inxeyi** /ˈinʃeji/ *n.* 'sound or noise'
- **iny** /iɲ/ *n.* 'area'
- **inyumqi** /iˈɲumŋi/ *n.* 'yolk'
- **ipi** /ˈipi/ *n.* 'Thursday'
- **ipiikwu** /ˈipiːkwu/ *n.* 'goitre'
- **ipla** /ˈipla/ *v.* 'dance'
- **ipu** /ˈipu/ *n.* 'quail'
- **ipulmi** /iˈpulmi/ *n.* 'razor'
- **ipyo** /ˈipjo/ *n.* 'mill'
- **iq** /iŋ/ *v.t.* 'to hunt' — PST: iqpu
- **iqabiir** /ˈiŋabiːr/ *part.* 'twice'
- **iqka** /ˈiŋka/ *n.* 'doubt'
- **iqkwunytwu** /iŋˈkwuɲtwu/ *n.* 'hunter' ← *iq*
- **iqma** /ˈiŋma/ *v.* 'let, permit'
- **iqqi** /ˈiŋŋi/ *adj.* 'tending to hunt' ← *iq*
- **iqzyuq** /ˈiŋzjuŋ/ *n.* 'message'
- **ir** /ir/ *n.* 'springtime'
- **irbiikwu** /ˈirbiːkwu/ *v.* 'turn over'
- **irsyinxwal** /irˈsjinʃwal/ *v.* 'remain'
- **irtaqli** /irˈtaŋli/ *n.* 'he-goat'
- **isun** /ˈisun/ *n.* 'cliff'
- **isyun** /ˈisjun/ *n.* 'lightning'
- **iunsa** /iˈunsa/ *v.* 'make'
- **iwa** /ˈiwa/ *n.* 'pillow'
- **iwao** /ˈiwao/ *adj.* 'crooked'
- **ixu** /ˈiʃu/ *v.* 'bring'
- **ixukyebiyi** /ˌiʃuˈkjebiji/ *v.* 'bring up' = *ixu* + *kyebiyi*
- **ixyi** /ˈiʃji/ *n.* 'war'
- **i·i** /ˈii/ *part.* 'for a long time'
- **i·ĩmqo** /iˈĩmŋo/ *n.* 'drum'
- **ĩdil** /ˈĩdil/ *n.* 'gourd'
- **ĩgisa** /ˈĩɡisa/ *n.* 'pubic hair'
- **ĩl** /ĩl/ *quant.* 'many'
- **ĩm** /ĩm/ *n.* 'tin'
- **ĩmdhwi** /ˈĩmðwi/ *v.* 'dry up'
- **ĩmklinii** /ˈĩmkliniː/ *n.* 'sin'
- **ĩmnyiwaam** /ˈĩmɲiwaːm/ *n.* 'tower'
- **ĩmupla** /ˈĩmupla/ *adj.* 'colourful'
- **ĩpi** /ˈĩpi/ [ˈĩβi] *v.t.* 'to sew' — PST: ĩpipu
- **ĩpikwunytwu** /ˌĩpiˈkwuɲtwu/ [ˌĩβikˈwuɲtwu] *n.* 'tailor' ← *ĩpi*
- **ĩpikwunytwu** /ˌĩpiˈkwuɲtwu/ *n.* 'tailor' ← *ĩpi* (agentivo)
- **ĩpinii** /ˈĩpiniː/ [ˈĩβiniː] *n.* 'garment' ← *ĩpi*
- **ĩr** /ĩr/ *n.* 'moon'
- **ka** /ka/ *pron.* '1sg pronoun'
- **kaa** /kaː/ *v.* 'catch'
- **kaakadyi** /ˈkaːkadji/ *v.* 'urge'
- **kaakinyiq** /ˈkaːkiɲiŋ/ *adj.* 'healthy'
- **kaakwunytwu** /kaːˈkwuɲtwu/ *n.* 'captive' ← *kaa* (agentivo)
- **kaaqnamam** /ˈkaːŋnamam/ *adj.* 'grey'
- **kagrul** /ˈkaɡrul/ *adj.* 'wide'
- **kagrulal** /ˈkaɡrulal/ *n.* 'width' ← *kagrul*
- **kagruliwe** /kaˈɡruliwe/ [kaɡˈruliwi] *v.* 'to make wide' ← *kagrul*
- **kamduli** /ˈkamduli/ *v.* 'measure'
- **kamyu** /ˈkamju/ *v.* 'can'
- **kanaq** /ˈkanaŋ/ *v.* 'owe'
- **kansyalpiq** /kanˈsjalpiŋ/ *n.* 'grandparents'
- **kany** /kaɲ/ *v.* 'ask (inquire)'
- **kanyyin** /ˈkaɲjin/ *n.* 'ship'
- **kar** /kar/ *v.* 'jump'
- **karkakaq** /ˈkarkakaŋ/ *n.* 'cape'
- **kartruq** /ˈkartruŋ/ *part.* 'sixty'
- **kasumqum** /kaˈsumŋum/ *v.* 'connect'
- **kasyapli** /ˈkasjapli/ *adj.* 'easy'
- **kawii** /ˈkawiː/ *adj.* 'bright'
- **kayi·in** /ˈkajiin/ *v.* 'join'
- **kayony** /ˈkajoɲ/ *n.* 'guest'
- **ke** /ke/ [ki] *n.* 'ear' — PL: kemi; GEN: ken
- **kegliimiiqkyo** /ˌkeɡliːˈmiːŋkjo/ *n.* 'earring' = *ke* + *gliimiiqkyo*
- **kenlo** /ˈkenlo/ *part.* 'second'
- **kenmaqruu** /kenˈmaŋruː/ *n.* 'Sunday'
- **kepyii** /ˈkepjiː/ *n.* 'string'
- **keqgyipu** /ˈkeŋɡjipu/ *adj.* 'happy'
- **keul** /ˈkeul/ *n.* 'divorce'
- **khamnya** /ˈkʰamɲa/ *v.i.* 'to float' — PST: khamnyapu
- **khan** /kʰan/ *adj.* 'skilful'
- **khemtutu** /ˈkʰemtutu/ *n.* 'nipple'
- **khimpu** /ˈkʰimpu/ *v.i.* 'to vomit' — PST: khimpupu
- **khin** /kʰin/ *n.* 'skin/hide' — PL: khinmi; GEN: khin
- **kho** /kʰo/ *n.* 'canoe'
- **khunzimni** /kʰunˈzimni/ *n.* 'tongs'
- **ki** /ki/ *quant.* 'all'
- **kiaa** /ˈkiaː/ *n.* 'coin'
- **kidi** /ˈkidi/ *v.* 'sieve'
- **kidrangaq** /kiˈdranɡaŋ/ *n.* 'battle-axe'
- **kii** /kiː/ *v.* 'light (ignite)'
- **kiiiblii** /ˈkiːibliː/ *v.* 'get dressed'
- **kiinhim** /ˈkiːnhim/ *n.* 'collar'
- **kiitru** /ˈkiːtru/ *n.* 'language'
- **kika** /ˈkika/ *v.* 'notice'
- **kikwe** /ˈkikwe/ *v.* 'rinse'
- **kilqa** /ˈkilŋa/ *n.* 'animal' — PL: kilqami; GEN: kilqan
- **kilqaso** /ˈkilŋaso/ *adj.* 'full of animal' ← *kilqa*
- **kim** /kim/ *n.* 'water' — PL: kimmi; GEN: kin
- **kimgiim** /ˈkimɡiːm/ *n.* 'jug'
- **kimso** /ˈkimso/ *adj.* 'watery' ← *kim*
- **kimun** /ˈkimun/ *n.* 'face'
- **kindwii** /ˈkindwiː/ *v.* 'irrigate'
- **kindyumwo** /kinˈdjumwo/ *v.* 'thunder (verb)'
- **kinyi** /ˈkiɲi/ *n.* 'daughter'
- **kinykyii** /ˈkiɲkjiː/ *v.t.* 'to carry' — PST: kinykyiipu
- **kipi** /ˈkipi/ *n.* 'bracelet'
- **kipyiiq** /ˈkipjiːŋ/ *v.* 'tinkle'
- **kiq** /kiŋ/ *n.* 'quarrel'
- **kisyuun** /ˈkisjuːn/ *n.* 'December'
- **kityim** /ˈkitjim/ *n.* 'kangaroo'
- **kiu** /ˈkiu/ *n.* 'cattle'
- **kiukwunytwu** /ˌkiuˈkwuɲtwu/ *n.* 'herdsman' = *kiu* + *kwunytwu*
- **kiyo** /ˈkijo/ *v.* 'chat'
- **kiyu** /ˈkiju/ *v.* 'get'
- **kiyudouqim** /ˌkijuˈdouŋim/ *v.* 'get tired' = *kiyu* + *douqim*
- **kki** /kːi/ *n.* 'hill'
- **kkuxaan** /ˈkːuʃaːn/ *v.* 'bless'
- **klaam** /klaːm/ *v.i.* 'to come' — PST: klaampu
- **klaamkrai** /ˈklaːmkrai/ *v.* 'come back' = *klaam* + *krai*
- **klaamqipo** /ˈklaːmŋipo/ *n.* 'stallion'
- **klapa** /ˈklapa/ *part.* 'in front of'
- **kle** /kle/ *part.* 'with'
- **kletyii** /ˈkletjiː/ *v.* 'bend (something)'
- **kli** /kli/ *n.* 'garden'
- **klikan** /ˈklikan/ [ˈkliɣan] *n.* 'sand' — PL: klikanmi; GEN: klikan
- **klikano** /ˈklikano/ *n.* 'sandfly' = *klikan* + *o*
- **klikanso** /kliˈkanso/ [kliˈɣanso] *adj.* 'sandy' ← *klikan*
- **klipina** /ˈklipina/ *n.* 'eyebrow'
- **kliwel** /ˈkliwel/ *adj.* 'pretty'
- **kliyu** /ˈkliju/ *n.* 'jaguar'
- **klĩlpi** /ˈklĩlpi/ *v.* 'knock'
- **klĩmqepa** /ˈklĩmŋepa/ *n.* 'digging stick'
- **klĩya** /ˈklĩja/ *v.* 'obey'
- **kloga** /ˈkloɡa/ *v.* 'jog'
- **klomsyiilwan** /klomˈsjiːlwan/ *n.* 'nape of the neck'
- **klu** /klu/ *n.* 'current'
- **kluiin** /ˈkluiːn/ *adv.* 'suddenly'
- **kluiixi** /ˈkluiːʃi/ *n.* 'hour'
- **kluin** /ˈkluin/ *n.* 'flock'
- **klulbrumplu** /klulˈbrumplu/ *v.* 'seem'
- **klununy** /ˈklunuɲ/ *n.* 'worm' — PL: klununymi; GEN: klunun
- **ko** /ko/ *n.* 'tobacco'
- **koaan** /ˈkoaːn/ *v.* 'meet'
- **kobigli** /ˈkobiɡli/ *n.* 'cuckoo'
- **kobrauun** /ˈkobrauːn/ *v.* 'command'
- **komtu** /ˈkomtu/ *n.* 'camp'
- **konu** /ˈkonu/ *n.* 'fox'
- **koplu** /ˈkoplu/ *n.* 'chieftain'
- **koqwiba** /ˈkoŋwiba/ *v.* 'improve'
- **kosil** /ˈkosil/ *v.t.* 'to hold' — PST: kosilpu
- **kosyir** /ˈkosjir/ *v.* 'lead (guide)'
- **kowuqtal** /koˈwuŋtal/ *n.* 'axe'
- **krai** /ˈkrai/ *n.* 'back' — PL: kraimi; GEN: krain
- **kraime** /ˈkraime/ *n.* 'hunger'
- **krapyurqa** /kraˈpjurŋa/ *part.* 'yes'
- **kreyuka** /ˈkrejuka/ *v.* 'mumble'
- **kriblo** /ˈkriblo/ *n.* 'Saturday'
- **krikuum** /ˈkrikuːm/ *v.* 'chop (into pieces)'
- **kripu** /ˈkripu/ *v.* 'show'
- **krukleqpii** /kruˈkleŋpiː/ *n.* 'sleeve'
- **krum** /krum/ *n.* 'penis'
- **kruqbum** /ˈkruŋbum/ *n.* 'lasso'
- **krur** /krur/ *n.* 'common cold (disease)'
- **kruti** /ˈkruti/ *n.* 'intention'
- **ku** /ku/ *v.i.* 'to die' — PST: kupu
- **kugisra** /ˈkuɡisra/ *n.* 'beech'
- **kugo** /ˈkuɡo/ [ˈkuɣo] *n.* 'death' ← *ku*
- **kuhel** /ˈkuhel/ *n.* 'anvil'
- **kukinyni** /kuˈkiɲni/ *n.* 'pocket'
- **kulno** /ˈkulno/ *n.* 'stick' — PL: kulnomi; GEN: kulnon
- **kumgim** /ˈkumɡim/ *n.* 'mother-in-law (of man)'
- **kun** /kun/ *n.* 'gun'
- **kuq** /kuŋ/ *v.* 'crawl'
- **kuqgruu** /ˈkuŋɡruː/ *v.* 'piss'
- **kuqtu** /ˈkuŋtu/ *v.* 'open'
- **kuunpyiq** /ˈkuːnpjiŋ/ *n.* 'willow'
- **kuunpyuum** /ˈkuːnpjuːm/ *n.* 'winter'
- **kuunyama** /ˈkuːɲama/ *n.* 'slave'
- **kuuquu** /ˈkuːŋuː/ *n.* 'clothing'
- **kuwean** /ˈkuwean/ *n.* 'helmet'
- **ku·uum** /ˈkuuːm/ *n.* 'door'
- **kwa** /kwa/ *v.* 'admit'
- **kwaampli** /ˈkwaːmpli/ *n.* 'hole'
- **kwaasyambu** /kwaːˈsjambu/ *v.* 'bother'
- **kwaila** /ˈkwaila/ *n.* 'yard'
- **kwal** /kwal/ *v.* 'plough'
- **kwam** /kwam/ *n.* 'tumpline'
- **kwanoim** /ˈkwanoim/ *v.* 'splash'
- **kwar** /kwar/ *n.* 'baby'
- **kwatildu** /kwaˈtildu/ *n.* 'thirst'
- **kwau** /ˈkwau/ *n.* 'belly' — PL: kwaumi; GEN: kwaun
- **kwe** /kwe/ *part.* 'which?'
- **kwi** /kwi/ *v.* 'cure'
- **kwigiq** /ˈkwiɡiŋ/ *n.* 'ambush'
- **kwii** /kwiː/ *n.* 'arm/hand' — PL: kwiimi; GEN: kwiin
- **kwiimiinyxwa** /kwiːˈmiːɲʃwa/ *n.* 'stepdaughter'
- **kwin** /kwin/ *v.* 'be hungry'
- **kwinynu** /ˈkwiɲnu/ *adj.* 'powerful'
- **kwisaan** /ˈkwisaːn/ *v.* 'guess'
- **kwiyaakiim** /ˈkwijaːkiːm/ *v.* 'hope (something)'
- **kwo** /kwo/ *v.t.* 'to split' — PST: kwopu
- **kwoben** /ˈkwoben/ *v.* 'disappear'
- **kwonii** /ˈkwoniː/ *n.* 'crack' ← *kwo*
- **kworzi** /ˈkworzi/ *n.* 'night' — PL: kworzimi; GEN: kworzin
- **kwou** /ˈkwou/ *n.* 'pity'
- **kwu** /kwu/ *v.* 'repair, mend'
- **kwuel** /ˈkwuel/ *n.* 'merchant'
- **kwuigriq** /ˈkwuiɡriŋ/ *adj.* 'dear'
- **kwunytwu** /ˈkwuɲtwu/ *n.* 'man' — PL: kwunytwumi; GEN: kwunytwun = mesma palavra que person
- **kwunytwu** /ˈkwuɲtwu/ *n.* 'person' — **PL: kwunytwu** (irregular); GEN: kwunytwun
- **kwuugeq** /ˈkwuːɡeŋ/ *v.* 'commend'
- **kwuuti** /ˈkwuːti/ *n.* 'veil'
- **kya** /kja/ *interr.* 'when?'
- **kyaii** /ˈkjaiː/ *n.* 'mountain or hill'
- **kyakyomtaa** /kjaˈkjomtaː/ *v.* 'bore'
- **kyam** /kjam/ *n.* 'ice' — PL: kyammi; GEN: kyan
- **kyani** /ˈkjani/ *v.* 'twist'
- **kyaqil** /ˈkjaŋil/ *n.* 'dress'
- **kyar** /kjar/ *n.* 'pine'
- **kyayu** /ˈkjaju/ *n.* 'gill'
- **kye** /kje/ *v.* 'turn out'
- **kyebiyi** /ˈkjebiji/ *part.* 'up'
- **kyi** /kji/ *n.* 'father' — PL: kyimi; GEN: kyin
- **kyiedyĩ** /ˈkjiedjĩ/ *n.* 'father's brother' = *kyi* + *edyĩ*
- **kyii** /kjiː/ *n.* 'window'
- **kyiimirii** /ˈkjiːmiriː/ *v.* 'win'
- **kyikyo** /ˈkjikjo/ *n.* 'widower'
- **kyima** /ˈkjima/ *n.* 'fine'
- **kyimkwa** /ˈkjimkwa/ *n.* 'price'
- **kyipu** /ˈkjipu/ *n.* 'father's sister' = *kyi* + *pu*
- **kyiq** /kjiŋ/ *v.* 'lose'
- **kyiqta** /ˈkjiŋta/ *n.* 'marriage, wedding'
- **kyir** /kjir/ *part.* 'zero'
- **kyityany** /ˈkjitjaɲ/ *n.* 'sack'
- **kyĩpam** /ˈkjĩpam/ *n.* 'life'
- **kyoyi** /ˈkjoji/ *n.* 'husband' — PL: kyoyimi; GEN: kyoyin = mesma palavra que male person
- **kyu** /kju/ *n.* 'tongue' — PL: kyumi; GEN: kyun
- **kyum** /kjum/ *adj.* 'soft'
- **kyunykwel** /ˈkjuɲkwel/ *n.* 'source'
- **kyuri·i** /ˈkjurii/ *v.* 'fall ill'
- **kyurzra** /ˈkjurzra/ *n.* 'cock'
- **kyuxi** /ˈkjuʃi/ *n.* 'cassava'
- **la** /la/ *adj.* 'sharp'
- **laa** /laː/ *n.* 'sock'
- **laawii** /ˈlaːwiː/ *part.* 'breathe, breath'
- **laguu** /ˈlaɡuː/ *n.* 'gap'
- **laki** /ˈlaki/ *n.* 'barley'
- **lal** /lal/ *part.* 'tomorrow'
- **lalkia** /ˈlalkia/ *n.* 'crop, harvest'
- **lalomxii** /laˈlomʃiː/ *n.* 'centipede'
- **lan** /lan/ *adj.* 'mute'
- **lapyiq** /ˈlapjiŋ/ *n.* 'mouth' — PL: lapyiqmi; GEN: lapyin
- **larti** /ˈlarti/ *n.* 'June'
- **latany** /ˈlataɲ/ *n.* 'onion'
- **lawaq** /ˈlawaŋ/ *adj.* 'rough'
- **lawe** /ˈlawe/ [ˈlawi] *v.* 'to make sharp' ← *la*
- **la·al** /ˈlaal/ *n.* 'sharpness' ← *la*
- **le** /le/ [li] *n.* 'root' — PL: lemi; GEN: len
- **lei** /ˈlei/ *n.* 'pestle'
- **leq** /leŋ/ *n.* 'pasture'
- **leqlemgin** /leŋˈlemɡin/ *v.* 'forbid'
- **leso** /ˈleso/ *adj.* 'full of root' ← *le*
- **lewa** /ˈlewa/ *adj.* 'small'
- **lewa·al** /ˈlewaal/ *n.* 'small thing' ← *lewa*
- **lexriq** /ˈleʃriŋ/ *n.* 'sausage'
- **lhwoge** /ˈɬwoɡe/ *adv.* 'instantly'
- **li** /li/ *dem.* 'that'
- **lii** /liː/ *n.* 'bat'
- **liidyoo** /ˈliːdjoo/ *v.* 'conceive'
- **liinokye** /ˈliːnokje/ *adj.* 'light (color)'
- **linraa** /ˈlinraː/ *v.* 'happen'
- **lin·yamhom** /linˈjamhom/ *n.* 'peg'
- **liqalkrom** /liˈŋalkrom/ *n.* 'pig'
- **lisu** /ˈlisu/ *n.* 'August'
- **lita** /ˈlita/ *v.* 'rescue'
- **li·iila** /ˈliiːla/ *adj.* 'surprised'
- **lĩnmu** /ˈlĩnmu/ *part.* 'outside'
- **lĩr** /lĩr/ *n.* 'wheel'
- **lo** /lo/ *v.t.* 'to drink' — PST: lopu
- **lokyu·uul** /ˈlokjuuːl/ *n.* 'child-in-law'
- **lol** /lol/ *n.* 'season'
- **lomkru** /ˈlomkru/ *adj.* 'green'
- **lomkyoq** /ˈlomkjoŋ/ *n.* 'omen'
- **lomo** /ˈlomo/ *n.* 'liver' — PL: lomomi; GEN: lomon
- **lona** /ˈlona/ *n.* 'vein'
- **loqi** /ˈloŋi/ *adj.* 'tending to drink' ← *lo*
- **lu** /lu/ *n.* 'blood vessel'
- **luglun** /ˈluɡlun/ *n.* 'crowd'
- **lulim** /ˈlulim/ *v.i.* 'sleep' — PST: lulimpu
- **lulimgo** /luˈlimɡo/ *n.* 'act of sleeping' ← *lulim*
- **lulimgwaaqum** /luˈlimɡwaːŋum/ *n.* 'bed' = *lulim* + *gwaaqum*
- **lulimqi** /luˈlimŋi/ *adj.* 'sleepy' ← *lulim*
- **luniwa** /ˈluniwa/ *v.* 'begin, beginning'
- **lun·yuu** /ˈlunjuː/ *n.* 'arm'
- **lupi** /ˈlupi/ *n.* 'tent'
- **lupo** /ˈlupo/ *n.* 'steam'
- **lupyim** /ˈlupjim/ *adj.* 'smooth'
- **luqhe** /ˈluŋhe/ *n.* 'fermented drink'
- **luqmi** /ˈluŋmi/ *n.* 'roof'
- **lutri** /ˈlutri/ *n.* 'man'
- **lutyu** /ˈlutju/ *n.* 'paper'
- **luuar** /ˈluːar/ *n.* 'paddle'
- **luuti** /ˈluːti/ *v.* 'visible'
- **luwo** /ˈluwo/ *v.* 'sharpen'
- **luxyu** /ˈluʃju/ *adj.* 'long'
- **luxyual** /ˈluʃjual/ *n.* 'length' ← *luxyu*
- **luxyudhi** /ˈluʃjuði/ *v.* 'to become long' ← *luxyu*
- **luyuplen** /ˈlujuplen/ *n.* 'initiation ceremony'
- **ma** /ma/ *adj.* 'short'
- **maakikil** /ˈmaːkikil/ *n.* 'seagull'
- **maam** /maːm/ *v.bitr.* 'to give' — PST: maampu
- **maamkrai** /ˈmaːmkrai/ *v.* 'give back' = *maam* + *krai*
- **maamu** /ˈmaːmu/ *n.* 'tapir'
- **maaqsyu** /ˈmaːŋsju/ *n.* 'ditch'
- **mageq** /ˈmaɡeŋ/ *n.* 'oven'
- **magwi** /ˈmaɡwi/ *n.* 'fin'
- **makwanwa** /maˈkwanwa/ *n.* 'hat'
- **makyemuq** /ˈmakjemuŋ/ *adj.* 'damp'
- **mam** /mam/ *n.* 'neck' — PL: mammi; GEN: man
- **mamki** /ˈmamki/ *v.* 'suspect'
- **mamqunyany** /ˈmamŋuɲaɲ/ *n.* 'firewood'
- **manil** /ˈmanil/ *v.* 'draw water'
- **many** /maɲ/ *n.* 'store'
- **mapye** /ˈmapje/ *n.* 'stingray'
- **maq** /maŋ/ *n.* 'soil' — PL: maqmi; GEN: man
- **maqge** /ˈmaŋɡe/ *v.* 'appear'
- **maqtwi** /ˈmaŋtwi/ *v.* 'braid (verb) or weave (basket)'
- **matwaa** /ˈmatwaː/ *n.* 'navel' — PL: matwaami; GEN: matwaan
- **matwibri** /ˈmatwibri/ *n.* 'length'
- **ma·aa** /ˈmaaː/ *v.i.* 'to sing' — PST: ma·aapu
- **ma·aago** /ˈmaaːɡo/ [ˈmaaːɣo] *n.* 'song' ← *ma·aa*
- **ma·aakwunytwu** /ˌmaaːˈkwuɲtwu/ *n.* 'singer' ← *ma·aa*
- **ma·aanii** /ˈmaaːniː/ *n.* 'what is sung' ← *ma·aa*
- **ma·aaqi** /ˈmaaːŋi/ *adj.* 'tending to sing' ← *ma·aa*
- **me** /me/ *v.* 'bake'
- **medwaq** /ˈmedwaŋ/ *n.* 'custom'
- **mee** /ˈmee/ *n.* 'noble'
- **megle** /ˈmeɡle/ *n.* 'walk'
- **megyuki** /ˈmeɡjuki/ *n.* 'axle'
- **meherbyi** /meˈherbji/ *v.* 'carry on shoulder'
- **mekuu** /ˈmekuː/ [ˈmeɣuː] *n.* 'cloud' — PL: mekuumi; GEN: mekuun
- **mekwe** /ˈmekwe/ *v.* 'convey'
- **mekyi** /ˈmekji/ *v.* 'shine'
- **mela** /ˈmela/ *n.* 'insect'
- **mem** /mem/ *n.* 'bottom'
- **memhaa** /ˈmemhaː/ *v.* 'herd'
- **mempyum** /ˈmempjum/ *n.* 'horn' — PL: mempyummi; GEN: mempyun
- **men** /men/ *n.* 'heel'
- **meqnu** /ˈmeŋnu/ *adj.* 'warm'
- **meqpi** /ˈmeŋpi/ *part.* 'today'
- **mer** /mer/ *n.* 'girl'
- **mesiki** /ˈmesiki/ *v.* 'prepare'
- **meuyi** /ˈmeuji/ *n.* 'mouse'
- **meyu** /ˈmeju/ *part.* 'we (inclusive)'
- **mi** /mi/ *n.* 'medicine'
- **miakyu** /ˈmiakju/ *v.* 'change (become different)'
- **miblupyi** /ˈmiblupji/ *n.* 'fever'
- **miduq** /ˈmiduŋ/ *n.* 'embers'
- **midyiny** /ˈmidjiɲ/ *v.* 'raise'
- **migwuu** /ˈmiɡwuː/ *v.* 'chop'
- **mii** /miː/ *v.* 'bend'
- **miin** /miːn/ *n.* 'pair'
- **miiqyiwiim** /ˈmiːŋjiwiːm/ *v.* 'surrender'
- **miiu** /ˈmiːu/ *n.* 'rye'
- **mikranhi** /miˈkranhi/ *v.* 'spoil'
- **mikwalnu** /miˈkwalnu/ *adv.* 'hardly'
- **mikwamkyii** /miˈkwamkjiː/ *n.* 'porpoise'
- **milmĩ** /ˈmilmĩ/ *n.* 'clock'
- **milxyugu** /ˈmilʃjuɡu/ *v.* 'understand'
- **mimi** /ˈmimi/ *v.* 'put'
- **miminy** /ˈmimiɲ/ *n.* 'livestock'
- **mimkyu** /ˈmimkju/ *n.* 'wood' — PL: mimkyumi; GEN: mimkyun = mesma palavra que tree
- **mimkyu** /ˈmimkju/ *n.* 'tree' — PL: mimkyumi; GEN: mimkyun
- **mimkyuso** /ˈmimkjuso/ *adj.* 'wooded' ← *mimkyu*
- **min** /min/ *n.* 'felt'
- **minbu** /ˈminbu/ *n.* 'meal'
- **minkyam** /ˈminkjam/ *n.* 'cow'
- **minyai** /ˈmiɲai/ *v.* 'pound'
- **minybyĩlnu** /miɲˈbjĩlnu/ *v.* 'curse'
- **minysyunyiq** /ˈmiɲsjuɲiŋ/ *part.* 'because of'
- **minyuu** /ˈmiɲuː/ *n.* 'heron'
- **mipol** /ˈmipol/ *n.* 'reindeer'
- **miqme** /ˈmiŋme/ *n.* 'chest'
- **mirzrom** /ˈmirzrom/ *n.* 'aunt'
- **mium** /ˈmium/ *n.* 'vulture'
- **miunbi** /miˈunbi/ *v.* 'yawn'
- **mĩlka** /ˈmĩlka/ *n.* 'bait'
- **mĩyago** /ˈmĩjaɡo/ *n.* 'heaven'
- **mo** /mo/ *v.* 'scold'
- **mobya·a** /ˈmobjaa/ *v.* 'visit'
- **mokweny** /ˈmokweɲ/ *n.* 'elk'
- **mon** /mon/ *v.* 'try'
- **mou** /ˈmou/ *n.* 'raccoon'
- **mu** /mu/ *n.* 'lizard'
- **mube** /ˈmube/ *n.* 'pattern'
- **mugomu** /ˈmuɡomu/ *n.* 'linen, flax'
- **mukii** /ˈmukiː/ *n.* 'shovel'
- **mukunpu** /muˈkunpu/ *n.* 'word'
- **mukwa** /ˈmukwa/ *n.* 'lamb'
- **mul** /mul/ *n.* 'law'
- **mulkluqi** /ˈmulkluŋi/ *v.* 'adjudicate'
- **mulkyu** /ˈmulkju/ *n.* 'pin'
- **mulpo** /ˈmulpo/ *v.* 'decay'
- **mum** /mum/ *n.* 'freshwater eel'
- **mumbi** /ˈmumbi/ *n.* 'memory'
- **mumkweni** /ˈmumkweni/ *part.* 'always'
- **mumti** /ˈmumti/ *n.* 'guts' — PL: mumtimi; GEN: mumtin
- **mumxe** /ˈmumʃe/ *n.* 'east'
- **mumyu** /ˈmumju/ *v.i.* 'to breathe' — PST: mumyupu
- **mumyugo** /ˈmumjuɡo/ [ˈmumjuɣo] *n.* 'act of breathing' ← *mumyu*
- **mun** /mun/ *n.* 'brass instrument (horn or trumpet)'
- **munkwitro** /ˈmunkwitro/ *part.* 'never'
- **muntyu** /ˈmuntju/ *n.* 'muroid (mouse or rat)'
- **munywal** /ˈmuɲwal/ *n.* 'fishing line'
- **mupyun** /ˈmupjun/ *n.* 'country'
- **murumgam** /muˈrumɡam/ *n.* 'dirt'
- **musugi** /ˈmusuɡi/ *n.* 'beak'
- **muugiie** /ˈmuːɡiːe/ *v.* 'hiccough'
- **muulnam** /ˈmuːlnam/ *v.* 'pinch'
- **muumi** /ˈmuːmi/ *n.* 'net'
- **muunysaakla** /ˈmuːɲsaːkla/ *part.* 'how many?'
- **muunyuu** /ˈmuːɲuː/ *n.* 'pus'
- **muuqkiwu** /ˈmuːŋkiwu/ *v.* 'be thirsty'
- **mu·umnaaq** /muˈumnaːŋ/ *n.* 'west'
- **na** /na/ *n.* 'rope' — PL: nami; GEN: nan
- **naa** /naː/ *v.* 'cover'
- **naam** /naːm/ *v.* 'ache'
- **naampyintwiiq** /naːmˈpjintwiːŋ/ *n.* 'bad luck'
- **naaq** /naːŋ/ *n.* 'corpse'
- **naayo** /ˈnaːjo/ *n.* 'grain'
- **nadye** /ˈnadje/ *n.* 'pouch'
- **nainma** /naˈinma/ *v.* 'liberate'
- **nam** /nam/ *n.* 'sheep'
- **nampem** /ˈnampem/ *v.* 'take a walk'
- **namtyi** /ˈnamtji/ *v.* 'rise'
- **nan** /nan/ *adj.* 'high'
- **nanile** /ˈnanile/ *n.* 'high tide' = *nan* + *ile*
- **nantaan** /ˈnantaːn/ *n.* 'bucket'
- **napim** /ˈnapim/ *n.* 'molar tooth'
- **naqnaakra** /ˈnaŋnaːkra/ *n.* 'table'
- **nar** /nar/ *n.* 'shoe'
- **narkwunytwu** /narˈkwuɲtwu/ *n.* 'shoemaker' = *nar* + *kwunytwu*
- **nasaa** /ˈnasaː/ *v.* 'pursue'
- **natedwi** /ˈnatedwi/ *n.* 'spine'
- **naumqo** /naˈumŋo/ *n.* 'soap'
- **ne** /ne/ [ni] *conj.* 'and'
- **nea** /ˈnea/ *n.* 'spider'
- **nelii** /ˈneliː/ *n.* 'spring or well'
- **nenyi** /ˈneɲi/ *v.* 'beget'
- **nertyaakhu** /ˈnertjaːkʰu/ *n.* 'rake'
- **nesu** /ˈnesu/ *n.* 'wrist'
- **nesye** /ˈnesje/ *v.* 'extinguish'
- **neuti** /ˈneuti/ *adj.* 'diligent'
- **ni** /ni/ *n.* 'ornament'
- **niiiiyi** /ˈniːiːji/ *n.* 'buffalo'
- **niim** /niːm/ *n.* 'savanna'
- **niirumnyan** /niːˈrumɲan/ *v.* 'choke'
- **niiu** /ˈniːu/ *adj.* 'merry'
- **nikwuq** /ˈnikwuŋ/ *n.* 'battle'
- **nikyel** /ˈnikjel/ *n.* 'court'
- **nila** /ˈnila/ *v.* 'clean (something)'
- **nimpĩam** /ˈnimpĩam/ *n.* 'eagle'
- **nin** /nin/ *v.* 'plant (something)'
- **ninkwunytwu** /ninˈkwuɲtwu/ *n.* 'farmer' ← *nin* (agentivo)
- **ninybyonpi** /niɲˈbjonpi/ *adj.* 'tall'
- **ninywusam** /ˈniɲwusam/ *adj.* 'difficult'
- **nipyiaa** /ˈnipjiaː/ *n.* 'shelf'
- **niqtonuu** /ˈniŋtonuː/ *adv.* 'then'
- **nirol** /ˈnirol/ *v.i.* 'to fall' — PST: nirolpu
- **nirzwem** /ˈnirzwem/ *v.* 'blow'
- **no** /no/ *n.* 'elbow'
- **noklanyu** /ˈnoklaɲu/ *adv.* 'still'
- **nolpyaaa** /ˈnolpjaːa/ *n.* 'plaintiff'
- **nom** /nom/ *quant.* 'other'
- **nomkloq** /ˈnomkloŋ/ *n.* 'swamp'
- **notyĩny** /ˈnotjĩɲ/ *n.* 'pit'
- **nu** /nu/ *n.* 'mother' — PL: numi; GEN: nun
- **nua** /ˈnua/ *n.* 'family'
- **nubri** /ˈnubri/ *n.* 'foam'
- **nuedyĩ** /ˈnuedjĩ/ *n.* 'mother's brother' = *nu* + *edyĩ*
- **nukhin** /ˈnukʰin/ *n.* 'sledge'
- **nullha** /ˈnulɬa/ *n.* 'drop (of a liquid)'
- **num** /num/ *n.* 'spirit'
- **numcyagyi** /ˈnumθjaɡji/ *n.* 'cheese'
- **nun** /nun/ *n.* 'place'
- **nunaa** /ˈnunaː/ *v.* 'choose'
- **nunmii** /ˈnunmiː/ *n.* 'coal'
- **nupinyqen** /nuˈpiɲŋen/ *v.* 'pile up'
- **nuplupi** /ˈnuplupi/ *n.* 'lion'
- **nupu** /ˈnupu/ *n.* 'mother's sister' = *nu* + *pu*
- **nuqkyi** /ˈnuŋkji/ *v.* 'have'
- **nutamdwe** /nuˈtamdwe/ *v.* 'row'
- **nutur** /ˈnutur/ *n.* 'blanket'
- **nuu** /nuː/ *adj.* 'sweet'
- **nuual** /ˈnuːal/ *n.* 'sweetness' ← *nuu*
- **nuugiimta** /nuːˈɡiːmta/ *n.* 'sweet potato' = *nuu* + *giimta*
- **nuulminza** /nuːlˈminza/ *adj.* 'delicious'
- **nuuqnyomu** /ˈnuːŋɲomu/ *n.* 'forked branch'
- **nuuutu** /ˈnuːutu/ *v.* 'mix'
- **nyaamipan** /ˈɲaːmipan/ *n.* 'storm'
- **nyaanyqiiken** /ˈɲaːɲŋiːken/ *n.* 'footprint'
- **nyal** /ɲal/ *v.* 'read'
- **nyanybyin** /ˈɲaɲbjin/ *num.* 'thousand'
- **nyeki** /ˈɲeki/ *v.* 'lend'
- **nyeniin** /ˈɲeniːn/ *n.* 'bag'
- **nyigyi** /ˈɲiɡji/ *v.* 'ask (request)'
- **nyilmun** /ˈɲilmun/ *n.* 'father-in-law (of woman)'
- **nyim** /ɲim/ *v.* 'shout'
- **nyimso** /ˈɲimso/ *adj.* 'drowned'
- **nyimuu** /ˈɲimuː/ *v.* 'sting'
- **nyinyĩii** /ˈɲiɲĩiː/ *v.* 'let'
- **nyinyĩiisenka** /ɲiˌɲĩiːˈsenka/ *v.* 'let go' = *nyinyĩii* + *senka*
- **nyiq** /ɲiŋ/ *v.* 'shut'
- **nyo** /ɲo/ *n.* 'cause'
- **nyoglin** /ˈɲoɡlin/ *v.* 'work (activity)'
- **nyolma** /ˈɲolma/ *adj.* 'narrow'
- **nyolquny** /ˈɲolŋuɲ/ *v.* 'hire or rent'
- **nyotuul** /ˈɲotuːl/ *n.* 'army'
- **nyukirtwaal** /ɲuˈkirtwaːl/ *n.* 'hawk'
- **nyulwu** /ˈɲulwu/ *n.* 'strap'
- **nyumor** /ˈɲumor/ *n.* 'skin' — PL: nyumormi; GEN: nyumon
- **nyunkrin** /ˈɲunkrin/ *n.* 'idea'
- **nyunuu** /ˈɲunuː/ *n.* 'meat'
- **nyuqany** /ˈɲuŋaɲ/ *n.* 'basket'
- **nyutrulta** /ɲuˈtrulta/ *n.* 'arson'
- **nyuu** /ɲuː/ *v.* 'look'
- **nyuyaabo** /ˈɲujaːbo/ *n.* 'ribbon'
- **o** /o/ *n.* 'fly' — PL: omi; GEN: on
- **odremse** /oˈdremse/ *n.* 'cloak'
- **ogrudhwe** /ˈoɡruðwe/ *n.* 'meadow'
- **ogu** /ˈoɡu/ *adj.* 'bald'
- **oka** /ˈoka/ *v.* 'wait'
- **okham** /ˈokʰam/ *v.* 'learn'
- **oki** /ˈoki/ *n.* 'adobe'
- **okio** /ˈokio/ *adj.* 'faithful'
- **okudi** /ˈokudi/ *n.* 'height'
- **ol** /ol/ *v.* 'touch'
- **om** /om/ *conj.* 'if'
- **omdu** /ˈomdu/ *v.* 'wrap'
- **omdyimi** /ˈomdjimi/ *n.* 'padlock'
- **onkyu** /ˈonkju/ *n.* 'weight'
- **onsri** /ˈonsri/ *n.* 'foot' — PL: onsrimi; GEN: onsrin
- **onybĩny** /ˈoɲbĩɲ/ *v.* 'sway'
- **on·yuxya** /ˈonjuʃja/ *n.* 'scissors'
- **opa** /ˈopa/ *part.* 'more'
- **opar** /ˈopar/ *n.* 'dish'
- **opimaa** /ˈopimaː/ *part.* 'ninety'
- **opya** /ˈopja/ *n.* 'stomach'
- **oqgyem** /ˈoŋɡjem/ *n.* 'mast'
- **orkliny** /ˈorkliɲ/ *n.* 'soup'
- **orwal** /ˈorwal/ *adj.* 'expensive'
- **osei** /ˈosei/ *adj.* 'hot'
- **osinpyoq** /oˈsinpjoŋ/ *v.* 'knead'
- **owiiyaquu** /oˈwiːjaŋuː/ *n.* 'ant' — PL: owiiyaquumi; GEN: owiiyaquun
- **owiiyaquuso** /ˌowiːˈjaŋuːso/ *adj.* 'full of ant' ← *owiiyaquu*
- **oxral** /ˈoʃral/ *adj.* 'brave'
- **oyomke** /oˈjomke/ *v.* 'listen'
- **ozwo** /ˈozwo/ *v.* 'approach'
- **pa** /pa/ *v.t.* 'to suck' — PST: papu
- **paa** /paː/ *v.* 'embrace'
- **paaaatwi** /ˈpaːaːtwi/ *n.* 'adze'
- **paaldyĩmxa** /paːlˈdjĩmʃa/ *n.* 'land'
- **paam** /paːm/ *n.* 'nit'
- **paanyam** /ˈpaːɲam/ *n.* 'middle, center'
- **paauupu** /ˈpaːuːpu/ *n.* 'birch'
- **paaxusrĩ** /ˈpaːʃusrĩ/ *v.* 'smell'
- **pai** /ˈpai/ *n.* 'crane'
- **paĩ** /ˈpaĩ/ *n.* 'horse'
- **palku** /ˈpalku/ *n.* 'eyelid'
- **palqi** /ˈpalŋi/ *n.* 'stone/rock' — PL: palqimi; GEN: palqin
- **papyam** /ˈpapjam/ *v.t.* 'to do/make' — PST: papyampu
- **papyaminii** /paˈpjaminiː/ *n.* 'deed' ← *papyam*
- **paqon** /ˈpaŋon/ *v.* 'like'
- **pasral** /ˈpasral/ *n.* 'walking stick'
- **patraamna** /paˈtraːmna/ *n.* 'son-in-law (of woman)'
- **payu** /ˈpaju/ *n.* 'leaf' — PL: payumi; GEN: payun
- **pe** /pe/ *n.* 'cockroach'
- **peiyo** /ˈpeijo/ *n.* 'vulva'
- **peq** /peŋ/ *v.* 'bathe'
- **peqbyoga** /ˈpeŋbjoɡa/ *n.* 'earwax'
- **per** /per/ *n.* 'corner'
- **perkwuu** /ˈperkwuː/ *n.* 'path'
- **peryo** /ˈperjo/ *v.i.* 'to live' — PST: peryopu
- **peryogo** /ˈperjoɡo/ [ˈperjoɣo] *n.* 'result of living' ← *peryo*
- **peryoqi** /ˈperjoŋi/ *adj.* 'tending to live' ← *peryo*
- **pesrebyi** /ˈpesrebji/ *n.* 'servant'
- **peyo** /ˈpejo/ *v.* 'stutter'
- **pha** /pʰa/ *n.* 'nail (tool)'
- **phanywuluu** /ˈpʰaɲwuluː/ *n.* 'copper, bronze'
- **phasaasi** /ˈpʰasaːsi/ *n.* 'tattoo'
- **phi** /pʰi/ *n.* 'coyote'
- **phiiiildwir** /pʰiːˈiːldwir/ *adj.* 'blue'
- **pho** /pʰo/ *n.* 'May'
- **phu** /pʰu/ *v.t.* 'to fear' — PST: phupu
- **pi** /pi/ *n.* 'year' — PL: pimi; GEN: pin
- **pigre** /ˈpiɡre/ *v.* 'press'
- **pii** /piː/ *n.* 'kettle'
- **piimbuum** /ˈpiːmbuːm/ *part.* 'down, below'
- **piita** /ˈpiːta/ *n.* 'rug'
- **pil** /pil/ *v.* 'weigh'
- **pimdwadii** /ˈpimdwadiː/ *n.* 'pepper'
- **pin** /pin/ *v.* 'be'
- **pinprigu** /ˈpinpriɡu/ *v.* 'be late' = *pin* + *prigu*
- **pinyi** /ˈpiɲi/ *n.* 'neighbour'
- **piqsyel** /ˈpiŋsjel/ *n.* 'nut'
- **pita** /ˈpita/ [ˈpiða] *n.* 'snow' — PL: pitami; GEN: pitan
- **piu** /ˈpiu/ *n.* 'air'
- **piuu** /ˈpiuː/ *part.* 'in'
- **piyuxu** /ˈpijuʃu/ *adj.* 'sick'
- **pĩrsyo** /ˈpĩrsjo/ *v.* 'dive'
- **plaare** /ˈplaːre/ [ˈplaːri] *adj.* 'bad'
- **plaaredhi** /ˈplaːreði/ *v.* 'to become bad' ← *plaare*
- **plaĩ** /ˈplaĩ/ *n.* 'buttocks'
- **plakriilmal** /plaˈkriːlmal/ *n.* 'mortar'
- **pla·al** /ˈplaal/ *adj.* 'unripe'
- **ple** /ple/ *v.* 'rest'
- **pli** /pli/ *v.* 'put on'
- **plibuun** /ˈplibuːn/ *n.* 'father-in-law (of man)'
- **plika** /ˈplika/ *n.* 'count'
- **plikim** /ˈplikim/ *n.* 'swarm'
- **pliku** /ˈpliku/ [ˈpliɣu] *v.t.* 'to kill' — PST: plikupu
- **plikugo** /ˈplikuɡo/ *n.* 'murder' ← *pliku* (ação)
- **plu** /plu/ *n.* 'adultery'
- **pluaa** /ˈpluaː/ *n.* 'shoulder'
- **plugyeaan** /ˈpluɡjeaːn/ *v.* 'think (reflect)'
- **plum** /plum/ *n.* 'handkerchief'
- **plun** /plun/ *v.* 'spin'
- **plunyyenke** /pluɲˈjenke/ *n.* 'character'
- **pluqiyal** /ˈpluŋijal/ *n.* 'anxiety'
- **po** /po/ *n.* 'ram'
- **pogwĩm** /ˈpoɡwĩm/ *n.* 'meeting house'
- **poklon** /ˈpoklon/ *n.* 'palm tree'
- **pomgwa** /ˈpomɡwa/ *adj.* 'quiet'
- **pomkur** /ˈpomkur/ *n.* 'lung'
- **ponsoqnyi** /ponˈsoŋɲi/ *adj.* 'proud'
- **popii** /ˈpopiː/ *v.* 'watch'
- **poqtu** /ˈpoŋtu/ *v.* 'move'
- **pra** /pra/ *v.* 'follow'
- **pranokuu** /ˈpranokuː/ *n.* 'copper'
- **pri** /pri/ *n.* 'fan (object)'
- **prigu** /ˈpriɡu/ *part.* 'late'
- **prike** /ˈprike/ *adj.* 'full'
- **prino** /ˈprino/ *n.* 'collarbone'
- **prisuq** /ˈprisuŋ/ *part.* 'under'
- **pri·i** /ˈprii/ *v.* 'find'
- **prolklĩ** /ˈprolklĩ/ *v.t.* 'to cut' — PST: prolklĩpu
- **prolklĩgilingwe** /prolˌklĩɡiˈlinɡwe/ *n.* 'knife' = *prolklĩ* + *gilingwe*
- **prolklĩnii** /ˈprolklĩniː/ *n.* 'wound' ← *prolklĩ*
- **prolklĩuum** /ˈprolklĩuːm/ *v.* 'cut down' = *prolklĩ* + *uum*
- **pronkwu** /ˈpronkwu/ *v.* 'blink'
- **prowuu** /ˈprowuː/ *n.* 'sculptor'
- **pru** /pru/ *conj.* 'because'
- **prugril** /ˈpruɡril/ *adj.* 'wrinkled'
- **prusa** /ˈprusa/ *n.* 'item'
- **pruxya** /ˈpruʃja/ *v.* 'believe'
- **pru·u** /ˈpruu/ *n.* 'south'
- **pu** /pu/ *n.* 'sister'
- **puaq** /ˈpuaŋ/ *v.* 'carry under the arm'
- **pudyal** /ˈpudjal/ *v.* 'betray'
- **puglou** /ˈpuɡlou/ *v.* 'brawl'
- **puki** /ˈpuki/ *n.* 'fireplace'
- **pukipluu** /ˈpukipluː/ *adv.* 'very'
- **pulgri** /ˈpulɡri/ *n.* 'game'
- **punal** /ˈpunal/ *n.* 'limb'
- **puonme** /puˈonme/ *n.* 'rainbow'
- **pupaa** /ˈpupaː/ *n.* 'morning'
- **pupaawilsi** /ˌpupaːˈwilsi/ *n.* 'breakfast' = *pupaa* + *wilsi*
- **pupru** /ˈpupru/ *adj.* 'dry'
- **puprudhi** /ˈpupruði/ *v.* 'to dry up' ← *pupru*
- **puq** /puŋ/ *v.* 'feed'
- **pusyaze** /ˈpusjaze/ *n.* 'hay'
- **puuka** /ˈpuːka/ *n.* 'power'
- **puum** /puːm/ *n.* 'silver'
- **puumplano** /ˈpuːmplano/ *v.* 'succeed'
- **puun** /puːn/ *n.* 'fog' — PL: puunmi; GEN: puun
- **puuzrumse** /puːˈzrumse/ *v.* 'tear (shred)'
- **puwan** /ˈpuwan/ *v.* 'painting'
- **puxyegeny** /ˈpuʃjeɡeɲ/ *n.* 'reason'
- **puyu** /ˈpuju/ *n.* 'chicken'
- **pya** /pja/ *n.* 'north'
- **pyam** /pjam/ *n.* 'furrow'
- **pyaqgyu** /ˈpjaŋɡju/ *v.* 'preach'
- **pyawe** /ˈpjawe/ *v.* 'carve'
- **pyawumhaa** /pjaˈwumhaː/ *n.* 'prostitute'
- **pyeyon** /ˈpjejon/ *n.* 'home'
- **pyi** /pji/ *adv.* 'here'
- **pyim** /pjim/ *n.* 'god'
- **pyimii** /ˈpjimiː/ *adj.* 'ready'
- **pyiyaaq** /ˈpjijaːŋ/ *n.* 'whirlpool'
- **pyi·iso** /ˈpjiiso/ *v.* 'drown'
- **pyĩme** /ˈpjĩme/ *n.* 'chill'
- **pyĩmnikwii** /ˈpjĩmnikwiː/ *v.* 'endure'
- **pyo** /pjo/ *n.* 'piece'
- **pyoe** /ˈpjoe/ *n.* 'frost'
- **pyol** /pjol/ *n.* 'needle (for sewing)'
- **pyoltu** /ˈpjoltu/ *v.* 'drive (cattle)'
- **pyulo** /ˈpjulo/ *n.* 'waterfall'
- **pyum** /pjum/ *v.* 'sell'
- **pyuweqkiq** /pjuˈweŋkiŋ/ *n.* 'lip'
- **pyu·u** /ˈpjuu/ *adj.* 'fragrant'
- **qa** /ŋa/ *n.* 'snake' — PL: qami; GEN: qan
- **qaa** /ŋaː/ *v.t.* 'to tie' — PST: qaapu
- **qaaku** /ˈŋaːku/ *v.* 'trap (catch)'
- **qaakyebiyi** /ŋaːˈkjebiji/ *v.* 'tie up' = *qaa* + *kyebiyi*
- **qaamdol** /ˈŋaːmdol/ *v.* 'sniff'
- **qaamni** /ˈŋaːmni/ *n.* 'soul'
- **qaanii** /ˈŋaːniː/ *n.* 'knot' ← *qaa*
- **qaku·ur** /ˈŋakuur/ *n.* 'silk'
- **qamkweqkluu** /ŋamˈkweŋkluː/ *n.* 'coast'
- **qamosaa** /ˈŋamosaː/ *n.* 'January'
- **qamzayu** /ˈŋamzaju/ *n.* 'statue'
- **qanin** /ˈŋanin/ *n.* 'shore'
- **qaqkii** /ˈŋaŋkiː/ *n.* 'itch'
- **qaxya** /ˈŋaʃja/ *n.* 'boundary'
- **qe** /ŋe/ *v.* 'scrape'
- **qelepyin** /ˈŋelepjin/ *n.* 'knife (for eating)'
- **qem** /ŋem/ *v.* 'lick'
- **qen** /ŋen/ *v.t.* 'to stab' — PST: qenpu
- **qesyar** /ˈŋesjar/ *v.* 'build'
- **qeyur** /ˈŋejur/ *n.* 'chain'
- **qi** /ŋi/ *n.* 'boomerang'
- **qidyii** /ˈŋidjiː/ *n.* 'load'
- **qiil** /ŋiːl/ *v.* 'separate'
- **qiiwany** /ˈŋiːwaɲ/ *v.* 'thaw'
- **qiklaan** /ˈŋiklaːn/ *n.* 'wheat'
- **qil** /ŋil/ *adv.* 'fast'
- **qilyum** /ˈŋiljum/ *n.* 'shame'
- **qinpul** /ˈŋinpul/ *v.* 'trade'
- **qiputrim** /ˈŋiputrim/ *v.* 'rule'
- **qiq** /ŋiŋ/ *n.* 'armpit'
- **qiqnu** /ˈŋiŋnu/ *n.* 'nettle'
- **qityirii** /ˈŋitjiriː/ *n.* 'debt'
- **qiwe** /ˈŋiwe/ *part.* 'sometimes'
- **qĩla** /ˈŋĩla/ *n.* 'latch'
- **qĩqplimdiiq** /ŋĩŋˈplimdiːŋ/ *adv.* 'together'
- **qo** /ŋo/ *num.* 'four'
- **qonypuko** /ˈŋoɲpuko/ *n.* 'grief'
- **qotyal** /ˈŋotjal/ *v.i.* 'to lie' — PST: qotyalpu
- **qotyaluum** /ˈŋotjaluːm/ *v.* 'lie down' = *qotyal* + *uum*
- **qu** /ŋu/ *num.* 'seven'
- **qubi** /ˈŋubi/ *v.* 'stream'
- **qumkyĩ** /ˈŋumkjĩ/ *n.* 'rain' — PL: qumkyĩmi; GEN: qumkyĩn
- **quq** /ŋuŋ/ *n.* 'nest'
- **quu** /ŋuː/ *n.* 'snail'
- **raa** /raː/ *n.* 'hip'
- **raam** /raːm/ *n.* 'plait'
- **rabia** /ˈrabia/ *n.* 'fingernail'
- **rahutuu** /ˈrahutuː/ *n.* 'wool'
- **rakiil** /ˈrakiːl/ *n.* 'spleen'
- **ralam** /ˈralam/ *n.* 'field'
- **ramdri·i** /ˈramdrii/ *n.* 'hook'
- **rame** /ˈrame/ *v.* 'weave'
- **ranyii** /ˈraɲiː/ *n.* 'rice'
- **rar** /rar/ *adv.* 'in vain'
- **re** /re/ *part.* 'often'
- **regyotuny** /ˈreɡjotuɲ/ *adv.* 'so'
- **rekoyar** /ˈrekojar/ *n.* 'mat'
- **ri** /ri/ *n.* 'honey'
- **riinu** /ˈriːnu/ *n.* 'envy'
- **rikunya** /ˈrikuɲa/ *adj.* 'delicate, fine'
- **rimkum** /ˈrimkum/ *v.* 'fry'
- **rirgwu** /ˈrirɡwu/ *v.* 'pour'
- **risan** /ˈrisan/ *v.* 'give'
- **risi** /ˈrisi/ *n.* 'handle'
- **risyaqxu** /riˈsjaŋʃu/ *n.* 'defeat'
- **ritron** /ˈritron/ *n.* 'son'
- **ri·i** /ˈrii/ *adj.* 'fat (obese)'
- **ri·izyin** /ˈriizjin/ *n.* 'body'
- **ri·izyinaambram** /riˌizjiˈnaːmbram/ *n.* 'body hair' = *ri·izyin* + *aambram*
- **ri·izyintya** /ˌriiˈzjintja/ *n.* 'body louse' = *ri·izyin* + *tya*
- **rom** /rom/ *v.* 'hurry'
- **roni** /ˈroni/ *adv.* 'everywhere'
- **ror** /ror/ *adv.* 'at that time'
- **ru** /ru/ *quant.* 'few'
- **rubletwu** /ˈrubletwu/ *v.* 'answer'
- **rudyi** /ˈrudji/ *v.* 'keep'
- **rumneni** /ˈrumneni/ *n.* 'chili pepper'
- **ruu** /ruː/ *n.* 'shore of lake'
- **ruulaaq** /ˈruːlaːŋ/ *v.* 'mould'
- **ruuphaa** /ˈruːpʰaː/ *n.* 'duck'
- **sa** /sa/ *pron.* 'they'
- **saa** /saː/ *n.* 'companion'
- **saadyĩ** /ˈsaːdjĩ/ *v.* 'own'
- **saagletrol** /ˈsaːɡletrol/ *v.* 'forget'
- **saali** /ˈsaːli/ *n.* 'fir'
- **saamilo** /ˈsaːmilo/ *n.* 'foal'
- **saan** /saːn/ *n.* 'end (of space)'
- **saaplo** /ˈsaːplo/ *adj.* 'cheap'
- **saka** /ˈsaka/ *part.* 'inside'
- **sal** /sal/ *n.* 'thigh' — PL: salmi; GEN: san
- **sam** /sam/ *n.* 'leg/foot' — PL: sammi; GEN: san
- **saq** /saŋ/ *v.* 'fishing'
- **saru** /ˈsaru/ *n.* 'chin'
- **sasany** /ˈsasaɲ/ *v.t.* 'to bite' — PST: sasanypu
- **sasanyqi** /saˈsaɲŋi/ *adj.* 'tending to bite' ← *sasany*
- **satra** /ˈsatra/ *n.* 'danger'
- **se** /se/ *n.* 'grape'
- **sebyaa** /ˈsebjaː/ *num.* 'five'
- **senka** /ˈsenka/ *v.i.* 'to go' — **PST: senke** (irregular)
- **senkakyebiyi** /ˌsenkaˈkjebiji/ *v.* 'go up' = *senka* + *kyebiyi*
- **senkauum** /ˈsenkauːm/ *v.* 'go down' = *senka* + *uum*
- **ser** /ser/ *n.* 'prawns'
- **seumzwi** /seˈumzwi/ *n.* 'day (24 hours)'
- **sidroq** /ˈsidroŋ/ *n.* 'headband'
- **sigwii** /ˈsiɡwiː/ *n.* 'seed' — PL: sigwiimi; GEN: sigwiin
- **sii** /siː/ *num.* 'ten'
- **siikha** /ˈsiːkʰa/ *v.* 'hide (oneself)'
- **siimra** /ˈsiːmra/ *n.* 'skirt'
- **siinyse** /ˈsiːɲse/ *v.* 'hit'
- **siinysruu** /ˈsiːɲsruː/ *n.* 'coconut'
- **siipaa** /ˈsiːpaː/ *n.* 'snowshoe'
- **sila** /ˈsila/ *n.* 'native country'
- **sili** /ˈsili/ *v.i.* 'to walk' — PST: silipu
- **siliqi** /ˈsiliŋi/ *adj.* 'tending to walk' ← *sili*
- **silsri** /ˈsilsri/ *v.t.* 'to count' — PST: silsripu
- **silsrinii** /ˈsilsriniː/ *n.* 'number' ← *silsri*
- **sim** /sim/ *n.* 'Tuesday'
- **simhim** /ˈsimhim/ *v.* 'groan'
- **siny** /siɲ/ *n.* 'cheek'
- **sĩ** /sĩ/ *n.* 'bill'
- **sĩmtwu** /ˈsĩmtwu/ *adj.* 'female (of person)'
- **sĩranen** /ˈsĩranen/ *n.* 'defendant'
- **so** /so/ *n.* 'forehead'
- **soda** /ˈsoda/ *n.* 'trousers'
- **sokhe** /ˈsokʰe/ *n.* 'chisel'
- **sole** /ˈsole/ *n.* 'moor'
- **som** /som/ *num.* 'six'
- **somxe** /ˈsomʃe/ *n.* 'mason'
- **sonyxĩge** /ˈsoɲʃĩɡe/ [ˈsoɲʃĩɣi] *v.i.* 'to cry/weep' — PST: sonyxĩgepu
- **sonyxĩgego** /soɲˈʃĩɡeɡo/ [soɲˈʃĩɣeɣo] *n.* 'act of crying' ← *sonyxĩge*
- **sonyxĩgeqi** /soɲˈʃĩɡeŋi/ [soɲˈʃĩɣeŋi] *adj.* 'tearful' ← *sonyxĩge*
- **soya** /ˈsoja/ *n.* 'book'
- **sraagio** /ˈsraːɡio/ *adj.* 'calm'
- **sraqkle** /ˈsraŋkle/ *n.* 'plain'
- **srayi** /ˈsraji/ *v.* 'barking'
- **sriiqgo** /ˈsriːŋɡo/ *n.* 'carpenter'
- **sritro** /ˈsritro/ *n.* 'heap'
- **sriuko** /ˈsriuko/ *v.* 'snore'
- **srium** /ˈsrium/ *n.* 'cloth'
- **sroka** /ˈsroka/ *v.* 'fan (action)'
- **sruaam** /ˈsruaːm/ *adj.* 'secret'
- **su** /su/ *part.* 'enough'
- **suenso** /suˈenso/ *v.* 'remember'
- **suiqtyim** /suˈiŋtjim/ *n.* 'oath'
- **suqhu·uu** /ˈsuŋhuuː/ *n.* 'beard'
- **suquumpĩ** /suˈŋuːmpĩ/ *v.* 'burn'
- **surpuminy** /ˈsurpumiɲ/ *v.* 'take off'
- **susawiim** /ˈsusawiːm/ *v.* 'borrow'
- **suuiq** /ˈsuːiŋ/ *n.* 'flute'
- **suutritii** /ˈsuːtritiː/ *n.* 'married man'
- **suuwoq** /ˈsuːwoŋ/ *n.* 'flower' — PL: suuwoqmi; GEN: suuwon
- **syaa** /sjaː/ *n.* 'sow (female pig)'
- **syaii** /ˈsjaiː/ *n.* 'cat'
- **syapregin** /ˈsjapreɡin/ *n.* 'town'
- **syaq** /sjaŋ/ *v.t.* 'know' — PST: syaqpu
- **sye** /sje/ *n.* 'floor'
- **syelcraa** /ˈsjelθraː/ *v.* 'pass'
- **syenpe** /ˈsjenpe/ *part.* 'third'
- **syerklo** /ˈsjerklo/ *n.* 'tick'
- **syeto** /ˈsjeto/ *n.* 'prison'
- **syiebu** /ˈsjiebu/ *v.* 'acquit'
- **syiindu** /ˈsjiːndu/ *adj.* 'dull'
- **syiinduwe** /ˈsjiːnduwe/ [ˈsjiːnduwi] *v.* 'to make dull' ← *syiindu*
- **syikyem** /ˈsjikjem/ *n.* 'bird' — PL: syikyemmi; GEN: syikyen
- **syilqu** /ˈsjilŋu/ *adj.* 'cold'
- **syilqual** /ˈsjilŋual/ *n.* 'coldness' ← *syilqu*
- **syilqudhi** /ˈsjilŋuði/ *v.* 'to cool down' ← *syilqu*
- **syilquwe** /ˈsjilŋuwe/ [ˈsjilŋuwi] *v.* 'to chill' ← *syilqu*
- **syita** /ˈsjita/ *part.* 'zero, nothing'
- **syogĩr** /ˈsjoɡĩr/ *v.* 'roast'
- **syom** /sjom/ *v.t.* 'to hit' — PST: syompu
- **syomgilingwe** /ˌsjomɡiˈlinɡwe/ *n.* 'hammer' = *syom* + *gilingwe*
- **syoq** /sjoŋ/ *n.* 'end (of time)'
- **syuerii** /ˈsjueriː/ *part.* 'next to'
- **syum** /sjum/ *v.* 'carry in hand'
- **syun** /sjun/ *n.* 'dog' — PL: syunmi; GEN: syun
- **syuudwam** /ˈsjuːdwam/ *v.* 'have sex'
- **ta** /ta/ *n.* 'day' — PL: tami; GEN: tan
- **taa** /taː/ *n.* 'brush'
- **taanklo** /ˈtaːnklo/ *n.* 'drink'
- **taargli** /ˈtaːrɡli/ *n.* 'sugar cane'
- **tabam** /ˈtabam/ *n.* 'gums'
- **tablun** /ˈtablun/ *v.* 'disturb'
- **tahi** /ˈtahi/ *v.* 'climb'
- **tal** /tal/ *n.* 'anchor'
- **tale** /ˈtale/ *n.* 'dough'
- **talri** /ˈtalri/ *part.* 'after'
- **talya** /ˈtalja/ *n.* 'grandchild'
- **tam** /tam/ *num.* 'eight'
- **tame** /ˈtame/ *v.* 'swing (movement)'
- **tan** /tan/ *n.* 'sword'
- **taqmu** /ˈtaŋmu/ *n.* 'perch'
- **ta·a** /ˈtaa/ *n.* 'intestines'
- **te** /te/ *adj.* 'round'
- **tel** /tel/ *adj.* 'precious'
- **temsum** /ˈtemsum/ *n.* 'leg' — PL: temsummi; GEN: temsun
- **tene** /ˈtene/ *adv.* 'little'
- **tepyi** /ˈtepji/ *n.* 'altar'
- **teq** /teŋ/ *adj.* 'empty'
- **ti** /ti/ *adj.* 'male (of person)'
- **tihĩm** /ˈtihĩm/ *n.* 'feather' — PL: tihĩmmi; GEN: tihĩn
- **tii** /tiː/ *n.* 'niece'
- **tiim** /tiːm/ *adj.* 'similar'
- **tiityukya** /ˈtiːtjukja/ *n.* 'beggar'
- **tiiugor** /ˈtiːuɡor/ *n.* 'help (assistance)'
- **tilem** /ˈtilem/ *n.* 'whale'
- **tim** /tim/ *n.* 'glove'
- **timkyium** /ˈtimkjium/ *v.* 'permit'
- **timuqsaa** /tiˈmuŋsaː/ *n.* 'lair'
- **tin** /tin/ *n.* 'netbag'
- **tinklaantor** /tinˈklaːntor/ *n.* 'odour'
- **tiny** /tiɲ/ *n.* 'people'
- **tio** /ˈtio/ *part.* 'early'
- **tipiq** /ˈtipiŋ/ *adj.* 'obscure'
- **tipra·a** /ˈtipraa/ *n.* 'ground'
- **tiqaar** /ˈtiŋaːr/ *n.* 'bundle'
- **tisinhaa** /tiˈsinhaː/ *n.* 'priest'
- **titwe** /ˈtitwe/ *v.* 'break (destroy or get destroyed)'
- **tiuul** /ˈtiuːl/ *v.* 'last (endure)'
- **tiwu** /ˈtiwu/ *n.* 'calf'
- **tiyin** /ˈtijin/ *v.t.* 'to squeeze' — PST: tiyinpu
- **ti·im** /ˈtiim/ *n.* 'peel, husk'
- **tĩ** /tĩ/ *n.* 'relatives'
- **tĩltyiin** /ˈtĩltjiːn/ *n.* 'beaver'
- **tĩnyo** /ˈtĩɲo/ *v.* 'dream (something)'
- **to** /to/ *quant.* 'some'
- **toa** /ˈtoa/ *adj.* 'naked'
- **todyuka** /ˈtodjuka/ *v.* 'do'
- **tomosa** /ˈtomosa/ *n.* 'poet'
- **tonkli** /ˈtonkli/ *adj.* 'innocent'
- **totinysi** /toˈtiɲsi/ *n.* 'linen'
- **traakeii** /ˈtraːkeiː/ *v.* 'forgive'
- **trablaal** /ˈtrablaːl/ *n.* 'dream'
- **tralpya** /ˈtralpja/ *n.* 'summit'
- **tranysroko** /ˈtraɲsroko/ *n.* 'flavour'
- **tri** /tri/ *n.* 'brain'
- **tribi** /ˈtribi/ *v.* 'share'
- **trorpa** /ˈtrorpa/ *part.* 'now'
- **tru** /tru/ *n.* 'loom'
- **trutanye** /ˈtrutaɲe/ *n.* 'belt'
- **tu** /tu/ *adj.* 'white'
- **tudhi** /ˈtuði/ *v.* 'to become white' ← *tu*
- **tue** /ˈtue/ *v.* 'feel'
- **tuehem** /ˈtuehem/ *adj.* 'strong'
- **tul** /tul/ *n.* 'rafter'
- **tulpikyaa** /ˈtulpikjaː/ *n.* 'shirt'
- **tun** /tun/ *n.* 'fortress'
- **tunu** /ˈtunu/ *n.* 'hair (head)'
- **tuny** /tuɲ/ *n.* 'tree trunk'
- **tun·yi** /ˈtunji/ *adj.* 'correct (right)' = mesma palavra que right
- **tun·yi** /ˈtunji/ *adj.* 'right'
- **tun·yidhi** /ˈtunjiði/ *v.* 'to become correct (right)' ← *tun·yi*
- **tun·yiwe** /ˈtunjiwe/ [ˈtunjiwi] *v.* 'to make correct (right)' ← *tun·yi*
- **tupri** /ˈtupri/ *n.* 'world'
- **tupunkriir** /tuˈpunkriːr/ *v.* 'threaten'
- **tura** /ˈtura/ *n.* 'manioc bread'
- **tusany** /ˈtusaɲ/ *n.* 'knee' — PL: tusanymi; GEN: tusan
- **tusokwo** /ˈtusokwo/ *n.* 'fur'
- **tuu** /tuː/ *n.* 'penalty'
- **tuun** /tuːn/ *n.* 'cone'
- **tuutuu** /ˈtuːtuː/ *n.* 'top'
- **tuwe** /ˈtuwe/ [ˈtuwi] *v.* 'to make white' ← *tu*
- **twaa** /twaː/ *v.* 'recognize'
- **twaatum** /ˈtwaːtum/ *part.* 'it'
- **twakole** /ˈtwakole/ *n.* 'mare'
- **twampartyeny** /twamˈpartjeɲ/ *n.* 'sign'
- **twamxa** /ˈtwamʃa/ *n.* 'weather'
- **twayiir** /ˈtwajiːr/ *v.* 'stretch'
- **twe** /twe/ *n.* 'idol'
- **tweka** /ˈtweka/ *n.* 'clay'
- **twekakwunytwu** /ˌtwekaˈkwuɲtwu/ *n.* 'potter' ← *tweka* (agentivo)
- **twerlueq** /ˈtwerlueŋ/ *v.* 'swear'
- **twernu** /ˈtwernu/ *v.* 'pull off (skin)'
- **twi** /twi/ *v.* 'drip'
- **twilboom** /ˈtwilboom/ *adj.* 'greedy'
- **twinyquny** /ˈtwiɲŋuɲ/ *v.* 'roll'
- **twiq** /twiŋ/ *n.* 'fathom'
- **twirponhul** /twirˈponhul/ *adj.* 'beautiful'
- **twituu** /ˈtwituː/ *v.* 'regret'
- **twiwapu** /ˈtwiwapu/ *adj.* 'dense'
- **twiyaamba** /twiˈjaːmba/ *v.* 'boil (something)'
- **twĩ** /twĩ/ *n.* 'tree stump'
- **two** /two/ *n.* 'hand' — PL: twomi; GEN: twon
- **twoku** /ˈtwoku/ *n.* 'chameleon'
- **twokwii** /ˈtwokwiː/ *n.* 'necklace'
- **twu** /twu/ *interr.* 'what?'
- **twua** /ˈtwua/ *v.* 'creep'
- **twuploqdwi** /twuˈploŋdwi/ *v.* 'pray'
- **twuploqdwigwaaqum** /ˌtwuploŋˈdwiɡwaːŋum/ *n.* 'temple' = *twuploqdwi* + *gwaaqum*
- **twuqu** /ˈtwuŋu/ *n.* 'smoke' — PL: twuqumi; GEN: twuqun
- **tya** /tja/ *n.* 'louse' — PL: tyami; GEN: tyan
- **tyaa** /tjaː/ *num.* 'one'
- **tyalseq** /ˈtjalseŋ/ *v.* 'leave'
- **tyany** /tjaɲ/ *n.* 'thunder'
- **tyeil** /ˈtjeil/ *part.* 'day before yesterday'
- **tyeĩpraq** /ˈtjeĩpraŋ/ *v.* 'sow seeds'
- **tyemiiq** /ˈtjemiːŋ/ *v.* 'sound (of instrument or voice)'
- **tyemnirsi** /tjemˈnirsi/ *n.* 'work (labour)'
- **tyeyutyu** /ˈtjejutju/ *adj.* 'female (of animal)'
- **tyialan** /ˈtjialan/ *n.* 'spark'
- **tyianim** /ˈtjianim/ *v.* 'worship'
- **tyibinu** /ˈtjibinu/ *n.* 'ewe'
- **tyinul** /ˈtjinul/ *part.* 'eighty'
- **tyinyu** /ˈtjiɲu/ *v.* 'change'
- **tyitunyla** /tjiˈtuɲla/ *v.* 'defend'
- **tyitwigwi** /ˈtjitwiɡwi/ *adv.* 'hence'
- **tyĩm** /tjĩm/ *n.* 'fringe'
- **tyo** /tjo/ *v.* 'boil (of liquid)'
- **tyol** /tjol/ *v.* 'abstain from food'
- **tyom** /tjom/ *n.* 'summer'
- **tyu** /tju/ *n.* 'stone' — PL: tyumi; GEN: tyun
- **tyuii** /ˈtjuiː/ *n.* 'salt' — PL: tyuiimi; GEN: tyuiin
- **tyuiiso** /ˈtjuiːso/ *adj.* 'salty' ← *tyuii* (proprietivo)
- **tyulĩ** /ˈtjulĩ/ *n.* 'woman' — PL: tyulĩmi; GEN: tyulĩn
- **tyunymumgli** /tjuɲˈmumɡli/ *adj.* 'different'
- **tyunyzon** /ˈtjuɲzon/ *n.* 'child (descendant)' — PL: tyunyzonmi; GEN: tyunyzon
- **tyuso** /ˈtjuso/ *adj.* 'stony' ← *tyu*
- **tyuwoki** /ˈtjuwoki/ *v.* 'rustle'
- **u** /u/ *pron.* '3sg pronoun'
- **u** /u/ *pron.* 'he'
- **ua** /ˈua/ *n.* 'nasal mucus'
- **uaaqaa** /ˈuaːŋaː/ *n.* 'hut'
- **uatwi** /ˈuatwi/ *part.* 'nothing'
- **udan** /ˈudan/ *v.* 'pay'
- **udĩbo** /ˈudĩbo/ *n.* 'ankle'
- **udoto** /ˈudoto/ *n.* 'hen'
- **ue** /ˈue/ *v.* 'budge'
- **uerlaa** /uˈerlaː/ *n.* 'quiet, silence'
- **ugi** /ˈuɡi/ *n.* 'happiness'
- **ugwum** /ˈuɡwum/ *n.* 'nephew'
- **uhen** /ˈuhen/ *n.* 'heart' — PL: uhenmi; GEN: uhen
- **ui** /ˈui/ *v.i.* 'to fly' — PST: uipu
- **uigo** /ˈuiɡo/ [ˈuiɣo] *n.* 'result of flying' ← *ui*
- **ukkum** /ˈukːum/ *n.* 'parents-in-law'
- **ukle** /ˈukle/ *n.* 'praise'
- **uku** /ˈuku/ *n.* 'match'
- **ul** /ul/ *num.* 'two'
- **ulam** /ˈulam/ *adv.* 'there'
- **ular** /ˈular/ *n.* 'ridgepole'
- **ulni** /ˈulni/ *adj.* 'flat'
- **ulpakluny** /ˈulpakluɲ/ *n.* 'church'
- **ulraaq** /ˈulraːŋ/ *n.* 'button'
- **ulu** /ˈulu/ *n.* 'sap'
- **um** /um/ *n.* 'eye' — PL: ummi; GEN: un
- **umĩka** /ˈumĩka/ *v.* 'help'
- **umlu** /ˈumlu/ *adj.* 'loud'
- **umlusiq** /ˈumlusiŋ/ *n.* 'joy'
- **umo** /ˈumo/ *n.* 'rattle'
- **umqe** /ˈumŋe/ *v.* 'send'
- **un** /un/ *n.* 'toucan'
- **unin** /ˈunin/ *n.* 'bay'
- **unmom** /ˈunmom/ *n.* 'good luck'
- **unte** /ˈunte/ [ˈunti] *adj.* 'dirty'
- **unykwaaq** /ˈuɲkwaːŋ/ *adj.* 'mad'
- **uom** /ˈuom/ *n.* 'harvest'
- **upru** /ˈupru/ *adj.* 'old'
- **uprual** /ˈuprual/ *n.* 'old age' ← *upru*
- **uprual** /ˈuprual/ *n.* 'age' ← *upru* (qualidade)
- **uprubo** /ˈuprubo/ *n.* 'older sibling' = *upru* + *bo*
- **uprudhi** /ˈupruði/ *v.* 'to age' ← *upru*
- **upruedyĩ** /uˈpruedjĩ/ *n.* 'older brother' = *upru* + *edyĩ*
- **uprukwunytwu** /ˌupruˈkwuɲtwu/ *n.* 'old man' = *upru* + *kwunytwu*
- **uprukyi** /ˈuprukji/ *n.* 'grandfather' = *upru* + *kyi*
- **uprunu** /ˈuprunu/ *n.* 'grandmother' = *upru* + *nu*
- **uprupu** /ˈuprupu/ *n.* 'older sister' = *upru* + *pu*
- **uprutyulĩ** /uˈprutjulĩ/ *n.* 'old woman' = *upru* + *tyulĩ*
- **upyon** /ˈupjon/ *v.t.* 'to eat' — PST: upyonpu
- **upyongilingwe** /uˌpjonɡiˈlinɡwe/ *n.* 'spoon' = *upyon* + *gilingwe*
- **upyongo** /uˈpjonɡo/ *n.* 'meal' ← *upyon*
- **upyonkwunytwu** /ˌupjonˈkwuɲtwu/ *n.* 'one who eats' ← *upyon*
- **upyonqi** /uˈpjonŋi/ *adj.* 'tending to eat' ← *upyon*
- **uq** /uŋ/ *v.* 'sneeze'
- **uqabrim** /ˈuŋabrim/ *n.* 'April'
- **ur** /ur/ *v.* 'promise'
- **urle** /ˈurle/ *n.* 'pipe'
- **urqol** /ˈurŋol/ *v.i.* 'to rain' — PST: urqolpu
- **usen** /ˈusen/ *n.* 'afternoon'
- **usi** /ˈusi/ *adj.* 'far'
- **usyilpra** /uˈsjilpra/ *adj.* 'thin (of shape of object)'
- **uu** /uː/ *adj.* 'thick'
- **uukliinkli** /uːˈkliːnkli/ *n.* 'dawn'
- **uum** /uːm/ *part.* 'down'
- **uumhakya** /ˈuːmhakja/ *n.* 'hammock'
- **uumuubil** /ˈuːmuːbil/ *n.* 'colour'
- **uundruba** /ˈuːndruba/ *adv.* 'slow'
- **uunkye** /ˈuːnkje/ *n.* 'story'
- **uunykyu** /ˈuːɲkju/ *n.* 'womb'
- **uuqra** /ˈuːŋra/ *adj.* 'heavy'
- **uuqradhi** /ˈuːŋraði/ *v.* 'to become heavy' ← *uuqra*
- **uur** /uːr/ *adj.* 'clever'
- **uura** /ˈuːra/ *adv.* 'back (direction)'
- **uusa** /ˈuːsa/ *adj.* 'brackish'
- **uyi** /ˈuji/ *n.* 'lamp'
- **uyiir** /ˈujiːr/ *n.* 'sibling-in-law'
- **uzaa** /ˈuzaː/ *v.* 'dash'
- **uzun** /ˈuzun/ *n.* 'Friday'
- **u·u** /ˈuu/ *n.* 'stable'
- **u·uo** /ˈuuo/ *n.* 'finger'
- **wa** /wa/ *n.* 'jaw'
- **waampa** /ˈwaːmpa/ *v.* 'cease'
- **waamtyu** /ˈwaːmtju/ *v.t.* 'to throw' — PST: waamtyupu
- **waamtyukwunytwu** /ˌwaːmtjuˈkwuɲtwu/ *n.* 'thing that throws' ← *waamtyu*
- **waanywaq** /ˈwaːɲwaŋ/ *n.* 'clan'
- **waaq** /waːŋ/ *v.* 'shoot'
- **wabla** /ˈwabla/ *n.* 'shell'
- **wabyi** /ˈwabji/ *n.* 'anger'
- **wagaa** /ˈwaɡaː/ *v.* 'buy'
- **wagaagwaaqum** /waˈɡaːɡwaːŋum/ *n.* 'market' = *wagaa* + *gwaaqum*
- **wakha** /ˈwakʰa/ *n.* 'master'
- **wamaaba** /ˈwamaːba/ *n.* 'oats'
- **wampe** /ˈwampe/ *adj.* 'broken'
- **wan** /wan/ *n.* 'bee'
- **wanwaku** /ˈwanwaku/ *v.* 'smile'
- **waqaq** /ˈwaŋaŋ/ *n.* 'sleep (state)'
- **waqgwa** /ˈwaŋɡwa/ *v.* 'invite'
- **waqgwinur** /ˈwaŋɡwinur/ *adj.* 'dead'
- **waqprawa** /ˈwaŋprawa/ *n.* 'swan'
- **wargyi** /ˈwarɡji/ *v.t.* 'to push' — PST: wargyipu
- **wate** /ˈwate/ *n.* 'goose'
- **watutwi** /ˈwatutwi/ *n.* 'magic'
- **waxal** /ˈwaʃal/ *part.* 'through'
- **waxihan** /ˈwaʃihan/ *v.* 'preserve'
- **wayi** /ˈwaji/ *part.* 'live, living, life'
- **wa·a** /ˈwaa/ *part.* 'soon'
- **wa·aaul** /ˈwaaːul/ *n.* 'frog'
- **we** /we/ *n.* 'thumb'
- **weliom** /ˈweliom/ *part.* 'where to'
- **welpo** /ˈwelpo/ *v.i.* 'to fight' — PST: welpopu
- **welpogo** /ˈwelpoɡo/ [ˈwelpoɣo] *n.* 'battle' ← *welpo*
- **welpokwunytwu** /ˌwelpoˈkwuɲtwu/ *n.* 'warrior' ← *welpo*
- **wemumgi** /weˈmumɡi/ *n.* 'beeswax'
- **wenpuuril** /ˈwenpuːril/ *n.* 'board'
- **wewĩ** /ˈwewĩ/ *n.* 'cover, lid'
- **wi** /wi/ *interr.* 'where?'
- **wia** /ˈwia/ *adj.* 'near'
- **wibiu** /ˈwibiu/ *n.* 'leather'
- **wigo** /ˈwiɡo/ *v.* 'study'
- **wigogwaaqum** /wiˈɡoɡwaːŋum/ *n.* 'school' = *wigo* + *gwaaqum*
- **wii** /wiː/ *n.* 'bone' — PL: wiimi; GEN: wiin
- **wiibyibyi** /ˈwiːbjibji/ *v.* 'hang'
- **wiibyibyikyebiyi** /wiːˌbjibjiˈkjebiji/ *v.* 'hang up' = *wiibyibyi* + *kyebiyi*
- **wiimtir** /ˈwiːmtir/ *v.* 'shit'
- **wiin** /wiːn/ *adj.* 'lazy'
- **wiipaain** /ˈwiːpaːin/ *v.* 'begin'
- **wiipaaingo** /ˌwiːpaːˈinɡo/ *n.* 'beginning' ← *wiipaain* (ação)
- **wiir** /wiːr/ *adj.* 'rich'
- **wiirkraa** /ˈwiːrkraː/ *n.* 'mountain' — PL: wiirkraami; GEN: wiirkraan
- **wilsi** /ˈwilsi/ *n.* 'food'
- **winbli** /ˈwinbli/ *n.* 'stove'
- **wiosril** /ˈwiosril/ *n.* 'cousin'
- **wiwi** /ˈwiwi/ *part.* 'beside'
- **wi·ii** /ˈwiiː/ *v.* 'limp'
- **wĩ** /wĩ/ *pron.* 'we'
- **wĩbaape** /ˈwĩbaːpe/ *n.* 'bamboo'
- **wĩmzokem** /ˈwĩmzokem/ *v.* 'dye'
- **wo** /wo/ *v.* 'tell'
- **woan** /ˈwoan/ *n.* 'attack'
- **wom** /wom/ *n.* 'filth'
- **wompe** /ˈwompe/ *n.* 'boil (of skin)'
- **wone** /ˈwone/ *n.* 'trap (pitfall)'
- **wonylayi** /ˈwoɲlaji/ *v.* 'die, dead'
- **wonywu** /ˈwoɲwu/ *n.* 'fear'
- **wotye** /ˈwotje/ *v.* 'annoy'
- **woubaam** /ˈwoubaːm/ *n.* 'ancestors'
- **woyonnyi** /woˈjonɲi/ *n.* 'daughter-in-law (of man)'
- **wu** /wu/ *v.* 'grasp'
- **wuaam** /ˈwuaːm/ *n.* 'violence'
- **wubor** /ˈwubor/ *n.* 'awl'
- **wudusa** /ˈwudusa/ *n.* 'September'
- **wulmakleq** /ˈwulmakleŋ/ *v.* 'explain'
- **wulquq** /ˈwulŋuŋ/ *n.* 'dust' — PL: wulquqmi; GEN: wulqun
- **wulquqso** /wulˈŋuŋso/ *adj.* 'full of dust' ← *wulquq*
- **wumo** /ˈwumo/ *n.* 'fairy'
- **wun** /wun/ *v.* 'sink'
- **wunbyon** /ˈwunbjon/ *n.* 'hare'
- **wunkheny** /ˈwunkʰeɲ/ *n.* 'fence'
- **wunum** /ˈwunum/ *n.* 'saucer'
- **wunykhuny** /ˈwuɲkʰuɲ/ *n.* 'fig'
- **wurti** /ˈwurti/ *n.* 'cap'
- **wutum** /ˈwutum/ *adj.* 'aged, old'
- **wuu** /wuː/ *n.* 'parrot'
- **wuuelphi** /wuːˈelpʰi/ *n.* 'October'
- **wuutwu** /ˈwuːtwu/ *adj.* 'weak'
- **wuzii** /ˈwuziː/ *v.* 'howl'
- **wuzwun** /ˈwuzwun/ *n.* 'mud'
- **xa** /ʃa/ *n.* 'anteater'
- **xaao** /ˈʃaːo/ *n.* 'space'
- **xahol** /ˈʃahol/ *n.* 'opossum'
- **xakiam** /ˈʃakiam/ *n.* 'descendants'
- **xapro** /ˈʃapro/ *adv.* 'afterwards'
- **xe** /ʃe/ *n.* 'donkey'
- **xeempun** /ʃeˈempun/ *n.* 'thought'
- **xekunyda** /ʃeˈkuɲda/ *v.* 'fall asleep'
- **xem** /ʃem/ *n.* 'calf of the leg'
- **xemo** /ˈʃemo/ *v.* 'stir'
- **xensaa** /ˈʃensaː/ *n.* 'arctic lights'
- **xeyin** /ˈʃejin/ *adj.* 'bitter'
- **xeyiniwe** /ʃeˈjiniwe/ [ʃeˈjiniwi] *v.* 'to make bitter' ← *xeyin*
- **xi** /ʃi/ *v.t.* 'to wipe' — PST: xipu
- **xia** /ˈʃia/ *v.* 'prevent'
- **xil** /ʃil/ *n.* 'orphan'
- **xinytye** /ˈʃiɲtje/ *adj.* 'rough (of sea)'
- **xiyii** /ˈʃijiː/ *n.* 'well'
- **xo** /ʃo/ *adj.* 'calm (of sea)'
- **xokwi** /ˈʃokwi/ *n.* 'shoulderblade'
- **xradyum** /ˈʃradjum/ *n.* 'conversation'
- **xrimnyusyiim** /ˈʃrimɲusjiːm/ *part.* 'immediately'
- **xromo** /ˈʃromo/ *n.* 'light (radiation)'
- **xrue** /ˈʃrue/ *n.* 'host'
- **xrusipo** /ˈʃrusipo/ *n.* 'mother-in-law (of woman)'
- **xudupyum** /ˈʃudupjum/ *v.* 'perish'
- **xum** /ʃum/ *n.* 'sibling’s child'
- **xuwal** /ˈʃuwal/ *n.* 'arrow'
- **xwaa** /ʃwaː/ *n.* 'sickle'
- **xwe** /ʃwe/ [ʃwi] *num.* 'three'
- **xweimolpyer** /ˌʃweiˈmolpjer/ *part.* 'three times' = *xwe* + *imolpyer*
- **xwen** /ʃwen/ *n.* 'citrus fruit'
- **xweu** /ˈʃweu/ *v.* 'roar'
- **xwi** /ʃwi/ *v.* 'stab'
- **xwiqtakwu** /ˈʃwiŋtakwu/ *n.* 'glue'
- **xwolpraamklu** /ʃwolˈpraːmklu/ *n.* 'square'
- **xwondasuq** /ˈʃwondasuŋ/ *v.* 'draw milk'
- **xwu** /ʃwu/ *n.* 'comb'
- **xyaapirpu** /ʃjaːˈpirpu/ *n.* 'circle'
- **xyalmi** /ˈʃjalmi/ *n.* 'flowing body of water'
- **xyanxuumsum** /ʃjanˈʃuːmsum/ *n.* 'lock'
- **xyanxuumsumgilingwe** /ˌʃjanʃuːmˌsumɡiˈlinɡwe/ *n.* 'key' = *xyanxuumsum* + *gilingwe*
- **xya·azya** /ˈʃjaazja/ *n.* 'manner'
- **xyuno** /ˈʃjuno/ *n.* 'pot, cooking vessel'
- **xyuqpukuq** /ˈʃjuŋpukuŋ/ *n.* 'earthquake'
- **xyuu** /ʃjuː/ *n.* 'yoke'
- **xyuupua** /ˈʃjuːpua/ *v.* 'spread out'
- **ya** /ja/ *n.* 'week'
- **yaaun** /ˈjaːun/ *v.* 'live'
- **yago** /ˈjaɡo/ *n.* 'paint (pigments)'
- **yagwam** /ˈjaɡwam/ *v.i.* 'to swim' — PST: yagwampu
- **yagwamkwunytwu** /ˌjaɡwamˈkwuɲtwu/ *n.* 'swimmer' ← *yagwam*
- **yagyami** /ˈjaɡjami/ *n.* 'noise'
- **yahobye** /ˈjahobje/ *n.* 'plate'
- **yake** /ˈjake/ [ˈjaɣi] *v.t.* 'to take' — PST: yakepu
- **yam** /jam/ *v.t.* 'to hit/beat' — PST: yampu
- **yame** /ˈjame/ *part.* 'before'
- **yan** /jan/ *part.* 'above'
- **yanpi** /ˈjanpi/ *part.* 'day after tomorrow'
- **yanygyo** /ˈjaɲɡjo/ *v.* 'cultivate'
- **yapil** /ˈjapil/ [ˈjaβil] *n.* 'name' — PL: yapilmi; GEN: yapin
- **yapro** /ˈjapro/ *n.* 'cave'
- **yaqgaxwe** /ˈjaŋɡaʃwe/ *n.* 'turtle'
- **yater** /ˈjater/ *n.* 'citizen'
- **yaunyzu** /jaˈuɲzu/ *v.* 'go out'
- **ya·awi** /ˈjaawi/ *n.* 'shield'
- **ye** /je/ [ji] *n.* 'head' — PL: yemi; GEN: yen
- **yekrewuu** /ˈjekrewuː/ *n.* 'mirror'
- **yel** /jel/ *v.* 'recover'
- **yelwo** /ˈjelwo/ *n.* 'slope'
- **yem** /jem/ *v.* 'slide'
- **yenyzyi** /ˈjeɲzji/ *n.* 'sky' — PL: yenyzyimi; GEN: yenyzyin
- **yepe** /ˈjepe/ *v.* 'assemble'
- **yeq** /jeŋ/ *n.* 'brick'
- **yeqmusyam** /ˈjeŋmusjam/ *v.* 'fold'
- **yesuhuu** /ˈjesuhuː/ *v.* 'enter'
- **yetya** /ˈjetja/ *n.* 'head louse' = *ye* + *tya*
- **yezo** /ˈjezo/ *n.* 'oak'
- **yi** /ji/ *v.i.* 'to spit' — PST: yipu
- **yia** /ˈjia/ *v.* 'deceive'
- **yiaai** /ˈjiaːi/ *n.* 'thread'
- **yibyan** /ˈjibjan/ *adj.* 'cold'
- **yiga** /ˈjiɡa/ *n.* 'toe'
- **yiibyi** /ˈjiːbji/ *n.* 'woods' — PL: yiibyimi; GEN: yiibyin
- **yiilu** /ˈjiːlu/ *adj.* 'rotten'
- **yiin** /jiːn/ *v.* 'drag'
- **yiipa** /ˈjiːpa/ *n.* 'stepfather'
- **yiirtwuq** /ˈjiːrtwuŋ/ *n.* 'mainland'
- **yiisoplo** /ˈjiːsoplo/ *n.* 'judge'
- **yiisoplogo** /jiːˈsoploɡo/ *n.* 'judgment' ← *yiisoplo* (ação)
- **yiiu** /ˈjiːu/ *n.* 'wages'
- **yilu** /ˈjilu/ *n.* 'mead'
- **yimxyau** /ˈjimʃjau/ *n.* 'knot'
- **yinii** /ˈjiniː/ *n.* 'what is spited' ← *yi*
- **yinpeqin** /ˈjinpeŋin/ *n.* 'sacrifice'
- **yintar** /ˈjintar/ *adj.* 'black'
- **yintaral** /ˈjintaral/ *n.* 'blackness' ← *yintar*
- **yintariwe** /jinˈtariwe/ [jinˈtariwi] *v.* 'to make black' ← *yintar*
- **yiq** /jiŋ/ *n.* 'freeman'
- **yiqapuuny** /ˈjiŋapuːɲ/ *n.* 'maize'
- **yiqi** /ˈjiŋi/ *n.* 'twins'
- **yir** /jir/ *n.* 'lake' — PL: yirmi; GEN: yin = mesma palavra que sea
- **yir** /jir/ *n.* 'sea' — PL: yirmi; GEN: yin
- **yiriwu** /ˈjiriwu/ *n.* 'picture'
- **yirlĩum** /ˈjirlĩum/ *v.t.* 'to hide' — PST: yirlĩumpu
- **yituul** /ˈjituːl/ *n.* 'wall'
- **yiyin** /ˈjijin/ *adj.* 'young'
- **yiyinbo** /jiˈjinbo/ *n.* 'younger sibling' = *yiyin* + *bo*
- **yiyinedyĩ** /jiˈjinedjĩ/ *n.* 'younger brother' = *yiyin* + *edyĩ*
- **yiyinkwunytwu** /ˌjijinˈkwuɲtwu/ *n.* 'young man' = *yiyin* + *kwunytwu*
- **yiyinpu** /jiˈjinpu/ *n.* 'younger sister' = *yiyin* + *pu*
- **yiyintyulĩ** /jiˈjintjulĩ/ *n.* 'young woman' = *yiyin* + *tyulĩ*
- **yĩ** /jĩ/ *n.* 'squirrel'
- **yo** /jo/ *v.t.* 'to say' — PST: yopu
- **yoam** /ˈjoam/ *v.* 'hate'
- **yodhuq** /ˈjoðuŋ/ *v.* 'miss'
- **yokuqku** /joˈkuŋku/ *n.* 'grass-skirt'
- **yol** /jol/ *n.* 'bread'
- **yolqe** /ˈjolŋe/ *n.* 'needle tree'
- **yomhikwa** /ˈjomhikwa/ *n.* 'circumcision'
- **yona** /ˈjona/ *v.* 'write'
- **yonii** /ˈjoniː/ *n.* 'saying' ← *yo*
- **yonmanypii** /jonˈmaɲpiː/ *n.* 'brook'
- **yonya** /ˈjoɲa/ *n.* 'hoarfrost'
- **yonzim** /ˈjonzim/ *part.* 'first'
- **yopyensri** /joˈpjensri/ *n.* 'evening'
- **yoqi** /ˈjoŋi/ *adj.* 'tending to say' ← *yo*
- **yoxyi** /ˈjoʃji/ *adv.* 'one time'
- **yu** /ju/ *v.* 'chew'
- **yudyosa** /ˈjudjosa/ *v.* 'hinder'
- **yuegi** /ˈjueɡi/ *v.* 'move (oneself)'
- **yuhitiiq** /ˈjuhitiːŋ/ *n.* 'gun, cannon'
- **yuin** /ˈjuin/ *v.* 'ring (make sound)'
- **yul** /jul/ *v.* 'carry on head'
- **yulguulkya** /julˈɡuːlkja/ *n.* 'stepson'
- **yultun** /ˈjultun/ *v.t.* 'to rub' — PST: yultunpu
- **yume** /ˈjume/ *n.* 'skull'
- **yumuprum** /ˈjumuprum/ *n.* 'nostril'
- **yuny** /juɲ/ *n.* 'truth'
- **yuul** /juːl/ *n.* 'sun' — PL: yuulmi; GEN: yuun
- **yuum** /juːm/ *n.* 'glass'
- **yuur** /juːr/ *v.* 'drive'
- **yuuyo** /ˈjuːjo/ *n.* 'distance'
- **yuya** /ˈjuja/ *v.* 'wash'
- **za** /za/ *n.* 'hoe'
- **zaaĩ** /ˈzaːĩ/ *adj.* 'shallow'
- **zabii** /ˈzabiː/ *v.* 'taste'
- **zaemi** /ˈzaemi/ *n.* 'doorpost'
- **zai** /ˈzai/ *v.* 'teach'
- **zaikwunytwu** /ˌzaiˈkwuɲtwu/ *n.* 'teacher' ← *zai* (agentivo)
- **zal** /zal/ *n.* 'tooth' — PL: zalmi; GEN: zan
- **zalqimqe** /zalˈŋimŋe/ *n.* 'arch'
- **zamhu** /ˈzamhu/ *n.* 'shop'
- **zatinkwĩ** /zaˈtinkwĩ/ *v.* 'rot'
- **za·anen** /ˈzaanen/ *v.* 'snap'
- **ze** /ze/ *n.* 'lunch'
- **zempya** /ˈzempja/ *n.* 'wing' — PL: zempyami; GEN: zempyan
- **zi** /zi/ *n.* 'line'
- **zim** /zim/ *v.* 'ride'
- **ziqipyu** /ˈziŋipju/ *n.* 'soldier'
- **zo** /zo/ *num.* 'nine'
- **zrikwa** /ˈzrikwa/ *n.* 'fowl'
- **zu** /zu/ *n.* 'voice'
- **zuaq** /ˈzuaŋ/ *n.* 'star' — PL: zuaqmi; GEN: zuan
- **zum** /zum/ *v.* 'think (believe)'
- **zurpyo** /ˈzurpjo/ *v.* 'bury'
- **zurpyogwaaqum** /zurˈpjoɡwaːŋum/ *n.* 'grave' = *zurpyo* + *gwaaqum*
- **zuuoxyaa** /ˈzuːoʃjaː/ *adv.* 'backward'
- **zuwun** /ˈzuwun/ *v.* 'hope'
- **zwa** /zwa/ *part.* 'same'
- **zwaamqa** /ˈzwaːmŋa/ *n.* 'bowl'
- **zwegreno** /ˈzweɡreno/ *v.* 'hinder, prevent'
- **zwerpumu** /ˈzwerpumu/ *v.* 'stop'
- **zwi** /zwi/ *adj.* 'poor'
- **zwoklokya** /ˈzwoklokja/ *n.* 'elevation'
- **zwu** /zwu/ *v.* 'convict'
- **zwukle** /ˈzwukle/ *n.* 'thatch'
- **zwun** /zwun/ *n.* 'milk'
- **zwuo** /ˈzwuo/ *adj.* 'former'
- **zyagwe** /ˈzjaɡwe/ *v.* 'drop (something)'
- **zyeo** /ˈzjeo/ *adj.* 'stupid'
- **zyilke** /ˈzjilke/ *n.* 'bean'
- **zyite** /ˈzjite/ *n.* 'fruit'
- **zyu·u** /ˈzjuu/ *v.* 'refuse'

Expressos sem palavra própria: 'in' → caso locative; 'at' → caso locative; 'with (accompanying)' → caso instrumental

## Nomes próprios

- Nomes sem marca de gênero
- Sobrenomes: nome do pai + sufixo patronímico (-am)
- Sufixo de povoado: -la /-la/

### Pessoas

| Nome | Pronúncia | Significado | Sobrenome |
|---|---|---|---|
| **Etwiqa Azemam** | /ˈetwiŋa/ | red snake | child of Azem |
| **Nowo Liyoam** | /ˈnowo/ | — | child of Liyo |
| **Miyum Neduam** | /ˈmijum/ | — | child of Nedu |
| **Ayaamqem Yinyeam** | /aˈjaːmŋem/ | — | child of Yinye |
| **Nuupita Uprubiam** | /ˈnuːpita/ | sweet snow | child of Uprubi |
| **Puyaamu Latwoam** | /ˈpujaːmu/ | — | child of Latwo |
| **Niwum Woneam** | /ˈniwum/ | — | child of Wone |
| **Ayii Lewamekuuam** | /ˈajiː/ | — | child of Lewamekuu |
| **Nuri Wiiriimam** | /ˈnuri/ | — | child of Wiiriim |
| **Huumal Qiiwuam** | /ˈhuːmal/ | — | child of Qiiwu |
| **Dyuyir Bunqa·am** | /ˈdjujir/ | yellow sea | child of Bunqa |
| **Luxyubu Umuyeam** | /ˈluʃjubu/ | long river | child of Umuye |
| **Tutwo Uprumekuuam** | /ˈtutwo/ | white hand | child of Uprumekuu |
| **Innyayir Nilepaqam** | /ˈinɲajir/ | new sea | child of Nilepaq |
| **Anim Iwiiqam** | /ˈanim/ | — | child of Iwiiq |
| **Ipanii Yomuuam** | /ˈipaniː/ | — | child of Yomuu |
| **Aru Puqĩnyanam** | /ˈaru/ | — | child of Puqĩnyan |
| **Qiwim Qeqiam** | /ˈŋiwim/ | — | child of Qeqi |
| **Uniyum Tuyiram** | /ˈunijum/ | — | child of Tuyir |
| **Omitil Etwimekuuam** | /ˈomitil/ | — | child of Etwimekuu |

### Lugares

| Nome | Pronúncia | Tipo | Significado |
|---|---|---|---|
| **Tyu·un** | /ˈtjuun/ | locativo | at the stone |
| **Bila** | /ˈbila/ | povoado | fish-town |
| **Mina** | /ˈmina/ | antigo (sem significado) | — |
| **Maqma** | /ˈmaŋma/ | antigo (sem significado) | — |
| **Innyabu** | /ˈinɲabu/ | composto | new river |
| **Pitayir** | /ˈpitajir/ | composto | snow sea |
| **Pitabu** | /ˈpitabu/ | composto | snow river |
| **Ani** | /ˈani/ | antigo (sem significado) | — |
| **Gwapalqi** | /ɡwaˈpalŋi/ | composto | grass stone |
| **Etwityu** | /ˈetwitju/ | composto | red stone |
| **Tyumaq** | /ˈtjumaŋ/ | composto | stone soil |
| **Miima** | /ˈmiːma/ | antigo (sem significado) | — |
| **Kimla** | /ˈkimla/ | povoado | water-town |
| **Maqun** | /ˈmaŋun/ | locativo | at the soil |
| **Pitala** | /ˈpitala/ | povoado | snow-town |
| **Wiiyir** | /ˈwiːjir/ | composto | bone sea |
| **Qala** | /ˈŋala/ | povoado | snake-town |
| **Gwaun** | /ˈɡwaun/ | locativo | at the grass |
| **Bu·un** | /ˈbuun/ | locativo | at the river |
| **Usemal** | /ˈusemal/ | antigo (sem significado) | — |

## Validação

- Fonemas fora do inventário: nenhum
- Formas que o sândi não reparou: 0
- Grafias que não podem ser lidas de volta: 0
- Avisos dos módulos:
  - Fonotática: encontros no ataque: obstruinte+líquida/glide
  - Fonotática: perfil de coda: sonorants
  - Derivação: 27 lacuna(s) e 1 bloqueio(s): nem toda base aceita cada processo, e palavras que já existem impedem a derivada
  - Numerais: conectivo obrigatório na soma, para distinguir 13 de 30
