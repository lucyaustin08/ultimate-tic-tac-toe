import type { Game } from "../api/client";
import { SmallBoard } from "./SmallBoard";

type UltimateBoardProps = {
  game: Game;
  disabled: boolean;
  onPlay: (board: number, cell: number) => void;
};

export function UltimateBoard({ game, disabled, onPlay }: UltimateBoardProps) {
  return (
    <div
      role="group"
      aria-label="Game board"
      className="grid w-full max-w-xl grid-cols-3 gap-3 rounded-lg bg-frame p-3"
    >
      {game.boards.map((board) => (
        <SmallBoard key={board.index} board={board} disabled={disabled} onPlay={onPlay} />
      ))}
    </div>
  );
}
