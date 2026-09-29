import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, createGame, fetchGame, playMove, type Game } from "./client";

export const gameQueryKey = (gameId: number) => ["games", gameId] as const;

export function useGame(gameId: number) {
  return useQuery({
    queryKey: gameQueryKey(gameId),
    queryFn: () => fetchGame(gameId),
  });
}

export function useCreateGame() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createGame,
    onSuccess: (game) => queryClient.setQueryData(gameQueryKey(game.id), game),
  });
}

export function usePlayMove(gameId: number) {
  const queryClient = useQueryClient();
  return useMutation<Game, Error, { board: number; cell: number }>({
    mutationFn: ({ board, cell }) => playMove(gameId, board, cell),
    onSuccess: (game) => queryClient.setQueryData(gameQueryKey(gameId), game),
    onError: async (error) => {
      // A refused move means this screen may be out of date, so reload the game.
      if (error instanceof ApiError && error.status === 409) {
        await queryClient.invalidateQueries({ queryKey: gameQueryKey(gameId) });
      }
    },
  });
}
