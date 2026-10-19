import { test, expect } from "@playwright/test";

test("IndexedDB aborta una transacción y conserva el snapshot", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Snapshot");
  await page.getByLabel("Descripción").fill("Antes del abort");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByText("Snapshot")).toBeVisible();
  await page.evaluate(
    () =>
      new Promise<void>((resolve, reject) => {
        const open = indexedDB.open("idea-prioritizer");
        open.onerror = () => reject(open.error);
        open.onsuccess = () => {
          const db = open.result;
          const tx = db.transaction("ideas", "readwrite");
          tx.objectStore("ideas").clear();
          tx.abort();
          tx.onabort = () => {
            db.close();
            resolve();
          };
          tx.onerror = () => {
            db.close();
            resolve();
          };
        };
      }),
  );
  await page.reload();
  await expect(page.getByText("Snapshot")).toBeVisible();
});
