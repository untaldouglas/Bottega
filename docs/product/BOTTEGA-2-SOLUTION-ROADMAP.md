# Bottega 2.0 — Solución y roadmap por incrementos

Estado: propuesta para GATE 2; no autoriza implementación, PoC, instalación de Frappe, release, publicación, producción ni cambios en GitHub.
Fecha: 2026-10-26 (CST, UTC-06:00).
Propietario de decisión: Douglas.

## 1. Propósito y trazabilidad de entrada

Este documento convierte el Product Brief y requisitos del Incremento 0 en una solución conceptual y un roadmap ejecutable por gates. Conserva el alcance aprobado: reducir tiempo, costo y retrabajo sin trasladar aceptación humana, release, publicación o producción a la autonomía.

Entradas revisadas:

- `BOTTEGA-2-REQUIREMENTS.md`, Product Brief aprobado para revisión, fuente de RF-001…RF-020, RNF-001…RNF-012, CA-001…CA-020, M-001…M-009, R-001…R-010 y decisiones D-001…D-008.
- Issue #1, “Bottega 2.0 — Incremento 0: consolidación y contrato de producto”: https://github.com/untaldouglas/Bottega/issues/1
- Issue #3, “Definir el contrato de producto de Bottega 2.0”: https://github.com/untaldouglas/Bottega/issues/3
- Repositorio público Bottega, leído sin modificar: https://github.com/untaldouglas/Bottega
- `README.md`, `ESTADO-PROYECTO.md`, `GUIA-DE-USO.md`, `kit/VALIDATION.md` y `kit/` del repositorio.

Observación de base: el repositorio ya ofrece un método por etapas con seis roles, aprobación humana, kit de preflight/init/gate check, manifiestos, paquete de revisión y un ejemplo `app01`. Es evidencia del método y del kit actual; no es evidencia de desempeño de Bottega 2.0, ni autorización para reutilizar Producto 02, fusionar PR #5 o ejecutar producción.

## 2. Propuesta de valor

Bottega 2.0 debe ser una capa de decisión y ejecución gobernada que reduzca trabajo perdido, contexto repetido y retrabajo evitable. Su valor no es “automatizar todo”; es hacer visible y repetible el camino desde una necesidad hasta un producto revisado, manteniendo los puntos de autoridad humana.

Resultados de valor:

1. Advisor transforma una necesidad incompleta en un contrato verificable, con alternativas y preguntas explícitas.
2. Taller convierte el contrato en una secuencia de trabajo con un owner por etapa, dependencias, permisos y artefactos esperados.
3. Auditor comprueba coherencia, trazabilidad, hashes, políticas y estados; distingue PASS, NEEDS_WORK y BLOCKED sin convertir un PASS en autorización institucional.
4. El expediente permite reanudar sin repetir silenciosamente acciones ni perder la razón de un bloqueo.
5. La plataforma permite usar un Golden Path Frappe v16 sin contaminar el core neutral.
6. La organización puede medir tiempo, costo, retrabajo, bloqueos contenidos e integridad de evidencia con denominadores explícitos, sin inventar mejoras antes de un baseline.

Hipótesis de valor a validar, no promesa: menos horas de ciclo, menor retrabajo y mejor trazabilidad que un flujo comparable sin Bottega. M-001…M-009 son métricas candidatas; P1, P2 y P7 siguen NO DETERMINABLE hasta definir baseline, límites y umbrales.

## 3. Alternativas consideradas

### A — Construir un runtime neutral propio desde cero

Descripción: construir primero un servicio de expedientes, políticas, workflow, ejecución de proveedores, reanudación, auditoría y UI; añadir después perfiles de plataforma y conectores.

Cumplimiento: alto potencial para RF-001…RF-020 y RNF-001…RNF-012.
Complejidad y costo: muy altos; requiere identidad, autorización, persistencia, idempotencia, ejecución segura, observabilidad, secretos y compatibilidad de proveedores antes de demostrar valor.
Mantenibilidad: control total, pero alto costo de propiedad.
Seguridad y auditabilidad: diseñables de forma correcta, pero el riesgo de fallar en detalles es alto.
Pruebas: amplias; especialmente reanudación, circuit breaker, estados separados e independencia.
Dependencias: infraestructura, almacenamiento, sandbox y contratos de proveedores aún NO DETERMINADOS (P3/P4/P6).
Reversibilidad: baja una vez que el dominio, el esquema y los contratos públicos quedan adoptados.

