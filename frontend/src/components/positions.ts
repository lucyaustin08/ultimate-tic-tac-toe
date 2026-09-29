export const POSITION_NAMES = [
  "top left",
  "top center",
  "top right",
  "middle left",
  "center",
  "middle right",
  "bottom left",
  "bottom center",
  "bottom right",
] as const;

export function positionName(index: number): string {
  return POSITION_NAMES[index] ?? `position ${index + 1}`;
}

export function playerName(player: "x" | "o"): string {
  return player.toUpperCase();
}
