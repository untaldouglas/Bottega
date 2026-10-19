import { test, expect } from "@playwright/test";

test("edita, cambia estado y deshace eliminación", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Editable");
  await page.getByLabel("Descripción").fill("Descripción inicial");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  const card = page.locator(".idea").filter({ hasText: "Editable" });
  await card.getByRole("combobox").selectOption("aprobada");
  await card.getByRole("button", { name: "Editar" }).click();
  const editForm = page.locator("form.edit-form");
  await editForm.getByLabel("Editar título").fill("Editada");
  await editForm.getByLabel("Editar descripción").fill("Descripción editada");
  await editForm.getByRole("button", { name: "Guardar cambios" }).click();
  await expect(page.getByRole("heading", { name: "Editada" })).toBeVisible();
  await page.getByRole("button", { name: "Eliminar" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Eliminar idea" })
    .click();
  await expect(
    page.getByRole("button", { name: "Deshacer eliminación" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Deshacer eliminación" }).click();
  await expect(page.getByRole("heading", { name: "Editada" })).toBeVisible();
});
