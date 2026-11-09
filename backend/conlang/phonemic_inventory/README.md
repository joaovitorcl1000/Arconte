# Módulo — Inventário Fonêmico

Este módulo decide **quais sons a conlang tem**. Ele parte do universo de segmentos do PHOIBLE e seleciona as consoantes, vogais e tons de uma língua, salvando o resultado em `phonemic_inventory.json`, que é consumido pela fonotática.

```
ipa_database/phoible.csv   (universo: ~3.100 segmentos, ~2.100 línguas)
        │
        ▼
phonemic_inventory/         ◄── este módulo
  • sorteia o tamanho do inventário
  • escolhe os fonemas (frequência + economia de traços)
  • aplica universais implicacionais
        │
        ▼
phonemic_inventory.json ──► phonotactics/
        ▲
morphological_typology.json (exigências opcionais: tons, nº mínimo de sons)
```

---

## Por que não sortear fonemas um a um

Sortear cada som de forma independente, apenas pela frequência, produz inventários incoerentes: /kʰ/ sem /k/, /ŋ/ sem /n/, /d/ e /ɡ/ sem /b/. Inventários reais são **sistemas**: os mesmos contrastes (vozeamento, aspiração, comprimento, nasalidade) atravessam vários pontos de articulação, e a presença de sons marcados implica a de sons menos marcados. O módulo modela as duas coisas.

---

## Dados

O módulo lê diretamente `../ipa_database/phoible.csv` e usa apenas a biblioteca padrão do Python (≥ 3.9).

| Tratamento | Motivo |
|---|---|
| Um inventário por `Glottocode` (o de menor `InventoryID`) | Línguas descritas por várias fontes não pesam mais que as outras |
| Segmentos com `Marginal = TRUE` descartados | Sons marginais (empréstimos, onomatopeias) distorcem as frequências |
| Linhas sem `Glottocode` descartadas | Não há como deduplicar |
| Símbolos normalizados em Unicode NFD | Garante comparação consistente entre símbolos |
| Transcrições ambíguas com `\|` (ex: `t̪\|t`) excluídas do sorteio | Não representam um fonema definido |
| Ditongos excluídos por padrão | Na maioria das análises são sequências, não fonemas (use `--diphthongs` para incluí-los) |
| Segmentos presentes em menos de 10 línguas ignorados no sorteio | Evita sons extremamente raros |

**Frequência** de um segmento = fração das línguas (deduplicadas) que o possuem.

Na primeira execução o CSV é processado e salvo em `.cache/phoible_stats.json`. Execuções seguintes leem o cache, que é reconstruído automaticamente se o CSV mudar (ou com `--rebuild-cache`).

### Relação com `ipa_database/phoible_inventory.json`

Aquele arquivo lista os 3.141 símbolos distintos com sua classe, mas sem frequências, traços ou línguas, então não serve como fonte para este módulo. Ele também não está totalmente em NFD: ao cruzá-lo com a saída deste módulo, normalize os símbolos antes de comparar.

---

## Modos de geração

### `feature` (padrão)

Constrói o inventário segmento a segmento.

1. **Tamanho:** sorteia o par (nº de consoantes, nº de vogais) de uma língua real, preservando a correlação entre os dois.
2. **Vogais iniciais:** semeia o triângulo vocálico básico (vogal baixa, alta anterior, alta posterior arredondada), normalmente /a i u/.
3. **Crescimento:** adiciona segmentos sorteados com peso

```
score = frequência^commonness × (1 + economy_weight × economia) × penalidade
```

- **Economia de traços** (Clements 2003): cada *parceiro de série* já presente soma 1 ponto, ou 2 se aquele contraste já é usado em outro par do inventário. Parceiros de série são segmentos que diferem apenas em traços de série:

  | Traço | Contraste |
  |---|---|
  | `periodicGlottalSource` | vozeamento (p/b) |
  | `spreadGlottis` | aspiração (k/kʰ) |
  | `constrictedGlottis`, `raisedLarynxEjective` | ejetividade (k/kʼ) |
  | `loweredLarynxImplosive` | implosão (b/ɓ) |
  | `long` | comprimento (a/aː) |
  | `nasal` | nasalidade vocálica (a/ã) |

  Exemplo: com /p t k b/ no inventário, /d/ e /ɡ/ ganham peso extra, porque o contraste de vozeamento já está em uso.

