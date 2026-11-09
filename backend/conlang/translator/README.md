# Módulo — Tradutor (inglês → conlang)

Traduz frases simples em inglês para a conlang **aplicando a gramática dela** — não só palavra por palavra —, como o "Smart Translation" do Vulgarlang. Funciona em qualquer língua gerada pelo orquestrador, inclusive nas **línguas evoluídas** e nas **famílias**.

```
$ python translator/translator.py --language languages/lang-31 "The fish was eaten by the dog."

Twukuu plaani alenuupunya.

    twukuː  plaːni   alenuːpuɲa
    twukuː  plaː-ni  alenuː-pu-ɲa
    fish    dog-INS  eat-PST-PASS
    'The fish was eaten by the dog.'
```

O módulo **não altera nenhum outro**: lê os JSONs da língua e usa as funções públicas do motor morfológico, da sintaxe, da comparação, da derivação e da ortografia.

---

## Onde colocar

```
conlang/
└── translator/
    ├── translator.py
    └── README.md
```

Usa apenas a biblioteca padrão do Python (≥ 3.9).

---

## Uso

```bash
# uma ou mais frases
python translator/translator.py --language languages/lang-31 "The woman sees the big dog." "Did the dog eat the fish?"

# um arquivo (uma frase por linha), guardando as traduções em translations.md
python translator/translator.py --language languages/lang-31 --file frases.txt --save

# modo interativo (linha vazia para sair)
python translator/translator.py --language languages/lang-31

# numa língua evoluída
python translator/translator.py --language languages/lang-31-romance-2000 "My dog sleeps."
```

| Opção | Descrição |
|---|---|
| `--language PATH` | Pasta da língua (obrigatório) |
| frases | Uma ou mais frases; um texto com várias frases é dividido nos pontos |
| `--file PATH` | Arquivo com frases |
| `--save` | Acrescenta as traduções ao `translations.md` da língua |

Cada tradução mostra a frase **escrita na grafia** da língua, a **glosa interlinear** (formas, morfemas e glosas), as palavras sem tradução e notas (por exemplo, "a língua não tem futuro gramatical").

---

## O que o tradutor entende

| Recurso | Exemplo | Como é traduzido |
|---|---|---|
| Ordem, caso e concordância | *The woman sees the big dog.* | pela sintaxe da língua (SOV, ergativo, pro-drop...) |
| Tempo | *ate*, *will eat*, *did eat* | passado e futuro, se a língua os tem (senão, presente com nota) |
| Aspecto progressivo | *is eating* | imperfectivo, se a língua o tem |
| Negação | *does not sleep*, *didn't* | afixo, partícula ou palavra 'não' da língua |
| Plural e numerais | *three dogs* | número do nome, numerais (do módulo de numerais), classificadores |
| Artigos e demonstrativos | *the*, *a*, *this*, *those* | artigos (se a língua tem definitude) e demonstrativos |
| Adjetivos | *the big dog* | na posição do adjetivo da língua |
| Posse | *my dog*, *the woman's dog*, *mine* | afixos, palavras possessivas ou classificador de posse (módulo de posse); genitivo |
| Perguntas | *Did...?*, *What does...?*, *Who...?*, *Where...?* | partícula, inversão ou entonação; palavra interrogativa no início ou no lugar do argumento, com o caso certo |
| Imperativo | *Eat the fish!*, *Don't eat the fish!* | imperativo e proibitivo do módulo de orações |
| Passiva | *was eaten by the dog* | passiva da língua (com o agente no caso ou adposição certos); sem passiva, frase ativa com nota |
| Comparação | *bigger than*, *the biggest*, *as big as* | estratégia da língua (locativa, de superar, partícula...) do módulo de comparação |
| Coordenação | *and*, *but*, *or* | conectivos do módulo de orações |
| Subordinação | *because*, *if*, *that* | subordinador no início ou no fim da subordinada, conforme a ordem da língua |
| Lugar | *under the tree*, *in the house* | caso locativo ou adposições espaciais (módulo de orações) |
| Objeto indireto | *gives the fish to the child* | caso ou adposição de recipiente |
| Palavras derivadas | *hunter*, *darkness*, *quickly* | **formadas com a derivação da própria língua** ('hunt' + agentivo) |
| Formas irregulares | *went*, *feet* | as irregularidades da língua (módulo de irregularidades) |

O vocabulário vem do léxico básico e, se existir, do **vocabulário ampliado** (cerca de 1.600 palavras) e dos **numerais**. Quando o inglês tem uma palavra para dois conceitos ('child' = 'criança' ou 'filho'), o tradutor escolhe o sentido mais comum.

Os módulos opcionais enriquecem a tradução, mas nenhum é obrigatório: sem o módulo de orações, não há imperativo nem adposições espaciais próprias; sem o de posse, *my dog* usa o pronome no genitivo; e assim por diante.

---

## Exemplos (língua 31)

```
I will eat the fish.             Ka twukuu alenuupi.          1SG fish eat-FUT
My dog sleeps.                   Paamlo plaa hulhuuwo.        CLF.POSS-1SG dog sleep
Did the dog eat the fish?        Plaa twukuu alenuupu li?     dog fish eat-PST Q
Don't eat the fish!              Twukuu se alenuul!           fish PROH eat-IMP
The dog is bigger than the fish. Plaa twukuubu twaawi.        dog fish-ABL big-COMPR
I know that the dog sleeps.      Ka plaa hulhuuwo qo me.      1SG dog sleep COMP know
The hunters laugh.               Aakyuuwami yake.             hunt-AG-PL laugh
```

---

## Testes

30 línguas (incluindo duas evoluídas, uma tonal, uma de raízes consonantais e ergativas) × 20 frases de teste (600 traduções): nenhum erro. As palavras sem tradução foram as esperadas (como *dragon*, que não está em nenhuma lista de conceitos).

---

## Limitações e próximos passos

- [ ] O inglês é analisado por regras simples: frases com uma ou duas orações funcionam bem; orações relativas (*the dog that I saw*), voz passiva com auxiliares compostos e frases muito longas, não
- [ ] *you* é sempre singular, e *we*, exclusivo, quando a língua distingue
- [ ] Palavras fora das listas de conceitos ficam sem tradução (‹ ›); uma opção para criar palavras novas na hora fica para depois
- [ ] Tradução no sentido contrário (conlang → inglês)
- [ ] Integrar ao orquestrador e ao frontend (um campo de texto que traduz enquanto o usuário digita)
