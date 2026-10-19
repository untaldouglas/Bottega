export const STATES = [
  "borrador",
  "en evaluación",
  "aprobada",
  "rechazada",
  "implementada",
] as const;
export type Estado = (typeof STATES)[number];
export type Score = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
export type Idea = {
  readonly id: string;
  readonly titulo: string;
  readonly descripcion: string;
  readonly estado: Estado;
  readonly impacto: Score;
  readonly confianza: Score;
  readonly facilidad: Score;
  readonly prioridad: number;
  readonly creadaEn: string;
  readonly modificadaEn: string;
  readonly etiquetas: readonly string[];
  readonly notas: string;
};
export type Issue = {
  code: string;
  path: string;
  message: string;
  limit?: string;
};
export type Result<T> =
  { ok: true; value: T } | { ok: false; issues: readonly Issue[] };
export const priority = (i: number, c: number, f: number) => i * c * f;
export const COLLECTION_LIMITS = {
  collectionBytes: 4 * 1024 * 1024,
  ideaCount: 10000,
} as const;
const issue = (
  code: string,
  path: string,
  message: string,
  limit?: string,
): Issue => ({ code, path, message, ...(limit ? { limit } : {}) });
const isScore = (n: unknown): n is Score =>
  Number.isInteger(n) && Number(n) >= 1 && Number(n) <= 10;
const isDate = (v: unknown): v is string =>
  typeof v === "string" &&
  !Number.isNaN(Date.parse(v)) &&
  /^\d{4}-\d{2}-\d{2}T/.test(v);
