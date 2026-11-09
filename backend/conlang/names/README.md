# Módulo — Nomes próprios

Gera nomes de **pessoas**, **famílias** e **lugares** que soam como a conlang e, quando possível, significam algo nela — o equivalente ao "Generate unique character/place name" do Vulgarlang, com etimologia.

```
Pessoas   Krotyulĩ Unukiiam   /ˈkrotjulĩ/   'new seed'
Lugares   Buiila              /ˈbuiːla/     'fire-town'
          Mor Iizreq          /mor ˈiːzreŋ/ 'black ice'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico (sândi e flexão), da ortografia e do acento.

---

## Onde colocar

```
conlang/
├── names/
│   ├── names.py
│   └── README.md
└── languages/lang-31/
    ├── names.json      ← gerado
    └── names.md        ← gerado
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
python names/names.py --language languages/lang-31
python names/names.py --language languages/lang-31 --people 50 --places 50
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--language PATH` | — (obrigatório) | Pasta de uma língua gerada |
| `--people N` | `20` | Quantidade de pessoas |
| `--places N` | `20` | Quantidade de lugares |
| `--seed N` | derivada | Semente; por padrão derivada da semente da língua, então a mesma língua gera sempre os mesmos nomes |

A pasta precisa ter, no mínimo, inventário, fonotática, categorias, morfologia e léxico. Se houver `orthography.json` e `stress.json`, os nomes saem escritos na grafia e com acento; senão, em IPA.

---

## Configuração de cada língua

Algumas convenções são sorteadas uma vez por língua e valem para todos os nomes:

| Convenção | Opções |
|---|---|
| **Gênero nos nomes** | Se a língua tem gênero masculino/feminino previsível pela vogal final, os nomes seguem essas vogais. Senão, em 50% das línguas os nomes ganham terminações próprias de gênero (como *-o*/*-a*); nas demais, não marcam gênero |
| **Sobrenomes** | nome do pai + palavra para 'filho' (como *-son*, *ibn*); nome do pai no caso genitivo ('de X'); nome do pai + sufixo patronímico novo; ou sem patronímicos (sobrenomes descritivos) |
| **Sufixo de povoado** | Um morfema novo que significa 'cidade, lugar', como o *-ton* do inglês ou o *-grad* do russo |

---

## Pessoas

Cada pessoa tem **nome** e **sobrenome**.

- **Nomes opacos** (65%): raízes novas de 2 a 3 sílabas, escolhidas entre várias candidatas pela eufonia — mais soantes, menos encontros consonantais e menos vogais em sequência —, nunca iguais a uma palavra do dicionário.
- **Nomes descritivos** (35%): uma qualidade + um elemento da natureza, um animal ou uma parte do corpo ('new seed', 'smooth wing', 'red star'), compostos na ordem dos compostos da língua e unidos pelo sândi dela.
- **Sobrenomes**: patronímicos formados a partir do nome do pai, conforme a convenção da língua, ou descritivos ('cold mountain').

## Lugares

| Modelo | Prob. | Exemplo |
|---|---|---|
| Composto | 30% | *Itutyuui* 'short wind' |
| Sintagma | 20% | *Mor Iizreq* 'black ice' — duas palavras, na ordem do adjetivo da sintaxe |
| Povoado | 20% | *Buiila* 'fire-town' — palavra + sufixo de povoado |
| Locativo | 10% | 'at the stone' — o nome no caso locativo, como muitos topônimos reais |
| Antigo | 20% | *Mena* — sem significado, como nomes cuja origem se perdeu |

Os elementos vêm de listas de conceitos geográficos (rio, montanha, pedra, floresta, mar...), qualidades (grande, negro, velho, frio...) e animais. Entre algumas combinações possíveis, o módulo prefere os compostos mais curtos e sem vogais em sequência, porque nomes longos demais soam artificiais.

Os significados ficam em inglês, como as glosas do dicionário.

---

## Saídas

### `names.md`

```markdown
| Nome | Pronúncia | Gênero | Significado | Sobrenome | Significado |
|---|---|---|---|---|---|
| **Krotyulĩ** | /ˈkrotjulĩ/ | — | new seed | Unukiiam | child of Unukii |

| Nome | Pronúncia | Tipo | Significado |
|---|---|---|---|
| **Buiila** | /ˈbuiːla/ | povoado | fire-town |
```

### `names.json`

```json
{
  "settings": {
    "patronymic": {"strategy": "suffix", "morpheme": ["a", "m"]},
    "settlement_suffix": ["l", "a"],
    "locative_case": "locative"
  },
  "people": [
    {"given": {"name": "Krotyulĩ", "ipa": "krotjulĩ", "pronunciation": "ˈkrotjulĩ",
               "meaning": "new seed", "etymology": "new + seed", "gender": "any"},
     "family": {"name": "Unukiiam", "ipa": "...", "meaning": "child of Unukii", "type": "patronymic"},
     "full": "Krotyulĩ Unukiiam"}
  ],
  "places": [
    {"name": "Buiila", "ipa": "buiːla", "pronunciation": "ˈbuiːla",
     "meaning": "fire-town", "template": "settlement"}
  ],
  "metadata": {"seed": 1234567, "spelled": true, "stressed": true}
}
```

### Uso como biblioteca

```python
from pathlib import Path
import names

g = names.NameGenerator(Path("languages/lang-31"))
g.person("female")        # um nome
g.full_person()           # nome + sobrenome
g.place()                 # um lugar, modelo sorteado
g.place("settlement")     # um lugar de um modelo específico
```

---

## Testes

31 línguas geradas, 1.860 nomes (pessoas e lugares), incluindo línguas tonais, de raízes consonantais e com gênero gramatical: nenhum erro, todos os nomes passando pela fonotática e pelo sândi da língua, e a mesma semente gerando os mesmos nomes.

---

## Limitações e próximos passos

- [ ] Integrar ao orquestrador (etapa opcional e seção no `grammar.md`)
- [ ] Nomes de povos e gentílicos ('os de Buiila')
- [ ] Apelidos e títulos ('o Velho', 'a Sábia')
- [ ] Nomes de divindades, astros e meses
- [ ] Em línguas de raízes consonantais, os compostos usam as formas de citação e podem ficar longos
