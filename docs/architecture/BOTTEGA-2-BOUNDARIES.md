# Bottega 2.0 — Límites arquitectónicos, seguridad y pruebas

Estado: PROPUESTA PARA REVISIÓN INDEPENDIENTE (NEEDS_WORK hasta decisión de Douglas)
Fecha: 2026-10-26 (CST, UTC-06:00)
Propietario de decisión: Douglas
Alcance: diseño del Incremento 0; no implementación, instalación, PoC, GitHub, producción ni datos reales.

Este documento transforma los artefactos 01, 02 y 03 y los issues públicos #1, #3 y #4 en límites verificables para un implementador posterior. No declara que exista runtime Bottega 2.0 ni que Frappe haya sido instalado o validado.

## 1. Entradas, hechos y decisiones protegidas

Fuentes inspeccionadas:

- `../product/BOTTEGA-2-REQUIREMENTS.md`: RF-001…RF-020, RNF-001…RNF-012, CA-001…CA-020, riesgos y preguntas P1…P7.
- `../product/BOTTEGA-2-SOLUTION-ROADMAP.md`: alternativa híbrida C recomendada, D como salida segura, core neutral, adaptador Frappe separado e incrementos I0…I5.
- `../product/BOTTEGA-2-UX-SERVICE-DESIGN.md`: contratos UX de Advisor/Taller/Auditor, estados, bloqueos, pausa/reanudación, evidencia y decisiones humanas.
- Repositorio público `https://github.com/untaldouglas/Bottega`, issues #1, #3 y #4, leídos sin modificar.

Hechos que el diseño debe preservar:

1. Los modos son Advisor, Taller y Auditor.
2. La autonomía es gobernada; no acepta humanamente, hace release, publica ni opera en producción por autoridad propia.
3. `PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL` y `PUBLICATION_AUTHORIZED` son estados de decisión distintos.
4. Producto 02, datos institucionales, secretos, producción y cambios de GitHub quedan fuera de este alcance.
5. Frappe v16 es Golden Path para productos nuevos; `v16.53.0` es baseline candidato, no `latest` ni baseline aprobado.
6. La revisión del implementador por sí mismo no es independiente.
7. Primer HTTP 429: abre circuito y detiene el intento; fallback sólo con `fallback_allowed: true` y proveedor/capacidad declarados.
8. Manifiestos y eventos históricos son append-only; una corrección crea un nuevo intento.
9. Todas las métricas de valor siguen sin baseline cuantitativo; no se inventan umbrales.

Decisión de arquitectura: alternativa C, “contrato neutral + adaptadores pequeños + kit documental”, con alternativa D (“no construir todavía”) como salida segura si faltan decisiones P2/P3/P4/P5/P6/P7 o autorización de piloto.

## 2. Topología y límites de componentes

La dependencia permitida apunta hacia el dominio; ningún componente externo puede introducir una regla de autoridad en el core.

```
[UI / API / exportación]
          |
[Aplicación: casos de uso + autorización de comando]
          |
[Core neutral: entidades, invariantes, políticas, transición]
          |                 \
[Puertos de persistencia]   [Puertos de ejecución/evidencia]
          |                         |
[Adapter store] [Adapter Frappe v16] [Adapter proveedor/modelo]
          |                         |
[backup/restore] [sandbox] [secret manager / red]
```

### 2.1 Core neutral

Responsabilidad: representar el contrato y decidir si una transición es válida con entradas ya autenticadas y políticas explícitas. No conoce Frappe, Bench, HTTP, UI, GitHub, SQL, un SDK de modelo, secretos ni rutas de filesystem.

Componentes conceptuales:

