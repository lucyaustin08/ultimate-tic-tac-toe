import { http, HttpResponse } from "msw";
import type { Game } from "../api/client";
import { afterMove, newGame } from "./fixtures";

const GAMES = "*/api/v1/games";

/** The game the default handlers serve. Tests can replace it with `setServerGame`. */
let serverGame: Game = newGame();

export function setServerGame(game: Game) {
  serverGame = game;
}

export function resetServerGame() {
  serverGame = newGame();
}

type MoveBody = { board: number; cell: number };

export const handlers = [
  http.post(GAMES, () => HttpResponse.json(serverGame, { status: 201 })),

  http.get(`${GAMES}/:gameId`, ({ params }) => {
    if (Number(params.gameId) !== serverGame.id) {
      return HttpResponse.json(
        { code: "game_not_found", detail: `There is no game with id ${String(params.gameId)}.` },
        { status: 404 },
      );
    }
    return HttpResponse.json(serverGame);
  }),

  http.post(`${GAMES}/:gameId/moves`, async ({ request }) => {
    const { board, cell } = (await request.json()) as MoveBody;
    serverGame = afterMove(serverGame, board, cell);
    return HttpResponse.json(serverGame, { status: 201 });
  }),
];

/** Handlers for specific failure cases, applied per test with `server.use(...)`. */
export const errorHandlers = {
  createGameFails: http.post(GAMES, () =>
    HttpResponse.json({ code: "internal_server_error", detail: "Server error." }, { status: 500 }),
  ),
  getGameFailsOnce: http.get(
    `${GAMES}/:gameId`,
    () =>
      HttpResponse.json({ code: "internal_server_error", detail: "Server error." }, { status: 500 }),
    { once: true },
  ),
  moveRefused: http.post(`${GAMES}/:gameId/moves`, () =>
    HttpResponse.json(
      { code: "wrong_board", detail: "This move must be played in board 4." },
      { status: 409 },
    ),
  ),
};
