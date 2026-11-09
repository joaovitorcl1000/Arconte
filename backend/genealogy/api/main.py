"""Ponto de entrada da API HTTP do Arconte (FastAPI).

Execute na pasta ``backend/genealogy``::

    python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

O arquivo padrão é ``data/sarnilia.json``. Para selecionar outro projeto::

    ARCONTE_PROJECT_FILE=data/outro_projeto.json python3 -m uvicorn api.main:app --reload

Caminhos relativos são resolvidos a partir de ``backend/genealogy``, não da
pasta em que o terminal foi aberto. As rotas POST e PATCH salvam o JSON completo de modo atômico.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.characters import router as characters_router
from api.relationships import router as relationships_router

GENEALOGY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROJECT_FILE = GENEALOGY_ROOT / "data" / "sarnilia.json"


def create_app(project_file: str | os.PathLike[str] | None = None) -> FastAPI:
    """Cria a aplicação; ``project_file`` permite teste com arquivos isolados."""
    selected = project_file if project_file is not None else os.environ.get("ARCONTE_PROJECT_FILE")
    path = Path(selected).expanduser() if selected is not None else DEFAULT_PROJECT_FILE
    if not path.is_absolute():
        path = GENEALOGY_ROOT / path
    path = path.resolve()

    app = FastAPI(
        title="Arconte — API de Personagens",
        description="Consulta, criação e edição de personagens para o Flutter.",
        version="0.1.0",
    )
    app.state.project_file = path

    # Somente aplicações web locais (Flutter Web no Firefox, portas variáveis).
    # Não use '*' com origens externas em produção; configure CORS adequadamente.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(?:localhost|127\.0\.0\.1)(?::[0-9]{1,5})?$",
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
        allow_credentials=False,
    )
    app.include_router(characters_router)
    app.include_router(relationships_router)

    @app.get("/health", tags=["Sistema"], summary="Verificar se a API está ativa")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

__all__ = ["app", "create_app"]
