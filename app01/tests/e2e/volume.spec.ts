import { test, expect } from "@playwright/test";

test("IndexedDB acepta exactamente 10.000 y rechaza 10.001 con snapshot intacto", async ({
  page,
  browserName,
}) => {
  test.skip(
    browserName !== "chromium",
    "La prueba de volumen usa IndexedDB real una vez en Chromium",
  );
  test.setTimeout(60_000);
  await page.addInitScript(() => {
    const originalGetAll = IDBObjectStore.prototype.getAll;
    IDBObjectStore.prototype.getAll = function (...args) {
      const request = originalGetAll.apply(this, args);
      const onSuccess = Object.getOwnPropertyDescriptor(
        IDBRequest.prototype,
        "onsuccess",
      );
      if (!onSuccess?.set) return request;
      const setter = onSuccess.set;
      Object.defineProperty(request, "onsuccess", {
        configurable: true,
        set(handler: ((event: Event) => void) | null) {
          setter.call(this, (event: Event) =>
            setTimeout(() => handler?.call(this, event), 6_000),
          );
        },
      });
      return request;
    };
  });
  await page.goto("/");
  const make = (count: number) =>
    JSON.stringify({
      schemaVersion: "1.0",
      exportedAt: "2026-01-01T00:00:00.000Z",
      ideas: Array.from({ length: count }, (_, index) => ({
        id: `volume-${index}`,
        titulo: `I${index}`,
        descripcion: "synthetic",
        estado: "borrador",
        impacto: 1,
        confianza: 1,
        facilidad: 1,
        prioridad: 1,
        creadaEn: "2026-01-01T00:00:00.000Z",
        modificadaEn: "2026-01-01T00:00:00.000Z",
        etiquetas: [],
        notas: "",
      })),
    });
  await page.locator("#import").setInputFiles({
    name: "10000.json",
    mimeType: "application/json",
    buffer: Buffer.from(make(10000)),
  });
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Modo de importación").selectOption("reemplazar");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Confirmar importación" })
    .click();
  await expect(page.getByRole("heading", { name: "I0" })).toBeVisible({
    timeout: 30_000,
  });
  await expect(page.getByRole("status")).toContainText(
    "Importación reemplazada",
  );
  await page.locator("#import").setInputFiles({
    name: "10001.json",
    mimeType: "application/json",
    buffer: Buffer.from(make(10001)),
  });
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("dialog")).toContainText("Importación rechazada");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Cerrar" })
    .click();
  await page.reload();
  await expect(page.getByRole("heading", { name: "I0" })).toBeVisible({
    timeout: 30_000,
  });
});
