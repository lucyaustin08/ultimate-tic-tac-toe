import { expect, test } from "@playwright/test";

test("two players can start a game and take turns", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Start game" }).click();

  await expect(page.getByText("X to move in any open board.")).toBeVisible();

  await page.getByRole("button", { name: /^top left board, center square/ }).click();
  await expect(page.getByText("O to move in the center board.")).toBeVisible();

  await page.getByRole("button", { name: /^center board, top right square/ }).click();
  await expect(page.getByText("X to move in the top right board.")).toBeVisible();
  await expect(
    page.getByRole("button", { name: /^center board, top right square, O$/ }),
  ).toBeVisible();
});
