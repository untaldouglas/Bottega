# Bottega

Método gobernado de desarrollo de software asistido por IA.

Bottega convierte una necesidad de software en un producto terminado, probado, documentado y listo para compartirse, mediante un grupo de Bots especializados que trabajan por etapas bajo aprobación humana y con evidencia verificable en cada paso.

No automatiza decisiones: las personas definen el alcance, aprueban cada puerta y deciden el resultado final.

## Primeros pasos

```bash
make bootstrap   # valida el entorno e imprime el checklist de instalación
make doctor      # confirma que Bottega quedó listo (solo lectura)
```

La guía completa de cero a proficiente está en `docs/ONBOARDING.md`.

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

- `docs/ONBOARDING.md` — rampa de cero a proficiente.
- `GUIA-DE-USO.md` — guía canónica de operación.
- `GLOSSARY.md` — glosario legible por agentes (fuente: `docs/glossary/terms.yaml`).
- `docs/diagrama-skills-matt-pocock.md` — mapa de skills por rol.
- `kit/` — kit de orquestación (preflight, init, gate_check).
- `scripts/` y `Makefile` — controles de documentación, CI, doctor y bootstrap.
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

- Onboarding: `docs/ONBOARDING.md`.
- Técnica y operativa: `GUIA-DE-USO.md`, `docs/`, `kit/`.
- Glosario: `GLOSSARY.md`.
- Mercadológica: `comunicacion/`.
- Del ejemplo: `app01/docs/`.

## Estado

Repositorio público. Publicar productos derivados y la adopción institucional del método requieren autorización explícita por separado.
