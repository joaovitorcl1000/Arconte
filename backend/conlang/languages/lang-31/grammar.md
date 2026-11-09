# Akixontaqian

Pasta: `languages/lang-31/`

Nome nativo: **akixontaq** /ˌakiˈʃontaŋ/ (literalmente 'person')

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
- Exemplos: /ˈbuiː/, /ˈkimʃwiːhuŋ/, /ˈporkju/, /klemˈkopuklaːm/, /ˈjapil/, /ˌiːamˈsriːlkwiː/

### Mudanças sonoras

3 regras, aplicadas em ordem; 37 de 228 palavras mudaram. A forma do dicionário fica entre barras /.../, e a pronúncia depois das mudanças, entre colchetes [...].

Sons novos criados pelas mudanças: [ɣ] [β]

| # | Regra | Origem | Palavras afetadas | Exemplo |
|---|---|---|---|---|
| 1 | `{p,t,k} > {b,d,ɡ} / V_V` | natural | 25 | *klemkopuklaam* /klemkopuklaːm/ → [klemˈkobuklaːm] 'tongue' |
| | sonorização entre vogais (como no espanhol: lupus → lobo) | | | |
| 2 | `{b,d,ɡ} > {β,ð,ɣ} / V_V` | natural | 33 | *klemkobuklaam* /klemkobuklaːm/ → [klemˈkoβuklaːm] 'tongue' |
| | espirantização entre vogais (como no espanhol: lado [laðo]) | | | |
| 3 | `n > m / _{p,b}` | natural | 6 | *ponpyel* /ponpjel/ → [ˈpompjel] 'back' |
| | assimilação nasal (n > m antes de labial) | | | |


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

### Nome: *plaː* 'dog'

|  | SG | PAUC | PL |
|---|---|---|---|
| DIR | plaː | plaːn | plaːmi |
| GEN | plaːn | plaːnin | plaːmin |
| LOC | plaːun | plaːnun | plaːmiun |
| INS | plaːni | plaːnni | plaːmini |
| ABL | plaːbu | plaːnbu | plaːmibu |
| ALL | plaːka | plaːnka | plaːmika |
| ESS | plaːm | plaːnim | plaːmim |

### Verbo: *ukwu* 'to see'

|  | PRS | PST | FUT |
|---|---|---|---|
| IND | ukwu | ukwupu | ukwupi |
| IMP | ukwua | ukwupua | ukwupia |
| POT | ukwuŋ | ukwupuŋ | ukwupiŋ |

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
- Posse inalienável (partes do corpo e parentes) marcada no próprio nome; nos demais, a marca vai no classificador de posse paam

### Possessivos

| Pessoa | Possessivo | Pronúncia | Plural |
|---|---|---|---|
| 1SG ('my dog') | **paamlo plaa** | /ˈpaːmlo plaː/ | **paamlo plaami** |
| 2SG ('your dog') | **paamqa plaa** | /ˈpaːmŋa plaː/ | **paamqa plaami** |
| 3SG ('his/her/its dog') | **paamol plaa** | /ˈpaːmol plaː/ | **paamol plaami** |
| 1INCL.PAUC ('our (incl.) (paucal) dog') | **paamin plaa** | /ˈpaːmin plaː/ | **paamin plaami** |
| 1EXCL.PAUC ('our (excl.) (paucal) dog') | **paampi plaa** | /ˈpaːmpi plaː/ | **paampi plaami** |
| 2PAUC ('your (paucal) dog') | **paamri plaa** | /ˈpaːmri plaː/ | **paamri plaami** |
| 3PAUC ('their (paucal) dog') | **paamki plaa** | /ˈpaːmki plaː/ | **paamki plaami** |
| 1INCL.PL ('our (incl.) dog') | **paamsu plaa** | /ˈpaːmsu plaː/ | **paamsu plaami** |
| 1EXCL.PL ('our (excl.) dog') | **paamil plaa** | /ˈpaːmil plaː/ | **paamil plaami** |
| 2PL ('your (pl.) dog') | **paampuu plaa** | /ˈpaːmpuː plaː/ | **paampuu plaami** |
| 3PL ('their dog') | **paamti plaa** | /ˈpaːmti plaː/ | **paamti plaami** |

### Alienabilidade

- **iiyugyuwilo** /ˌiːjuˈɡjuwilo/ — 'my hand' (inalienable)
- **paamlo plaa** /ˈpaːmlo plaː/ — 'my dog' (alienable)

### Posse entre nomes

- **ozwuun plaa** /ˈozwuːn plaː/ — 'the woman's dog'

## Comparação

- Comparativo: locativa (o termo comparado vai num caso ou adposição de origem/lugar)
- Termo comparado no caso ablative
- Grau comparativo no adjetivo: -wi
- Superlativo: afixo -uq
- Equativo: partícula ('como') qon

### Formas do adjetivo

| Grau | Forma | Pronúncia |
|---|---|---|
| Positivo | **twaa** | /twaː/ |
| Comparativo | **twaawi** | /ˈtwaːwi/ |
| Superlativo | **twaauq** | /ˈtwaːuŋ/ |

### Comparativo

**Plaa twukuubu twaawi.**

```
plaa  twukuubu   twaawi
plaː  twukuː-bu  twaː-wi
dog   fish-ABL   big-COMPR
'The dog is bigger than the fish.'
```

### Superlativo

**Plaa twaauq.**

```
plaa  twaauq
plaː  twaː-uŋ
dog   big-SUPL
'The dog is the biggest.'
```

### Equativo

**Plaa twukuu qon twaa.**

```
plaa  twukuu  qon  twaa
plaː  twukuː  ŋon  twaː
dog   fish    as   big
'The dog is as big as the fish.'
```

