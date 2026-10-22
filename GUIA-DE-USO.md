# Bottega — Guía de uso

**Versión:** 1.0
**Propietario:** Equipo Bottega
**Sección:** Soluciones de Software
**Grupo:** Bottega

## Qué es

Bottega es un grupo de seis Bots nuevos y especializados que convierten una necesidad de software en un producto terminado, probado, documentado y listo para compartirse bajo buenas prácticas open source. Usted conduce; cada Bot ejecuta una sola especialidad y deja evidencia en el repositorio del proyecto.

```text
Andrea del Verrocchio  → requisitos
Leonardo da Vinci      → diseño de solución
Donatello (UX)         → experiencia de usuario y diseño
Filippo Brunelleschi   → arquitectura técnica
Michelangelo Buonarroti→ implementación y pruebas
Raffaello Sanzio       → revisión independiente
```

## Roles y skills de Matt Pocock

| Bot | Función | Skills prioritarios |
|---|---|---|
| Andrea del Verrocchio | Requisitos y FRD | `grilling`, `grill-with-docs`, `domain-modeling`, `to-spec` |
| Leonardo da Vinci | Alternativas y plan de solución | `wayfinder`, `codebase-design`, `research`, `to-spec`, `to-tickets` |
| Donatello | UX y diseño de producto | `discovery`, `flujos`, `arquitectura de información`, `prototipos`, `accesibilidad`, `pruebas de usabilidad`, `handoff` |
| Filippo Brunelleschi | Arquitectura técnica | `codebase-design`, `improve-codebase-architecture`, `domain-modeling`, `prototype` |
| Michelangelo Buonarroti | Implementación y TDD | `implement`, `implement-spec`, `tdd`, `diagnosing-bugs`, `pr` |
| Raffaello Sanzio | Revisión independiente | `code-review`, `triage`, `handoff`, `wait-what` |

## El flujo con gates

```text
Necesidad
   ↓
Andrea: requisitos          → GATE 1 (usted)
   ↓
Leonardo: diseño            → GATE 2 (usted)
   ↓
Donatello: UX y prototipo   → UX GATE (usted)
   ↓
Filippo: arquitectura       → GATE 3 (usted)
   ↓
Michelangelo: implementación→ GATE 4 (usted, con evidencia)
   ↓
Donatello: fidelidad UX     → verificación
   ↓
Raffaello: validación       → PASS / NEEDS_WORK / BLOCKED
   ↓
Correcciones ↔ nueva validación
   ↓
Producto liberable
   ↓
Cierre humano             → ADOPTAR / ADAPTAR / DETENER
   ↓
Retrospectiva             → backlog de mejoras del método
```

## Reglas de operación

1. Abra **Bots → Soluciones de Software → Bottega**.
2. Mencione **un solo Bot por etapa**. Nunca use `@all`.
3. Use un identificador común, por ejemplo `PRODUCTO-001`.
4. Indique siempre la misma **ruta absoluta** del proyecto:
   ```text
   RUTA_PROYECTO=/ruta/al/repositorio/idea-prioritizer
   ```
5. Cada Bot lee los artefactos anteriores antes de producir el suyo.
6. No autorice implementación hasta aprobar requisitos, solución, UX y arquitectura.
7. Si Raffaello devuelve `NEEDS_WORK`, regrese sus observaciones a Michelangelo y vuelva a validar.
8. El producto está terminado solo cuando Raffaello emite `PASS`.

---

## Ejemplo completo: Idea Prioritizer

Una aplicación web para registrar ideas y priorizarlas mediante ICE:

```text
Prioridad = Impacto × Confianza × Facilidad
```

Sustituya `<RUTA_PROYECTO>` por una ruta real y permanente antes de iniciar.

### Etapa 1 — Andrea define el producto

```text
@andrea-verrocchio inicia PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

Necesidad:

Necesito una aplicación web sencilla llamada Idea Prioritizer para registrar
ideas y priorizarlas mediante impacto, confianza y facilidad. Debe usar solo
datos sintéticos, funcionar localmente y poder compartirse como open source.

Usa grilling, grill-with-docs, domain-modeling y to-spec.

Crea docs/01-product-requirements.md con:
1. problema y resultado esperado;
2. tipos de usuario;
3. historias de usuario;
4. modelo de dominio;
5. reglas de negocio;
6. requisitos funcionales;
7. requisitos no funcionales;
8. validaciones y casos límite;
9. criterios de aceptación verificables;
10. alcance y elementos fuera de alcance;
11. preguntas abiertas;
12. Definition of Done preliminar.

No escribas código. Separa hechos, supuestos y preguntas. Verifica el archivo
y reporta su ruta.
```

