import { describe, expect, it } from "vitest";
import { createIdea } from "../src/domain";
import {
  exportDocument,
  importPreview,
  applyImport,
  LIMITS,
} from "../src/exchange";
const idea = createIdea(
  { titulo: "A", descripcion: "B", impacto: 1, confianza: 2, facilidad: 3 },
  { id: () => "one", now: () => "2026-01-01T00:00:00.000Z" },
);
describe("exchange", () => {
  it("round trips a compact versioned document", () => {
    const json = exportDocument([idea], "2026-01-02T00:00:00.000Z");
    expect(JSON.parse(json)).toMatchObject({
      schemaVersion: "1.0",
      ideas: [idea],
    });
    expect(new TextEncoder().encode(json).byteLength).toBeLessThan(
      LIMITS.collectionBytes,
    );
  });
  it("rejects duplicate ids without mutating the local collection", () => {
    const duplicate = { ...idea };
    const source = JSON.stringify({
      schemaVersion: "1.0",
      exportedAt: "2026-01-01T00:00:00.000Z",
      ideas: [idea, duplicate],
    });
    const preview = importPreview(source, [idea], "combinar");
    expect(preview.issues.some((i) => i.code === "DUPLICATE_ID")).toBe(true);
    expect(applyImport(preview, [idea])).toEqual([idea]);
  });
  it("combines and replaces by id only after a valid preview", () => {
    const incoming = { ...idea, titulo: "Actualizada" };
    const newIdea = { ...idea, id: "new", titulo: "Nueva" };
    const p = importPreview(
      JSON.stringify({
        schemaVersion: "1.0",
        exportedAt: "2026-01-01T00:00:00.000Z",
        ideas: [incoming, newIdea],
      }),
      [idea],
      "combinar",
    );
    expect(p.issues).toHaveLength(0);
    expect(applyImport(p, [idea]).map((i) => i.id)).toEqual(["one", "new"]);
  });
});
