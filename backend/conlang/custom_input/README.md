# Módulo — Palavras e fonemas do usuário

Permite que o usuário fixe os **sons** da língua e coloque **palavras que ele mesmo criou**, como nos campos do Vulgarlang. Tudo o que não for informado continua sendo sorteado: não existe número mínimo de palavras.

```
minha_lingua.txt ──► custom_input ──┬──► inventário   (fonemas declarados ou somados)
                                    ├──► fonotática   (regras adaptadas às palavras)
                                    ├──► motor        (palavras gramaticais: 'not', 'the')
                                    └──► léxico       (palavras travadas nos seus conceitos)
```

Este módulo não roda sozinho: é usado pelo orquestrador. **Nenhum outro módulo precisa ser alterado**: ele só lê e ajusta os JSONs que os módulos produzem, e usa as funções públicas deles.

```bash
python generate_language/generate_language.py --seed 31 --custom minha_lingua.txt
```

---

## Onde colocar os arquivos

```
conlang/
├── generate_language/
│   └── generate_language.py   ← versão nova (ganhou --custom)
├── custom_input/              ← pasta nova
│   ├── custom_input.py
│   └── README.md
├── minha_lingua.txt           ← o arquivo do usuário (pode ficar em qualquer lugar)
├── ...                        (demais módulos: sem alteração)
└── languages/
    └── lang-31/
        ├── custom.txt         ← cópia do arquivo usado, para reproduzir a língua
        └── grammar.md         ← ganha a seção "Palavras do usuário"
```

O arquivo do usuário pode ter qualquer nome e ficar em qualquer pasta; basta passar o caminho em `--custom`. Use o `minha_lingua.txt` entregue junto como modelo.

---

## Formato do arquivo

```
# Linhas com # são comentários. Todas as seções são opcionais.

[fonemas]
consoantes: p t k b d ɡ m n f s ʃ x h l r j w
vogais: a e i o u
# tons: ˥ ˩

[substantivos]
# forma | significado | gênero (opcional)
wad    | dog          | masculino
imme   | sea
xin    | tool, weapon

[verbos]
# forma | significado | transitividade (opcional)
kip    | bite         | transitivo
rima   | sleep        | intransitivo

[adjetivos]
nos    | good

[outras]
# forma | significado | classe
ti     | I            | pronome
ɡiʃ    | the          | artigo
ka     | not          | negação
```

### Seções

| Seção | Nomes aceitos | Terceiro campo (opcional) |
|---|---|---|
| Fonemas | `[fonemas]`, `[phonemes]` | — (linhas `consoantes:`, `vogais:`, `tons:`) |
| Substantivos | `[substantivos]`, `[nomes]`, `[nouns]` | gênero: `masculino`, `feminino`, `neutro`, `animado`, `inanimado`, `humano`, `classe 3` |
| Verbos | `[verbos]`, `[verbs]` | `transitivo`, `intransitivo`, `bitransitivo`, `estativo` |
| Adjetivos | `[adjetivos]`, `[adjectives]` | — |
| Outras | `[outras]`, `[other]` | classe: `artigo`, `pronome`, `conjunção`, `preposição`, `advérbio`, `numeral`, `negação`, `interjeição`, `partícula`, `demonstrativo`, `interrogativo`, `quantificador` |
| Genérica | `[palavras]`, `[words]` | — (a classe vem do conceito do Concepticon) |

### Formas

- Escritas em **IPA**, uma palavra por linha, sem espaços.
- Divididas em fonemas pelo maior símbolo do PHOIBLE que casa: em `t̠ʃʰapo`, `t̠ʃʰ` é um fonema só.
- `ˈ`, `ˌ`, `.` e `-` são ignorados, então `ˈim.me` vale como `imme`.
- Atalhos de teclado aceitos: `g` vira `ɡ` (o símbolo IPA usado pelo PHOIBLE) e `'` vira `ʼ`.

### Significados

- Em **inglês**, para casar com os conceitos do Concepticon (`dog`, `bite`, `sea`). Prefixos como `to` são ignorados (`to bite` = `bite`).
- Vários significados separados por vírgula ou ponto e vírgula (`tool, weapon`): a palavra ocupa todos os conceitos encontrados, como as palavras polissêmicas do Vulgarlang.
- Significados sem conceito correspondente (ex: `frog`, que não está nas listas) viram **entradas novas** do dicionário.
- Se o conceito existir no Concepticon embutido mas não na lista escolhida (`--list leipzig-jakarta`), ele é acrescentado à lista.

---

## O que acontece em cada etapa

### Inventário

| Situação | Comportamento |
|---|---|
| Com `[fonemas]` | A língua usa **exatamente** os fonemas declarados. Palavras com outros sons são ignoradas, com aviso indicando o símbolo |
| Sem `[fonemas]` | O inventário é sorteado normalmente e os fonemas das palavras do usuário são **somados** a ele |

Símbolos declarados que não existem no PHOIBLE interrompem a geração com uma mensagem indicando quais são. Fonemas listados na seção errada (ex: `j` em `vogais`) são reclassificados com aviso.

### Fonotática (`--custom-policy`)

| Política | Comportamento |
|---|---|
| `adapt` (padrão) | A fonotática **aprende com as palavras do usuário** |
| `exception` | As regras sorteadas não mudam; palavras que as violam ficam marcadas como **exceção fonotática** (como empréstimos) |

Na política `adapt`, as palavras do usuário são silabificadas pela sonoridade e:

