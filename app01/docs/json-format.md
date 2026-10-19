# Formato JSON 1.0

El documento compacto contiene `schemaVersion: "1.0"`, `exportedAt` ISO-8601 e `ideas`. Cada idea conserva identidad, campos, prioridad calculada, fechas UTC, etiquetas sin duplicados y notas. Se rechazan versiones desconocidas, campos incompletos, IDs duplicados, prioridades inconsistentes y límites excedidos. La importación es validar → previsualizar → confirmar → transacción.

Ejemplo mínimo: `{ "schemaVersion":"1.0", "exportedAt":"2026-01-01T00:00:00.000Z", "ideas":[] }`. `exportedAt` siempre se emite al exportar; al importar schema 1.0 puede faltar por compatibilidad histórica, pero si aparece debe ser una fecha ISO-8601 válida. `normalizedBytes` es un cálculo de validación y no se persiste en cada idea.
