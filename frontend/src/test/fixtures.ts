import type { Game, Player, SmallBoard } from "../api/client";

export function emptyBoard(index: number): SmallBoard {
  return { index, cells: Array(9).fill(null), status: "open", winner: null, playable: true };
}

export function newGame(overrides: Partial<Game> = {}): Game {
  return {
    id: 1,
    created_at: "2026-09-29T09:00:00Z",
    status: "in_progress",
    winner: null,
    current_player: "x",
    active_board: null,
    boards: Array.from({ length: 9 }, (_, index) => emptyBoard(index)),
    moves: [],
    ...overrides,
  };
}

/**
 * What a mock server returns after a simple move: the mark is placed and the opponent is sent
 * to the matching board. This is only enough behaviour to drive the UI; the real rules are
 * tested on the backend.
 */
export function afterMove(game: Game, board: number, cell: number): Game {
  const player: Player = game.current_player ?? "x";
  const boards = game.boards.map((small) => ({
    ...small,
    cells: small.index === board ? small.cells.map((m, i) => (i === cell ? player : m)) : small.cells,
    playable: small.index === cell,
  }));
  return {
    ...game,
    boards,
    current_player: player === "x" ? "o" : "x",
    active_board: cell,
    moves: [
      ...game.moves,
      { sequence: game.moves.length, board, cell, player, created_at: "2026-09-29T09:01:00Z" },
    ],
  };
}

export function finishedGame(winner: Player): Game {
  const won = (index: number): SmallBoard => ({
    index,
    cells: [winner, winner, winner, null, null, null, null, null, null],
    status: "won",
    winner,
    playable: false,
  });
  return newGame({
    status: "won",
    winner,
    current_player: null,
    boards: Array.from({ length: 9 }, (_, index) =>
      index < 3 ? won(index) : { ...emptyBoard(index), playable: false },
    ),
  });
}