- moldes silábicos novos (ex: CVC numa língua só CV) passam a ser permitidos;
- encontros no ataque, codas e encontros em coda das palavras são acrescentados às regras;
- palavras começando por vogal tornam o ataque opcional; vogais em sequência liberam o hiato; consoantes proibidas no início de palavra são liberadas se o usuário as usar ali;
- os moldes das palavras do usuário **ganham peso no sorteio**, então as palavras geradas ficam parecidas com as dele. O peso cresce com o número de sílabas informadas, até metade do total (com 40 sílabas ou mais);
- cada molde com coda garante também a versão sem coda (CVC → CV, VC → V).

Palavras sem vogal ou com encontros fora do que a fonotática representa (ataques com mais de 3 consoantes, codas com mais de 2) ficam como exceção.

### Motor morfológico

Palavras do usuário com os significados abaixo **substituem as palavras gramaticais sorteadas**, então aparecem também nas frases de exemplo:

| Significado | Substitui |
|---|---|
| `not`, `no` | partícula de negação |
| `the` | artigo definido |
| `a`, `an` | artigo indefinido |
| `one` | artigo indefinido, quando ele deriva do numeral "um" |

Se a gramática da língua não tiver aquela palavra livre (ex: o definido é um sufixo), a palavra do usuário entra só no dicionário, e o relatório explica o motivo.

### Léxico

O léxico é gerado normalmente pelo módulo `lexicon`; em seguida, este módulo aplica as palavras do usuário sobre o resultado:

- A palavra ocupa o conceito e fica **travada**: substitui a forma gerada, e compostos ou colexificações que existiam naquele conceito são desfeitos.
- Se outro conceito tinha sido colexificado com aquele (ex: *wife* com a mesma palavra de *woman*), ele passa a usar a forma do usuário, mantendo a colexificação.
- **Nenhuma palavra gerada** fica idêntica a uma palavra do usuário: as que coincidirem são regeradas.
- Gênero, classe flexional e transitividade não informados são atribuídos pelas mesmas regras das palavras geradas. Um gênero que não existe na língua (ex: `masculino` numa língua animado/inanimado) é substituído, com aviso.
- **Pronomes** (`I`, `you`, `you (pl)`, `he`, `she`, `it`, `we`, `we (inclusive)`, `we (exclusive)`, `they`) entram na célula correspondente da tabela de pronomes.
- Adjetivos do usuário viram verbos estativos se a língua tiver adjetivos verbais.
- As palavras do usuário são **flexionadas normalmente** pelo motor (plural, caso, concordância) e aparecem nas frases de exemplo quando o conceito é usado lá (*dog*, *woman*, *see*, *sleep*...).
- No dicionário, aparecem com a nota "palavra do usuário ★".

**Raízes consonantais:** em línguas com transfixação, as palavras são formadas por padrões vocálicos sobre esqueletos de consoantes. Nesse caso, nomes e verbos do usuário viram **esqueletos C1-C2-C3** com as três primeiras consoantes da palavra (repetindo a última quando há menos de três, como no árabe *m-d-d*): *wad* vira *w-d-d*. A forma original não é preservada, e o relatório registra a conversão.

---

## Relatório

O terminal e o `grammar.md` mostram o que foi feito com o arquivo:

```
  ★ Palavras do usuário: 14 (14 válidas pela fonotática)
    · codas novos: d p s x ʃ
    [!] linha 30: 'nof' ignorada — 'f' não está entre os fonemas declarados
```

```markdown
## Palavras do usuário

Arquivo: `custom.txt` — política: **adapt**

- Inventário: declarado pelo usuário
- Fonotática: codas novos: d p s x ʃ
- Palavras gramaticais: 'not' = ka (palavra gramatical do usuário)

| Forma | Significado | Conceito | Situação |
|---|---|---|---|
| *wad* | dog | DOG | ok |
| *tad* | frog | (entrada nova) | ok |
| *ti* | I | pronome 1.singular | ok |
```

O mesmo relatório fica no `manifest.json`, na chave `custom`.

---

## Reprodutibilidade e `--from`

- A mesma semente com o mesmo arquivo gera a mesma língua, byte a byte.
- Ao **mudar o arquivo**, regere a partir do inventário (`--from inventory`), já que palavras novas podem trazer fonemas novos. O orquestrador recusa um `--from` posterior se as palavras usarem fonemas fora do inventário salvo.
- Mudanças só nos significados ou nas classes podem ser aplicadas com `--from lexicon`.

---

## Testes

60 línguas completas (sementes 400–429, com fonemas declarados e sem eles), usando os módulos `lexicon`, `morphological_engine` e `syntax` sem nenhuma alteração: nenhuma falha de execução, e a mesma semente com o mesmo arquivo gera os mesmos JSONs byte a byte. As poucas formas inválidas vieram de uma palavra de teste propositalmente sem vogal.

---

## Limitações e próximos passos

- [ ] Aceitar as formas na ortografia da língua (quando houver o módulo de ortografia), não só em IPA
- [ ] Significados em português (exige a tradução dos conceitos do Concepticon)
- [ ] Afixos definidos pelo usuário (ex: plural `-u`)
- [ ] Nome da língua definido pelo usuário
- [ ] Ajustar automaticamente os plurais dos pronomes quando o usuário define só o singular
- [ ] Preservar a forma do usuário em línguas de raiz consonantal (exige uma mudança no motor morfológico)
