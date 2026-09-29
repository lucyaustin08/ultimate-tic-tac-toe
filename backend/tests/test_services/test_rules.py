"""Tests for the pure rules engine. No database, no HTTP."""

import pytest

from app.core.errors import RuleViolationError
from app.models.enums import BoardStatus, GameStatus, Player
from app.services.rules import (
    BOARD_CLOSED,
    CELL_OCCUPIED,
    EMPTY_BOARD,
    GAME_FINISHED,
    WRONG_BOARD,
    GameState,
    SmallBoard,
    apply_move,
    initial_state,
    replay,
)
from tests.game_scripts import FREE_MOVE_PREFIX, X_WINS_GAME

X, O = Player.X, Player.O  # noqa: E741 - "O" is the player's name


def board_with(cells: str) -> SmallBoard:
    """Build an open small board from a 9-character string like 'xo.......'."""
    marks = tuple({"x": X, "o": O, ".": None}[ch] for ch in cells)
    return SmallBoard(cells=marks, status=BoardStatus.OPEN, winner=None)


def won_by(player: Player) -> SmallBoard:
    return SmallBoard(cells=(player,) * 3 + (None,) * 6, status=BoardStatus.WON, winner=player)


def state_with(
    boards: dict[int, SmallBoard], active_board: int | None, move_count: int = 0
) -> GameState:
    return GameState(
        boards=tuple(boards.get(i, EMPTY_BOARD) for i in range(9)),
        move_count=move_count,
        status=GameStatus.IN_PROGRESS,
        winner=None,
        active_board=active_board,
    )


def assert_refused(code: str, state: GameState, board: int, cell: int) -> None:
    with pytest.raises(RuleViolationError) as caught:
        apply_move(state, board, cell)
    assert caught.value.code == code


# --- Turn order -------------------------------------------------------------------------------


def test_x_moves_first_and_players_alternate() -> None:
    state = initial_state()
    assert state.current_player is X

    state = apply_move(state, 4, 4)
    assert state.boards[4].cells[4] is X
    assert state.current_player is O

    state = apply_move(state, 4, 0)
    assert state.boards[4].cells[0] is O
    assert state.current_player is X


# --- First move may go anywhere ---------------------------------------------------------------


def test_first_move_may_go_in_any_board() -> None:
    state = initial_state()
    assert state.active_board is None
    for board in range(9):
        assert apply_move(state, board, 0).boards[board].cells[0] is X


# --- The opponent is sent to the board matching the cell just played --------------------------


def test_move_sends_opponent_to_matching_board() -> None:
    state = apply_move(initial_state(), 0, 5)
    assert state.active_board == 5
    assert [state.is_board_playable(b) for b in range(9)] == [b == 5 for b in range(9)]


def test_playing_in_the_active_board_is_allowed() -> None:
    state = apply_move(initial_state(), 0, 5)
    assert apply_move(state, 5, 0).boards[5].cells[0] is O


def test_playing_outside_the_active_board_is_refused() -> None:
    state = apply_move(initial_state(), 0, 5)
    assert_refused(WRONG_BOARD, state, 3, 0)


# --- Squares can only be marked once ----------------------------------------------------------


def test_marking_an_empty_square_is_allowed() -> None:
    state = apply_move(initial_state(), 2, 0)
    assert apply_move(state, 0, 2).boards[0].cells[2] is O


def test_marking_a_taken_square_is_refused() -> None:
    state = replay([(2, 0), (0, 2)])  # O's move sends X back to board 2, where 0 is taken
    assert_refused(CELL_OCCUPIED, state, 2, 0)


# --- Winning a small board --------------------------------------------------------------------


def test_three_in_a_row_captures_the_small_board() -> None:
    state = state_with({4: board_with("xx.......")}, active_board=4)
    after = apply_move(state, 4, 2)
    assert after.boards[4].status is BoardStatus.WON
    assert after.boards[4].winner is X


def test_filling_a_small_board_without_a_line_draws_it() -> None:
    # x o x / x o o / o x .  -> X fills the last square without making a line.
    state = state_with({4: board_with("xoxxooox.")}, active_board=4)
    after = apply_move(state, 4, 8)
    assert after.boards[4].status is BoardStatus.DRAWN
    assert after.boards[4].winner is None


# --- Being sent to a board that can't be played gives a free move -----------------------------


def test_being_sent_to_a_won_board_gives_a_free_move() -> None:
    state = replay(FREE_MOVE_PREFIX)
    assert state.boards[0].status is BoardStatus.WON  # X was just sent here
    assert state.active_board is None
    playable = [b for b in range(9) if state.is_board_playable(b)]
    assert playable == [b for b in range(9) if state.boards[b].is_open]


def test_being_sent_to_a_drawn_board_gives_a_free_move() -> None:
    drawn = SmallBoard(
        cells=(X, O, X, X, O, O, O, X, X), status=BoardStatus.DRAWN, winner=None
    )
    state = state_with({3: drawn}, active_board=None)
    after = apply_move(state, 0, 3)  # cell 3 would send O to board 3
    assert after.active_board is None
    assert not after.is_board_playable(3)
    assert after.is_board_playable(0)


def test_free_move_into_an_open_board_is_allowed() -> None:
    state = replay(FREE_MOVE_PREFIX)
    after = apply_move(state, 1, 0)
    assert after.boards[1].cells[0] is X


def test_free_move_into_a_decided_board_is_refused() -> None:
    state = replay(FREE_MOVE_PREFIX)
    assert state.boards[0].cells[0] is None  # empty square, but the board is decided
    assert_refused(BOARD_CLOSED, state, 0, 0)


# --- Winning and drawing the whole game -------------------------------------------------------


def test_three_small_boards_in_a_row_wins_the_game() -> None:
    state = state_with(
        {0: won_by(X), 1: won_by(X), 2: board_with("xx.......")}, active_board=2
    )
    after = apply_move(state, 2, 2)
    assert after.status is GameStatus.WON
    assert after.winner is X
    assert after.current_player is None
    assert after.active_board is None


def test_full_scripted_game_ends_with_x_winning() -> None:
    state = replay(X_WINS_GAME)
    assert state.status is GameStatus.WON
    assert state.winner is X
    assert [state.boards[b].winner for b in (6, 7, 8)] == [X, X, X]


def test_no_line_once_every_board_is_decided_is_a_draw() -> None:
    # Every board decided except board 8, and no three-in-a-row is possible for anyone:
    #   X O X
    #   X O O
    #   O X ?   <- board 8 is about to be drawn
    decided = {
        0: won_by(X),
        1: won_by(O),
        2: won_by(X),
        3: won_by(X),
        4: won_by(O),
        5: won_by(O),
        6: won_by(O),
        7: won_by(X),
        8: board_with("xoxxooox."),
    }
    state = state_with(decided, active_board=8)
    after = apply_move(state, 8, 8)
    assert after.status is GameStatus.DRAWN
    assert after.winner is None
    assert after.current_player is None


def test_moving_after_the_game_is_over_is_refused() -> None:
    state = replay(X_WINS_GAME)
    assert_refused(GAME_FINISHED, state, 1, 0)


# --- Guard rails ------------------------------------------------------------------------------


@pytest.mark.parametrize(("board", "cell"), [(-1, 0), (9, 0), (0, -1), (0, 9)])
def test_out_of_range_indexes_are_a_programming_error(board: int, cell: int) -> None:
    with pytest.raises(ValueError):
        apply_move(initial_state(), board, cell)
