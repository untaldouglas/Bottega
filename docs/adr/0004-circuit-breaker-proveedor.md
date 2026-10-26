# ADR-0004: Circuit breaker y registro de proveedor efectivo

- Estado: ACEPTADO COMO DIRECCIÓN DEL CONTRATO; no autoriza implementación
- Fecha: 2026-10-26
- Decisor: Douglas
- Alcance: ejecución futura de proveedores/modelos

## Contexto
Los retries y fallbacks pueden ocultar fallas, costo o cambio de proveedor. El contrato exige detener el primer HTTP 429.

## Decisión propuesta
El primer 429 abre el circuito y detiene el intento. Sólo una política explícita con `fallback_allowed: true`, proveedor/capacidad declarados y autorización vigente puede recuperar. Cada intento registra proveedor y modelo efectivos sin secretos, con contadores separados.

## Consecuencias
Puede reducir disponibilidad inmediata, pero conserva trazabilidad, control de costo y capacidad de auditoría. No se ejecuta en I0.

## Evidencia y revisión
RF-012/013, RNF-002/004, CA-009/011; revisión independiente y decisión humana requeridas.
