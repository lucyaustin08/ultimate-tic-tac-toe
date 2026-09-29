import createClient from "openapi-fetch";
import type { components, paths } from "./schema";

export type Game = components["schemas"]["GameRead"];
export type SmallBoard = components["schemas"]["SmallBoardRead"];
export type Player = components["schemas"]["Player"];
type ErrorBody = components["schemas"]["ErrorResponse"];

/** An error response from the API, carrying the envelope's `code` and `detail`. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, body: Partial<ErrorBody> | undefined) {
    super(body?.detail ?? "Something went wrong. Please try again.");
    this.name = "ApiError";
    this.status = status;
    this.code = body?.code ?? "unknown_error";
  }
}

export const api = createClient<paths>({
  // openapi-fetch needs an absolute URL; the API is served from the same origin as the page.
  baseUrl: globalThis.location?.origin ?? "",
  // Look fetch up at call time rather than capturing it once, so test mocks can intercept it.
  fetch: (request) => globalThis.fetch(request),
});

export async function createGame(): Promise<Game> {
  const { data, error, response } = await api.POST("/api/v1/games");
  if (data === undefined) throw new ApiError(response.status, error);
  return data;
}

export async function fetchGame(gameId: number): Promise<Game> {
  const { data, error, response } = await api.GET("/api/v1/games/{game_id}", {
    params: { path: { game_id: gameId } },
  });
  if (data === undefined) throw new ApiError(response.status, error);
  return data;
}

export async function playMove(gameId: number, board: number, cell: number): Promise<Game> {
  const { data, error, response } = await api.POST("/api/v1/games/{game_id}/moves", {
    params: { path: { game_id: gameId } },
    body: { board, cell },
  });
  if (data === undefined) throw new ApiError(response.status, error);
  return data;
}