## Derivação

6 processos produtivos; 72 palavras derivadas (o léxico base tem 231).

| Processo | Forma | Classe | Exemplo |
|---|---|---|---|
| agentivo ('quem faz') | sufixo -wa | v. → n. | *aakyuu* → **aakyuuwa** 'one who hunts' |
| ação ('o ato de') | sufixo -go | v. → n. | *alenuu* → **alenuugo** 'act of eating' |
| qualidade ('-eza', '-idade') | sufixo -al | adj. → n. | *nu* → **nual** 'goodness' |
| incoativo ('ficar ...') | sufixo -dhi | adj. → v. | *qaakye* → **qaakyedhi** 'to become old' |
| factitivo ('tornar ...') | sufixo -ul | adj. → v. | *twaa* → **twaaul** 'to make big' |
| proprietivo ('cheio de', '-oso') | sufixo -we | n. → adj. | *i* → **iwe** 'full of stone' |


## Irregularidades

2 palavras irregulares, todas entre as mais frequentes da língua.

### Palavras irregulares

| Palavra | Tipo | Forma | Regular seria | Irregular |
|---|---|---|---|---|
| 'go' (verbo) | apofonia | go-PST | ~~ipu~~ | **o** /o/ |
| 'person' (nome) | plural zero | person-PL | ~~akixontaqmi~~ | **akixontaq** /ˌakiˈʃontaŋ/ |

## Sintaxe

- Ordem básica: SOV
- Adposições: posposições
- Genitivo antes do nome; adjetivo depois do nome; demonstrativo depois do nome; numeral depois do nome
- Oração relativa: núcleo interno
- Perguntas sim/não: partícula no fim; perguntas de conteúdo: no início
- Pro-drop: não; cópula: zero
- Compostos: núcleo final (harmônico com o genitivo)

### 1. Oração intransitiva

**Iimyaki hulhuuwo.**

```
iːmjaki  huɬuːwo
child    sleep
'The child sleeps.'
```

### 2. Oração transitiva

**Ozwuu twukuu ukwu.**

```
ozwuː  twukuː  ukwu
woman  fish    see
'The woman sees the fish.'
```

### 3. Passado, objeto plural

**Plaa twukuumi alenuupu.**

```
plaː  twukuːmi   alenuːpu
plaː  twukuː-mi  alenuː-pu
dog   fish-PL    eat-PST
'The dog ate the fish.'
```

### 4. Oração bitransitiva

**Ozwuu iimyakika twukuu yirlĩ.**

```
ozwuː  iːmjakika   twukuː  jirlĩ
ozwuː  iːmjaki-ka  twukuː  jirlĩ
woman  child-ALL   fish    give
'The woman gives the fish to the child.'
```

### 5. Pronomes

**Ka gwiny ukwu.**

```
ka   ɡwiɲ  ukwu
1SG  2SG   see
'I see you.'
```

### 6. Sintagma nominal (demonstrativo, numeral, adjetivo)

**Plaami twaa ogwu twu yapil.**

```
plaːmi   twaː  oɡwu  twu   japil
plaː-mi  twaː  oɡwu  twu   japil
dog-PL   big   two   this  come
'These two big dogs come.'
```

### 7. Posse (genitivo)

**Ozwuun plaa hulhuuwo.**

```
ozwuːn     plaː  huɬuːwo
ozwuː-n    plaː  huɬuːwo
woman-GEN  dog   sleep
'The woman's dog sleeps.'
```

### 8. Adjunto locativo

**Iimyaki klaxuutyaaun hulhuuwo.**

```
iːmjaki  klaʃuːtjaːun   huɬuːwo
iːmjaki  klaʃuːtjaː-un  huɬuːwo
child    house-LOC      sleep
'The child sleeps in the house.'
```

### 9. Predicado adjetival (cópula zero)

**Twukuu twaa.**

```
twukuː  twaː
fish    big
'The fish is big.'
```

### 10. Negação

**Iimyaki hulhuuwogu.**

```
iːmjaki  huɬuːwoɡu
iːmjaki  huɬuːwo-ɡu
child    sleep-NEG
'The child does not sleep.'
```

### 11. Pergunta sim/não

**Ozwuu twukuu ukwu li.**

```
ozwuː  twukuː  ukwu  li
woman  fish    see   Q
'Does the woman see the fish?'
```

### 12. Pergunta de conteúdo (palavra interrogativa no início)

**Twa ozwuu ukwu.**

```
twa   ozwuː  ukwu
what  woman  see
'What does the woman see?'
```

## Dicionário

231 entradas, lista `all` do Concepticon, mais 72 palavras derivadas.

Formato: **grafia** /pronúncia/ [pronúncia depois das mudanças sonoras, quando muda] classe 'significado' ← base, nas derivadas