Veredicto: no recomendable como primer paso. Es construir demasiado antes de validar el contrato y la economía del flujo.

### B — Adaptar directamente una plataforma open source de orquestación

Descripción: seleccionar y modificar un motor de workflow/agentes o el kit/repositorio Bottega existente para obtener UI, jobs, proveedores y persistencia rápidamente.

Cumplimiento: medio; puede cubrir ejecución, pero no garantiza los contratos específicos de Advisor/Taller/Auditor, estados de decisión independientes ni fail-closed.
Complejidad y costo: menor al inicio; mayor costo oculto de adaptar semántica, migraciones, upgrades y límites del proyecto de origen.
Mantenibilidad: dependiente de upstream y de la calidad del fork/adaptadores.
Seguridad y auditabilidad: se heredan supuestos; deben verificarse, no inferirse.
Pruebas: se aprovecha cobertura existente, pero hay riesgo de confundir tests del framework con CA del producto.
Dependencias: licencia, versión, modelo de datos, API, proveedor y ciclo de cambios del upstream.
Reversibilidad: media si el dominio propio está detrás de un adaptador; baja si se acopla directamente al esquema del upstream.

Veredicto: no adoptar como núcleo sin un spike autorizado, análisis de licencia/seguridad y pruebas contra CA. Puede ser fuente de patrones o componente sustituible, nunca la definición del contrato.

### C — Híbrida: contrato neutral + adaptadores pequeños + kit documental

Descripción: preservar primero el dominio y los contratos como core neutral; reutilizar/adaptar sólo piezas comprobadas del kit Bottega y, cuando corresponda, un motor open source detrás de un adaptador. Implementar verticales pequeñas y verificables: primero Advisor, luego expediente/gates/reanudación, después perfil Frappe y finalmente piloto.

Cumplimiento: alto y gradual; RF/RNF se validan por verticales, sin anticipar runtime completo.
Complejidad y costo: moderados; se paga el costo del contrato y de los adaptadores, no una plataforma completa de una vez.
Mantenibilidad: buena si el core define interfaces estables y el adaptador concentra variabilidad.
Seguridad y auditabilidad: el contrato fail-closed es propio; cada integración debe probarse en sandbox.
Pruebas: alineadas con CA; fixtures sintéticas separan evidencia del método de evidencia del producto.
Dependencias: decisiones posteriores sobre identidad, persistencia, proveedores y límites; no bloquea el diseño conceptual de I0.
Reversibilidad: alta en selección de proveedor, motor y perfil; baja sólo en decisiones explícitamente declaradas como contrato público.

Veredicto: recomendada. Es la alternativa con mejor relación evidencia/riesgo y permite detenerse temprano si Advisor o el piloto no justifican más construcción.

### D — No construir todavía; consolidar contrato y usar el método existente

Descripción: mantener Bottega como método documental y kit validado, sin runtime 2.0, hasta obtener un caso de uso y baseline comparativo.

Cumplimiento: adecuado para I0; insuficiente para validar RF-002, RF-010, RF-011 y la economía de automatización.
Costo y riesgo: mínimos; no hay lock-in ni superficie operativa nueva.
Reversibilidad: máxima.

Veredicto: es la política de fallback y un gate válido, no la solución objetivo. Si no se resuelven P3/P4/P5/P6 o no hay sponsor y piloto autorizado, se debe DETENER en lugar de construir por inercia.

### Decisión

Recomendar C, con D como condición de salida. No se selecciona todavía proveedor, motor open source, esquema definitivo, identidad, despliegue ni baseline operativo. La selección de componentes se difiere a un spike autorizado después de aprobar el contrato y sus criterios.

## 4. Forma de la solución propuesta

### 4.1 Núcleo neutral