**Revisión del gate 1:** ¿funciones suficientes? ¿sin datos personales? ¿criterios comprobables? ¿alcance sin crecer?

Si hay cambios:

```text
@andrea-verrocchio corrige docs/01-product-requirements.md para incorporar:
[CAMBIOS]. Mantén PRODUCTO-001.
```

Cuando esté conforme:

```text
GATE-1 APROBADO para PRODUCTO-001.
```

### Etapa 2 — Leonardo diseña la solución

```text
@leonardo-da-vinci continúa PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

Lee docs/01-product-requirements.md.

Usa wayfinder, research, codebase-design, to-spec y to-tickets.

Compara al menos: (1) web estática con almacenamiento local; (2) cliente-
servidor con API y base de datos; (3) adaptar una solución open source.

Evalúa cada alternativa por: cumplimiento, complejidad, mantenibilidad,
seguridad, pruebas, operación, costo, dependencia tecnológica, facilidad
open source y reversibilidad.

Crea docs/02-solution-design.md y docs/02-delivery-backlog.md.

Recomienda una alternativa y justifica. El backlog debe tener épicas,
historias, dependencias, riesgos y criterios de aceptación.

No implementes. Verifica los archivos y reporta sus rutas.
```

Para este ejemplo lo razonable es: aplicación estática TypeScript + React + Vite con persistencia local.

Después de revisar:

```text
GATE-2 APROBADO para PRODUCTO-001.
Alternativa aprobada: [ALTERNATIVA].
```

### Etapa 3 — Filippo define la arquitectura

```text
@filippo-brunelleschi continúa PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

Lee: 01-product-requirements.md, 02-solution-design.md, 02-delivery-backlog.md.

Usa codebase-design, improve-codebase-architecture, domain-modeling y prototype.

Crea:
- docs/03-architecture.md
- docs/adr/0001-technology-stack.md
- docs/adr/0002-data-persistence.md
- docs/03-test-strategy.md
- docs/03-security-model.md

Define: componentes y responsabilidades; estructura del repositorio; entidades
y contratos TypeScript; flujo de información; persistencia y versionado;
importación/exportación JSON; validación de entradas; manejo de errores;
seguridad y privacidad; accesibilidad; observabilidad; estrategia de pruebas
unitarias, de componentes y end-to-end; empaquetado con Docker; versiones y
releases; ADR con trade-offs.

No escribas código de producción. Comprueba trazabilidad y reporta bloqueos.
```

**Revisión del gate 3:** arquitectura sin sobrecomplejidad, componentes con responsabilidades separadas, estrategia de migración de datos, pruebas que cubren la regla de prioridad, ejecución sin servicios institucionales.

```text
GATE-3 APROBADO para PRODUCTO-001.
Arquitectura autorizada para implementación sandbox.
```

### Etapa 4 — Michelangelo implementa

```text
@michelangelo-buonarroti implementa PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

Gate vigente: GATE-3 APROBADO. Entorno: exclusivamente sandbox.
No uses producción, servicios institucionales ni datos reales.

Lee todos los artefactos de docs/ antes de modificar archivos.

Usa implement-spec, implement, tdd, diagnosing-bugs y pr.

Implementa mediante TDD: prueba roja, cambio mínimo, prueba verde, refactor.

El repositorio debe incluir como mínimo:
- código fuente;
- pruebas unitarias, de componentes y end-to-end;
- lint y typecheck;
- build reproducible;
- datos sintéticos de ejemplo;
- Dockerfile, docker-compose.yml, .dockerignore, .gitignore;
- README.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md,
  CHANGELOG.md;
- docs/;
- GitHub Actions para CI;
- plantillas de issue y pull request;
- package-lock.json o equivalente.

Estandariza: npm run dev / lint / typecheck / test / test:e2e / build / validate.

npm run validate ejecuta todos los controles requeridos.

Antes de responder ejecuta: instalación limpia, lint, typecheck, pruebas,
build, imagen Docker, contenedor, comprobación funcional, detención del
contenedor, verificación de ausencia de secretos, y genera
docs/04-implementation-report.md.

Genera también `REVIEW-PACKET.md` (plantilla en `kit/templates/REVIEW-PACKET.md`)
con Summary, Evidence y Merge Danger. Debe citar el HEAD exacto, el manifiesto
de evidencia y la reversibilidad del cambio. Sin este paquete no se promueve a
revisión independiente.

No declares éxito si falla una comprobación. Reporta comandos reales,
resultados, cobertura, archivos modificados y pendientes.
```

**Gate 4 requiere evidencia real** (no basta que Michelangelo afirme "listo"):

