import { test, expect } from "@playwright/test";

test("edita un criterio y recalcula prioridad y orden sin recargar", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Baja");
  await page.getByLabel("Descripción").fill("Dato sintético");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByRole("heading", { name: "Baja" })).toBeVisible();
  await page.getByLabel("Título").fill("Alta");
  await page.getByLabel("Descripción").fill("Dato sintético");
  await page.getByLabel("Impacto").fill("10");
  await page.getByLabel("Confianza").fill("10");
  await page.getByLabel("Facilidad").fill("10");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByRole("heading", { name: "Alta" })).toBeVisible();

  const firstTitle = async () =>
    (await page.locator("ul.ideas > li h3").first().textContent()) ?? "";
  expect(await firstTitle()).toBe("Alta");

  const card = page.locator(".idea").filter({ hasText: "Baja" });
  await card.getByRole("button", { name: "Editar" }).click();
  const editForm = page.locator("form.edit-form");
  await editForm.getByLabel("Editar impacto").fill("10");
  await editForm.getByLabel("Editar confianza").fill("10");
  await editForm.getByLabel("Editar facilidad").fill("10");
  await editForm.getByRole("button", { name: "Guardar cambios" }).click();

  await expect(page.locator(".idea").filter({ hasText: "Baja" })).toContainText(
    "Prioridad 1000",
  );
  expect(await firstTitle()).toBe("Baja");
});
