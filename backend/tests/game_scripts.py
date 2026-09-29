"""Known move sequences shared by the tests. Each pair is (board, cell)."""

# A full, legal game that X wins by taking boards 6, 7 and 8 (the bottom row).
# O takes board 0 on move 16; X takes board 8 on move 17.
X_WINS_GAME: list[tuple[int, int]] = [
    (2, 0),
    (0, 4),
    (4, 0),
    (0, 6),
    (6, 0),
    (0, 7),
    (7, 4),
    (4, 6),
    (6, 8),
    (8, 8),
    (8, 6),
    (6, 7),
    (7, 5),
    (5, 8),
    (8, 0),
    (0, 8),
    (8, 3),
    (3, 0),
    (6, 4),
    (4, 8),
    (7, 3),
]

# After these 18 moves X was sent to board 0, which O has already won, so X may play in any
# open board. Boards 0 (won by O) and 8 (won by X) are closed.
FREE_MOVE_PREFIX = X_WINS_GAME[:18]
