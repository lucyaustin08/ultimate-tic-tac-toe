# Decisions

Every choice below had a real alternative. Each entry names what was chosen, what was not, and why.

## Game rules (confirmed with the product owner)

- **The whole game is won with three captured small boards in a row** on the big board.
- **A decided small board is closed.** Once a board is won, or filled with no winner, nobody may play in it again, even if it still has empty squares.
- **A small board that fills up with no winner counts for nobody.**
- **The game is a draw when every small board is decided and nobody has three in a row.** *Not chosen:* ending the game early once no line is possible, or awarding the win to whoever captured more boards. Those are known variants the product owner did not ask for.
- **X always moves first.**
- **Being sent to a decided board gives a free move** in any open board. That is what "a place where they can't play" means once decided boards are closed.

## Scope

- **Only what was asked for.** The product owner asked that nothing extra be added. The UI has one "Start game" button, the board, and a status line. *Not built:* a "New game" button on the game page, visual highlighting of the active board, undo, player names, or a list of past games.
- **The status line names the board the next move must go in** ("O to move in the center board."). This is the rule itself stated in words, not an extra. Without it, the only clue would be which squares are disabled, which is hard to see and does not meet the accessibility floor.
- **No list endpoint.** Nothing in the requirements lists games, so the list conventions (`q`, `sort`, paging) have nothing to apply to.
- **No delete endpoint**, so there is nothing to soft-delete.
- **Local deployment is `docker compose up`.** No hosting was requested.

## Design

- **Only moves are stored; everything else is derived.** A move stores its game, sequence number, board and cell. Whose turn it is (sequence parity), which board is active, who won each small board, and who won the game are recomputed by replaying the moves through `app/services/rules.py`. *Not chosen:* storing a status, winner, or current player on the game row, which the constitution forbids and which could fall out of sync.
- **The rules engine is pure functions over frozen dataclasses**, with no database or HTTP. It is tested exhaustively without any setup.
- **The server enforces every rule.** The frontend never decides whether a move is legal. The API marks each small board `playable`, and the UI simply enables those squares. *Not chosen:* repeating the rules in TypeScript, which would mean two copies to keep in agreement.
- **`POST /api/v1/games/{id}/moves` returns `201` with the updated game**, and its `Location` header points at the game. A move has no URL of its own. *Not chosen:* a `GET .../moves/{sequence}` endpoint just so `Location` could point at the move. The product owner asked for nothing extra, and returning the game saves the client a second request.
- **Illegal moves return `409`** with one of `wrong_board`, `board_closed`, `cell_occupied`, `game_finished`. A board or cell outside 0–8 is a schema failure, so it returns `422`.
- **Two moves racing for the same turn** (for example a double click) are stopped by a unique constraint on `(game_id, sequence)`. The loser gets `409 move_conflict`. *Not chosen:* locking, which is more machinery than a same-screen game needs.
- **Game ids are auto-increment integers.** *Not chosen:* UUIDs. There are no accounts and nothing to hide, and small ids keep URLs readable.
- **Timestamps pass through a `UTCDateTime` column type**, because SQLite drops timezone information and the API must emit UTC.
- **Settings are read with `os.environ`.** *Not chosen:* `pydantic-settings`, which is not in the stack contract and is not worth a dependency for one variable.
- **The backend healthcheck requests `/openapi.json`.** *Not chosen:* a dedicated health endpoint, since one would be an extra route.
- **Operation ids are the route function names**, so generated TypeScript reads `get_game` rather than `get_game_api_v1_games__game_id__get`.
- **`openapi-fetch` is given a `fetch` wrapper that looks up `globalThis.fetch` on every call.** Otherwise the client captures `fetch` when the module loads, before MSW installs its interceptor in tests.
- **CI checks that `src/api/schema.d.ts` matches the backend.** It regenerates the types and fails on any difference, so the types can never be hand-edited out of sync.

## Tests

- **No repository pagination tests.** There is no list endpoint, so there are no paging boundaries to test.
- **No client-side validation tests.** The UI has no form inputs, only buttons.
- **The frontend's MSW move handler places the mark and sends play to the matching board, and does nothing more.** The real rules are tested on the backend. The mock only needs to be realistic enough to drive the UI.
