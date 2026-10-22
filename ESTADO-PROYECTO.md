# Estado del proyecto — Bottega

**Última actualización:** 2026-10-22 (CST, UTC-06:00)

## Resumen ejecutivo

Bottega es un método gobernado de desarrollo de software asistido por IA: seis Bots especializados trabajan por etapas, bajo aprobación humana en cada gate y con evidencia verificable. Al cierre de esta sesión quedó **consolidado como método usable de cero a proficiente**, con la confianza del TDD endurecida contra falsos RED/GREEN.

## Estado consolidado (2026-10-22)

- **Onboarding e instalación** — `make doctor` (valida herramientas, plugin y seis perfiles), `make bootstrap` (checklist de cero a listo) y `docs/ONBOARDING.md`.
- **Glosario legible por agentes** — `GLOSSARY.md` generado desde `docs/glossary/terms.yaml` (fuente única, sin drift).
- **Paquete de revisión** — `kit/templates/REVIEW-PACKET.md` (Summary → Evidence → Merge Danger), obligatorio antes de validación.
- **Retrospectiva desacoplada** — `retro` salió de Raffaello; es etapa posterior al cierre, ejecutada por una persona autorizada, nunca un Bot autónomo.
- **Contrato TDD negativo** — `kit/templates/TEST-SEAMS.yaml`: cada seam declara qué detecta y qué no; sin `misses` no hay evidencia de GATE 4.
- **Diagrama de skills** — `docs/diagrama-skills-matt-pocock.md` (mapa de skills de Matt Pocock por rol).
- **Plugin Matt Pocock** — actualizado a `5beb35b` (v1.3.1), respaldado y con rollback disponible.

## Backlog diferido (con justificación)

| Mejora | Motivo del diferimiento |
|---|---|
| Grafo/frontera (`implement-spec`, ejecución paralela) | Optimización de velocidad, no corrección; prematura sin un spec grande con tickets independientes. |
| Contrato de compatibilidad de skills | Robustez defensiva ante cambios futuros de upstream; baja frecuencia; `make doctor` ya cubre "plugin instalado". |

## Gobernanza

- **Repositorio público:** `untaldouglas/Bottega`. Publicar productos derivados y la adopción institucional del método requieren autorización explícita por separado.
- **Retrospectiva:** la ejecuta una persona autorizada (Director, ingeniero u operador); aceptar/posponer/rechazar es decisión humana y no se auto-aplica.
- **Seis perfiles canónicos:** `andrea-verrocchio`, `leonardo-da-vinci`, `donatello-ux`, `filippo-brunelleschi`, `michelangelo-buonarroti`, `raffaello-sanzio`.

## Decisiones abiertas

- Ninguna bloqueante. La próxima iniciativa (PRODUCTO-002) debe pasar por el piloto comparativo (Caso A / Caso B) documentado en el paquete `bottega-di-douglas`, no generalizar desde PRODUCTO-001.

## Siguiente acción recomendada

Ejecutar el piloto comparativo de PRODUCTO-002 usando el kit completo (brief → gates → TDD con seams → review packet → validación → retrospectiva), antes de decidir ADOPTAR / ADAPTAR / DETENER.
