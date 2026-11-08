arconte-backend/
├── app/
│   ├── main.py              # Ponto de entrada (inicialização do FastAPI)
│   ├── api/                 # Endpoints (Rotas da API)
│   │   ├── routes/
│   │   │   ├── auth.py      # Rotas de sessão e permissões
│   │   │   ├── entities.py  # Rotas CRUD (criar personagem, atualizar local)
│   │   │   └── trees.py     # Rotas específicas para as árvores genealógicas
│   ├── core/                # Configurações globais 
│   │   ├── config.py        # Variáveis de ambiente, CORS
│   │   └── security.py      # Verificação de tokens do Firebase
│   ├── models/              # Modelos Pydantic (Validação de dados)
│   │   ├── character.py
│   │   └── location.py
│   └── services/            # Regras de negócio pesadas 
│       ├── firebase_db.py   # Lógica de conexão com Firebase Admin SDK
│       └── graph_logic.py   # Algoritmos para mapear conexões/linhagens
├── requirements.txt         # Dependências (fastapi, uvicorn, firebase-admin)
└── .env                     # Chaves e segredos locais