# Bottega 2.0 — Product Brief y requisitos verificables

Estado: APPROVED_GATE_0 para el contrato de I0; no autoriza diseño de I1, implementación, PoC, release, publicación ni producción.
Fecha de elaboración: 2026-10-26 (CST, UTC-06:00).
Propietario de la decisión final: Douglas.

## 1. Resumen ejecutivo

Bottega 2.0 será un asesor y sistema autónomo gobernado para producir software con menor tiempo, costo y retrabajo, manteniendo la decisión humana en los puntos de autoridad. El Incremento 0 no construye esas capacidades: fija el contrato de producto, sus límites, lenguaje, evidencia y gates para que los incrementos posteriores puedan evaluarse sin confundir asistencia con autorización.

El producto debe poder operar en tres modos complementarios:

- Advisor: ayuda a convertir una necesidad en decisiones, alternativas, requisitos, riesgos y próximos pasos; no ejecuta cambios irreversibles.
- Taller: coordina trabajo de construcción por etapas, un responsable por etapa, dependencias explícitas y evidencia reproducible.
- Auditor: inspecciona requisitos, estados, artefactos, trazabilidad, guardrails y evidencia; informa PASS, NEEDS_WORK o BLOCKED sin aprobar por sí solo release o publicación.

La autonomía es gobernada: puede preparar, ejecutar acciones autorizadas y reanudar trabajo según políticas declaradas, pero no puede aceptar humanamente el resultado, hacer release, publicar ni operar en producción por su propia autoridad.

## 2. Problema y resultado esperado

### Problema

El método actual ya describe etapas, roles y gates, pero Bottega 2.0 necesita un contrato único que evite:

- comenzar implementación antes de aprobar requisitos, solución, UX y arquitectura;
- presentar una señal técnica como si fuera una autorización de release o publicación;
- mezclar el core neutral con decisiones específicas de Frappe;
- reintentar o cambiar de proveedor sin una política explícita;
- aceptar evidencia no reproducible, métricas sin denominador o fixtures como evidencia de producto;
- usar Producto 02 o datos institucionales como requisito del nuevo producto;
- autoaplicar retrospectivas o cambios de gobernanza.

### Resultado esperado del Incremento 0

Un paquete coherente, trazable y revisable de forma independiente que permita a una persona responder, con evidencia:

1. qué problema resuelve Bottega 2.0 y para quién;
2. qué puede y no puede hacer cada modo;
3. qué decisiones siguen siendo humanas;
4. qué requisitos se probarán, cómo y con qué evidencia;
5. cómo se separan PRODUCT_PASS, RELEASE_READY_CONDITIONAL y PUBLICATION_AUTHORIZED;
6. cuándo una iniciativa puede avanzar al siguiente gate;
7. qué afirmaciones son hechos, supuestos, preguntas o NO DETERMINABLE.

## 3. Fuentes y evidencia consultada

Fuentes primarias públicas consultadas el 2026-10-26:

- Issue #1, objetivo, decisiones, límites y gates: https://github.com/untaldouglas/Bottega/issues/1
- Issue #3, contrato de producto, criterios y fuera de alcance: https://github.com/untaldouglas/Bottega/issues/3
- README del repositorio: https://github.com/untaldouglas/Bottega/blob/main/README.md
- Estado del proyecto: https://github.com/untaldouglas/Bottega/blob/main/ESTADO-PROYECTO.md
- Guía canónica de uso: https://github.com/untaldouglas/Bottega/blob/main/GUIA-DE-USO.md
- Glosario: https://github.com/untaldouglas/Bottega/blob/main/GLOSSARY.md
- Kit operativo: https://github.com/untaldouglas/Bottega/tree/main/kit
- Validación publicada del kit: https://github.com/untaldouglas/Bottega/blob/main/kit/VALIDATION.md
- Requisitos de app01, usado sólo como aprendizaje de especificación: https://github.com/untaldouglas/Bottega/blob/main/app01/docs/01-product-requirements.md
- PR #5: permanece draft y no autoriza merge: https://github.com/untaldouglas/Bottega/pull/5

