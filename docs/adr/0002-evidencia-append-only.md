# ADR-0002: Eventos y evidencia append-only

- Estado: ACEPTADO COMO DIRECCIÓN DEL CONTRATO; no autoriza implementación
- Fecha: 2026-10-26
- Decisor: Douglas
- Alcance: expediente, eventos y evidencia de Bottega 2.0

## Contexto
La reanudación, auditoría y trazabilidad requieren conservar el historial y distinguir correcciones de ediciones silenciosas.

## Decisión propuesta
Usar eventos, manifiestos y referencias de evidencia append-only, con hash canónico, snapshots derivados y un número de intento nuevo para cada corrección. Un mismatch o hash ausente bloquea.

## Consecuencias
Aumenta almacenamiento y disciplina de serialización, pero permite reconstrucción, detección de alteraciones y reanudación verificable. La retención queda NO DETERMINABLE hasta resolver P6.

## Evidencia y revisión
RF-011/014, RNF-004/008, CA-010/017; revisión independiente y decisión humana requeridas.
