# Módulo — Orações

Completa a gramática da frase com o que uma língua precisa além da oração simples: **voz** (passiva, antipassiva, reflexivo, recíproco), **demonstrativos** com sistema de distância, **imperativo** e proibitivo, **orações complexas** (coordenação, completivas, condicionais, causais), **possessivos independentes** e **adposições espaciais**.

```
twukuː  plaːni   alenuːɲa
twukuː  plaː-ni  alenuː-ɲa
fish    dog-INS  eat-PASS
'The fish is eaten by the dog.'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico, da sintaxe (casos, concordância e ordem das palavras já decididos), da ortografia e do acento. As frases saem montadas pelas mesmas regras das 12 frases do `grammar.md`.

---

## Onde colocar

```
conlang/
├── clauses/
│   ├── clauses.py
│   └── README.md
└── languages/lang-31/
    ├── clauses.json     ← gerado
    └── clauses.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python clauses/clauses.py --language languages/lang-31
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |
| `--wals PATH` | `../wals/cldf` | Pasta `cldf/` do WALS (opcional) |
| `--no-wals` | — | Usa só as distribuições embutidas |

A pasta precisa ter inventário, fonotática, categorias, morfologia, léxico e sintaxe. O módulo também aproveita, se existirem:

- `vocabulary.json`, para as palavras 'ou', 'quando', 'debaixo', 'atrás'... já criadas pelo vocabulário ampliado;
- `possession.json`, para os possessivos independentes;
- `orthography.json` e `stress.json`, para a grafia.

Rode este módulo **depois** do vocabulário e da posse.

---

## Decisões

### Voz e valência

| Construção | WALS | Opções |
|---|---|---|
| **Passiva** | 107A (43% das línguas têm) | afixo no verbo, ou partícula/auxiliar nas línguas isolantes; o agente aparece em 60% dos casos, no caso instrumental, ablativo ou ergativo, ou com uma adposição nova ('por') |
| **Antipassiva** | 108A | só em línguas ergativas: um afixo tira o objeto da oração, e o agente passa ao caso do sujeito intransitivo |
| **Reflexivo** | — | afixo no verbo (40% das línguas não isolantes) ou pronome 'si mesmo' |
| **Recíproco** | 106A | igual ao reflexivo (como o *se* do português), forma própria, ou sem construção própria |

### Demonstrativos (WALS 41A)

| Graus | Prob. | Termos |
|---|---|---|
| Sem contraste | 3% | um só demonstrativo |
| Dois | 54% | 'este' / 'aquele' (inglês) |
| Três | 38% | 'este' / 'esse' / 'aquele' (português, japonês) |
| Quatro ou mais | 6% | mais 'aquele muito longe' |

Cada grau tem um demonstrativo e um advérbio de lugar ('aqui', 'aí', 'lá'). *This*, *that*, *here* e *there* do léxico são reaproveitados; os graus extras são palavras novas. A posição do demonstrativo no sintagma é a da sintaxe da língua.

### Imperativo e proibitivo (WALS 70A e 71A)

- **Imperativo:** radical puro ('vem!'), afixo próprio, ou nenhum (25% das línguas usam a 2ª pessoa do indicativo). Línguas isolantes usam o verbo sem marca.
- **Proibitivo:** partícula própria ('não coma!' com uma negação especial, como o latim *nē*), em 66% das línguas, ou a negação comum.

### Orações complexas

| Tipo | Palavra |
|---|---|
| Coordenação | 'e' (do léxico), 'ou', 'mas' |
| Completiva | complementizador 'que' (zero em 30% das línguas, como no inglês *I know she came*) |
| Condicional | 'se' |
| Causal | 'porque' |

As palavras vêm do léxico ou do vocabulário ampliado quando existem; senão, são novas. **A ordem segue a da língua:** em línguas OV, o subordinador fica no **fim** da subordinada, e a subordinada vem **antes** da principal (como no japonês: *inu-ga neru **kara**...*); em línguas VO, o subordinador fica no início (como no português).

### Possessivos independentes ('é meu')