Evidencia observada del repositorio:

- README: método por etapas, seis roles, aprobación humana por gate y `app01` como ejemplo probado.
- GUIA-DE-USO: flujo Necesidad → requisitos → solución → UX → arquitectura → implementación → fidelidad UX → revisión → decisión humana; Raffaello sólo después de `READY_FOR_VALIDATION`.
- Kit: `PROJECT-BRIEF.yaml`, `ACCEPTANCE-MANIFEST.yaml`, `REVIEW-PACKET.md`, `WORKFLOW-STATE.json` y manifiestos de runs; hashes inmutables y trazabilidad requisito → prueba → evidencia.
- Kit: estados independientes `PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL` y `PUBLICATION_AUTHORIZED`; el último exige autorización institucional explícita.
- Kit: el primer HTTP 429 abre circuit breaker; fallback sólo si `authorization.fallback_allowed: true`.
- PR #5: pruebas y fixtures `P02_*` descritas como sintéticas; el PR está abierto en draft y explícitamente no debe fusionarse.

## 4. Actores y trabajos críticos

| Actor | Trabajo crítico | Autoridad / límite |
|---|---|---|
| Director / propietario (Douglas) | Define alcance, autoriza gates, decide ADOPTAR/ADAPTAR/DETENER, release y publicación | Autoridad final; no delegable al sistema |
| Usuario de Advisor | Explica una necesidad y obtiene opciones, preguntas, riesgos y contrato verificable | Puede aceptar o rechazar una propuesta; no se presume autorización |
| Operador de Taller | Inicia y supervisa una iniciativa con un brief y dependencias | Sólo ejecuta dentro de autorizaciones declaradas |
| Revisor de Auditor | Comprueba coherencia, trazabilidad, guardrails y evidencia | Emite resultado de revisión; no convierte PASS en publicación |
| Bot de etapa | Produce un artefacto delimitado | Un Bot por etapa; no se auto-revisa |
| Proveedor/modelo | Ejecuta una tarea autorizada | No decide fallback ni cambios de alcance |
| Repositorio/GitHub | Conserva cambios, issues, PR y checks | No es autorización institucional por sí mismo |
| Sistema Bottega | Orquesta estados, políticas, evidencia y reanudación | Fail-closed ante políticas ausentes o inválidas |

## 5. Vocabulario de dominio

- Gate: punto de control con criterios explícitos que autoriza avanzar o exige corrección.
- Evidencia: salida reproducible que demuestra una acción, prueba o decisión.
- Baseline: estado de referencia documentado contra el cual se comparan cambios.
- Core neutral: capacidades del producto que no requieren Frappe ni otro proveedor/plataforma específico.
- Golden Path: camino recomendado para un tipo de producto; en este contrato, Frappe v16 para productos nuevos, sin convertirlo en dependencia del core.
- Autonomía gobernada: ejecución automática limitada por autorización, alcance, políticas, auditoría y gates; nunca autoridad humana implícita.
- Producto terminado: producto con `PRODUCT_PASS`; no implica `RELEASE_READY_CONDITIONAL` ni `PUBLICATION_AUTHORIZED`.
- Paquete de revisión: Summary → Evidence → Merge Danger.
- Retrospectiva: actividad posterior al cierre humano que propone mejoras; no reabre el veredicto ni se autoaplica.

## 6. Hechos, supuestos y preguntas abiertas

### 6.1 Hechos verificados

H1. El objetivo aprobado es reducir tiempo, costo y retrabajo sin trasladar aceptación humana, release, publicación o producción a la autonomía.

H2. Las líneas protegidas son Frappe v16 para productos nuevos, `v16.53.0` como baseline candidato sujeto a validación y core neutral de plataforma.

