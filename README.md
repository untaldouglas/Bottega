# Bottega

Método gobernado de desarrollo de software asistido por IA.

Bottega convierte una necesidad de software en un producto terminado, probado, documentado y listo para compartirse, mediante un grupo de Bots especializados que trabajan por etapas bajo aprobación humana y con evidencia verificable en cada paso.

No automatiza decisiones: las personas definen el alcance, aprueban cada puerta y deciden el resultado final.

## Roles

| Bot | Función |
|---|---|
| Andrea del Verrocchio | requisitos y criterios de aceptación |
| Leonardo da Vinci | alternativas y plan de solución |
| Donatello | experiencia de usuario y diseño |
| Filippo Brunelleschi | arquitectura y estrategia de pruebas |
| Michelangelo Buonarroti | implementación y pruebas (TDD) |
| Raffaello Sanzio | revisión independiente |

Un rol por etapa. Quien implementa no se revisa a sí mismo.

## Flujo

```text
Necesidad → requisitos → solución → UX → arquitectura → implementación (TDD) → fidelidad UX → revisión independiente → decisión humana
```

Cada etapa termina en un gate que solo una persona autoriza. La implementación se autoriza únicamente después de aprobar requisitos, solución, UX y arquitectura.

## Estructura del repositorio

- `GUIA-DE-USO.md` — guía canónica de operación.
- `kit/` — kit de orquestación (preflight, init, gate_check).
- `docs/glossary/` — glosario técnico.
- `scripts/` y `Makefile` — controles de documentación y CI.
- `comunicacion/` — documentación mercadológica.
- `app01/` — ejemplo probado (Idea Prioritizer).

## app01 — ejemplo probado

`app01/` es **Idea Prioritizer**, una aplicación local para registrar ideas y priorizarlas mediante la fórmula `Impacto × Confianza × Facilidad`, con datos sintéticos, persistencia local y exportación/importación JSON.

Construir y ejecutar localmente:

```bash
cd app01
npm ci
npm run build
npm run preview
```

Validación completa (lint, typecheck, pruebas unitarias y E2E, build, seguridad y licencias):

```bash
cd app01
npm run validate
```

## Documentación

- Técnica y operativa: `GUIA-DE-USO.md`, `docs/`, `kit/`.
- Mercadológica: `comunicacion/`.
- Del ejemplo: `app01/docs/`.

## Estado

Repositorio privado. La publicación pública y la adopción institucional requieren autorización explícita por separado.
