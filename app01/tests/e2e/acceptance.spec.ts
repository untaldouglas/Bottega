import { test, expect } from "@playwright/test";

test("persiste una idea al recargar", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Título").fill("Persistente");
  await page.getByLabel("Descripción").fill("Dato sintético persistente");
  await page.getByLabel("Impacto").fill("8");
  await page.getByLabel("Confianza").fill("5");
  await page.getByLabel("Facilidad").fill("6");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(
    page.getByRole("heading", { name: "Persistente" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Persistente" }),
  ).toBeVisible();
});

test("bloquea red externa, trata XSS como texto y publica CSP/estado accesible", async ({
  page,
}) => {
  const external: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).origin !== "http://127.0.0.1:5183")
      external.push(request.url());
  });
  await page.goto("/");
  expect(external).toEqual([]);
  await expect(
    page.locator('meta[http-equiv="Content-Security-Policy"]'),
  ).toHaveAttribute("content", /connect-src 'none'/);
  await page.getByLabel("Título").fill("<script>window.__xss=1</script>");
  await page
    .getByLabel("Descripción")
    .fill("Texto <img src=x onerror=alert(1)>");
  await page.getByLabel("Impacto").fill("1");
  await page.getByLabel("Confianza").fill("1");
  await page.getByLabel("Facilidad").fill("1");
  await page.getByRole("button", { name: "Agregar idea" }).click();
  await expect(page.getByText("<script>window.__xss=1</script>")).toBeVisible();
  expect(
    await page.evaluate(() => (window as unknown as { __xss?: number }).__xss),
  ).toBeUndefined();
  await expect(page.locator('[role="status"]')).toHaveAttribute(
    "aria-live",
    "polite",
  );
});

test("mantiene foco visible, zoom 200% y contraste declarativo", async ({
  page,
}) => {
  await page.goto("/");
  await page.setViewportSize({ width: 640, height: 480 });
  await page.evaluate(() => {
    document.body.style.zoom = "2";
  });
  await page.getByLabel("Título").focus();
  const accessibility = await page.evaluate(() => {
    const input = document.querySelector('input[name="titulo"]')!;
    const styles = getComputedStyle(input);
    return {
      outline: styles.outlineStyle,
      color: styles.color,
      background: styles.backgroundColor,
      overflow:
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth * 2,
    };
  });
  expect(accessibility.outline).not.toBe("none");
  expect(accessibility.color).not.toBe(accessibility.background);
  expect(accessibility.overflow).toBe(true);
});

test("permite navegación por teclado en formulario", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Título").focus();
  await expect(page.getByLabel("Título")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Impacto")).toBeFocused();
});