H3. Los modos aprobados son Advisor, Taller y Auditor.

H4. El flujo existente exige aprobación humana por gate y una revisión independiente; quien implementa no se revisa a sí mismo.

H5. El kit exige datos sintéticos, preflight no destructivo, evidencia con hash y estados de decisión independientes.

H6. Producto 02 permanece en stand by y no debe modificarse, migrarse ni usarse como runtime requerido.

H7. El repositorio público y el PR #5 no son autorización para fusionar, publicar ni ejecutar en producción.

H8. `app01` es evidencia de aprendizaje sobre especificación y validación local; no demuestra el desempeño de Bottega 2.0.

### 6.2 Supuestos que deben validarse

S1. Una misma iniciativa puede tener artefactos locales y referencias GitHub, siempre que el expediente separe datos sintéticos de datos operativos.

S2. El Director podrá definir el alcance, owner, organización, clasificación de datos, autorizaciones y gates antes de iniciar un run.

S3. Los proveedores podrán devolver estado, logs y evidencia suficiente sin exponer secretos.

S4. La interfaz podrá mostrar una razón explícita cuando una acción requiera aprobación humana o sea bloqueada.

S5. El baseline Frappe `v16.53.0` será instalable y compatible con el producto piloto; esto es una hipótesis, no un hecho.

### 6.3 Preguntas abiertas / NO DETERMINABLE

P1. NO DETERMINABLE: definición cuantitativa de “menor tiempo, costo y retrabajo”; no hay baseline comparativo ni denominadores históricos publicados.

P2. NO DETERMINABLE: límites máximos de tamaño, duración, concurrencia y costo por iniciativa.

P3. NO DETERMINABLE: mecanismo exacto de identidad, autenticación y autorización del operador en la futura interfaz.

P4. NO DETERMINABLE: lista completa de proveedores soportados y política de compatibilidad entre versiones.

P5. NO DETERMINABLE: conjunto de capacidades Frappe que compondrá el Golden Path más allá de la línea v16 y el baseline candidato.

P6. NO DETERMINABLE: política de retención y borrado de expedientes operativos en una futura instalación multiusuario.

P7. NO DETERMINABLE: umbrales de adopción para decidir ADOPTAR, ADAPTAR o DETENER.

Estas preguntas no se rellenan con métricas inventadas; deben resolverse en una decisión posterior con owner, fecha y evidencia.

## 7. Alcance del Incremento 0

### Incluido

- Product Brief y vocabulario compartido.
- Contrato de Advisor, Taller y Auditor.
- Política de autonomía gobernada y límites fail-closed.
- Estados, gates, dependencias y responsables.
- Requisitos funcionales y no funcionales del producto futuro.
- Trazabilidad requisito → prueba → evidencia.
- Criterios observables y casos límite.
- Métricas candidatas con denominadores explícitos.
- Riesgos, supuestos y preguntas abiertas.
- Roadmap de incrementos posteriores.

### Fuera de alcance

- Implementar Advisor, runner autónomo o Auditor.
- Instalar o configurar Frappe.
- Ejecutar el piloto de Producto 03.
- Modificar o migrar Producto 02.
- Usar datos reales, institucionales o secretos.
- Cambiar GitHub, fusionar el PR #5 o proteger ramas como parte de este entregable.
- Autorizar release, publicación, despliegue o producción.
- Seleccionar arquitectura final, esquema técnico definitivo o proveedor definitivo.
- Autoaplicar retrospectivas, cambios de skills o reglas de gobernanza.

## 8. Requisitos funcionales

RF-001 — Modos explícitos. El sistema deberá ofrecer Advisor, Taller y Auditor como modos distinguibles, con propósito, permisos, salida y límites visibles.

RF-002 — Advisor. Dada una necesidad, el sistema deberá producir preguntas faltantes, problema, actores, trabajos, alcance, supuestos, riesgos, requisitos y criterios de aceptación; deberá marcar lo no verificable como NO DETERMINABLE.

