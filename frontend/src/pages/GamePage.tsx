import { Link, useParams } from "react-router";
import { ApiError } from "../api/client";
import { useGame, usePlayMove } from "../api/games";
import { GameStatus } from "../components/GameStatus";
import { UltimateBoard } from "../components/UltimateBoard";

export function GamePage() {
  const { gameId } = useParams();
  const id = Number(gameId);
  if (!Number.isInteger(id) || id < 1) return <GameNotFound />;
  return <Game gameId={id} />;
}

function GameNotFound() {
  return (
    <section className="flex flex-col items-center gap-4 text-center">
      <h2 className="text-2xl font-bold">Game not found</h2>
      <Link to="/" className="font-semibold text-action underline">
        Start a new game
      </Link>
    </section>
  );
}

function Game({ gameId }: { gameId: number }) {
  const game = useGame(gameId);
  const move = usePlayMove(gameId);

  if (game.isPending) {
    return <p role="status">Loading game…</p>;
  }

  if (game.isError) {
    if (game.error instanceof ApiError && game.error.status === 404) return <GameNotFound />;
    return (
      <section className="flex flex-col items-center gap-4 text-center">
        <p role="alert" className="text-error">
          Couldn't load the game: {game.error.message}
        </p>
        <button
          type="button"
          onClick={() => void game.refetch()}
          className="rounded-md bg-action px-4 py-2 font-semibold text-white hover:bg-action-hover focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus"
        >
          Retry
        </button>
      </section>
    );
  }

  return (
    <section className="flex w-full flex-col items-center gap-4">
      <GameStatus game={game.data} />
      {move.isError && (
        <p role="alert" className="text-error">
          {move.error.message}
        </p>
      )}
      <UltimateBoard
        game={game.data}
        disabled={move.isPending}
        onPlay={(board, cell) => move.mutate({ board, cell })}
      />
    </section>
  );
}