- `Initiative`: alcance, owner, clasificación de datos, exclusiones, roles, política y estado.
- `Stage`: trabajo delimitado, un Bot responsable, predecesoras, permisos y artefactos esperados.
- `Requirement` y `RequirementLink`: requisito → criterio → prueba → evidencia → owner → resultado.
- `Run` y `Attempt`: ejecución y contadores separados.
- `Artifact` y `EvidenceRef`: salida, origen, entorno, timestamp, hash y relación.
- `Authorization` / `PolicyDecision`: actor, alcance, datos permitidos, operación, proveedor permitido, expiración y decisión explícita.
- `Review`: actor independiente, identidad, alcance del snapshot, veredicto y razones.
- `DecisionState`: los tres estados de producto/release/publicación, independientes.
- `DomainEvent`: transición append-only, actor, reloj, motivo, versión de esquema y referencias.
- `CircuitState`: cerrado, abierto o, sólo por política explícita, medio de recuperación; el primer 429 abre.

Invariantes del core:

- ausencia, invalidez o ambigüedad de autorización, alcance, política, dependencia o evidencia = `BLOCKED`;
- una etapa no habilita si la predecesora no está aprobada y su evidencia requerida no está disponible;
- un actor que implementó una etapa no puede cerrarla como revisor independiente;
- ningún PASS técnico muta cualquier estado humano posterior;
- un evento confirmado no se edita ni borra;
- un `provider_retry` no incrementa `delivery_attempt` ni `validation_attempt`;
- cualquier corrección tiene `attempt_no` nuevo y conserva el original;
- retrospectiva produce propuesta, nunca mutación automática de configuración o gobernanza;
- clasificación `SYNTHETIC` nunca se presenta como desempeño de producto.

### 2.2 Aplicación / orquestación

Responsabilidad: convertir comandos autenticados en llamadas al core, cargar el snapshot, validar política antes y después de efectos externos, coordinar idempotencia, persistir eventos y devolver resultados comprensibles.

Casos de uso mínimos posteriores a I0:

- `CreateInitiative`, `PrepareAdvisor`, `OpenStage`;
- `StartRun`, `RecordProviderRetry`, `RecordValidation`, `RecordCleanup`;
- `PauseInitiative`, `ResumeFromManifest`;
- `CreateEvidenceManifest`, `ReviewSnapshot`;
- `RequestHumanDecision`, `RecordHumanDecision`;
- `ExportCaseFile`, `BackupCaseFile`, `RestoreCaseFile`.

Cada comando recibe `actor`, `correlation_id`, `idempotency_key`, `scope`, `policy_snapshot` y `expected_revision`. Un comando mutante no se considera exitoso hasta que su evento y manifiesto quedan confirmados en almacenamiento durable. Si el efecto remoto ocurrió pero la confirmación local no, el estado es `UNKNOWN/BLOCKED`, nunca “éxito” inferido.

### 2.3 Interfaces de puerto

Contratos conceptuales (los nombres son parte del diseño; el lenguaje queda pendiente):

- `CaseRepository.load(initiative_id) -> CaseSnapshot | NotFound`.
- `CaseRepository.append(expected_revision, events[]) -> CommitReceipt | Conflict`.
- `EvidenceStore.put(content, metadata) -> EvidenceRef` y `EvidenceStore.get(ref) -> bytes/metadata`; no sobrescribe una referencia existente.
- `ProviderExecutor.execute(ProviderRequest) -> ProviderOutcome`; nunca recibe autorización implícita.
- `ProviderRegistry.resolve(policy, capability, requested_version) -> EffectiveProvider` o `PolicyBlocked`.
- `Clock.now()`, `IdGenerator.next()`, `Hasher.sha256(bytes)` como dependencias inyectables para determinismo.
- `SecretRefResolver.resolve(ref) -> opaque handle`; el core sólo recibe referencias, nunca el valor secreto.
- `PlatformAdapter.validate_baseline(profile) -> PlatformValidation`; el core recibe versión/resultado/evidencia, no DocTypes.
- `BackupStore.write(snapshot_manifest, chunks) -> BackupReceipt` y `BackupStore.read(backup_id) -> VerifiedSnapshot`.

