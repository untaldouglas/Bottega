# Changelog

## Hallmark v2 — unreleased

- Implementada la superficie visual Hallmark con tokens, copy neutral, estados accesibles, foco, diálogo de eliminación, live region, reduced motion y responsive.
- Se conserva `CollectionRepository` público con `Idea[]`; exportación siempre incluye `exportedAt`, importación 1.0 lo acepta opcionalmente si es válido; `normalizedBytes` es derivado y no persistido.
- Añadido `hallmark:check` para allowlist/read-back de fuente, dist y runtime.
- No se añade LLM, provider, fallback, red, integración, publicación ni claim de aceptación/mercado.

## 1.0.0

- Aplicación local de priorización con estados, cálculo y orden determinista.
- IndexedDB, exportación/importación atómica y límites 5 MiB/4 MiB/10.000.
- Pruebas unitarias y E2E, Docker, CI y documentación open source.
