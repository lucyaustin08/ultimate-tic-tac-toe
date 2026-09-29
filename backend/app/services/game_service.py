"""Game use cases: create a game, read it, and play a move."""

from dataclasses import dataclass
from datetime import datetime

from app.core.errors import NotFoundError
from app.models.enums import Player
from app.models.game import Game
from app.repositories.game_repository import GameRepository
from app.services.rules import GameState, apply_move, player_for_sequence, replay


@dataclass(frozen=True, slots=True)
class MoveView:
    sequence: int
    board: int
    cell: int
    player: Player
    created_at: datetime


@dataclass(frozen=True, slots=True)
class GameView:
    id: int
    created_at: datetime
    state: GameState
    moves: tuple[MoveView, ...]


def _to_view(game: Game) -> GameView:
    moves = tuple(
        MoveView(
            sequence=move.sequence,
            board=move.board,
            cell=move.cell,
            player=player_for_sequence(move.sequence),
            created_at=move.created_at,
        )
        for move in game.moves
    )
    state = replay((move.board, move.cell) for move in moves)
    return GameView(id=game.id, created_at=game.created_at, state=state, moves=moves)


class GameService:
    def __init__(self, repository: GameRepository) -> None:
        self._repository = repository

    def _load(self, game_id: int) -> Game:
        game = self._repository.get(game_id)
        if game is None:
            raise NotFoundError("game_not_found", f"There is no game with id {game_id}.")
        return game

    def create_game(self) -> GameView:
        return _to_view(self._repository.create())

    def get_game(self, game_id: int) -> GameView:
        return _to_view(self._load(game_id))

    def play_move(self, game_id: int, board: int, cell: int) -> GameView:
        game = self._load(game_id)
        state = _to_view(game).state
        apply_move(state, board, cell)  # raises RuleViolationError if the move is not allowed
        self._repository.add_move(game, sequence=state.move_count, board=board, cell=cell)
        return _to_view(game)
