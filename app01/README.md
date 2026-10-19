# Idea Prioritizer

Aplicación local para capturar y ordenar ideas sintéticas. No hay servidor, cuentas, sincronización ni llamadas de red en runtime.

## Uso

```bash
npm ci
npm run dev
```

Crea ideas con título, descripción y criterios 1–10. La prioridad es impacto × confianza × facilidad. Exporta JSON como respaldo; importa con vista previa y modos Combinar/Reemplazar. IndexedDB conserva la última colección confirmada. Consulta `docs/user-guide.md`.

## Calidad

`npm run lint`, `npm run typecheck`, `npm test`, `npm run test:e2e`, `npm run build`, `npm run validate`.

## Límites

Archivo de entrada 5 MiB; colección JSON compacta 4 MiB; máximo preventivo 10.000 ideas. Consulta `docs/json-format.md` y `docs/privacy.md`.

## Hallmark v2

La superficie Hallmark conserva la colección local, la fórmula y los contratos públicos existentes. Incluye foco visible, navegación por teclado, región live, diálogo accesible de eliminación, reduced motion y responsive en 320/375/414/768/1440 px.

Para la comprobación de empaquetado ejecuta `npm run build && npm run hallmark:check`. No hay provider LLM, fallback, endpoint, cuenta ni integración externa.

## Contribuir

Lee `CONTRIBUTING.md`. Solo se aceptan datos sintéticos y cambios verificables. Licencia MIT.

Referencia: [Baseline](../docs/glossary/entries/baseline.md#glossary-baseline).
