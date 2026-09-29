import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { finishedGame, newGame } from "../test/fixtures";
import { errorHandlers, setServerGame } from "../test/handlers";
import { renderAt } from "../test/render";
import { server } from "../test/server";

const square = (board: string, cell: string) =>
  screen.getByRole("button", { name: new RegExp(`^${board} board, ${cell} square`) });

describe("GamePage", () => {
  it("shows a loading message while the game is fetched", async () => {
    renderAt("/games/1");

    expect(screen.getByRole("status")).toHaveTextContent("Loading game…");
    expect(await screen.findByText("X to move in any open board.")).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows an empty board with every square open when the game has no moves", async () => {
    renderAt("/games/1");

    const board = await screen.findByRole("group", { name: "Game board" });
    const squares = within(board).getAllByRole("button");
    expect(squares).toHaveLength(81);
    squares.forEach((button) => expect(button).toBeEnabled());
    expect(within(board).getAllByRole("group")).toHaveLength(9);
  });

  it("shows an error with a retry button that reloads the game", async () => {
    server.use(errorHandlers.getGameFailsOnce);
    const user = userEvent.setup();
    renderAt("/games/1");

    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load the game");
    await user.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByRole("group", { name: "Game board" })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("says the game was not found when the API has no such game", async () => {
    renderAt("/games/42");

    expect(await screen.findByRole("heading", { name: "Game not found" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Start a new game" })).toHaveAttribute("href", "/");
  });

  it("says the game was not found for an id that is not a number", () => {
    renderAt("/games/abc");

    expect(screen.getByRole("heading", { name: "Game not found" })).toBeInTheDocument();
  });

  it("marks the square, passes the turn, and limits play to the matching board", async () => {
    const user = userEvent.setup();
    renderAt("/games/1");
    await screen.findByRole("group", { name: "Game board" });

    await user.click(square("top left", "center"));

    expect(await screen.findByText("O to move in the center board.")).toBeInTheDocument();
    expect(square("top left", "center")).toHaveTextContent("X");
    expect(square("top left", "center")).toBeDisabled();
    expect(square("center", "top left")).toBeEnabled();
    expect(square("top right", "top left")).toBeDisabled();
  });

  it("can be played with the keyboard", async () => {
    const user = userEvent.setup();
    renderAt("/games/1");
    await screen.findByRole("group", { name: "Game board" });

    await user.tab(); // the title link
    await user.tab(); // the first square
    expect(square("top left", "top left")).toHaveFocus();
    await user.keyboard("{Enter}");

    expect(await screen.findByText("O to move in the top left board.")).toBeInTheDocument();
    expect(square("top left", "top left")).toHaveTextContent("X");
  });

  it("shows why a move was refused", async () => {
    server.use(errorHandlers.moveRefused);
    const user = userEvent.setup();
    renderAt("/games/1");
    await screen.findByRole("group", { name: "Game board" });

    await user.click(square("top left", "center"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "This move must be played in board 4.",
    );
    expect(square("top left", "center")).toHaveTextContent("");
  });

  it("announces the winner and disables every square when the game is over", async () => {
    setServerGame(finishedGame("x"));
    renderAt("/games/1");

    expect(await screen.findByText("X wins!")).toBeInTheDocument();
    screen
      .getAllByRole("button", { name: /square/ })
      .forEach((button) => expect(button).toBeDisabled());
  });

  it("names who won each decided small board", async () => {
    setServerGame(finishedGame("o"));
    renderAt("/games/1");

    expect(
      await screen.findByRole("group", { name: "top left board, won by O" }),
    ).toBeInTheDocument();
  });

  it("announces a draw", async () => {
    setServerGame(newGame({ status: "drawn", current_player: null }));
    renderAt("/games/1");

    expect(await screen.findByText("It's a draw.")).toBeInTheDocument();
  });
});
