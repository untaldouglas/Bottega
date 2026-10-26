# Bottega 2.0 — Diseño de servicio UX: Advisor, Taller y Auditor

Estado: PROPUESTA PARA REVISIÓN INDEPENDIENTE
Decisión UX: NEEDS_WORK hasta completar revisión independiente y decisión humana de Douglas.
Fecha: 2026-10-26 (CST, UTC-06:00)
Propietario de diseño: Donatello (UX)
Alcance: Incremento 0; diseño de servicio y experiencia, sin implementación, prototipo funcional, instalación, datos reales, producción ni cambios en GitHub.

Este documento no es aprobación de UX Gate ni autorización de I1. Define una experiencia observable para que una revisión independiente pueda comprobarla.

## 1. Entradas, hechos y límites

Entradas leídas:

- BOTTEGA-2-REQUIREMENTS.md: RF-001…RF-020, RNF-001…RNF-012, CA-001…CA-020, actores, límites, riesgos y preguntas P1…P7.
- BOTTEGA-2-SOLUTION-ROADMAP.md: alternativa C recomendada, D como salida segura, core neutral, adaptador Frappe separado, incrementos I0…I5 y gates.
- Issue #1: consolidación del contrato de producto para Incremento 0.
- Issue #3: contrato de producto, alcance, criterios y exclusiones.
- Evidencia referida en los artefactos: README, GUIA-DE-USO, kit de validación y estados de decisión; se tratan como evidencia del método existente, no del desempeño futuro.

Hechos de diseño:

- Existen tres modos explícitos: Advisor, Taller y Auditor.
- Un PASS técnico no es aceptación humana, release, publicación ni producción.
- El flujo debe fallar cerrado ante autorización, política, alcance o evidencia ausentes.
- Los datos sintéticos son el valor por defecto; Producto 02, datos institucionales y secretos están fuera de alcance.
- Los estados PRODUCT_PASS, RELEASE_READY_CONDITIONAL y PUBLICATION_AUTHORIZED son independientes.
- La revisión del implementador por sí mismo es inválida.

Supuestos de experiencia (pendientes de validar):

- La persona operadora puede identificar su rol y comprender una etiqueta de estado sin conocer el modelo interno.
- El sistema puede mostrar una causa de bloqueo, evidencia esperada y responsable sin revelar secretos.
- Un expediente puede conservar decisiones, intentos y referencias a artefactos sin exigir una sesión viva del proveedor.
- La identidad, autenticación, retención, límites de tamaño/duración/concurrencia/costo y proveedores siguen NO DETERMINADOS (P2, P3, P4, P6).

Decisiones de diseño:

- La pantalla siempre separa “resultado técnico” de “decisión humana requerida”.
- Las acciones de riesgo son explícitas, reversibles cuando sea posible y nunca se activan por lenguaje conversacional ambiguo.
- La navegación prioriza el expediente, su estado y la siguiente decisión; el historial detallado se consulta bajo demanda.
- Ningún texto usa “aprobado” para significar más de lo que el estado permite.

Preguntas abiertas UX:

- PUX-01: ¿qué identidad y rol verán las personas en la primera instalación? Depende de P3.
- PUX-02: ¿qué retención y borrado puede ofrecer el expediente? Depende de P6.
- PUX-03: ¿cuáles son los límites visibles de costo, duración, tamaño y concurrencia? Depende de P2.
- PUX-04: ¿qué proveedor y capacidades de streaming/log están autorizados? Depende de P4.
- PUX-05: ¿qué umbral humano define ADOPTAR, ADAPTAR o DETENER? Depende de P7.

## 2. Principio de servicio y modelo mental

La unidad principal no es una conversación: es una iniciativa con expediente verificable.

Modelo mental para la persona usuaria:

1. Entro con una necesidad o un brief.
2. El sistema me muestra qué sabe, qué supone y qué falta.
3. Elijo el siguiente paso dentro de un alcance declarado.
4. Cada etapa deja un artefacto y una evidencia identificable.
5. Un gate me dice si puedo continuar, corregir o pedir una decisión humana.
6. Puedo pausar y volver sin perder qué ocurrió ni repetirlo silenciosamente.

