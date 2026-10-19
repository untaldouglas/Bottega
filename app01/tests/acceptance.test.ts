import { describe, expect, it } from "vitest";
import {
  createIdea,
  priority,
  sortIdeas,
  STATES,
  type Idea,
} from "../src/domain";
import {
  applyImport,
  exportDocument,
  importPreview,
  LIMITS,
} from "../src/exchange";
const deps = (id: string, now = "2026-01-01T00:00:00.000Z") => ({
  id: () => id,
  now: () => now,
});
const idea = (
  id: string,
  title = `Idea ${id}`,
  now = "2026-01-01T00:00:00.000Z",
) =>
  createIdea(
    {
      titulo: title,
      descripcion: "Descripción sintética",
      impacto: 8,
      confianza: 5,
      facilidad: 6,
      etiquetas: ["demo"],
      notas: "nota",
    },
    deps(id, now),
  );
describe("acceptance contract", () => {
  it("supports all five free state transitions and recalculated edits", () => {
    let current = idea("a");
    for (const estado of STATES) current = { ...current, estado };
    current = {
      ...current,
      impacto: 1,
      prioridad: priority(1, current.confianza, current.facilidad),
      modificadaEn: "2026-01-02T00:00:00.000Z",
    };
    expect(current.estado).toBe("implementada");
    expect(current.prioridad).toBe(30);
  });
  it("orders equal priority by modification and title", () => {
    const values = [
      idea("a", "Z", "2026-01-01T00:00:00.000Z"),
      idea("b", "A", "2026-01-01T00:00:00.000Z"),
      idea("c", "M", "2026-01-02T00:00:00.000Z"),
    ];
    expect(sortIdeas(values).map((x) => x.id)).toEqual(["c", "b", "a"]);
  });
  it("round trips identity, fields, priority and dates through export/import", () => {
    const source = [
      idea("a"),
      idea("b", "Unicode 🚀", "2026-01-02T00:00:00.000Z"),
    ];
    const json = exportDocument(source, "2026-01-03T00:00:00.000Z");
    const preview = importPreview(json, [], "reemplazar");
    expect(preview.issues).toEqual([]);
    expect(applyImport(preview, [])).toEqual(sortIdeas(source));
  });
  it("previews without mutation and supports cancel, combine and replace", () => {
    const local = [idea("a"), idea("old")];
    const incoming = { ...idea("a", "Updated"), id: "a" };
    const json = JSON.stringify({
      schemaVersion: "1.0",
      exportedAt: "2026-01-03T00:00:00.000Z",
      ideas: [incoming, idea("new")],
    });
    const preview = importPreview(json, local, "combinar");
    expect(local[0].titulo).toBe("Idea a");
    expect(preview.conflicts).toEqual(["a"]);
    expect(applyImport(preview, local)).toHaveLength(3);
    expect(
      applyImport(
        {
          ...preview,
          issues: [
            { code: "OperationCancelled", path: "$", message: "cancel" },
          ],
        },
        local,
      ),
    ).toEqual(local);
    expect(importPreview(json, local, "reemplazar").resultCount).toBe(2);
  });
  it("rejects a file above 5 MiB before parsing and accepts the exact boundary hint", () => {
    const json = exportDocument([], "2026-01-01T00:00:00.000Z");
    expect(
      importPreview(json, [], "reemplazar", LIMITS.inputBytes).issues,
    ).toHaveLength(0);
    expect(
      importPreview(json, [], "reemplazar", LIMITS.inputBytes + 1).limit,
    ).toBe("inputBytes");
  });
  it("rejects Combinar cuando 3 MiB locales más 3 MiB entrantes superan 4 MiB", () => {
    const build = (prefix: string) =>
      Array.from({ length: 1500 }, (_, index) => ({
        ...idea(`${prefix}-${index}`),
        notas: "x".repeat(1800),
      }));
    const local = build("local");
    const incoming = build("incoming");
    const preview = importPreview(exportDocument(incoming), local, "combinar");
    expect(preview.limit).toBe("collectionBytes");
    expect(applyImport(preview, local)).toEqual(local);
  });
  it("accepts 10,000 compact ideas and rejects 10,001", () => {
    const tenThousand = Array.from({ length: 10000 }, (_, index) => ({
      ...idea(`count-${index}`),
      notas: "",
    }));
    expect(
      importPreview(exportDocument(tenThousand), [], "reemplazar").issues,
    ).toHaveLength(0);
    const elevenThousand = [
      ...tenThousand,
      { ...tenThousand[0], id: "count-10000" },
    ];
    expect(
      importPreview(exportDocument(elevenThousand), [], "reemplazar").limit,
    ).toBe("ideaCount");
  });
  it("accepts a collection exactly at the 4 MiB normalized boundary", () => {
    const bytes = (items: Idea[]) =>
      new TextEncoder().encode(
        JSON.stringify({
          schemaVersion: "1.0",
          exportedAt: "2026-01-01T00:00:00.000Z",
          ideas: items,
        }),
      ).byteLength;
    const base: Idea = { ...idea("boundary"), notas: "" };
    const baseBytes = bytes([base]);
    const exact = [
      { ...base, notas: "x".repeat(LIMITS.collectionBytes - baseBytes) },
    ];
    expect(bytes(exact!)).toBe(LIMITS.collectionBytes);
    expect(
      importPreview(exportDocument(exact!), [], "reemplazar").issues,
    ).toHaveLength(0);
    expect(
      importPreview(
        exportDocument([
          ...exact!.slice(0, -1),
          { ...exact!.at(-1)!, notas: `${exact!.at(-1)!.notas}x` },
        ]),
        [],
        "reemplazar",
      ).limit,
    ).toBe("collectionBytes");
  });
  it("reports UTF-8 bytes and rejects a normalized collection over 4 MiB", () => {
    const unicode = idea("u", "🚀".repeat(100));
    const json = exportDocument([unicode]);
    expect(new TextEncoder().encode(json).byteLength).toBeGreaterThan(
      json.length,
    );
    const oversized: Idea = { ...idea("large"), notas: "x".repeat(2000) };
    const many = Array.from({ length: 2300 }, (_, i) => ({
      ...oversized,
      id: `large-${i}`,
    }));
    const preview = importPreview(exportDocument(many), [], "reemplazar");
    expect(preview.limit).toBe("collectionBytes");
  });
});