```text
npm ci               → PASS
npm run lint         → PASS
npm run typecheck    → PASS
npm test             → PASS
npm run test:e2e     → PASS
npm run build        → PASS
npm run validate     → PASS
docker compose build → PASS
docker compose up    → aplicación accesible
```

Si todo está respaldado:

```text
GATE-4 APROBADO para PRODUCTO-001.
Implementación lista para revisión independiente.
```

### Etapa 5 — Raffaello valida

```text
@raffaello-sanzio valida independientemente PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

No aceptes el reporte de Michelangelo como evidencia suficiente. Inspecciona
y reproduce.

Lee requisitos, diseño, arquitectura, ADR, estrategia de pruebas, código,
pruebas, documentación, `REVIEW-PACKET.md` y docs/04-implementation-report.md.

Usa code-review, triage, handoff y wait-what.

Debes: comprobar trazabilidad; ejecutar npm ci y npm run validate; pruebas
end-to-end; build; construir y ejecutar el contenedor; probar el flujo
principal; entradas inválidas y casos límite; seguridad, accesibilidad y
privacidad; ausencia de secretos; dependencias y licencias; instrucciones de
instalación desde cero; LICENSE, README, CONTRIBUTING, SECURITY, CHANGELOG y
CI; que una tercera persona pueda ejecutar el producto.

Crea docs/05-validation-report.md y docs/05-release-checklist.md.

Emite exactamente uno de: PASS, NEEDS_WORK, BLOCKED.

Incluye evidencia, comandos, resultados y defectos por severidad. No corrijas
silenciosamente.
```

---

## Ciclo de corrección

Si Raffaello responde `NEEDS_WORK`:

```text
@michelangelo-buonarroti corrige PRODUCTO-001.

RUTA_PROYECTO=<RUTA_PROYECTO>

Lee docs/05-validation-report.md y docs/05-release-checklist.md.

Corrige todos los defectos críticos y altos. Aplica TDD a cada corrección.
No reduzcas controles, cobertura ni criterios para que pasen las pruebas.

Actualiza pruebas, documentación, CHANGELOG.md y
docs/04-implementation-report.md.

Ejecuta npm run validate, build y prueba del contenedor. Reporta resultados
reales.
```

Luego:

```text
@raffaello-sanzio vuelve a validar PRODUCTO-001 después de las correcciones.

Reproduce todas las comprobaciones y actualiza los reportes. Emite PASS,
NEEDS_WORK o BLOCKED.
```

Repita hasta obtener `PASS`.

---

## Retrospectiva (fuera del gate)

La retrospectiva no forma parte de la validación del producto. Se ejecuta después del cierre humano (ADOPTAR / ADAPTAR / DETENER) y revisa sesiones reales para proponer mejoras al entorno del agente, nunca para reabrir el veredicto.

```text
Veredicto del producto (PASS / NEEDS_WORK / BLOCKED)
   ↓
Cierre humano (ADOPTAR / ADAPTAR / DETENER)
   ↓
Selección de sesiones (una fallida o representativa)
   ↓
Retrospectiva → hallazgos clasificados por severidad
   ↓
Backlog de mejoras del método (ACEPTAR / POSPONER / RECHAZAR)
```

Cada hallazgo se clasifica en una de estas categorías:

- **mecánica**: se convierte en lint, test, hook o CI;
- **criterio**: se documenta para revisión;
- **navegación**: se añade un puntero;
- **herramientas/tokens**: se optimiza el flujo;
- **información**: se habilita acceso de solo lectura.

Reglas: la retrospectiva la ejecuta cualquier persona autorizada (Director, ingeniero u operador) sobre sesiones seleccionadas; nunca un Bot de forma autónoma. Un Bot puede asistir redactando hallazgos, pero aceptar, posponer o rechazar es decisión humana. No se auto-aplica: no edita por sí misma perfiles, skills, CI ni reglas; cada hallazgo aceptado se implementa como una mejora separada con gate.

---

## Definition of Done

El producto está terminado solo si cumple **todo** lo siguiente.

**Producto**
- [ ] Todos los requisitos aceptados implementados.
- [ ] Funciones principales ejecutables de principio a fin.
- [ ] Errores y casos límite controlados.
- [ ] Solo información sintética.

**Calidad**
- [ ] Lint sin errores.
- [ ] Typecheck sin errores.
- [ ] Pruebas unitarias, de componentes y end-to-end aprobadas.
- [ ] Cobertura mínima documentada.
- [ ] Build reproducible.
- [ ] Raffaello emitió `PASS`.

**Ejecución**
- [ ] `npm ci && npm run dev` funciona.
- [ ] Docker funciona.
- [ ] `npm run validate` reproduce todos los controles.
- [ ] Una computadora limpia puede seguir el README.
- [ ] Sin dependencias de rutas personales o credenciales.

