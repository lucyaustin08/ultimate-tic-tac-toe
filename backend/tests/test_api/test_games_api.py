from typing import Any

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import Engine, event

from tests.game_scripts import FREE_MOVE_PREFIX, X_WINS_GAME

pytestmark = pytest.mark.anyio

GAMES = "/api/v1/games"


async def new_game(client: AsyncClient) -> int:
    response = await client.post(GAMES)
    assert response.status_code == 201
    game_id: int = response.json()["id"]
    return game_id


async def play(client: AsyncClient, game_id: int, board: int, cell: int) -> Response:
    return await client.post(f"{GAMES}/{game_id}/moves", json={"board": board, "cell": cell})


async def play_all(client: AsyncClient, game_id: int, moves: list[tuple[int, int]]) -> None:
    for board, cell in moves:
        response = await play(client, game_id, board, cell)
        assert response.status_code == 201, response.json()


def assert_error(response: Response, status_code: int, code: str) -> None:
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"code", "detail"}
    assert body["code"] == code
    assert isinstance(body["detail"], str) and body["detail"]


def assert_game_shape(body: dict[str, Any]) -> None:
    assert set(body) == {
        "id",
        "created_at",
        "status",
        "winner",
        "current_player",
        "active_board",
        "boards",
        "moves",
    }
    assert len(body["boards"]) == 9
    for index, board in enumerate(body["boards"]):
        assert set(board) == {"index", "cells", "status", "winner", "playable"}
        assert board["index"] == index
        assert len(board["cells"]) == 9


# --- POST /games ------------------------------------------------------------------------------


async def test_create_game_returns_201_an_empty_board_and_a_location(client: AsyncClient) -> None:
    response = await client.post(GAMES)

    assert response.status_code == 201
    body = response.json()
    assert_game_shape(body)
    assert response.headers["location"] == f"{GAMES}/{body['id']}"
    assert body["status"] == "in_progress"
    assert body["current_player"] == "x"
    assert body["winner"] is None
    assert body["active_board"] is None
    assert body["moves"] == []
    assert body["created_at"].endswith("Z")
    assert all(board["playable"] for board in body["boards"])
    assert all(cell is None for board in body["boards"] for cell in board["cells"])


# --- GET /games/{id} --------------------------------------------------------------------------


async def test_get_game_returns_the_game(client: AsyncClient) -> None:
    game_id = await new_game(client)

    response = await client.get(f"{GAMES}/{game_id}")

    assert response.status_code == 200
    assert_game_shape(response.json())
    assert response.json()["id"] == game_id


async def test_get_game_that_does_not_exist_returns_404(client: AsyncClient) -> None:
    assert_error(await client.get(f"{GAMES}/999"), 404, "game_not_found")


async def test_get_game_with_a_non_numeric_id_returns_422(client: AsyncClient) -> None:
    assert_error(await client.get(f"{GAMES}/abc"), 422, "validation_error")


# --- POST /games/{id}/moves: success ----------------------------------------------------------


async def test_a_legal_move_returns_201_and_the_updated_game(client: AsyncClient) -> None:
    game_id = await new_game(client)

    response = await play(client, game_id, board=4, cell=2)

    assert response.status_code == 201
    assert response.headers["location"] == f"{GAMES}/{game_id}"
    body = response.json()
    assert_game_shape(body)
    assert body["boards"][4]["cells"][2] == "x"
    assert body["current_player"] == "o"
    assert body["active_board"] == 2
    assert [board["playable"] for board in body["boards"]] == [i == 2 for i in range(9)]
    assert [(m["sequence"], m["board"], m["cell"], m["player"]) for m in body["moves"]] == [
        (0, 4, 2, "x")
    ]


async def test_being_sent_to_a_decided_board_opens_every_open_board(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, FREE_MOVE_PREFIX)

    body = (await client.get(f"{GAMES}/{game_id}")).json()

    assert body["active_board"] is None
    assert body["boards"][0]["status"] == "won"
    assert body["boards"][0]["winner"] == "o"
    assert [board["playable"] for board in body["boards"]] == [
        board["status"] == "open" for board in body["boards"]
    ]


async def test_a_winning_move_ends_the_game(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, X_WINS_GAME)

    body = (await client.get(f"{GAMES}/{game_id}")).json()

    assert body["status"] == "won"
    assert body["winner"] == "x"
    assert body["current_player"] is None
    assert not any(board["playable"] for board in body["boards"])


# --- POST /games/{id}/moves: refusals ---------------------------------------------------------


async def test_move_in_a_game_that_does_not_exist_returns_404(client: AsyncClient) -> None:
    assert_error(await play(client, 999, 0, 0), 404, "game_not_found")


async def test_move_outside_the_active_board_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play(client, game_id, 4, 2)
    assert_error(await play(client, game_id, 5, 0), 409, "wrong_board")


async def test_move_on_a_taken_square_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, [(2, 0), (0, 2)])
    assert_error(await play(client, game_id, 2, 0), 409, "cell_occupied")


async def test_move_in_a_decided_board_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, FREE_MOVE_PREFIX)
    assert_error(await play(client, game_id, 0, 0), 409, "board_closed")


async def test_move_after_the_game_is_over_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, X_WINS_GAME)
    assert_error(await play(client, game_id, 1, 0), 409, "game_finished")


@pytest.mark.parametrize(
    "payload",
    [
        {"board": 9, "cell": 0},
        {"board": 0, "cell": -1},
        {"board": "3", "cell": 0},
        {"board": 0},
        {"board": 0, "cell": 0, "player": "o"},
    ],
    ids=["board-too-big", "cell-negative", "board-as-string", "cell-missing", "extra-field"],
)
async def test_malformed_move_returns_422(client: AsyncClient, payload: dict[str, Any]) -> None:
    game_id = await new_game(client)
    response = await client.post(f"{GAMES}/{game_id}/moves", json=payload)
    assert_error(response, 422, "validation_error")


# --- Derived values are computed, not stored --------------------------------------------------


async def test_reading_a_game_derives_winners_without_writing_anything(
    client: AsyncClient, engine: Engine
) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, FREE_MOVE_PREFIX)

    statements: list[str] = []

    def record(_conn: Any, _cursor: Any, statement: str, *_args: Any) -> None:
        statements.append(statement.strip().split()[0].upper())

    event.listen(engine, "before_cursor_execute", record)
    try:
        body = (await client.get(f"{GAMES}/{game_id}")).json()
    finally:
        event.remove(engine, "before_cursor_execute", record)

    assert body["boards"][0]["winner"] == "o"
    assert body["boards"][8]["winner"] == "x"
    assert body["current_player"] == "x"
    assert statements, "expected the read to query the database"
    assert set(statements) == {"SELECT"}


# --- Unknown routes use the same envelope -----------------------------------------------------


async def test_unknown_route_returns_404_in_the_error_envelope(client: AsyncClient) -> None:
    assert_error(await client.get("/api/v1/nope"), 404, "not_found")