El core expresa conceptos y reglas independientes de Frappe y de un proveedor de IA:

- Initiative: owner, alcance, clasificación de datos, autorizaciones, riesgos, gates y estado.
- Artifact y Evidence: salida, origen, entorno, timestamp, hash, intento y relación con requisitos/pruebas.
- RequirementLink: requisito, criterio, prueba, owner, evidencia y resultado.
- Stage: etapa, un Bot responsable, predecesoras, permisos y artefactos esperados.
- PolicyDecision: autorización, alcance, datos permitidos, política de proveedor y condición de gate.
- Run/Attempt: `delivery_attempt`, `provider_retry`, `validation_attempt`, `operational_cleanup` separados.
- DecisionState: `PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL`, `PUBLICATION_AUTHORIZED` independientes.
- Review: actor independiente, veredicto PASS/NEEDS_WORK/BLOCKED y razones.

Reglas núcleo: fail-closed ante ausencia o ambigüedad; no se habilita una etapa sin predecesora aprobada y evidencia; un retry no reescribe un intento; los manifiestos son inmutables; un PASS técnico nunca implica release/publicación/producción; retrospectivas sólo producen propuestas.

El core no debe importar APIs, documentos o modelo de datos de Frappe (RF-016, RNF-007). La persistencia, ejecución y UI se consumirán por puertos/adaptadores en la arquitectura posterior; esta separación es una decisión de diseño, no una autorización para implementarla ahora.

### 4.2 Adaptador y perfil Frappe v16

Frappe v16 es la línea oficial para productos nuevos y `v16.53.0` es baseline candidato, no `latest` (D-002/D-003). El adaptador Frappe debe:

- mapear sólo capacidades necesarias del Golden Path a contratos del core;
- registrar versión, entorno, fecha, resultado y evidencia de validación;
- mantener instalaciones, fixtures y pruebas fuera del core neutral;
- rechazar el perfil si el baseline candidato no es instalable o compatible;
- no permitir que una API o DocType de Frappe se convierta accidentalmente en regla de dominio;
- poder sustituirse por otro perfil sin migrar el dominio del core.

La validación de Frappe pertenece a I3; I0 no instala Frappe. CA-013 y CA-014 son gates mínimos.

### 4.3 Advisor, Taller y Auditor

Advisor — entrada: necesidad y contexto permitido. Salida: problema, actores, trabajos, alternativas, alcance, hechos, supuestos, preguntas abiertas, NO DETERMINABLE, riesgos, requisitos y criterios. Límite: no ejecuta cambios irreversibles ni interpreta una aceptación conversacional como autorización (RF-001/002, CA-001/003).

Taller — entrada: brief aprobado y autorizaciones. Salida: iniciativa, stages, dependencias, owner, datos, riesgos, gates, artefactos, runs y reanudación. Límite: sólo ejecuta dentro de la política declarada; no desbloquea por sí mismo una condición humana (RF-003/005/006/010/011/012, CA-004/009/011/017).

Auditor — entrada: expediente y evidencia. Salida: PASS, NEEDS_WORK o BLOCKED, siempre con razón y referencia. Límite: no se audita a sí mismo, no modifica evidencia histórica y no autoriza release/publicación/producción (RF-004/007/008/014/020, CA-005/006/007/018/019/020).

## 5. Roadmap por incrementos verticales

Cada incremento entrega un flujo comprobable y tiene un gate propio. El orden evita construir ejecución irreversible antes de fijar contratos, identidad y autorización.

### I0 — Contrato y solución (actual)

Entrega: Product Brief, solución recomendada, alternativas, trazabilidad, gates, riesgos y roadmap.
Dependencias: Issue #1, Issue #3 y Product Brief.
No incluye: código, PoC, Frappe, runtime, proveedor, UI, Producto 02 o datos reales.
Gate: aprobación independiente del paquete y aprobación final de Douglas. Resultado: GATE 1 aprobado sólo si el paquete es coherente, trazable y separado del contrato de implementación. Este documento recomienda C/D, no autoriza I1.

### I1 — Advisor mínimo verificable

