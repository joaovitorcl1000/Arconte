# Módulo — Mudanças sonoras

Aplica **regras de mudança sonora** às palavras da conlang, como o campo "Sound changes" do Vulgarlang e na mesma notação. As regras podem vir do usuário ou ser sorteadas entre mudanças comuns nas línguas do mundo. O resultado é a **pronúncia fonética** de cada palavra: a forma do dicionário continua entre barras, e a forma depois das mudanças aparece entre colchetes.

```
yapil  /japil/  →  [ˈjaβil]  'to come'      (p > b entre vogais, depois b > β)
ponpyel /ponpjel/ → [ˈpompjel]  'back'       (n > m antes de labial)
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── sound_changes/
│   ├── sound_changes.py
│   └── README.md
└── languages/lang-31/
    ├── sound_changes.json     ← gerado
    └── sound_changes.md       ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
# mudanças naturais sorteadas
python sound_changes/sound_changes.py --language languages/lang-31

# só as regras do usuário
python sound_changes/sound_changes.py --language languages/lang-31 --no-natural \
       --rule "a > e / _k" --rule "C > ∅ / _#"

# regras num arquivo, e a grafia passa a seguir a pronúncia nova
python sound_changes/sound_changes.py --language languages/lang-31 \
       --rules-file minhas_regras.txt --reflect-spelling
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--rule "..."` | — | Uma regra do usuário; pode repetir |
| `--rules-file PATH` | — | Arquivo com uma regra por linha (linhas com `#` são comentários) |
| `--no-natural` | — | Não sorteia mudanças naturais (usa só as do usuário) |
| `--reflect-spelling` | — | A grafia segue a pronúncia nova ("Reflect sound changes in spelling") |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua |

As regras naturais vêm primeiro e as do usuário depois, todas aplicadas **em ordem**: cada regra age sobre o resultado da anterior, como na história real das línguas.

---

## Notação

| Regra | Significado |
|---|---|
| `a > e` | todo *a* vira *e* |
| `a > e / _k` | *a* vira *e* antes de *k* |
| `a > e / #_` | *a* vira *e* no início da palavra |
| `C > ∅ / _#` | consoantes caem no fim da palavra |
| `{p,b} > m / V_V` | *p* ou *b* viram *m* entre vogais |
| `{p,t,k} > {b,d,ɡ} / V_V` | cada som vira o correspondente da segunda lista |
| `∅ > e / #_s` | insere *e* antes de *s* no início da palavra |
| `h > ∅` | apaga todo *h* (`∅`, `0` ou nada à direita de `>` apagam) |

| Símbolo | Significado |
|---|---|
| `_` | a posição do som que muda (exatamente um por ambiente) |
| `#` | fronteira da palavra |
| `{a,b,c}` | qualquer um desses sons |
| `C`, `V` | consoante, vogal |
| `P`, `F`, `N`, `L`, `G` | oclusiva (e africada), fricativa, nasal, líquida, semivogal |

**As regras usam IPA, não a grafia:** na língua 31, *ʃ* é escrito *x*, então a regra é `ʃ > s`, não `x > s`. Uma regra que não muda nenhuma palavra gera um aviso dizendo isso. Regras mal escritas (sem `>`, com dois `_`, listas de tamanhos diferentes) são ignoradas, com a explicação.

Limitações da notação: o alvo é sempre um único som (ou lista, ou classe); sequências como `ts > s` não são aceitas.

---

## Mudanças naturais

Sem `--no-natural`, o módulo sorteia de 2 a 4 mudanças entre as mais comuns nas línguas do mundo, montadas com os sons que a língua de fato tem:

| Mudança | Regra (exemplo) | Exemplo real |
|---|---|---|
| Sonorização entre vogais | `{p,t,k} > {b,d,ɡ} / V_V` | latim *lupus* → espanhol *lobo* |
| Espirantização entre vogais | `{b,d,ɡ} > {β,ð,ɣ} / V_V` | espanhol *lado* [laðo] |
| Ensurdecimento final | `{b,d,ɡ} > {p,t,k} / _#` | alemão *Hund* [hʊnt] |
| Palatalização | `{k,ɡ} > {t̠ʃ,d̠ʒ} / _{i,e}` | italiano *cento* [t̠ʃɛnto] |
| Assimilação nasal | `n > m / _{p,b}`, `n > ŋ / _{k,ɡ}` | português *também* |
| Queda de *h* | `h > ∅ / V_V` | — |
| Debucalização | `s > h / V_V` | espanhol caribenho *mismo* [mihmo] |
| Elevação de vogal final | `e > i / _#`, `o > u / _#` | português *leite* [lejt͡ʃi] |
| Apócope | `V > ∅ / VC_#` | latim *bene* → francês *bien* |

