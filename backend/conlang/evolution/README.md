# Módulo — Evolução linguística

Simula a **história de uma língua**: escolhe leis fonéticas reais (lei de Grimm, lei de Verner, metafonia, lenição românica, palatalização, tonogênese...) conforme um perfil e um tempo, aplica-as em ordem cronológica à língua inteira e gera uma **língua-filha completa** numa pasta nova.

```
EVOLUÇÃO — lang-31 → lang-31-germanic-1500 (germânico, 1500 anos)
  1. ~  200  Lei de Grimm                      152 palavras  /buiː/ → /puiː/ 'fire'
  2. ~  450  Lei de Verner                      25 palavras  /ximʃwiːhuŋ/ → /ximʒwiːhuŋ/ 'water'
  3. ~  650  Metafonia (umlaut)                 53 palavras  /puiː/ → /pyiː/ 'fire'
  4. ~  850  Redução de átonas                  89 palavras  /xlemɣoβuxlaːm/ → /xləmɣəβuxlaːm/ 'tongue'
  5. ~ 1050  Apócope                            36 palavras  /siwətə/ → /siwət/ 'arm/hand'
```

O módulo cobre quatro etapas: **1. mudanças fonéticas**, **2. léxico** (substituição de palavras, mudanças de significado e empréstimos), **3. gramática** (erosão, gramaticalização, ordem das palavras e irregularidades herdadas) e **4. famílias de línguas** (árvore genealógica, cognatos, correspondências sonoras e distâncias).

O módulo **não altera nenhum outro**, e **a língua-mãe não é modificada**: a filha é uma pasta nova.

---

## Onde colocar

```
conlang/
├── evolution/
│   ├── evolution.py      ← o motor e a linha de comando
│   ├── laws.py           ← o catálogo de leis fonéticas
│   ├── lexical.py        ← a evolução do léxico (etapa 2)
│   ├── grammar_evolution.py ← a evolução da gramática (etapa 3)
│   ├── family.py         ← famílias de línguas (etapa 4)
│   └── README.md
└── languages/
    ├── lang-31/                    ← língua-mãe (não muda)
    └── lang-31-germanic-1500/      ← língua-filha (criada)
```

Usa apenas a biblioteca padrão do Python (≥ 3.9) e o `ipa_database/phoible.csv` do projeto, para os traços dos sons.

---

## Uso

