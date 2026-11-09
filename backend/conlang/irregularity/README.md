# Módulo — Irregularidades

Dá à conlang as **irregularidades** das línguas reais — os "irregularities and quirks" do slogan do Vulgarlang — concentradas, como nelas, nas **palavras mais frequentes**.

```
'go'      apofonia        go-PST      ~~ipu~~          →  o
'person'  plural zero     person-PL   ~~akixontaqmi~~  →  akixontaq
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico, das mudanças sonoras, da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── irregularity/
│   ├── irregularity.py
│   └── README.md
└── languages/lang-31/
    ├── irregularity.json     ← gerado
    └── irregularity.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python irregularity/irregularity.py --language languages/lang-31
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |

A pasta precisa ter inventário, fonotática, categorias, morfologia e léxico. Se houver `comparison.json`, surgem comparativos supletivos; se houver `sound_changes.json`, o módulo procura alternâncias; com `orthography.json` e `stress.json`, as formas saem escritas e acentuadas. Rode este módulo **por último**, depois da comparação e das mudanças sonoras.

---

## Por que nas palavras frequentes

Nas línguas reais, as irregularidades sobrevivem justamente nas palavras mais usadas: por serem ouvidas o tempo todo, elas resistem à regularização (Bybee 1985). Por isso, o módulo escolhe as palavras a partir de listas ordenadas por frequência:

| Classe | Primeiras candidatas |
|---|---|
| Verbos | go, come, give, see, say, eat, do/make, take, know, die... |
| Nomes | person, child, woman, man, eye, hand, foot, tooth, day... |
| Adjetivos | good, bad, big, small, many, old... |

O módulo alterna entre as classes (um verbo, um nome, um adjetivo...) até chegar à quantidade da língua.

## Quantas irregularidades

| Tipo de língua | Palavras irregulares | Exemplo real |
|---|---|---|
| Fusional | 6 a 10 | latim, português, alemão |
| Aglutinante (ou polissintética) | 2 a 5 | turco, finlandês |
| Isolante | 0 a 2 | mandarim, vietnamita |

Nos testes, a média ficou em 8 nas fusionais, 2,9 nas aglutinantes e 0,2 nas isolantes.

---

## Tipos

| Tipo | Classe | O que acontece | Exemplo real |
|---|---|---|---|
| **Supletivismo** | verbos e nomes | uma raiz totalmente diferente em parte do paradigma | *ir* → *fui*; *pessoa* → *gente* |
| **Apofonia** | verbos e nomes | a vogal da raiz muda, e essa mudança **substitui** o afixo | *sing* → *sang*; *foot* → *feet* |
| **Plural zero** | nomes | o plural é igual ao singular | *sheep* → *sheep* |
| **Comparativo supletivo** | adjetivos | uma raiz nova no comparativo e, se houver afixo, no superlativo | *good* → *better* → *best* |

Qual parte do paradigma é irregular:

- **Verbos:** o passado, se a língua tem passado por afixo; senão, o perfectivo, outro aspecto ou outro modo. Todas as formas daquele tempo usam a raiz irregular.
- **Nomes:** o plural (ou outro número não singular), se a língua marca número na palavra.
- **Adjetivos:** o comparativo, se a comparação usa afixo ou palavra de grau.

Em línguas de raízes consonantais, a apofonia não se aplica (os padrões vocálicos já fazem esse papel); o supletivismo usa um esqueleto consonantal novo.

---

## Alternâncias das mudanças sonoras

Se a língua passou pelo módulo de mudanças sonoras, as regras são aplicadas também às **formas flexionadas** de até 80 nomes e 80 verbos. Quando uma regra atinge o radical numa forma e não na outra, surge uma alternância, como no alemão *Hund* [hʊnt] 'cão' / *Hunde* [hʊndə] 'cães': o ensurdecimento final só age quando o *d* fica no fim da palavra.

Mudanças que atingem só o afixo (como *-pu* virando [-βu] entre vogais) não contam, porque não tornam o radical irregular. Na língua 31, por exemplo, as três regras atingem o radical da mesma forma no singular e no plural, então não há alternâncias.

---

## Saídas

### Terminal

```
IRREGULARIDADES — 2 palavras irregulares, 0 alternâncias
  'go' apofonia               go-PST           ipu → o
  'person' plural zero        person-PL        akixontaqmi → akixontaq
```

Exemplo de uma língua fusional:

```
  'come'  supletivismo   come-PST   ŋihblirbip → ŋihŋabip
  'see'   supletivismo   see-PST    ŋihwawip   → ŋihdismisip
  'eat'   apofonia       eat-PST    ŋihdibip   → ŋihdowip
```

### `irregularity.md`

```markdown
| Palavra | Tipo | Forma | Regular seria | Irregular |
|---|---|---|---|---|
| 'go' (verbo) | apofonia | go-PST | ~~ipu~~ | **o** /o/ |
| 'person' (nome) | plural zero | person-PL | ~~akixontaqmi~~ | **akixontaq** /ˌakiˈʃontaŋ/ |
```

Seguido da lista de alternâncias, quando houver: `'cão': SG *hund* /hund/ [hunt] · PL *hunde* /hunde/ [hunde]`.

### `irregularity.json`

```json
{
  "irregulars": [
    {"gloss": "GO", "label": "go", "pos": "verb", "citation": "i",
     "type": "ablaut", "features": {"tense": "past"}, "label_gloss": "go-PST",
     "regular": {"written": "ipu", "ipa": "ipu", "pronunciation": "ˈipu"},
     "irregular": {"written": "o", "ipa": "o", "pronunciation": "o"},
     "root": ["o"], "replaces_affix": true}
  ],
  "alternations": [],
  "settings": {"target": 2, "verb_feature": ["tense", "past"], "noun_feature": ["number", "plural"]},
  "metadata": {"seed": 1234567, "notes": [], "irregular_count": 2, "alternation_count": 0}
}
```

`type` vale `suppletion`, `ablaut`, `zero` ou `suppletive_comparative`. Para os tipos com raiz nova, `root` guarda a raiz irregular, para que outros módulos possam flexioná-la.

### Uso como biblioteca

```python
from pathlib import Path
import irregularity

b = irregularity.IrregularityBuilder(Path("languages/lang-31"))
data = b.build()
for x in data["irregulars"]:
    print(x["label"], x["type"], x["irregular"]["written"])
```

---

## Testes

70 línguas geradas (incluindo isolantes, tonais e de raízes consonantais): nenhum erro, as quantidades seguindo o tipo de língua, e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador: etapa opcional, seção no `grammar.md` e formas irregulares no dicionário e nos paradigmas
- [ ] Fazer o motor morfológico usar as formas irregulares nas frases de exemplo (hoje elas aparecem só nas tabelas deste módulo)
- [ ] Irregularidade em mais de uma célula (como o verbo 'ser', irregular em quase todo o paradigma)
- [ ] Aplicar as mudanças sonoras também aos afixos, criando alomorfia (*-pu* ~ *-βu*)
