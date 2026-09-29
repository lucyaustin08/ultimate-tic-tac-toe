from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.v1.errors import register_exception_handlers
from app.api.v1.games import router as games_router


def _operation_id(route: APIRoute) -> str:
    # Keeps generated frontend types readable: "get_game" instead of "get_game_api_v1_..._get".
    return route.name


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ultimate Tic-Tac-Toe API",
        version="0.1.0",
        generate_unique_id_function=_operation_id,
    )
    register_exception_handlers(app)
    app.include_router(games_router, prefix="/api/v1")
    return app


app = create_app()