Regla de lenguaje: la interfaz debe preferir “condición faltante”, “requiere decisión humana” y “evidencia no encontrada” frente a “falló” cuando el problema sea de gobernanza; usar “error” sólo para una falla técnica identificable.

## 3. Arquitectura de información mínima

Navegación global:

- Inicio / Iniciativas
- Nueva iniciativa
- Expediente actual
- Gates y decisiones
- Evidencia y trazabilidad
- Ayuda de términos

Cabecera persistente del expediente:

- Nombre sintético de iniciativa.
- Modo actual: Advisor, Taller o Auditor.
- Estado de iniciativa: Borrador, En revisión, Bloqueada, En ejecución autorizada, Pausada, Lista para decisión, Cerrada.
- Datos: Sintéticos / clasificación declarada.
- Gate actual y siguiente condición.
- Botón visible: Pausar y guardar.

Panel de contexto resumido:

- Propósito y alcance.
- Owner y revisor independiente.
- Autorizaciones vigentes y alcance de cada una.
- Riesgos y preguntas abiertas.
- Última transición: actor, fecha/hora, motivo y referencia.

Vista de expediente:

- Resumen: estado y siguiente acción.
- Decisiones: humanas, técnicas y pendientes, separadas.
- Requisitos: RF/RNF, criterio, owner, prueba y evidencia.
- Etapas: dependencias y responsables.
- Evidencia: artefacto, origen, entorno, timestamp, hash, intento y resultado.
- Historial: eventos inmutables; las correcciones crean un intento nuevo.
- Bloqueos: condición, impacto, responsable y acción permitida.

## 4. Onboarding: de cero a primera recomendación

Objetivo: que una persona con una necesidad incompleta obtenga una primera propuesta de Advisor sin confundirla con autorización de ejecución.

Entrada del onboarding:

- Nombre sintético de iniciativa.
- Necesidad en lenguaje libre, con aviso: “No incluyas secretos, credenciales ni datos institucionales”.
- Resultado deseado, si se conoce.
- Actores o audiencia, si se conocen.
- Datos permitidos: selector obligatorio Sintéticos / otro valor sólo si existe política vigente.
- Owner de la iniciativa.

Paso 1 — Orientación

Texto visible: “Bottega ayuda a preparar decisiones y trabajo verificable. No acepta release, publicación ni producción por sí sola.”

La persona elige: “Quiero entender una necesidad” (Advisor), “Tengo un brief aprobado” (Taller) o “Quiero revisar evidencia” (Auditor). Si no sabe, “Ayúdame a elegir” muestra tres tarjetas con objetivo, entrada, salida y límite.

Paso 2 — Preflight de entrada

El sistema valida presencia de owner, alcance mínimo, clasificación de datos y autorización requerida para el siguiente paso. Resultado:

- LISTO: se puede generar propuesta de Advisor.
- NECESITA INFORMACIÓN: faltan campos no peligrosos; permite corregir.
- BLOQUEADO: falta autorización, hay datos no permitidos o el alcance intenta Producto 02, producción o una acción irreversible.

Paso 3 — Clarificación guiada

El Advisor pregunta primero lo que cambia la decisión. Cada pregunta tiene: por qué importa, respuesta opcional, “no lo sé” y “marcar NO DETERMINABLE”. No se rellena un dato por inferencia silenciosa.

Paso 4 — Primera recomendación

La salida se presenta en cuatro capas:

- Recomendación breve: “La alternativa recomendada es…”.
- Por qué: evidencia de entrada y supuestos usados.
- Opciones: al menos una alternativa comparable cuando la decisión sea relevante.
- Próximo paso: corregir, exportar expediente, solicitar revisión o pasar a Taller sólo si el brief y las autorizaciones lo permiten.

La tarjeta de recomendación lleva la etiqueta “Propuesta de Advisor — no es autorización de ejecución”.

Criterio de finalización del onboarding: la persona puede localizar problema, hechos, supuestos, NO DETERMINABLE, riesgos, requisitos, criterios y siguiente decisión; no se exige que acepte la recomendación.

## 5. Flujo del modo Advisor

