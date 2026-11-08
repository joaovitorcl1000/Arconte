arconte-frontend/
├── lib/
│   ├── main.dart            # Ponto de entrada, inicialização do Firebase e App
│   ├── core/                # Código global usado por toda a aplicação
│   │   ├── theme/           # Cores, tipografia (modo escuro/claro)
│   │   ├── routing/         # Configuração de rotas (ex: pacote go_router)
│   │   └── network/         # Cliente HTTP (Dio) interceptando chamadas para a API
│   ├── shared/              # Componentes visuais reaproveitáveis
│   │   └── widgets/         # Botões customizados, menus laterais, cards de loading
│   └── features/            # O coração do app, dividido por domínios
│       ├── auth/            # Login, Cadastro, Recuperação de Senha
│       ├── dashboard/       # Painel inicial mostrando os mundos criados
│       ├── editor/          # O módulo do editor de texto rico (usando flutter_quill)
│       ├── characters/      # Módulo de personagens e árvores
│       │   ├── models/      # Classes Dart do personagem (from/to JSON)
│       │   ├── providers/   # Gerenciamento de estado (Riverpod ou Bloc)
│       │   └── views/       # Telas (lista, ficha completa, visão da árvore)
│       └── maps/            # Módulo de mapas interativos (flutter_map)
├── pubspec.yaml             # Dependências do Flutter
└── web/                     # Arquivos para a compilação web (index.html)