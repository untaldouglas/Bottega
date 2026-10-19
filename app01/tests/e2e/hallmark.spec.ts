import { test, expect } from "@playwright/test";

for (const width of [320, 375, 414, 768, 1440]) {
  test(`Hallmark responsive ${width}px sin overflow`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Idea Prioritizer" }),
    ).toBeVisible();
    const overflow = await page.evaluate(
      () =>
        document.documentElement.scrollWidth >
        document.documentElement.clientWidth,
    );
    expect(overflow).toBe(false);
  });
}

test("Hallmark diálogo de eliminación conserva foco y Escape cancela", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Diálogo sintético");
  await page.getByLabel("Descripción").fill("Contenido sintético");
  await page.getByLabel("Impacto").fill("8");
  await page.getByLabel("Confianza").fill("5");
  await page.getByLabel("Facilidad").fill("6");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  const remove = page.getByRole("button", { name: "Eliminar" });
  await remove.click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: "Diálogo sintético" }),
  ).toBeVisible();
});

test("Hallmark carga stylesheet self y expone tokens computados", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator('link[rel="stylesheet"]')).toHaveCount(1);
  await expect(page.locator('link[rel="stylesheet"]')).toHaveAttribute(
    "href",
    /style|assets/,
  );
  await expect
    .poll(() =>
      page.evaluate(() =>
        getComputedStyle(document.documentElement)
          .getPropertyValue("--accent")
          .trim(),
      ),
    )
    .toBe("#1b6b50");
});

test("Hallmark usa scroll instantáneo con reduced motion", async ({ page }) => {
  await page.addInitScript(() => {
    const original = window.matchMedia;
    window.matchMedia = (query: string) =>
      query.includes("prefers-reduced-motion")
        ? ({
            matches: true,
            media: query,
            onchange: null,
            addListener: () => {},
            removeListener: () => {},
            addEventListener: () => {},
            removeEventListener: () => {},
            dispatchEvent: () => false,
          } as MediaQueryList)
        : original(query);
    Element.prototype.scrollIntoView = function (
      options?: ScrollIntoViewOptions,
    ) {
      (this as HTMLElement).dataset.scrollBehavior =
        typeof options === "object" ? (options.behavior ?? "auto") : "auto";
    };
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Ver colección" }).click();
  await expect(page.locator("#collection")).toHaveAttribute(
    "data-scroll-behavior",
    "auto",
  );
});
