# ADR-0001: Stack tecnológico

- **Estado:** Propuesto; requiere decisión de GATE 3
- **Fecha:** 2026-10-13
- **Contexto:** PRODUCTO-001 necesita una aplicación local pequeña, accesible, reproducible, sin servidor, autenticación ni red. El dominio debe poder probarse sin navegador.

## Decisión

Usar **TypeScript + Vite sin framework de UI**. Vite se limita al desarrollo/empaquetado estático; TypeScript expresa contratos y evita clases de errores en dominio, intercambio y aplicación. La UI usará DOM semántico y módulos de presentación pequeños. IndexedDB se trata en ADR-0002.

### Alternativa descartada: TypeScript + React + Vite

React + Vite es técnicamente viable, pero introduce runtime, JSX, modelo de componentes y dependencias adicionales para una pantalla/flujo acotado. No aporta una capacidad requerida que justifique ese coste. Se mantiene como opción reversible: una futura capa React puede consumir los mismos casos de uso, estado y puertos.

### Alternativas también descartadas

- JavaScript sin tipado: menor barrera inicial, mayor riesgo en contratos JSON y mutaciones atómicas.
- Framework full-stack o SSR: contradice cero servidor y añade superficie innecesaria.
- Solución open source adaptada: no hay evidencia de que cumpla exactamente dominio, privacidad, licencia y persistencia.

## Consecuencias

**Positivas:** menor complejidad, runtime mínimo, dependencia de ejecución nula, control directo de foco/accesibilidad, dominio portable y migración futura posible.

**Negativas:** se debe disciplinar la composición de UI, implementar estados/foco sin una librería de componentes y construir una estrategia clara para listas grandes. TypeScript no sustituye validación de datos externos.

## Límites

No se permite que la UI reimplemente reglas de dominio. La aplicación no importa APIs del navegador salvo puertos. Los datos importados siempre se validan en runtime. El uso de librerías de UI requiere ADR o justificación documentada por accesibilidad y tamaño.

## Verificación

La selección se valida con pruebas unitarias sin navegador, pruebas DOM/componentes, E2E en navegadores objetivo, auditoría de dependencias/licencias y prueba de red bloqueada. GATE 3 debe aceptar explícitamente los trade-offs antes de implementar.
