# Ultimate Tic-Tac-Toe

A web version of ultimate tic-tac-toe for two players sharing one screen.

## Rules

- The board is a 3×3 grid of small 3×3 boards.
- X moves first and may play anywhere.
- After that, you must play in the small board that matches the square your opponent just marked. For example, if they marked the top-right square of any board, you play in the top-right board.
- Three in a row on a small board wins that board. A board that fills up with no winner counts for nobody. Nobody can play in a decided board again.
- If you are sent to a decided board, you may play in any open board instead.
- Win three small boards in a row to win the game. If every board is decided and nobody has three in a row, the game is a draw.

## Run it

You need Docker. From the repository root:

```sh
docker compose up --build
```

Then open <http://localhost:8080>.

## Develop

### Backend (Python 3.14, uv)

```sh
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The API runs at <http://localhost:8000>, with interactive docs at `/docs`.

Checks:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --cov=app --cov-report=term-missing:skip-covered --cov-report=html --cov-fail-under=80
```

### Frontend (Node 24, pnpm)

```sh
cd frontend
corepack enable
pnpm install
pnpm dev
```

The app runs at <http://localhost:5173> and forwards `/api` to the backend.

Checks:

```sh
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test:cov
```

After changing the API, regenerate the frontend types (the backend must be installed):

```sh
pnpm gen:api
```

End-to-end smoke test, with `docker compose up` running:

```sh
pnpm exec playwright install chromium
pnpm e2e
```

## Layout

| Path | What it holds |
|---|---|
| `backend/app/services/rules.py` | The game rules, as pure functions |
| `backend/app/services/game_service.py` | Use cases: create a game, read it, play a move |
| `backend/app/repositories/` | Database access |
| `backend/app/api/v1/` | HTTP routes and error handling |
| `frontend/src/pages/` | The start page and the game page |
| `frontend/src/components/` | The board |
| `infra/docker/` | Dockerfiles and the nginx config |

Design choices and the alternatives that were not taken are recorded in [DECISIONS.md](DECISIONS.md).