Los adaptadores deben mapear errores a un catálogo estable (`POLICY_BLOCKED`, `AUTHZ_MISSING`, `DEPENDENCY_BLOCKED`, `HASH_MISMATCH`, `PROVIDER_429`, `PROVIDER_TIMEOUT`, `PERSISTENCE_CONFLICT`, `SECRET_DETECTED`, `UNKNOWN_EFFECT`) sin filtrar tokens, prompts privados ni stack traces a la UI.

## 3. Adaptadores de plataforma

### 3.1 Adaptador Frappe / Bench

Frappe pertenece a un perfil de producto y a I3, no al dominio. El adaptador sólo traduce capacidades requeridas por el Golden Path: entorno, versión, ejecución no destructiva, artefactos de prueba, exportación de resultados y estado de instalación. No importa DocTypes o APIs en las entidades del core.

Registro mínimo de una validación futura:

- `profile_id`, `platform: frappe`, `framework_version: v16.53.0`, `bench_version: v5.31.1`;
- fecha/hora UTC, entorno declarado y fingerprint no secreto de la imagen/entorno;
- producto/sandbox y alcance de la prueba;
- resultado `PASS`, `NEEDS_WORK` o `BLOCKED`, razón y evidencia hashada;
- responsable y revisor independientes;
- estado `candidate`, `validated` o `rejected`.

`v16.53.0` y `v5.31.1` son baseline candidatos declarados por el contrato; la fecha y compatibilidad deben verificarse en I3. No se ejecutó instalación en este Incremento 0, por lo que no se afirma compatibilidad. La etiqueta `latest` nunca satisface el registro.

### 3.2 Adaptador de proveedor/modelo

El core pide una capacidad (`capability`, límites y política), no un SDK. El registro de proveedor efectivo se escribe por intento y contiene:

- `requested_provider`, `requested_model`, `effective_provider`, `effective_model`;
- versiones de SDK/API y `provider_policy_id`/versión;
- región/entorno sólo si la política lo permite, sin credenciales;
- motivo de selección o fallback (`primary`, `authorized_fallback`, `replay`, `blocked`);
- timestamp, run/attempt, capability, input/output classification;
- límites declarados y uso medido (tokens/tiempo/costo sólo si están disponibles y autorizados);
- resultado, error normalizado y hash del request/response redacted.

Un cambio de proveedor no se oculta: crea evento y registro nuevo. La UI muestra proveedor/modelo efectivo y política, nunca API key, Authorization header, prompt secreto ni contenido restringido.

## 4. Estado durable, eventos y append-only

### 4.1 Fuente de verdad

El expediente durable es la fuente de verdad; un snapshot materializado es derivado y reconstruible. Se separan:

- `CaseSnapshot`: estado actual verificable;
- `EventLog`: eventos inmutables y ordenados por `sequence_no`;
- `AttemptLog`: delivery/provider retry/validation/cleanup por separado;
- `EvidenceManifest`: referencias a bytes, hash, origen, entorno y clasificación;
- `DecisionLog`: decisiones humanas con alcance y expiración;
- `ProviderLedger`: proveedor/modelo efectivo por intento;
- `BackupManifest`: backup, cadena de hash, versión de esquema y restore test.

Commit atómico: validar comando completo contra `expected_revision`, anexar evento(s), actualizar índice/snapshot derivado y confirmar transacción. Si cualquiera falla, conservar el último estado confirmado y devolver error; no hacer “best effort” silencioso.

### 4.2 Esquema mínimo conceptual

Identificadores: `initiative_id`, `stage_id`, `run_id`, `attempt_id`, `event_id`, `evidence_id`, `review_id`, `decision_id`, `correlation_id` y `idempotency_key`, todos opacos y únicos.

Cada evento incluye `event_type`, `schema_version`, `sequence_no`, `occurred_at`, `recorded_at`, `actor_id/role`, `correlation_id`, `causation_id`, `payload_ref`, `payload_hash`, `classification` y `previous_event_hash`. El encadenamiento detecta huecos o alteraciones; no sustituye control de acceso.

