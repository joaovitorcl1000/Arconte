# Orquestrador — `generate_language.py`

Gera uma **língua completa com uma única semente**: roda até quinze módulos em sequência, deriva a semente de cada um, salva tudo numa pasta própria da língua, valida a cadeia e monta um documento único (`grammar.md`) com fonologia, ortografia, acento, morfologia, paradigmas, posse, comparação, derivação, irregularidades, sintaxe, dicionário e nomes próprios — o equivalente à página de resultado do Vulgarlang.

```
                              generate_language.py --seed 31
                                           │
  ┌─ núcleo ──────────────────────────────────────────────────────────────────────────┐
  │ tipologia → inventário → fonotática → categorias → motor → léxico → sintaxe       │
  └───────────────────────────────────────────────────────────────────────────────────┘
  ┌─ módulos opcionais ───────────────────────────────────────────────────────────────┐
  │ ortografia → acento → nomes → posse → comparação → derivação → mudanças sonoras   │
  │ → irregularidades                                                                 │
  └───────────────────────────────────────────────────────────────────────────────────┘
                                           │
                              languages/lang-31/grammar.md
```

---

## Instalação

O orquestrador pode ficar na raiz do projeto ou numa pasta própria, como os demais módulos; nos dois casos ele encontra as pastas vizinhas e salva as línguas em `conlang/languages/`:

```
conlang/
├── generate_language/
│   ├── generate_language.py      ← este arquivo
│   └── README.md
├── ipa_database/phoible.csv
│
├── morphological_typology/       ┐
├── phonemic_inventory/           │
├── phonotactics/                 │
├── grammatical_categories/       │ núcleo (obrigatórios)
├── morphological_engine/         │
├── lexicon/                      │
├── syntax/                       │
├── custom_input/                 ┘
│
├── orthography/                  ┐
├── stress/                       │
├── names/                        │
├── possession/                   │ opcionais: se a pasta não existir,
├── comparison/                   │ a etapa é pulada sem erro
├── derivation/                   │
├── sound_changes/                │
├── irregularity/                 ┘
│
├── wals/cldf/                     (opcional: distribuições do WALS atualizadas)
├── concepticon-data/              (opcional: outras listas de conceitos)
└── languages/                     ← criada automaticamente
    └── lang-31/
```

Requer Python ≥ 3.9 e **pydantic ≥ 2** (só para sortear a tipologia; dispensável com `--typology-file`). Os módulos são importados diretamente, sem subprocessos. As pastas `__pycache__` criadas pelo Python podem ser ignoradas.

---

## Uso

```bash
python generate_language/generate_language.py                  # semente aleatória (mostrada na tela)
python generate_language/generate_language.py --seed 31        # sempre a mesma língua
python generate_language/generate_language.py --seed 31 --name elfico
```

### Restrições

Para quem quer uma língua com características específicas:

```bash
python generate_language/generate_language.py --seed 7 --synthesis isolating --order SVO
python generate_language/generate_language.py --seed 8 --fusion fusional --affix-position strongly_prefixing
python generate_language/generate_language.py --seed 9 --complexity simple --no-tones --list swadesh-200
python generate_language/generate_language.py --seed 31 --style diacritics --stress-rule penultimate
```

### Palavras e fonemas do usuário

```bash
python generate_language/generate_language.py --seed 31 --custom minha_lingua.txt
python generate_language/generate_language.py --seed 31 --custom minha_lingua.txt --custom-policy exception
```

O arquivo tem seções `[fonemas]`, `[substantivos]`, `[verbos]`, `[adjetivos]` e `[outras]`, todas opcionais; o que o usuário não informar é sorteado. Veja o README do módulo `custom_input/` para o formato completo. O arquivo é copiado para a pasta da língua como `custom.txt`, e o `grammar.md` ganha a seção "Palavras do usuário" com o relatório.

### Mudanças sonoras do usuário

```bash
python generate_language/generate_language.py --seed 31 --sound-change "a > e / _k" --sound-change "C > ∅ / _#"
python generate_language/generate_language.py --seed 31 --sound-change "{p,t,k} > {b,d,ɡ} / V_V" --no-natural-changes --reflect-spelling
```

As regras usam a notação do Vulgarlang, em IPA. Veja o README do módulo `sound_changes/`.

### Regerar a partir de uma etapa

Gostou da fonologia, mas quer outro vocabulário? `--from` mantém as etapas anteriores e refaz só as seguintes:

```bash
python generate_language/generate_language.py --seed 31 --from lexicon --list leipzig-jakarta
python generate_language/generate_language.py --seed 31 --from orthography --style romance
python generate_language/generate_language.py --seed 31 --from sound_changes --sound-change "a > e / _k"
```

