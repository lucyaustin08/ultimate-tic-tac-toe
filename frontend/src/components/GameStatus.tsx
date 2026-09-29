import type { Game } from "../api/client";
import { playerName, positionName } from "./positions";

export function gameStatusText(game: Game): string {
  if (game.status === "won" && game.winner) return `${playerName(game.winner)} wins!`;
  if (game.status === "drawn") return "It's a draw.";
  if (!game.current_player) return "";

  const player = playerName(game.current_player);
  if (game.active_board === null) return `${player} to move in any open board.`;
  return `${player} to move in the ${positionName(game.active_board)} board.`;
}

export function GameStatus({ game }: { game: Game }) {
  return (
    <p aria-live="polite" className="text-xl font-semibold">
      {gameStatusText(game)}
    </p>
  );
}
