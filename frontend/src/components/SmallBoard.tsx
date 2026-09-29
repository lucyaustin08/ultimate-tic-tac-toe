import type { SmallBoard as SmallBoardData } from "../api/client";
import { playerName, positionName } from "./positions";

type SmallBoardProps = {
  board: SmallBoardData;
  disabled: boolean;
  onPlay: (board: number, cell: number) => void;
};

function boardLabel(board: SmallBoardData): string {
  const name = `${positionName(board.index)} board`;
  if (board.status === "won" && board.winner) return `${name}, won by ${playerName(board.winner)}`;
  if (board.status === "drawn") return `${name}, drawn`;
  return name;
}

export function SmallBoard({ board, disabled, onPlay }: SmallBoardProps) {
  const decided = board.status !== "open";

  return (
    <div
      role="group"
      aria-label={boardLabel(board)}
      className="relative grid grid-cols-3 gap-1 rounded-md bg-board p-1.5"
    >
      {board.cells.map((mark, cell) => {
        const canPlay = !disabled && board.playable && mark === null;
        const label = `${positionName(board.index)} board, ${positionName(cell)} square, ${
          mark ? playerName(mark) : "empty"
        }`;
        return (
          <button
            key={cell}
            type="button"
            aria-label={label}
            disabled={!canPlay}
            onClick={() => onPlay(board.index, cell)}
            className={[
              "flex aspect-square items-center justify-center rounded-sm bg-cell text-2xl font-bold",
              "focus-visible:outline-3 focus-visible:outline-offset-1 focus-visible:outline-focus",
              canPlay ? "cursor-pointer hover:bg-cell-hover" : "cursor-default",
              mark === "x" ? "text-player-x" : "text-player-o",
            ].join(" ")}
          >
            {mark ? playerName(mark) : ""}
          </button>
        );
      })}

      {decided && (
        <div
          aria-hidden="true"
          className={[
            "pointer-events-none absolute inset-0 flex items-center justify-center rounded-md",
            "bg-board/80 text-7xl font-black",
            board.winner === "x" ? "text-player-x" : "text-player-o",
          ].join(" ")}
        >
          {board.winner ? playerName(board.winner) : "–"}
        </div>
      )}
    </div>
  );
}