RF-003 — Taller. El sistema deberá representar una iniciativa con owner, alcance, datos permitidos, riesgos, gates, autorizaciones, dependencias, estado y artefactos esperados.

RF-004 — Auditor. El sistema deberá verificar la presencia, coherencia y vínculo entre requisitos, pruebas, evidencia, hashes, estados y autorizaciones; deberá emitir PASS, NEEDS_WORK o BLOCKED con razones.

RF-005 — Gates. El sistema deberá impedir avanzar a una etapa si la predecesora no está aprobada y la evidencia requerida no está disponible.

RF-006 — Un Bot por etapa. El sistema deberá conservar un único responsable de Bot por etapa y prohibir la auto-revisión del implementador.

RF-007 — Trazabilidad. Cada requisito deberá poder enlazarse a uno o más criterios, prueba, evidencia, propietario y resultado.

RF-008 — Estados separados. El sistema deberá mantener independientes `PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL` y `PUBLICATION_AUTHORIZED`.

RF-009 — Autorización humana. El sistema deberá requerir aprobación explícita del responsable para aceptar producto, autorizar release, publicar o ejecutar producción; un PASS técnico no bastará.

RF-010 — Autonomía gobernada. Antes de ejecutar una acción el sistema deberá comprobar alcance, autorización, datos permitidos, política del proveedor y condición del gate; si una condición no es demostrable, deberá detenerse y escalar.

RF-011 — Reanudación. El sistema deberá poder reanudar una iniciativa desde un estado y manifiesto verificables, sin repetir silenciosamente una acción ya contabilizada.

RF-012 — Contadores separados. El expediente deberá diferenciar `delivery_attempt`, `provider_retry`, `validation_attempt` y `operational_cleanup`.

RF-013 — Circuit breaker. El primer HTTP 429 deberá detener el intento; sólo podrá usarse fallback si el brief declara `fallback_allowed: true`; si no, el estado será bloqueado/escalado.

RF-014 — Evidencia inmutable. Los manifiestos de evidencia deberán conservar hash y cualquier corrección deberá crear un nuevo intento, no editar el anterior.

RF-015 — Privacidad. El sistema deberá mantener datos sintéticos por defecto y evitar imprimir o incluir secretos en artefactos, logs o contextos de build.

RF-016 — Frappe desacoplado. El sistema deberá poder expresar reglas del core sin requerir Frappe; el Golden Path Frappe v16 deberá vivir como perfil o camino de producto separado.

RF-017 — Baseline candidato. El sistema deberá registrar `v16.53.0` como baseline candidato, con resultado de validación y fecha; nunca deberá tratarlo como `latest` permanente sin evidencia.

RF-018 — Retrospectiva gobernada. El sistema podrá producir propuestas de mejora, pero no deberá aplicarlas ni modificar perfiles, skills, CI o reglas sin una iniciativa y gate separados.

RF-019 — Separación de Producto 02. El sistema deberá rechazar o bloquear acciones que modifiquen o migren Producto 02 dentro de este alcance.

RF-020 — Revisión independiente. El expediente no podrá cerrarse como producto terminado sin una revisión independiente y un resultado PASS; PASS no autoriza publicación.

RF-021 — Patch calificado. El perfil Frappe v16 deberá seleccionar desde fuentes oficiales una tupla completa reproducible, evaluar licencias, advisories, SBOM y procedencia, y exigir aceptación, backup, restore, rollback y comparación contra patches posteriores; `v16.53.0` permanecerá candidato hasta validar todo el contrato.

## 9. Requisitos no funcionales

RNF-001 — Trazabilidad completa. El 100% de los requisitos requeridos en una iniciativa deberá tener criterio, prueba planeada, owner y referencia de evidencia antes del gate correspondiente.

RNF-002 — Determinismo. Con el mismo expediente, versión y entradas, las validaciones deberán producir el mismo resultado o declarar la fuente de variabilidad.