- **aakyuu** /ˈaːkjuː/ *v.t.* 'to hunt' — PST: aakyuupu
- **aakyuuwa** /ˈaːkjuːwa/ *n.* 'one who hunts' ← *aakyuu*
- **aamxi** /ˈaːmʃi/ *n.* 'louse' — PL: aamximi; GEN: aamxin
- **akixontaq** /ˌakiˈʃontaŋ/ [ˌaɣiˈʃontaŋ] *n.* 'person' — **PL: akixontaq** (irregular); GEN: akixontan
- **alenuu** /ˈalenuː/ *v.t.* 'to eat' — PST: alenuupu
- **alenuugo** /aˈlenuːɡo/ [aˈlenuːɣo] *n.* 'act of eating' ← *alenuu*
- **alenuuwa** /aˈlenuːwa/ *n.* 'one who eats' ← *alenuu*
- **alrunrenblĩn** /ˌalrunˈrenblĩn/ [ˌalrunˈremblĩn] *v.t.* 'to hit' — PST: alrunrenblĩnpu
- **an** /an/ *pron.* 'ye'
- **aqi** /ˈaŋi/ *adj.* 'smooth'
- **aqiul** /ˈaŋiul/ *v.* 'to make smooth' ← *aqi*
- **aqoton** /ˈaŋoton/ [ˈaŋoðon] *n.* 'eye' — PL: aqotonmi; GEN: aqoton
- **asem** /ˈasem/ *n.* 'fog' — PL: asemmi; GEN: asen
- **balwuplu** /ˈbalwuplu/ *adj.* 'red'
- **balwupludhi** /balˈwupluði/ *v.* 'to become red' ← *balwuplu*
- **banpya** /ˈbanpja/ [ˈbampja] *adj.* 'bad'
- **banpyadhi** /ˈbanpjaði/ [ˈbampjaði] *v.* 'to become bad' ← *banpya*
- **bantwa** /ˈbantwa/ *n.* 'ant' — PL: bantwami; GEN: bantwan
- **ber** /ber/ *adj.* 'hard'
- **bi** /bi/ *adj.* 'narrow'
- **binliikrool** /binˈliːkrool/ *n.* 'thigh' — PL: binliikroolmi; GEN: binliikroon
- **bo** /bo/ *adj.* 'dry'
- **bodhi** /ˈboði/ *v.* 'to become dry' ← *bo*
- **boul** /ˈboul/ *v.* 'to make dry' ← *bo*
- **bu** /bu/ *quant.* 'few'
- **buii** /ˈbuiː/ *n.* 'fire' — PL: buiimi; GEN: buiin
- **buiiwe** /ˈbuiːwe/ *adj.* 'full of fire' ← *buii*
- **byaaq** /bjaːŋ/ *n.* 'rain' — PL: byaaqmi; GEN: byaan
- **byaasamsagwiq** /bjaːˈsamsaɡwiŋ/ *n.* 'stone/rock' — PL: byaasamsagwiqmi; GEN: byaasamsagwin
- **byezyi** /ˈbjezji/ *n.* 'liver' — PL: byezyimi; GEN: byezyin
- **byimam** /ˈbjimam/ *n.* 'flesh/meat' — PL: byimammi; GEN: byiman
- **byuun** /bjuːn/ *n.* 'night' — PL: byuunmi; GEN: byuun
- **cuurpe** /ˈθuːrpe/ *adj.* 'near'
- **dan** /dan/ *n.* 'grass' — PL: danmi; GEN: dan
- **danwe** /ˈdanwe/ *adj.* 'full of grass' ← *dan*
- **dyopuu** /ˈdjopuː/ [ˈdjoβuː] *v.i.* 'to vomit' — PST: dyopuupu
- **dyuu** /djuː/ *adj.* 'white'
- **dyuudhi** /ˈdjuːði/ *v.* 'to become white' ← *dyuu*
- **dyuuiq** /ˈdjuːiŋ/ *adj.* 'dirty'
- **dyuuul** /ˈdjuːul/ *v.* 'to make white' ← *dyuu*
- **e** /e/ *n.* 'child (descendant)' — PL: emi; GEN: en
- **em** /em/ *conj.* 'and'
- **enlu** /ˈenlu/ *v.t.* 'know (something)' — PST: enlupu
- **eqtasel** /ˈeŋtasel/ *v.i.* 'to rain' — PST: eqtaselpu
- **gro** /ɡro/ *num.* 'one'
- **gu** /ɡu/ *neg.* 'not' — expresso por afixo verbal
- **guony** /ˈɡuoɲ/ *n.* 'heart' — PL: guonymi; GEN: guon
- **gwe** /ɡwe/ *v.t.* 'to hit/beat' — PST: gwepu
- **gwim** /ɡwim/ *n.* 'nose' — PL: gwimmi; GEN: gwin
- **gwiny** /ɡwiɲ/ *pron.* '2sg pronoun'
- **gyakya** /ˈɡjakja/ *v.t.* 'to rub' — PST: gyakyapu
- **haaobe** /ˈhaːobe/ [ˈhaːoβe] *n.* 'wood' — PL: haaobemi; GEN: haaoben = mesma palavra que tree
- **haaobe** /ˈhaːobe/ [ˈhaːoβe] *n.* 'tree' — PL: haaobemi; GEN: haaoben
- **haaobewe** /haːˈobewe/ [haːˈoβewe] *adj.* 'full of tree' ← *haaobe*
- **he** /he/ *n.* 'blood' — PL: hemi; GEN: hen
- **hepyiqayin** /heˈpjiŋajin/ *n.* 'ear' — PL: hepyiqayinmi; GEN: hepyiqayin
- **hewe** /ˈhewe/ *adj.* 'full of blood' ← *he*
- **him** /him/ *v.i.* 'to blow' — PST: himpu
- **hulhuuwo** /ˈhuɬuːwo/ *v.i.* 'sleep' — PST: hulhuuwopu
- **hulhuuwogo** /huˈɬuːwoɡo/ [huˈɬuːwoɣo] *n.* 'act of sleeping' ← *hulhuuwo*
- **huzye** /ˈhuzje/ *n.* 'road' — PL: huzyemi; GEN: huzyen
- **i** /i/ *v.i.* 'to go' — **PST: o** (irregular)
- **i** /i/ *n.* 'stone' — PL: imi; GEN: in
- **ii** /iː/ *n.* 'leg/foot' — PL: iimi; GEN: iin
- **iiamsriilkwii** /ˌiːamˈsriːlkwiː/ *n.* 'name' — PL: iiamsriilkwiimi; GEN: iiamsriilkwiin
- **iimyaki** /ˈiːmjaki/ [ˈiːmjaɣi] *n.* 'child (young human)' — PL: iimyakimi; GEN: iimyakin
- **iiyugyuwi** /iːˈjuɡjuwi/ *n.* 'hand' — PL: iiyugyuwimi; GEN: iiyugyuwin
- **iizreq** /ˈiːzreŋ/ *adj.* 'black'
- **iizreqdhi** /iːˈzreŋði/ *v.* 'to become black' ← *iizreq*
- **iizrequl** /ˈiːzreŋul/ *v.* 'to make black' ← *iizreq*
- **ilgwaan** /ˈilɡwaːn/ *adj.* 'left'
- **iliinmun** /iˈliːnmun/ *n.* 'tooth' — PL: iliinmunmi; GEN: iliinmun
- **itu** /ˈitu/ [ˈiðu] *adj.* 'short'
- **iwe** /ˈiwe/ *adj.* 'full of stone' ← *i*
- **ĩge** /ˈĩɡe/ [ˈĩɣe] *n.* 'horn' — PL: ĩgemi; GEN: ĩgen
- **ĩgwiii** /ˈĩɡwiːi/ *v.i.* 'to die' — PST: ĩgwiiipu
- **ĩgwiiigo** /ĩˈɡwiːiɡo/ [ĩɡˈwiːiɣo] *n.* 'act of dying' ← *ĩgwiii*
- **ĩtwa** /ˈĩtwa/ *adj.* 'green'
- **ka** /ka/ *pron.* '1sg pronoun'
- **kaa** /kaː/ *n.* 'stick' — PL: kaami; GEN: kaan
- **kaeki** /ˈkaeki/ [ˈkaeɣi] *v.i.* 'sit' — PST: kaekipu
- **kake** /ˈkake/ [ˈkaɣe] *v.i.* 'to think' — PST: kakepu
- **kakego** /ˈkakeɡo/ [ˈkaɣeɣo] *n.* 'act of thinking' ← *kake*
- **kakewa** /ˈkakewa/ [ˈkaɣewa] *n.* 'one who thinks' ← *kake*
- **kankwatĩ** /ˈkankwatĩ/ [ˈkankwaðĩ] *v.t.* 'to bite' — PST: kankwatĩpu
- **ka·aal** /ˈkaaːl/ *n.* 'hair' — PL: ka·aalmi; GEN: ka·aan
- **ka·aalwe** /kaˈaːlwe/ *adj.* 'full of hair' ← *ka·aal*
- **kii** /kiː/ *n.* 'sun' — PL: kiimi; GEN: kiin
- **kiibyar** /ˈkiːbjar/ *v.i.* 'to swim' — PST: kiibyarpu
- **kiibyargo** /kiːˈbjarɡo/ *n.* 'act of swimming' ← *kiibyar*
- **kiibyarwa** /kiːˈbjarwa/ *n.* 'one who swims' ← *kiibyar*
- **kiirti** /ˈkiːrti/ *n.* 'wife' — PL: kiirtimi; GEN: kiirtin
- **kimxwiihuq** /ˈkimʃwiːhuŋ/ *n.* 'water' — PL: kimxwiihuqmi; GEN: kimxwiihun
- **kimxwiihuqwe** /ˌkimʃwiːˈhuŋwe/ *adj.* 'full of water' ← *kimxwiihuq*
- **kintyuul** /ˈkintjuːl/ *v.i.* 'to fall' — PST: kintyuulpu
- **klaxuutyaa** /ˈklaʃuːtjaː/ *n.* 'house' — PL: klaxuutyaami; GEN: klaxuutyaan
- **klemkopuklaam** /klemˈkopuklaːm/ [klemˈkoβuklaːm] *n.* 'tongue' — PL: klemkopuklaammi; GEN: klemkopuklaan
- **klĩsii** /ˈklĩsiː/ *adj.* 'small'
- **klĩsiial** /ˈklĩsiːal/ *n.* 'smallness' ← *klĩsii*
- **konka** /ˈkonka/ *adj.* 'long'
- **konkadhi** /ˈkonkaði/ *v.* 'to become long' ← *konka*
- **konkaul** /ˈkonkaul/ *v.* 'to make long' ← *konka*
- **konka·al** /ˈkonkaal/ *n.* 'longness' ← *konka*
- **kosil** /ˈkosil/ *v.t.* 'to dig' — PST: kosilpu
- **kosilwa** /koˈsilwa/ *n.* 'one who digs' ← *kosil*
- **kou** /ˈkou/ *v.t.* 'to drink' — PST: koupu
- **kowelpotwu** /koˈwelpotwu/ *n.* 'berry' — PL: kowelpotwumi; GEN: kowelpotwun
- **krizikham** /ˈkrizikʰam/ *v.i.* 'to breathe' — PST: krizikhampu
- **kro** /kro/ *adj.* 'new'
- **kroal** /ˈkroal/ *n.* 'newness' ← *kro*
- **ku** /ku/ *interr.* 'how'
- **kuprakle** /ˈkuprakle/ *v.t.* 'to split' — PST: kupraklepu
- **kuua·aambram** /ˌkuːaˈaːmbram/ *v.t.* 'to do/make' — PST: kuua·aambrampu
- **kwiinybyuu** /ˈkwiːɲbjuː/ *v.i.* 'to run' — PST: kwiinybyuupu
- **kwiinybyuugo** /ˈkwiːɲbjuːɡo/ [ˈkwiːɲbjuːɣo] *n.* 'act of running' ← *kwiinybyuu*
- **kwiinybyuuwa** /ˈkwiːɲbjuːwa/ *n.* 'one who runs' ← *kwiinybyuu*
- **kwu** /kwu/ *quant.* 'all'
- **kyam** /kjam/ *dem.* 'that'
- **kyel** /kjel/ *v.t.* 'to crush/grind' — PST: kyelpu
- **kyĩ** /kjĩ/ *n.* 'root' — PL: kyĩmi; GEN: kyĩn
- **kyĩwe** /ˈkjĩwe/ *adj.* 'full of root' ← *kyĩ*
- **kyony** /kjoɲ/ *n.* 'snow' — PL: kyonymi; GEN: kyon
- **kyoyi** /ˈkjoji/ *v.i.* 'to flow' — PST: kyoyipu
- **kyoyo** /ˈkjojo/ *n.* 'worm' — PL: kyoyomi; GEN: kyoyon
- **lel** /lel/ *conj.* 'because'
- **lhakwuny** /ˈɬakwuɲ/ *n.* 'foot' — PL: lhakwunymi; GEN: lhakwun
- **lhrenenin** /ˈɬrenenin/ *n.* 'skin/hide' — PL: lhreneninmi; GEN: lhrenenin
- **linyou** /ˈliɲou/ *n.* 'shade/shadow' — PL: linyoumi; GEN: linyoun
- **lisyunpyuugem** /liˈsjunpjuːɡem/ [lisˈjumpjuːɣem] *adj.* 'heavy'
- **lisyunpyuugemal** /ˌlisjunˈpjuːɡemal/ [ˌlisjumpˈjuːɣemal] *n.* 'heavyness' ← *lisyunpyuugem*
- **lomopyu** /ˈlomopju/ *n.* 'egg' — PL: lomopyumi; GEN: lomopyun
- **lu** /lu/ *v.i.* 'to swell' — PST: lupu
- **luiiu** /ˈluiːu/ *n.* 'cloud' — PL: luiiumi; GEN: luiiun
- **luqbye** /ˈluŋbje/ *v.i.* 'to spit' — PST: luqbyepu
- **ma** /ma/ *v.t.* 'to suck' — PST: mapu
- **mapu** /ˈmapu/ [ˈmaβu] *v.i.* 'to fly' — PST: mapupu
- **mauu** /ˈmauː/ *adj.* 'warm'
- **mauual** /ˈmauːal/ *n.* 'warmness' ← *mauu*
- **mauudhi** /ˈmauːði/ *v.* 'to become warm' ← *mauu*
- **mauuul** /ˈmauːul/ *v.* 'to make warm' ← *mauu*
- **me** /me/ *v.t.* 'know' — PST: mepu
- **mempyi** /ˈmempji/ *n.* 'fat' — PL: mempyimi; GEN: mempyin
- **mempyiwe** /ˈmempjiwe/ *adj.* 'full of fat' ← *mempyi*
- **metumon** /ˈmetumon/ [ˈmeðumon] *n.* 'skin' — PL: metumonmi; GEN: metumon
- **mi** /mi/ *quant.* 'many'
- **miaa** /ˈmiaː/ *adj.* 'thin'
- **mom** /mom/ *v.t.* 'to wipe' — PST: mompu
- **mor** /mor/ *n.* 'ice' — PL: mormi; GEN: mon
- **muku** /ˈmuku/ [ˈmuɣu] *adj.* 'wide'
- **mukual** /ˈmukual/ [ˈmuɣual] *n.* 'wideness' ← *muku*
- **muku·ul** /ˈmukuul/ [ˈmuɣuul] *v.* 'to make wide' ← *muku*
- **mum** /mum/ *n.* 'rope' — PL: mummi; GEN: mun
- **na** /na/ *v.t.* 'to pull' — PST: napu
- **naxi** /ˈnaʃi/ *n.* 'sea' — PL: naximi; GEN: naxin
- **neel** /ˈneel/ *n.* 'ash' — PL: neelmi; GEN: neen
- **niq** /niŋ/ *v.t.* 'to say' — PST: niqpu
- **nu** /nu/ *adj.* 'good'
- **nual** /ˈnual/ *n.* 'goodness' ← *nu*
- **nudhi** /ˈnuði/ *v.* 'to become good' ← *nu*
- **nyorabi** /ˈɲorabi/ [ˈɲoraβi] *v.t.* 'to smell' — PST: nyorabipu
- **nyu** /ɲu/ *n.* 'star' — PL: nyumi; GEN: nyun
- **nyuulqiwa** /ˈɲuːlŋiwa/ *n.* 'mother' — PL: nyuulqiwami; GEN: nyuulqiwan
- **o** /o/ *n.* 'husband' — PL: omi; GEN: on
- **ogwu** /ˈoɡwu/ *num.* 'two'
- **oka** /ˈoka/ [ˈoɣa] *v.i.* 'to sing' — PST: okapu
- **okago** /ˈokaɡo/ [ˈoɣaɣo] *n.* 'act of singing' ← *oka*
- **okawa** /ˈokawa/ [ˈoɣawa] *n.* 'one who sings' ← *oka*
- **om** /om/ *v.t.* 'to kill' — PST: ompu
- **omwa** /ˈomwa/ *n.* 'one who kills' ← *om*
- **oqla** /ˈoŋla/ *v.t.* 'to push' — PST: oqlapu
- **ozwuu** /ˈozwuː/ *n.* 'woman' — PL: ozwuumi; GEN: ozwuun
- **pa** /pa/ *v.i.* 'to play' — PST: papu
- **pago** /ˈpaɡo/ [ˈpaɣo] *n.* 'act of playing' ← *pa*
- **pam** /pam/ *quant.* 'some'
- **pan** /pan/ *interr.* 'where?'
- **pawa** /ˈpawa/ *n.* 'one who plays' ← *pa*
- **pepu** /ˈpepu/ [ˈpeβu] *adj.* 'rotten'
- **peryo** /ˈperjo/ *v.i.* 'to float' — PST: peryopu
- **phunyqo** /ˈpʰuɲŋo/ *n.* 'river' — PL: phunyqomi; GEN: phunyqon
- **pior** /ˈpior/ *n.* 'snake' — PL: piormi; GEN: pion
- **plaa** /plaː/ *n.* 'dog' — PL: plaami; GEN: plaan
- **pliqoto** /ˈpliŋoto/ [ˈpliŋoðo] *v.t.* 'to count' — PST: pliqotopu
- **ponpyel** /ˈponpjel/ [ˈpompjel] *n.* 'back' — PL: ponpyelmi; GEN: ponpyen
- **porkyu** /ˈporkju/ *n.* 'mouth' — PL: porkyumi; GEN: porkyun
- **praasye** /ˈpraːsje/ *n.* 'man' — PL: praasyemi; GEN: praasyen
- **prusyi·im** /ˈprusjiim/ *n.* 'animal' — PL: prusyi·immi; GEN: prusyi·in
- **pruzwi** /ˈpruzwi/ *v.t.* 'to tie' — PST: pruzwipu
- **puqkyeny** /ˈpuŋkjeɲ/ *n.* 'year' — PL: puqkyenymi; GEN: puqkyen
- **pur** /pur/ *n.* 'sky' — PL: purmi; GEN: pun
- **puunbi** /ˈpuːnbi/ [ˈpuːmbi] *adj.* 'cold'
- **puunbial** /ˈpuːnbial/ [ˈpuːmbial] *n.* 'coldness' ← *puunbi*
- **puunbidhi** /ˈpuːnbiði/ [ˈpuːmbiði] *v.* 'to become cold' ← *puunbi*
- **puunbiul** /ˈpuːnbiul/ [ˈpuːmbiul] *v.* 'to make cold' ← *puunbi*
- **puutusyewar** /puːˈtusjewar/ [puːˈðusjewar] *v.i.* 'to freeze' — PST: puutusyewarpu
- **pyam** /pjam/ *n.* 'fly' — PL: pyammi; GEN: pyan
- **pyilna** /ˈpjilna/ *adj.* 'yellow'
- **pyo** /pjo/ *v.i.* 'to walk' — PST: pyopu
- **pyogo** /ˈpjoɡo/ [ˈpjoɣo] *n.* 'act of walking' ← *pyo*
- **pyu** /pju/ *interr.* 'when?'
- **qaakye** /ˈŋaːkje/ *adj.* 'old'
- **qaakyeal** /ˈŋaːkjeal/ *n.* 'oldness' ← *qaakye*
- **qaakyedhi** /ˈŋaːkjeði/ *v.* 'to become old' ← *qaakye*
- **qaalu** /ˈŋaːlu/ *v.i.* 'to burn' — PST: qaalupu
- **qaxu** /ˈŋaʃu/ *n.* 'tail' — PL: qaxumi; GEN: qaxun
- **qerwe** /ˈŋerwe/ *n.* 'feather' — PL: qerwemi; GEN: qerwen
- **qiyisyaq** /ˈŋijisjaŋ/ *n.* 'navel' — PL: qiyisyaqmi; GEN: qiyisyan
- **qulsya** /ˈŋulsja/ *adj.* 'right'
- **qurlal** /ˈŋurlal/ *n.* 'day' — PL: qurlalmi; GEN: qurlan
- **quutyoq** /ˈŋuːtjoŋ/ *n.* 'sand' — PL: quutyoqmi; GEN: quutyon
- **quutyoqwe** /ŋuːˈtjoŋwe/ *adj.* 'full of sand' ← *quutyoq*
- **re** /re/ *n.* 'smoke' — PL: remi; GEN: ren
- **req** /reŋ/ *v.t.* 'to hold' — PST: reqpu
- **sa** /sa/ *pron.* 'they'
- **sal** /sal/ *n.* 'leaf' — PL: salmi; GEN: san
- **sany** /saɲ/ *interr.* 'who?'
- **seqklun** /ˈseŋklun/ *adj.* 'sharp'
- **seqklunal** /ˈseŋklunal/ *n.* 'sharpness' ← *seqklun*
- **seqklunul** /ˈseŋklunul/ *v.* 'to make sharp' ← *seqklun*
- **siwado** /ˈsiwado/ [ˈsiwaðo] *n.* 'arm/hand' — PL: siwadomi; GEN: siwadon
- **sonyxĩ** /ˈsoɲʃĩ/ *v.t.* 'to take' — PST: sonyxĩpu
- **sraugleny** /ˈsrauɡleɲ/ *n.* 'mountain' — PL: srauglenymi; GEN: srauglen
- **sre** /sre/ *v.t.* 'to throw' — PST: srepu
- **syike** /ˈsjike/ [ˈsjiɣe] *n.* 'father' — PL: syikemi; GEN: syiken
- **ta** /ta/ *adj.* 'wet'
- **tadhi** /ˈtaði/ *v.* 'to become wet' ← *ta*
- **taito** /ˈtaito/ [ˈtaiðo] *v.i.* 'to lie' — PST: taitopu
- **tao** /ˈtao/ *n.* 'knee' — PL: taomi; GEN: taon
- **taul** /ˈtaul/ *v.* 'to make wet' ← *ta*
- **tiblĩ** /ˈtiblĩ/ *v.i.* 'to cry/weep' — PST: tiblĩpu
- **tiblĩgo** /ˈtiblĩɡo/ [ˈtiblĩɣo] *n.* 'act of crying' ← *tiblĩ*
- **toxu** /ˈtoʃu/ *n.* 'dust' — PL: toxumi; GEN: toxun
- **toxuwe** /ˈtoʃuwe/ *adj.* 'full of dust' ← *toxu*
- **truqdebaany** /ˈtruŋdebaːɲ/ [ˈtruŋdeβaːɲ] *n.* 'bark' — PL: truqdebaanymi; GEN: truqdebaan
- **tugoraq** /ˈtuɡoraŋ/ [ˈtuɣoraŋ] *v.t.* 'to scratch' — PST: tugoraqpu
- **tuquulno** /tuˈŋuːlno/ *adj.* 'bitter'
- **tusany** /ˈtusaɲ/ *v.i.* 'to stand' — PST: tusanypu
- **twa** /twa/ *interr.* 'what?'
- **twaa** /twaː/ *adj.* 'big'
- **twaaal** /ˈtwaːal/ *n.* 'bigness' ← *twaa*
- **twaadhi** /ˈtwaːði/ *v.* 'to become big' ← *twaa*
- **twaaul** /ˈtwaːul/ *v.* 'to make big' ← *twaa*
- **twim** /twim/ *v.i.* 'to turn' — PST: twimpu
- **twisi** /ˈtwisi/ *adj.* 'sweet'
- **twu** /twu/ *dem.* 'this'
- **twukuu** /ˈtwukuː/ [ˈtwuɣuː] *n.* 'fish' — PL: twukuumi; GEN: twukuun
- **tya** /tja/ *n.* 'breast' — PL: tyami; GEN: tyan
- **tyal** /tjal/ *num.* 'five'
- **tyati** /ˈtjati/ [ˈtjaði] *n.* 'belly' — PL: tyatimi; GEN: tyatin
- **tyati** /ˈtjati/ [ˈtjaði] *n.* 'guts' — PL: tyatimi; GEN: tyatin = mesma palavra que belly
- **tye** /tje/ *adv.* 'there'
- **tyim** /tjim/ *n.* 'salt' — PL: tyimmi; GEN: tyin
- **tyimwe** /ˈtjimwe/ *adj.* 'full of salt' ← *tyim*
- **tyulĩ** /ˈtjulĩ/ *n.* 'seed' — PL: tyulĩmi; GEN: tyulĩn
- **tyuni** /ˈtjuni/ *v.t.* 'to hide' — PST: tyunipu
- **tyuny** /tjuɲ/ *adv.* 'yesterday'
- **tyuui** /ˈtjuːi/ *n.* 'wind' — PL: tyuuimi; GEN: tyuuin
- **u** /u/ *pron.* '3sg pronoun'
- **u** /u/ *pron.* 'he'
- **ukwu** /ˈukwu/ *v.t.* 'to see' — PST: ukwupu
- **ukwuwa** /ˈukwuwa/ *n.* 'one who sees' ← *ukwu*
- **um** /um/ *v.t.* 'to carry' — PST: umpu
- **unkyam** /ˈunkjam/ *adj.* 'dull'
- **unu** /ˈunu/ *adj.* 'straight'
- **unual** /ˈunual/ *n.* 'straightness' ← *unu*
- **unu·ul** /ˈunuul/ *v.* 'to make straight' ← *unu*
- **upru** /ˈupru/ *v.t.* 'to hear' — PST: uprupu
- **upyon** /ˈupjon/ *n.* 'soil' — PL: upyonmi; GEN: upyon
- **uwobye** /ˈuwobje/ *v.t.* 'to squeeze' — PST: uwobyepu
- **waosyun** /ˈwaosjun/ *n.* 'head' — PL: waosyunmi; GEN: waosyun
- **wiirkraabyi** /ˈwiːrkraːbji/ *n.* 'flower' — PL: wiirkraabyimi; GEN: wiirkraabyin
- **wiqa** /ˈwiŋa/ *n.* 'leg' — PL: wiqami; GEN: wiqan
- **wĩ** /wĩ/ *pron.* 'we'
- **wur** /wur/ *v.t.* 'to fear' — PST: wurpu
- **wuu** /wuː/ *v.t.* 'to wash' — PST: wuupu
- **xiltii** /ˈʃiltiː/ *v.t.* 'to stab' — PST: xiltiipu
- **xodyuuqtu** /ʃoˈdjuːŋtu/ *adj.* 'correct (right)'
- **xunyqoqpilmii** /ˌʃuɲŋoŋˈpilmiː/ *adj.* 'thick'
- **xwaamqinsipo** /ʃwaːmˈŋinsipo/ [ʃwaːmˈŋinsiβo] *n.* 'woods' — PL: xwaamqinsipomi; GEN: xwaamqinsipon
- **xwirprii** /ˈʃwirpriː/ *v.i.* 'to fight' — PST: xwirpriipu
- **xwirpriigo** /ˈʃwirpriːɡo/ [ˈʃwirpriːɣo] *n.* 'act of fighting' ← *xwirprii*
- **xwirpriiwa** /ˈʃwirpriːwa/ *n.* 'one who fights' ← *xwirprii*
- **ya** /ja/ *quant.* 'other'
- **yake** /ˈjake/ [ˈjaɣe] *v.i.* 'to laugh' — PST: yakepu
- **yakego** /ˈjakeɡo/ [ˈjaɣeɣo] *n.* 'act of laughing' ← *yake*
- **yapil** /ˈjapil/ [ˈjaβil] *v.i.* 'to come' — PST: yapilpu
- **yi** /ji/ *v.i.* 'to live' — PST: yipu
- **yii** /jiː/ *v.t.* 'to sew' — PST: yiipu
- **yiiwa** /ˈjiːwa/ *n.* 'one who sews' ← *yii*
- **yin** /jin/ *adj.* 'far'
- **yinpliqkupaal** /jinˈpliŋkupaːl/ [jimpˈliŋkuβaːl] *v.t.* 'to cut' — PST: yinpliqkupaalpu
- **yiqpisil** /ˈjiŋpisil/ *n.* 'bird' — PL: yiqpisilmi; GEN: yiqpisin
- **yir** /jir/ *adv.* 'here'
- **yirlĩ** /ˈjirlĩ/ *v.bitr.* 'to give' — PST: yirlĩpu
- **yu** /ju/ *n.* 'neck' — PL: yumi; GEN: yun
- **yulqam** /ˈjulŋam/ *num.* 'three'
- **ze** /ze/ *num.* 'four'
- **zi** /zi/ *n.* 'wing' — PL: zimi; GEN: zin
- **zo** /zo/ *conj.* 'if'
- **zwin** /zwin/ *n.* 'lake' — PL: zwinmi; GEN: zwin
- **zyi** /zji/ *n.* 'bone' — PL: zyimi; GEN: zyin