Vertical: necesidad incompleta → expediente de propuesta con hechos/supuestos/NO DETERMINABLE, requisitos y criterios.
Incluye RF-001/002, RF-007 de forma documental, RF-015 y RNF-010/011/006; fixtures sintéticas y exportación del expediente.
Dependencias: GATE 1; decisiones mínimas sobre formato de expediente, identidad del operador y clasificación de datos (P3/P6 no pueden ocultarse).
Evidencia: CA-001, CA-003, CA-012, trazabilidad RF/RNF a prueba y artefacto.
Gate: Auditor independiente confirma contrato, privacidad y determinismo documental; Douglas decide continuar.
Salida: PRODUCT_PASS del Advisor no es autorización de ejecución.

### I2 — Core de Taller, gates y reanudación

Vertical: expediente aprobado → stages/gates → acción autorizada en sandbox → interrupción/reanudación → manifiesto auditable.
Incluye RF-003, RF-005…RF-015, RF-020 y RNF-001…RNF-012 según alcance probado; circuit breaker ante primer 429; contadores separados; revisión independiente.
Dependencias: I1 aprobado; política de proveedor/fallback; límites P2; identidad/autorización P3; almacenamiento/retención P6; sandbox no destructivo.
Evidencia: CA-002, CA-004…CA-011, CA-016…CA-020 y pruebas de seguridad.
Gate: ejercicios de bloqueo, reanudación, hash, 429, secreto y no autorización implícita. Ningún efecto en producción.

### I3 — Golden Path Frappe v16

Vertical: perfil Frappe separado que valida `v16.53.0` candidato y mapea sólo contratos necesarios.
Incluye RF-016/017, RNF-007 y CA-013/014.
Dependencias: I2 aprobado; entorno sandbox; versión y compatibilidad del producto piloto; decisión de alcance Frappe P5.
Evidencia: instalación reproducible, registro de versión/fecha/entorno, pruebas core sin Frappe y pruebas del adaptador.
Gate: baseline validado o BLOCKED. `latest` no satisface el gate. No se modifica Producto 02.

### I4 — Piloto controlado de Producto 03

Vertical: un producto nuevo, datos sintéticos, autorización específica, camino Frappe opcional y revisión independiente.
Incluye una muestra representativa de RF/RNF y CA, no una generalización institucional.
Dependencias: I2/I3 aprobados; sponsor y owner; autorización escrita del piloto; límites de costo/duración/concurrencia; comparación Caso A/Caso B.
Evidencia: expediente completo, hashes, comandos/resultados, métricas M-001…M-009 con denominadores, incidentes y decisión humana separada.
Gate: PRODUCT_PASS, luego decisión separada RELEASE_READY_CONDITIONAL; publicación permanece NO salvo autorización institucional explícita.

### I5 — Medición y decisión ADOPTAR/ADAPTAR/DETENER

Vertical: análisis del piloto y recomendación de evolución, no autoaplicación.
Dependencias: I4 cerrado y métricas con baseline suficiente; revisión independiente; owner de decisión.
Evidencia: comparación con alcance equivalente, costo autorizado, retrabajo, bloqueos contenidos, integridad y reanudación.
Gate: Douglas decide ADOPTAR, ADAPTAR o DETENER. Una retrospectiva sólo genera backlog; no cambia skills, CI, perfiles o reglas sin nueva iniciativa.

## 6. Backlog trazable a requisitos

| ID | Épica / entrega | Requisitos | Criterios de aceptación | Dependencias | Gate |
|---|---|---|---|---|---|
| S-01 | Contrato de modos | RF-001…RF-004 | CA-001, CA-003, CA-018 | I0 | GATE 1/I1 |
| S-02 | Expediente y trazabilidad | RF-003, RF-007, RF-014; RNF-001, RNF-004, RNF-011 | CA-005, CA-010, CA-019 | S-01 | I1/I2 |
| S-03 | Gates y autorización | RF-005, RF-008…RF-010, RF-020; RNF-003, RNF-009, RNF-010 | CA-004, CA-007, CA-008, CA-020 | S-02, P3 | I2 |
| S-04 | Ejecución segura/reanudable | RF-011…RF-015; RNF-002, RNF-005, RNF-008, RNF-012 | CA-002, CA-009, CA-011, CA-012, CA-017 | S-03, P2/P4/P6 | I2 |
| S-05 | Perfil Golden Path | RF-016/017; RNF-007 | CA-013, CA-014 | I2, P5 | I3 |
| S-06 | Reglas de separación | RF-018/019; RNF-006 | CA-015, CA-016 | S-03 | I2/I4 |
| S-07 | Auditoría independiente | RF-004/020; RNF-004/006 | CA-006, CA-018, CA-019 | S-02/S-03 | I2 |
| S-08 | Piloto y medición | RF/RNF ejercitados por alcance; M-001…M-009 | evidencia comparable y decisión separada | I2, I3, autorización piloto | I4/I5 |