- **Penalidade** (× 0,01): candidatos com o mesmo esqueleto de um segmento presente sem serem parceiros de série, como /t̪/ ao lado de /t/ ou /s̺/ ao lado de /s/. Isso evita quase-duplicatas.

### `real`

Parte do inventário de uma língua real do PHOIBLE e o modifica:

1. Remove cerca de 15% dos segmentos (`--mutation`), com preferência pelos mais raros.
2. Completa o inventário com o mesmo mecanismo de pontuação do modo `feature`, sem readicionar os sons removidos.
3. Herda o sistema tonal da língua-base, se houver.

É o modo mais seguro para obter inventários naturalistas; o modo `feature` gera mais variedade.

---

## Universais implicacionais

Depois da geração, uma etapa de reparo verifica implicações do tipo "se a língua tem X, tem Y":

| Tipo | Exemplos |
|---|---|
| Modificadores | /kʰ/ → /k/, /kʷ/ → /k/, /tʼ/ → /t/, /aː/ → /a/, /ã/ → /a/, /ⁿd/ → /d/ |
| Vozeamento em obstruintes | /b/ → /p/, /z/ → /s/, /ɡ/ → /k/ |
| Implosivas | /ɓ/ → /b/ |
| Nasais | /ŋ/ → /n/, /ɲ/ → /n/, /ɳ/ → /n/ |

Cada violação é resolvida de forma probabilística, já que universais são tendências e não leis:

| Probabilidade | Ação |
|---|---|
| 75% | Adiciona o segmento implicado |
| 20% | Remove o segmento marcado |
| 5% | Tolera a lacuna (ex: o árabe tem /b/ sem /p/) |

Todas as alterações ficam registradas em `metadata.changes`.

---

## Tons

- Sem indicação, a língua é tonal com a mesma probabilidade observada no PHOIBLE.
- Quando é tonal, o sistema tonal inteiro é copiado de uma língua tonal real, o que garante coerência.
- No modo `real`, os tons vêm da língua-base.
- `--tones` / `--no-tones` forçam a escolha.

---

## Integração com a tipologia morfológica

Se `../morphological_typology/morphological_typology.json` existir, o módulo traduz os processos ativos em exigências:

| Processo morfológico | Exigência no inventário |
|---|---|
| `tonal_morphology` | Tons obrigatórios |
| `apophony` | Pelo menos 5 vogais |
| `transfixation` | Pelo menos 18 consoantes |

Use `--no-morph` para ignorar o arquivo.

---

## Uso

```bash
cd phonemic_inventory

python phonemic_inventory.py                          # modo feature, aleatório
python phonemic_inventory.py --seed 42                # reprodutível
python phonemic_inventory.py --mode real --seed 7     # baseado em língua real
python phonemic_inventory.py --consonants 22 --vowels 5 --no-tones
python phonemic_inventory.py --commonness 3           # inventário mais "comum"
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--mode {feature,real}` | `feature` | Modo de geração |
| `--seed N` | aleatória | Semente para reprodutibilidade |
| `--consonants N` | sorteado | Força o nº de consoantes |
| `--vowels N` | sorteado | Força o nº de vogais |
| `--tones` / `--no-tones` | sorteado | Força presença ou ausência de tons |
| `--diphthongs` | desligado | Permite ditongos como fonemas |
| `--mutation X` | `0.15` | Modo `real`: fração do inventário trocada |
| `--economy X` | `1.5` | Peso da economia de traços |
| `--commonness X` | `2.0` | Expoente da frequência (1 = proporcional; maior = sons mais comuns) |
| `--phoible PATH` | `../ipa_database/phoible.csv` | Caminho do CSV |
| `--morph PATH` | `../morphological_typology/morphological_typology.json` | Caminho da tipologia |
| `--no-morph` | — | Ignora a tipologia morfológica |
| `--rebuild-cache` | — | Reprocessa o CSV |
| `-o PATH` | `phonemic_inventory.json` | Arquivo de saída |

### Exemplo de saída no terminal

