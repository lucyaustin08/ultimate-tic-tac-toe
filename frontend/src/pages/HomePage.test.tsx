import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { errorHandlers } from "../test/handlers";
import { renderAt } from "../test/render";
import { server } from "../test/server";

describe("HomePage", () => {
  it("starts a game and opens it", async () => {
    const user = userEvent.setup();
    const { router } = renderAt("/");

    await user.click(screen.getByRole("button", { name: "Start game" }));

    expect(await screen.findByText("X to move in any open board.")).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/games/1");
  });

  it("shows an error and lets the player try again when a game can't be started", async () => {
    server.use(errorHandlers.createGameFails);
    const user = userEvent.setup();
    renderAt("/");

    await user.click(screen.getByRole("button", { name: "Start game" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't start a game");
    expect(screen.getByRole("button", { name: "Start game" })).toBeEnabled();
  });
});