La persistencia concreta (SQL/objeto/otro) es una decisión posterior detrás del puerto. Debe soportar transacción, conflicto optimista, índices por iniciativa y sequence, retención definida por P6 y exportación sin sesión viva. No se diseña multi-tenant ni event bus permanente en I0.

### 4.3 Reanudación

`ResumeFromManifest` carga snapshot + último manifiesto, comprueba hash, autorización vigente, scope, política, dependencia e idempotency key. Expone “ocurrió / no ocurrió / se repetirá / no se repetirá”. Si hash, autorización o efecto remoto son ambiguos: `BLOCKED` o `UNKNOWN_EFFECT`; no reintenta automáticamente. La transición de reanudación es nueva y conserva la interrupción original.

## 5. Autorizaciones y estados ortogonales

### 5.1 Modelo de autorización

Una autorización debe declarar explícitamente: `subject`, `role`, `action`, `resource_scope`, `data_classification`, `environment`, `provider_policy`, `expires_at`, `issued_by`, `decision_id`, `reason` y `revocation`. “Revisé”, un PASS, CI verde, PR abierto o lenguaje conversacional no son autorización.

Matriz mínima:

- Advisor: leer entrada permitida y producir propuesta; no ejecutar mutaciones irreversibles.
- Taller: ejecutar sólo stages y sandbox dentro del brief autorizado.
- Auditor: leer snapshot/evidencia y emitir veredicto; no mutar historia ni publicar.
- Director/owner: decisiones humanas de aceptación, release y publicación según alcance institucional.
- Implementador: producir artefacto; no auto-revisar.

La política se evalúa fail-closed antes de cada efecto y se registra el `policy_snapshot_id` aplicado.

### 5.2 Estados ortogonales

No usar una sola máquina de estados para mezclar ejecución y autoridad. Mantener al menos estas dimensiones:

- ejecución: `DRAFT`, `READY`, `RUNNING`, `PAUSED`, `BLOCKED`, `UNKNOWN_EFFECT`, `CLOSED`;
- revisión técnica: `NOT_REVIEWED`, `NEEDS_WORK`, `PASS`, `BLOCKED`;
- decisión de producto: `NOT_ACCEPTED`, `PRODUCT_PASS`;
- decisión de release: `NOT_READY`, `RELEASE_READY_CONDITIONAL`;
- decisión de publicación: `NOT_AUTHORIZED`, `PUBLICATION_AUTHORIZED`.

Las transiciones técnicas sólo pueden agregar evidencia a su dimensión. Cada estado humano exige actor, alcance, timestamp, razón, evidencia y autorización vigente. La UI debe mostrar las dimensiones separadas y sus consecuencias.

## 6. Reintentos, circuit breaker y presupuesto

Regla aprobada: el primer HTTP 429 abre el circuito y detiene el intento actual. No se cambia silenciosamente de modelo/proveedor.

Presupuesto por run, explícito y configurable por política (no se inventan valores globales mientras P2/P4 siga NO DETERMINABLE):

- `delivery_attempt`: cada intento de entregar/ejecutar la etapa;
- `provider_retry`: reintento interno contra el mismo proveedor, sólo si la política lo permite;
- `validation_attempt`: cada validación del artefacto;
- `operational_cleanup`: recuperación/limpieza, nunca se disfraza de delivery.

La política debe declarar máximos de intentos, duración, costo/tokens, concurrencia, tipos de error reintentables, backoff/jitter, fallback permitido y condición de cierre. Si falta cualquier límite requerido, se bloquea antes de ejecutar.

Circuit states:

- `CLOSED`: llamada permitida dentro de política.
- `OPEN`: llamada rechazada; razón y primer 429 registrados.
- `RECOVERY_PENDING`: sólo una reanudación explícita, con nueva autorización/política y prueba no destructiva, puede intentar recuperar.

El fallback requiere `fallback_allowed: true`, proveedor y capability declarados, compatibilidad de clasificación, autorización vigente y un nuevo registro de proveedor efectivo. Timeout, 5xx o error de validación no se convierten automáticamente en 429; cada taxonomía conserva su razón.