Expressos sem palavra própria: 'in' → caso locative; 'at' → caso locative; 'with (accompanying)' → caso instrumental

## Nomes próprios

- Nomes sem marca de gênero
- Sobrenomes: nome do pai + sufixo patronímico (-am)
- Sufixo de povoado: -la /-la/

### Pessoas

| Nome | Pronúncia | Significado | Sobrenome |
|---|---|---|---|
| **Nui Azemam** | /ˈnui/ | good stone | child of Azem |
| **Nowo Liyoam** | /ˈnowo/ | — | child of Liyo |
| **Miyum Neduam** | /ˈmijum/ | — | child of Nedu |
| **Ayaamqem Yinyeam** | /aˈjaːmŋem/ | — | child of Yinye |
| **Twisikyony Qaakyetwukuuam** | /ˈtwisikjoɲ/ | sweet snow | child of Qaakyetwukuu |
| **Elogi Seqkluniam** | /ˈeloɡi/ | — | child of Seqkluni |
| **Niwum Woneam** | /ˈniwum/ | — | child of Wone |
| **Ayii Dyuuqerweam** | /ˈajiː/ | — | child of Dyuuqerwe |
| **Nuri Wiiriimam** | /ˈnuri/ | — | child of Wiiriim |
| **Huumal Qiiwuam** | /ˈhuːmal/ | — | child of Qiiwu |
| **Konkaplaa Nupioram** | /ˈkonkaplaː/ | long dog | child of Nupior |
| **Nuqerwe Umuyeam** | /nuˈŋerwe/ | good feather | child of Umuye |
| **Berphunyqo Mauuqerweam** | /berˈpʰuɲŋo/ | hard river | child of Mauuqerwe |
| **Kronaxi Nilepaqam** | /ˈkronaʃi/ | new sea | child of Nilepaq |
| **Anim Iwiiqam** | /ˈanim/ | — | child of Iwiiq |
| **Ipanii Yomuuam** | /ˈipaniː/ | — | child of Yomuu |
| **Aru Puqĩnyanam** | /ˈaru/ | — | child of Puqĩnyan |
| **Qiwim Qeqiam** | /ˈŋiwim/ | — | child of Qeqi |
| **Uniyum Dyuunaxiam** | /ˈunijum/ | — | child of Dyuunaxi |
| **Omitil Nyoya·am** | /ˈomitil/ | — | child of Nyoya |

