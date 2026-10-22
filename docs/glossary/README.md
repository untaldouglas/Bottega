# Glosario enlazable

Registro canónico: [`terms.yaml`](terms.yaml). Las anclas HTML son estables.

## Índice

### B

- [Backlog](entries/backlog.md#glossary-backlog) — operación (active)
- [Baseline](entries/baseline.md#glossary-baseline) — gobernanza (active)
### C

- [Criterio de aceptación](entries/acceptance-criteria.md#glossary-acceptance-criteria) — proceso (active)
### D

- [Definition of Done](entries/definition-of-done.md#glossary-definition-of-done) — proceso (active)
### E

- [Evidencia](entries/evidence.md#glossary-evidence) — gobernanza (active)
### G

- [Gate](entries/gate.md#glossary-gate) — gobernanza (active)
### K

- [Kanban](entries/kanban.md#glossary-kanban) — operación (active)
### M

- [Migración](entries/migration.md#glossary-migration) — proceso (active)
### P

- [Propietario](entries/owner.md#glossary-owner) — gobernanza (active)
### R

- [Release](entries/release.md#glossary-release) — producto (active)
- [Revisión](entries/review.md#glossary-review) — proceso (active)
- [Rollout](entries/rollout.md#glossary-rollout) — operación (active)
### S

- [Skill](entries/skill.md#glossary-skill) — técnico (active)

## Tabla de términos

| Término | Categoría | Estado |
| --- | --- | --- |
| [Backlog](entries/backlog.md#glossary-backlog) | operación | active |
| [Baseline](entries/baseline.md#glossary-baseline) | gobernanza | active |
| [Criterio de aceptación](entries/acceptance-criteria.md#glossary-acceptance-criteria) | proceso | active |
| [Definition of Done](entries/definition-of-done.md#glossary-definition-of-done) | proceso | active |
| [Evidencia](entries/evidence.md#glossary-evidence) | gobernanza | active |
| [Gate](entries/gate.md#glossary-gate) | gobernanza | active |
| [Kanban](entries/kanban.md#glossary-kanban) | operación | active |
| [Migración](entries/migration.md#glossary-migration) | proceso | active |
| [Propietario](entries/owner.md#glossary-owner) | gobernanza | active |
| [Release](entries/release.md#glossary-release) | producto | active |
| [Revisión](entries/review.md#glossary-review) | proceso | active |
| [Rollout](entries/rollout.md#glossary-rollout) | operación | active |
| [Skill](entries/skill.md#glossary-skill) | técnico | active |

## Esquema y uso

`terms.yaml` es la fuente canónica (JSON válido como YAML 1.2). Cada término requiere `id`, `label`, `aliases`, `acronym`, `anchor`, `category`, `definition`, `context`, `source`, `related`, `owner`, `status`, `reviewed_on`, `review_due`, `introduced_in` y `deprecated_by`. IDs y anclas son estables; `owner` siempre es un rol o equipo.

Enlaza solo la primera aparición significativa por documento o sección autónoma. No enlaces encabezados, tablas ni bloques de código. Ejecuta `make glossary-check`, `make docs-check` y `python scripts/glossary.py render --check` antes de abrir una PR.

El archivo `GLOSSARY.md` de la raíz es un glosario legible por agentes generado desde este mismo registro; edita `terms.yaml` y ejecuta `make docs`, no edites `GLOSSARY.md` a mano.