## 7. Evidence store, hashes y trazabilidad

Un `EvidenceManifest` contiene `evidence_id`, `artifact_id`, bytes/URI controlado, `sha256`, tamaño, MIME, clasificación, origen, entorno, timestamp, actor, run/attempt, requisito/criterio/prueba, resultado, `detects`, `does_not_detect`, herramienta/versión y referencias a logs redacted. El store es de sólo anexado para una referencia ya confirmada.

Reglas:

- hash calculado sobre bytes canónicos; serialización determinista para manifiestos;
- verificar hash al escribir, leer, exportar, restaurar y antes de cada gate;
- mismatch/ausencia = `BLOCKED`, conservando ambas referencias;
- corrección = nuevo artifact/evidence/attempt, nunca edición histórica;
- fixtures llevan `SYNTHETIC_FIXTURE` y “no demuestra desempeño del producto”;
- exportación contiene Summary, Evidence y Merge Danger, sin secretos ni rutas privadas;
- un resultado se considera evidencia sólo si declara qué detecta y qué no detecta.

La relación requisito → criterio → prueba → evidencia → owner → resultado debe ser consultable y validarse al 100% antes del gate que la requiera.

## 8. Aislamiento implementación/revisión

Separar tres identidades lógicas: actor que implementa, actor que ejecuta validación y actor que revisa. El sistema debe rechazar cierre si `implementer_id == reviewer_id` para la misma etapa/alcance. El Auditor lee un snapshot inmutable; no modifica evidencia ni puede convertir su PASS en decisión institucional.

Separar también:

- workspace de implementación y workspace de revisión;
- permisos de escritura de artefactos y permisos de veredicto;
- credenciales/secretos de ejecución y lectura de evidencia redacted;
- producto distribuible y expediente interno;
- branch/PR y decisión de release/publicación.

El CI es evidencia de checks del HEAD que validó; nunca autoridad de publicación. Issue, PR, merge y release deben quedar vinculados a una autorización separada.

## 9. Threat model

Activos: autorizaciones, secretos y referencias a secretos, expedientes, evidencia y hashes, identidad/roles, decisiones humanas, integridad de estados, costos y disponibilidad, artefactos públicos y cadena de supply chain.

Actores/amenazas:

- usuario no autenticado o con rol excesivo: intenta ejecutar/publicar o leer otro expediente;
- prompt/entrada/artefacto malicioso: prompt injection, instrucciones dentro de archivos o datos no confiables;
- proveedor comprometido o con fuga: devuelve contenido sensible o solicita acciones fuera de scope;
- implementador malicioso o con error: altera evidencia, se auto-revisa o amplía alcance;
- insider/revisor coludido: fabrica PASS o autorización;
- replay/doble entrega: repite mutación después de timeout;
- corrupción/ransomware: altera store o backup;
- dependencia/workflow comprometido: ejecuta supply-chain code;
- abuso de costo/429: fuerza retries, fallback o denegación de servicio;
- error de clasificación: mezcla fixture, datos reales o Producto 02.

Controles obligatorios:

- autenticación y autorización por comando/scope; deny-by-default y expiración;
- secret manager y redacción; nunca secretos en logs, exportaciones, prompts o mensajes;
- tratar todo texto/JSON importado como dato no confiable: parsear, validar esquema, renderizar como texto y nunca ejecutarlo;
- sandbox no destructivo, allowlist de comandos/rutas/red y aislamiento de procesos;
- límites de tamaño, tiempo, concurrencia y costo; circuit breaker y contadores;
- idempotency key + conflicto de revisión + manifiesto para impedir replay;
- hash/encadenamiento, backup separado y pruebas de restore;
- doble control para decisiones de release/publicación/producción;
- revisión independiente y separación de permisos;
- SCA/lockfiles/pinning de acciones por SHA cuando proceda, con due diligence de licencia;
- clasificación visible y scan de secretos antes de almacenar/exportar;
- auditoría de accesos y alertas para cambios de política, scope o proveedor.