As etapas, em ordem:

| # | Etapa (`--from`) | Módulo | Depende de |
|---|---|---|---|
| 1 | `typology` | morphological_typology | — |
| 2 | `inventory` | phonemic_inventory | 1 |
| 3 | `phonotactics` | phonotactics | 1, 2 |
| 4 | `categories` | grammatical_categories | 1 |
| 5 | `morphology` | morphological_engine | 1–4 |
| 6 | `lexicon` | lexicon | 5 |
| 7 | `syntax` | syntax | 6 |
| 8 | `orthography` | orthography | 2, 3, 6 |
| 9 | `stress` | stress | 2, 3 |
| 10 | `names` | names | 6, 8, 9 |
| 11 | `possession` | possession | 6, 7 |
| 12 | `comparison` | comparison | 7, 11 |
| 13 | `derivation` | derivation | 6, 11, 12 |
| 14 | `sound_changes` | sound_changes | 6, 10, 13 |
| 15 | `irregularity` | irregularity | 12, 14 |

A ordem das etapas 11 a 15 importa: cada módulo evita repetir formas criadas pelos anteriores (a comparação não reutiliza um possessivo como superlativo, por exemplo), e as mudanças sonoras alcançam as palavras derivadas e os nomes. A pasta da língua precisa existir (gerada antes sem `--from`). Se um módulo opcional não estiver instalado, a numeração das etapas se ajusta.

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--seed N` | aleatória | Semente principal |
| `--name NOME` | `lang-<semente>` | Nome da pasta e do documento |
| `--out PATH` | `languages/` | Pasta onde as línguas são salvas |
| `--from ETAPA` | `typology` | Regera a partir desta etapa |
| **Tipologia** | | |
| `--synthesis` | sorteado | `isolating`, `synthetic`, `polysynthetic` |
| `--fusion` | sorteado | `none`, `agglutinative`, `fusional` |
| `--affix-position` | sorteado | `little_affixation`, `strongly_suffixing`, ..., `strongly_prefixing` |
| `--locus` | sorteado | `head_marking`, `dependent_marking`, `double_marking`, `no_marking` |
| `--typology-file PATH` | — | Usa uma tipologia pronta (dispensa o pydantic) |
| **Fonologia** | | |
| `--inventory-mode` | `feature` | `feature` ou `real` (baseado em língua real) |
| `--consonants N`, `--vowels N` | sorteados | Tamanho do inventário |
| `--tones` / `--no-tones` | sorteado | Força presença ou ausência de tons |
| `--complexity` | sorteada | `simple`, `moderate`, `complex` |
| **Léxico e sintaxe** | | |
| `--list` | `all` | `leipzig-jakarta`, `swadesh-200`, `all` ou lista do Concepticon |
| `--order` | sorteada | `SOV`, `SVO`, `VSO`, `VOS`, `OVS`, `OSV` |
| **Ortografia e acento** | | |
| `--style` | sorteado | `english`, `diacritics`, `economic`, `romance` |
| `--stress-rule` | sorteada | `penultimate`, `initial`, `ultimate`, `right_oriented`, `lexical`, `none`... |
| **Nomes próprios** | | |
| `--people N`, `--places N` | `20` | Quantidade de nomes de pessoa e de lugar |
| **Derivação e mudanças sonoras** | | |
| `--derive-per-process N` | `12` | Palavras derivadas por processo |
| `--derive-all` | — | Deriva de todas as bases possíveis |
| `--sound-change "regra"` | — | Regra de mudança sonora do usuário (repetível) |
| `--no-natural-changes` | — | Não sorteia mudanças sonoras naturais |
| `--reflect-spelling` | — | A grafia segue a pronúncia depois das mudanças |
| **Palavras do usuário** | | |
| `--custom PATH` | — | Arquivo com palavras e fonemas do usuário |
| `--custom-policy` | `adapt` | `adapt` (a fonotática aprende com as palavras) ou `exception` |
| **Dados** | | |
| `--phoible`, `--wals`, `--concepticon` | pastas padrão | Dados |
| `--no-wals` | — | Usa só as distribuições embutidas |

---

## Como funciona

### Sementes e reprodutibilidade

Cada módulo recebe uma semente derivada da principal por hash (`sha256("31:lexicon")`). Assim:

- a mesma semente com os **mesmos dados** (PHOIBLE, WALS e listas de conceitos) recria exatamente a mesma língua, byte a byte, inclusive em outra máquina;
- as sementes dos módulos são independentes: regerar o léxico com `--from lexicon` não altera a fonologia.

Atenção: instalar ou remover a pasta `wals/` muda as distribuições usadas e, portanto, as línguas geradas a partir daí. As línguas já geradas continuam salvas nas suas pastas.

Todas as sementes ficam registradas no `manifest.json`. Alguns módulos opcionais (nomes, posse, comparação, derivação, mudanças sonoras, irregularidades) leem a semente da língua no manifesto; numa geração nova, o orquestrador grava um manifesto provisório antes deles, e o definitivo no final.

### Restrições por amostragem com rejeição

Restrições como `--synthesis isolating` ou `--order SVO` não forçam o valor diretamente: o orquestrador sorteia perfis completos até encontrar um que atenda à restrição. Isso preserva as correlações do WALS — uma língua com `--order SVO` recebe preposições, genitivo e adjetivos coerentes com SVO, em vez de herdar escolhas feitas para outra ordem.

Combinações impossíveis (ex: `--synthesis isolating --fusion fusional`) são recusadas com uma mensagem explicando o motivo, sem deixar pasta vazia para trás.

### Validação

Ao final, o orquestrador verifica a cadeia inteira:

- **fonemas do léxico** que não estejam no inventário (sinal de JSONs fora de sincronia);
- **formas inválidas** nos paradigmas e nas formas principais do dicionário;
- **grafias** que não possam ser lidas de volta como os mesmos fonemas;
- **avisos** de todos os módulos (regras de mudança sonora mal escritas, gêneros inexistentes em palavras do usuário...), reunidos num só lugar.

O resultado aparece no terminal, no fim do `grammar.md` e no `manifest.json`.

### Nome da língua

Muitas línguas chamam a si mesmas de "pessoa(s)" ou "gente". O nome nativo é a palavra para *person* (ou *man*, *woman*) no léxico; se a lista não tiver esses conceitos, é uma raiz nova de duas sílabas. Com o módulo de ortografia, o nome é escrito na grafia da língua e ganha uma forma "inglesa", como o *Wïikhoian* do Vulgarlang (*akixontaq* → *Akixontaqian*).

---

## Saída

```
languages/lang-31/
├── grammar.md                     ← documento único da língua
├── manifest.json                  ← sementes, opções, validação
├── dictionary.md, examples.md
├── morphological_typology.json, phonemic_inventory.json, phonotactics.json,
├── grammatical_categories.json, morphology.json, lexicon.json, syntax.json
├── orthography.json / .md         ┐
├── stress.json / .md              │
├── names.json / .md               │
├── possession.json / .md          │ um par por módulo opcional
├── comparison.json / .md          │
├── derivation.json / .md          │
├── sound_changes.json / .md       │
├── irregularity.json / .md        ┘
└── custom.txt                     (só com --custom)
```

### Conteúdo do `grammar.md`

1. **Nome da língua**, nome nativo com grafia e pronúncia, semente e comando para regerar
2. **Fonologia:** grade de consoantes, quadro vocálico, tons, estrutura silábica, encontros e codas; **ortografia** (tabela de grafias); **acento** (regra e exemplos); **mudanças sonoras** (regras e exemplos)
3. **Morfologia:** tipo, processos, sândi, harmonia; categorias; moldes; tabelas de afixos; processos não lineares; palavras gramaticais
4. **Paradigmas:** declinação de um nome, conjugação de um verbo e tabela de pronomes
5. **Posse e determinantes:** possessivos, alienabilidade, posse entre nomes, artigos no plural
6. **Comparação:** formas do adjetivo, comparativo, superlativo e equativo
7. **Derivação:** processos de formação de palavras, com exemplos
8. **Irregularidades:** palavras irregulares e alternâncias das mudanças sonoras
9. **Sintaxe:** decisões de ordem e as 12 frases, cada uma escrita na grafia e com glosa interlinear
10. **Dicionário** no formato do Vulgarlang — **grafia** /pronúncia/ [pronúncia depois das mudanças sonoras] classe 'significado' —, incluindo as palavras derivadas (com a base de onde vêm) e as formas irregulares no lugar das regulares
11. **Nomes próprios:** convenções, pessoas e lugares
12. **Palavras do usuário** (só com `--custom`)
13. **Validação**

As seções dos módulos opcionais só aparecem se eles estiverem instalados.

### Exemplo no terminal

```
Gerando 'lang-31' (semente 31) em languages/lang-31/
  [1/15] Tipologia morfológica    synthetic, agglutinative, strongly_suffixing, dependent_marking (+ reduplication_full)
  [2/15] Inventário fonêmico      24 consoantes, 9 vogais, 0 tons (ref.: Tem)
  [3/15] Fonotática               moderate (CV/CVC/CCV/V)
  [4/15] Categorias gramaticais   7 categorias: number, case, tense, aspect, mood, evidentiality, negation
  [5/15] Motor morfológico        24 células de afixo; moldes ROOT-number-case | ROOT-negation-aspect-tense-mood-evidentiality
  [6/15] Léxico                   231 entradas (all)
  [7/15] Sintaxe                  SOV, postpositions, 12 frases
  [8/15] Ortografia               estilo economic — Akixontaqian, separador em 9 sequências
  [9/15] Acento                   weight_sensitive (right_oriented, peso: coda)
  [10/15] Nomes próprios          20 pessoas, 20 lugares (ex.: Nui, Mukuzwin)
  [11/15] Posse e determinantes   possessivos: affix; posse nominal: dependent; 2 classe(s) de posse
  [12/15] Comparação              locational; grau: affix; superlativo: affix
  [13/15] Derivação               6 processos, 72 palavras derivadas
  [14/15] Mudanças sonoras        3 regras, 37 de 228 palavras mudaram
  [15/15] Irregularidades         2 palavras irregulares, 0 alternâncias

  Língua: Akixontaqian — nativamente akixontaq /ˌakiˈʃontaŋ/ ('person')
  · Fonotática: encontros no ataque: obstruinte+líquida/glide
  · Fonotática: perfil de coda: sonorants