RNF-003 — Fail-closed. La ausencia, invalidez o ambigüedad de autorización, alcance, política o evidencia deberá bloquear la acción, no inferir permiso.

RNF-004 — Auditabilidad. Toda transición de estado deberá registrar actor, timestamp, motivo, referencia al artefacto y resultado.

RNF-005 — Reproducibilidad. Una persona autorizada deberá poder repetir las pruebas declaradas usando datos sintéticos y obtener evidencia comparable.

RNF-006 — Seguridad. No se deberán revelar secretos, tokens, credenciales, rutas privadas ni datos institucionales en artefactos públicos o mensajes de estado.

RNF-007 — Neutralidad de plataforma. Las reglas de dominio del core no deberán depender de APIs o modelos de datos de Frappe.

RNF-008 — Reanudabilidad. Un fallo o detención deberá conservar el estado previo y permitir continuar sin duplicar efectos autorizados.

RNF-009 — Separación de decisiones. Ningún estado técnico deberá sobrescribir o implicar automáticamente una decisión de release, publicación o producción.

RNF-010 — Comprensibilidad. Cada bloqueo deberá indicar condición incumplida, evidencia esperada y responsable de resolverlo.

RNF-011 — Interoperabilidad documental. El expediente deberá poder exportarse o revisarse sin depender de una sesión viva del proveedor de IA.

RNF-012 — Operación segura. Preflight, auditoría y gate check deberán ser no destructivos por defecto.

## 10. Casos límite y políticas

- Brief sin owner, datos permitidos o autorización: BLOCKED; no se inicia ejecución.
- Requisito sin criterio observable: NEEDS_WORK; no cuenta como trazable.
- Evidencia con hash ausente o inconsistente: BLOCKED.
- Prueba verde sin declaración de qué detecta y qué no detecta: no cuenta como evidencia suficiente.
- Primer HTTP 429 sin fallback autorizado: circuito abierto, sin cambio silencioso de proveedor.
- Fallback autorizado pero proveedor alternativo no declarado: BLOCKED hasta registrar la política.
- `PRODUCT_PASS` con release condicionado: se conserva PRODUCT_PASS y se marca RELEASE_READY_CONDITIONAL, sin publicación.
- `PUBLICATION_AUTHORIZED` sin autorización institucional vigente: imposible; el valor debe permanecer NO.
- Revisor que también implementó la etapa: revisión inválida; debe reasignarse.
- Cierre de navegador, proveedor o proceso durante una acción: conservar intento y reanudar sólo desde manifiesto verificable.
- Solicitud de editar Producto 02, datos reales o producción: fuera de alcance y BLOCKED.
- Retrospectiva que propone cambiar sus propias reglas: registrar propuesta, no autoaplicarla.
- `v16.53.0` sin validación en el entorno del piloto: baseline candidato, no baseline aprobado.

## 11. Criterios de aceptación observables

CA-001 — Modos. Dado un expediente nuevo, una revisión de interfaz/documentación muestra los tres modos Advisor, Taller y Auditor, cada uno con objetivo, entrada, salida y límites; falta de cualquiera = FAIL. Método: inspección documental y prueba de aceptación.

CA-002 — Brief mínimo. Dado un brief sin owner, clasificación de datos o autorización, el preflight/gate check termina BLOCKED y no crea ni modifica un remoto. Método: prueba de kit con fixture sintética.

CA-003 — Advisor. Dada una necesidad incompleta, la salida contiene preguntas, hechos, supuestos, preguntas abiertas, requisitos y criterios; cualquier afirmación no sustentada aparece como NO DETERMINABLE. Método: fixture fija y revisión contra esquema.

CA-004 — Dependencias. Dada una etapa posterior con predecesora no aprobada, el sistema no la habilita y muestra la predecesora, estado y evidencia faltante. Método: prueba de transición.

