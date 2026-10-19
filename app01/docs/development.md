# Desarrollo

Arquitectura: dominio independiente, intercambio JSON, aplicación DOM y puerto `CollectionRepository`; IndexedDB es el adaptador real y memoria el fake de pruebas.

Instala con `npm ci`. Ejecuta `npm run validate` antes de contribuir. No hay red en runtime. `style.css` se entrega como recurso self enlazado desde HTML (no se usa `unsafe-inline`); `prefers-reduced-motion` fuerza scroll instantáneo. Los fixtures y ejemplos deben ser sintéticos.

## Hallmark v2

La UI usa los tokens Hallmark y mantiene el dominio/puerto `CollectionRepository` existentes. Ejecuta `npm run hallmark:check` después de `npm run build` para verificar allowlist y read-back del runtime. El desarrollo usa TDD RED → GREEN → REFACTOR y solo fixtures sintéticos.
