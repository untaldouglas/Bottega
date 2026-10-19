import { describe, expect, it } from "vitest";
import {
  createIdea,
  sortIdeas,
  updateIdea,
  validateIdea,
  validateCollectionCapacity,
  type Idea,
} from "../src/domain";

describe("domain", () => {
  it("creates a draft with calculated priority", () => {
    const idea = createIdea(
      {
        titulo: "Sintética",
        descripcion: "Descripción sintética",
        impacto: 8,
        confianza: 5,
        facilidad: 6,
      },
      { id: () => "idea-1", now: () => "2026-01-01T00:00:00.000Z" },
    );
    expect(idea).toMatchObject({
      id: "idea-1",
      estado: "borrador",
      prioridad: 240,
      creadaEn: idea.modificadaEn,
    });
  });
  it("rejects invalid boundaries and duplicate tags", () => {
    const result = validateIdea({
      id: "x",
      titulo: "a".repeat(121),
      descripcion: "ok",
      estado: "borrador",
      impacto: 0,
      confianza: 1,
      facilidad: 1,
      prioridad: 0,
      creadaEn: "bad",
      modificadaEn: "bad",
      etiquetas: ["x", "x"],
      notas: "",
    });
    expect(result.ok).toBe(false);
    if (!result.ok)
      expect(result.issues.map((issue) => issue.code)).toEqual(
        expect.arrayContaining([
          "TITLE_TOO_LONG",
          "SCORE_OUT_OF_RANGE",
          "DUPLICATE_TAG",
          "INVALID_DATE",
        ]),
      );
  });
  it("sorts by priority, modification date, then title", () => {
    const base = {
      id: "1",
      descripcion: "d",
      estado: "borrador" as const,
      impacto: 1 as const,
      confianza: 1 as const,
      facilidad: 1 as const,
      prioridad: 10,
      creadaEn: "2026-01-01T00:00:00.000Z",
      modificadaEn: "2026-01-01T00:00:00.000Z",
      etiquetas: [],
      notas: "",
    };
    const ideas: Idea[] = [
      { ...base, id: "a", titulo: "Zeta" },
      { ...base, id: "b", titulo: "Alfa" },
      {
        ...base,
        id: "c",
        titulo: "Alta",
        modificadaEn: "2026-01-02T00:00:00.000Z",
      },
    ];
    expect(sortIdeas(ideas).map((i) => i.id)).toEqual(["c", "b", "a"]);
  });
  it("recalculates priority on update without touching identity", () => {
    const idea = createIdea(
      { titulo: "a", descripcion: "b", impacto: 1, confianza: 1, facilidad: 1 },
      { id: () => "id-1", now: () => "2026-01-01T00:00:00.000Z" },
    );
    const updated = updateIdea(
      idea,
      {
        titulo: "a",
        descripcion: "b",
        impacto: 8,
        confianza: 5,
        facilidad: 6,
        etiquetas: [],
        notas: "",
      },
      "2026-01-02T00:00:00.000Z",
    );
    expect(updated).toMatchObject({
      id: "id-1",
      estado: "borrador",
      creadaEn: "2026-01-01T00:00:00.000Z",
      prioridad: 240,
      modificadaEn: "2026-01-02T00:00:00.000Z",
    });
    expect(validateIdea(updated).ok).toBe(true);
  });
  it("rejects collection mutations over the hard idea limit", () => {
    const base = createIdea(
      { titulo: "a", descripcion: "b", impacto: 1, confianza: 1, facilidad: 1 },
      { id: () => "seed", now: () => "2026-01-01T00:00:00.000Z" },
    );
    const result = validateCollectionCapacity(
      Array.from({ length: 10001 }, (_, index) => ({
        ...base,
        id: `idea-${index}`,
      })),
    );
    expect(result.ok).toBe(false);
    if (!result.ok)
      expect(result.issues.map((item) => item.code)).toContain(
        "CAPACITY_EXCEEDED",
      );
  });
});
