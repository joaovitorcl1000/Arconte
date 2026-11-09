# Interface web do Arconte

cd ipa_database
curl -L -o phoible.csv "https://raw.githubusercontent.com/phoible/dev/master/data/phoible.csv"

Uma página no navegador que **roda todos os motores em Python** do projeto: criar línguas com todas as escolhas, ver o documento completo de cada língua, evoluir, criar famílias e traduzir.

O navegador não executa Python sozinho, por isso a interface tem duas partes, as duas só com a biblioteca padrão (nada para instalar):

- `server.py`: um servidor local que recebe as escolhas da página e chama os módulos;
- `index.html`: a página (HTML, CSS e JavaScript num arquivo só).

## Onde colocar

```
backend/conlang/
├── webui/
│   ├── server.py
│   ├── index.html
│   └── README.md
├── generate_language/
├── evolution/
├── translator/
├── ...                (os demais módulos)
└── languages/
```

## Como usar

A partir de `backend/conlang/`:

```bash
python webui/server.py
```

O navegador abre sozinho em **http://localhost:8000**. Para parar, `Ctrl+C` no terminal. Outra porta: `python webui/server.py --port 8080`; sem abrir o navegador: `--no-browser`.

O servidor só aceita conexões deste computador (127.0.0.1).

## O que a página faz

| Aba | O que roda | Escolhas |
|---|---|---|
| **Criar língua** | `generate_language.py` (as 18 etapas) | nome e semente; estrutura das palavras; sons; escrita e acento; ordem e base numeral; lista de vocabulário; seus sons e palavras (com teclado IPA); mudanças sonoras; quantidades; filhas, família e frases para traduzir logo em seguida |
| **Minhas línguas** | — | lista as línguas de `languages/`, mostra o `grammar.md` (e a evolução, a família e as traduções) formatado, e baixa qualquer arquivo |
| **Evoluir** | `evolution.py` + `grammar_evolution.py` | língua-mãe, perfil, anos, gramática, só sons, leis escolhidas à mão (na ordem marcada), empréstimos de outra língua |
| **Família** | `family.py` | protolíngua, ramos, sub-ramos, níveis, anos, perfis dos ramos, gramática, versão completa de cada língua |
| **Traduzir** | `translator.py` | língua e frases em inglês; mostra a frase escrita e a glosa interlinear |

Na aba **Criar língua**, o quadro escuro no topo mostra, enquanto você escolhe, o comando equivalente do gerador. Ao terminar, a língua abre sozinha em **Minhas línguas**, e a saída do terminal fica disponível embaixo do botão.

As palavras do usuário e as frases viram arquivos temporários em `languages/.webui/` (o `minha_lingua.txt` e o `frases.txt`), passados ao gerador com `--custom` e `--translate`.

## Cuidados

- Criar uma língua leva de alguns segundos a alguns minutos (mais com filhas, família ou a primeira execução, que processa o PHOIBLE). O botão fica desativado enquanto o motor roda.
- Os motores rodam **um de cada vez**, porque escrevem nas mesmas pastas.
- As fontes vêm do Google Fonts; sem internet, a página usa as fontes do sistema e continua funcionando.
- Os dados (`ipa_database/phoible.csv`, `vocabulary/wold_1460.tsv`) precisam estar nas pastas, como na linha de comando.

## Próximos passos

- [ ] Mostrar o progresso das etapas enquanto o motor roda (hoje a saída aparece no fim)
- [ ] Editar uma língua existente (regerar a partir de uma etapa, como o `--from`)
- [ ] Servir o mesmo backend para o frontend do Arconte, com o contrato em JSON
