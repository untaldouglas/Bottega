# ADR-0003: Estados técnicos y decisiones humanas ortogonales

- Estado: ACEPTADO COMO DIRECCIÓN DEL CONTRATO; no autoriza implementación
- Fecha: 2026-10-26
- Decisor: Douglas
- Alcance: estados y autorización

## Contexto
Un PASS técnico, CI verde o PR abierto no es aceptación humana, autorización de release, publicación ni producción.

## Decisión propuesta
Separar ejecución, revisión técnica, PRODUCT_PASS, RELEASE_READY_CONDITIONAL y PUBLICATION_AUTHORIZED. Cada decisión humana exige actor, alcance, timestamp, razón, evidencia y autorización vigente. La política es fail-closed.

## Consecuencias
La interfaz y los checks tienen más estados explícitos, pero impiden autorización implícita y hacen auditable cada transición.

## Evidencia y revisión
RF-008/009/010/020, RNF-003/009, CA-007/008/020; revisión independiente y decisión humana requeridas.