Fuera de alcance de I0: afirmar una solución completa de identidad, multi-tenant, retención o despliegue. P3/P6 requieren ADR y decisión humana antes de I1/I2.

## 10. Estrategia TDD y pruebas negativas

La implementación futura debe empezar por tests de contrato del core, antes que adaptadores o UI. Cada test porta ID RF/RNF/CA, fixture sintética, precondición, comando, resultado esperado y evidencia esperada. Los resultados de esta sección son planificados; no se ejecutaron en I0.

Capas:

1. Tests de dominio puros: invariantes, transiciones ortogonales, permisos, dependencia, idempotencia y contadores.
2. Tests de aplicación: commit atómico, conflictos, replay, pausa/reanudación y redacción.
3. Contract tests de puertos: store, evidence, provider registry, executor y backup con fakes deterministas.
4. Tests de adaptador: Frappe/Bench y proveedores sólo en sandbox; verificar mapping, versión y errores.
5. Tests de integración: expediente completo con datos sintéticos, sin remoto destructivo.
6. Auditoría: validación de manifiestos, hashes, trazabilidad e independencia.
7. Seguridad: secret scan, autorización negativa, path/network allowlist, payloads maliciosos y supply chain.
8. UI/accessibility: teclado, foco, lector, zoom/reflow, mensajes y comprensión de estados; no confundir éxito visual con autorización.

Matriz de pruebas negativas mínima:

- brief sin owner/clasificación/autorización → `BLOCKED`, cero efecto;
- dependencia no aprobada → no habilitar etapa;
- actor implementador como revisor → revisión inválida;
- `PRODUCT_PASS` intentando publicar → `NOT_AUTHORIZED`;
- PR/CI verde intentando release → bloqueo;
- primer 429 → circuito abierto, cero fallback no autorizado;
- fallback true sin proveedor/capability declarado → bloqueo;
- timeout después de posible efecto → `UNKNOWN_EFFECT`, no replay automático;
- hash ausente/mismatch → bloqueo y nuevo intento requerido;
- retry del proveedor → no incrementar delivery/validation;
- evento duplicado/sequence conflict → rechazo sin sobrescribir;
- secret/token en entrada, log o exportación → redacción o bloqueo;
- fixture `P02_*`, dato real o producción → fuera de alcance, cero cambio;
- retrospectiva que intenta cambiar reglas → backlog, no mutación;
- snapshot/backup corrupto o de versión incompatible → restore abortado, último estado intacto;
- payload JSON con instrucciones embebidas → dato literal, nunca ejecución;
- autorización expirada/revocada → bloqueo;
- reanudación con manifiesto incompleto → bloqueo y diagnóstico accionable.

Gate de evidencia: cada test realmente ejecutado debe registrar fecha, entorno, versión, fixture, comando, resultado, log redacted y hash. “Planned/not executed” no se presenta como PASS.

## 11. Golden Path Frappe v16

El Golden Path es un perfil, no una dependencia del core:

1. Crear un sandbox aislado y un caso sintético; confirmar autorización y datos permitidos.
2. Registrar explícitamente `frappe v16.53.0` y `bench v5.31.1` como candidatos exactos, fecha y entorno.
3. Validar reproducibilidad de instalación/configuración, migración no destructiva del producto piloto y comandos permitidos, sin `latest` implícito.
4. Ejecutar tests del core sin Frappe; después tests del adaptador que comprueben mapping mínimo.
5. Capturar logs redacted, versión efectiva, resultado, hash y reviewer independiente.
6. Si instalación, compatibilidad, licencia, seguridad o evidencia fallan: `BLOCKED`/`NEEDS_WORK`; no reemplazar versión por otra sin nueva decisión.
7. No usar Producto 02, datos institucionales ni producción; el piloto futuro es Producto 03 con autorización independiente.

