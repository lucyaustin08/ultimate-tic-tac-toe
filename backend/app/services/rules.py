"""The rules of ultimate tic-tac-toe, as pure functions over immutable state.

Nothing here touches the database or HTTP. The whole game state is a fold of ``apply_move``
over the stored move list, which is why nothing derived is ever stored.

Board and cell indexes run 0-8, left to right, top to bottom:

    0 | 1 | 2
    3 | 4 | 5
    6 | 7 | 8
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Final

from app.core.errors import RuleViolationError
from app.models.enums import BoardStatus, GameStatus, Player

SIZE: Final = 9

WIN_LINES: Final = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

GAME_FINISHED: Final = "game_finished"
WRONG_BOARD: Final = "wrong_board"
BOARD_CLOSED: Final = "board_closed"
CELL_OCCUPIED: Final = "cell_occupied"


@dataclass(frozen=True, slots=True)
class SmallBoard:
    cells: tuple[Player | None, ...]
    status: BoardStatus
    winner: Player | None

    @property
    def is_open(self) -> bool:
        return self.status is BoardStatus.OPEN


@dataclass(frozen=True, slots=True)
class GameState:
    boards: tuple[SmallBoard, ...]
    move_count: int
    status: GameStatus
    winner: Player | None
    # The board the next move must go in, or None when the next player may pick any open board
    # (or when the game is over).
    active_board: int | None

    @property
    def current_player(self) -> Player | None:
        if self.status is not GameStatus.IN_PROGRESS:
            return None
        return player_for_sequence(self.move_count)

    def is_board_playable(self, board: int) -> bool:
        if self.status is not GameStatus.IN_PROGRESS:
            return False
        if self.active_board is not None:
            return board == self.active_board
        return self.boards[board].is_open


EMPTY_BOARD: Final = SmallBoard(cells=(None,) * SIZE, status=BoardStatus.OPEN, winner=None)


def player_for_sequence(sequence: int) -> Player:
    """X always moves first, so even-numbered moves are X's."""
    return Player.X if sequence % 2 == 0 else Player.O


def line_winner(marks: Sequence[Player | None]) -> Player | None:
    for a, b, c in WIN_LINES:
        if marks[a] is not None and marks[a] == marks[b] == marks[c]:
            return marks[a]
    return None


def initial_state() -> GameState:
    return GameState(
        boards=(EMPTY_BOARD,) * SIZE,
        move_count=0,
        status=GameStatus.IN_PROGRESS,
        winner=None,
        active_board=None,
    )


def _check_index(name: str, value: int) -> None:
    if not 0 <= value < SIZE:
        raise ValueError(f"{name} must be between 0 and {SIZE - 1}, got {value}.")


def _place(board: SmallBoard, cell: int, player: Player) -> SmallBoard:
    cells = board.cells[:cell] + (player,) + board.cells[cell + 1 :]
    winner = line_winner(cells)
    if winner is not None:
        return SmallBoard(cells=cells, status=BoardStatus.WON, winner=winner)
    if all(mark is not None for mark in cells):
        return SmallBoard(cells=cells, status=BoardStatus.DRAWN, winner=None)
    return SmallBoard(cells=cells, status=BoardStatus.OPEN, winner=None)


def apply_move(state: GameState, board: int, cell: int) -> GameState:
    """Return the state after the current player marks ``cell`` in ``board``.

    Raises ``RuleViolationError`` when the move is not allowed.
    """
    _check_index("board", board)
    _check_index("cell", cell)

    player = state.current_player
    if player is None:
        raise RuleViolationError(GAME_FINISHED, "The game is over; no more moves can be made.")
    if state.active_board is not None and board != state.active_board:
        raise RuleViolationError(
            WRONG_BOARD,
            f"This move must be played in board {state.active_board}.",
        )
    if not state.boards[board].is_open:
        raise RuleViolationError(
            BOARD_CLOSED,
            f"Board {board} is already decided; choose an open board.",
        )
    if state.boards[board].cells[cell] is not None:
        raise RuleViolationError(CELL_OCCUPIED, "That square is already taken.")

    boards = state.boards[:board] + (_place(state.boards[board], cell, player),) + state.boards[
        board + 1 :
    ]

    game_winner = line_winner([small.winner for small in boards])
    if game_winner is not None:
        return GameState(
            boards=boards,
            move_count=state.move_count + 1,
            status=GameStatus.WON,
            winner=game_winner,
            active_board=None,
        )
    if not any(small.is_open for small in boards):
        return GameState(
            boards=boards,
            move_count=state.move_count + 1,
            status=GameStatus.DRAWN,
            winner=None,
            active_board=None,
        )

    # The opponent is sent to the board matching the cell just played, unless that board is
    # already decided, in which case they may play in any open board.
    next_board = cell if boards[cell].is_open else None
    return replace(
        state,
        boards=boards,
        move_count=state.move_count + 1,
        active_board=next_board,
    )


def replay(moves: Iterable[tuple[int, int]]) -> GameState:
    """Rebuild the game state from ``(board, cell)`` pairs in the order they were played."""
    state = initial_state()
    for board, cell in moves:
        state = apply_move(state, board, cell)
    return state