```bash
# perfil e tempo
python evolution/evolution.py --language languages/lang-31 --profile germanic --years 1500

# já com ortografia, acento, nomes, posse... e o grammar.md da filha
python evolution/evolution.py --language languages/lang-31 --profile romance --years 2000 --rebuild

# leis escolhidas pelo usuário, nesta ordem
python evolution/evolution.py --language languages/lang-31 --laws grimm,verner,umlaut --rebuild

# com empréstimos de outra língua do projeto
python evolution/evolution.py --language languages/lang-31 --profile celtic --years 2000 \
       --donor languages/lang-77 --borrowing high --rebuild

# evoluir a filha de novo (neta), como o inglês a partir do germânico
python evolution/evolution.py --language languages/lang-31-germanic-1500 --profile english --years 800 --rebuild

# etapa 3: a gramática da filha evolui também (roda sobre a filha criada acima)
python evolution/grammar_evolution.py --language languages/lang-31-romance-2000 --rebuild

# etapa 4: uma família inteira a partir da protolíngua
python evolution/family.py --language languages/lang-31 --branches 3 --sub-branches 2 --years 1500 --rebuild

# ver todas as leis e perfis
python evolution/evolution.py --list-laws
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta da língua-mãe, gerada com o orquestrador |
| `--profile` | `natural` | Tipo de evolução (tabela abaixo) |
| `--years N` | `1000` | Tempo de evolução, em anos |
| `--laws a,b,c` | — | Leis escolhidas, em ordem (ignora perfil e tempo) |
| `--name NOME` | `<mãe>-<perfil>-<anos>` | Nome da pasta da filha |
| `--seed N` | derivada | Semente; por padrão derivada da língua, do perfil e do tempo |
| `--no-lexical` | — | Só mudanças fonéticas: sem substituições, mudanças de significado nem empréstimos |
| `--donor PATH` | — | Língua doadora de empréstimos (outra pasta de `languages/`) |
| `--borrowing` | `medium` com `--donor` | Intensidade dos empréstimos: `none`, `low`, `medium`, `high` |
| `--rebuild` | — | Roda o orquestrador na filha a partir da ortografia, gerando todos os módulos e o `grammar.md` |
| `--list-laws` | — | Lista as leis e os perfis |

---

## Perfis

| Perfil | Leis, em ordem cronológica |
|---|---|
| `germanic` | Grimm, Verner, metafonia, ensurdecimento final, redução de átonas, apócope, degeminação |
| `english` | Grimm, Verner, metafonia, redução de átonas, apócope, Grande Mudança Vocálica, queda de h, simplificação de encontros |
| `romance` | perda da quantidade, palatalização, sonorização, kt → jt/tt, síncope, espirantização, ditongação, degeminação, apócope, nasalização, queda das fricativas, elevação de vogal final |
| `celtic` | perda do p, lenição céltica, apócope, síncope, s → h, assimilação nasal |
| `slavic` | primeira palatalização, monotongação, ruki, lei das sílabas abertas, redução de átonas, ensurdecimento final |
| `indo_iranian` | Grassmann, ruki, s → h, perda da aspiração, monotongação |
| `hellenic` | Grassmann, s → h, queda de h, perda da aspiração, redução de átonas |
| `polynesian` | queda de consoantes finais, perda da sonoridade, s → h, k → ʔ, fusão de líquidas, queda de h, queda de ʔ |
| `sinitic` | glotalização de codas, **tonogênese**, perda da sonoridade, perda da quantidade, queda de consoantes finais |
| `natural` | leis comuns nas línguas do mundo, sorteadas pela frequência aproximada com que aparecem |

O catálogo tem **38 leis**, cada uma com o nome, a família, a descrição e um exemplo real (*latim pater ~ inglês father*). Elas são escritas **por traços fonéticos** (do PHOIBLE), e não por símbolos fixos, para funcionar em qualquer inventário: a lei de Grimm transforma qualquer oclusiva surda em fricativa, com as saídas históricas (*p* → *f*, *t* → *θ*, *k* → *x*) onde elas existem. Leis que dependem do acento (Verner, síncope, apócope, redução de átonas) usam a regra de acento da língua-mãe.

## Tempo

O tempo é uma **aproximação**: de 3 a 5 mudanças fonéticas grandes por milênio, sorteadas. O motor percorre as leis do perfil em ordem e só aceita as que **de fato mudam** pelo menos três palavras da língua (a lei de Grimm não faz nada numa língua sem oclusivas). Se o perfil acabar antes do tempo, completa com leis do perfil natural. Cada lei recebe uma data aproximada na história.

É uma simulação plausível, não uma previsão: línguas reais mudam em ritmos muito diferentes.

---

## Etapa 2 — léxico

Ativada por padrão (desligue com `--no-lexical`). Três processos:

### Substituição lexical

Palavras somem e são trocadas a uma taxa que segue a **glotocronologia** e a **estabilidade de cada significado**:

- Cada significado da lista **Leipzig-Jakarta** tem uma taxa própria, pela ordem de estabilidade de Tadmor, Haspelmath & Taylor (2010): 'fogo', 'nariz', 'ir' e 'água' quase nunca mudam; 'esmagar', 'duro' e 'largo' mudam muito mais. Os demais significados seguem a retenção típica da lista Swadesh-200.
- A probabilidade de troca cresce com o tempo (decaimento exponencial). Nos testes, a retenção média da lista básica ficou em **91% em 500 anos, 84% em 1.000, 76% em 2.000 e 67% em 3.000** — a curva clássica da glotocronologia (cerca de 86% por milênio).
- A palavra nova é uma raiz nova da fonologia da mãe ou, para 'orelha', 'joelho', 'sol' e 'pássaro', **um antigo diminutivo que virou a palavra comum** (se a mãe tem diminutivo na derivação), como o latim *auricula* 'orelhinha' → português *orelha*. Em línguas de raízes consonantais, a palavra nova é um esqueleto consonantal novo (como *k-t-b*).
- Pronomes, numerais e negação não são substituídos.

### Mudanças de significado

Doze mudanças atestadas, aplicadas quando as duas palavras existem na língua (cerca de uma a cada mil e quinhentos anos):

| Tipo | Mudança | Exemplo real |
|---|---|---|
| Restrição | 'pessoa' → 'homem'; 'homem' → 'marido'; 'mulher' → 'esposa' | latim *homo* → francês *homme*; alemão *Mann*, *Frau* |
| Ampliação | 'andar' → 'ir'; 'névoa' → 'nuvem'; 'pé' → 'perna'; 'criança' → 'filho' | latim *nebula* → italiano *nuvola*; inglês *child* |
| Metáfora | 'ver' → 'saber'; 'pele' → 'casca'; 'cabelo' → 'pena' | grego *oîda* 'eu vi' → 'eu sei' |
| Metonímia | 'árvore' → 'madeira'; 'sol' → 'dia' | gótico *triu*; chinês 日 |

A palavra de origem passa a cobrir também o outro significado, e a palavra antiga do destino se perde.

### Empréstimos

Com `--donor`, palavras de outra língua do projeto entram na filha **adaptadas**: cada som estrangeiro vira o mais parecido da filha (pela distância de traços do PHOIBLE), e encontros proibidos ganham uma vogal epentética, como *football* → *futebol*. Os campos mais emprestados são os do WOLD (comida, casa, agricultura, vestuário, sociedade, religião, lei, guerra); o vocabulário básico resiste muito mais. Os empréstimos são recentes: entram depois das leis fonéticas.

### Nas saídas

- O `evolution.md` ganha a seção **Léxico**, com a retenção do vocabulário básico e as listas de palavras substituídas, mudanças de significado e empréstimos, cada uma com a data aproximada e o exemplo real.
- A tabela de **cognatos** marca o que **não é** cognato (substituída, mudança de significado, empréstimo), como num estudo comparativo real.
- No dicionário da filha, cada palavra afetada traz uma nota: "substituiu uma palavra antiga", "antes significava 'andar' (ampliação)", "empréstimo de lang-77 (...)".

---

## Etapa 3 — gramática

Roda **sobre a língua-filha** já criada pelas etapas 1 e 2, com um comando próprio:

```bash
python evolution/grammar_evolution.py --language languages/lang-31-romance-2000 --rebuild
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta da língua-filha (precisa ter o `evolution.json`) |
| `--seed N` | derivada | Semente; por padrão derivada da evolução |
| `--rebuild` | — | Refaz a ortografia, os módulos opcionais e o `grammar.md` da filha |