**Documentación**
- [ ] `README.md` (usuario, instalación, desarrollo, troubleshooting).
- [ ] Documentación técnica.
- [ ] Arquitectura y ADR.
- [ ] Estrategia de pruebas.
- [ ] `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`.

**Open source**
- [ ] Licencia con identificador SPDX.
- [ ] Derechos de publicación confirmados.
- [ ] Sin datos institucionales, personales, credenciales ni secretos.
- [ ] Dependencias y licencias compatibles.
- [ ] CI configurado.
- [ ] Plantillas de issues y pull requests.
- [ ] Política de reporte de vulnerabilidades.
- [ ] Versión semántica (ej. `0.1.0`).
- [ ] Release notes preparadas.
- [ ] Artefacto ejecutable o imagen de contenedor reproducible.

> Publicación pública exige autorización institucional aparte, aunque el producto quede técnicamente listo.

---

## Resultado final esperado

```text
idea-prioritizer/
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/
│   ├── adr/
│   ├── 01-product-requirements.md
│   ├── 02-solution-design.md
│   ├── 02-delivery-backlog.md
│   ├── 03-architecture.md
│   ├── 03-test-strategy.md
│   ├── 03-security-model.md
│   ├── 04-implementation-report.md
│   ├── 05-validation-report.md
│   └── 05-release-checklist.md
├── src/
├── tests/
├── e2e/
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── package.json
└── package-lock.json
```

## Operación canónica con el kit de mejoras

Antes de iniciar una iniciativa, el Director confirma el alcance y se crea un
`PROJECT-BRIEF.yaml` con datos sintéticos, riesgos, gates y autorizaciones. El
preflight es obligatorio y no destructivo; desde la raíz de `kit/` se
ejecuta:

```bash
python3 scripts/bottega_preflight.py --project <RUTA_PROYECTO> --dry-run --format json
```

El scaffold reproducible y sus comandos reales están en
`kit/README.md`. Para crear un proyecto local, sin remoto:

```bash
python3 scripts/init_bottega_project.py \
  --target <RUTA_PROYECTO> --product-name "Producto sintético" \
  --slug producto-sintetico --owner "Usuario Ejemplo" \
  --org organizacion-ejemplo --init-git
```

Cada iniciativa debe conservar estos artefactos: `PROJECT-BRIEF.yaml`,
`ACCEPTANCE-MANIFEST.yaml` (requisito → prueba → evidencia),
`REVIEW-PACKET.md` (Summary → Evidence → Merge Danger),
`WORKFLOW-STATE.json` y `runs/<run-id>/attempts/<n>/manifest.json`. El
manifiesto de evidencia se crea con hash y no se edita después; cualquier
corrección genera un intento nuevo. `gate_check.py` verifica los archivos, los
estados, los contadores separados, la política 429 y los hashes:

```bash
python3 scripts/gate_check.py --project <RUTA_PROYECTO> --format json
```

El Kanban refleja dependencias explícitas: Andrea → Leonardo → Filippo →
Michelangelo → Raffaello. Cada tarjeta nombra un único Bot, su artefacto de
salida, la prueba que lo valida y la tarjeta predecesora; no se mueve una
tarjeta a ejecución si su dependencia no está aprobada.

Los estados de decisión no se sustituyen entre sí:

- `PRODUCT_PASS`: requisitos, pruebas y gates del producto aprobados.
- `RELEASE_READY_CONDITIONAL`: listo técnicamente, pero condicionado a
  pendientes o controles de liberación; no autoriza publicación.
- `PUBLICATION_AUTHORIZED`: autorización institucional explícita y vigente;
  si no existe, permanece `NO`.

Un primer HTTP 429 abre el circuit breaker. Se detiene el intento y solo se
usa fallback si `authorization.fallback_allowed: true` en el brief; nunca se
reintenta a ciegas ni se cambian proveedores en producción. Un repositorio
privado es opcional y requiere autorización explícita y los flags
`--create-private-repo --repo-name ... --confirm-private-repo`; nunca se crea
un repositorio público ni remoto por defecto.

Raffaello permanece bloqueado hasta `READY_FOR_VALIDATION` (GATE-4 con
evidencia reproducible). Su revisión independiente vuelve a emitir `PASS`,
`NEEDS_WORK` o `BLOCKED`; `PASS` no equivale a `PUBLICATION_AUTHORIZED`.
Conserve la regla de un Bot por etapa y no use `@all`.

Glosario: [Definition of Done](docs/glossary/entries/definition-of-done.md#glossary-definition-of-done).
