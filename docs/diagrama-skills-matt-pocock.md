# Diagrama — Skills de Matt Pocock por rol en Bottega

Estado al cierre del método v1 (pos-retrospectiva desacoplada). Derivado de `GUIA-DE-USO.md`; si cambia la tabla de roles, actualizar también este diagrama.

## 1. Flujo con roles, skills y gates

```text
                             NECESIDAD
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ ANDREA DEL VERROCCHIO · Requisitos y FRD                     │  → GATE 1 (usted)
 │   grilling · grill-with-docs · domain-modeling · to-spec     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ LEONARDO DA VINCI · Alternativas y plan de solución          │  → GATE 2 (usted)
 │   wayfinder · research · to-spec · to-tickets · codebase-design│
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ DONATELLO · UX y diseño de producto                          │  → UX GATE (usted)
 │   [no-Matt] discovery · flujos · arquitectura de info        │
 │   [no-Matt] prototipos · accesibilidad · pruebas de usabilidad│
 │   [Matt] handoff                                             │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ FILIPPO BRUNELLESCHI · Arquitectura técnica                  │  → GATE 3 (usted)
 │   codebase-design · domain-modeling                          │
 │   improve-codebase-architecture · prototype                  │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ MICHELANGELO BUONARROTI · Implementación y TDD               │  → GATE 4 (evidencia)
 │   implement · implement-spec · tdd                           │
 │   diagnosing-bugs · pr  →  REVIEW-PACKET.md                  │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ RAFFAELLO SANZIO · Revisión independiente                    │  → PASS / NEEDS_WORK / BLOCKED
 │   code-review · triage · handoff · wait-what                 │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                    CIERRE HUMANO (ADOPTAR / ADAPTAR / DETENER)
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ RETROSPECTIVA · persona autorizada (no un Bot)               │  → backlog de mejoras
 │   retro (+ writing-for-agents)                               │
 └─────────────────────────────────────────────────────────────┘
```

## 2. Asignación consolidada

**Leyenda:** `U` = invocada por el usuario (explícita) · `M` = invocada por el modelo (el agente la alcanza solo).

| Rol (Bot) | Responsabilidad | Skills de Matt Pocock | Tipo |
|---|---|---|---|
| Andrea del Verrocchio | Requisitos y FRD | `grilling`, `grill-with-docs`, `domain-modeling`, `to-spec` | M, U, M, U |
| Leonardo da Vinci | Alternativas y plan de solución | `wayfinder`, `research`, `to-spec`, `to-tickets`, `codebase-design` | U, M, U, U, M |
| Donatello | UX y diseño de producto | `handoff` *(el resto son skills UX no-Matt)* | U |
| Filippo Brunelleschi | Arquitectura técnica | `codebase-design`, `domain-modeling`, `improve-codebase-architecture`, `prototype` | M, M, U, M |
| Michelangelo Buonarroti | Implementación y TDD | `implement`, `implement-spec`, `tdd`, `diagnosing-bugs`, `pr` | U, U, M, M, M |
| Raffaello Sanzio | Revisión independiente | `code-review`, `triage`, `handoff`, `wait-what` | M, U, U, U |
| — (persona autorizada: Director / ingeniero / operador) | Retrospectiva (post-cierre, no un Bot autónomo) | `retro` | U |

## 3. Capas transversales (no asignadas a un Bot)

```text
grilling          ── primitiva de entrevista que sostiene grill-with-docs,
                     grill-me, triage, wayfinder e improve-codebase-architecture
domain-modeling   ── mantiene GLOSSARY.md (lenguaje del dominio) en toda etapa
writing-for-agents── la usa retro para redactar mejoras; aplica a skills y AGENTS.md
setup-matt-pocock-skills ── config única por repo (tracker, labels, layout) antes de operar
ask-matt          ── router opcional: sugiere qué skill usar según la situación
```

## 4. Observaciones

1. `retro` ya no está en Raffaello: quedó en una etapa propia, fuera del gate, posterior al cierre humano. La ejecuta una persona autorizada (Director, ingeniero u operador), nunca un Bot de forma autónoma, y no se auto-aplica.
2. `pr` alimenta el `REVIEW-PACKET.md` en Michelangelo; no es solo el cuerpo de una PR en GitHub.
3. Donatello es el único rol híbrido: combina skills UX propias (no-Matt) con una sola skill Matt (`handoff`).
4. `codebase-design` y `domain-modeling` se repiten en Leonardo y Filippo: son el vocabulario compartido de diseño profundo y de dominio.
