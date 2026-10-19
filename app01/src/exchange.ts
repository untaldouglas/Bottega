import { validateCollection, type Idea, type Issue, sortIdeas } from "./domain";
export const LIMITS = {
  inputBytes: 5 * 1024 * 1024,
  collectionBytes: 4 * 1024 * 1024,
  ideaCount: 10000,
} as const;
export type ImportMode = "combinar" | "reemplazar";
export type Preview = {
  mode: ImportMode;
  incomingCount: number;
  resultCount: number;
  conflicts: string[];
  issues: Issue[];
  normalizedBytes: number;
  limit?: keyof typeof LIMITS;
  proposed: Idea[];
};
const issue = (
  code: string,
  path: string,
  message: string,
  limit?: string,
): Issue => ({ code, path, message, ...(limit ? { limit } : {}) });
export const compact = (v: unknown) => JSON.stringify(v);
export function exportDocument(
  ideas: readonly Idea[],
  exportedAt = new Date().toISOString(),
): string {
  return compact({ schemaVersion: "1.0", exportedAt, ideas: sortIdeas(ideas) });
}
function capacity(ideas: Idea[]): {
  bytes: number;
  limit?: keyof typeof LIMITS;
  issues: Issue[];
} {
  const bytes = new TextEncoder().encode(
    compact({
      schemaVersion: "1.0",
      exportedAt: "1970-01-01T00:00:00.000Z",
      ideas,
    }),
  ).byteLength;
  const issues: Issue[] = [];
  let limit: keyof typeof LIMITS | undefined;
  if (bytes > LIMITS.collectionBytes) {
    limit = "collectionBytes";
    issues.push(
      issue(
        "CAPACITY_EXCEEDED",
        "$",
        `La colección supera ${LIMITS.collectionBytes} bytes compactos`,
        String(LIMITS.collectionBytes),
      ),
    );
  }
  if (ideas.length > LIMITS.ideaCount) {
    limit ??= "ideaCount";
    issues.push(
      issue(
        "CAPACITY_EXCEEDED",
        "ideas",
        `La colección supera ${LIMITS.ideaCount} ideas`,
        String(LIMITS.ideaCount),
      ),
    );
  }
  return { bytes, limit, issues };
}
export function importPreview(
  text: string,
  local: readonly Idea[],
  mode: ImportMode,
  inputBytes?: number,
): Preview {
  const base = {
    mode,
    incomingCount: 0,
    resultCount: local.length,
    conflicts: [],
    issues: [],
    normalizedBytes: 0,
    proposed: [...local],
  };
  const bytes = inputBytes ?? new TextEncoder().encode(text).byteLength;
  if (bytes > LIMITS.inputBytes)
    return {
      ...base,
      issues: [
        issue(
          "CAPACITY_EXCEEDED",
          "$",
          `El archivo supera ${LIMITS.inputBytes} bytes`,
          String(LIMITS.inputBytes),
        ),
      ],
      limit: "inputBytes",
    };
  let doc: unknown;
  try {
    doc = JSON.parse(text);
  } catch {
    return {
      ...base,
      issues: [
        issue("INVALID_JSON", "$", "El archivo no contiene JSON válido"),
      ],
    };
  }
  if (
    !doc ||
    typeof doc !== "object" ||
    (doc as { schemaVersion?: unknown }).schemaVersion !== "1.0" ||
    !Array.isArray((doc as { ideas?: unknown }).ideas)
  )
    return {
      ...base,
      issues: [
        issue(
          "UNSUPPORTED_SCHEMA",
          "$",
          "Se requiere schemaVersion 1.0 y una lista ideas",
        ),
      ],
    };
  const exportedAt = (doc as { exportedAt?: unknown }).exportedAt;
  if (
    exportedAt !== undefined &&
    (typeof exportedAt !== "string" || Number.isNaN(Date.parse(exportedAt)))
  )
    return {
      ...base,
      issues: [
        issue(
          "INVALID_EXPORTED_AT",
          "exportedAt",
          "exportedAt debe ser una fecha ISO válida",
        ),
      ],
    };
  const incoming = (doc as { ideas: unknown[] }).ideas;
  if (incoming.length > LIMITS.ideaCount)
    return {
      ...base,
      incomingCount: incoming.length,
      issues: [
        issue(
          "CAPACITY_EXCEEDED",
          "ideas",
          `La colección supera ${LIMITS.ideaCount} ideas`,
          String(LIMITS.ideaCount),
        ),
      ],
      limit: "ideaCount",
    };
  const validated = validateCollection(incoming);
  if (!validated.ok)
    return {
      ...base,
      incomingCount: incoming.length,
      issues: [...validated.issues],
    };
  const accepted: Idea[] = validated.value;
  const conflicts = accepted
    .filter((i) => local.some((l) => l.id === i.id))
    .map((i) => i.id);
  const proposed =
    mode === "reemplazar"
      ? accepted
      : sortIdeas([
          ...local.filter((l) => !conflicts.includes(l.id)),
          ...accepted,
        ]);
  const cap = capacity(proposed);
  return {
    ...base,
    incomingCount: validated.value.length,
    resultCount: proposed.length,
    conflicts,
    issues: cap.issues,
    normalizedBytes: cap.bytes,
    limit: cap.limit,
    proposed,
  };
}
export const applyImport = (
  preview: Preview,
  current: readonly Idea[],
): Idea[] => (preview.issues.length ? [...current] : [...preview.proposed]);