CA-005 — Trazabilidad. Para cada requisito requerido, el manifiesto enlaza criterio, prueba, owner y evidencia; se rechaza un manifiesto al que le falte cualquiera. Método: validación de manifiesto con caso válido e inválido.

CA-006 — Independencia. Una revisión ejecutada por el mismo actor que implementó se marca inválida y no permite cerrar el gate. Método: fixture de identidad/rol.

CA-007 — Decisiones separadas. `PRODUCT_PASS` no cambia `RELEASE_READY_CONDITIONAL` ni `PUBLICATION_AUTHORIZED`; cada transición exige su propia evidencia y autorización. Método: prueba de estados.

CA-008 — Humano obligatorio. Una solicitud de aceptación, release, publicación o producción sin aprobación explícita queda bloqueada; ningún PASS técnico la sustituye. Método: prueba de autorización negativa.

CA-009 — 429. Ante el primer HTTP 429 el circuito se abre, el intento se detiene y se registra el motivo; sólo con `fallback_allowed: true` puede seguirse la política declarada. Método: simulación sintética del proveedor.

CA-010 — Evidencia. Un manifiesto creado con hash no puede ser editado para cambiar el resultado; una corrección exige un nuevo número de intento. Método: prueba de integridad/hash.

CA-011 — Contadores. Un retry del proveedor no incrementa delivery_attempt ni validation_attempt; el expediente conserva los cuatro contadores separados. Método: replay sintético.

CA-012 — Privacidad. En una ejecución con datos sintéticos, el escaneo de secretos no encuentra tokens y el expediente no contiene datos institucionales. Método: scan y revisión de artefactos.

CA-013 — Neutralidad. Una validación del core pasa sin instalar Frappe; la ruta Frappe se valida en un perfil separado. Método: ejecución con y sin perfil de plataforma.

CA-014 — Baseline. `v16.53.0` aparece como candidato con fecha, entorno y resultado de validación; no se acepta una etiqueta `latest` como sustituto. Método: revisión de registro de baseline.

CA-015 — Producto 02. Una acción que intenta modificar o migrar Producto 02 es rechazada y no produce cambios. Método: prueba negativa con recurso sintético `P02_*`.

CA-016 — Retrospectiva. Una propuesta de mejora queda en backlog pendiente de decisión humana y no altera configuración automáticamente. Método: prueba de flujo posterior al cierre.

CA-017 — Reanudación. Interrumpir una ejecución deja un manifiesto verificable; reanudar no duplica una acción ya completada ni pierde el motivo de interrupción. Método: prueba de interrupción/reanudación.

CA-018 — Auditor. Con un expediente válido, Auditor emite PASS; con evidencia incompleta emite NEEDS_WORK; con política prohibida o ausencia crítica emite BLOCKED, siempre con razón y referencia. Método: tres fixtures.

CA-019 — Revisión independiente. El paquete contiene Summary, Evidence y Merge Danger y no se cierra sin revisión independiente. Método: checklist de gate y revisión de expediente.

CA-020 — No autorización implícita. PR abierto, CI verde, `PRODUCT_PASS` o revisión PASS no se presentan como autorización de publicación. Método: inspección de estados y mensajes.

CA-021 — Patch calificado. Dado un candidato Frappe, la política registra fuentes oficiales, línea mayor, patch, tag, commit, dependencias, licencias, advisories, SBOM, procedencia, aceptación humana, backup/restore/rollback y comparación posterior; falta de cualquier elemento bloquea y `latest` no pasa. Método: check determinista documental más revisión del expediente de validación.

## 12. Métricas candidatas

No son objetivos aprobados todavía. Cada métrica requiere baseline y owner antes de usarse para ADOPTAR/ADAPTAR/DETENER.