Propósito: convertir una necesidad en un contrato verificable.

Estados de Advisor:

- Borrador: entrada creada, aún no evaluada.
- Preguntas pendientes: hay información faltante o NO DETERMINABLE.
- Propuesta lista: salida generada con hechos/supuestos/alternativas.
- Revisión solicitada: esperando revisión independiente.
- NEEDS_WORK: la revisión encontró faltantes o ambigüedad.
- PASS técnico: el contrato cumple los criterios del Advisor; no autoriza ejecución.
- BLOCKED: falta condición que no puede inferirse.

Secuencia:

1. Capturar necesidad y clasificación de datos.
2. Detectar actores, trabajos, alcance, restricciones y riesgos.
3. Separar hechos de supuestos y preguntas abiertas.
4. Marcar como NO DETERMINABLE toda afirmación no verificable.
5. Proponer opciones con trade-offs comprensibles.
6. Derivar requisitos funcionales/no funcionales y criterios observables.
7. Mostrar resumen y permitir comentarios o correcciones.
8. Solicitar revisión independiente.
9. Exponer PASS, NEEDS_WORK o BLOCKED con referencias.
10. Ofrecer exportación del expediente y, sólo con precondiciones, transición a Taller.

Interacción para aceptación del usuario:

“Confirmar que revisé esta propuesta” registra revisión de la persona; no cambia por sí sola un gate de ejecución. Para avanzar se muestran por separado: “Revisar propuesta”, “Solicitar decisión humana” y “Autorizar etapa”, cada una con consecuencia y alcance.

## 6. Flujo del modo Taller

Propósito: coordinar una iniciativa desde un brief aprobado, con stages, owners, dependencias, políticas y evidencia.

Precondición visible:

“Puedes abrir Taller cuando el brief requerido está disponible y el gate anterior tiene resultado aprobado para esta transición. PRODUCT_PASS no implica autorización de release o publicación.”

Configuración mínima de iniciativa:

- Owner y revisor independiente.
- Alcance, exclusiones y clasificación de datos.
- Stages y un Bot responsable por etapa.
- Predecesoras y artefactos esperados.
- Autorizaciones, políticas de proveedor y fallback.
- Presupuesto/límites sólo si están definidos por política.
- Entorno: sandbox/no destructivo por defecto.

Vista de tablero de etapas:

Cada tarjeta muestra: nombre, propósito, owner/Bot, dependencia, estado, evidencia esperada, última transición y siguiente gate. Estados recomendados: No disponible, Lista, En curso, Pausada, Necesita corrección, Bloqueada, Lista para revisión, Cerrada.

Flujo normal:

1. Preflight de iniciativa.
2. Confirmación de scope y política antes de cada ejecución.
3. Habilitación sólo tras predecesora aprobada y evidencia requerida.
4. Ejecución autorizada en sandbox.
5. Registro de delivery_attempt, provider_retry, validation_attempt y operational_cleanup por separado.
6. Generación de artefacto y hash.
7. Auditoría/revisión independiente.
8. Gate: PASS, NEEDS_WORK o BLOCKED.
9. Decisión humana independiente para producto, release, publicación o producción.

La tarjeta de una etapa bloqueada nunca ofrece un botón “continuar de todos modos”. Ofrece “Ver condición”, “Corregir brief”, “Solicitar decisión” o “Cerrar iniciativa”.

## 7. Flujo del modo Auditor

Propósito: inspeccionar coherencia, trazabilidad, guardrails, estados, hashes y autorizaciones sin modificar evidencia histórica ni autorizar publicación.

Entrada: expediente y evidencia de una iniciativa. El Auditor debe identificar su actor/revisor y rechazar auto-revisión.

Secuencia:

1. Seleccionar expediente y snapshot verificable.
2. Ejecutar comprobaciones deterministas no destructivas.
3. Revisar cobertura requisito → criterio → prueba → evidencia → owner → resultado.
4. Revisar hashes, intentos, timestamps, entorno y clasificación de datos.
5. Revisar dependencias, autorización, fallback y estado de cada gate.
6. Emitir resultado por regla y resultado global.

Resultados:

- PASS: evidencia suficiente para el alcance de la revisión.
- NEEDS_WORK: faltan elementos corregibles; lista cada faltante y cómo verificarlo.
- BLOCKED: política prohibida, ausencia crítica, identidad inválida, secreto detectado o ambigüedad que impide revisar de forma segura.

El resultado global no se presenta como “publicable”. Texto obligatorio: “Este resultado no autoriza release, publicación ni producción”.

Vista de hallazgo:

- Regla/requisito afectado.
- Resultado observado.
- Evidencia consultada, con hash si aplica.
- Qué detecta y qué no detecta esta comprobación.
- Acción correctiva permitida.
- Owner y revisión requerida.

## 8. Estados, bloqueos y mensajes

Catálogo UX de estados:

- Borrador — “Aún no se ha comprobado el expediente.”
- En revisión — “Una revisión independiente está pendiente.”
- LISTO — “Puedes iniciar el siguiente paso autorizado.”
- Necesita información — “Falta un dato para decidir; nada se ejecutará todavía.”
- NEEDS_WORK — “La revisión encontró faltantes corregibles.”
- BLOCKED — “La acción está detenida porque una condición obligatoria no está demostrada.”
- Pausada — “La iniciativa conserva su manifiesto y espera reanudación explícita.”
- PRODUCT_PASS — “El producto cumple el alcance técnico revisado; no es autorización de release/publicación.”
- RELEASE_READY_CONDITIONAL — “El producto está condicionado a una decisión de release separada.”
- PUBLICATION_AUTHORIZED — “Sólo aparece con autorización institucional vigente y evidencia correspondiente.”

Plantilla de bloqueo:

“BLOQUEADO: [acción].
Condición incumplida: [condición].
Evidencia esperada: [artefacto o decisión].
Responsable: [owner/rol].
Puedes: [corregir / solicitar revisión / cerrar].
No se realizó ninguna acción irreversible.”

Mensajes de casos críticos:

- Sin owner/datos/autorización: “No se puede iniciar. Completa owner, clasificación de datos y autorización del alcance.”
- Dependencia pendiente: “Etapa no disponible. [Predecesora] está [estado]; falta [evidencia].”
- Hash ausente/inconsistente: “BLOCKED. El manifiesto no prueba integridad. Conserva el intento y genera una corrección como nuevo intento.”
- Revisor implementador: “Revisión inválida. Asigna un revisor independiente.”
- Primer HTTP 429: “Circuit breaker abierto. El intento se detuvo. Fallback no autorizado por la política actual.”
- Fallback sin proveedor declarado: “BLOCKED. La política permite fallback, pero no identifica proveedor/capacidad alternativa.”
- Producto 02/producción/datos reales: “Fuera de alcance de esta iniciativa. No se realizó ningún cambio.”
- PASS técnico: “PASS técnico registrado. Aún no implica aceptación humana, release, publicación o producción.”
- Cierre inesperado: “La sesión terminó durante [acción]. El intento quedó registrado; reanuda desde el manifiesto, no desde una suposición.”

## 9. Pausa, reanudación y recuperación

Pausa voluntaria:

- Botón persistente “Pausar y guardar”.
- Pide motivo opcional y muestra qué quedará guardado.
- Confirma: estado, stage, último intento, evidencia, siguiente acción y datos pendientes.
- No revierte ni borra el historial.

Pausa por bloqueo:

- Se congela la ejecución autorizada.
- Se conservan los contadores separados y el último manifiesto verificable.
- Se muestra si es posible corregir, escalar o cerrar.
- No se reintenta automáticamente.

Reanudación:

1. La persona abre “Reanudar”.
2. El sistema muestra snapshot: “Qué ocurrió”, “Qué no ocurrió”, “Qué se repetirá”, “Qué no se repetirá” y “Qué autorización sigue vigente”.
3. Se vuelve a validar scope, política, datos, dependencia y evidencia.
4. La persona confirma la reanudación de ese alcance.
5. Se crea una transición nueva; no se edita el evento anterior.

Recuperación:

- Si el artefacto está disponible y el hash coincide: continuar desde el siguiente paso verificable.
- Si el hash no coincide: BLOCKED, conservar ambas referencias y pedir revisión.
- Si la autorización expiró o es ambigua: BLOCKED, solicitar nueva autorización.
- Si la UI no está disponible: el expediente exportado debe permitir a una persona autorizada reconstruir el estado sin sesión viva del proveedor.

Criterio contra duplicados: una reanudación nunca presenta como nueva una acción ya contabilizada; cualquier corrección usa un número de intento nuevo.

## 10. Evidencia visible para la persona usuaria

La interfaz debe mostrar, sin exponer secretos:

- ID de iniciativa, stage, run y attempt.
- Actor, owner, revisor y timestamp.
- Entrada y entorno declarados.
- Artefacto generado, origen y hash.
- Requisito/criterio/prueba relacionados.
- Resultado y razón.
- Qué detecta y qué no detecta la prueba.
- Datos sintéticos y clasificación.
- Política de proveedor aplicada; nunca tokens o credenciales.
- Diferencia entre delivery_attempt, provider_retry, validation_attempt y operational_cleanup.
- Estado de decisión separado: producto, release y publicación.

La vista resumida debe ser legible en menos de un minuto; el detalle debe ser expandible y exportable. La evidencia de fixtures debe portar la etiqueta “Fixture sintética — no demuestra desempeño de producto”.

## 11. Decisiones humanas mínimas

El sistema puede preparar y ejecutar sólo lo autorizado; la persona conserva como mínimo:

1. Confirmar alcance, owner, clasificación de datos y autorización inicial.
2. Aceptar o rechazar la propuesta de Advisor como insumo de trabajo.
3. Resolver ambigüedades que el sistema marque NO DETERMINABLE.
4. Aprobar la apertura de un stage que tenga precondiciones satisfechas.
5. Autorizar fallback cuando la política lo permita y el proveedor esté declarado.
6. Aceptar el producto tras revisión independiente (`PRODUCT_PASS`).
7. Decidir `RELEASE_READY_CONDITIONAL` con evidencia separada.
8. Autorizar publicación o producción de forma institucional y explícita (`PUBLICATION_AUTHORIZED`).
9. Decidir ADOPTAR, ADAPTAR o DETENER tras métricas con baseline.
10. Aprobar cualquier cambio de alcance, política, retención, identidad o gobernanza.

La interfaz debe pedir una decisión sólo con un resumen de impacto, evidencia, opciones y consecuencia; nunca con un botón ambiguo “Aceptar”.

## 12. Tareas críticas y criterios de usabilidad

Tareas críticas de primera versión:

- T1. Crear una iniciativa sintética y obtener una propuesta de Advisor.
- T2. Encontrar hechos, supuestos, NO DETERMINABLE y preguntas abiertas.
- T3. Identificar por qué una etapa está bloqueada y quién puede resolverla.
- T4. Distinguir PRODUCT_PASS de autorización de publicación.
- T5. Revisar trazabilidad de un requisito hasta su evidencia.
- T6. Pausar y reanudar sin duplicar una acción.
- T7. Detectar que un fallback no está autorizado tras un 429.
- T8. Reconocer que un revisor que implementó la etapa no es independiente.
- T9. Exportar un expediente comprensible sin sesión viva.

Criterios observables para prueba futura:

- La persona identifica el modo correcto sin ayuda en 4 de 5 escenarios sintéticos.
- Localiza el motivo, responsable y evidencia esperada de un bloqueo en menos de 90 segundos, sin usar texto técnico externo.
- Clasifica correctamente PRODUCT_PASS, RELEASE_READY_CONDITIONAL y PUBLICATION_AUTHORIZED en 5 escenarios.
- Reanuda un caso interrumpido y explica qué no se repetirá, sin duplicar el intento.
- Encuentra la relación requisito → criterio → prueba → evidencia en menos de 2 minutos.
- Explica con sus palabras qué significa NO DETERMINABLE y cuándo escalar.
- No se registra una autorización accidental al pulsar “revisé” o “continuar”.

Estos son criterios de prueba, no resultados observados. No se afirma usabilidad hasta obtener evidencia humana.

## 13. Prototipo futuro mínimo

