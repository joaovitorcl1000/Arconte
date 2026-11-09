# Kwunytwun

Pasta: `languages/teste31-natural-1000/`

Nome nativo: **kwunytwu** /ˈkwuɲtwu/ (literalmente 'person')

Semente: `31` — gere de novo, a partir de `conlang/`, com `python generate_language/generate_language.py --seed 31`

A mesma semente com os mesmos dados (PHOIBLE, WALS e listas de conceitos) gera sempre a mesma língua.

## Fonologia

### Consoantes (22)

|  | Labial | Coronal | Palatal | Velar | Labiovelar | Laríngea |
|---|---|---|---|---|---|---|
| Oclusiva | b p pʰ | d t |  | k kʰ ɡ |  |  |
| Fricativa |  | s z ð ʃ θ |  |  |  | h |
| Nasal | m | n | ɲ | ŋ |  |  |
| Rótica |  | r |  |  |  |  |
| Lateral |  | l |  |  |  |  |
| Aproximante |  |  | j |  | w |  |

### Vogais (9)

|  | Anterior | Central | Posterior |
|---|---|---|---|
| Alta | i iː ĩ |  | u uː |
| Média | e |  | o |
| Baixa |  | a aː |  |

### Estrutura silábica

- Complexidade: **moderate** (forced)
- Moldes: CV (50%), CCV (17%), CVC (11%), V (10%), CCVC (7%), VC (4%), CCCVC (0%), CCCV (0%)
- Ataque opcional; hiato permitido
- Encontros no ataque (46): bj bl br dj dr dw jj kj kl kr kw lw mj ml nj nl nr pj pl pr rj sj sr sw tj tr tw wj zj zr zw ðj ðr ðw ŋr ŋw ɡj ɡl ɡr ɡw …
- Codas: b d j k l m n p r s t w ŋ ɡ ɲ

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
| **l** | /l/ |
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
- Exemplos: /ˈbuiː/, /ˈsjenka/, /ˈlapjiŋ/, /ˈŋumkjĩ/, /ˈjabil/, /ˈzjempja/

### Mudanças sonoras

3 regras, aplicadas em ordem; 30 de 228 palavras mudaram. A forma do dicionário fica entre barras /.../, e a pronúncia depois das mudanças, entre colchetes [...].

Sons novos criados pelas mudanças: [ɣ] [β]

| # | Regra | Origem | Palavras afetadas | Exemplo |
|---|---|---|---|---|
| 1 | `{b,d,ɡ} > {β,ð,ɣ} / V_V` | natural | 5 | *yabil* /jabil/ → [ˈjaβil] 'name' |
| | espirantização entre vogais (como no espanhol: lado [laðo]) | | | |
| 2 | `e > i / _#` | natural | 10 | *e* /e/ → [i] 'blood' |
| | elevação de vogal final (e > i, como no português: leite [lejt͡ʃi]) | | | |
| 3 | `o > u / _#` | natural | 15 | *po* /po/ → [pu] 'nose' |
| | elevação de vogal final (o > u, como no português: leite [lejt͡ʃi]) | | | |


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
- Posse inalienável (partes do corpo e parentes) marcada no próprio nome; nos demais, a marca vai no classificador de posse me

### Possessivos

| Pessoa | Possessivo | Pronúncia | Plural |
|---|---|---|---|
| 1SG ('my dog') | **mek syun** | /mek sjun/ | **mek syunmi** |
| 2SG ('your dog') | **meoy syun** | /ˈmeoj sjun/ | **meoy syunmi** |
| 3SG ('his/her/its dog') | **meip syun** | /ˈmeip sjun/ | **meip syunmi** |
| 1INCL.PAUC ('our (incl.) (paucal) dog') | **mep syun** | /mep sjun/ | **mep syunmi** |
| 1EXCL.PAUC ('our (excl.) (paucal) dog') | **meki syun** | /ˈmeki sjun/ | **meki syunmi** |
| 2PAUC ('your (paucal) dog') | **mesu syun** | /ˈmesu sjun/ | **mesu syunmi** |
| 3PAUC ('their (paucal) dog') | **meiy syun** | /ˈmeij sjun/ | **meiy syunmi** |
| 1INCL.PL ('our (incl.) dog') | **mepuu syun** | /ˈmepuː sjun/ | **mepuu syunmi** |
| 1EXCL.PL ('our (excl.) dog') | **meti syun** | /ˈmeti sjun/ | **meti syunmi** |
| 2PL ('your (pl.) dog') | **mei syun** | /ˈmei sjun/ | **mei syunmi** |
| 3PL ('their dog') | **mete syun** | /ˈmete sjun/ | **mete syunmi** |

### Alienabilidade

- **krek** /krek/ — 'my hand' (inalienable)
- **mek syun** /mek sjun/ — 'my dog' (alienable)

### Posse entre nomes

- **tyun syun** /tjun sjun/ — 'the woman's dog'

## Comparação

- Comparativo: locativa (o termo comparado vai num caso ou adposição de origem/lugar)
- Termo comparado no caso ablative
- Grau comparativo no adjetivo: -wi
- Superlativo: afixo -il
- Equativo: partícula ('como') kep

### Formas do adjetivo

| Grau | Forma | Pronúncia |
|---|---|---|
| Positivo | **yaap** | /jaːp/ |
| Comparativo | **yaapwi** | /ˈjaːpwi/ |
| Superlativo | **yaapil** | /ˈjaːpil/ |

### Comparativo

**Syun bibu yaapwi.**

```
syun  bibu      yaapwi
sjun  bi-bu     jaːp-wi
dog   fish-ABL  big-COMPR
'The dog is bigger than the fish.'
```

### Superlativo

**Syun yaapil.**

```
syun  yaapil
sjun  jaːp-il
dog   big-SUPL
'The dog is the biggest.'
```

### Equativo

**Syun bi kep yaap.**

```
syun  bi    kep  yaap
sjun  bi    kep  jaːp
dog   fish  as   big
'The dog is as big as the fish.'
```

## Derivação

8 processos produtivos; 96 palavras derivadas (o léxico base tem 231).

| Processo | Forma | Classe | Exemplo |
|---|---|---|---|
| agentivo ('quem faz') | composição com *kwunytwu* ('person') | v. → n. | *iq* → **iqkwunytwu** 'hunter' |
| ação ('o ato de') | sufixo -go | v. → n. | *upyon* → **upyongo** 'meal' |
| qualidade ('-eza', '-idade') | sufixo -yi | adj. → n. | *bun* → **bun·yi** 'goodness' |
| incoativo ('ficar ...') | sufixo -ad | adj. → v. | *upru* → **upruad** 'to age' |
| factitivo ('tornar ...') | sufixo -zi (depois de consoante: -izi) | adj. → v. | *yaap* → **yaapizi** 'to enlarge' |
| proprietivo ('cheio de', '-oso') | sufixo -uy | n. → adj. | *qim* → **qimuy** 'stony' |
| tendência ('-ão', 'brigão') | sufixo -we | v. → adj. | *banuuny* → **banuunywe** 'cheerful' |
| produto do verbo ('o que se faz') | sufixo -so (depois de consoante: -iso) | v. → n. | *ĩp* → **ĩpiso** 'garment' |


## Irregularidades

2 palavras irregulares, todas entre as mais frequentes da língua; 8 alternâncias criadas pelas mudanças sonoras.

### Palavras irregulares

| Palavra | Tipo | Forma | Regular seria | Irregular |
|---|---|---|---|---|
| 'go' (verbo) | apofonia | go-PST | ~~syenkapu~~ | **syenko** /ˈsjenko/ |
| 'person' (nome) | plural zero | person-PL | ~~kwunytwumi~~ | **kwunytwu** /ˈkwuɲtwu/ |

### Alternâncias das mudanças sonoras

As regras de mudança sonora atingem o radical em uma forma e não na outra:

- 'nose': SG *po* /po/ [pu] · PL *pomi* /pomi/ [pomi]
- 'blood': SG *e* /e/ [i] · PL *emi* /emi/ [emi]
- 'breast': SG *he* /he/ [hi] · PL *hemi* /hemi/ [hemi]
- 'fly': SG *o* /o/ [u] · PL *omi* /omi/ [omi]
- 'say': PRS *yo* /jo/ [ju] · PST *yopu* /jopu/ [jopu]
- 'drink': PRS *lo* /lo/ [lu] · PST *lopu* /lopu/ [lopu]
- 'stand': PRS *gro* /ɡro/ [ɡru] · PST *gropu* /ɡropu/ [ɡropu]
- 'run': PRS *byaae* /bjaːe/ [bjaːi] · PST *byaaepu* /bjaːepu/ [bjaːepu]

## Sistema numeral

- Base: decimal (base 10)
- Ordem: multiplicador antes da base ('três-dez' = 30); menor antes ('sete-e-trinta', como no alemão)
- Numerais compostos em palavras separadas, ligados por *do* ('e')
- Ordinais: 'primeiro' ou 'um-ésimo'; os demais derivados

### Numerais

| Número | Numeral | Pronúncia | Composição |
|---|---|---|---|
| 1 | **tyaa** | /tjaː/ | 1 |
| 2 | **ul** | /ul/ | 2 |
| 3 | **xwe** | /ʃwe/ | 3 |
| 4 | **qo** | /ŋo/ | 4 |
| 5 | **syebyaa** | /ˈsjebjaː/ | 5 |
| 6 | **sre** | /sre/ | 6 |
| 7 | **sra** | /sra/ | 7 |
| 8 | **mo** | /mo/ | 8 |
| 9 | **du** | /du/ | 9 |
| 10 | **i** | /i/ | 10 |
| 11 | **tyaa do i** | /tjaː do i/ | 1 + 10 |
| 12 | **ul do i** | /ul do i/ | 2 + 10 |
| 13 | **xwe do i** | /ʃwe do i/ | 3 + 10 |
| 14 | **qo do i** | /ŋo do i/ | 4 + 10 |
| 15 | **syebyaa do i** | /ˈsjebjaː do i/ | 5 + 10 |
| 16 | **sre do i** | /sre do i/ | 6 + 10 |
| 17 | **sra do i** | /sra do i/ | 7 + 10 |
| 18 | **mo do i** | /mo do i/ | 8 + 10 |
| 19 | **du do i** | /du do i/ | 9 + 10 |
| 20 | **ul i** | /ul i/ | 2×10 |
| 30 | **xwe i** | /ʃwe i/ | 3×10 |
| 37 | **sra do xwe i** | /sra do ʃwe i/ | 7 + 3×10 |
| 40 | **qo i** | /ŋo i/ | 4×10 |
| 50 | **syebyaa i** | /ˈsjebjaː i/ | 5×10 |
| 60 | **sre i** | /sre i/ | 6×10 |
| 80 | **mo i** | /mo i/ | 8×10 |
| 90 | **du i** | /du i/ | 9×10 |
| 99 | **du do du i** | /du do du i/ | 9 + 9×10 |
| 100 | **bak** | /bak/ | 100 |
| 256 | **sre do syebyaa i do ul bak** | /sre do ˈsjebjaː i do ul bak/ | 6 + 5×10 + 2×100 |
| 1000 | **okyal** | /ˈokjal/ | 1000 |

### Ordinais

| Número | Ordinal | Pronúncia |
|---|---|---|
| 1º | **konla** | /ˈkonla/ |
| 2º | **ulu** | /ˈulu/ |
| 3º | **xweu** | /ˈʃweu/ |
| 4º | **qou** | /ˈŋou/ |
| 5º | **syebyaau** | /ˈsjebjaːu/ |

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

**Am kwip.**

```
am     kwip
child  sleep
'The child sleeps.'
```

### 2. Oração transitiva

**Tyul bi alqo.**

```
tjul   bi    alŋo
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

**Tyul amka bi maam.**

```
tjul   amka       bi    maːm
tjul   am-ka      bi    maːm
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

**Syunmi yaap ul ar klaam.**

```
sjunmi   jaːp  ul   ar    klaːm
sjun-mi  jaːp  ul   ar    klaːm
dog-PL   big   two  this  come
'These two big dogs come.'
```

### 7. Posse (genitivo)

**Tyun syun kwip.**

```
tjun       sjun  kwip
tjul-n     sjun  kwip
woman-GEN  dog   sleep
'The woman's dog sleeps.'
```

### 8. Adjunto locativo

**Am gwaaqumun kwip.**

```
am     ɡwaːŋumun   kwip
am     ɡwaːŋum-un  kwip
child  house-LOC   sleep
'The child sleeps in the house.'
```

### 9. Predicado adjetival (cópula zero)

**Bi yaap.**

```
bi    jaːp
fish  big
'The fish is big.'
```

### 10. Negação

**Am kwipgu.**

```
am     kwipɡu
am     kwip-ɡu
child  sleep-NEG
'The child does not sleep.'
```

### 11. Pergunta sim/não

**Tyul bi alqo tyum.**

```
tjul   bi    alŋo  tjum
woman  fish  see   Q
'Does the woman see the fish?'
```

### 12. Pergunta de conteúdo (palavra interrogativa no início)

**Klu tyul alqo.**

```
klu   tjul   alŋo
what  woman  see
'What does the woman see?'
```

## Orações

- Passiva: sufixo -y; agente no caso instrumental
- Reflexivo: afixo op
- Recíproco: afixo t
- Demonstrativos: 2 graus de distância
- Imperativo: afixo ap
- Proibitivo: partícula própria kyin
- Subordinação: subordinador no fim da subordinada; complementizador yyuy ('que')

### Demonstrativos

| Distância | Demonstrativo | Advérbio |
|---|---|---|
| perto de quem fala | **ar** 'this' | **pyi** 'here' |
| longe | **gye** 'that' | **ulam** 'there' |

### Possessivos independentes

| Pessoa | Forma |
|---|---|
| 1SG | **pruuk** |
| 2SG | **pruuoy** |
| 3SG | **pruuip** |
| 1INCL.PAUC | **pruup** |
| 1EXCL.PAUC | **pruuki** |
| 2PAUC | **pruusu** |
| 3PAUC | **pruuiy** |
| 1INCL.PL | **pruupuu** |
| 1EXCL.PL | **pruuti** |
| 2PL | **pruui** |
| 3PL | **pruute** |

### Conectivos e adposições

| Palavra | Forma |
|---|---|
| 'or' | **lwew** |
| 'but' | **tiim** |
| 'if' | **om** |
| 'because' | **pru** |
| 'when' | **kya** |
| 'and' | **do** |
| 'under' | **dhipri** |
| 'above' | **yeq** |
| 'inside' | **agaa** |
| 'behind' | **na·a** |
| 'in front of' | **swunak** |
| 'near' | **wia** |

### Passiva

**Bi syunni upyoy.**

```
bi    sjunni   upjoj
bi    sjun-ni  upjon-j
fish  dog-INS  eat-PASS
'The fish is eaten by the dog.'
```

### Reflexivo

**Tyul dyapyaop.**

```
tjul   djapjaop
tjul   djapja-op
woman  wash-REFL
'The woman washes herself.'
```

### Recíproco

**Syunmi alqot.**