| ID | Métrica | Numerador | Denominador | Fuente | Estado |
|---|---|---|---|---|---|
| M-001 | Tasa de trazabilidad completa | requisitos con criterio + prueba + evidencia válida | requisitos requeridos del run | manifiesto y auditoría | candidata; baseline NO DETERMINABLE |
| M-002 | Tasa de gates sin retrabajo posterior | gates que no reciben NEEDS_WORK por defecto evitable | gates cerrados | historial de gates | candidata; baseline NO DETERMINABLE |
| M-003 | Tiempo de ciclo | horas desde brief aprobado hasta PRODUCT_PASS | runs cerrados con PRODUCT_PASS | timestamps de expediente | candidata; baseline NO DETERMINABLE |
| M-004 | Retrabajo | intentos de corrección posteriores al primer resultado | runs cerrados | delivery/validation attempts | candidata; baseline NO DETERMINABLE |
| M-005 | Bloqueos correctamente contenidos | acciones prohibidas detenidas sin efecto | acciones prohibidas simuladas | auditoría de políticas | candidata; baseline NO DETERMINABLE |
| M-006 | Integridad de evidencia | manifiestos con hash válido | manifiestos revisados | gate check | candidata; baseline NO DETERMINABLE |
| M-007 | Reanudación sin duplicado | runs reanudados sin efectos duplicados | runs interrumpidos y reanudados | manifiestos y auditoría | candidata; baseline NO DETERMINABLE |
| M-008 | Costo por producto | costo total del run | productos con PRODUCT_PASS | registros autorizados de costo | NO DETERMINABLE en Incremento 0 |
| M-009 | Uso correcto de Frappe Golden Path | productos nuevos que validan baseline candidato | productos nuevos que declaran Frappe | registro de producto | candidata; no medir sin piloto |

No se afirma una mejora porcentual hasta ejecutar una comparación definida (Caso A/Caso B o baseline equivalente) con el mismo alcance y denominador.

## 13. Riesgos y mitigaciones

R-001. Confundir PASS técnico con autorización institucional. Mitigación: estados independientes, aceptación humana explícita y CA-007/008/020.

R-002. Autonomía demasiado amplia. Mitigación: fail-closed, permisos por modo, acciones irreversibles siempre humanas, auditoría y CA-008.

R-003. Vendor lock-in o dependencia accidental de Frappe. Mitigación: core neutral, perfil Golden Path separado y CA-013.

R-004. Fallback o retry que oculta fallas y costo. Mitigación: circuit breaker al primer 429, contadores separados y CA-009/011.

R-005. Evidencia sintética presentada como evidencia de producto. Mitigación: clasificación explícita de datos, fuente y entorno en manifiestos; etiqueta NO DETERMINABLE cuando corresponda.

R-006. Producto 02 reabierto por dependencia histórica. Mitigación: fuera de alcance, bloqueo explícito y CA-015.

R-007. Métricas sin baseline. Mitigación: denominadores obligatorios, estado candidata y prohibición de porcentajes inventados.

R-008. Revisión insuficientemente independiente. Mitigación: owner distinto, identidad registrada y CA-006/019.

R-009. Reanudación que duplica efectos. Mitigación: manifiestos inmutables, idempotencia observable y CA-010/017.

R-010. Cambios de gobernanza autoaplicados por retrospectiva. Mitigación: backlog separado y aprobación humana.
R-011. Patch Frappe no reproducible o actualización sin recuperación probada. Mitigación: política de patch calificado, tupla completa, procedencia, SBOM, backup/restore/rollback y comparación posterior.

## 14. Decisiones protegidas

D-001. Modos Advisor, Taller y Auditor. Responsable de cambio: Douglas. Evidencia requerida: revisión del contrato y criterios CA-001/003/018.

D-002. Frappe v16 como línea oficial de productos nuevos. Responsable: Douglas. No implica dependencia del core. Evidencia: validación del Golden Path.

D-003. `v16.53.0` como baseline candidato sujeto a validación. Responsable: Douglas. No usar como `latest` permanente.

D-004. Core neutral de plataforma. Responsable: Douglas. Un cambio requiere justificar el impacto en independencia del dominio.

