# ADR-0005: Política de patch calificado para Frappe v16

- Estado: PROPUESTA PARA REVISIÓN; no aprobada en I0
- Fecha: 2026-10-26
- Decisor: Douglas
- Alcance: perfil Golden Path Frappe v16; no Producto 02

## Contexto

Declarar `v16.53.0` como baseline candidato no basta para reproducir o recuperar una actualización. Un patch puede cambiar dependencias, licencias, advisories, SBOM, procedencia o capacidad de rollback aunque conserve la misma línea mayor.

## Decisión propuesta

Adoptar `docs/product/BOTTEGA-2-FRAPPE-PATCH-POLICY.md` como contrato verificable. La selección parte de fuentes oficiales y registra la tupla completa de framework, Bench, Python, Node.js, MariaDB, Redis/Valkey, Yarn y OS, además de tag, commit y digest. Ningún candidato pasa sin licencias, advisories, SBOM, procedencia, aceptación humana, backup restaurado, rollback probado y comparación con patches posteriores.

`latest` y referencias mutables no son pins. `v16.53.0` permanece `candidate` hasta completar I3; I0 no instala Frappe ni afirma compatibilidad.

## Consecuencias

El expediente y la validación requieren más evidencia, pero permiten reproducibilidad, auditoría y recuperación. Cada cambio de tupla crea un candidato nuevo y conserva el anterior como rollback target. La aceptación sigue siendo humana y separada de un PASS técnico.

## Evidencia y revisión

RF-017/021, RNF-002/003/004/005/006/012, CA-014/021; `make docs-check`; revisión independiente y decisión humana requeridas.