No se implementa en Incremento 0. Para I1, el prototipo navegable mínimo debe incluir sólo fixtures sintéticas y cinco rutas:

1. Inicio → elección de modo → onboarding.
2. Advisor: necesidad incompleta → preguntas → propuesta.
3. Taller: expediente → tablero de etapas → bloqueo → corrección.
4. Auditor: evidencia → hallazgo → resultado NEEDS_WORK/BLOCKED/PASS.
5. Pausa/reanudación: snapshot → validación → confirmación.

Pantallas mínimas:

- Selector de modo con límites.
- Formulario de onboarding y preflight.
- Resumen Advisor con hechos/supuestos/NO DETERMINABLE.
- Expediente y cabecera de estado.
- Tarjeta de stage y bloqueo.
- Trazabilidad requisito-evidencia.
- Panel de Auditor.
- Snapshot de pausa/reanudación.
- Modal de decisión humana con alcance y consecuencia.

El prototipo debe simular, no ejecutar, proveedores, Frappe, GitHub o acciones remotas. Cada fixture debe usar nombres como `INICIATIVA-SINTETICA-01`, `REQ-SYN-001` y `EVIDENCIA-SYN-001`.

## 14. Plan de prueba humana con datos sintéticos

Gate de autorización de prueba: revisión independiente del guion y autorización humana de Douglas; no se reclutan personas ni se afirma resultado antes de ello.

Participantes sintéticos de planificación (no son datos reales):

- P-A: persona directora/propietaria que decide gates.
- P-B: operador de Taller.
- P-C: revisor de Auditor.
- P-D: usuario nuevo de Advisor sin vocabulario técnico.

Escenarios:

- S1 necesidad incompleta con dos preguntas NO DETERMINABLE.
- S2 brief sin owner ni autorización, que debe quedar BLOCKED.
- S3 stage con predecesora no aprobada.
- S4 PRODUCT_PASS sin autorización de publicación.
- S5 primer 429 sin fallback autorizado.
- S6 interrupción durante una acción y reanudación desde manifiesto.
- S7 evidencia con hash inconsistente.
- S8 intento de modificar Producto 02.

Método futuro:

- Prueba moderada, una tarea por escenario, sin datos personales ni sistemas reales.
- Registrar éxito/fallo, tiempo, errores de interpretación, preguntas y citas literales.
- No inducir la respuesta; permitir “no sé” y registrar cuándo la interfaz no es comprensible.
- Criterio de salida: analizar resultados por tarea, severidad y patrón; la decisión del gate la toma una persona independiente.
- Si aparece un riesgo de autorización, secreto o acción irreversible, detener la prueba y marcar BLOCKED.

## 15. Accesibilidad y lenguaje técnico controlado

Accesibilidad desde el diseño:

- Flujo completo con teclado: foco visible, orden lógico, sin trampa de foco y atajos no obligatorios.
- Estructura semántica: encabezados, landmarks, etiquetas asociadas, tabla de trazabilidad accesible y mensajes anunciados para cambios de estado.
- No depender sólo del color: estado con texto, icono y patrón; contraste suficiente según WCAG 2.2 AA como criterio objetivo futuro.
- Zoom y reflujo hasta 200% sin perder acciones críticas; diseño usable en viewport estrecho.
- Mensajes de error junto al campo y resumen de errores al inicio; lenguaje accionable.
- No usar tiempo límite sin aviso, extensión y alternativa.
- Controles grandes y separados; soporte para lectores de pantalla y navegación por voz sujeto a prueba.
- Evitar movimiento, parpadeo y actualización automática no anunciada.
- Exportación legible y estructurada, no sólo captura visual.

Lenguaje controlado:

- Usar “iniciativa”, “etapa”, “evidencia”, “criterio”, “revisión” y “decisión”.
- Definir una vez “gate”, “hash”, “attempt”, “fallback” y “circuit breaker”; ofrecer explicación contextual.
- Mostrar la etiqueta española y el identificador técnico cuando sea necesario: “Necesita corrección (NEEDS_WORK)”.
- Evitar antropomorfizar al sistema: “el sistema verificó”, no “el sistema decidió por ti”.
- Evitar “seguro”, “listo para publicar” o “aprobado” fuera del alcance exacto de la evidencia.
- Usar frases cortas, voz activa, fechas y actores explícitos.

