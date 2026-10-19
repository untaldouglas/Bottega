import { describe, expect, it } from "vitest";
import { createIdea } from "../src/domain";
import { MemoryRepository } from "../src/repository";

describe("repository capacity invariant", () => {
  it("rejects create, edit and restore candidates crossing capacity atomically", async () => {
    const repo = new MemoryRepository();
    const seed = createIdea(
      {
        titulo: "seed",
        descripcion: "synthetic",
        impacto: 1,
        confianza: 1,
        facilidad: 1,
      },
      { id: () => "seed", now: () => "2026-01-01T00:00:00.000Z" },
    );
    expect((await repo.commit([seed])).ok).toBe(true);
    const oversized = { ...seed, notas: "x".repeat(4 * 1024 * 1024) };
    for (const candidate of [
      [oversized],
      [seed, oversized],
      [oversized, seed],
    ]) {
      expect((await repo.commit(candidate)).ok).toBe(false);
      expect((await repo.load()).value).toEqual([seed]);
    }
  });

  it("preserves the snapshot when storage reports a failure", async () => {
    const repo = new MemoryRepository();
    const seed = createIdea(
      {
        titulo: "seed",
        descripcion: "synthetic",
        impacto: 1,
        confianza: 1,
        facilidad: 1,
      },
      { id: () => "seed", now: () => "2026-01-01T00:00:00.000Z" },
    );
    await repo.commit([seed]);
    repo.failNext = true;
    repo.failNextCode = "QUOTA_EXCEEDED";
    expect((await repo.commit([])).ok).toBe(false);
    expect((await repo.load()).value).toEqual([seed]);
  });

  it("rejects an oversized commit before changing the snapshot", async () => {
    const repo = new MemoryRepository();
    const seed = createIdea(
      { titulo: "a", descripcion: "b", impacto: 1, confianza: 1, facilidad: 1 },
      { id: () => "seed", now: () => "2026-01-01T00:00:00.000Z" },
    );
    expect((await repo.commit([seed])).ok).toBe(true);
    const oversized = Array.from({ length: 10001 }, (_, index) => ({
      ...seed,
      id: `idea-${index}`,
    }));
    const result = await repo.commit(oversized);
    expect(result.ok).toBe(false);
    expect((await repo.load()).value).toEqual([seed]);
  });
});
