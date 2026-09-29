from datetime import UTC

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConcurrentWriteError
from app.models.game import Move
from app.repositories.game_repository import GameRepository


def test_create_assigns_an_id_and_a_utc_created_at(session: Session) -> None:
    game = GameRepository(session).create()
    assert game.id is not None
    assert game.created_at.tzinfo is UTC


def test_created_at_is_still_utc_after_a_round_trip(session: Session) -> None:
    repository = GameRepository(session)
    game_id = repository.create().id
    session.expire_all()
    reloaded = repository.get(game_id)
    assert reloaded is not None
    assert reloaded.created_at.tzinfo is UTC


def test_get_returns_none_for_a_missing_game(session: Session) -> None:
    assert GameRepository(session).get(999) is None


def test_moves_come_back_in_the_order_they_were_played(session: Session) -> None:
    repository = GameRepository(session)
    game = repository.create()
    repository.add_move(game, sequence=0, board=4, cell=2)
    repository.add_move(game, sequence=1, board=2, cell=7)
    session.expire_all()

    reloaded = repository.get(game.id)
    assert reloaded is not None
    assert [(m.sequence, m.board, m.cell) for m in reloaded.moves] == [(0, 4, 2), (1, 2, 7)]


def test_a_second_move_with_the_same_sequence_is_refused(session: Session) -> None:
    repository = GameRepository(session)
    game = repository.create()
    repository.add_move(game, sequence=0, board=4, cell=2)

    with pytest.raises(ConcurrentWriteError) as caught:
        repository.add_move(game, sequence=0, board=4, cell=3)

    assert caught.value.code == "move_conflict"
    assert session.scalar(select(func.count()).select_from(Move)) == 1
