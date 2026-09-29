import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, RuleViolationError
from app.models.enums import GameStatus, Player
from app.models.game import Move
from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService


@pytest.fixture
def service(session: Session) -> GameService:
    return GameService(GameRepository(session))


def count_moves(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Move)) or 0


def test_a_new_game_is_empty_with_x_to_move(service: GameService) -> None:
    game = service.create_game()
    assert game.moves == ()
    assert game.state.status is GameStatus.IN_PROGRESS
    assert game.state.current_player is Player.X


def test_getting_a_missing_game_raises_not_found(service: GameService) -> None:
    with pytest.raises(NotFoundError) as caught:
        service.get_game(999)
    assert caught.value.code == "game_not_found"


def test_a_legal_move_is_stored_and_reflected_in_the_state(
    service: GameService, session: Session
) -> None:
    game_id = service.create_game().id

    game = service.play_move(game_id, board=4, cell=2)

    assert count_moves(session) == 1
    assert [(m.sequence, m.board, m.cell, m.player) for m in game.moves] == [(0, 4, 2, Player.X)]
    assert game.state.current_player is Player.O
    assert game.state.active_board == 2


def test_an_illegal_move_is_refused_and_nothing_is_stored(
    service: GameService, session: Session
) -> None:
    game_id = service.create_game().id
    service.play_move(game_id, board=4, cell=2)  # O must now play in board 2

    with pytest.raises(RuleViolationError) as caught:
        service.play_move(game_id, board=5, cell=0)

    assert caught.value.code == "wrong_board"
    assert count_moves(session) == 1


def test_playing_in_a_missing_game_raises_not_found(service: GameService) -> None:
    with pytest.raises(NotFoundError) as caught:
        service.play_move(999, board=0, cell=0)
    assert caught.value.code == "game_not_found"
