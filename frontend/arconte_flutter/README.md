# ARCONTE — Ateliê de Mundos

Interface Flutter **conceitual** para o projeto Arconte. Inspirada na atmosfera de ferramentas de worldbuilding, mas com identidade original de códice fantástico: pergaminho, bosque, tinta escura, latão e ilustrações vetoriais feitas com `CustomPainter`.

## O que já existe nesta versão

- Dashboard responsivo para Linux, navegador e celular.
- Barra lateral (desktop) / menu lateral (telas menores).
- Pesquisa instantânea pelos módulos na visão geral.
- Navegação para páginas de cada módulo, com estado visual de integração.
- Mundo ilustrativo **Sarnília**, ano **67 depois da Unificação**, usado apenas para apresentar o design.
- 7 conceitos com módulos Python já desenvolvidos: personagens, genealogias, casas e famílias, organizações, religiões, divindades e doutrinas.
- 5 áreas apenas **planejadas**: cronologias, lugares, reinos, espécies e artefatos.
- Sem dependências Flutter externas, sem imagens, fotos, fontes ou APIs externas.

> **Importante:** Esta versão é uma casca visual. **Não** lê `sarnilia.json`, não importa Python, não altera projetos e não consulta uma API. Os exemplos de personagens e do mundo são apenas textos ilustrativos.

## Pré-requisito

Instale o **Flutter SDK** e valide com `flutter doctor`. Para execução desktop em Ubuntu, configure também o suporte Flutter para Linux e suas dependências. Uma opção simples para começar é rodar no Chrome.

## Instalação

Extraia o pacote. Se a pasta ainda não tem os arquivos de plataforma do Flutter (`linux/`, `web/`, etc.), gere-os assim, na pasta `arconte_flutter`:

```bash
flutter create . --platforms=linux,web,android
flutter pub get
flutter run -d chrome
```

Para executar no Linux Desktop (com os requisitos do Flutter instalados):

```bash
flutter config --enable-linux-desktop
flutter run -d linux
```

Rodar testes:

```bash
flutter test
```

**Observação:** Os diretórios de plataforma são gerados localmente pelo Flutter. Isso evita embutir arquivos dependentes da versão do SDK nesta entrega. Os arquivos de `lib/`, `test/`, `pubspec.yaml` e `analysis_options.yaml` já estão prontos.

## Organização

```text
lib/
  main.dart                   # Entrada
  app/arconte_app.dart        # MaterialApp
  theme/arconte_theme.dart    # Paleta e tipografia
  models/world_module.dart    # Definição de módulos visuais
  data/module_catalog.dart   # Catálogo de navegação
  screens/workspace_screen.dart
  widgets/
    navigation_panel.dart     # Barra lateral
    dashboard_view.dart      # Início/códice
    module_tile.dart         # Cartão de módulo
    module_view.dart         # Página individual placeholder
    ornaments.dart           # Ilustrações vetoriais
```

## Como conectar ao backend futuramente

Os modelos atuais do Arconte estão em Python. Flutter **não importa** classes `.py` diretamente. A integração prevista será via uma API (p.ex. FastAPI), com serviços Dart consumindo JSON. Arquitetura recomendada:

```text
Flutter UI → Repository Dart → REST API (FastAPI) → Project / Editor (Python)
```

O `id` de cada `WorldModule` poderá ser usado para mapear as telas aos repositórios correspondentes. As páginas já deixam claro quando o backend existe mas a conexão não está feita. A API, autenticação, navegação de dados reais e edição **não** fazem parte desta entrega.

## Identidade visual

- Pergaminho: `#F0E9DB`
- Papel: `#FBF7EE`
- Verde bosque: `#234940`
- Tinta: `#172629`
- Latão envelhecido: `#AF8753`
- Vinho: `#8F4C46`

Nenhum recurso visual da captura de tela de referência foi copiado ou reutilizado.
