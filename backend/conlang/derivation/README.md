# Módulo — Derivação

Cria os **processos de formação de palavras** da conlang e, com eles, **palavras derivadas** a partir do léxico — como o *-ubtu* do Vulgarlang em *liar*, *killer* e *visitor*. É o que permite ampliar o vocabulário além das 231 palavras da lista de conceitos.

```
aakyuu  'to hunt'   →  aakyuuwa  'one who hunts'      (agentivo, sufixo -wa)
twaa    'big'       →  twaadhi   'to become big'      (incoativo, sufixo -dhi)
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico (sândi), da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── derivation/
│   ├── derivation.py
│   └── README.md
└── languages/lang-31/
    ├── derivation.json     ← gerado
    └── derivation.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python derivation/derivation.py --language languages/lang-31
python derivation/derivation.py --language languages/lang-31 --per-process 30
python derivation/derivation.py --language languages/lang-31 --all
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--per-process N` | `12` | Palavras derivadas por processo |
| `--all` | — | Deriva de todas as bases possíveis (centenas de palavras) |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |

A pasta precisa ter inventário, fonotática, categorias, morfologia e léxico. Com `orthography.json` e `stress.json`, as formas saem escritas e acentuadas.

---

## Processos

Cada língua sorteia quais processos tem (no mínimo quatro entre os doze primeiros, mais os novos que forem sorteados). As probabilidades são aproximações a partir de levantamentos tipológicos de formação de palavras (Štekauer, Valera & Körtvélyessy 2012): agentivos e nominalizações existem em quase todas as línguas; privativos e aumentativos são mais raros.

| Processo | Base → resultado | Prob. | Significado gerado |
|---|---|---|---|
| Agentivo | verbo → nome | 85% | 'one who hunts' |
| Ação | verbo → nome | 70% | 'act of eating' |
| Diminutivo | nome → nome | 60% | 'little dog' |
| Causativo | verbo intransitivo → verbo | 60% | 'to make (someone) die' |
| Qualidade | adjetivo → nome | 50% | 'goodness' |
| Instrumento | verbo → nome | 40% | 'thing for cutting' |
| Lugar | verbo → nome | 35% | 'place for sleeping' |
| Incoativo | adjetivo → verbo | 35% | 'to become old' |
| Proprietivo | nome → adjetivo | 35% | 'full of stone' |
| Aumentativo | nome → nome | 30% | 'huge dog' |
| Factitivo | adjetivo → verbo | 30% | 'to make warm' |
| Privativo | nome → adjetivo | 25% | 'without water' |
| **Advérbio** | adjetivo → advérbio | 45% | 'in a good way' |
| **Verbo a partir de nome** | nome → verbo | 40% | 'to do or use water' |
| **Resultativo** | verbo → adjetivo | 45% | 'eaten', 'cut' |
| **Tendência** | verbo → adjetivo | 30% | 'tending to laugh' |
| **Produto do verbo** | verbo → nome | 40% | 'what is sewn' |
| **Relacional** | nome → adjetivo | 35% | 'relating to sea' |

Os seis últimos correspondem aos tipos de afixo do Vulgarlang que faltavam (*Adjective → adverb*, *Noun → verb*, *Verb → adjective*, *Verb → noun that verb physically produces*, *Noun → adjective relating to noun*). Eles são sorteados **à parte**, com um gerador próprio, e processados depois dos demais: assim, uma língua gerada antes desta versão mantém exatamente os mesmos processos e palavras derivadas, e só ganha os novos.

Cada processo tem uma lista de bases preferidas (para o agentivo: *hunt*, *sing*, *fight*, *kill*...; para o instrumento: *cut*, *dig*, *sew*, *tie*...), usadas primeiro; depois, as demais bases da classe certa. Em línguas de adjetivos verbais, os verbos estativos servem de base para os processos adjetivais.

### Formas

