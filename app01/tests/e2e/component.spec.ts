import { test, expect } from "@playwright/test";
test("componente de formulario es navegable y etiquetado", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("Título")).toHaveAttribute("maxlength", "120");
  await expect(page.getByLabel("Descripción")).toHaveAttribute(
    "maxlength",
    "2000",
  );
  await expect(
    page.getByRole("button", { name: "Agregar idea" }),
  ).toBeVisible();
});
test("IndexedDB expone el índice de estado", async ({ page }) => {
  await page.goto("/");
  const indexes = await page.evaluate(async () => {
    const request = indexedDB.open("idea-prioritizer");
    return await new Promise<string[]>((resolve, reject) => {
      request.onsuccess = () => {
        const names = Array.from(
          request.result.transaction("ideas").objectStore("ideas").indexNames,
        );
        request.result.close();
        resolve(names);
      };
      request.onerror = () => reject(request.error);
    });
  });
  expect(indexes).toContain("estado");
});
