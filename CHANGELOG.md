# Changelog

## 0.1.0

- Two players on one screen can start a game of ultimate tic-tac-toe and play it to a win or a draw.
- The backend stores each game's moves in SQLite and enforces every rule. Illegal moves are refused with a `409` and a reason.
- The frontend shows the board, whose turn it is, and which board they must play in.
- Docker Compose runs the backend and the frontend together. GitHub Actions lints, typechecks, and tests both on every push and pull request.