Una tarjeta de implementación futura sólo puede crearse si conserva: IDs de requisitos, CA, owner, dependencia, evidencia esperada, reversibilidad, datos permitidos y gate. No se crean tickets para Producto 02, producción, integración institucional o mejoras de gobernanza autoaplicadas.

## 7. Decisiones reversibles e irreversibles

Reversibles y diferibles: motor de workflow; proveedor/modelo; UI; almacenamiento concreto; formato de exportación si existe adaptador; proveedor cloud/local; número de workers; estrategia de observabilidad; selección de open source; profundidad del perfil Frappe. Criterio: encapsular detrás de puertos, registrar versión y probar sustitución en sandbox.

Irreversibles o costosas: contrato público de estados y autoridad humana; semántica de hashes/attempts; clasificación de datos; exposición de secretos; acoplar dominio a Frappe; migrar Producto 02; publicar datos o integraciones; aceptar un esquema de identidad/retención sin política. Requieren decisión de Douglas, ADR o equivalente, evidencia de impacto y gate explícito.

Protecciones: ningún proveedor, CI verde, PR abierto, `PRODUCT_PASS` o revisión PASS puede convertirse en `PUBLICATION_AUTHORIZED` (RF-008/009, CA-007/008/020).

## 8. Economía de herramientas y contexto

Principios:

- Un expediente canónico por iniciativa; cada etapa recibe sólo el resumen, decisiones, requisitos, artefactos y evidencia relevantes, no todo el historial conversacional.
- Resumen estable de contexto: problema, alcance, riesgos, decisiones protegidas, IDs de requisitos y estado del gate. Los artefactos grandes se referencian por ruta/hash.
- Un Bot por etapa y un revisor independiente; evitar `@all`, duplicación de análisis y auto-revisión, coherente con la guía actual.
- Ejecutar Auditor y validaciones deterministas antes de consumir modelos caros. Usar modelos/proveedores sólo donde exista juicio no determinista y una política explícita.
- Reintentos de proveedor, correcciones de entrega y validaciones cuentan por separado para no ocultar costo ni retrabajo.
- Fixtures sintéticas, preflight no destructivo y caché de artefactos verificables reducen costo sin convertir fixtures en evidencia de producto.
- Preferir una vertical pequeña con evidencia completa sobre una plataforma horizontal con muchas capacidades no usadas.
- Presupuestos de tokens, duración, concurrencia y costo quedan NO DETERMINABLE hasta resolver P2; no se inventan umbrales.

Indicadores a observar: M-003 tiempo de ciclo, M-004 retrabajo, M-008 costo por producto y M-001/M-006/M-007 calidad de evidencia. Ninguno es objetivo aprobado hasta tener baseline y owner.

## 9. Política de no sobrediseño

1. No implementar una abstracción sin un segundo consumidor o un criterio de sustitución demostrable.
2. No construir multiusuario, multi-tenant, marketplace, plugin system, event bus, scheduler permanente, billing, analytics avanzado ni compatibilidad amplia de proveedores: todos están fuera del alcance aprobado salvo decisión posterior.
3. No elegir un esquema definitivo de identidad, retención o concurrencia mientras P2/P3/P6 sean NO DETERMINABLE.
4. No usar Producto 02 como runtime, fixture operativa, fuente de migración ni prueba de rendimiento.
5. No convertir el kit documental existente en prueba de un runtime futuro; repetir las CA contra el producto nuevo.
6. No agregar fallback, paralelismo o reintentos por “resiliencia” si no hay autorización explícita y contadores observables.
7. Cada incremento debe poder detenerse con un artefacto revisable y sin efectos irreversibles.
8. Si D no basta para resolver una pregunta, se bloquea y se escala; no se rellena con convenciones técnicas.

