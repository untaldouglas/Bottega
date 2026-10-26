# Bottega — Onboarding (de cero a proficiente)

Esta guía te lleva de *"no sé qué es Bottega"* a *"corrí mi primer producto de principio a fin"*. No asume que conozcas Hermes ni los Bots.

## 1. Qué es Bottega

Bottega es un **método gobernado de desarrollo de software asistido por IA**. Convierte una necesidad en un producto terminado, probado, documentado y listo para compartirse, mediante **seis Bots especializados** que trabajan por etapas, bajo **aprobación humana en cada puerta (gate)** y con **evidencia verificable** en cada paso.

```text
Andrea del Verrocchio   → requisitos
Leonardo da Vinci       → solución
Donatello               → UX y diseño
Filippo Brunelleschi    → arquitectura
Michelangelo Buonarroti → implementación (TDD)
Raffaello Sanzio        → revisión independiente
```

Tú conduces. Los Bots ejecutan una especialidad por etapa y dejan evidencia. Nadie implementa sin tu aprobación previa de requisitos, solución, UX y arquitectura.

## 2. Prerrequisitos

| Qué | Para qué | Cómo verificarlo |
|---|---|---|
| **Hermes Agent** | orquestador de los Bots | `hermes --version` |
| **Una clave de proveedor LLM** | que los Bots razonen | configurada en Hermes (`hermes model`) |
| **git** | repositorios de producto | `git --version` |
| **python3** | kit de orquestación | `python3 --version` |
| *(opcional)* node/npm/docker | construir productos (ejemplo app01) | `make doctor` te lo dirá |

## 3. Instalación

```bash
git clone <url-del-repo-bottega>
cd Bottega
make bootstrap
```

`make bootstrap` valida tu entorno y te imprime un **checklist ordenado** con el comando exacto para cada pendiente. Los pasos clave que verás:

```text
1. Hermes Agent        → curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
2. Skills de Matt Pocock → hermes plugins install --enable mattpocock/skills
3. Los seis perfiles     → hermes profile create <perfil> --clone-from default --description '...'
4. Modelo por perfil     → hermes -p <perfil> model
```

> Los perfiles (Bots) requieren decisión humana: qué modelo y proveedor usa cada Bot. Bottega no elige por ti.

## 4. Validar que quedó listo

```bash
make doctor
```

Salida esperada: `[PASS]` en herramientas, plugin y los seis perfiles, y el resumen **"Bottega listo"**. Si algo falla, el mismo comando te da la línea exacta para corregirlo. `doctor` es solo lectura: nunca modifica nada.

## 5. Tu primer producto (Idea Prioritizer)

El ejemplo probado es **Idea Prioritizer** (`app01/`), una app local para registrar ideas y priorizarlas con `Impacto × Confianza × Facilidad`.

Para verlo correr sin pasar por los Bots:

```bash
cd app01 && npm ci && npm run dev
```

Para vivirlo como método completo, sigue `GUIA-DE-USO.md` con el identificador `PRODUCTO-001`:

```text
Necesidad
  → @andrea-verrocchio    (requisitos)        → GATE 1
  → @leonardo-da-vinci    (solución)          → GATE 2
  → @donatello-ux         (UX)                → UX GATE
  → @filippo-brunelleschi (arquitectura)      → GATE 3
  → @michelangelo-buonarroti (implementación) → GATE 4 (con evidencia)
  → @raffaello-sanzio     (validación)        → PASS / NEEDS_WORK / BLOCKED
  → cierre humano         (ADOPTAR / ADAPTAR / DETENER)
  → retrospectiva         (mejoras del método)
```

Reglas de oro: **un solo Bot por etapa** (nunca `@all`), **la misma ruta de proyecto** siempre, y **no se implementa** hasta aprobar requisitos, solución, UX y arquitectura.

## 6. Roles, skills y glosario

- **Mapa de roles y skills** de Matt Pocock: `docs/diagrama-skills-matt-pocock.md`.
- **Lenguaje del dominio** (gate, evidencia, DoD, paquete de revisión…): `GLOSSARY.md`.
- **Kit operativo** (iniciar proyectos con trazabilidad): `kit/README.md`.

## 7. Solución de problemas

| Síntoma | Qué hacer |
|---|---|
| `make doctor` marca `FAIL` | Lee la línea `→` de cada fallo; ejecuta ese comando y vuelve a correr `make doctor` |
| Un Bot no responde | Verifica el perfil y su modelo: `hermes profile show <perfil>` |
| `raffaello-sanzio` validó `NEEDS_WORK` | Regresa sus observaciones a Michelangelo y vuelve a validar (ver `GUIA-DE-USO.md`) |
| No entiendes un término | Búscalo en `GLOSSARY.md` |

## 8. Siguiente nivel (proficiente)

1. Corre tu primer producto real (no el ejemplo) con el **kit**: `kit/scripts/init_bottega_project.py --target ... --dry-run` y luego sin `--dry-run`.
2. Exige el **paquete de revisión** (`REVIEW-PACKET.md`: Summary → Evidence → Merge Danger) antes de cada validación.
3. Después de cada cierre, corre la **retrospectiva** para mejorar el método (la ejecuta una persona autorizada, nunca un Bot solo).

## 9. Advisor (Incremento 1) — motor determinista, sólo lectura

El Advisor convierte una necesidad en un contrato verificable (hechos, supuestos, preguntas abiertas, NO DETERMINABLE, requisitos y criterios) **sin LLM ni proveedor**. No ejecuta cambios: toda salida es una propuesta de sólo lectura que nunca autoriza release, publicación ni producción.

### Subcomandos

```bash
python3 kit/scripts/bottega_advisor.py validate-intake --input kit/tests/fixtures/advisor/intake-valid.yaml
python3 kit/scripts/bottega_advisor.py prepare-report --intake kit/tests/fixtures/advisor/intake-valid.yaml \
  --out report.json --now 2026-10-26T00:00:00Z
python3 kit/scripts/bottega_advisor.py validate-report --input report.json
python3 kit/scripts/bottega_advisor.py export-casefile --intake kit/tests/fixtures/advisor/intake-valid.yaml \
  --report report.json --out ./casefile
```

Códigos de salida estables (los consume CI): `0` PASS, `1` NEEDS_WORK, `2` CLI/IO, `3` BLOCKED.

### Reglas y límites

- Datos sintéticos por defecto (`SYNTHETIC` / `SYNTHETIC_FIXTURE`). Secretos, datos reales/institucionales, Producto 02, producción, Frappe o proveedor/modelo distinto de `none` ⇒ `BLOCKED` (exit 3), cero efecto.
- Todo campo no verificable se marca `NO DETERMINABLE`; el motor nunca inventa un valor ni lo convierte en supuesto silencioso.
- El reporte es determinista: misma entrada + mismo `--now` ⇒ bytes idénticos.
- El expediente exportado incluye un manifiesto de hash; un tampering ⇒ `HASH_MISMATCH` (exit 3).

Correr las pruebas: `make advisor-validate` (o `make advisor-test`). El `PASS` técnico del Advisor no autoriza ejecución, release, publicación ni producción.

Consulta de referencia completa: `GUIA-DE-USO.md`.