export function validateIdea(value: unknown): Result<Idea> {
  const v = value as Partial<Idea>;
  const issues: Issue[] = [];
  if (!v || typeof v !== "object")
    return {
      ok: false,
      issues: [issue("INVALID_IDEA", "$", "La idea debe ser un objeto")],
    };
  if (typeof v.id !== "string" || !v.id.trim())
    issues.push(issue("INVALID_ID", "id", "El identificador es obligatorio"));
  if (typeof v.titulo !== "string" || !v.titulo.trim())
    issues.push(issue("TITLE_REQUIRED", "titulo", "El título es obligatorio"));
  else if (v.titulo.length > 120)
    issues.push(
      issue(
        "TITLE_TOO_LONG",
        "titulo",
        "El título supera 120 caracteres",
        "120",
      ),
    );
  if (typeof v.descripcion !== "string" || !v.descripcion.trim())
    issues.push(
      issue(
        "DESCRIPTION_REQUIRED",
        "descripcion",
        "La descripción es obligatoria",
      ),
    );
  else if (v.descripcion.length > 2000)
    issues.push(
      issue(
        "DESCRIPTION_TOO_LONG",
        "descripcion",
        "La descripción supera 2.000 caracteres",
        "2000",
      ),
    );
  if (!STATES.includes(v.estado as Estado))
    issues.push(issue("INVALID_STATE", "estado", "Estado no válido"));
  for (const key of ["impacto", "confianza", "facilidad"] as const)
    if (!isScore(v[key]))
      issues.push(
        issue(
          "SCORE_OUT_OF_RANGE",
          key,
          "Debe ser un entero entre 1 y 10",
          "1..10",
        ),
      );
  if (!isDate(v.creadaEn) || !isDate(v.modificadaEn))
    issues.push(
      issue("INVALID_DATE", "fechas", "Las fechas deben ser ISO válidas"),
    );
  if (
    !Array.isArray(v.etiquetas) ||
    v.etiquetas.some((t) => typeof t !== "string")
  )
    issues.push(
      issue("INVALID_TAGS", "etiquetas", "Las etiquetas deben ser texto"),
    );
  else if (
    new Set(v.etiquetas.map((t) => t.trim().toLocaleLowerCase())).size !==
    v.etiquetas.length
  )
    issues.push(
      issue(
        "DUPLICATE_TAG",
        "etiquetas",
        "No puede haber etiquetas duplicadas",
      ),
    );
  if (typeof v.notas !== "string")
    issues.push(issue("INVALID_NOTES", "notas", "Las notas deben ser texto"));
  if (
    isScore(v.impacto) &&
    isScore(v.confianza) &&
    isScore(v.facilidad) &&
    v.prioridad !== priority(v.impacto, v.confianza, v.facilidad)
  )
    issues.push(
      issue(
        "INCONSISTENT_PRIORITY",
        "prioridad",
        "La prioridad no coincide con los criterios",
      ),
    );
  return issues.length ? { ok: false, issues } : { ok: true, value: v as Idea };
}
export function createIdea(
  input: Pick<
    Idea,
    "titulo" | "descripcion" | "impacto" | "confianza" | "facilidad"
  > &
    Partial<Pick<Idea, "etiquetas" | "notas">>,
  deps: { id: () => string; now: () => string },
): Idea {
  const now = deps.now();
  return {
    id: deps.id(),
    titulo: input.titulo,
    descripcion: input.descripcion,
    estado: "borrador",
    impacto: input.impacto,
    confianza: input.confianza,
    facilidad: input.facilidad,
    prioridad: priority(input.impacto, input.confianza, input.facilidad),
    creadaEn: now,
    modificadaEn: now,
    etiquetas: input.etiquetas ?? [],
    notas: input.notas ?? "",
  };
}
export function updateIdea(
  idea: Idea,
  patch: Pick<
    Idea,
    | "titulo"
    | "descripcion"
    | "impacto"
    | "confianza"
    | "facilidad"
    | "etiquetas"
    | "notas"
  >,
  now: string,
): Idea {
  return {
    ...idea,
    titulo: patch.titulo,
    descripcion: patch.descripcion,
    impacto: patch.impacto,
    confianza: patch.confianza,
    facilidad: patch.facilidad,
    etiquetas: patch.etiquetas,
    notas: patch.notas,
    prioridad: priority(patch.impacto, patch.confianza, patch.facilidad),
    modificadaEn: now,
  };
}
export function sortIdeas(ideas: readonly Idea[]): Idea[] {
  return [...ideas].sort(
    (a, b) =>
      b.prioridad - a.prioridad ||
      b.modificadaEn.localeCompare(a.modificadaEn) ||
      a.titulo.localeCompare(b.titulo, "es") ||
      a.id.localeCompare(b.id),
  );
}
export function validateCollection(ideas: readonly unknown[]): Result<Idea[]> {
  const issues: Issue[] = [];
  const ids = new Set<string>();
  const validIdeas: Idea[] = [];
  for (let n = 0; n < ideas.length; n++) {
    const r = validateIdea(ideas[n]);
    if (!r.ok)
      issues.push(
        ...r.issues.map((i) => ({ ...i, path: `ideas[${n}].${i.path}` })),
      );
    else if (ids.has(r.value.id))
      issues.push(
        issue("DUPLICATE_ID", `ideas[${n}].id`, "Identificador duplicado"),
      );
    else {
      ids.add(r.value.id);
      validIdeas.push(r.value);
    }
  }
  return issues.length
    ? { ok: false, issues }
    : { ok: true, value: sortIdeas(validIdeas) };
}
export function validateCollectionCapacity(
  ideas: readonly unknown[],
): Result<Idea[]> {
  const valid = validateCollection(ideas);
  if (!valid.ok) return valid;
  const bytes = new TextEncoder().encode(
    JSON.stringify({ schemaVersion: "1.0", ideas: valid.value }),
  ).byteLength;
  const issues: Issue[] = [];
  if (bytes > COLLECTION_LIMITS.collectionBytes)
    issues.push(
      issue(
        "CAPACITY_EXCEEDED",
        "$",
        `La colección supera ${COLLECTION_LIMITS.collectionBytes} bytes compactos`,
        String(COLLECTION_LIMITS.collectionBytes),
      ),
    );
  if (valid.value.length > COLLECTION_LIMITS.ideaCount)
    issues.push(
      issue(
        "CAPACITY_EXCEEDED",
        "ideas",
        `La colección supera ${COLLECTION_LIMITS.ideaCount} ideas`,
        String(COLLECTION_LIMITS.ideaCount),
      ),
    );
  return issues.length ? { ok: false, issues } : valid;
}