Cada candidata é testada contra o léxico, e só entra se mudar **pelo menos três palavras**, para que nenhuma regra fique sem efeito.

---

## Acento e grafia

- **Acento.** Calculado na forma antiga e mantido na mesma sílaba depois das mudanças, como acontece historicamente (*yapil* /ˈjapil/ → [ˈjaβil]). Se uma mudança apaga uma sílaba, o acento é recalculado na forma nova.
- **Tons.** Mantidos quando o número de sílabas não muda.
- **Grafia.** Sem `--reflect-spelling`, a grafia continua sendo a da forma do dicionário (como no inglês, em que a escrita guarda pronúncias antigas). Com `--reflect-spelling`, a grafia segue a pronúncia nova, e **sons que não existiam** (como [β] e [ɣ] na língua 31) ganham letras próprias no estilo da ortografia da língua.

---

## Alcance

As mudanças são aplicadas às palavras do léxico e, se existirem, às palavras derivadas (`derivation.json`) e aos nomes próprios (`names.json`). Rode este módulo **depois** desses dois.

As formas das tabelas de flexão (`morphology.json`) e das frases (`syntax.json`) não são alteradas: as mudanças descrevem a pronúncia fonética das palavras do dicionário, como no Vulgarlang. Formas irregulares que nascem das mudanças ficam para o módulo de irregularidades.

---

## Saídas

### Terminal

```
MUDANÇAS SONORAS — 3 regras; 37 de 228 palavras mudaram
  1. {p,t,k} > {b,d,ɡ} / V_V      (natural, 25 palavras)
     sonorização entre vogais (como no espanhol: lupus → lobo)
       yapil          /japil/ → [ˈjabil]  'to come'
  2. {b,d,ɡ} > {β,ð,ɣ} / V_V      (natural, 33 palavras)
     espirantização entre vogais (como no espanhol: lado [laðo])
       yabil          /jabil/ → [ˈjaβil]  'to come'
  Sons novos: [ɣ] [β]
```

Cada exemplo mostra o efeito **daquela regra** (o antes e o depois dela), não o resultado final.

### `sound_changes.md`

1. Resumo: quantas regras, quantas palavras mudaram, sons novos
2. Tabela das regras, com origem (natural ou usuário), palavras afetadas e exemplo
3. Todas as palavras que mudaram: `**grafia** /forma do dicionário/ [pronúncia] 'significado'`

### `sound_changes.json`

```json
{
  "rules": [
    {"text": "{p,t,k} > {b,d,ɡ} / V_V", "source": "natural",
     "description": "sonorização entre vogais (como no espanhol: lupus → lobo)",
     "changed_words": 25,
     "examples": [{"before": "japil", "after": "jabil", "word": "japil", "label": "to come",
                   "before_written": "yapil", "after_phonetic": "ˈjabil"}]}
  ],
  "entries": [
    {"gloss": "COME", "label": "to come", "pos": "verb", "underlying": "japil", "changed": "jaβil",
     "rules": [0, 1], "written": "yapil", "changed_written": "yapil", "phonetic": "ˈjaβil"}
  ],
  "derived": ["..."],
  "names": ["..."],
  "new_sounds": ["β", "ɣ"],
  "new_graphemes": {},
  "settings": {"natural": true, "reflect_spelling": false},
  "metadata": {"seed": 1234567, "changed_words": 37, "total_words": 228, "errors": [], "warnings": []}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import sound_changes as sc

s = sc.SoundChanger(Path("languages/lang-31"))
data = s.run(["a > e / _k", "C > ∅ / _#"], natural=False)

r = sc.Rule("{p,t,k} > {b,d,ɡ} / V_V", s.symbols)
r.apply(["j", "a", "p", "i", "l"], s.classify)    # ['j', 'a', 'b', 'i', 'l']
```

---

## Testes

70 línguas geradas (incluindo tonais e de raízes consonantais), com e sem regras do usuário e com e sem `--reflect-spelling`: nenhum erro; em média 31% das palavras mudaram; e a mesma semente gerando o mesmo arquivo.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional, pronúncia [...] no dicionário e regras como opção `--sound-change`)
- [ ] Alvos com mais de um som (`ts > s`) e exceções (`// _#`)
- [ ] Mudanças condicionadas pelo acento (redução de vogais átonas)
- [ ] Aplicar as mudanças também às formas flexionadas, criando irregularidades nos paradigmas
- [ ] Línguas-filhas: aplicar conjuntos diferentes de regras à mesma língua para gerar uma família com cognatos