## 10. Dependencias y riesgos

Dependencias externas: decisión de Douglas en cada gate; identidad/autorización P3; límites P2; proveedores P4; Golden Path P5; retención P6; umbrales P7; entorno sandbox; licencias y seguridad de cualquier open source; disponibilidad de baseline Frappe v16.53.0.

Riesgos principales y respuesta:

- R-001/R-002: PASS o autonomía se confunden con autoridad. Estados independientes, fail-closed, aprobación humana y CA-007/008/020.
- R-003: lock-in Frappe o motor. Core neutral, perfil/adaptador aislado, CA-013.
- R-004: retries/fallback ocultan costo o fallas. Circuit breaker al primer 429, política declarada y contadores separados.
- R-005/R-006: fixtures o Producto 02 se convierten en evidencia/runtime. Clasificación, bloqueos y CA-012/015.
- R-007: métricas sin baseline. Numerador, denominador, fuente, owner y estado candidata.
- R-008/R-009: Auditor se revisa a sí mismo o reanudación duplica efectos. Actor independiente, manifiestos inmutables e idempotencia observable.
- R-010: retrospectiva cambia sus propias reglas. Backlog separado y gate humano.
- Riesgo nuevo de adaptación open source: licencia, seguridad, divergencia y migración. Mitigación: spike read-only/autorizado, due diligence, adaptador y criterio de salida D.
- Riesgo de sobreconstrucción: I2 se convierte en plataforma antes del piloto. Mitigación: verticales, gates y lista explícita de exclusiones.

## 11. Criterios de gate y decisión

GATE 1 / cierre de I0: hechos, supuestos, preguntas y decisiones separados; alternativa C recomendada y D como fallback; contratos de modos completos; RF/RNF/CA trazables; core neutral y Frappe separado; límites y no-sobrediseño explícitos; revisión independiente y aprobación de Douglas. Si falta cualquiera: NEEDS_WORK o BLOCKED, no autorización de I1.

GATE 2 / Advisor: CA-001, CA-003, CA-012 y trazabilidad pasan con fixtures sintéticas; los NO DETERMINABLE se conservan; no hay ejecución irreversible ni secretos. PASS técnico sólo habilita revisión del siguiente gate.

GATE 3 / Taller y core: CA-002, CA-004…CA-011, CA-016…CA-020 reproducibles; bloqueo fail-closed, reanudación, hash, circuit breaker, contadores y revisión independiente probados. Una condición de identidad, autorización, datos o política ausente = BLOCKED.

GATE Frappe: CA-013/014 pasan con registro de versión, fecha, entorno y resultado; `v16.53.0` sigue candidato hasta validación; core pasa sin Frappe.

GATE piloto: autorización específica, datos sintéticos, alcance y límites definidos, comparación equivalente, evidencia reproducible, revisión independiente y decisión humana separada. Producto 02, producción y publicación permanecen bloqueados.

Gate de decisión: ADOPTAR sólo con evidencia suficiente y baseline; ADAPTAR si el valor es prometedor pero hay defectos/ajustes acotados; DETENER si no se demuestra valor, seguridad, trazabilidad o economía, o si persisten preguntas críticas sin owner.

## 12. Recomendación final

Aprobar esta solución como diseño condicionado para el siguiente gate: adoptar la alternativa híbrida C, mantener D como salida segura, iniciar sólo I1 después de la aprobación de I0 y reservar la selección de runtime/proveedor para un spike autorizado. El principio rector es: contrato neutral primero, una vertical verificable después, adaptador Frappe aislado sólo cuando exista evidencia, y ninguna señal técnica se presenta como autoridad humana.

Este documento no modifica repositorio ni GitHub y no autoriza ninguna implementación.