```
sjunmi   alŋot
sjun-mi  alŋo-t
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

**Syun gye.**

```
sjun  ɡje
dog   DEM.DIST
'that dog'
```

### Imperativo

**Klaamap.**

```
klaːmap
klaːm-ap
come-IMP
'Come!'
```

### Proibitivo

**Bi kyin upyonap.**

```
bi    kjin  upjonap
bi    kjin  upjon-ap
fish  PROH  eat-IMP
'Don't eat the fish!'
```

### Coordenação ('e')

**Syun kwip do am bi upyon.**

```
sjun  kwip   do   am     bi    upjon
dog   sleep  and  child  fish  eat
'The dog sleeps and the child eats the fish.'
```

### Coordenação ('mas')

**Syun kwip tiim am bi upyon.**

```
sjun  kwip   tiːm  am     bi    upjon
dog   sleep  but   child  fish  eat
'The dog sleeps, but the child eats the fish.'
```

### Condicional ('se')

**Syun kwip om am bi upyon.**

```
sjun  kwip   om  am     bi    upjon
dog   sleep  if  child  fish  eat
'If the dog sleeps, the child eats the fish.'
```

### Causal ('porque')

**Syun kwip pru am bi upyon.**

```
sjun  kwip   pru      am     bi    upjon
dog   sleep  because  child  fish  eat
'The child eats the fish because the dog sleeps.'
```

### Completiva ('que')

**Ka syun kwip yyuy mu.**

```
ka   sjun  kwip   jjuj  mu
1SG  dog   sleep  COMP  know
'I know that the dog sleeps.'
```

### Possessivo independente

**Syun pruuk.**

```
sjun  pruːk
sjun  pruː-k
dog   1SG.POSS
'The dog is mine.'
```

### Adposição espacial

**Syun syimdyilun dhipri kwip.**

```
sjun  sjimdjilun   ðipri  kwip
sjun  sjimdjil-un  ðipri  kwip
dog   tree-LOC     under  sleep
'The dog sleeps under the tree.'
```

## Dicionário

231 entradas, lista `all` do Concepticon, mais 96 palavras derivadas, 1533 do vocabulário ampliado (WOLD), 7 numerais.

Formato: **grafia** /pronúncia/ [pronúncia depois das mudanças sonoras, quando muda] classe 'significado' ← base, nas derivadas

- **a** /a/ *n.* 'father' — PL: ami; GEN: an — substituiu uma palavra antiga
- **aa** /aː/ *n.* 'brush'
- **aabiswe** /ˈaːbiswe/ *part.* 'never'
- **aaluu** /ˈaːluː/ *v.* 'destroy'
- **aaluuso** /ˈaːluːso/ *v.* 'damage' ← *aaluu* (produto)
- **aambram** /ˈaːmbram/ *n.* 'hair' — PL: aambrammi; GEN: aambran
- **aamlo** /ˈaːmlo/ *part.* 'in'
- **aanmi** /ˈaːnmi/ *n.* 'navel' — PL: aanmimi; GEN: aanmin — substituiu uma palavra antiga
- **aan·yuqo** /ˈaːnjuŋo/ *n.* 'porpoise'
- **aap** /aːp/ *n.* 'idol'
- **aaqe** /ˈaːŋe/ *n.* 'mast'
- **aauy** /ˈaːuj/ *n.* 'garden-house'
- **ablu** /ˈablu/ *n.* 'country'
- **abo** /ˈabo/ *v.* 'deceive'
- **abyo** /ˈabjo/ *v.* 'sting'
- **adhe** /ˈaðe/ *v.* 'put'
- **adwa** /ˈadwa/ *v.* 'like'
- **aew** /ˈaew/ *n.* 'ladder'
- **agaa** /ˈaɡaː/ *part.* 'inside'
- **agiqwi** /ˈaɡiŋwi/ *n.* 'earwax'
- **agwusqa** /aˈɡwusŋa/ *n.* 'father's brother' = *a* + *gwusqa*
- **aip** /ˈaip/ *v.* 'sharpen'
- **aiu** /ˈaiu/ *part.* 'up'
- **ak** /ak/ *v.i.* 'to fall' — PST: akpu — substituiu uma palavra antiga
- **akha** /ˈakʰa/ *n.* 'neighbour'
- **aklĩn** /ˈaklĩn/ *adj.* 'alone'
- **aku** /ˈaku/ *n.* 'beam'
- **akyuptwe** /aˈkjuptwe/ *adj.* 'grey'
- **ala** /ˈala/ *n.* 'muroid (mouse or rat)'
- **alga** /ˈalɡa/ *v.t.* 'to dig' — PST: algapu
- **algakwunytwu** /ˌalɡaˈkwuɲtwu/ *n.* 'digger' ← *alga*
- **algaso** /ˈalɡaso/ [ˈalɡasu] *n.* 'hole' ← *alga*
- **alo** /ˈalo/ *n.* 'death'
- **alqo** /ˈalŋo/ [ˈalŋu] *v.t.* 'to see' — PST: alqopu
- **alqokwunytwu** /ˌalŋoˈkwuɲtwu/ *n.* 'witness' ← *alqo* (agentivo)
- **am** /am/ *n.* 'child (young human)' — PL: ammi; GEN: an
- **am** /am/ *adj.* 'wet'
- **ama** /ˈama/ *n.* 'father's sister' = *a* + *ma*
- **amad** /ˈamad/ *v.* 'to become wet' ← *am*
- **amiruny** /ˈamiruɲ/ *n.* 'flavour'
- **amizi** /ˈamizi/ *v.* 'to make wet' ← *am*
- **amkhan** /ˈamkʰan/ *v.* 'trade'
- **amu** /ˈamu/ *n.* 'camp'
- **an** /an/ *pron.* 'ye'
- **ana** /ˈana/ *n.* 'December'
- **angyi** /ˈanɡji/ *v.i.* 'to play' — PST: angyipu
- **angyigo** /ˈanɡjiɡo/ [ˈanɡjiɣu] *n.* 'act of playing' ← *angyi*
- **angyikwunytwu** /ˌanɡjiˈkwuɲtwu/ *n.* 'player' ← *angyi*
- **aniyi** /ˈaniji/ *v.* 'succeed'
- **ao** /ˈao/ *v.* 'dash'
- **apo** /ˈapo/ *v.* 'blow'
- **apwyom** /ˈapwjom/ *v.* 'dry up'
- **aqkheny** /ˈaŋkʰeɲ/ *n.* 'liver' — PL: aqkhenymi; GEN: aqkhen — substituiu uma palavra antiga
- **aqnu** /ˈaŋnu/ *n.* 'sausage'
- **aqtesu** /ˈaŋtesu/ *adv.* 'so'
- **aqu** /ˈaŋu/ *n.* 'lagoon'
- **ar** /ar/ *dem.* 'this'
- **ashĩ** /ˈashĩ/ *n.* 'face'
- **asyĩp** /ˈasjĩp/ *n.* 'lead (chemical element)'
- **atru** /ˈatru/ *part.* 'breathe, breath'
- **aup** /ˈaup/ *n.* 'dish'
- **awii** /ˈawiː/ *n.* 'chain'
- **awu** /ˈawu/ *v.* 'lay'
- **ay** /aj/ *n.* 'spirit'
- **ayilaa** /ˈajilaː/ *v.* 'hinder, prevent'
- **aymi** /ˈajmi/ *n.* 'flowing body of water'
- **aysi** /ˈajsi/ *v.* 'twist'
- **ayutret** /ˈajutret/ *v.* 'bore'
- **ayyedu** /ˈajjedu/ *adj.* 'light (weight)'
- **azala** /ˈazala/ *n.* 'laughter'
- **a·aki** /ˈaaki/ *adj.* 'holy'
- **ba** /ba/ *n.* 'udder'
- **baa** /baː/ *v.* 'earn'
- **baaanwi** /baːˈanwi/ *n.* 'board'
- **baamtaa** /ˈbaːmtaː/ *v.* 'sparkle, twinkle'
- **baawma** /ˈbaːwma/ *n.* 'grandchild'
- **baayimad** /ˈbaːjimad/ *n.* 'sound or noise'
- **babnywogu** /ˈbabɲwoɡu/ *n.* 'gate'
- **bak** /bak/ *num.* 'hundred'
- **bakloq** /ˈbakloŋ/ *n.* 'tail' — PL: bakloqmi; GEN: baklon
- **bakra** /ˈbakra/ *n.* 'jaguar'
- **bam** /bam/ *n.* 'parrot'
- **bamiimi** /ˈbamiːmi/ *v.* 'endure'
- **bamtrizruw** /ˈbamtrizruw/ *adv.* 'then'
- **bantwa** /ˈbantwa/ *n.* 'ash' — PL: bantwami; GEN: bantwan
- **banuuny** /ˈbanuːɲ/ *v.i.* 'to laugh' — PST: banuunypu
- **banuunygo** /baˈnuːɲɡo/ [baˈnuːɲɡu] *n.* 'laughter' ← *banuuny*
- **banuunywe** /ˈbanuːɲwe/ [ˈbanuːɲwi] *adj.* 'cheerful' ← *banuuny*
- **bas** /bas/ *part.* 'which?'
- **bayi** /ˈbaji/ *n.* 'nasal mucus'
- **bayplua** /ˈbajplua/ *v.* 'gather'
- **be** /be/ *n.* 'week'
- **bebyi** /ˈbebji/ *adj.* 'warm'
- **bel** /bel/ *n.* 'soil' — PL: belmi; GEN: ben — substituiu uma palavra antiga
- **beposi** /ˈbeposi/ *v.* 'knead'
- **bi** /bi/ *n.* 'fish' — PL: bimi; GEN: bin
- **biboway** /ˈbibowaj/ *n.* 'fish trap' = *bi* + *boway*
- **bii** /biː/ *adj.* 'raw'
- **bikwunytwu** /biˈkwuɲtwu/ *n.* 'fisherman' = *bi* + *kwunytwu*
- **bilod** /ˈbilod/ *n.* 'enemy'
- **bim** /bim/ *n.* 'rabbit'
- **biqaayka** /biˈŋaːjka/ *n.* 'battle-axe'
- **biqninii** /ˈbiŋniniː/ *v.* 'snap'
- **biuhutwo** /biˈuhutwo/ *n.* 'fishhook' = *bi* + *uhutwo*
- **biwido** /ˈbiwido/ *n.* 'fish poison' = *bi* + *wido*
- **biwumii** /ˈbiwumiː/ *n.* 'glue'
- **biyiraam** /ˈbijiraːm/ *adj.* 'different'
- **bizrutyu** /ˈbizrutju/ *n.* 'fishnet' = *bi* + *zrutyu*
- **bĩg** /bĩɡ/ *n.* 'bill'
- **bla** /bla/ *v.* 'scrape'
- **blaakwwu** /ˈblaːkwwu/ *v.* 'carve'
- **blaszua** /ˈblaszua/ *v.* 'condemn'
- **bli** /bli/ *adj.* 'high'
- **blin·yaluu** /ˈblinjaluː/ *n.* 'high tide' = *bli* + *n·yaluu*
- **blĩo** /ˈblĩo/ [ˈblĩu] *n.* 'bark' — PL: blĩomi; GEN: blĩon
- **blony** /bloɲ/ *interr.* 'where?' — substituiu uma palavra antiga
- **bluna** /ˈbluna/ *n.* 'midday'
- **bluuswii** /ˈbluːswiː/ *v.* 'herd'
- **bo** /bo/ *v.* 'plough'
- **boi** /ˈboi/ *v.* 'howl'
- **bokrap** /ˈbokrap/ *n.* 'post'
- **bome** /ˈbome/ *n.* 'claw'
- **bomno** /ˈbomno/ *adj.* 'fragrant'
- **bomya** /ˈbomja/ *v.* 'move'
- **bosaa** /ˈbosaː/ *n.* 'sap'
- **boway** /ˈbowaj/ *n.* 'trap (pitfall)'
- **boyi** /ˈboji/ *n.* 'twins'
- **bozo** /ˈbozo/ *adj.* 'pointed'
- **brihi** /ˈbrihi/ *adj.* 'drunk'
- **bruup** /bruːp/ *n.* 'charcoal'
- **bu** /bu/ *n.* 'lunch'
- **bubo** /ˈbubo/ *n.* 'steam'
- **bubyu** /ˈbubju/ *n.* 'noble'
- **bud** /bud/ *n.* 'anchor'
- **buii** /ˈbuiː/ *n.* 'fire' — PL: buiimi; GEN: buiin
- **buiio** /ˈbuiːo/ *n.* 'firefly' = *buii* + *o*
- **buiiuy** /ˈbuiːuj/ *adj.* 'fiery' ← *buii*
- **buke** /ˈbuke/ *n.* 'shark'
- **bukio** /ˈbukio/ *n.* 'soldier'
- **bukiqu** /ˈbukiŋu/ *adj.* 'nasty, dire'
- **bumlop** /ˈbumlop/ *n.* 'opossum'
- **bumta** /ˈbumta/ *n.* 'arctic lights'
- **bun** /bun/ *adj.* 'good'
- **bun·yi** /ˈbunji/ *n.* 'goodness' ← *bun*
- **buseya** /ˈbuseja/ *v.* 'hope (something)'
- **buu** /buː/ *n.* 'fortress'
- **buud** /buːd/ *n.* 'grape'
- **buuwtya** /ˈbuːwtja/ *n.* 'heat'
- **buxyos** /ˈbuʃjos/ *adj.* 'ready'
- **buyiizi** /ˈbujiːzi/ *n.* 'waist'
- **byaae** /ˈbjaːe/ [ˈbjaːi] *v.i.* 'to run' — PST: byaaepu
- **byaaego** /ˈbjaːeɡo/ [ˈbjaːeɣu] *n.* 'result of running' ← *byaae*
- **byaaekwunytwu** /ˌbjaːeˈkwuɲtwu/ *n.* 'runner' ← *byaae*
- **byaaewe** /ˈbjaːewe/ [ˈbjaːewi] *adj.* 'tending to run' ← *byaae*
- **byaku** /ˈbjaku/ *n.* 'chin'
- **byama** /ˈbjama/ *n.* 'tax'
- **byeqromi** /ˈbjeŋromi/ *n.* 'church'
- **byetwazuu** /ˈbjetwazuː/ *part.* 'last (final)'
- **byii** /bjiː/ *n.* 'dove'
- **byiin** /bjiːn/ *adv.* 'yesterday'
- **byobuup** /ˈbjobuːp/ *n.* 'widower'
- **byuker** /ˈbjuker/ *n.* 'valley'
- **byweip** /ˈbjweip/ *n.* 'beaver'
- **bywetwi** /ˈbjwetwi/ *n.* 'berry' — PL: bywetwimi; GEN: bywetwin
- **byyezyi** /ˈbjjezji/ *v.i.* 'to blow' — PST: byyezyipu
- **byyiib** /bjjiːb/ *n.* 'tobacco'
- **byyuti** /ˈbjjuti/ *adj.* 'secret'
- **co** /θo/ *n.* 'sickle'
- **cuumukii** /ˈθuːmukiː/ *n.* 'oats'
- **cuur** /θuːr/ *v.i.* 'to swell' — PST: cuurpu
- **cuuriso** /ˈθuːriso/ *n.* 'swelling' ← *cuur* (produto)
- **cyahise** /ˈθjahise/ *n.* 'flea'
- **cyaniin** /ˈθjaniːn/ *n.* 'quail'
- **da** /da/ *n.* 'pasture'
- **daaktuprim** /ˈdaːktuprim/ *n.* 'razor'
- **daetra** /ˈdaetra/ *n.* 'weapons'
- **dagyu** /ˈdaɡju/ *n.* 'collar'
- **damuu** /ˈdamuː/ *n.* 'strength'
- **danotuu** /ˈdanotuː/ *n.* 'hammock'
- **dape** /ˈdape/ *n.* 'bracelet'
- **dasaglyaa** /ˈdasaɡljaː/ *n.* 'finger'
- **dawi** /ˈdawi/ *n.* 'doubt'
- **de** /de/ *n.* 'area'
- **denup** /ˈdenup/ *n.* 'moor'
- **dersei** /ˈdersei/ *adj.* 'tired'
- **dhiiyu** /ˈðiːju/ *v.* 'visible'
- **dhipri** /ˈðipri/ *part.* 'under'
- **dhunyasyin** /ˈðuɲasjin/ *n.* 'firewood'
- **dhwibtegi** /ˈðwibteɡi/ *adv.* 'together'
- **dhye** /ðje/ *n.* 'common cold (disease)'
- **dhyil** /ðjil/ *n.* 'fat' — PL: dhyilmi; GEN: dhyin
- **dhyiluy** /ˈðjiluj/ *adj.* 'full of fat' ← *dhyil*
- **di** /di/ *n.* 'pine'
- **dibyyusye** /ˈdibjjusje/ *v.* 'yawn'
- **dii** /diː/ *n.* 'relatives'
- **diiwupla** /ˈdiːwupla/ *n.* 'stepson'
- **dik** /dik/ *v.* 'bake'
- **dila** /ˈdila/ *n.* 'limb'
- **dimyaqki** /diˈmjaŋki/ *n.* 'campfire'
- **diw** /diw/ *v.* 'shoot'
- **diwuklĩ** /ˈdiwuklĩ/ *n.* 'quiet, silence'
- **dizaalbu** /diˈzaːlbu/ *v.* 'spoil'
- **dizu** /ˈdizu/ *n.* 'game'
- **dĩ** /dĩ/ *n.* 'king'
- **do** /do/ [du] *conj.* 'and' — substituiu uma palavra antiga
- **dobi** /ˈdobi/ *v.* 'stream'
- **dotopu** /ˈdotopu/ *n.* 'hen'
- **downyi** /ˈdowɲi/ *v.* 'work (activity)'
- **doyi** /ˈdoji/ *adj.* 'broken'
- **drai** /ˈdrai/ *n.* 'vagina'
- **draqnrensuu** /draŋˈnrensuː/ *n.* 'circumcision'
- **dri** /dri/ *v.* 'weigh'
- **drout** /ˈdrout/ *n.* 'divorce'
- **dru** /dru/ *v.* 'light (ignite)'
- **drunzaa** /ˈdrunzaː/ *n.* 'hole'
- **du** /du/ *num.* 'nine'
- **dubo** /ˈdubo/ *n.* 'omen'
- **duketyu** /ˈduketju/ *v.* 'call by name'
- **dunyawa** /ˈduɲawa/ *adj.* 'proud'
- **duublel** /ˈduːblel/ *n.* 'master'
- **duuwpi** /ˈduːwpi/ *adj.* 'ugly'
- **dwa** /dwa/ *n.* 'glove'
- **dwaqi** /ˈdwaŋi/ *v.* 'obey'
- **dwar** /dwar/ *n.* 'quarrel'
- **dwaya** /ˈdwaja/ *n.* 'guard'
- **dwi** /dwi/ *v.* 'convict'
- **dwimui** /ˈdwimui/ *n.* 'ground'
- **dwiny** /dwiɲ/ *v.t.* 'to pull' — PST: dwinypu
- **dwitkyu** /ˈdwitkju/ *n.* 'paddy'
- **dwo** /dwo/ *adj.* 'fresh'
- **dya** /dja/ *n.* 'puzzle'
- **dyanykyil** /ˈdjaɲkjil/ *adj.* 'rough'
- **dyapya** /ˈdjapja/ *v.t.* 'to wash' — PST: dyapyapu
- **dyapyakwunytwu** /ˌdjapjaˈkwuɲtwu/ *n.* 'thing that washes' ← *dyapya*
- **dyeluu** /ˈdjeluː/ *n.* 'army'
- **dyi** /dji/ *n.* 'girl'
- **dyinu** /ˈdjinu/ *n.* 'stepmother'
- **dyirgwu** /ˈdjirɡwu/ *adj.* 'stupid'
- **dyiszi** /ˈdjiszi/ *n.* 'gums'
- **dyiyna** /ˈdjijna/ *n.* 'rug'
- **dyonu** /ˈdjonu/ *n.* 'spider'
- **dyu** /dju/ *adj.* 'yellow'
- **dyun** /djun/ *n.* 'river' — PL: dyunmi; GEN: dyun — substituiu uma palavra antiga
- **dyu·u·u** /ˈdjuuu/ *v.* 'explain'
- **e** /e/ [i] *n.* 'blood' — PL: emi; GEN: en
- **ebno** /ˈebno/ *v.* 'pinch'
- **ehubyyak** /ˈehubjjak/ *n.* 'doorpost'
- **ei** /ˈei/ *v.* 'sail'
- **ekbeye** /ˈekbeje/ *n.* 'birch'
- **ekirko** /eˈkirko/ *n.* 'yard'
- **ekomxi** /eˈkomʃi/ *part.* 'yes'
- **ekya** /ˈekja/ *n.* 'dress'
- **em** /em/ *v.i.* 'to turn' — PST: empu
- **emnyuu** /ˈemɲuː/ *n.* 'bean'
- **emumu** /ˈemumu/ *n.* 'beeswax'
- **en** /en/ *n.* 'companion'
- **endan·yu** /ˈendanju/ *v.t.* 'to crush/grind' — PST: endan·yupu
- **endan·yuso** /enˈdanjuso/ [enˈdanjusu] *n.* 'flour' ← *endan·yu*
- **entu** /ˈentu/ *n.* 'towel'
- **eny** /eɲ/ *part.* 'with'
- **enyweyu** /ˈeɲweju/ *adj.* 'dense'
- **eosyu** /ˈeosju/ *adv.* 'hardly'
- **epyyaa** /ˈepjjaː/ *v.* 'choose'
- **eq** /eŋ/ *n.* 'larch'
- **eqonywe** /ˈeŋoɲwe/ *v.* 'let'
- **eqonywesyenka** /eˌŋoɲweˈsjenka/ *v.* 'let go' = *eqonywe* + *syenka*
- **esenbyyag** /eˈsenbjjaɡ/ *adv.* 'very'
- **esgabim** /ˈesɡabim/ *n.* 'spindle'
- **eso** /ˈeso/ *n.* 'spade'
- **etaa** /ˈetaː/ *v.* 'extinguish'
- **etaqii** /ˈetaŋiː/ *n.* 'shirt'
- **etopĩ** /ˈetopĩ/ *part.* 'nothing'
- **ewiwi** /ˈewiwi/ *v.* 'join'
- **eyi** /ˈeji/ *n.* 'fence'
- **ga** /ɡa/ *adj.* 'empty'
- **gak** /ɡak/ *n.* 'god'
- **gako** /ˈɡako/ *part.* 'early'
- **gamuru** /ˈɡamuru/ *n.* 'elevation'
- **ganiaak** /ˈɡaniaːk/ *v.* 'acquit'
- **gaqe** /ˈɡaŋe/ *adv.* 'suddenly'
- **gaswemla** /ˈɡaswemla/ *v.* 'rot'
- **ge** /ɡe/ [ɡi] *interr.* 'who?'
- **geki** /ˈɡeki/ *n.* 'merchant'
- **gemli** /ˈɡemli/ *n.* 'aunt'
- **geny** /ɡeɲ/ *interr.* 'how'
- **gi** /ɡi/ *n.* 'floor'
- **giat** /ˈɡiat/ *adj.* 'brackish'
- **giguyyi** /ˈɡiɡujji/ *n.* 'July'
- **gii** /ɡiː/ *v.* 'flee'
- **gimikwa** /ˈɡimikwa/ *n.* 'thing'
- **gini** /ˈɡini/ *v.* 'leave'
- **ginlum** /ˈɡinlum/ *adj.* 'warm'
- **ginlumad** /ˈɡinlumad/ *v.* 'to warm up' ← *ginlum*
- **ginlumizi** /ɡiˈnlumizi/ *v.* 'to heat' ← *ginlum*
- **ginlumyi** /ˈɡinlumji/ *n.* 'warmth' ← *ginlum*
- **giqwu** /ˈɡiŋwu/ *n.* 'hair (head)'
- **gitinygu** /ɡiˈtiɲɡu/ *adj.* 'calm'
- **gityinkuy** /ɡiˈtjinkuj/ *n.* 'deity'
- **gĩ** /ɡĩ/ *v.* 'admit'
- **gla** /ɡla/ *v.i.* 'sit' — PST: glapu
- **glamlii** /ˈɡlamliː/ *v.* 'sit down' = *gla* + *mlii*
- **glany** /ɡlaɲ/ *v.i.* 'to freeze' — PST: glanypu
- **glen** /ɡlen/ *n.* 'speech'
- **glĩlbyi** /ˈɡlĩlbji/ *n.* 'fireplace'
- **glukglupo** /ˈɡlukɡlupo/ *n.* 'bolt of lightning'
- **glyenygyo** /ˈɡljeɲɡjo/ [ˈɡljeɲɡju] *adj.* 'straight'
- **glyerqobraa** /ˈɡljerŋobraː/ *n.* 'armour'
- **glyumo** /ˈɡljumo/ *v.* 'marry'
- **glyumogo** /ˈɡljumoɡo/ *n.* 'wedding' ← *glyumo* (ação)
- **godu** /ˈɡodu/ *v.* 'suspect'
- **gorti** /ˈɡorti/ *v.* 'groan'
- **gotak** /ˈɡotak/ *n.* 'weight'
- **graal** /ɡraːl/ *v.* 'swallow'
- **grinyĩn·yiq** /ˈɡriɲĩnjiŋ/ *n.* 'cuckoo'
- **griwuuaa** /ˈɡriwuːaː/ *n.* 'mother-in-law (of woman)'
- **gro** /ɡro/ [ɡru] *v.i.* 'to stand' — PST: gropu
- **groaiu** /ɡroˈaiu/ *v.* 'stand up' = *gro* + *aiu*
- **gruun·yamkis** /ɡruːˈnjamkis/ *n.* 'colour'
- **gu** /ɡu/ *neg.* 'not' — expresso por afixo verbal
- **gukatwu** /ˈɡukatwu/ *v.* 'hiccough'
- **gukuso** /ˈɡukuso/ *n.* 'ring'
- **gun·yua** /ˈɡunjua/ *n.* 'manner'
- **guony** /ˈɡuoɲ/ *v.t.* 'to scratch' — PST: guonypu
- **gupyi** /ˈɡupji/ *v.* 'cultivate'
- **gusii** /ˈɡusiː/ *n.* 'idea'
- **guua** /ˈɡuːa/ *v.t.* 'to hear' — PST: guuapu
- **guuwyawi** /ˈɡuːwjawi/ *v.* 'swear'
- **guuxe** /ˈɡuːʃe/ *n.* 'cotton'
- **gwa** /ɡwa/ *n.* 'grass' — PL: gwami; GEN: gwan
- **gwaaqum** /ˈɡwaːŋum/ *n.* 'house' — PL: gwaaqummi; GEN: gwaaqun
- **gwagu** /ˈɡwaɡu/ *n.* 'space'
- **gwaqmi** /ˈɡwaŋmi/ *v.i.* 'to think' — PST: gwaqmipu
- **gwaqmikwunytwu** /ˌɡwaŋmiˈkwuɲtwu/ *n.* 'one who thinks' ← *gwaqmi*
- **gwaqmiso** /ˈɡwaŋmiso/ [ˈɡwaŋmisu] *n.* 'what is thought' ← *gwaqmi*
- **gwauy** /ˈɡwauj/ *adj.* 'full of grass' ← *gwa*
- **gwewqwubaa** /ˈɡwewŋwubaː/ *n.* 'bruise'
- **gwi** /ɡwi/ *n.* 'mortar binder'
- **gwiny** /ɡwiɲ/ *pron.* '2sg pronoun'
- **gwiwon** /ˈɡwiwon/ *n.* 'flour'
- **gwoymuu** /ˈɡwojmuː/ *n.* 'weather'
- **gwoynowu** /ˈɡwojnowu/ *n.* 'axle'
- **gwu** /ɡwu/ *v.* 'follow'
- **gwuaha** /ˈɡwuaha/ *v.* 'hide (conceal)'
- **gwuklu** /ˈɡwuklu/ *adj.* 'aged, old'
- **gwulpa** /ˈɡwulpa/ *n.* 'money'
- **gwusqa** /ˈɡwusŋa/ *n.* 'brother'
- **gwuu** /ɡwuː/ *n.* 'end (of space)'
- **gye** /ɡje/ [ɡji] *dem.* 'that' — substituiu uma palavra antiga
- **gyimi** /ˈɡjimi/ *n.* 'lasso'
- **gyisewre** /ɡjiˈsewre/ *n.* 'meadow'
- **gyishiitwed** /ˈɡjishiːtwed/ *adj.* 'female (of animal)'
- **gyuk** /ɡjuk/ *n.* 'yoke'
- **gyungyolok** /ˈɡjunɡjolok/ *v.* 'liberate'
- **gyuud** /ɡjuːd/ *adj.* 'heavy' — substituiu uma palavra antiga
- **gyuudad** /ˈɡjuːdad/ [ˈɡjuːðad] *v.* 'to become heavy' ← *gyuud*
- **gyuuyka** /ˈɡjuːjka/ *v.* 'break (cleave)'
- **gyuw** /ɡjuw/ *n.* 'road' — PL: gyuwmi; GEN: gyun
- **gyuy** /ɡjuj/ *part.* 'same'
- **ha** /ha/ *n.* 'mosquito'
- **haa** /haː/ *n.* 'tree stump'
- **haawu** /ˈhaːwu/ *v.* 'disappear'
- **hadqa** /ˈhadŋa/ *n.* 'itch'
- **hagag** /ˈhaɡaɡ/ *v.* 'show'
- **haluuxwu** /ˈhaluːʃwu/ *v.* 'get dressed'
- **hamewe** /ˈhamewe/ *n.* 'tip'
- **hamlo** /ˈhamlo/ *n.* 'air'
- **hamyin** /ˈhamjin/ *n.* 'embers'
- **haus** /ˈhaus/ *n.* 'throat'
- **hawpoi** /ˈhawpoi/ *v.* 'retreat'
- **he** /he/ [hi] *n.* 'breast' — PL: hemi; GEN: hen
- **hi** /hi/ *n.* 'wave'
- **hia** /ˈhia/ *part.* 'through'
- **hii** /hiː/ *v.* 'feed'
- **hip** /hip/ *v.* 'drag'
- **hitu** /ˈhitu/ *n.* 'room'
- **hĩqapyaaq** /ˈhĩŋapjaːŋ/ *n.* 'bad luck'
- **ho** /ho/ *adj.* 'calm (of sea)'
- **hogi** /ˈhoɡi/ *n.* 'barley'
- **hoi** /ˈhoi/ *n.* 'ship'
- **homaap** /ˈhomaːp/ *v.* 'forge'
- **horya** /ˈhorja/ *n.* 'pot, cooking vessel'
- **houm** /ˈhoum/ *adj.* 'true'
- **hoxwuu** /ˈhoʃwuː/ *n.* 'vulture'
- **hu** /hu/ *n.* 'heel'
- **hudyi** /ˈhudji/ *n.* 'wife' — PL: hudyimi; GEN: hudyin
- **hukait** /ˈhukait/ *v.* 'forbid'
- **huu** /huː/ *n.* 'outrigger'
- **huwu** /ˈhuwu/ *v.* 'invite'
- **huxĩrgi** /huˈʃĩrɡi/ *n.* 'beard'
- **i** /i/ *num.* 'ten'
- **iaa** /ˈiaː/ *n.* 'home'
- **iaai** /ˈiaːi/ *adj.* 'faithful'
- **iaqu** /ˈiaŋu/ *n.* 'tower'
- **ibi** /ˈibi/ *n.* 'dandruff'
- **igaalo** /ˈiɡaːlo/ *n.* 'disease'
- **ihi** /ˈihi/ *v.* 'fan (action)'
- **ii** /iː/ *part.* 'tomorrow'
- **iiam** /ˈiːam/ *n.* 'flesh/meat' — PL: iiammi; GEN: iian
- **iibnum** /ˈiːbnum/ *part.* 'seventy'
- **iibpamiin** /ˈiːbpamiːn/ *n.* 'axe'
- **iidgya** /ˈiːdɡja/ *n.* 'gold'
- **iigum** /ˈiːɡum/ [ˈiːɣum] *v.t.* 'to smell' — PST: iigumpu
- **iigumuy** /ˈiːɡumuj/ *adj.* 'stinking' ← *iigum* (proprietivo)
- **iii** /ˈiːi/ *v.* 'happen'
- **iikop** /ˈiːkop/ *n.* 'price'
- **iilgowse** /iːlˈɡowse/ *n.* 'chili pepper'
- **iiltye** /ˈiːltje/ *n.* 'chameleon'
- **iimya** /ˈiːmja/ *v.i.* 'to flow' — PST: iimyapu
- **iinnyaa** /ˈiːnɲaː/ *n.* 'mother-in-law (of man)'
- **iiq** /iːŋ/ *n.* 'egg' — PL: iiqmi; GEN: iin
- **iirpuphu** /ˈiːrpupʰu/ *n.* 'lip'
- **iiti** /ˈiːti/ *part.* 'after'
- **iitumi** /ˈiːtumi/ *v.* 'begin, beginning'
- **iiw** /iːw/ *n.* 'raft'
- **iiwi** /ˈiːwi/ *n.* 'needle tree'
- **iiysiqi** /ˈiːjsiŋi/ *part.* 'she'
- **ikapi** /ˈikapi/ *adj.* 'healthy'
- **ikluu** /ˈikluː/ *adj.* 'left'
- **ikuwyu** /ˈikuwju/ *n.* 'pepper'
- **ima** /ˈima/ *n.* 'whirlpool'
- **inaartu** /iˈnaːrtu/ *n.* 'poet'
- **innya** /ˈinɲa/ *adj.* 'new'
- **innyayi** /ˈinɲaji/ *n.* 'newness' ← *innya*
- **innyazi** /ˈinɲazi/ *v.* 'to make new' ← *innya*
- **inozyii** /ˈinozjiː/ *v.* 'adjudicate'
- **inuzi** /ˈinuzi/ *n.* 'deer'
- **ipaa** /ˈipaː/ *n.* 'string'
- **ipyaa** /ˈipjaː/ *n.* 'peel, husk'
- **ipyag** /ˈipjaɡ/ *v.* 'mould'
- **iq** /iŋ/ *v.t.* 'to hunt' — PST: iqpu
- **iqgyĩpglaa** /iŋˈɡjĩpɡlaː/ *n.* 'fur'
- **iqkuywo** /iŋˈkujwo/ *adv.* 'still'
- **iqkwunytwu** /iŋˈkwuɲtwu/ *n.* 'hunter' ← *iq*
- **iqwe** /ˈiŋwe/ [ˈiŋwi] *adj.* 'tending to hunt' ← *iq*
- **ira** /ˈira/ *adj.* 'innocent'
- **iryi** /ˈirji/ *n.* 'ditch'
- **iryup** /ˈirjup/ *v.* 'beget'
- **is** /is/ *n.* 'carcass'
- **isalu** /ˈisalu/ *v.* 'turn over'
- **isi** /ˈisi/ *v.* 'buy'
- **isigwaaqum** /iˈsiɡwaːŋum/ *n.* 'market' = *isi* + *gwaaqum*
- **iso** /ˈiso/ *n.* 'skull'
- **ita** /ˈita/ *n.* 'boar'
- **ite** /ˈite/ *n.* 'olive'
- **itlo** /ˈitlo/ *v.* 'chat'
- **iuu** /ˈiuː/ *n.* 'spear'
- **iw** /iw/ *n.* 'wheel'
- **iwnaa** /ˈiwnaː/ *v.* 'grow'
- **iwpiyu** /ˈiwpiju/ *adj.* 'sick'
- **iwyo** /ˈiwjo/ *v.* 'bless'
- **ixwugii** /ˈiʃwuɡiː/ *n.* 'autumn'
- **iyanysi** /iˈjaɲsi/ *v.* 'spread out'
- **iyo** /ˈijo/ *n.* 'spleen'
- **iyyiiklu** /ˈijjiːklu/ *n.* 'ribbon'
- **i·i** /ˈii/ *v.* 'rinse'
- **i·ikab** /ˈiikab/ *v.* 'wake'
- **i·ikabaiu** /iˌikaˈbaiu/ *v.* 'wake up' = *i·ikab* + *aiu*
- **ĩ** /ĩ/ *quant.* 'many' — substituiu uma palavra antiga
- **ĩno** /ˈĩno/ *v.* 'cough'
- **ĩn·yo** /ˈĩnjo/ *v.* 'shine'
- **ĩp** /ĩp/ *v.t.* 'to sew' — PST: ĩppu
- **ĩpiso** /ˈĩpiso/ [ˈĩpisu] *n.* 'garment' ← *ĩp*
- **ĩpkwunytwu** /ĩpˈkwuɲtwu/ *n.* 'tailor' ← *ĩp*
- **ĩpkwunytwu** /ĩpˈkwuɲtwu/ *n.* 'tailor' ← *ĩp* (agentivo)
- **ĩpliw** /ˈĩpliw/ *n.* 'violence'
- **ka** /ka/ *pron.* '1sg pronoun'
- **kaa** /kaː/ *v.* 'sell'
- **kaatai** /ˈkaːtai/ *n.* 'beech'
- **kabyii** /ˈkabjiː/ *n.* 'pit'
- **kagowhat** /kaˈɡowhat/ *v.* 'melt'
- **kagrul** /ˈkaɡrul/ *adj.* 'wide'
- **kagrulizi** /kaˈɡrulizi/ *v.* 'to make wide' ← *kagrul*
- **kagrulyi** /kaˈɡrulji/ *n.* 'width' ← *kagrul*
- **kaii** /ˈkaiː/ *v.* 'decay'
- **kamli** /ˈkamli/ *n.* 'meal'
- **kanklo** /ˈkanklo/ *n.* 'trousers'
- **kanre** /ˈkanre/ *n.* 'basket'
- **kapbyyada** /ˈkapbjjada/ *n.* 'grief'
- **katdayci** /katˈdajθi/ *n.* 'eyebrow'
- **kaxi** /ˈkaʃi/ *n.* 'peace'
- **kaykho** /ˈkajkʰo/ *adj.* 'naked'
- **kayowyuuq** /ˈkajowjuːŋ/ *n.* 'prostitute'
- **ke** /ke/ [ki] *n.* 'ear' — PL: kemi; GEN: ken
- **kegiilswu** /keˈɡiːlswu/ *v.* 'smile'
- **kegukuso** /keˈɡukuso/ *n.* 'earring' = *ke* + *gukuso*
- **kehaa** /ˈkehaː/ *v.* 'talk'
- **kek·hanas** /ˈkekhanas/ *n.* 'daughter-in-law (of man)'
- **kenurew** /ˈkenurew/ *n.* 'October'
- **kephii** /ˈkepʰiː/ *v.* 'guess'
- **keuum** /ˈkeuːm/ *n.* 'conversation'
- **kewyiibywob** /ˈkewjiːbjwob/ *adj.* 'blue'
- **keyi** /ˈkeji/ *n.* 'cover, lid'
- **kezwa** /ˈkezwa/ *adj.* 'pregnant'
- **kha** /kʰa/ *n.* 'line'
- **khamnya** /ˈkʰamɲa/ *v.i.* 'to float' — PST: khamnyapu
- **khe** /kʰe/ *v.* 'kneel'
- **khimpu** /ˈkʰimpu/ *v.i.* 'to vomit' — PST: khimpupu
- **khio** /ˈkʰio/ *n.* 'livestock'
- **ki** /ki/ *v.* 'look for'
- **kia** /ˈkia/ *n.* 'coal'
- **kiblo** /ˈkiblo/ *n.* 'item'
- **kigor** /ˈkiɡor/ *n.* 'memory'
- **kihe** /ˈkihe/ *n.* 'coin'
- **kihopa** /ˈkihopa/ *n.* 'boat'
- **kii** /kiː/ *n.* 'blister'
- **kiima** /ˈkiːma/ *n.* 'good luck'
- **kikwig** /ˈkikwiɡ/ *n.* 'lamb'
- **kim** /kim/ *n.* 'water' — PL: kimmi; GEN: kin
- **kimiqme** /kiˈmiŋme/ *n.* 'square'
- **kimuy** /ˈkimuj/ *adj.* 'watery' ← *kim*
- **kin** /kin/ *n.* 'toucan'
- **kinykyii** /ˈkiɲkjiː/ *v.t.* 'to carry' — PST: kinykyiipu
- **kio** /ˈkio/ *v.* 'creep'
- **kip** /kip/ *v.* 'catch'
- **kipa** /ˈkipa/ *v.* 'bend (something)'
- **kipkwunytwu** /kipˈkwuɲtwu/ *n.* 'captive' ← *kip* (agentivo)
- **kiprel** /ˈkiprel/ *n.* 'fig'
- **kipyag** /ˈkipjaɡ/ *v.* 'wrap'
- **kipyi** /ˈkipji/ *n.* 'pus'
- **kipyuuk** /ˈkipjuːk/ *part.* 'thirty'
- **kiralwa** /ˈkiralwa/ *v.* 'sow seeds'
- **kit** /kit/ *v.* 'sink'
- **kitwe** /ˈkitwe/ *n.* 'cow'
- **kiu** /ˈkiu/ *n.* 'wolf'
- **klaam** /klaːm/ *v.i.* 'to come' — PST: klaampu
- **klaamkrai** /ˈklaːmkrai/ *v.* 'come back' = *klaam* + *krai*
- **klamti** /ˈklamti/ *n.* 'calf'
- **kle** /kle/ *n.* 'shoe'
- **klekwunytwu** /kleˈkwuɲtwu/ *n.* 'shoemaker' = *kle* + *kwunytwu*
- **kleyo** /ˈklejo/ *n.* 'whetstone'
- **kli** /kli/ *n.* 'store'
- **kligan** /ˈkliɡan/ [ˈkliɣan] *n.* 'sand' — PL: kliganmi; GEN: kligan
- **kligano** /ˈkliɡano/ *n.* 'sandfly' = *kligan* + *o*
- **kliganuy** /ˈkliɡanuj/ [ˈkliɣanuj] *adj.* 'sandy' ← *kligan*
- **klii** /kliː/ *v.* 'call'
- **kliibywitbug** /kliːˈbjwitbuɡ/ *n.* 'forked branch'
- **kliiso** /ˈkliːso/ *n.* 'kidney'
- **klikoa** /ˈklikoa/ *v.* 'be annoyed'
- **klil** /klil/ *n.* 'place'
- **klinya** /ˈkliɲa/ *n.* 'wrist'
- **kliwsa** /ˈkliwsa/ *n.* 'family'
- **kloya** /ˈkloja/ *n.* 'middle, center'
- **klu** /klu/ *interr.* 'what?' — substituiu uma palavra antiga
- **kluma** /ˈkluma/ *v.* 'cook'
- **klumagwaaqum** /kluˈmaɡwaːŋum/ *n.* 'cookhouse' = *kluma* + *gwaaqum*
- **klumn·yaas** /ˈklumnjaːs/ *v.* 'commend'
- **klununy** /ˈklunuɲ/ *n.* 'worm' — PL: klununymi; GEN: klunun
- **kluqmlip** /ˈkluŋmlip/ *adj.* 'obscure'
- **klusyuneb** /ˈklusjuneb/ *v.* 'remain'
- **ko** /ko/ *v.* 'lick'
- **koa** /ˈkoa/ *n.* 'custom'
- **koĩm** /ˈkoĩm/ *n.* 'sailcloth'
- **konruswag** /ˈkonruswaɡ/ *v.* 'move (oneself)'
- **konwe** /ˈkonwe/ *n.* 'month'
- **kopu** /ˈkopu/ *adv.* 'little'
- **kopuse** /ˈkopuse/ *n.* 'Sunday'
- **kotwo** /ˈkotwo/ *n.* 'coat'
- **kowuhi** /ˈkowuhi/ *n.* 'tool'
- **kra** /kra/ *n.* 'religion'
- **kraalwe** /ˈkraːlwe/ *n.* 'latch'
- **krai** /ˈkrai/ *n.* 'back' — PL: kraimi; GEN: krain
- **krawu** /ˈkrawu/ *adj.* 'rough (of sea)'
- **krel** /krel/ *n.* 'hand' — PL: krelmi; GEN: kren — substituiu uma palavra antiga
- **kritkal** /ˈkritkal/ *part.* 'fifty'
- **kro** /kro/ *n.* 'boomerang'
- **kroryika** /ˈkrorjika/ *n.* 'arch'
- **krubizu** /ˈkrubizu/ *v.* 'snore'
- **krulkwwĩrdi** /krulˈkwwĩrdi/ *n.* 'work (labour)'
- **krusukaas** /ˈkrusukaːs/ *n.* 'mirror'
- **kruu** /kruː/ *v.* 'fishing'
- **ku** /ku/ *v.i.* 'to die' — PST: kupu
- **kudi** /ˈkudi/ *n.* 'bag'
- **kugo** /ˈkuɡo/ [ˈkuɣu] *n.* 'death' ← *ku*
- **kukal** /ˈkukal/ *n.* 'door'
- **kukwik** /ˈkukwik/ *v.* 'stutter'
- **kulno** /ˈkulno/ [ˈkulnu] *n.* 'stick' — PL: kulnomi; GEN: kulnon
- **kuminy** /ˈkumiɲ/ *n.* 'life'
- **kune** /ˈkune/ *n.* 'call (appeal)'
- **kunram** /ˈkunram/ *v.* 'chop (into pieces)'
- **kupilu** /ˈkupilu/ *n.* 'Wednesday'
- **kurit** /ˈkurit/ *n.* 'yam'
- **kurud** /ˈkurud/ *n.* 'harvest'
- **kut** /kut/ *v.* 'sweep'
- **kutadyu** /ˈkutadju/ *v.* 'pile up'
- **kutgimikwa** /kutˈɡimikwa/ *n.* 'broom' = *kut* + *gimikwa*
- **kutmu** /ˈkutmu/ *n.* 'gourd'
- **kuu** /kuː/ *n.* 'stranger'
- **kuuiil** /ˈkuːiːl/ *v.i.* 'to breathe' — PST: kuuiilpu — substituiu uma palavra antiga
- **kuuiilgo** /kuːˈiːlɡo/ [kuːˈiːlɡu] *n.* 'act of breathing' ← *kuuiil*
- **kuunop** /ˈkuːnop/ *adj.* 'mad'
- **kuwiy** /ˈkuwij/ *n.* 'envy'
- **kuyu** /ˈkuju/ *v.* 'budge'
- **kwa** /kwa/ *n.* 'penis'
- **kwaa** /kwaː/ *n.* 'friend'
- **kwalnu** /ˈkwalnu/ *v.* 'roar'
- **kwe** /kwe/ *v.* 'turn out'
- **kwekoyi** /ˈkwekoji/ *n.* 'foal'
- **kwenli** /ˈkwenli/ *v.* 'cheat'
- **kwesil** /ˈkwesil/ *v.t.* 'to hold' — PST: kwesilpu
- **kwi** /kwi/ *n.* 'pitchfork'
- **kwiimyir** /ˈkwiːmjir/ *n.* 'battle'
- **kwip** /kwip/ *v.i.* 'sleep' — PST: kwippu — substituiu uma palavra antiga
- **kwipgo** /ˈkwipɡo/ [ˈkwipɡu] *n.* 'act of sleeping' ← *kwip*
- **kwipgwaaqum** /ˈkwipɡwaːŋum/ *n.* 'bed' = *kwip* + *gwaaqum*
- **kwipwe** /ˈkwipwe/ [ˈkwipwi] *adj.* 'sleepy' ← *kwip*
- **kwiqag** /ˈkwiŋaɡ/ *adj.* 'drowned'
- **kwiruzaa** /ˈkwiruzaː/ *v.* 'connect'
- **kwit** /kwit/ *v.* 'decrease'
- **kwi·ĩp** /ˈkwiĩp/ *n.* 'anvil'
- **kwĩ** /kwĩ/ *adj.* 'clever'
- **kwo** /kwo/ [kwu] *v.t.* 'to split' — PST: kwopu
- **kwokwuwpuu** /kwoˈkwuwpuː/ *n.* 'hour'
- **kwoso** /ˈkwoso/ [ˈkwosu] *n.* 'crack' ← *kwo*
- **kwu** /kwu/ *n.* 'blame'
- **kwunytwu** /ˈkwuɲtwu/ *n.* 'man' — PL: kwunytwumi; GEN: kwunytwun = mesma palavra que person
- **kwunytwu** /ˈkwuɲtwu/ *n.* 'person' — **PL: kwunytwu** (irregular); GEN: kwunytwun
- **kwuotu** /ˈkwuotu/ *part.* 'forty'
- **kwuuo** /ˈkwuːo/ *n.* 'rudder'
- **kwwa** /kwwa/ *n.* 'thunder'
- **kwwerzi** /ˈkwwerzi/ *n.* 'night' — PL: kwwerzimi; GEN: kwwerzin
- **kwwogkwulaa** /ˈkwwoɡkwulaː/ *n.* 'moustache'
- **kya** /kja/ *interr.* 'when?'
- **kyam** /kjam/ *n.* 'ice' — PL: kyammi; GEN: kyan
- **kyauupi** /ˈkjauːpi/ *n.* 'plot'
- **kyawbli** /ˈkjawbli/ *part.* 'at'
- **kyawbliwolu** /kjawˈbliwolu/ *adv.* 'at first' = *kyawbli* + *wolu*
- **kyayqi** /ˈkjajŋi/ *n.* 'side'
- **kye** /kje/ *n.* 'donkey'
- **kyeiwli** /kjeˈiwli/ *adj.* 'strong, mighty, powerful'
- **kyewyaki** /ˈkjewjaki/ *n.* 'September'
- **kyey** /kjej/ *adv.* 'in vain'
- **kyi** /kji/ *n.* 'cheek'
- **kyib** /kjib/ *adj.* 'skilful'
- **kyibyyet** /ˈkjibjjet/ *n.* 'mud'
- **kyiib** /kjiːb/ *v.* 'recognize'
- **kyiloti** /ˈkjiloti/ *n.* 'thought'
- **kyilyu** /ˈkjilju/ *v.* 'steal'
- **kyilyukwunytwu** /ˌkjiljuˈkwuɲtwu/ *n.* 'thief' ← *kyilyu* (agentivo)
- **kyinmiyu** /ˈkjinmiju/ *n.* 'spine'
- **kyogruu** /ˈkjoɡruː/ *n.* 'praise'
- **kyoha** /ˈkjoha/ *n.* 'meat'
- **kyoy** /kjoj/ *n.* 'husband' — PL: kyoymi; GEN: kyon = mesma palavra que male person
- **kyu** /kju/ *n.* 'tongue' — PL: kyumi; GEN: kyun
- **kyukayii** /ˈkjukajiː/ *n.* 'cart'
- **la** /la/ *adj.* 'sharp'
- **laanug** /ˈlaːnuɡ/ *v.* 'stretch'
- **lae** /ˈlae/ *v.* 'find'
- **laed** /ˈlaed/ *adj.* 'cheap'
- **laguu** /ˈlaɡuː/ *n.* 'load'
- **lama** /ˈlama/ *n.* 'chair'
- **laplipe** /ˈlaplipe/ *n.* 'digging stick'
- **lapyiq** /ˈlapjiŋ/ *n.* 'mouth' — PL: lapyiqmi; GEN: lapyin
- **laripya** /ˈlaripja/ *adj.* 'damp'
- **lasu** /ˈlasu/ *v.* 'weave'
- **layi** /ˈlaji/ *n.* 'sharpness' ← *la*
- **layu** /ˈlaju/ *n.* 'nut'
- **lazi** /ˈlazi/ *v.* 'to make sharp' ← *la*
- **le** /le/ *n.* 'felt'
- **lepli** /ˈlepli/ *n.* 'banyan'
- **leq** /leŋ/ *n.* 'blood vessel'
- **lew** /lew/ *adj.* 'small'
- **lewyi** /ˈlewji/ *n.* 'small thing' ← *lew*
- **li** /li/ *n.* 'springtime'
- **libruq** /ˈlibruŋ/ *n.* 'palm tree'
- **liduubi** /ˈliduːbi/ *n.* 'picture'
- **lii** /liː/ *n.* 'nit'
- **liiamle** /ˈliːamle/ *adj.* 'diligent'
- **liikwi** /ˈliːkwi/ *n.* 'wheat'
- **liim** /liːm/ *n.* 'citrus fruit'
- **liimuupre** /ˈliːmuːpre/ *v.* 'fill'
- **liinla·ak** /ˈliːnlaak/ *part.* 'ninety'
- **liipi** /ˈliːpi/ *v.* 'become'
- **lil** /lil/ *v.* 'grasp'
- **lina** /ˈlina/ *n.* 'oar'
- **lipribuuk** /ˈlipribuːk/ *n.* 'crop, harvest'
- **liqwoqnli** /liˈŋwoŋnli/ *n.* 'monkey'
- **lisimo** /ˈlisimo/ *v.* 'begin'
- **lisimogo** /liˈsimoɡo/ *n.* 'beginning' ← *lisimo* (ação)
- **litiisun** /ˈlitiːsun/ *n.* 'butterfly'
- **litĩ** /ˈlitĩ/ *n.* 'chisel'
- **litu** /ˈlitu/ *n.* 'toe'
- **lixe** /ˈliʃe/ *v.* 'disturb'
- **lĩlwimlup** /ˈlĩlwimlup/ *v.* 'forgive'
- **lo** /lo/ [lu] *v.t.* 'to drink' — PST: lopu
- **lod** /lod/ *adj.* 'precious'
- **log** /loɡ/ *n.* 'bird' — PL: logmi; GEN: lon — substituiu uma palavra antiga
- **lohonyi** /ˈlohoɲi/ *n.* 'hut'
- **lom** /lom/ *v.t.* 'to suck' — PST: lompu — substituiu uma palavra antiga
- **lomyapik** /ˈlomjapik/ *n.* 'parents'
- **loukpyo** /loˈukpjo/ *n.* 'wool'
- **lowe** /ˈlowe/ [ˈlowi] *adj.* 'tending to drink' ← *lo*
- **lu** /lu/ *n.* 'root' — PL: lumi; GEN: lun — substituiu uma palavra antiga
- **lube** /ˈlube/ *v.* 'divide'
- **lubreso** /ˈlubreso/ *n.* 'rake'
- **lug** /luɡ/ *v.* 'crawl'
- **lukwip** /ˈlukwip/ *n.* 'mason'
- **luoy** /ˈluoj/ *n.* 'light (radiation)'
- **lupyim** /ˈlupjim/ *adj.* 'smooth'
- **luqĩw** /ˈluŋĩw/ *n.* 'ox'
- **luu** /luː/ *v.* 'carry in hand'
- **luuba** /ˈluːba/ *n.* 'grain'
- **luuk** /luːk/ *n.* 'mule'
- **luwnu** /ˈluwnu/ *n.* 'saucer'
- **luxyu** /ˈluʃju/ *adj.* 'long'
- **luxyuad** /ˈluʃjuad/ *v.* 'to become long' ← *luxyu*
- **luxyuyi** /ˈluʃjuji/ *n.* 'length' ← *luxyu*
- **lu·uy** /ˈluuj/ *adj.* 'full of root' ← *lu*
- **lwabyebe** /ˈlwabjebe/ *v.* 'feel (tactually)'
- **lwagli** /ˈlwaɡli/ *n.* 'Monday'
- **lwanri** /ˈlwanri/ *n.* 'queen'
- **lwaqwo** /ˈlwaŋwo/ *n.* 'need'
- **lwemkru** /ˈlwemkru/ *adj.* 'green'
- **lwew** /lwew/ *part.* 'or'
- **lwewa** /ˈlwewa/ *v.* 'assemble'
- **lwi** /lwi/ *v.* 'jump'
- **lwo** /lwo/ *adj.* 'round'
- **lwownuk** /ˈlwownuk/ *n.* 'waterfall'
- **lwul** /lwul/ *adj.* 'guilty'
- **lwurbaape** /ˈlwurbaːpe/ *v.* 'fold'
- **lwurqe** /ˈlwurŋe/ *v.* 'cast'
- **lwuumzu·uu** /ˈlwuːmzuuː/ *n.* 'matter'
- **ma** /ma/ *n.* 'sister'
- **maa** /maː/ *n.* 'cone'
- **maaba** /ˈmaːba/ *n.* 'acorn'
- **maagiwdra** /maːˈɡiwdra/ *adj.* 'colourful'
- **maam** /maːm/ *v.bitr.* 'to give' — PST: maampu
- **maamkrai** /ˈmaːmkrai/ *v.* 'give back' = *maam* + *krai*
- **maanyaa** /ˈmaːɲaː/ *n.* 'handle'
- **magub** /ˈmaɡub/ *n.* 'crane'
- **magwe** /ˈmaɡwe/ *n.* 'oven'
- **maklure** /ˈmaklure/ *v.* 'borrow'
- **mam** /mam/ *n.* 'neck' — PL: mammi; GEN: man
- **manlobo** /ˈmanlobo/ *n.* 'boy'
- **mao** /ˈmao/ *n.* 'pouch'
- **map·haqwo** /ˈmaphaŋwo/ *v.* 'want'
- **mat** /mat/ *part.* 'zero'
- **mau** /ˈmau/ *v.* 'teach'
- **maukwunytwu** /ˌmauˈkwuɲtwu/ *n.* 'teacher' ← *mau* (agentivo)
- **mawyanyu** /ˈmawjaɲu/ *n.* 'plate'
- **maxyay** /ˈmaʃjaj/ *n.* 'foam'
- **ma·aa** /ˈmaaː/ *v.i.* 'to sing' — PST: ma·aapu
- **ma·aago** /ˈmaaːɡo/ [ˈmaaːɣu] *n.* 'song' ← *ma·aa*
- **ma·aakwunytwu** /ˌmaaːˈkwuɲtwu/ *n.* 'singer' ← *ma·aa*
- **ma·aaso** /ˈmaaːso/ [ˈmaaːsu] *n.* 'what is sung' ← *ma·aa*
- **ma·aawe** /ˈmaaːwe/ [ˈmaaːwi] *adj.* 'tending to sing' ← *ma·aa*
- **me** /me/ *n.* 'temples'
- **meplemlut** /ˈmeplemlut/ *n.* 'ghost'
- **mes** /mes/ *n.* 'kettle'
- **mi** /mi/ *n.* 'nest'
- **mia** /ˈmia/ *n.* 'size'
- **mib** /mib/ *adj.* 'thin' — substituiu uma palavra antiga
- **mie** /ˈmie/ *adv.* 'once (in the past)'
- **mihut** /ˈmihut/ *part.* 'live, living, life'
- **mii** /miː/ *n.* 'orphan'
- **miiil** /ˈmiːil/ *n.* 'paint (pigments)'
- **miiu** /ˈmiːu/ *n.* 'cormorant'
- **miiuu** /ˈmiːuː/ *n.* 'awl'
- **miiwya** /ˈmiːwja/ *n.* 'pan'
- **mikyik** /ˈmikjik/ *n.* 'bowl'
- **mil** /mil/ *part.* 'without'
- **milĩlu** /ˈmilĩlu/ *n.* 'butter'
- **mim** /mim/ *n.* 'corpse'
- **mimkyu** /ˈmimkju/ *n.* 'wood' — PL: mimkyumi; GEN: mimkyun = mesma palavra que tree
- **miplusum** /ˈmiplusum/ *n.* 'soap'
- **miprulu** /ˈmiprulu/ *n.* 'cloak'
- **mipyoq** /ˈmipjoŋ/ *n.* 'thatch'
- **miqtwii** /ˈmiŋtwiː/ *part.* 'day after tomorrow'
- **miqwudwe** /ˈmiŋwudwe/ *v.* 'stop'
- **miri** /ˈmiri/ *n.* 'well'
- **mispo** /ˈmispo/ *n.* 'wall'
- **mita** /ˈmita/ *v.* 'write'
- **mitipyi** /ˈmitipji/ *adj.* 'easy'
- **mitsyaai** /ˈmitsjaːi/ *v.* 'rustle'
- **miuk** /ˈmiuk/ *n.* 'chimney'
- **miy** /mij/ *n.* 'rafter'
- **miyuu** /ˈmijuː/ *n.* 'port'
- **mĩ** /mĩ/ *n.* 'ornament'
- **mĩk** /mĩk/ *v.* 'tumble'
- **mĩtaabes** /ˈmĩtaːbes/ *v.* 'preserve'
- **mla** /mla/ *n.* 'window'
- **mlapa** /ˈmlapa/ *v.* 'pay'
- **mlay** /mlaj/ *n.* 'lizard'
- **mle** /mle/ *n.* 'son-in-law (of man)'
- **mlenkye** /ˈmlenkje/ *n.* 'fin'
- **mli** /mli/ *v.* 'move (affect emotionally)'
- **mlii** /mliː/ *part.* 'down'
- **mliihuu** /ˈmliːhuː/ *n.* 'chill'
- **mlika** /ˈmlika/ *part.* 'why?'
- **mliq** /mliŋ/ *adj.* 'low'
- **mliqn·yaluu** /ˈmliŋnjaluː/ *n.* 'low tide' = *mliq* + *n·yaluu*
- **mlog** /mloɡ/ *v.* 'deny'
- **mloywuqaa** /ˈmlojwuŋaː/ *n.* 'belt'
- **mlu** /mlu/ *adj.* 'soft'
- **mluamqaa** /mluˈamŋaː/ *n.* 'victory'
- **mlumewa** /ˈmlumewa/ *adj.* 'foreign'
- **mluu** /mluː/ *n.* 'middle'
- **mluwkruyyu** /ˈmluwkrujju/ *v.* 'change (become different)'
- **mluyphii** /ˈmlujpʰiː/ *adv.* 'afterwards'
- **mo** /mo/ *num.* 'eight'
- **mobyas** /ˈmobjas/ *v.* 'drive (cattle)'
- **modipu** /ˈmodipu/ *n.* 'beggar'
- **moger** /ˈmoɡer/ *n.* 'kangaroo'
- **molomi** /ˈmolomi/ *n.* 'deceit'
- **molwuwi** /ˈmolwuwi/ *v.* 'smell'
- **momey** /ˈmomej/ *n.* 'fox'
- **moni** /ˈmoni/ *n.* 'whale'
- **monulyu** /moˈnulju/ *n.* 'perjury'
- **mopa** /ˈmopa/ *n.* 'horse'
- **mopikye** /ˈmopikje/ *part.* 'immediately'
- **moprii** /ˈmopriː/ *v.* 'hire'
- **mopyugal** /ˈmopjuɡal/ *n.* 'need, necessity'
- **motu** /ˈmotu/ *v.* 'convey'
- **mu** /mu/ *v.t.* 'know' — PST: mupu — substituiu uma palavra antiga
- **mua** /ˈmua/ *n.* 'rye'
- **mudwyi** /ˈmudwji/ *adj.* 'broken (not working)'
- **muiwtu** /muˈiwtu/ *v.* 'rule'
- **mulep** /ˈmulep/ *n.* 'manioc bread'
- **mulisnre** /muˈlisnre/ *n.* 'kid'
- **muluu** /ˈmuluː/ *adj.* 'flat'
- **mum** /mum/ *v.* 'land (descend)'
- **muma** /ˈmuma/ *n.* 'morning'
- **mumayabwo** /ˌmumaˈjabwo/ *n.* 'breakfast' = *muma* + *yabwo*
- **mumyĩ** /ˈmumjĩ/ *n.* 'clan'
- **munamxa** /muˈnamʃa/ *v.* 'go out'
- **muq** /muŋ/ *part.* 'often'
- **mutwu** /ˈmutwu/ *n.* 'August'
- **muu** /muː/ *v.* 'shriek'
- **muugyir** /ˈmuːɡjir/ *n.* 'fruit'
- **muuo** /ˈmuːo/ *adj.* 'male (of animal)'
- **muup** /muːp/ *v.* 'kick'
- **muuqu** /ˈmuːŋu/ *n.* 'sling'
- **muwudud** /ˈmuwudud/ *n.* 'dirt'
- **mu·u** /ˈmuu/ *n.* 'mead'
- **mya** /mja/ *n.* 'honey'
- **myaa** /mjaː/ *n.* 'jaw'
- **myabriir** /ˈmjabriːr/ *n.* 'paw'
- **myayi** /ˈmjaji/ *adj.* 'former'
- **myebyo** /ˈmjebjo/ *n.* 'willow'
- **myeda** /ˈmjeda/ *n.* 'soul'
- **myekibzaa** /mjeˈkibzaː/ *n.* 'copper'
- **myem** /mjem/ *n.* 'handkerchief'
- **myempyum** /ˈmjempjum/ *n.* 'horn' — PL: myempyummi; GEN: myempyun
- **myenyzyal** /ˈmjeɲzjal/ *v.t.* 'to do/make' — PST: myenyzyalpu — substituiu uma palavra antiga
- **myenyzyaliso** /mjeɲˈzjaliso/ [mjeɲzˈjalisu] *n.* 'deed' ← *myenyzyal*
- **myeyya** /ˈmjejja/ *n.* 'noose'
- **myibyi** /ˈmjibji/ *n.* 'top'
- **myiini** /ˈmjiːni/ *part.* 'today'
- **myikda** /ˈmjikda/ *part.* 'down, below'
- **myinya** /ˈmjiɲa/ *n.* 'iron'
- **myinywarmi** /mjiˈɲwarmi/ *n.* 'magic'
- **myiplos** /ˈmjiplos/ *n.* 'citizen'
- **myiquu** /ˈmjiŋuː/ *adj.* 'clear'
- **myi·ib** /ˈmjiib/ *v.* 'shiver'
- **myĩyyi** /ˈmjĩjji/ *adv.* 'instantly'
- **myowin·ya** /ˈmjowinja/ *n.* 'priest'
- **myoyĩ** /ˈmjojĩ/ *adj.* 'fat (obese)'
- **myuu** /mjuː/ *n.* 'daughter-in-law (of woman)'
- **myuuqri** /ˈmjuːŋri/ *n.* 'lightning'
- **myuyalaal** /ˈmjujalaːl/ *v.* 'set'
- **na** /na/ *n.* 'rope' — PL: nami; GEN: nan
- **naakwwiisge** /naːˈkwwiːsɡe/ *adj.* 'dear'
- **naanyi** /ˈnaːɲi/ *v.* 'hate'
- **nadaud** /ˈnadaud/ *v.* 'escape'
- **nagmuy** /ˈnaɡmuj/ *v.* 'drop (something)'
- **nakwug** /ˈnakwuɡ/ *n.* 'sack'
- **nakwupu** /ˈnakwupu/ *n.* 'tongs'
- **nal** /nal/ *adj.* 'deep'
- **nalaa** /ˈnalaː/ *n.* 'necklace'
- **namyig** /ˈnamjiɡ/ *n.* 'mushroom'
- **nanaa** /ˈnanaː/ *v.* 'sway'
- **naplii** /ˈnapliː/ *n.* 'intestines'
- **nasi** /ˈnasi/ *n.* 'jewel'
- **nat** /nat/ *adj.* 'male (of person)'
- **na·a** /ˈnaa/ *part.* 'behind'
- **ne** /ne/ *n.* 'cockroach'
- **neaa** /ˈneaː/ *v.* 'take a walk'
- **nemiey** /ˈnemiej/ *part.* 'where to'
- **nesii** /ˈnesiː/ *n.* 'pin'
- **net** /net/ *n.* 'edge'
- **neyiw** /ˈnejiw/ *adj.* 'merry'
- **neyya** /ˈnejja/ *n.* 'danger'
- **ni** /ni/ *n.* 'bull'
- **niho** /ˈniho/ *v.* 'send'
- **niimii** /ˈniːmiː/ *n.* 'court'
- **niimlub** /ˈniːmlub/ *n.* 'mistake'
- **niitu** /ˈniːtu/ *v.* 'have'
- **niiu** /ˈniːu/ *adj.* 'young'
- **niiugwusqa** /ˌniːuˈɡwusŋa/ *n.* 'younger brother' = *niiu* + *gwusqa*
- **niiukwunytwu** /ˌniːuˈkwuɲtwu/ *n.* 'young man' = *niiu* + *kwunytwu*
- **niiuma** /ˈniːuma/ *n.* 'younger sister' = *niiu* + *ma*
- **niiupu** /ˈniːupu/ *n.* 'younger sibling' = *niiu* + *pu*
- **niiutyul** /ˈniːutjul/ *n.* 'young woman' = *niiu* + *tyul*
- **niiwe** /ˈniːwe/ *v.* 'have sex'
- **niiyo** /ˈniːjo/ *n.* 'gill'
- **nikyad** /ˈnikjad/ *n.* 'tent'
- **nim** /nim/ *n.* 'belly' — PL: nimmi; GEN: nin — substituiu uma palavra antiga
- **nimo** /ˈnimo/ *v.* 'wait'
- **nimyegaa** /ˈnimjeɡaː/ *n.* 'child-in-law'
- **nimyuuraa** /ˈnimjuːraː/ *n.* 'beak'
- **niq** /niŋ/ *n.* 'pen'
- **nir** /nir/ *adj.* 'poor'
- **niu** /ˈniu/ *adj.* 'brave'
- **niwaii** /ˈniwaiː/ *n.* 'copper, bronze'
- **niweli** /ˈniweli/ *n.* 'footprint'
- **niyew** /ˈnijew/ *v.* 'swing (something)'
- **niyo** /ˈnijo/ *v.* 'regret'
- **ni·iwya** /ˈniiwja/ *n.* 'shelf'
- **nĩk** /nĩk/ *v.* 'touch'
- **nla** /nla/ *n.* 'sheep'
- **nlazwan** /ˈnlazwan/ *n.* 'vegetables'
- **nle** /nle/ *v.* 'stab'
- **nlekuu** /ˈnlekuː/ *n.* 'hell'
- **nlenyi** /ˈnleɲi/ *n.* 'threshing-floor'
- **nli** /nli/ *n.* 'corner'
- **nlĩkwanhi** /nlĩˈkwanhi/ *n.* 'cheese'
- **nluk** /nluk/ *n.* 'crocodile'
- **nlukle** /ˈnlukle/ *n.* 'story'
- **nlusa·a** /ˈnlusaa/ *n.* 'slave'
- **nluuge** /ˈnluːɡe/ *part.* 'outside'
- **nluughotyo** /ˈnluːɡhotjo/ *v.* 'do'
- **nluutibne** /nluːˈtibne/ *n.* 'married man'
- **no** /no/ *n.* 'armpit'
- **nokrirbe** /noˈkrirbe/ *v.* 'be thirsty'
- **nokwamlu** /ˈnokwamlu/ *n.* 'hawk'
- **nom** /nom/ *quant.* 'other'
- **nomn·yin** /ˈnomnjin/ *n.* 'eyelid'
- **nop** /nop/ *part.* 'only'
- **nopa** /ˈnopa/ *n.* 'cap'
- **noqnlii** /ˈnoŋnliː/ *n.* 'happiness'
- **noswu** /ˈnoswu/ *v.* 'fart'
- **notiduy** /ˈnotiduj/ *n.* 'he-goat'
- **nowublo** /ˈnowublo/ *n.* 'grass-skirt'
- **nrigum** /ˈnriɡum/ *v.* 'miss'
- **nrinyĩ** /ˈnriɲĩ/ *n.* 'father-in-law (of man)'
- **nriu** /ˈnriu/ *n.* 'hare'
- **nrogroxyaa** /ˈnroɡroʃjaː/ *n.* 'bamboo'
- **nu** /nu/ *n.* 'mother' — PL: numi; GEN: nun
- **nubi** /ˈnubi/ *n.* 'Friday'
- **nubuute** /ˈnubuːte/ *n.* 'noise'
- **nugwusqa** /nuˈɡwusŋa/ *n.* 'mother's brother' = *nu* + *gwusqa*
- **nule** /ˈnule/ *v.* 'build'
- **numa** /ˈnuma/ *n.* 'mother's sister' = *nu* + *ma*
- **numay** /ˈnumaj/ *n.* 'perch'
- **nune** /ˈnune/ *n.* 'collarbone'
- **nupum** /ˈnupum/ *n.* 'anger'
- **nusu·u** /ˈnusuu/ *v.* 'make'
- **nutinu** /ˈnutinu/ *v.* 'hang'
- **nutinuaiu** /nuˌtinuˈaiu/ *v.* 'hang up' = *nutinu* + *aiu*
- **nuu** /nuː/ *adj.* 'sweet'
- **nuupuot** /ˈnuːpuot/ *v.* 'step'
- **nuuwotwuu** /ˈnuːwotwuː/ *n.* 'sweet potato' = *nuu* + *wotwuu*
- **nuuyi** /ˈnuːji/ *n.* 'sweetness' ← *nuu*
- **nuyi** /ˈnuji/ *n.* 'daughter'
- **nu·uma** /ˈnuuma/ *v.* 'hollow out'
- **nya** /ɲa/ *v.t.* 'to wipe' — PST: nyapu — substituiu uma palavra antiga
- **nyaa** /ɲaː/ *n.* 'silver'
- **nyai** /ˈɲai/ *n.* 'count'
- **nyaiike** /ˈɲaiːke/ *n.* 'ankle'
- **nyake** /ˈɲake/ *adj.* 'sad'
- **nyama** /ˈɲama/ *n.* 'guest'
- **nyamuskuy** /ɲaˈmuskuj/ *adj.* 'open (state)'
- **nyapyamu** /ˈɲapjamu/ *n.* 'statue'
- **nyari** /ˈɲari/ *n.* 'trough'
- **nye** /ɲe/ *n.* 'voice'
- **nyed** /ɲed/ *n.* 'savanna'
- **nyegraq** /ˈɲeɡraŋ/ *part.* 'zero, nothing'
- **nyesa** /ˈɲesa/ *n.* 'headband'
- **nyibĩ** /ˈɲibĩ/ *v.* 'meet'
- **nyiim** /ɲiːm/ *v.* 'hurry'
- **nyiin** /ɲiːn/ *n.* 'bottom'
- **nyiipu** /ˈɲiːpu/ *v.* 'smoke (inhale)'
- **nyisi** /ˈɲisi/ *v.* 'last (endure)'
- **nyiti** /ˈɲiti/ *n.* 'father-in-law (of woman)'
- **nyiwlo** /ˈɲiwlo/ *n.* 'sort'
- **nyo** /ɲo/ *v.* 'be born'
- **nyomabyyem** /ˈɲomabjjem/ *n.* 'peg'
- **nyomum** /ˈɲomum/ *part.* 'no'
- **nyonu·u** /ˈɲonuu/ *n.* 'linen, flax'
- **nyu** /ɲu/ *v.* 'carry on head'
- **nyulĩ** /ˈɲulĩ/ *v.* 'own'
- **nyumor** /ˈɲumor/ *n.* 'skin' — PL: nyumormi; GEN: nyumon
- **nyusaok** /ˈɲusaok/ *v.* 'urge'
- **nyuunibii** /ˈɲuːnibiː/ *n.* 'seagull'
- **nyuupli** /ˈɲuːpli/ *n.* 'scar'
- **nyuyi** /ˈɲuji/ *v.* 'trap (catch)'
- **nywapli** /ˈɲwapli/ *adj.* 'clean'
- **nywapodyur** /ˈɲwapodjur/ *n.* 'helmet'
- **nywikgok** /ˈɲwikɡok/ *adj.* 'firm, solid'
- **nywiwiny** /ˈɲwiwiɲ/ *v.* 'thaw'
- **nywui** /ˈɲwui/ *n.* 'paper'
- **n·ya** /nja/ *n.* 'summer'
- **n·yaid** /ˈnjaid/ *v.* 'knit'
- **n·yalsawom** /ˈnjalsawom/ *n.* 'meaning'
- **n·yaluu** /ˈnjaluː/ *n.* 'tide'
- **n·yapi** /ˈnjapi/ *adj.* 'lame'
- **n·yaqĩo** /ˈnjaŋĩo/ *n.* 'grandparents'
- **n·yatbupa** /ˈnjatbupa/ *n.* 'evening'
- **n·ye** /nje/ *v.* 'rest'
- **n·yepi** /ˈnjepi/ *n.* 'sledge'
- **n·yi** /nji/ *v.* 'cover'
- **n·yigluba** /ˈnjiɡluba/ *n.* 'bunch'
- **n·yii** /njiː/ *n.* 'freshwater eel'
- **n·yiidbiimqel** /njiːdˈbiːmŋel/ *n.* 'April'
- **n·yiixaa** /ˈnjiːʃaː/ *n.* 'drink'
- **n·yil** /njil/ *n.* 'furrow'
- **n·yipret** /ˈnjipret/ *n.* 'jug'
- **n·yiq** /njiŋ/ *adj.* 'gentle'
- **n·yo** /njo/ *v.* 'separate'
- **n·yu** /nju/ *n.* 'sock'
- **n·yuskhĩ** /ˈnjuskʰĩ/ *part.* 'beside'
- **n·yuu** /njuː/ *n.* 'calf of the leg'
- **o** /o/ [u] *n.* 'fly' — PL: omi; GEN: on
- **oblu** /ˈoblu/ *adv.* 'hither'
- **odyu** /ˈodju/ *adj.* 'evil'
- **oehud** /ˈoehud/ *v.* 'protect'
- **okyal** /ˈokjal/ *num.* 'thousand'
- **om** /om/ *conj.* 'if'
- **omisyaam** /ˈomisjaːm/ *n.* 'reason'
- **omnyu** /ˈomɲu/ *part.* 'third'
- **omnywa** /ˈomɲwa/ *n.* 'bow'
- **omtwidbo** /omˈtwidbo/ *n.* 'pupil'
- **oni** /ˈoni/ *n.* 'distance'
- **onxamyi** /ˈonʃamji/ *adj.* 'familiar'
- **oshayyap** /ˈoshajjap/ *v.* 'answer'
- **osul** /ˈosul/ *n.* 'cat'
- **owenyi** /ˈoweɲi/ *adj.* 'difficult'
- **owiiyaquu** /oˈwiːjaŋuː/ *n.* 'ant' — PL: owiiyaquumi; GEN: owiiyaquun
- **owiiyaquuuy** /ˌowiːˈjaŋuːuj/ *adj.* 'full of ant' ← *owiiyaquu*
- **owu** /ˈowu/ *v.* 'thresh'
- **oyi** /ˈoji/ *v.* 'break (destroy or get destroyed)'
- **oyimdyon** /oˈjimdjon/ *adj.* 'happy'
- **pa** /pa/ *n.* 'forehead'
- **paa** /paː/ *n.* 'snail'
- **paakuu** /ˈpaːkuː/ *adj.* 'sour'
- **paapi** /ˈpaːpi/ *n.* 'November'
- **pake** /ˈpake/ *v.* 'bring'
- **pakeaiu** /ˌpakeˈaiu/ *v.* 'bring up' = *pake* + *aiu*
- **pakhe** /ˈpakʰe/ *n.* 'pity'
- **paku** /ˈpaku/ *n.* 'match'
- **palqi** /ˈpalŋi/ *n.* 'stone/rock' — PL: palqimi; GEN: palqin
- **panru** /ˈpanru/ *n.* 'Saturday'
- **panytyik** /ˈpaɲtjik/ *n.* 'beer'
- **pan·yon** /ˈpanjon/ *adj.* 'wrong'
- **paq** /paŋ/ *v.* 'bend'
- **paqre** /ˈpaŋre/ *v.* 'share'
- **paqu** /ˈpaŋu/ *adv.* 'everywhere'
- **par** /par/ *n.* 'filth'
- **pasoya** /ˈpasoja/ *n.* 'town'
- **pauu** /ˈpauː/ *n.* 'poncho'
- **pawtemik** /ˈpawtemik/ *n.* 'maize'
- **paxus** /ˈpaʃus/ *n.* 'book'
- **pay** /paj/ *n.* 'leaf' — PL: paymi; GEN: pan
- **pa·aazwĩ** /ˈpaaːzwĩ/ *v.* 'perspire'
- **pe** /pe/ *part.* 'enough'
- **pebawa** /ˈpebawa/ *v.* 'pray'
- **pebawagwaaqum** /ˌpebaˈwaɡwaːŋum/ *n.* 'temple' = *pebawa* + *gwaaqum*
- **pee** /ˈpee/ *n.* 'beehive'
- **peku** /ˈpeku/ *n.* 'stove'
- **pemyi** /ˈpemji/ *v.* 'preach'
- **peo** /ˈpeo/ *n.* 'host'
- **pepe** /ˈpepe/ *v.* 'let, permit'
- **pepiwe** /ˈpepiwe/ *v.* 'measure'
- **pepugpa** /peˈpuɡpa/ *v.* 'whisper'
- **pepyo** /ˈpepjo/ *n.* 'button'
- **petsomya** /ˈpetsomja/ *n.* 'cousin'
- **pewiibpe** /peˈwiːbpe/ *n.* 'eyelash'
- **pexok** /ˈpeʃok/ *n.* 'clay'
- **pexokkwunytwu** /ˌpeʃokˈkwuɲtwu/ *n.* 'potter' ← *pexok* (agentivo)
- **peyeno** /ˈpejeno/ *v.* 'die, dead'
- **pha** /pʰa/ *n.* 'tin'
- **phaaqu** /ˈpʰaːŋu/ *n.* 'duck'
- **phasazo** /ˈpʰasazo/ *n.* 'lion'
- **phekya** /ˈpʰekja/ *n.* 'drop (of a liquid)'
- **phi** /pʰi/ *n.* 'medicine'
- **phii** /pʰiː/ *n.* 'comb'
- **phiyiipaa** /ˈpʰijiːpaː/ *n.* 'mat'
- **phu** /pʰu/ *v.t.* 'to fear' — PST: phupu
- **phumii** /ˈpʰumiː/ *n.* 'womb'
- **phunli** /ˈpʰunli/ *n.* 'ocean'
- **pi** /pi/ *n.* 'year' — PL: pimi; GEN: pin
- **pigad** /ˈpiɡad/ *adj.* 'unripe'
- **piikra** /ˈpiːkra/ *adv.* 'thither'
- **piimsabi** /ˈpiːmsabi/ *v.* 'brawl'
- **piislu** /ˈpiːslu/ *v.* 'carry under the arm'
- **piiyi** /ˈpiːji/ *n.* 'remains'
- **pik** /pik/ *adj.* 'rich'
- **pikiiw** /ˈpikiːw/ *adj.* 'full'
- **pikliina** /ˈpikliːna/ *adj.* 'dead'
- **pikumu** /ˈpikumu/ *n.* 'scissors'
- **pikuyet** /ˈpikujet/ *n.* 'half'
- **pinla** /ˈpinla/ *n.* 'shop'
- **pinyal** /ˈpiɲal/ *n.* 'lamp'
- **piqwaagwa** /ˈpiŋwaːɡwa/ *v.* 'choke'
- **pit** /pit/ *n.* 'snow' — PL: pitmi; GEN: pin
- **pite** /ˈpite/ *n.* 'swamp'
- **piwaa** /ˈpiwaː/ *n.* 'afternoon'
- **piwu** /ˈpiwu/ *v.* 'roll'
- **pixa** /ˈpiʃa/ *n.* 'cattle'
- **pixakwunytwu** /ˌpiʃaˈkwuɲtwu/ *n.* 'herdsman' = *pixa* + *kwunytwu*
- **piya** /ˈpija/ *v.* 'irrigate'
- **pĩ** /pĩ/ *v.* 'arrive'
- **pĩptrii** /ˈpĩptriː/ *n.* 'sculptor'
- **plaar** /plaːr/ *adj.* 'bad'
- **plaarad** /ˈplaːrad/ *v.* 'to become bad' ← *plaar*
- **plesus** /ˈplesus/ *v.* 'fry'
- **pli** /pli/ *n.* 'Tuesday'
- **plik** /plik/ *v.t.* 'to kill' — PST: plikpu
- **plikgo** /ˈplikɡo/ *n.* 'murder' ← *plik* (ação)
- **plil** /plil/ *v.* 'imitate'
- **plinyig** /ˈpliɲiɡ/ *n.* 'plain'
- **pliqada** /ˈpliŋada/ *v.* 'draw milk'
- **pliyi** /ˈpliji/ *v.* 'finish'
- **plo** /plo/ [plu] *n.* 'skin/hide' — PL: plomi; GEN: plon — substituiu uma palavra antiga
- **plu** /plu/ *v.* 'boil (of liquid)'
- **plumgyĩli** /ˈplumɡjĩli/ *n.* 'earlobe'
- **plurgu** /ˈplurɡu/ *adj.* 'narrow' — substituiu uma palavra antiga
- **pluseep** /ˈpluseep/ *n.* 'sin'
- **plusuu** /ˈplusuː/ *n.* 'reef'
- **pluuer** /ˈpluːer/ *n.* 'pillow'
- **po** /po/ [pu] *n.* 'nose' — PL: pomi; GEN: pon — substituiu uma palavra antiga
- **podtwaa** /ˈpodtwaː/ *n.* 'flesh'
- **pokwu** /ˈpokwu/ *adj.* 'female (of person)'
- **polu** /ˈpolu/ *n.* 'sleep (state)'
- **pomyiise** /ˈpomjiːse/ *n.* 'pocket'
- **poneo** /ˈponeo/ *n.* 'nipple'
- **poniibuu** /ˈponiːbuː/ *n.* 'shield'
- **ponybu·uu** /ˈpoɲbuuː/ *n.* 'day (24 hours)'
- **pooda** /ˈpooda/ *n.* 'ewe'
- **poohaa** /ˈpoohaː/ *n.* 'mare'
- **poq** /poŋ/ *quant.* 'some' — substituiu uma palavra antiga
- **poqnomo** /ˈpoŋnomo/ *v.* 'conceive'
- **powuny** /ˈpowuɲ/ *n.* 'intention'
- **powurol** /ˈpowurol/ *part.* 'twice'
- **poyyem** /ˈpojjem/ *n.* 'boot'
- **pra** /pra/ *v.* 'think (believe)'
- **praabmiyu** /ˈpraːbmiju/ *n.* 'pig'
- **priikwa** /ˈpriːkwa/ *n.* 'parents-in-law'
- **prip·hagru** /ˈpriphaɡru/ *n.* 'arson'
- **pro** /pro/ *adj.* 'ripe'
- **probyuno** /ˈprobjuno/ *adj.* 'surprised'
- **pru** /pru/ *conj.* 'because'
- **pruwa** /ˈpruwa/ *n.* 'fir'
- **prwelklĩ** /ˈprwelklĩ/ *v.t.* 'to cut' — PST: prwelklĩpu
- **prwelklĩgimikwa** /ˌprwelklĩˈɡimikwa/ *n.* 'knife' = *prwelklĩ* + *gimikwa*
- **prwelklĩmlii** /ˈprwelklĩmliː/ *v.* 'cut down' = *prwelklĩ* + *mlii*
- **prwelklĩso** /ˈprwelklĩso/ [ˈprwelklĩsu] *n.* 'wound' ← *prwelklĩ*
- **pu** /pu/ *n.* 'sibling'
- **pubkliit** /ˈpubkliːt/ *n.* 'support, rest'
- **pum** /pum/ *n.* 'freeman'
- **pumi** /ˈpumi/ *n.* 'veil'
- **pumlu** /ˈpumlu/ *v.* 'dive'
- **pumo** /ˈpumo/ *n.* 'raccoon'
- **pupaa** /ˈpupaː/ *n.* 'clock'
- **pupru** /ˈpupru/ *adj.* 'dry'
- **pupruad** /ˈpupruad/ *v.* 'to dry up' ← *pupru*
- **puqwi** /ˈpuŋwi/ *part.* 'soon'
- **putyikde** /puˈtjikde/ *v.* 'permit'
- **puu** /puː/ *n.* 'grapevine'
- **puun** /puːn/ *n.* 'cloud' — PL: puunmi; GEN: puun — antes significava 'fog' (ampliação)
- **puun** /puːn/ *n.* 'fog' — PL: puunmi; GEN: puun
- **puuxrĩ** /ˈpuːʃrĩ/ *adj.* 'pretty'
- **puwa** /ˈpuwa/ *n.* 'shoulder'
- **puxe** /ˈpuʃe/ *n.* 'flute'
- **puyyay** /ˈpujjaj/ *part.* 'how much?'
- **pyaaaayni** /pjaːˈaːjni/ *n.* 'storm'
- **pyaamgyuhaa** /ˈpjaːmɡjuhaː/ *n.* 'eagle'
- **pyaapyo** /ˈpjaːpjo/ *v.* 'sniff'
- **pyeryo** /ˈpjerjo/ [ˈpjerju] *v.i.* 'to live' — PST: pyeryopu
- **pyeryogo** /ˈpjerjoɡo/ [ˈpjerjoɣu] *n.* 'result of living' ← *pyeryo*
- **pyeryowe** /ˈpjerjowe/ [ˈpjerjowi] *adj.* 'tending to live' ← *pyeryo*
- **pyeya** /ˈpjeja/ *n.* 'shell'
- **pyi** /pji/ *adv.* 'here'
- **pyig** /pjiɡ/ *v.* 'chew'
- **pyii** /pjiː/ *v.* 'cure'
- **pyiixa** /ˈpjiːʃa/ *adj.* 'wrinkled'
- **pyiiyam** /ˈpjiːjam/ *n.* 'men's house'
- **pyik** /pjik/ *v.* 'boast'
- **pyimyab** /ˈpjimjab/ *n.* 'gift'
- **pyip** /pjip/ *n.* 'adultery'
- **pyiqmizwem** /ˈpjiŋmizwem/ *adj.* 'hard' — substituiu uma palavra antiga
- **pyoktraaqru** /ˈpjoktraːŋru/ *adj.* 'thin (of shape of object)'
- **pyoy** /pjoj/ *v.* 'shout'
- **pyu** /pju/ *n.* 'branch'
- **pyuk** /pjuk/ *v.* 'ask (inquire)'
- **pyupsrakdik** /pjupˈsrakdik/ *adj.* 'greedy'
- **qa** /ŋa/ *n.* 'snake' — PL: qami; GEN: qan
- **qaa** /ŋaː/ *v.t.* 'to tie' — PST: qaapu
- **qaaaiu** /ŋaːˈaiu/ *v.* 'tie up' = *qaa* + *aiu*
- **qaaso** /ˈŋaːso/ [ˈŋaːsu] *n.* 'knot' ← *qaa*
- **qagi** /ˈŋaɡi/ *n.* 'flock'
- **qakla** /ˈŋakla/ *v.* 'owe'
- **qalaap** /ˈŋalaːp/ *v.* 'stir'
- **qar** /ŋar/ *n.* 'needle (for sewing)'
- **qawye** /ˈŋawje/ *adj.* 'closed'
- **qe** /ŋe/ [ŋi] *v.i.* 'to spit' — PST: qepu — substituiu uma palavra antiga
- **qeb** /ŋeb/ *v.* 'scold'
- **qelo** /ˈŋelo/ *n.* 'world'
- **qen** /ŋen/ *v.t.* 'to stab' — PST: qenpu
- **qena** /ˈŋena/ *v.* 'mow'
- **qenka** /ˈŋenka/ *n.* 'east'
- **qeso** /ˈŋeso/ [ˈŋesu] *n.* 'what is spited' ← *qe*
- **qi** /ŋi/ *n.* 'grandson'
- **qid** /ŋid/ *v.* 'be hungry'
- **qiema** /ˈŋiema/ *part.* 'we (exclusive)'
- **qii** /ŋiː/ *v.* 'repair, mend'
- **qiislay** /ˈŋiːslaj/ *v.* 'approach'
- **qiiwa** /ˈŋiːwa/ *v.* 'tinkle'
- **qika** /ˈŋika/ *adj.* 'blind'
- **qila** /ˈŋila/ *v.* 'love'
- **qim** /ŋim/ *n.* 'stone' — PL: qimmi; GEN: qin — substituiu uma palavra antiga
- **qima** /ˈŋima/ *part.* 'before'
- **qimuk** /ˈŋimuk/ *n.* 'frost'
- **qimuy** /ˈŋimuj/ *adj.* 'stony' ← *qim*
- **qiquho** /ˈŋiŋuho/ *v.* 'speak'
- **qispaamkob** /ŋisˈpaːmkob/ *n.* 'lock'
- **qispaamkobgimikwa** /ŋisˌpaːmkobˈɡimikwa/ *n.* 'key' = *qispaamkob* + *gimikwa*
- **qiye** /ˈŋije/ *n.* 'snowshoe'
- **qo** /ŋo/ [ŋu] *num.* 'four'
- **qogyi** /ˈŋoɡji/ *v.* 'knock'
- **qremlib** /ˈŋremlib/ *n.* 'news'
- **qreny** /ŋreɲ/ *adj.* 'stingy'
- **qri** /ŋri/ *v.* 'drive'
- **qrukma** /ˈŋrukma/ *v.* 'get'
- **qrukmadersei** /ˌŋrukmaˈdersei/ *v.* 'get tired' = *qrukma* + *dersei*
- **qruse** /ˈŋruse/ *n.* 'ointment'
- **qu** /ŋu/ *n.* 'milk'
- **qumkyĩ** /ˈŋumkjĩ/ *n.* 'rain' — PL: qumkyĩmi; GEN: qumkyĩn
- **quupuo** /ˈŋuːpuo/ *v.* 'rush'
- **quxatwi** /ˈŋuʃatwi/ *n.* 'mouse'
- **quzre** /ˈŋuzre/ *n.* 'stingray'
- **qwa** /ŋwa/ *n.* 'hill'
- **qwakhaa** /ˈŋwakʰaː/ *v.* 'sieve'
- **qwetyal** /ˈŋwetjal/ *v.i.* 'to lie' — PST: qwetyalpu
- **qwetyalmlii** /ŋweˈtjalmliː/ *v.* 'lie down' = *qwetyal* + *mlii*
- **qwinye** /ˈŋwiɲe/ *n.* 'pestle'
- **qwo** /ŋwo/ *n.* 'nail (tool)'
- **qwuo** /ˈŋwuo/ *v.* 'ripen'
- **qwupya** /ˈŋwupja/ *n.* 'ball'
- **ra** /ra/ *n.* 'bee'
- **raa** /raː/ *adv.* 'fast'
- **raakwin** /ˈraːkwin/ *v.* 'pass'
- **raalnlitkhii** /raːlˈnlitkʰiː/ *v.* 'surrender'
- **raara** /ˈraːra/ *n.* 'strap'
- **raatdrozi** /ˈraːtdrozi/ *n.* 'mortar'
- **rabaa** /ˈrabaː/ *n.* 'fairy'
- **rahutuu** /ˈrahutuː/ *n.* 'leather'
- **rakabii** /ˈrakabiː/ *n.* 'oath'
- **ramiryu** /ˈramirju/ *n.* 'judge'
- **ramiryugo** /raˈmirjuɡo/ *n.* 'judgment' ← *ramiryu* (ação)
- **ramu** /ˈramu/ *n.* 'physician'
- **ranarii** /ˈranariː/ *v.* 'bother'
- **ranypi** /ˈraɲpi/ *n.* 'winter'
- **rapi** /ˈrapi/ *n.* 'reindeer'
- **raqwuy** /ˈraŋwuj/ *adj.* 'shallow'
- **rasimi** /ˈrasimi/ *v.* 'seem'
- **re** /re/ *n.* 'scale'
- **rebuyo** /ˈrebujo/ *v.* 'perish'
- **rehag** /ˈrehaɡ/ *n.* 'nettle'
- **rek** /rek/ *adj.* 'slim'
- **reko** /ˈreko/ *v.* 'raise'
- **repnaya** /ˈrepnaja/ *v.* 'tan'
- **ri** /ri/ *n.* 'ram'
- **rila** /ˈrila/ *v.* 'jog'
- **ripraw** /ˈripraw/ *n.* 'fishing line'
- **riwuna** /ˈriwuna/ *n.* 'character'
- **ronite** /ˈronite/ *part.* 'because of'
- **row** /row/ *adj.* 'similar'
- **roye** /ˈroje/ *n.* 'man'
- **ru** /ru/ *quant.* 'few'
- **rumyu** /ˈrumju/ *v.* 'can'
- **rutema** /ˈrutema/ *n.* 'linen'
- **rya** /rja/ *v.* 'plant (something)'
- **ryakwunytwu** /rjaˈkwuɲtwu/ *n.* 'farmer' ← *rya* (agentivo)
- **ryay** /rjaj/ *v.* 'recover'
- **ryek** /rjek/ *n.* 'brass instrument (horn or trumpet)'
- **ryeycyaamya** /ˈrjejθjaːmja/ *v.* 'fall ill'
- **ryeyduwbrii** /rjejˈduwbriː/ *n.* 'odour'
- **ryiswug** /ˈrjiswuɡ/ *n.* 'fork'
- **ryo** /rjo/ *v.* 'embrace'
- **ryu** /rju/ *n.* 'mosque'
- **ryukuw** /ˈrjukuw/ *v.* 'lie (mislead)'
- **ryul** /rjul/ *n.* 'sinew'
- **sa** /sa/ *pron.* 'they'
- **saa** /saː/ *v.* 'whistle'
- **saabtyum** /ˈsaːbtjum/ *n.* 'molar tooth'
- **saabuti** /ˈsaːbuti/ *n.* 'amount'
- **saba** /ˈsaba/ *n.* 'skirt'
- **sabanypu** /saˈbaɲpu/ *n.* 'sacrifice'
- **sabas** /ˈsabas/ *n.* 'stomach'
- **sabgiku** /ˈsabɡiku/ *v.* 'drown'
- **sai** /ˈsai/ *v.* 'decorate'
- **saiog** /ˈsaioɡ/ *adj.* 'light (color)'
- **sal** /sal/ *n.* 'thigh' — PL: salmi; GEN: san
- **salwagal** /ˈsalwaɡal/ *n.* 'pubic hair'
- **sam** /sam/ *n.* 'leg/foot' — PL: sammi; GEN: san
- **sapaa** /ˈsapaː/ *adj.* 'quiet'
- **sapyizu** /ˈsapjizu/ *v.* 'curse'
- **saqwa** /ˈsaŋwa/ *n.* 'meeting house'
- **sasany** /ˈsasaɲ/ *v.t.* 'to bite' — PST: sasanypu
- **sasanywe** /ˈsasaɲwe/ [ˈsasaɲwi] *adj.* 'tending to bite' ← *sasany*
- **semi** /ˈsemi/ *v.* 'betray'
- **sertuukaw** /ˈsertuːkaw/ *v.* 'remember'
- **seupi** /ˈseupi/ *n.* 'hat'
- **sexyaw** /ˈseʃjaw/ *n.* 'grasshopper'
- **si** /si/ *n.* 'tone'
- **sigleg** /ˈsiɡleɡ/ *v.* 'believe'
- **sigwii** /ˈsiɡwiː/ *n.* 'seed' — PL: sigwiimi; GEN: sigwiin
- **siho** /ˈsiho/ *v.* 'chop'
- **sii** /siː/ *v.* 'ride'
- **siib** /siːb/ *n.* 'coyote'
- **siila** /ˈsiːla/ *n.* 'tear (of eye)'
- **sikityol** /ˈsikitjol/ *v.* 'listen'
- **sikiyu** /ˈsikiju/ *v.* 'beat'
- **sil** /sil/ *v.i.* 'to walk' — PST: silpu
- **silsri** /ˈsilsri/ *v.t.* 'to count' — PST: silsripu
- **silsriso** /ˈsilsriso/ [ˈsilsrisu] *n.* 'number' ← *silsri*
- **silwe** /ˈsilwe/ [ˈsilwi] *adj.* 'tending to walk' ← *sil*
- **sininy** /ˈsiniɲ/ *n.* 'hoarfrost'
- **siphi** /ˈsipʰi/ *n.* 'shoulderblade'
- **siplu** /ˈsiplu/ *adj.* 'bright'
- **siqma** /ˈsiŋma/ *n.* 'wasp'
- **sis** /sis/ *n.* 'garden'
- **sitoa** /ˈsitoa/ *n.* 'knot'
- **sitpako** /ˈsitpako/ *n.* 'defeat'
- **siyi** /ˈsiji/ *n.* 'way'
- **sĩ** /sĩ/ *n.* 'hip'
- **so** /so/ *n.* 'sow (female pig)'
- **sole** /ˈsole/ *n.* 'source'
- **sope** /ˈsope/ *n.* 'scorpion'
- **sopii** /ˈsopiː/ *v.* 'hit'
- **sopno** /ˈsopno/ *v.* 'ring (make sound)'
- **sorya** /ˈsorja/ *part.* 'more'
- **sra** /sra/ *num.* 'seven'
- **sre** /sre/ *num.* 'six'
- **sri** /sri/ *n.* 'sword'
- **sribii** /ˈsribiː/ *n.* 'sibling-in-law'
- **sriison·yuum** /ˈsriːsonjuːm/ *n.* 'fault'
- **sruunwu** /ˈsruːnwu/ *v.* 'lend'
- **su** /su/ *n.* 'bat'
- **suba** /ˈsuba/ *n.* 'arm'
- **sudye** /ˈsudje/ *n.* 'insect'
- **suglabluu** /ˈsuɡlabluː/ *v.* 'command'
- **sulyatu** /ˈsuljatu/ *n.* 'buffalo'
- **sunle** /ˈsunle/ *n.* 'rape'
- **sunywi** /ˈsuɲwi/ *v.* 'hope'
- **suphu** /ˈsupʰu/ *v.* 'give'
- **suqwo** /ˈsuŋwo/ *part.* 'eighty'
- **suu** /suː/ *adj.* 'lazy'
- **suudemli** /ˈsuːdemli/ *n.* 'plaintiff'
- **suumus** /ˈsuːmus/ *n.* 'boundary'
- **suut** /suːt/ *v.* 'go'
- **suuwoq** /ˈsuːwoŋ/ *n.* 'flower' — PL: suuwoqmi; GEN: suuwon
- **suwba** /ˈsuwba/ *adj.* 'expensive'
- **suxroy** /ˈsuʃroj/ *n.* 'crowd'
- **suyi** /ˈsuji/ *n.* 'onion'
- **su·uwpu** /suˈuwpu/ *n.* 'earthquake'
- **swa** /swa/ *n.* 'fingernail or toenail'
- **swamo** /ˈswamo/ *n.* 'elk'
- **sweg** /sweɡ/ *n.* 'fringe'
- **swenyxĩg** /ˈsweɲʃĩɡ/ *v.i.* 'to cry/weep' — PST: swenyxĩgpu
- **swenyxĩggo** /sweɲˈʃĩɡɡo/ [sweɲˈʃĩɡɡu] *n.* 'act of crying' ← *swenyxĩg*
- **swenyxĩgwe** /ˈsweɲʃĩɡwe/ [ˈsweɲʃĩɡwi] *adj.* 'tearful' ← *swenyxĩg*
- **swergwiqu** /ˈswerɡwiŋu/ *n.* 'hay'
- **swidoti** /ˈswidoti/ *adj.* 'delicious'
- **swidwu** /ˈswidwu/ *v.* 'learn'
- **swobokyii** /ˈswobokjiː/ *v.* 'win'
- **swoni** /ˈswoni/ *n.* 'power'
- **swunak** /ˈswunak/ *part.* 'in front of'
- **swuy** /swuj/ *v.* 'read'
- **sya** /sja/ *v.* 'shut'
- **syabkad** /ˈsjabkad/ *n.* 'pipe'
- **syal** /sjal/ *n.* 'tree trunk'
- **syebyaa** /ˈsjebjaː/ *num.* 'five'
- **syekwanqa** /sjeˈkwanŋa/ *n.* 'length'
- **syenka** /ˈsjenka/ *v.i.* 'to go' — **PST: syenko** (irregular)
- **syenkamlii** /ˈsjenkamliː/ *v.* 'go down' = *syenka* + *mlii*
- **syenka·aiu** /ˌsjenkaˈaiu/ *v.* 'go up' = *syenka* + *aiu*
- **syepo** /ˈsjepo/ *n.* 'bay'
- **syeyuya** /ˈsjejuja/ *v.* 'splash'
- **syi** /sji/ *n.* 'brain'
- **syidyu** /ˈsjidju/ *n.* 'desire'
- **syig** /sjiɡ/ *adv.* 'at that time'
- **syiindu** /ˈsjiːndu/ *adj.* 'dull'
- **syiinduzi** /ˈsjiːnduzi/ *v.* 'to make dull' ← *syiindu*
- **syilqu** /ˈsjilŋu/ *adj.* 'cold'
- **syilquad** /ˈsjilŋuad/ *v.* 'to cool down' ← *syilqu*
- **syilquyi** /ˈsjilŋuji/ *n.* 'coldness' ← *syilqu*
- **syilquzi** /ˈsjilŋuzi/ *v.* 'to chill' ← *syilqu*
- **syimdyil** /ˈsjimdjil/ *n.* 'tree' — PL: syimdyilmi; GEN: syimdyin — substituiu uma palavra antiga
- **syimdyiluy** /ˈsjimdjiluj/ *adj.* 'wooded' ← *syimdyil*
- **syiqswayii** /ˈsjiŋswajiː/ *n.* 'sleeve'
- **syĩrya** /ˈsjĩrja/ *n.* 'wages'
- **syom** /sjom/ *v.t.* 'to hit' — PST: syompu
- **syomgimikwa** /sjomˈɡimikwa/ *n.* 'hammer' = *syom* + *gimikwa*
- **syoqmo** /ˈsjoŋmo/ *n.* 'walking stick'
- **syukaqi** /ˈsjukaŋi/ *n.* 'stallion'
- **syun** /sjun/ *n.* 'dog' — PL: syunmi; GEN: syun
- **syu·uwa** /ˈsjuuwa/ *v.* 'think (reflect)'
- **ta** /ta/ *n.* 'day' — PL: tami; GEN: tan
- **taagpo** /ˈtaːɡpo/ *n.* 'ridgepole'
- **taamaa** /ˈtaːmaː/ *n.* 'mainland'
- **tahi** /ˈtahi/ *n.* 'path'
- **tami** /ˈtami/ *v.* 'translate'
- **tanequ** /ˈtaneŋu/ *v.* 'shake'
- **tasaku** /ˈtasaku/ *v.* 'carry on shoulder'
- **taynywi** /ˈtajɲwi/ *adj.* 'cold'
- **te** /te/ *v.* 'sneeze'
- **tekuy** /ˈtekuj/ *n.* 'goat'
- **tephuu** /ˈtepʰuː/ *n.* 'goose'
- **ti** /ti/ *v.* 'spin'
- **tigyiw** /ˈtiɡjiw/ *n.* 'crow'
- **tihĩm** /ˈtihĩm/ *n.* 'feather' — PL: tihĩmmi; GEN: tihĩn
- **tiitgi** /ˈtiːtɡi/ *n.* 'bucket'
- **til** /til/ *n.* 'prawns'
- **tiwees** /ˈtiwees/ *n.* 'tattoo'
- **tiyin** /ˈtijin/ *v.t.* 'to squeeze' — PST: tiyinpu
- **tĩnyo** /ˈtĩɲo/ *v.* 'dribble'
- **to** /to/ *n.* 'dew'
- **tomosa** /ˈtomosa/ *n.* 'village'
- **ton·yiisyi** /ˈtonjiːsji/ *adv.* 'slow'
- **topu** /ˈtopu/ *n.* 'club'
- **totwok** /ˈtotwok/ *n.* 'blacksmith'
- **totyaa** /ˈtotjaː/ *n.* 'tapir'
- **towtu** /ˈtowtu/ *n.* 'cock'
- **traatunqi** /traːˈtunŋi/ *v.* 'untie'
- **traaxedyuu** /ˈtraːʃedjuː/ *n.* 'son-in-law (of woman)'
- **tri** /tri/ *n.* 'cause'
- **tu** /tu/ *adj.* 'white'
- **tuad** /ˈtuad/ *v.* 'to become white' ← *tu*
- **tud** /tud/ *n.* 'tumpline'
- **tudwuumgwun** /tuˈdwuːmɡwun/ *v.* 'peel'
- **tuge** /ˈtuɡe/ *adj.* 'wise'
- **tuhii** /ˈtuhiː/ *n.* 'chest'
- **tui** /ˈtui/ *v.* 'ask (request)'
- **tuki** /ˈtuki/ *n.* 'summit'
- **tulwili** /ˈtulwili/ *adj.* 'strong'
- **tumi** /ˈtumi/ *n.* 'paddle'
- **tun·yi** /ˈtunji/ *adj.* 'correct (right)' = mesma palavra que right
- **tun·yi** /ˈtunji/ *adj.* 'right'
- **tun·yiad** /ˈtunjiad/ *v.* 'to become correct (right)' ← *tun·yi*
- **tun·yizi** /ˈtunjizi/ *v.* 'to make correct (right)' ← *tun·yi*
- **tupn·yu** /ˈtupnju/ *v.* 'roast'
- **tuqzukkhi** /tuŋˈzukkʰi/ *n.* 'brook'
- **tusany** /ˈtusaɲ/ *n.* 'knee' — PL: tusanymi; GEN: tusan
- **tuu** /tuː/ *n.* 'fathom'
- **tuumeya** /ˈtuːmeja/ *adj.* 'tall'
- **tuuqwa** /ˈtuːŋwa/ *part.* 'for a long time'
- **tuyuubat** /ˈtujuːbat/ *n.* 'coast'
- **tuzi** /ˈtuzi/ *v.* 'to make white' ← *tu*
- **twa** /twa/ *v.* 'try'
- **twazaha** /ˈtwazaha/ *n.* 'drum'
- **twek** /twek/ *n.* 'brick'
- **tweki** /ˈtweki/ *adj.* 'loud'
- **twey** /twej/ *n.* 'niece'
- **twihimew** /ˈtwihimew/ *n.* 'nape of the neck'
- **twinpaaxa** /ˈtwinpaːʃa/ *n.* 'land'
- **twiqpim** /ˈtwiŋpim/ *v.t.* 'to hide' — PST: twiqpimpu — substituiu uma palavra antiga
- **twĩ** /twĩ/ *n.* 'people'
- **twoguu** /ˈtwoɡuː/ *n.* 'sugar cane'
- **twukukuu** /ˈtwukukuː/ *n.* 'debt'
- **twunate** /ˈtwunate/ *n.* 'rib'
- **twupukwe** /ˈtwupukwe/ *n.* 'table'
- **twuq** /twuŋ/ *n.* 'smoke' — PL: twuqmi; GEN: twun
- **twu·uub** /ˈtwuuːb/ *n.* 'saw'
- **tya** /tja/ *n.* 'louse' — PL: tyami; GEN: tyan
- **tyaa** /tjaː/ *num.* 'one'
- **tyaliiu** /ˈtjaliːu/ *n.* 'help (assistance)'
- **tyaluu** /ˈtjaluː/ *n.* 'heron'
- **tyas** /tjas/ *n.* 'season'
- **tyay** /tjaj/ *v.* 'be silent'
- **tyemsum** /ˈtjemsum/ *n.* 'leg' — PL: tyemsummi; GEN: tyemsun
- **tyi** /tji/ *adj.* 'short' — substituiu uma palavra antiga
- **tyinyabi** /ˈtjiɲabi/ *v.* 'enter'
- **tyipyi** /ˈtjipji/ *v.* 'barking'
- **tyĩt** /tjĩt/ *n.* 'moon'
- **tyo** /tjo/ *n.* 'current'
- **tyomamlaa** /ˈtjomamlaː/ *v.* 'thunder (verb)'
- **tyu** /tju/ *n.* 'truth'
- **tyua** /ˈtjua/ *n.* 'wine'
- **tyuaapklĩd** /tjuˈaːpklĩd/ *part.* 'between'
- **tyuii** /ˈtjuiː/ *n.* 'salt' — PL: tyuiimi; GEN: tyuiin
- **tyuiiuy** /ˈtjuiːuj/ *adj.* 'salty' ← *tyuii* (proprietivo)
- **tyul** /tjul/ *n.* 'woman' — PL: tyulmi; GEN: tyulĩn — GEN irregular, herdado
- **tyum** /tjum/ *n.* 'netbag'
- **tyunyzon** /ˈtjuɲzon/ *n.* 'child (descendant)' — PL: tyunyzonmi; GEN: tyunyzon
- **tyuqul** /ˈtjuŋul/ *n.* 'shore'
- **tyutyephu** /ˈtjutjepʰu/ *n.* 'thirst'
- **tyuumuubi** /ˈtjuːmuːbi/ *adj.* 'hot'
- **tyu·uzra** /ˈtjuuzra/ *n.* 'dawn'
- **u** /u/ *pron.* '3sg pronoun'
- **u** /u/ *pron.* 'he'
- **ubi** /ˈubi/ *v.* 'hide (oneself)'
- **ubi·i** /ˈubii/ *n.* 'servant'
- **ubywup** /ˈubjwup/ *v.* 'dream (something)'
- **udqite** /ˈudŋite/ *n.* 'word'
- **udu** /ˈudu/ *adv.* 'one time'
- **ugtwa** /ˈuɡtwa/ *n.* 'altar'
- **uhen** /ˈuhen/ *n.* 'heart' — PL: uhenmi; GEN: uhen
- **uhutwo** /ˈuhutwo/ *n.* 'hook'
- **ui** /ˈui/ *v.i.* 'to fly' — PST: uipu
- **uigo** /ˈuiɡo/ [ˈuiɣu] *n.* 'result of flying' ← *ui*
- **uiinla** /ˈuiːnla/ *adv.* 'hence'
- **uiw** /ˈuiw/ *n.* 'boil (of skin)'
- **uk** /uk/ *v.t.* 'know (something)' — PST: ukpu — substituiu uma palavra antiga
- **ul** /ul/ *num.* 'two'
- **ulam** /ˈulam/ *adv.* 'there'
- **ulno** /ˈulno/ *part.* 'sixty'
- **um** /um/ *n.* 'eye' — PL: ummi; GEN: un
- **umanis** /ˈumanis/ *n.* 'heaven'
- **umni** /ˈumni/ *adj.* 'red' — substituiu uma palavra antiga
- **umniad** /ˈumniad/ *v.* 'to blush' ← *umni*
- **uniimyii** /ˈuniːmjiː/ *n.* 'goitre'
- **unte** /ˈunte/ [ˈunti] *adj.* 'dirty'
- **unynuubo** /ˈuɲnuːbo/ *n.* 'widow'
- **unypreu** /ˈuɲpreu/ *part.* 'always'
- **up** /up/ *adj.* 'certain'
- **upage** /ˈupaɡe/ *part.* 'next'
- **upguma** /ˈupɡuma/ *n.* 'body'
- **upgumatya** /upˈɡumatja/ *n.* 'body louse' = *upguma* + *tya*
- **upguma·aambram** /upˌɡumaˈaːmbram/ *n.* 'body hair' = *upguma* + *aambram*
- **upru** /ˈupru/ *adj.* 'old'
- **uprua** /ˈuprua/ *n.* 'grandfather' = *upru* + *a*
- **upruad** /ˈupruad/ *v.* 'to age' ← *upru*
- **uprugwusqa** /ˌupruˈɡwusŋa/ *n.* 'older brother' = *upru* + *gwusqa*
- **uprukwunytwu** /ˌupruˈkwuɲtwu/ *n.* 'old man' = *upru* + *kwunytwu*
- **upruma** /ˈupruma/ *n.* 'older sister' = *upru* + *ma*
- **uprunu** /ˈuprunu/ *n.* 'grandmother' = *upru* + *nu*
- **uprupu** /ˈuprupu/ *n.* 'older sibling' = *upru* + *pu*
- **uprutyul** /ˈuprutjul/ *n.* 'old woman' = *upru* + *tyul*
- **upruyi** /ˈupruji/ *n.* 'old age' ← *upru*
- **upruyi** /ˈupruji/ *n.* 'age' ← *upru* (qualidade)
- **upuu** /ˈupuː/ *v.* 'add'
- **upyon** /ˈupjon/ *v.t.* 'to eat' — PST: upywenpu — PST irregular, herdado
- **upyongimikwa** /ˌupjonˈɡimikwa/ *n.* 'spoon' = *upyon* + *gimikwa*
- **upyongo** /uˈpjonɡo/ [upˈjonɡu] *n.* 'meal' ← *upyon*
- **upyonkwunytwu** /ˌupjonˈkwuɲtwu/ *n.* 'one who eats' ← *upyon*
- **upyonwe** /uˈpjonwe/ [upˈjonwi] *adj.* 'tending to eat' ← *upyon*
- **uqaa** /ˈuŋaː/ *v.* 'limp'
- **uqam** /ˈuŋam/ *n.* 'stable'
- **uril** /ˈuril/ *n.* 'June'
- **urqol** /ˈurŋol/ *v.i.* 'to rain' — PST: urqolpu
- **us** /us/ *adj.* 'far'
- **usaa** /ˈusaː/ *n.* 'apple'
- **usal** /ˈusal/ *n.* 'sorcerer'
- **uta** /ˈuta/ *v.* 'blink'
- **utit** /ˈutit/ *v.* 'bury'
- **utitgwaaqum** /uˈtitɡwaːŋum/ *n.* 'grave' = *utit* + *gwaaqum*
- **utmleymlu** /utˈmlejmlu/ *n.* 'sugar'
- **utu** /ˈutu/ *n.* 'south'
- **utwi** /ˈutwi/ *part.* 'second'
- **uu** /uː/ *adj.* 'thick'
- **uubu** /ˈuːbu/ *n.* 'plant (vegetation)'
- **uuk** /uːk/ *n.* 'law'
- **uulĩsyi** /ˈuːlĩsji/ *n.* 'turtle'
- **uunluu** /ˈuːnluː/ *n.* 'cassava'
- **uuu** /ˈuːu/ *n.* 'clothing'
- **uwmis** /ˈuwmis/ *n.* 'carpenter'
- **uwzra** /ˈuwzra/ *adj.* 'bald'
- **uye** /ˈuje/ *n.* 'dream'
- **uyyopru** /ˈujjopru/ *n.* 'height'
- **uzii** /ˈuziː/ *n.* 'language'
- **uzwuk** /ˈuzwuk/ *v.* 'dance'
- **u·u** /ˈuu/ *n.* 'mountain or hill'
- **wa** /wa/ *n.* 'arm/hand' — PL: wami; GEN: wan — substituiu uma palavra antiga
- **waa** /waː/ *v.* 'accuse'
- **waamtyu** /ˈwaːmtju/ *v.t.* 'to throw' — PST: waamtyupu
- **waamtyukwunytwu** /ˌwaːmtjuˈkwuɲtwu/ *n.* 'thing that throws' ← *waamtyu*
- **waapaa** /ˈwaːpaː/ *v.* 'pour'
- **waaqhan** /ˈwaːŋhan/ *v.* 'increase'
- **wabwumya** /ˈwabwumja/ *n.* 'frog'
- **waktuw** /ˈwaktuw/ *v.* 'refuse'
- **wakwaqo** /ˈwakwaŋo/ *v.* 'help'
- **wapglacaa** /ˈwapɡlaθaː/ *v.* 'mumble'
- **wapo** /ˈwapo/ *n.* 'bundle'
- **wapuyus** /ˈwapujus/ *v.* 'row'
- **wara** /ˈwara/ *n.* 'lung'
- **wargyi** /ˈwarɡji/ *v.t.* 'to push' — PST: wargyipu
- **wat** /wat/ *v.* 'slide'
- **watoruu** /ˈwatoruː/ *n.* 'lair'
- **wauu** /ˈwauː/ *v.* 'study'
- **wauugwaaqum** /waˈuːɡwaːŋum/ *n.* 'school' = *wauu* + *gwaaqum*
- **wayxyĩ** /ˈwajʃjĩ/ *v.* 'appear'
- **we** /we/ *n.* 'penalty'
- **wehi** /ˈwehi/ *n.* 'dinner'
- **wensri** /ˈwensri/ *n.* 'foot' — PL: wensrimi; GEN: wensrin
- **wepaamkob** /weˈpaːmkob/ *n.* 'nostril'
- **wewĩa** /ˈwewĩa/ *n.* 'border'
- **wewutron** /ˈwewutron/ *v.* 'dare'
- **wi** /wi/ *n.* 'uncle'
- **wia** /ˈwia/ *adj.* 'near'
- **wido** /ˈwido/ *n.* 'poison'
- **wihii** /ˈwihiː/ *n.* 'attack'
- **wii** /wiː/ *n.* 'bone' — PL: wiimi; GEN: wiin
- **wiiaapkod** /wiːˈaːpkod/ *n.* 'gun, cannon'
- **wiib** /wiːb/ *n.* 'thumb'
- **wiiguny** /ˈwiːɡuɲ/ [ˈwiːɣuɲ] *n.* 'wind' — PL: wiigunymi; GEN: wiigun — substituiu uma palavra antiga
- **wiigunyuy** /ˈwiːɡuɲuj/ [ˈwiːɣuɲuj] *adj.* 'full of wind' ← *wiiguny*
- **wiipaanob** /ˈwiːpaːnob/ *part.* 'again'
- **wiirkraa** /ˈwiːrkraː/ *n.* 'mountain' — PL: wiirkraami; GEN: wiirkraan
- **wik** /wik/ *n.* 'north'
- **wikyuuwu** /ˈwikjuːwu/ *n.* 'hunger'
- **wil** /wil/ *v.* 'be'
- **wilipar** /ˈwilipar/ *v.* 'hinder'
- **wilyuki** /ˈwiljuki/ *v.* 'be late' = *wil* + *yuki*
- **wine** /ˈwine/ *n.* 'chieftain'
- **winyaa** /ˈwiɲaː/ *n.* 'fowl'
- **wipluqwi** /ˈwipluŋwi/ *n.* 'defendant'
- **wiqma** /ˈwiŋma/ *n.* 'vein'
- **wiwĩk** /ˈwiwĩk/ *n.* 'cave'
- **wiywata** /ˈwijwata/ *n.* 'joy'
- **wĩ** /wĩ/ *pron.* 'we'
- **wĩhaa** /ˈwĩhaː/ *v.* 'hire or rent'
- **wĩpyu** /ˈwĩpju/ *n.* 'booty'
- **wo** /wo/ *v.* 'lose'
- **wokkhu** /ˈwokkʰu/ *n.* 'rice'
- **wolu** /ˈwolu/ *part.* 'first'
- **womuo** /ˈwomuo/ *v.* 'understand'
- **wos** /wos/ *n.* 'loom'
- **wotwuu** /ˈwotwuː/ *n.* 'potato'
- **wouudhuu** /ˈwouːðuː/ *n.* 'twig'
- **wowuxu** /ˈwowuʃu/ *adv.* 'already'
- **wowyike** /ˈwowjike/ *n.* 'ancestors'
- **woydhru** /ˈwojðru/ *n.* 'prison'
- **wu** /wu/ *quant.* 'all' — substituiu uma palavra antiga
- **wublek** /ˈwublek/ *v.* 'pick'
- **wublekaiu** /ˌwubleˈkaiu/ *v.* 'pick up' = *wublek* + *aiu*
- **wug** /wuɡ/ *v.* 'announce'
- **wuhenri** /ˈwuhenri/ *n.* 'silk'
- **wulake** /ˈwulake/ *n.* 'spark'
- **wulel** /ˈwulel/ *v.* 'painting'
- **wulquq** /ˈwulŋuŋ/ *n.* 'dust' — PL: wulquqmi; GEN: wulqun
- **wulququy** /ˈwulŋuŋuj/ *adj.* 'full of dust' ← *wulquq*
- **wulwaryi** /ˈwulwarji/ *n.* 'cup'
- **wumnupit** /ˈwumnupit/ *v.* 'harm, injure, damage'
- **wuna** /ˈwuna/ *part.* 'we (inclusive)'
- **wuqla** /ˈwuŋla/ *n.* 'native country'
- **wut** /wut/ *n.* 'canoe'
- **wutu** /ˈwutu/ *adv.* 'forward'
- **wuuil** /ˈwuːil/ *v.* 'keep'
- **wuukhay** /ˈwuːkʰaj/ *adj.* 'powerful'
- **wuukowĩ** /ˈwuːkowĩ/ *n.* 'vulva'
- **wuulupii** /ˈwuːlupiː/ *n.* 'lie (falsehood)'
- **wuunumnu** /wuːˈnumnu/ *n.* 'circle'
- **wuuu** /ˈwuːu/ *adj.* 'weak'
- **wuwĩ** /ˈwuwĩ/ *v.* 'press'
- **wuya** /ˈwuja/ *n.* 'stepfather'
- **wuyonnyu** /wuˈjonɲu/ *n.* 'January'
- **wya** /wja/ *n.* 'candle'
- **wyan·yo** /ˈwjanjo/ *n.* 'mill'
- **wyaya** /ˈwjaja/ *n.* 'ambush'
- **wye** /wje/ *n.* 'squirrel'
- **wyelpo** /ˈwjelpo/ [ˈwjelpu] *v.i.* 'to fight' — PST: wyelpopu
- **wyelpogo** /ˈwjelpoɡo/ [ˈwjelpoɣu] *n.* 'battle' ← *wyelpo*
- **wyelpokwunytwu** /ˌwjelpoˈkwuɲtwu/ *n.* 'warrior' ← *wyelpo*
- **wyelxekwu** /ˈwjelʃekwu/ *v.* 'prepare'
- **wyewkwanbya** /wjewˈkwanbja/ *n.* 'breath'
- **wyikumye** /ˈwjikumje/ *v.* 'threaten'
- **wyi·iiysaa** /wjiˈiːjsaː/ *n.* 'thread'
- **wyoq** /wjoŋ/ *n.* 'shore of lake'
- **wyowu** /ˈwjowu/ *n.* 'fine'
- **wyu** /wju/ *n.* 'camel'
- **wyulnaa** /ˈwjulnaː/ *v.* 'notice'
- **wyumya** /ˈwjumja/ *n.* 'heap'
- **wyupama** /ˈwjupama/ *v.* 'boil (something)'
- **xahi** /ˈʃahi/ *n.* 'flame'
- **xakiyiw** /ˈʃakijiw/ *n.* 'descendants'
- **xawo** /ˈʃawo/ *n.* 'mush'
- **xe** /ʃe/ *n.* 'anteater'
- **xepuy** /ˈʃepuj/ *v.* 'rescue'
- **xewbi** /ˈʃewbi/ *n.* 'testicles'
- **xeyuud** /ˈʃejuːd/ *v.* 'clean (something)'
- **xi** /ʃi/ *v.* 'bathe'
- **xiiguaap** /ˈʃiːɡuaːp/ *n.* 'centipede'
- **xiimi** /ˈʃiːmi/ *v.* 'wash'
- **xisako** /ˈʃisako/ *n.* 'time'
- **xoge** /ˈʃoɡe/ *n.* 'war'
- **xruwuu** /ˈʃruwuː/ *n.* 'tick'
- **xu** /ʃu/ *v.* 'look'
- **xumia** /ˈʃumia/ *n.* 'fever'
- **xusru** /ˈʃusru/ *n.* 'nephew'
- **xuwnya** /ˈʃuwɲa/ *n.* 'buttocks'
- **xuwo** /ˈʃuwo/ *n.* 'bait'
- **xwaxyu** /ˈʃwaʃju/ *n.* 'fear'
- **xwe** /ʃwe/ [ʃwi] *num.* 'three'
- **xwepudĩ** /ˈʃwepudĩ/ *n.* 'fingernail'
- **xwexisako** /ʃweˈʃisako/ *part.* 'three times' = *xwe* + *xisako*
- **xyaqep** /ˈʃjaŋep/ *v.* 'live'
- **xyasekwiy** /ˈʃjasekwij/ *n.* 'adze'
- **xyeyin** /ˈʃjejin/ *adj.* 'bitter'
- **xyeyinizi** /ʃjeˈjinizi/ *v.* 'to make bitter' ← *xyeyin*
- **xyi** /ʃji/ *n.* 'fan (object)'
- **xyis** /ʃjis/ *v.* 'abstain from food'
- **xyuĩ** /ˈʃjuĩ/ *adv.* 'back (direction)'
- **xyuqa** /ˈʃjuŋa/ *n.* 'message'
- **xyuuye** /ˈʃjuːje/ *v.* 'piss'
- **ya** /ja/ *v.* 'drip'
- **yaa** /jaː/ *n.* 'pair'
- **yaabonywu** /ˈjaːboɲwu/ *n.* 'February'
- **yaaduli** /ˈjaːduli/ *n.* 'cross'
- **yaaduligimikwa** /jaːˌduliˈɡimikwa/ *n.* 'bridge' = *yaaduli* + *gimikwa*
- **yaai** /ˈjaːi/ *v.* 'braid (verb) or weave (basket)'
- **yaale** /ˈjaːle/ *n.* 'soup'
- **yaap** /jaːp/ *adj.* 'big' — substituiu uma palavra antiga
- **yaapad** /ˈjaːpad/ *v.* 'to grow' ← *yaap*
- **yaapizi** /ˈjaːpizi/ *v.* 'to enlarge' ← *yaap*
- **yaapyi** /ˈjaːpji/ *n.* 'size' ← *yaap*
- **yaaymesi** /ˈjaːjmesi/ *v.* 'improve'
- **yabil** /ˈjabil/ [ˈjaβil] *n.* 'name' — PL: yabilmi; GEN: yabin
- **yabwo** /ˈjabwo/ *n.* 'food'
- **yagin·yii** /ˈjaɡinjiː/ [ˈjaɣinjiː] *n.* 'shade/shadow' — PL: yagin·yiimi; GEN: yagin·yiin — substituiu uma palavra antiga
- **yago** /ˈjaɡo/ *v.* 'crouch'
- **yagwam** /ˈjaɡwam/ *v.i.* 'to swim' — PST: yagwampu
- **yagwamkwunytwu** /ˌjaɡwamˈkwuɲtwu/ *n.* 'swimmer' ← *yagwam*
- **yak** /jak/ *v.t.* 'to take' — PST: yagep — PST irregular, herdado
- **yakwomiq** /ˈjakwomiŋ/ *adv.* 'backward'
- **yalbu** /ˈjalbu/ *part.* 'it'
- **yam** /jam/ *v.t.* 'to hit/beat' — PST: yampu
- **yaqu** /ˈjaŋu/ *v.* 'lead (guide)'
- **yas** /jas/ *n.* 'animal' — PL: yasmi; GEN: yan — substituiu uma palavra antiga
- **yasgi** /ˈjasɡi/ *n.* 'famine'
- **yasuy** /ˈjasuj/ *adj.* 'full of animal' ← *yas*
- **ye** /je/ [ji] *n.* 'head' — PL: yemi; GEN: yen
- **yedyun** /ˈjedjun/ *v.i.* 'to burn' — PST: yedyunpu
- **yeglip** /ˈjeɡlip/ *v.* 'feel'
- **yeksremnu** /jekˈsremnu/ *v.* 'pound'
- **yelo** /ˈjelo/ *n.* 'palm of the hand'
- **yemebi** /ˈjemebi/ *n.* 'bear'
- **yep** /jep/ *n.* 'mind'
- **yeq** /jeŋ/ *part.* 'above'
- **yeqwi** /ˈjeŋwi/ *v.* 'rise'
- **yetya** /ˈjetja/ *n.* 'head louse' = *ye* + *tya*
- **yi** /ji/ *n.* 'banana'
- **yibiki** /ˈjibiki/ *part.* 'how many?'
- **yidukwe** /ˈjidukwe/ *v.* 'dye'
- **yidyuknuu** /jiˈdjuknuː/ *v.* 'mix'
- **yii** /jiː/ *n.* 'May'
- **yiibyi** /ˈjiːbji/ *n.* 'woods' — PL: yiibyimi; GEN: yiibyin
- **yiil** /jiːl/ *adj.* 'rotten'
- **yiimo** /ˈjiːmo/ *n.* 'millet'
- **yiiryĩk** /ˈjiːrjĩk/ *part.* 'day before yesterday'
- **yiiwi** /ˈjiːwi/ *part.* 'sometimes'
- **yikli** /ˈjikli/ *n.* 'elephant'
- **yikliw** /ˈjikliw/ *part.* 'how much'
- **yila** /ˈjila/ *v.* 'taste'
- **yileke** /ˈjileke/ *adj.* 'deaf'
- **yimi** /ˈjimi/ *v.* 'climb'
- **yimimpaq** /jiˈmimpaŋ/ *n.* 'west'
- **yinal** /ˈjinal/ *n.* 'marriage, wedding'
- **yintar** /ˈjintar/ *adj.* 'black'
- **yintarizi** /jinˈtarizi/ *v.* 'to make black' ← *yintar*
- **yintaryi** /ˈjintarji/ *n.* 'blackness' ← *yintar*
- **yioew** /ˈjioew/ *adj.* 'beautiful'
- **yiqapuu** /ˈjiŋapuː/ *n.* 'vine'
- **yiqum** /ˈjiŋum/ *n.* 'fermented drink'
- **yir** /jir/ *n.* 'lake' — PL: yirmi; GEN: yin = mesma palavra que sea
- **yir** /jir/ *n.* 'sea' — PL: yirmi; GEN: yin
- **yis** /jis/ *n.* 'end (of time)'
- **yisyimdyil** /jiˈsjimdjil/ *n.* 'banana tree' = *yi* + *syimdyil*
- **yit** /jit/ *n.* 'piece'
- **yita** /ˈjita/ *v.* 'pursue'
- **yitrulnaa** /jiˈtrulnaː/ *adj.* 'crooked'
- **yitsu** /ˈjitsu/ *v.* 'shit'
- **yiuze** /ˈjiuze/ *v.* 'defend'
- **yiwyi** /ˈjiwji/ *v.* 'cease'
- **yiypyi** /ˈjijpji/ *n.* 'rattle'
- **yĩ** /jĩ/ *v.* 'promise'
- **yĩdu** /ˈjĩdu/ *n.* 'termites'
- **yĩka** /ˈjĩka/ *n.* 'son'
- **yo** /jo/ [ju] *v.t.* 'to say' — PST: yopu
- **yohu** /ˈjohu/ *n.* 'dough'
- **yokwiku** /ˈjokwiku/ *v.* 'injure'
- **yokwikuso** /joˈkwikuso/ *n.* 'wound' ← *yokwiku* (produto)
- **yolqaahi** /ˈjolŋaːhi/ *n.* 'anxiety'
- **yom** /jom/ *n.* 'pain'
- **yomi** /ˈjomi/ *n.* 'pike'
- **yomu** /ˈjomu/ *n.* 'adobe'
- **yoso** /ˈjoso/ [ˈjosu] *n.* 'saying' ← *yo*
- **yosru** /ˈjosru/ *part.* 'now'
- **yowe** /ˈjowe/ [ˈjowi] *adj.* 'tending to say' ← *yo*
- **yu** /ju/ *n.* 'island'
- **yua** /ˈjua/ *n.* 'pattern'
- **yud** /jud/ *n.* 'sibling’s child'
- **yudiwa** /ˈjudiwa/ *n.* 'bead'
- **yuike** /ˈjuike/ *n.* 'March'
- **yukakra** /ˈjukakra/ *n.* 'cape'
- **yukegi** /ˈjukeɡi/ *n.* 'knife (for eating)'
- **yuki** /ˈjuki/ *part.* 'late'
- **yultun** /ˈjultun/ *v.t.* 'to rub' — PST: yultunpu
- **yupomxa** /juˈpomʃa/ *v.* 'smoke (emit smoke)'
- **yuqo** /ˈjuŋo/ *n.* 'slope'
- **yuqul** /ˈjuŋul/ *n.* 'demon'
- **yus** /jus/ *n.* 'granddaughter'
- **yutbyoqyii** /jutˈbjoŋjiː/ *n.* 'padlock'
- **yutu** /ˈjutu/ *n.* 'married woman'
- **yuu** /juː/ *n.* 'leash'
- **yuul** /juːl/ *n.* 'sun' — PL: yuulmi; GEN: yuun
- **yuuti** /ˈjuːti/ *n.* 'shovel'
- **yuuyo** /ˈjuːjo/ *n.* 'walk'
- **yuwa** /ˈjuwa/ *n.* 'chicken'
- **yuy** /juj/ *n.* 'gun'
- **yuyu** /ˈjuju/ *n.* 'Thursday'
- **yuzĩphi** /ˈjuzĩpʰi/ *adj.* 'delicate, fine'
- **yuzruu** /ˈjuzruː/ *v.* 'pull off (skin)'
- **yu·u** /ˈjuu/ *v.* 'swing (movement)'
- **yyaapyi** /ˈjjaːpji/ *v.* 'prevent'
- **yyadpa** /ˈjjadpa/ *n.* 'cloth'
- **yyahauu** /ˈjjahauː/ *part.* 'next to'
- **yyanripum** /ˈjjanripum/ *v.* 'visit'
- **yya·a** /ˈjjaa/ *n.* 'swarm'
- **yye** /jje/ *n.* 'oil'
- **yyebak** /ˈjjebak/ *v.* 'open'
- **yyenyzyi** /ˈjjeɲzji/ *n.* 'sky' — PL: yyenyzyimi; GEN: yyenyzyin
- **yyep** /jjep/ *adj.* 'cooked'
- **yyetpoet** /ˈjjetpoet/ *n.* 'pumpkin'
- **yyi** /jji/ *adj.* 'mute'
- **yyiiputid** /ˈjjiːputid/ *n.* 'rainbow'
- **yyiiqdwukwi** /ˈjjiːŋdwukwi/ *n.* 'stepdaughter'
- **yyin** /jjin/ *n.* 'plait'
- **yyiphiyo** /ˈjjipʰijo/ *n.* 'initiation ceremony'
- **yyoa** /ˈjjoa/ *v.* 'change'
- **yyokle** /ˈjjokle/ *v.* 'annoy'
- **yyosil** /ˈjjosil/ *n.* 'coconut'
- **yyow** /jjow/ *n.* 'bread'
- **yyuk** /jjuk/ *v.* 'comb (verb)'
- **yyuklati** /ˈjjuklati/ *n.* 'sign'
- **yyul** /jjul/ *v.* 'ache'
- **yyunat** /ˈjjunat/ *n.* 'roof'
- **yyuu** /jjuː/ *n.* 'owl'
- **yyuyyaa** /ˈjjujjaː/ *v.* 'draw water'
- **zabiiam** /ˈzabiːam/ *adj.* 'dark'
- **zabiiamyi** /zaˈbiːamji/ *n.* 'darkness' ← *zabiiam* (qualidade)
- **zabrimi** /ˈzabrimi/ *v.* 'fall asleep'
- **zadzolqa** /zadˈzolŋa/ *v.* 'worship'
- **zal** /zal/ *n.* 'tooth' — PL: zalmi; GEN: zan
- **zalwa** /ˈzalwa/ *n.* 'spring or well'
- **zati** /ˈzati/ *v.* 'sound (of instrument or voice)'
- **zaw** /zaw/ *n.* 'baby'
- **zem** /zem/ *v.* 'tell'
- **zemowa** /ˈzemowa/ *v.* 'take off'
- **zexawmow** /zeˈʃawmow/ *n.* 'yolk'
- **zi** /zi/ *n.* 'part'
- **ziqi** /ˈziŋi/ *n.* 'arrow'
- **zis** /zis/ *n.* 'guts' — PL: zismi; GEN: zin — substituiu uma palavra antiga
- **zixemo** /ˈziʃemo/ *v.* 'burn'
- **zĩw** /zĩw/ *n.* 'elbow'
- **zo** /zo/ *n.* 'hoe'
- **zra** /zra/ *v.* 'put on'
- **zria** /ˈzria/ *n.* 'shame'
- **zrokwe** /ˈzrokwe/ *n.* 'oak'
- **zrutyu** /ˈzrutju/ *n.* 'net'
- **zuaq** /ˈzuaŋ/ *n.* 'star' — PL: zuaqmi; GEN: zuan
- **zusumi** /ˈzusumi/ *v.* 'tear (shred)'
- **zuuqe** /ˈzuːŋe/ *v.* 'watch'
- **zwi** /zwi/ *n.* 'glass'
- **zwiiwkades** /ˈzwiːwkades/ *n.* 'swan'
- **zwuuu** /ˈzwuːu/ *n.* 'gap'
- **zwuwizwuuy** /ˈzwuwizwuːj/ *v.* 'forget'
- **zyaapii** /ˈzjaːpiː/ *n.* 'cliff'
- **zyaaqĩ** /ˈzjaːŋĩ/ *n.* 'blanket'
- **zya·aka** /ˈzjaaka/ *v.* 'kiss'
- **zyek** /zjek/ *n.* 'pot'
- **zyempya** /ˈzjempja/ *n.* 'wing' — PL: zyempyami; GEN: zyempyan
- **zyit** /zjit/ *n.* 'spider web'
- **zyupye** /ˈzjupje/ *n.* 'field'

Expressos sem palavra própria: 'in' → caso locative; 'at' → caso locative; 'with (accompanying)' → caso instrumental

## Nomes próprios

- Nomes sem marca de gênero
- Sobrenomes: nome do pai + sufixo patronímico (-ak)
- Sufixo de povoado: -la /-la/

### Pessoas

| Nome | Pronúncia | Significado | Sobrenome |
|---|---|---|---|
| **Umniqa Howariak** | /ˈumniŋa/ | red snake | child of Howari |
| **Anya Kana·ak** | /ˈaɲa/ | — | child of Kana |
| **Umnidyun Yawuak** | /ˈumnidjun/ | red river | child of Yawu |
| **Emani Wina·ak** | /ˈemani/ | — | child of Wina |
| **Wupanul Ola·ak** | /ˈwupanul/ | — | child of Ola |
| **Wĩnu Tusuuwoqak** | /ˈwĩnu/ | — | child of Tusuuwoq |
| **Sewiq Omeak** | /ˈsewiŋ/ | — | child of Ome |
| **Iyaa Anuak** | /ˈijaː/ | — | child of Anu |
| **Qime Wiwiiak** | /ˈŋime/ | — | child of Wiwii |
| **Weruu Unileak** | /ˈweruː/ | — | child of Unile |
| **Lonyino Muyoak** | /ˈloɲino/ | — | child of Muyo |
| **Miri Dyubiak** | /ˈmiri/ | — | child of Dyubi |
| **Yuqal Yageak** | /ˈjuŋal/ | — | child of Yage |
| **Innyatihĩm Layirak** | /inˈɲatihĩm/ | new feather | child of Layir |
| **Ulaa Nyemeak** | /ˈulaː/ | — | child of Nyeme |
| **Niita Nyonunak** | /ˈniːta/ | — | child of Nyonun |
| **Ili Yewuak** | /ˈili/ | — | child of Yewu |
| **Yaapyir Laleak** | /ˈjaːpjir/ | big sea | child of Lale |
| **Dyuyuul Nuukrelak** | /ˈdjujuːl/ | yellow sun | child of Nuukrel |
| **Nuubi Dyuqimak** | /ˈnuːbi/ | sweet fish | child of Dyuqim |

### Lugares

| Nome | Pronúncia | Tipo | Significado |
|---|---|---|---|
| **Pitla** | /ˈpitla/ | povoado | snow-town |
| **Yir Umni** | /jir ˈumni/ | sintagma | red sea |
| **Nama** | /ˈnama/ | antigo (sem significado) | — |
| **Uskim** | /ˈuskim/ | composto | far water |
| **Imi** | /ˈimi/ | antigo (sem significado) | — |
| **Yirun** | /ˈjirun/ | locativo | at the lake |
| **Miyi** | /ˈmiji/ | antigo (sem significado) | — |
| **Qama** | /ˈŋama/ | antigo (sem significado) | — |
| **Amdyun** | /ˈamdjun/ | composto | wet river |
| **Ayu** | /ˈaju/ | antigo (sem significado) | — |
| **Bila** | /ˈbila/ | povoado | fish-town |
| **Innyagwa** | /ˈinɲaɡwa/ | composto | new grass |
| **Amyir** | /ˈamjir/ | composto | wet sea |
| **Qimun** | /ˈŋimun/ | locativo | at the stone |
| **Pitkim** | /ˈpitkim/ | composto | snow water |
| **Logla** | /ˈloɡla/ | povoado | bird-town |
| **Puun·yir** | /ˈpuːnjir/ | composto | fog sea |
| **Qunyu** | /ˈŋuɲu/ | antigo (sem significado) | — |
| **Wunya** | /ˈwuɲa/ | antigo (sem significado) | — |
| **Memi** | /ˈmemi/ | antigo (sem significado) | — |

## Validação

- Fonemas fora do inventário: nenhum
- Formas que o sândi não reparou: 0
- Grafias que não podem ser lidas de volta: 0
- Avisos dos módulos:
  - Fonotática: encontros no ataque: obstruinte+líquida/glide
  - Fonotática: regras adaptadas às palavras evoluídas
  - Derivação: 27 lacuna(s) e 1 bloqueio(s): nem toda base aceita cada processo, e palavras que já existem impedem a derivada
  - Numerais: conectivo obrigatório na soma, para distinguir 13 de 30
