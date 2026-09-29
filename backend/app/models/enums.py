from enum import StrEnum


class Player(StrEnum):
    X = "x"
    O = "o"  # noqa: E741 - "O" is the name of the player, not a variable


class BoardStatus(StrEnum):
    OPEN = "open"
    WON = "won"
    DRAWN = "drawn"


class GameStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAWN = "drawn"