D-005. Autonomía gobernada sin aceptación humana, release, publicación ni producción autónomos. Responsable: Douglas; no puede relajarse por un PASS técnico.

D-006. Producto 02 permanece en stand by. Responsable: Douglas. No se modifica ni migra en este alcance.

D-007. Datos reales e integraciones institucionales fuera de alcance. Responsable: Douglas.

D-008. Retrospectiva propone y no autoaplica. Responsable: persona autorizada; aprobación final de Douglas.

D-009. Un patch Frappe sólo puede promocionarse mediante la política de patch calificado; `v16.53.0` es candidato hasta validación completa. Responsable: Douglas.

## 15. Roadmap condicionado

I0 — Contrato y requisitos: este documento, revisión independiente y aprobación de GATE 1.

I1 — Bottega Advisor: sólo después de I0 aprobado; validar RF-001/002 y preguntas abiertas de identidad/autorización.

I2 — Core autónomo y reanudable: sólo después del diseño; validar RF-005 a RF-015 y RNF-002 a RNF-012.

I3 — Golden Path Frappe v16: validar instalación y compatibilidad del baseline candidato sin contaminar el core.

I4 — Piloto controlado con un producto nuevo (Producto 03): datos sintéticos, autorización específica, comparación y revisión independiente.

I5 — Medición y decisión ADOPTAR, ADAPTAR o DETENER: sólo con métricas con baseline, denominador y evidencia suficiente.

Todos los incrementos posteriores requieren sus propios gates. Este documento no los autoriza.

## 16. Gate de aprobación del Incremento 0

Para recomendar GATE 1 APROBADO deben verificarse todos los puntos:

- [ ] Hechos, supuestos, preguntas y decisiones están separados.
- [ ] Cada requisito tiene criterio observable y método de prueba.
- [ ] Los tres modos tienen contrato y límites explícitos.
- [ ] La política de autonomía es fail-closed y conserva autoridad humana.
- [ ] Los estados de producto, release y publicación son independientes.
- [ ] Frappe v16 es Golden Path separado del core; `v16.53.0` es candidato, no latest.
- [ ] Producto 02, datos reales, producción, PoC y cambios GitHub están fuera de alcance.
- [ ] Las métricas tienen numerador, denominador, fuente y estado; no hay porcentajes sin evidencia.
- [ ] Se ejecutó una revisión independiente que devuelva PASS, NEEDS_WORK o BLOCKED.
- [ ] Douglas emite la aprobación final del paquete.

Decisión del gate: NO DETERMINABLE hasta completar la revisión independiente y la aprobación de Douglas. El documento está listo para revisión; no autoriza implementación.

## 17. Matriz de trazabilidad resumida

| Necesidad / decisión | Requisitos | Criterios |
|---|---|---|
| Tres modos gobernados | RF-001–004 | CA-001, CA-003, CA-018 |
| Flujo por etapas y gates | RF-005–007, RNF-001–005 | CA-004, CA-005, CA-019 |
| Autoridad humana separada | RF-008–010, RNF-003, RNF-009 | CA-007, CA-008, CA-020 |
| Autonomía reanudable y segura | RF-010–015, RF-017–018 | CA-009–012, CA-016–017 |
| Core neutral y Golden Path | RF-016–017, RNF-007 | CA-013–014 |
| Patch Frappe reproducible y recuperable | RF-021, RNF-002–006, RNF-012 | CA-021 |
| Producto 02 en stand by | RF-019 | CA-015 |
| Revisión y cierre independientes | RF-020, RNF-004–006 | CA-018–019 |
| Métricas con evidencia | RNF-001–005 | M-001–M-009; CA-005, CA-010 |

## 18. Nota de no implementación

Este artefacto contiene decisiones de producto, requisitos y criterios de aceptación. No selecciona arquitectura final, no escribe código, no modifica GitHub y no ejecuta una PoC, instalación, release o producción.
