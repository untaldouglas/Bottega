# ADR-0001: Core neutral y puertos/adaptadores

- Estado: ACEPTADO COMO DIRECCIÓN DEL CONTRATO; no autoriza implementación
- Fecha: 2026-10-26
- Decisor: Douglas
- Alcance: Bottega 2.0

## Contexto
Bottega debe conservar reglas de dominio independientes de Frappe, proveedores, UI y persistencia concreta. Frappe v16 es un Golden Path separado y `v16.53.0` sólo un baseline candidato.

## Decisión propuesta
Mantener el core neutral y expresar integraciones mediante puertos y adaptadores. La selección de runtime, proveedor, identidad, persistencia y despliegue queda diferida a un spike autorizado posterior.

## Consecuencias
Aumenta el trabajo de contratos iniciales, pero permite validar el core sin Frappe, sustituir proveedores y reducir lock-in. No autoriza implementación ni instalación.

## Evidencia y revisión
RF-016/017, RNF-007, CA-013/014; revisión independiente y decisión humana requeridas.