I0 no instala Frappe ni Bench y no afirma que la pareja de versiones sea compatible. La compatibilidad queda como hipótesis de I3.

## 12. Criterios de calificación de patch

Un patch futuro sólo califica si:

- referencia un issue, RF/RNF/CA y gate; no mezcla alcance no autorizado;
- conserva core neutral y concentra Frappe/proveedores en adaptadores;
- incluye contrato y tests antes de ampliar capacidad;
- pasa tests positivos y negativos relevantes con fixtures sintéticas;
- demuestra fail-closed, estados ortogonales, hash, append-only, idempotencia y contador correcto;
- muestra proveedor/modelo efectivo sin secretos;
- incorpora migración/rollback reversible o explica por qué no aplica;
- no usa `latest`, no toca Producto 02 ni introduce producción/integraciones institucionales;
- mantiene accesibilidad, lenguaje de autorización y exportación documental;
- incluye Summary, Evidence y Merge Danger, revisión independiente y CI sobre el HEAD del PR;
- no contiene secretos, rutas personales, evidencia operativa privada ni claims no sustentados;
- deja el gate como `PASS`, `NEEDS_WORK` o `BLOCKED` con razón, nunca “aprobado” ambiguo.

Falla automática: cualquier secreto, efecto remoto no autorizado, mutación histórica, auto-revisión, publicación implícita, dependencia de Frappe en dominio o test que sólo compruebe un fixture sin declarar alcance.

## 13. Backup, restore, rollback y exit test

### Backup

- Snapshot lógico + EventLog + EvidenceManifest + ProviderLedger + DecisionLog + esquema/versiones.
- Cifrado en reposo y tránsito según política futura; claves fuera del backup.
- Manifest con `backup_id`, fecha, origen, rango de sequence, hashes, clasificación y versión.
- Copias con separación de permisos y retención pendiente de P6.
- Verificación de hash y lectura de muestra; nunca exponer secretos.

### Restore

- Restaurar primero en sandbox aislado y de sólo lectura.
- Verificar cadena de eventos, hashes, referencias, esquema y clasificación.
- Reconstruir snapshot y comparar estado/sequence/decisiones con el manifest.
- Ejecutar suite de smoke y pruebas negativas; registrar evidencia.
- Promover sólo con autorización humana explícita y plan de reversión.
- Si falla cualquier verificación: abortar sin alterar la fuente ni declarar restore exitoso.

### Rollback

Preferir rollback lógico: detener ejecución, conservar eventos, revertir a snapshot confirmado anterior sólo mediante una nueva decisión registrada. Para cambios de esquema, migración reversible con backup probado y compatibilidad de lectura. Nunca borrar historia ni “corregir” hash.

### Exit test

Una iniciativa puede salir a un gate humano sólo si: expediente exportable sin sesión viva; trazabilidad completa; secretos scan limpio; hashes verificados; todos los efectos declarados; contadores coherentes; proveedor/modelo efectivo registrado; revisión independiente; decisiones ortogonales; backup y restore test documentados cuando apliquen; y no quedan preguntas críticas sin owner. El exit test no autoriza release, publicación ni producción.

## 14. Límites de MCP y producción

MCP, si se usa en un incremento posterior, es sólo transporte/adaptador de herramientas, no fuente de autoridad. Cada herramienta debe tener schema estricto, allowlist, scope, actor, idempotency key, timeout, límites de payload, clasificación y registro de resultado. No aceptar una instrucción MCP como autorización humana ni permitir que el servidor decida fallback, publicación o cambio de alcance. Entradas y resultados son no confiables y deben validarse/redactarse.

Producción está fuera de I0–I3 y requiere un gate específico posterior: identidad institucional, doble control, backup/restore probado, rollback, observabilidad, límites de blast radius, runbook, incident response, aprobación de release y `PUBLICATION_AUTHORIZED` separado. Sin ello, cualquier solicitud de producción = `BLOCKED` sin efecto.

## 15. ADR candidatos

