import { describe, expect, it } from "vitest";
import { createIdea } from "../src/domain";
import { exportDocument, importPreview } from "../src/exchange";

const idea = createIdea(
  {
    titulo: "Hallmark",
    descripcion: "Sintética",
    impacto: 8,
    confianza: 5,
    facilidad: 6,
  },
  { id: () => "hallmark-1", now: () => "2026-01-01T00:00:00.000Z" },
);

describe("Hallmark exchange contract", () => {
  it("always emits exportedAt and accepts a valid optional value", () => {
    const document = JSON.parse(
      exportDocument([idea], "2026-01-02T00:00:00.000Z"),
    );
    expect(document.exportedAt).toBe("2026-01-02T00:00:00.000Z");
    expect(
      importPreview(
        JSON.stringify({ ...document, exportedAt: undefined }),
        [],
        "reemplazar",
      ).issues,
    ).toEqual([]);
    expect(
      importPreview(
        JSON.stringify({ ...document, exportedAt: "not-a-date" }),
        [],
        "reemplazar",
      ).issues,
    ).toHaveLength(1);
  });

  it("exposes normalizedBytes as derived data and not persisted on ideas", () => {
    const preview = importPreview(exportDocument([idea]), [], "reemplazar");
    expect(preview.normalizedBytes).toBeGreaterThan(0);
    expect(preview.proposed[0]).not.toHaveProperty("normalizedBytes");
  });
});