O tempo é o mesmo da evolução (lido do `evolution.json`). Rodar de novo **não acumula** mudanças: o estado das etapas 1 e 2 é guardado em `.before_grammar/`, e cada execução parte dele. Se a filha for refeita pelo `evolution.py`, o retrato é renovado automaticamente.

```
EVOLUÇÃO DA GRAMÁTICA — lang-31-romance-2000 (2000 anos)
  ~ 1200  Gramaticalização           o demonstrativo 'this' virou artigo definido (twu)
  ~ 1300  Irregularidade herdada     'mother' GEN: a forma antiga evoluiu inteira e ficou irregular: ɲulŋin → ɲulŋiwã
  ~ 1400  Gramaticalização           o numeral 'um' virou artigo indefinido (ɡro)
  ~ 1500  Irregularidade herdada     'eye' PL: ... ãdõmi → ãdwẽmi
```

### Erosão

- Se as leis fonéticas **apagaram todos os afixos** de uma categoria, ela deixa de existir na filha, como os casos do latim que sumiram nas línguas românicas quando as terminações se desgastaram.
- Se dois valores que eram distintos **ficaram com a mesma forma**, o motor registra o **sincretismo** (como dativo e acusativo no inglês *him*).

### Gramaticalização (Heine & Kuteva 2002)

| Caminho | Quando | Paralelo real |
|---|---|---|
| Demonstrativo → artigo definido | a língua não tem artigos (25% por milênio) | latim *ille* 'aquele' → francês *le*, português *o* |
| 'Um' → artigo indefinido | depois do definido (60%) | latim *unus* → francês *un* |
| 'Ir' → futuro | a língua não tem futuro (30% por milênio) | inglês *going to*, francês *je vais chanter* |
| Partícula → afixo | cada partícula gramatical (35% por milênio) | latim *cantare habeo* → português *cantarei* |

A palavra que se gramaticaliza **encolhe** (fica com a primeira sílaba), como acontece nas línguas reais. Os artigos vão para a posição dos demonstrativos; o futuro, para o lado dos complementos do verbo. Se uma língua isolante ganha afixos, o **ciclo tipológico** avança para aglutinante, e a tipologia da filha é atualizada.