| Forma | Quando | Exemplo |
|---|---|---|
| **Afixo** | o caso geral; prefixo ou sufixo conforme a afixação da língua | *aakyuu-wa* 'caçador' |
| **Reduplicação** | diminutivo e aumentativo, em 50% das línguas que têm reduplicação | *ya~ya* 'cãozinho' |
| **Composição** | agentivo com 'pessoa', diminutivo com 'criança' (só se a palavra tiver até duas sílabas) | 'caçar-pessoa' |
| **Perífrase** | causativo e factitivo com 'fazer', privativo com 'não' | 'fazer morrer' |
| **Padrão vocálico** | nominalizações em línguas de raízes consonantais, às vezes com prefixo, como o árabe *maktab* 'escritório' (de *k-t-b*) | *kis-rumamo* 'lugar de dormir' |
| **Morfema livre** | línguas isolantes, quando não há palavra do léxico adequada | 'cortar' + morfema 'coisa' |

Línguas isolantes nunca usam afixos: derivam por composição, perífrase ou reduplicação, como o mandarim.

### Coerência com o resto da língua

- Os afixos novos **nunca repetem** formas que a língua já tem: afixos do motor, palavras gramaticais, possessivos e classificadores (se o módulo de posse já rodou) e formas da comparação (se ela já rodou). Rode a derivação **depois** da posse e da comparação.
- Toda derivação passa pelo **sândi** da língua, e todas as palavras geradas nos testes passaram pela fonotática.
- Nas línguas tonais, a base mantém seus tons e as sílabas novas recebem o tom mais comum.
- Derivadas que coincidem com uma palavra do léxico são marcadas como **homófonas**, como acontece nas línguas reais.

---

## Saídas

### Terminal

```
DERIVAÇÃO — 6 processos, 72 palavras novas
  agentivo ('quem faz')              sufixo -wa
      aakyuu       → aakyuuwa           /ˈaːkjuːwa/  'one who hunts'
  incoativo ('ficar ...')            sufixo -dhi
      qaakye       → qaakyedhi          /ˈŋaːkjeði/  'to become old'
```

### `derivation.md`

1. Tabela com cada processo, sua forma, as classes de entrada e saída e um exemplo
2. Todas as palavras derivadas no formato do dicionário: `**grafia** /pronúncia/ classe 'significado' ← base`

### `derivation.json`

```json
{
  "rules": {
    "agentive": {"from": "verb", "to": "noun", "gloss": "AG", "type": "affix",
                 "position": "suffix", "form": ["w", "a"]},
    "inchoative": {"from": "adjective", "to": "verb", "gloss": "INCH", "type": "affix",
                   "position": "suffix", "form": ["ð", "i"]}
  },
  "derived": [
    {"written": "aakyuuwa", "ipa": "aːkjuːwa", "pronunciation": "ˈaːkjuːwa", "seg": "aːkjuː-wa",
     "process": "agentive", "pos": "noun", "base": "HUNT", "base_written": "aakyuu",
     "meaning": "one who hunts", "gloss": "hunt-AG"}
  ],
  "metadata": {"seed": 1234567, "notes": [], "lexicon_size": 231, "derived_count": 72, "per_process": 12}
}
```

`type` vale `affix`, `reduplication`, `compound`, `compound_new` ou `pattern`. `to` pode ser `noun`, `verb`, `adjective` ou `adverb`.

### Uso como biblioteca

```python
from pathlib import Path
import derivation

b = derivation.DerivationBuilder(Path("languages/lang-31"))
data = b.build(per_process=12)            # ou None para todas as bases

b.derive(b.entries["KILL"], "agentive")   # se a língua tiver o processo agentivo
```

---

## Testes

70 línguas geradas (incluindo isolantes, tonais e de raízes consonantais), 4.848 palavras derivadas com 12 por processo: nenhum erro, nenhuma forma inválida pela fonotática, e a mesma semente gerando o mesmo arquivo. Com `--all`, as mesmas 70 línguas geraram mais de 24 mil palavras derivadas.

Com os seis processos novos: 60 línguas com o sorteio normal e as mesmas 60 com todos os processos novos forçados, 14.340 palavras derivadas, nenhum erro e nenhuma forma inválida. Nas línguas já geradas, os processos e as palavras anteriores saem idênticos.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional, seção no `grammar.md` e palavras derivadas no dicionário)
- [ ] Significados lexicalizados ('one who hunts' → 'hunter'; derivados com sentido especializado)
- [ ] Derivação recursiva (diminutivo de um agentivo)
- [ ] Usar as derivadas para cobrir listas maiores de conceitos (como a do WOLD, com cerca de 1.460)
- [ ] Bases do usuário: derivar também as palavras do `custom_input`
