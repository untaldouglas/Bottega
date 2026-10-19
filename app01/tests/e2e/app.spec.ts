import { test, expect } from "@playwright/test";
test("crea una idea y muestra prioridad", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Idea sintética");
  await page.getByLabel("Descripción").fill("Descripción sintética");
  await page.getByLabel("Impacto").fill("8");
  await page.getByLabel("Confianza").fill("5");
  await page.getByLabel("Facilidad").fill("6");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByText(/Prioridad 240/)).toBeVisible();
});
