import { test, expect } from "@playwright/test";

test("contexto aislado tipo privado no conserva IndexedDB tras cerrarse", async ({
  browser,
}) => {
  const first = await browser.newContext();
  const page = await first.newPage();
  await page.goto("/");
  await page.getByLabel("Título").fill("Privada");
  await page.getByLabel("Descripción").fill("Sesión sintética");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByRole("heading", { name: "Privada" })).toBeVisible();
  await first.close();
  const second = await browser.newContext();
  const reopened = await second.newPage();
  await reopened.goto("/");
  await expect(reopened.getByRole("heading", { name: "Privada" })).toHaveCount(
    0,
  );
  await second.close();
});

test("ausencia de IndexedDB muestra fallback sin afirmar persistencia", async ({
  page,
}) => {
  await page.addInitScript(() =>
    Object.defineProperty(window, "indexedDB", {
      configurable: true,
      get: () => undefined,
    }),
  );
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText(
    "Persistencia local no disponible",
  );
});