### Ordem das palavras

A ordem básica pode mudar, com as taxas por milênio das mudanças mais comuns: **SOV → SVO** (12%, como o latim → românicas), VSO/VOS → SVO (10%), OVS/OSV → SOV (20%). Em mudanças de 1.500 anos ou mais, as adposições podem acompanhar a nova ordem (50%), porque mudam mais devagar que a oração. As frases de exemplo são refeitas na ordem nova.

### Irregularidades herdadas

Nas etapas 1 e 2, raízes e afixos evoluem separadamente e são recompostos regularmente. A etapa 3 compara isso com a **evolução da palavra inteira** (forma da mãe → leis → filha): quando o radical sai diferente, a forma antiga sobrevive como **irregular**, exatamente o mecanismo de *foot*/*feet* (o *-i* do plural causou metafonia no radical, e depois caiu). As candidatas são as palavras mais frequentes ('ir', 'dar', 'ver', 'mulher', 'olho', 'mão'...), e a quantidade cresce com o tempo (de 2 a 10). As formas irregulares substituem as regulares no dicionário, com a nota "irregular, herdado".

### Nas saídas

- O `evolution.md` ganha a seção **Gramática**: cada mudança com a data aproximada, o que aconteceu na língua e o paralelo real.
- O `evolution.json` ganha a chave `"grammar"` com os eventos.
- Com `--rebuild`, o `grammar.md` da filha mostra as categorias novas (artigos, futuro, afixos), a ordem nova e as formas irregulares.

---

## Etapa 4 — famílias de línguas

Transforma uma língua numa **família**: a protolíngua se divide em ramos, cada ramo evolui por um caminho próprio (etapas 1, 2 e 3) e pode se dividir de novo, como o proto-indo-europeu deu o latim, o germânico e o céltico, e o latim deu o português, o espanhol e o francês.

```bash
python evolution/family.py --language languages/lang-31
python evolution/family.py --language languages/lang-31 --profiles romance,germanic,celtic --rebuild
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | A protolíngua |
| `--branches N` | `3` | Ramos principais |
| `--sub-branches N` | `2` | Sub-ramos de cada ramo |
| `--depth N` | `2` | Níveis da árvore (1 a 3) |
| `--years N` | `1500` | Tempo médio de cada divisão; cada ramo varia de 70% a 130% disso |
| `--profiles a,b,c` | sorteados | Perfis dos ramos principais (sem repetir, entre românico, germânico, céltico, eslavo, indo-iraniano, grego, polinésio e chinês) |
| `--no-grammar` | — | Sem a etapa 3 |
| `--name NOME` | `<protolíngua>-familia` | Pasta onde ficam o `family.md` e o `family.json` |
| `--seed N` | derivada | Semente |
| `--rebuild` | — | Gera a ortografia e o `grammar.md` de cada língua (demora mais) |

Os sub-ramos continuam o perfil do ramo ou seguem mudanças comuns (perfil natural). As línguas ficam em `languages/`, com nomes que mostram a árvore: `lang-31-A`, `lang-31-A1`, `lang-31-A2`, `lang-31-B`...

```
lang-31 (protolíngua)
├── lang-31-A  [indo-iraniano, 1400 anos; Regra ruki, s → h, Monotongação...]
│   ├── lang-31-A1  [indo-iraniano, 1400 anos; ...]
│   └── lang-31-A2  [natural, 1250 anos; ...]
├── lang-31-B  [céltico, 1650 anos; Perda do p céltico, Lenição céltica, Apócope...]
└── lang-31-C  [polinésio, 1450 anos; Queda de consoantes finais, Perda da sonoridade...]
```

### A análise comparativa

O `family.md` faz com a família o que a linguística histórica faz com uma família real:

- **Árvore genealógica**, em texto e em diagrama Mermaid (que o GitHub e vários editores desenham), e uma tabela com o perfil, o tempo, as leis e a pasta de cada língua.
- **Cognatos:** cerca de 90 significados básicos em todas as línguas, lado a lado, com as **classes de cognatos** (*a*, *b*, *c*...) como nas tabelas dos manuais. Palavras com a mesma letra descendem da mesma palavra; uma letra nova marca uma inovação num ramo — e as filhas desse ramo a herdam juntas, como acontece nas famílias reais.
- **Correspondências sonoras** (o método comparativo): cada palavra cognata é alinhada à forma da protolíngua (Needleman-Wunsch), e a tabela mostra o reflexo mais frequente de cada som em cada língua. Na família da língua 31, por exemplo, apareceram a perda do *p* no ramo céltico, o *k* > ∅ e o *r* > *l* no polinésio:

  | *proto | A1 | A2 | B1 | B2 | C1 | C2 |
  |---|---|---|---|---|---|---|
  | *p | p | p | **∅** | **∅** | p | p |
  | *k | k | k | k | k | **∅** | **∅** |
  | *r | r | r | r | r | **l** | **l** |

- **Distâncias** (lexicoestatística): a porcentagem do vocabulário em que cada par de línguas ainda usa palavras cognatas. Irmãs compartilham mais entre si (cerca de 60% na língua 31) do que com as primas (35% a 45%), e a matriz recupera a forma da árvore.

O `family.json` traz a árvore, os cognatos, as correspondências e as distâncias em formato estruturado.

---

## O que muda na língua-filha

| Parte | Como evolui |
|---|---|
| Raízes do léxico | aplicando as leis em ordem; a fronteira da palavra só conta quando a raiz de fato fica na borda da forma de citação (raízes sempre seguidas de sufixo não sofrem apócope) |
| Afixos | sufixos com fronteira só à direita, prefixos só à esquerda; um afixo que se apaga vira marca zero, como acontece na erosão real dos afixos |
| Pronomes, partículas, palavras gramaticais | como palavras independentes |
| Padrões vocálicos, apofonia, harmonia | cada vogal segue o destino que teria isolada |
| Esqueletos consonantais | cada consoante muda sozinha, sem perder posições |
| Tons | mantidos quando o número de sílabas não muda; criados pela tonogênese |
| **Inventário** | refeito com os sons que restaram e os que surgiram, com os traços do PHOIBLE |
| **Fonotática** | refeita para o inventário novo e **aprendida das palavras evoluídas** (aceita os encontros e codas que as leis criaram) |
| Formas de citação, paradigmas, frases | recalculados pelo motor e pela sintaxe com as peças novas; as decisões gramaticais (ordem, casos, concordância) são herdadas |

Com `--rebuild`, o orquestrador gera também a ortografia, o acento, os nomes, a posse, a comparação, a derivação, as mudanças sonoras, as irregularidades e o `grammar.md` da filha.

---

## Saídas

Na pasta da filha, além dos JSONs da língua:

### `evolution.md`

1. Perfil, tempo e quantidade de leis
2. Tabela das leis em ordem cronológica: ano aproximado, nome, família, o que mudou, quantas palavras foram afetadas e o exemplo real
3. Exemplos de cada lei na própria língua (antes e depois daquela lei)
4. Inventário: sons perdidos e sons novos
5. **Cognatos**: palavras básicas na mãe e na filha, com grafia e pronúncia

```markdown
| Significado | lang-31 | lang-31-germanic-1500 |
|---|---|---|
| fire | **buii** /buiː/ | **püii** /pyiː/ |
| water | **kimxwiihuq** /kimʃwiːhuŋ/ | **khimjwiihuq** /ximʒwiːhuŋ/ |
| big | **twaa** /twaː/ | **cwaa** /θwaː/ |
```

### `evolution.json`

```json
{
  "parent": "lang-31", "daughter": "lang-31-germanic-1500", "profile": "germanic",
  "profile_name": "germânico", "years": 1500,
  "laws": [{"id": "grimm", "order": 1, "year": 200, "name": "Lei de Grimm", "family": "germânica",
            "description": "p t k → f θ x; b d ɡ → p t k; bʱ dʱ ɡʱ → b d ɡ",
            "example": "latim pater, piscis ~ inglês father, fish", "words_affected": 152,
            "examples": [{"label": "fire", "before": "buiː", "after": "puiː"}]}],
  "cognates": [{"gloss": "FIRE", "label": "fire", "before": "buiː", "after": "pyiː"}],
  "inventory": {"lost": ["d", "kʰ"], "gained": ["f", "x", "y", "ə"], "consonants": 27, "vowels": 15, "tones": 0},
  "phonotactics_changes": ["..."],
  "metadata": {"seed": 1234567, "invalid_paradigm_forms": 0, "variants": {}}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import evolution

ev = evolution.Evolver(Path("languages/lang-31"), profile="celtic", years=2000)
result = ev.build(Path("languages/lang-31-celta"))
for law in result["laws"]:
    print(law["year"], law["name"], law["words_affected"])
```

---

## Testes

- 140 línguas-filhas (20 línguas-mãe × 7 perfis, de 500 a 3.000 anos), incluindo mães tonais, de raízes consonantais e ergativas: nenhum erro, nenhum fonema fora do inventário, e 7 formas principais inválidas em 36 mil (0,02%).
- Com a etapa 4: famílias de 3 ramos × 2 sub-ramos a partir de protolínguas comuns, tonais e de raízes consonantais (estas com cerca de 60% de cognatos com a protolíngua, como as demais); famílias com `--rebuild` com todas as línguas validadas sem fonemas fora do inventário; mesma semente → mesmo `family.json`.
- Refazer uma filha com outro perfil depois da etapa 3 e rodar a etapa 3 de novo: validação limpa e resultado idempotente. As duas correções não mudam nada nas línguas sem raízes consonantais (saídas idênticas byte a byte).
- Com a etapa 3: 72 línguas-filhas (24 mães × 3 perfis, de 1.000 a 3.000 anos): nenhum erro, com 36 gramaticalizações, 52 partículas que viraram afixos, 16 mudanças de ordem, 13 sincretismos e 263 irregularidades herdadas; filhas com essas mudanças geram o `grammar.md` com a validação limpa, e rodar a etapa 3 duas vezes dá o mesmo resultado.
- Com a etapa 2: 64 línguas-filhas (16 mães × 4 perfis, um terço com empréstimos), com 3.183 substituições, 78 mudanças de significado e 92 empréstimos: nenhum erro, nenhum fonema fora do inventário, nenhuma forma inválida, e a retenção seguindo a curva da glotocronologia.
- Todos os perfis com `--rebuild` na língua 31: língua-filha completa, com `grammar.md` e validação limpa.
- Evolução encadeada (filha → neta) funcionando.
- Mesma semente → mesmos arquivos, mesmo com `PYTHONHASHSEED` diferente.

---

## Cuidados e limitações

- **O cabeçalho do `grammar.md` da filha** mostra o comando do orquestrador com a semente da mãe; para recriar a filha, use o comando de evolução (ele é reprodutível).
- **Raízes e afixos evoluem separadamente** e são recompostos pelo motor, com o sândi da língua. As alternâncias que surgiriam da evolução das palavras inteiras (como *foot*/*feet*) entram pela etapa 3, nas formas principais do dicionário; os paradigmas e as frases continuam usando as formas regulares.
- **Com `--rebuild`, os módulos opcionais** (nomes, posse, comparação, derivação...) são gerados de novo para a filha, com as palavras evoluídas, e não herdados da mãe. Herdá-los e evoluí-los é parte da etapa 3.
- Em línguas de raízes consonantais, só as mudanças que não dependem de contexto atingem as consoantes dos esqueletos.
- O tempo é aproximado, e as datas das leis são distribuídas de forma regular ao longo dele.
- **Famílias e pastas existentes:** criar uma família de novo com a mesma protolíngua reescreve as pastas `<protolíngua>-A`, `-B`... da família anterior.
- **Refazer uma filha:** rodar o `evolution.py` de novo sobre uma filha que já passou pela etapa 3 é seguro: a etapa 3 percebe que a filha foi refeita (o `evolution.json` volta sem a chave `"grammar"`) e renova o retrato `.before_grammar/` sozinha.
- As substituições e mudanças de significado recebem uma data, mas são aplicadas na língua-mãe e passam por todas as leis fonéticas (como se tivessem acontecido no início); os empréstimos, ao contrário, entram depois de todas as leis. Um modelo com datas exatas para cada palavra fica para uma versão futura.

## Próximas etapas

- [ ] Famílias: datas absolutas na árvore e reconstrução automática da protolíngua a partir das filhas (o caminho inverso do método comparativo)

- [ ] Etapa 3: fusão de afixos vizinhos em formas cumulativas (aglutinante → fusional) e perífrases que substituem categorias perdidas (casos → preposições)
- [ ] As frases de exemplo ainda não usam os artigos nem o futuro novos (aparecem nas tabelas e no dicionário)
- [ ] **Etapa 4 — famílias:** várias filhas da mesma mãe por caminhos diferentes, com tabela de cognatos de toda a família
- [ ] Integrar ao orquestrador (opção `--evolve` com perfil e tempo)
