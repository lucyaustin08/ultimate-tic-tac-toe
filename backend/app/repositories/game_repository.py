"""Data access for games and their moves. No game rules live here."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConcurrentWriteError
from app.models.game import Game, Move


class GameRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self) -> Game:
        game = Game()
        self._session.add(game)
        self._session.commit()
        return game

    def get(self, game_id: int) -> Game | None:
        return self._session.get(Game, game_id)

    def add_move(self, game: Game, sequence: int, board: int, cell: int) -> Move:
        move = Move(sequence=sequence, board=board, cell=cell)
        game.moves.append(move)
        try:
            self._session.commit()
        except IntegrityError as error:
            # Two moves raced for the same sequence number (for example a double click).
            # The loser was computed from out-of-date state, so refuse it.
            self._session.rollback()
            raise ConcurrentWriteError(
                "move_conflict",
                "Another move was recorded first. Reload the game and try again.",
            ) from error
        return move
