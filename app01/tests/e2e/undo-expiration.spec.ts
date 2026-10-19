import { test, expect } from "@playwright/test";

test("expira el deshacer después de diez segundos", async ({ page }) => {
  test.setTimeout(20_000);
  await page.goto("/");
  await page.getByLabel("Título").fill("Expirable");
  await page.getByLabel("Descripción").fill("Dato sintético");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await page.getByRole("button", { name: "Eliminar" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Eliminar idea" })
    .click();
  await expect(
    page.getByRole("button", { name: "Deshacer eliminación" }),
  ).toBeVisible();
  await page.waitForTimeout(10_500);
  await expect(
    page.getByRole("button", { name: "Deshacer eliminación" }),
  ).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Expirable" })).toHaveCount(0);
});