ADR-001 — Core neutral y puertos/adaptadores.
Decisión propuesta: dominio no conoce Frappe, Bench, proveedor, UI ni persistencia concreta. Trade-off: más contratos iniciales; beneficio: sustitución y pruebas sin plataforma. Reversibilidad: alta antes de adoptar contratos públicos.

ADR-002 — Event log append-only + snapshots derivados.
Decisión propuesta: eventos/manifiestos inmutables, snapshot reconstruible, conflicto optimista. Trade-off: más almacenamiento/consultas; beneficio: auditoría y reanudación. Requiere decidir retención P6.

ADR-003 — Estados de ejecución, revisión y decisión ortogonales.
Decisión propuesta: no colapsar PASS técnico con release/publicación. Trade-off: UI y modelo más explícitos; beneficio: evita autorización implícita. Cambio protegido por Douglas.

ADR-004 — Circuit breaker al primer 429 y contadores separados.
Decisión propuesta: detener, registrar y sólo fallback autorizado. Trade-off: menor disponibilidad inmediata; beneficio: costo/falla visible y controlable.

ADR-005 — Evidence store hashado y manifiestos canónicos.
Decisión propuesta: SHA-256 sobre bytes canónicos, append-only y nuevo attempt para corrección. Trade-off: disciplina de serialización; beneficio: integridad/reproducibilidad.

ADR-006 — Registro del proveedor/modelo efectivo.
Decisión propuesta: registrar selección efectiva, política y versión por intento, sin secretos. Trade-off: más metadata; beneficio: auditabilidad y costo visible.

ADR-007 — Independencia de implementación y revisión.
Decisión propuesta: identidades, permisos y workspaces separados; rechazo de auto-revisión. Trade-off: coordinación adicional; beneficio: gate creíble.

ADR-008 — Frappe v16 como perfil Golden Path.
Decisión propuesta: `v16.53.0`/Bench `v5.31.1` candidatos exactos, validables en I3, no `latest`, fuera del core. Trade-off: adaptador adicional; beneficio: evita lock-in.

ADR-009 — Datos sintéticos por defecto y Producto 02 aislado.
Decisión propuesta: clasificación obligatoria, scan y bloqueos. Trade-off: no medir desempeño real en I0; beneficio: privacidad y reversibilidad.

ADR-010 — Backup/restore como condición de salida operativa.
Decisión propuesta: no promover una etapa operativa sin restore verificable y rollback documentado. Trade-off: tiempo antes de piloto; beneficio: limitar pérdida y blast radius.

Los ADR son candidatos, no decisiones aprobadas por este documento. Cada uno requiere owner, fecha, alcance, evidencia y decisión de Douglas donde indique “protegido”.

## 16. Gate de este diseño

Revisión independiente debe comprobar:

- [ ] Componentes, puertos, adaptadores y dependencias están definidos.
- [ ] Estado durable, append-only, hash, reanudación e idempotencia tienen reglas.
- [ ] Autorizaciones y estados técnicos/humanos son ortogonales y fail-closed.
- [ ] Reintentos, 429, fallback y proveedor/modelo efectivo son observables.
- [ ] Threat model y controles negativos cubren secretos, replay, prompt injection, supply chain y costo.
- [ ] TDD, tests negativos y distinción planned/executed son explícitos.
- [ ] Golden Path Frappe v16 y baseline candidato están separados del core; no se afirma validación.
- [ ] Criterios de patch, backup/restore/rollback y exit test son ejecutables.
- [ ] MCP y producción permanecen limitados y bloqueados sin gates posteriores.
- [ ] ADR candidatos tienen trade-offs y reversibilidad.
- [ ] El documento no implementa, instala, ejecuta PoC, modifica GitHub ni toca datos sensibles.

Veredicto de Incremento 0: NEEDS_WORK hasta revisión independiente y decisión humana de Douglas. Este documento habilita una conversación de diseño posterior; no autoriza I1, Frappe, proveedor, piloto, release, publicación ni producción.
