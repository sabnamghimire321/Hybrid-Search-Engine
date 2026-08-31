from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from search_engine.api.analytics import QueryHistoryStore
from search_engine.api.routes import search as search_routes
from search_engine.cli.main import SearchEngineCLI
from search_engine.observability.middleware import RequestLoggingMiddleware

def create_app(
    engine: SearchEngineCLI | None = None, history: QueryHistoryStore | None = None
) -> FastAPI:
    app = FastAPI(title="Hybrid Search Engine API", version="0.1.0")
    app.state.engine = engine or SearchEngineCLI()
    app.state.history = history or QueryHistoryStore()
    app.include_router(search_routes.router)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_app()