## 16. Trazabilidad UX y riesgos

| Decisión UX | Requisito/CA relacionado | Evidencia futura |
|---|---|---|
| Tres modos con límites visibles | RF-001, CA-001 | Inspección de interfaz y escenario de elección |
| Hechos/supuestos/NO DETERMINABLE separados | RF-002, CA-003 | Fixture de necesidad incompleta |
| Bloqueo con condición, evidencia y responsable | RF-005, RNF-010, CA-004 | Escenario de predecesora pendiente |
| Estado técnico separado de decisión humana | RF-008/009, CA-007/008/020 | Escenarios de PASS y publicación |
| Revisión independiente | RF-020, CA-006/019 | Fixture de identidad de revisor |
| Pausa/reanudación desde manifiesto | RF-011, RF-014, CA-010/017 | Replay sintético e historial |
| Circuit breaker visible | RF-013, CA-009 | Escenario 429 |
| Privacidad y datos sintéticos por defecto | RF-015, RNF-006, CA-012/015 | Scan y escenario de Producto 02 |
| Exportación sin sesión viva | RNF-011 | Revisión del expediente exportado |
| No autorización implícita | RNF-009, CA-020 | Inspección de textos y transiciones |

Riesgos UX principales:

- RUX-01: “PASS” se interpreta como permiso de publicar. Mitigación: estados separados, texto persistente y prueba de comprensión.
- RUX-02: exceso de terminología técnica oculta la decisión. Mitigación: capas de resumen/detalle y glosario contextual.
- RUX-03: una pausa parece pérdida o deshacer. Mitigación: snapshot explícito y diferencia “qué ocurrió/no ocurrió”.
- RUX-04: demasiadas preguntas bloquean el onboarding. Mitigación: priorizar preguntas que cambian la decisión y permitir NO DETERMINABLE.
- RUX-05: evidencia sintética se toma como desempeño real. Mitigación: etiqueta de fixture y aviso visible de alcance.
- RUX-06: estados múltiples se confunden. Mitigación: cabecera con estado actual, siguiente gate y consecuencias; prueba de clasificación.

## 17. UX Gate y decisión

Checklist para revisión independiente:

- [ ] Los tres modos tienen propósito, entrada, salida, límites y transición explícitos.
- [ ] El onboarding llega a primera recomendación sin inventar datos.
- [ ] Todos los bloqueos muestran condición, evidencia esperada, responsable y acción permitida.
- [ ] Pausa, reanudación y recuperación preservan intentos y evitan duplicados.
- [ ] La evidencia visible es suficiente para reconstruir una decisión sin secretos.
- [ ] Los estados técnicos no implican aceptación, release, publicación o producción.
- [ ] Las tareas críticas tienen criterios observables y escenarios sintéticos.
- [ ] La accesibilidad y el lenguaje controlado están incluidos antes del prototipo.
- [ ] Un revisor independiente inspeccionó el diseño y registró PASS, NEEDS_WORK o BLOCKED.
- [ ] Douglas tomó la decisión humana requerida.

Veredicto actual: NEEDS_WORK / NO APROBADO. Este documento está listo para revisión independiente, pero su autor no emite el UX Gate. No se autoriza implementación de I1, prototipo funcional, proveedor, Frappe, integración, release o producción.

## 18. Handoff para diseño/ingeniería posterior

Antes de construir, el equipo deberá convertir este servicio en estados, componentes y contratos revisados, conservando:

- estado visible y estado técnico separado;
- permisos y alcance por modo;
- esquema de bloqueo y evidencia esperada;
- contadores de intentos separados;
- historial inmutable y reanudación verificable;
- fixtures sintéticas y pruebas negativas;
- copy exacto de autorización y no autorización implícita;
- requisitos de accesibilidad y teclado;
- trazabilidad UX → RF/RNF/CA → prueba → evidencia.

Cualquier decisión sobre identidad, retención, proveedor, límites, persistencia o integración deberá abrirse como decisión explícita y no resolverse mediante una convención silenciosa.