[OK] Língua completa em languages/lang-31/ — comece por grammar.md
```

Esta é a língua 31 gerada sem a pasta `wals/`; com o WALS instalado, a mesma semente produz outra língua.

### Trechos do `grammar.md`

```markdown
### 2. Oração transitiva

**Ozwuu twukuu ukwu.**

    ozwuː  twukuː  ukwu
    woman  fish    see
    'The woman sees the fish.'
```

```markdown
- **akixontaq** /ˌakiˈʃontaŋ/ [ˌaɣiˈʃontaŋ] *n.* 'person' — **PL: akixontaq** (irregular); GEN: akixontan
- **aakyuuwa** /ˈaːkjuːwa/ *n.* 'one who hunts' ← *aakyuu*
- **yapil** /ˈjapil/ [ˈjaβil] *v.i.* 'to come' — PST: yapilpu
```

---

## Uso como biblioteca

```python
import json
import generate_language as gl

pasta = gl.generate(31, name="elfico", synthesis="isolating", order="SVO", tones=False)
lexicon = json.loads((pasta / "lexicon.json").read_text(encoding="utf-8"))
```

As opções de `generate()` têm os mesmos nomes da linha de comando, com `_` no lugar de `-` (`affix_position`, `stress_rule`, `derive_per_process`, `start` para `--from`). Opções repetíveis, como `--sound-change`, ainda não são aceitas por `generate()`; use a linha de comando. A função devolve a pasta da língua. Cada etapa também está disponível isoladamente nos módulos, como descrito nos READMEs de cada um.

---

## Testes

- geração completa (15 etapas) do zero, com e sem `--custom`, com regras de mudança sonora do usuário e `--reflect-spelling`;
- os arquivos de cada módulo opcional saem idênticos aos do módulo rodado sozinho;
- mesma semente → mesmos arquivos (os `grammar.md` só diferem no nome da pasta), mesmo com `PYTHONHASHSEED` diferente;
- `--from` em cada etapa mantém intactos os arquivos das anteriores;
- sem as pastas dos módulos opcionais, o orquestrador ajusta a numeração das etapas e gera o documento sem as seções correspondentes;
- restrições incompatíveis são recusadas sem deixar pasta vazia para trás.

---

## Cuidados

- **Versões dos módulos:** o orquestrador chama as funções públicas de cada módulo; mantenha todos na versão mais recente.
- **Cache do PHOIBLE:** a primeira execução processa o `phoible.csv` e cria `phonemic_inventory/.cache/`; as seguintes são rápidas.
- **`--from` e restrições:** ao regerar a partir de uma etapa, as restrições das etapas mantidas são ignoradas (os arquivos já existem).
- **`--from` e dependências:** como as etapas 11 a 15 dependem umas das outras, regerar uma delas regera também as seguintes.
- **Sobrescrita:** gerar de novo com o mesmo `--name` substitui os arquivos daquela língua.

---

## Próximos passos

- [ ] Contrato com o frontend: entrada e saída em JSON (opções do formulário → língua inteira num único JSON)
- [ ] Aceitar opções repetíveis em `generate()` (como as regras de mudança sonora)
- [ ] Usar as formas irregulares também nos paradigmas e nas frases de exemplo
- [ ] Exportar o `grammar.md` em HTML ou PDF