| Posse da língua | Possessivo independente |
|---|---|
| Afixos possessivos | uma base nova que recebe o afixo, como nas línguas oceânicas (*a-ku* 'meu') |
| Palavras possessivas | a própria palavra usada sozinha |
| Sem módulo de posse, com genitivo | o pronome no genitivo |
| Sem nada disso | pronome + partícula nova |

### Adposições espaciais

'Debaixo de', 'acima de', 'dentro de', 'atrás de', 'na frente de' e 'perto de', do vocabulário ampliado quando existem. Elas vêm antes ou depois do nome conforme a língua tenha preposições ou posposições, e regem o caso locativo (ou genitivo), quando a língua tem um.

---

## Saídas

### Terminal e `clauses.md`

```
  Passiva: sufixo -nya; agente no caso instrumental
  Reflexivo: afixo ge
  Recíproco: afixo r
  Demonstrativos: 2 graus de distância
  Imperativo: afixo l
  Proibitivo: partícula própria se
  Subordinação: subordinador no fim da subordinada; complementizador qo ('que')

  Completiva ('que')
    ka   plaː  huɬuːwo  ŋo    me
    1SG  dog   sleep    COMP  know
    'I know that the dog sleeps.'
```

O `clauses.md` traz também as tabelas de demonstrativos (com os advérbios de lugar), possessivos independentes, conectivos e adposições, e cada frase escrita na grafia da língua antes da glosa.

### Frases geradas

Passiva, antipassiva (se houver), reflexivo, recíproco, demonstrativos (até três graus), imperativo, proibitivo, coordenação com 'e' e com 'mas', condicional, causal, completiva, possessivo independente e adposição espacial — até 15 frases, todas com glosa interlinear.

### `clauses.json`

```json
{
  "settings": {
    "passive": {"present": true, "type": "affix", "form": ["ɲ", "a"], "position": "suffix",
                "agent": {"type": "case", "case": "instrumental"}},
    "antipassive": {"present": false},
    "reflexive": {"type": "affix", "form": ["ɡ", "e"], "position": "suffix"},
    "reciprocal": {"type": "affix", "form": ["r"], "position": "suffix"},
    "demonstratives": {"terms": ["proximal", "distal"], "forms": {"...": "..."}, "adverbs": {"...": "..."}},
    "imperative": {"type": "affix", "form": ["l"], "position": "suffix", "number": "both"},
    "prohibitive": {"type": "special", "form": ["s", "e"]},
    "connectives": {"or": ["..."], "but": ["..."], "if": ["..."], "because": ["..."], "when": ["..."], "and": ["e", "m"]},
    "complementizer": ["ŋ", "o"],
    "subordinator_position": "final",
    "independent_possessive": {"type": "base_affix", "base": ["p", "j", "a"], "position": "suffix"},
    "adpositions": {"position": "after", "governed_case": "locative", "forms": {"under": ["s", "a", "k", "a"], "...": "..."}}
  },
  "tables": {"demonstratives": ["..."], "connectives": {"...": "..."}, "adpositions": {"...": "..."},
             "independent_possessives": ["..."]},
  "sentences": [{"key": "passive", "title": "Passiva", "words": ["..."], "translation": "...",
                 "written": "Twukuu plaani alenuunya", "ipa": "..."}],
  "metadata": {"seed": 1234567, "sources": {"107A": "WALS 107A (embutido)"}, "notes": []}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import clauses

b = clauses.ClauseBuilder(Path("languages/lang-31"))
data = b.build()
for s in data["sentences"]:
    print(s["written"], "—", s["translation"])
```

---

## Testes

70 línguas geradas (incluindo isolantes, tonais, de raízes consonantais e ergativas): nenhum erro, todas as frases geradas em todas as línguas, e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional e seção no `grammar.md`)
- [ ] O sândi pode apagar um afixo curto (ex: *japil* + *-l* → *japil*); a glosa mostra o afixo, mas a forma fica igual ao radical
- [ ] Orações subordinadas reduzidas (infinitivo, gerúndio, verbos não finitos), comuns em línguas OV
- [ ] Orações relativas com mais estratégias (hoje decididas na sintaxe)
- [ ] Discurso indireto, perguntas encaixadas ('sei **quem** veio') e concordância de tempos
