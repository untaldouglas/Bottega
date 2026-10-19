import { test, expect } from "@playwright/test";

test("Reemplazar sustituye, cancelar conserva y JSON adversarial se rechaza", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Local");
  await page.getByLabel("Descripción").fill("Local sintética");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  const replacement = JSON.stringify({
    schemaVersion: "1.0",
    exportedAt: "2026-01-01T00:00:00.000Z",
    ideas: [
      {
        id: "replacement",
        titulo: "Reemplazo",
        descripcion: "Sintética",
        estado: "borrador",
        impacto: 2,
        confianza: 2,
        facilidad: 2,
        prioridad: 8,
        creadaEn: "2026-01-01T00:00:00.000Z",
        modificadaEn: "2026-01-01T00:00:00.000Z",
        etiquetas: [],
        notas: "",
      },
    ],
  });
  await page.locator("#import").setInputFiles({
    name: "replace.json",
    mimeType: "application/json",
    buffer: Buffer.from(replacement),
  });
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Modo de importación").selectOption("reemplazar");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Confirmar importación" })
    .click();
  await expect(page.getByRole("heading", { name: "Reemplazo" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Local" })).toHaveCount(0);
  await page.locator("#import").setInputFiles({
    name: "cancel.json",
    mimeType: "application/json",
    buffer: Buffer.from(replacement),
  });
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Cancelar" })
    .click();
  await expect(page.getByRole("heading", { name: "Reemplazo" })).toBeVisible();
  await page.locator("#import").setInputFiles({
    name: "adversarial.json",
    mimeType: "application/json",
    buffer: Buffer.from('{"ideas": ['),
  });
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("dialog")).toContainText("Importación rechazada");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Cerrar" })
    .click();
});

test("exporta y reimporta en modo combinar sin duplicar", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Round trip");
  await page.getByLabel("Descripción").fill("Datos sintéticos");
  await page.getByLabel("Impacto").fill("8");
  await page.getByLabel("Confianza").fill("5");
  await page.getByLabel("Facilidad").fill("6");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  const before = await page.evaluate(
    () =>
      new Promise<unknown>((resolve, reject) => {
        const request = indexedDB.open("idea-prioritizer");
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
          const tx = request.result.transaction("ideas");
          const get = tx.objectStore("ideas").getAll();
          get.onsuccess = () => {
            request.result.close();
            resolve(get.result[0]);
          };
        };
      }),
  );
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Exportar JSON" }).click();
  const download = await downloadPromise;
  const path = await download.path();
  expect(path).not.toBeNull();
  await page.locator("#import").setInputFiles(path!);
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Modo de importación").selectOption("combinar");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Confirmar importación" })
    .click();
  await expect(page.getByText("Round trip")).toBeVisible();
  const after = await page.evaluate(
    () =>
      new Promise<unknown>((resolve, reject) => {
        const request = indexedDB.open("idea-prioritizer");
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
          const tx = request.result.transaction("ideas");
          const get = tx.objectStore("ideas").getAll();
          get.onsuccess = () => {
            request.result.close();
            resolve(get.result[0]);
          };
        };
      }),
  );
  expect(after).toEqual(before);
});