```
CONSOANTES (16)
              labial        coronal       palatal       velar         labial-velar
stop          b p pʼ        d t                         k
affricate                   d̠ʒ t̠ʃ
nasal         m             n             ɲ             ŋ
rhotic                      r
lateral                     l
approximant                               j                           w

VOGAIS (6)
  i  u  ɛ  a  uː  aː

TONS (4)
  ˥˩  ˦  ˨  ˩˥

Tamanho inspirado em: Boro
Alterações: +t̠ʃ (implicado por /d̠ʒ/), -v (sem /f/), tons copiados do sistema de Iyive (iyiv1238)
```

### Uso como biblioteca

```python
from phonemic_inventory import (
    load_stats, InventoryGenerator, GeneratorOptions,
    read_morph_requirements, DEFAULT_PHOIBLE, DEFAULT_MORPH,
)

stats = load_stats(DEFAULT_PHOIBLE)
req = read_morph_requirements(DEFAULT_MORPH)
opts = GeneratorOptions(mode="feature", seed=42, n_vowels=5)

result = InventoryGenerator(stats, opts, req).generate()
print([c["ipa"] for c in result["consonants"]])
```

---

## Formato de `phonemic_inventory.json`

```json
{
  "consonants": [
    {
      "ipa": "p",
      "frequency": 0.8582,
      "manner": "stop",
      "place": "labial",
      "features": {"consonantal": "+", "sonorant": "-", "labial": "+", "...": "..."}
    }
  ],
  "vowels": [
    {
      "ipa": "a",
      "frequency": 0.8711,
      "height": "low",
      "backness": "central",
      "rounded": false,
      "long": false,
      "nasal": false,
      "features": {"...": "..."}
    }
  ],
  "tones": [{"ipa": "˦", "frequency": 0.2459}],
  "counts": {"consonants": 16, "vowels": 6, "tones": 4},
  "metadata": {
    "mode": "feature",
    "seed": 3,
    "targets": {"consonants": 16, "vowels": 6},
    "reference_language": {"name": "Boro", "glottocode": "..."},
    "morphology_requirements": {},
    "changes": ["+t̠ʃ (implicado por /d̠ʒ/)", "..."],
    "phoible_languages": 2157
  }
}
```

Cada fonema carrega os **38 traços distintivos do PHOIBLE**, então a fonotática pode calcular sonoridade sem reabrir o CSV. Os rótulos `manner`, `place`, `height` e `backness` são derivados dos traços e servem para exibição e regras simples.

| Campo | Valores possíveis |
|---|---|
| `manner` | `stop`, `affricate`, `fricative`, `nasal`, `rhotic`, `lateral`, `approximant`, `click` |
| `place` | `labial`, `coronal`, `palatal`, `velar`, `labial-velar`, `uvular`, `laryngeal` |
| `height` | `high`, `mid`, `low` |
| `backness` | `front`, `central`, `back` |

> Os valores de frequência e de `phoible_languages` acima são ilustrativos; os reais dependem da versão do PHOIBLE.

---

## Cuidados

- **Unicode:** todos os símbolos saem em NFD. Qualquer módulo que compare símbolos deve normalizar da mesma forma.
- **`ɡ` ≠ `g`:** o PHOIBLE usa o caractere IPA `ɡ` (U+0261), não o `g` do teclado (U+0067).
- **Sons incomuns:** com `--commonness 2` ainda aparecem ocasionalmente sons raros (ex: /ȴ/, /ŋ̥/). Aumente o valor para inventários mais conservadores.
- **Cache:** adicione `.cache/` ao `.gitignore`.

---

## Limitações e próximos passos

- [ ] Geração tonal própria (hoje os sistemas são copiados de línguas reais)
- [ ] Mais universais implicacionais (ex: vogais médias implicam /i a u/; fricativas implicam /s/)
- [ ] Usar o tamanho do inventário do WALS (1A, 2A) como alternativa ao PHOIBLE
- [ ] Ponderar a escolha da língua de referência por família ou região
- [ ] Gerar `ipa_database/phoible_inventory.json` a partir do cache deste módulo, para manter o frontend consistente

---

## Referências

- Moran, S. & McCloy, D. (eds.) (2019) — *PHOIBLE 2.0*. https://phoible.org
- Clements, G. N. (2003) — *Feature economy in sound systems*. Phonology 20(3)
- Maddieson, I. (1984) — *Patterns of Sounds*. Cambridge University Press
- Hammarström, H. et al. — *Glottolog*. https://glottolog.org