### Lugares

| Nome | Pronúncia | Tipo | Significado |
|---|---|---|---|
| **Mukuzwin** | /ˈmukuzwin/ | composto | wide lake |
| **Danla** | /ˈdanla/ | povoado | grass-town |
| **Mowĩ** | /ˈmowĩ/ | antigo (sem significado) | — |
| **Kiinaxi** | /ˈkiːnaʃi/ | composto | sun sea |
| **I Konka** | /i ˈkonka/ | sintagma | long stone |
| **Phunyqo Mauu** | /ˈpʰuɲŋo ˈmauː/ | sintagma | warm river |
| **Dyuuzwin** | /ˈdjuːzwin/ | composto | white lake |
| **Huzyeun** | /ˈhuzjeun/ | locativo | at the road |
| **Lewaa** | /ˈlewaː/ | antigo (sem significado) | — |
| **Bidan** | /ˈbidan/ | composto | narrow grass |
| **Aquu** | /ˈaŋuː/ | antigo (sem significado) | — |
| **Kyonyquutyoq** | /ˈkjoɲŋuːtjoŋ/ | composto | snow sand |
| **Nyula** | /ˈɲula/ | povoado | star-town |
| **Plaazwin** | /ˈplaːzwin/ | composto | dog lake |
| **Zwin Iizreq** | /zwin ˈiːzreŋ/ | sintagma | black lake |
| **Morla** | /ˈmorla/ | povoado | ice-town |
| **Upyonun** | /ˈupjonun/ | locativo | at the soil |
| **Kyonyla** | /ˈkjoɲla/ | povoado | snow-town |
| **Mori** | /ˈmori/ | composto | ice stone |
| **Kiila** | /ˈkiːla/ | povoado | sun-town |

## Validação

- Fonemas fora do inventário: nenhum
- Formas que o sândi não reparou: 0
- Grafias que não podem ser lidas de volta: 0
- Avisos dos módulos:
  - Fonotática: encontros no ataque: obstruinte+líquida/glide
  - Fonotática: perfil de coda: sonorants
