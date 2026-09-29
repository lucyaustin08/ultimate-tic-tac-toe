import { useNavigate } from "react-router";
import { useCreateGame } from "../api/games";

export function HomePage() {
  const navigate = useNavigate();
  const createGame = useCreateGame();

  const start = () =>
    createGame.mutate(undefined, {
      onSuccess: (game) => navigate(`/games/${game.id}`),
    });

  return (
    <section className="flex flex-col items-center gap-6 text-center">
      <p className="max-w-md">
        Two players, one screen. Your move decides which small board your opponent must play in
        next. Win three small boards in a row to win the game.
      </p>
      <button
        type="button"
        onClick={start}
        disabled={createGame.isPending}
        className="rounded-md bg-action px-6 py-3 text-lg font-semibold text-white hover:bg-action-hover focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-focus disabled:opacity-60"
      >
        {createGame.isPending ? "Starting…" : "Start game"}
      </button>
      {createGame.isError && (
        <p role="alert" className="text-error">
          Couldn't start a game: {createGame.error.message}
        </p>
      )}
    </section>
  );
}
