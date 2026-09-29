"""HTTP routes for games. Routers translate HTTP to service calls and nothing more."""

from typing import Any

from fastapi import APIRouter, Request, Response, status

from app.api.v1.dependencies import GameServiceDep
from app.schemas.game import ErrorResponse, GameRead, MoveCreate

router = APIRouter(prefix="/games", tags=["games"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "The game does not exist."}
}
INVALID: dict[int | str, dict[str, Any]] = {
    422: {"model": ErrorResponse, "description": "The request failed schema validation."}
}
REFUSED: dict[int | str, dict[str, Any]] = {
    409: {"model": ErrorResponse, "description": "A game rule refused the move."}
}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_game(request: Request, response: Response, service: GameServiceDep) -> GameRead:
    game = GameRead.from_view(service.create_game())
    response.headers["Location"] = str(request.app.url_path_for("get_game", game_id=str(game.id)))
    return game


@router.get("/{game_id}", responses={**NOT_FOUND, **INVALID})
def get_game(game_id: int, service: GameServiceDep) -> GameRead:
    return GameRead.from_view(service.get_game(game_id))


@router.post(
    "/{game_id}/moves",
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_FOUND, **REFUSED, **INVALID},
)
def play_move(
    game_id: int,
    move: MoveCreate,
    request: Request,
    response: Response,
    service: GameServiceDep,
) -> GameRead:
    """Record a move and return the updated game."""
    game = GameRead.from_view(service.play_move(game_id, board=move.board, cell=move.cell))
    response.headers["Location"] = str(request.app.url_path_for("get_game", game_id=str(game_id)))
    return game
