# Requisitos de producto — Idea Prioritizer

- **Producto:** Idea Prioritizer
- **Documento:** 01 — Product Requirements
- **Versión:** 1.1
- **Estado:** corregido para revisión del GATE 1 de requisitos
- **Ámbito de persistencia:** un navegador y un dispositivo

## 1. Propósito y problema

El producto permitirá capturar, evaluar, ordenar y mantener ideas de forma local. El problema que resuelve es la dificultad de comparar oportunidades de manera consistente cuando las ideas se encuentran dispersas, no tienen un estado visible o no cuentan con una priorización reproducible.

La primera versión debe ofrecer un registro local de ideas con criterios de **impacto**, **confianza** y **facilidad**, una prioridad calculada automáticamente y mecanismos explícitos de importación, exportación y eliminación reversible durante un periodo breve.

### Objetivos

- Registrar ideas con información suficiente para evaluarlas.
- Hacer visible una prioridad calculada y ordenable.
- Permitir que el usuario gestione el estado manualmente.
- Conservar los datos al cerrar y volver a abrir el navegador.
- Permitir respaldo y traslado mediante archivos JSON.
- Evitar pérdidas accidentales mediante confirmación y deshacer temporal.

## 2. Alcance

### Incluido

1. Crear, consultar, modificar y eliminar ideas.
2. Asignar manualmente uno de los cinco estados definidos.
3. Capturar impacto, confianza y facilidad como enteros de 1 a 10.
4. Calcular la prioridad como `impacto × confianza × facilidad`.
5. Ordenar por prioridad descendente con desempates definidos.
6. Guardar y recuperar automáticamente la colección en almacenamiento local del navegador.
7. Exportar toda la colección a un archivo JSON descargable.
8. Validar, previsualizar, confirmar y aplicar importaciones JSON de forma atómica.
9. Importar en modo **Combinar** o **Reemplazar**.
10. Confirmar eliminaciones y ofrecer deshacer durante 10 segundos.

### No incluido en esta versión

Véase la sección 12, que prevalece sobre cualquier interpretación ampliada del alcance.

## 3. Actores

| Actor                 | Responsabilidad / necesidad                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Usuario gestor        | Crea, consulta, evalúa, cambia estados, edita, elimina, importa y exporta ideas.                                    |
| Aplicación            | Valida datos, calcula prioridad, gestiona fechas, persiste cambios, procesa archivos y aplica reglas de atomicidad. |
| Navegador/dispositivo | Proporciona el almacenamiento local y la descarga/selección de archivos. No es un actor multiusuario.               |

No existen cuentas, roles, autenticación ni actores remotos en esta versión.

## 4. Historias de usuario

- **HU-01 — Registrar idea:** Como usuario gestor, quiero crear una idea con título, descripción, estado inicial y criterios de evaluación para no perder una oportunidad.
- **HU-02 — Consultar prioridad:** Como usuario gestor, quiero ver la prioridad calculada de cada idea para comparar oportunidades.
- **HU-03 — Editar idea:** Como usuario gestor, quiero modificar los datos editables para mantener la evaluación actualizada.
- **HU-04 — Cambiar estado:** Como usuario gestor, quiero seleccionar manualmente el estado de una idea para reflejar su situación real sin estar limitado por un workflow rígido.
- **HU-05 — Ordenar colección:** Como usuario gestor, quiero ver primero las ideas de mayor prioridad y resolver empates de forma determinista.
- **HU-06 — Persistir localmente:** Como usuario gestor, quiero cerrar y reabrir el navegador sin perder la colección.
- **HU-07 — Exportar respaldo:** Como usuario gestor, quiero descargar todas las ideas en JSON para respaldarlas o trasladarlas.
- **HU-08 — Previsualizar importación:** Como usuario gestor, quiero conocer las ideas válidas y los conflictos antes de cambiar mi colección.
- **HU-09 — Combinar o reemplazar:** Como usuario gestor, quiero elegir si una importación se combina con la colección local o la sustituye.
- **HU-10 — Recuperar eliminación:** Como usuario gestor, quiero deshacer una eliminación durante 10 segundos para corregir una acción accidental.

## 5. Modelo de dominio

### 5.1 Entidad Idea

Una **Idea** tiene los siguientes atributos:

| Atributo       | Obligatorio | Regla                                                                         |
| -------------- | ----------: | ----------------------------------------------------------------------------- |
| `id`           |          Sí | Identificador único generado automáticamente; no editable por el usuario.     |
| `titulo`       |          Sí | Texto de máximo 120 caracteres. No puede faltar ni estar vacío.               |
| `descripcion`  |          Sí | Texto de máximo 2.000 caracteres. No puede faltar ni estar vacío.             |
| `estado`       |          Sí | Uno de: `borrador`, `en evaluación`, `aprobada`, `rechazada`, `implementada`. |
| `impacto`      |          Sí | Entero entre 1 y 10, inclusive.                                               |
| `confianza`    |          Sí | Entero entre 1 y 10, inclusive.                                               |
| `facilidad`    |          Sí | Entero entre 1 y 10, inclusive.                                               |
| `prioridad`    |          Sí | Calculada: `impacto × confianza × facilidad`; no editable.                    |
| `creadaEn`     |          Sí | Fecha y hora gestionadas automáticamente por la aplicación.                   |
| `modificadaEn` |          Sí | Fecha y hora gestionadas automáticamente por la aplicación.                   |
| `etiquetas`    |          No | Texto libre; no debe haber duplicados dentro de una misma idea.               |
| `notas`        |          No | Texto libre.                                                                  |

La identidad de una idea es su `id`. La prioridad y las fechas son datos derivados o gestionados por la aplicación y no constituyen entradas editables del usuario.

### 5.2 Colección de ideas

La aplicación mantiene una colección local de ideas. La colección se muestra por defecto en este orden:

1. `prioridad` descendente.
2. `modificadaEn` descendente (la modificada más recientemente primero).
3. `titulo` en orden alfabético para resolver cualquier empate restante.

El documento de intercambio JSON contiene como mínimo una versión de esquema, una fecha de exportación y la colección completa de ideas.

### 5.3 Operaciones de dominio

- **Crear:** genera `id`, establece estado `borrador`, calcula prioridad y establece las dos fechas automáticamente.
- **Modificar:** actualiza únicamente campos editables; recalcula prioridad si cambia un criterio y actualiza `modificadaEn`.
- **Eliminar:** requiere confirmación; crea una oportunidad de deshacer de 10 segundos.
- **Importar:** valida el archivo completo antes de mutar la colección y aplica el modo elegido de forma atómica.
- **Exportar:** serializa todas las ideas actuales y metadatos de esquema/exportación sin datos personales ni credenciales.

## 6. Estados y reglas de negocio

### 6.1 Estados

Los estados válidos son:

- `borrador`
- `en evaluación`
- `aprobada`
- `rechazada`
- `implementada`

Toda idea nueva inicia en `borrador`. En esta versión el usuario puede cambiar manualmente entre cualesquiera de los estados válidos mediante una lista. No existe un workflow rígido ni se bloquean transiciones por estado previo.

### 6.2 Reglas numeradas

- **RN-01:** El identificador se genera automáticamente y es único dentro de la colección.
- **RN-02:** El título es obligatorio y no supera 120 caracteres.
- **RN-03:** La descripción es obligatoria y no supera 2.000 caracteres.
- **RN-04:** Las etiquetas son opcionales, de texto libre y sin duplicados dentro de una idea.
- **RN-05:** Las notas son opcionales y de texto libre.
- **RN-06:** Impacto, confianza y facilidad son enteros de 1 a 10, inclusive.
- **RN-07:** La prioridad siempre es el producto de los tres criterios y no es editable.
- **RN-08:** Las fechas de creación y modificación son gestionadas automáticamente.
- **RN-09:** Todo cambio persistible se guarda automáticamente después de crear, modificar, eliminar o importar.
- **RN-10:** La eliminación exige confirmación explícita y permite deshacer durante 10 segundos.
- **RN-11:** Una importación inválida no aplica ningún cambio parcial.
- **RN-12:** En modo Combinar, un mismo `id` actualiza la idea local existente; un `id` nuevo agrega una idea.
- **RN-13:** En modo Reemplazar, la colección local se sustituye completamente por la colección importada válida.
- **RN-14:** Una importación con identificadores duplicados en el mismo archivo se rechaza completa.
- **RN-15:** El orden predeterminado aplica prioridad, fecha de modificación y título como desempates, en ese orden.
- **RN-16:** Los estados válidos son `borrador`, `en evaluación`, `aprobada`, `rechazada` e `implementada`; toda idea nueva inicia en `borrador`; el usuario puede cambiar manualmente entre cualesquiera de esos estados; en esta versión no existe un workflow rígido.

## 7. Requisitos funcionales

- **RF-01 — Alta:** El sistema debe permitir crear una idea proporcionando título, descripción, impacto, confianza y facilidad; debe asignar los valores iniciales y gestionados automáticamente.
- **RF-02 — Listado:** El sistema debe mostrar las ideas almacenadas y su prioridad calculada.
- **RF-03 — Detalle/edición:** El sistema debe permitir consultar y editar los campos editables de una idea existente.
- **RF-04 — Estado:** El sistema debe ofrecer una lista con los cinco estados válidos y permitir cualquier cambio manual entre ellos.
- **RF-05 — Cálculo:** El sistema debe recalcular la prioridad inmediatamente después de modificar cualquiera de los tres criterios.
- **RF-06 — Orden:** El sistema debe ordenar por prioridad descendente, luego modificación más reciente y luego título alfabético.
- **RF-07 — Persistencia:** El sistema debe guardar automáticamente tras cada creación, modificación, eliminación confirmada o importación aplicada.
- **RF-08 — Recuperación:** El sistema debe reconstruir la colección persistida al abrirse nuevamente en el mismo navegador y dispositivo.
- **RF-09 — Exportación:** El sistema debe exportar todas las ideas actuales a un archivo JSON descargable que incluya versión de esquema y fecha de exportación.
- **RF-10 — Prevalidación:** El sistema debe analizar el archivo completo y validar JSON, versión, estructura, campos, tipos, rangos y unicidad de identificadores antes de aplicar cambios.
- **RF-11 — Vista previa:** Antes de importar, el sistema debe mostrar cantidad de ideas válidas, conflictos y errores encontrados.
- **RF-12 — Confirmación:** El sistema no debe modificar la colección antes de la confirmación explícita del usuario.
- **RF-13 — Modos:** El sistema debe permitir elegir Combinar, opción predeterminada, o Reemplazar.
- **RF-14 — Atomicidad:** El sistema debe aplicar una importación completamente o no aplicarla en absoluto.
- **RF-15 — Eliminación segura:** El sistema debe pedir confirmación explícita antes de eliminar y mostrar deshacer durante 10 segundos después.
- **RF-16 — Fin de deshacer:** Transcurridos 10 segundos sin deshacer, la eliminación debe quedar definitiva y sin papelera permanente.

## 8. Requisitos no funcionales

- **RNF-01 — Persistencia local:** La información debe conservarse mediante almacenamiento local del navegador; no se requiere servidor.
- **RNF-02 — Atomicidad:** Una operación de importación no debe dejar una colección parcialmente modificada si falla la validación o aplicación.
- **RNF-03 — Integridad:** La prioridad almacenada o presentada debe ser consistente con los tres criterios vigentes.
- **RNF-04 — Determinismo:** Con los mismos datos, las reglas de ordenación y validación deben producir el mismo resultado.
- **RNF-05 — Transparencia:** Los errores de validación deben identificar el problema de manera comprensible para el usuario.
- **RNF-06 — Privacidad de exportación:** El archivo exportado no debe contener datos personales ni credenciales.
- **RNF-07 — Compatibilidad de esquema:** El sistema debe rechazar versiones de esquema no compatibles, sin intentar una conversión silenciosa.
- **RNF-08 — Recuperación de sesión:** Cerrar y volver a abrir el navegador no debe borrar una colección correctamente guardada.
- **RNF-09 — Usabilidad:** Las acciones destructivas y las decisiones de importación deben ser explícitas y distinguibles.

No se fija todavía una arquitectura ni una tecnología de almacenamiento concreta más allá del requisito funcional de almacenamiento local del navegador.

## 9. Validaciones y casos límite

### Validaciones de entrada

1. Rechazar título ausente, vacío o de más de 120 caracteres.
2. Rechazar descripción ausente, vacía o de más de 2.000 caracteres.
3. Rechazar impacto, confianza o facilidad ausentes, no enteros, menores que 1 o mayores que 10.
4. Rechazar estado fuera del conjunto definido.
5. Rechazar edición manual del `id`, la prioridad o las fechas.
6. Rechazar etiquetas duplicadas dentro de la misma idea.
7. Aceptar notas y etiquetas vacías cuando son opcionales.
8. Generar prioridad sin permitir que el usuario la introduzca directamente.

### Casos límite

- Una prioridad mínima es `1 × 1 × 1 = 1`; una máxima es `10 × 10 × 10 = 1000`.
- Dos ideas con igual prioridad se ordenan por la fecha de modificación más reciente.
- Si también empatan en fecha, se ordenan por título alfabético.
- Si dos títulos son idénticos y persiste el empate, el orden puede quedar determinado por el identificador interno, pero no se debe presentar como una regla de negocio adicional.
- Un archivo JSON válido pero vacío debe ser aceptado únicamente si su estructura de exportación es válida y contiene una colección vacía.
- Un JSON válido con colección parcial o campos obligatorios ausentes debe rechazarse completo.
- Un archivo con identificadores duplicados debe rechazarse incluso si las ideas duplicadas tienen contenido idéntico.
- Una versión de esquema desconocida o no compatible debe rechazarse antes de mostrar una opción de aplicación.
- Cancelar la vista previa o la confirmación no debe modificar la colección.
- Un error durante la aplicación de una importación no debe dejar una combinación parcial visible.
- Si el usuario no pulsa deshacer dentro de 10 segundos, la eliminación se vuelve definitiva.
- Al modificar un criterio, la prioridad y el orden deben reflejarse inmediatamente; la fecha de modificación debe actualizarse automáticamente.

## 10. Requisitos de importación y exportación

### 10.1 Exportación

- **IE-01:** Debe incluir todas las ideas de la colección en el momento de exportar.
- **IE-02:** Debe incluir `schemaVersion` o equivalente explícito.
- **IE-03:** Debe incluir `exportedAt` o equivalente con fecha y hora de exportación.
- **IE-04:** Debe producir un archivo JSON descargable.
- **IE-05:** Cada idea exportada debe conservar su identidad, campos, prioridad coherente y fechas gestionadas.
- **IE-06:** No debe incluir credenciales ni datos personales.

### 10.2 Importación

- **II-01:** Debe aceptar un archivo JSON seleccionado por el usuario.
- **II-02:** Debe leer y analizar el archivo completo antes de cualquier mutación.
- **II-03:** Debe validar sintaxis JSON, versión de esquema, estructura, campos obligatorios, tipos, rangos, estados, etiquetas e identificadores.
- **II-04:** Debe presentar una vista previa con conteo de ideas válidas y conflictos.
- **II-05:** Debe dejar la colección intacta hasta una confirmación explícita.
- **II-06:** Debe ofrecer Combinar como opción predeterminada y Reemplazar como alternativa.
- **II-07:** Combinar agrega identificadores nuevos y actualiza los existentes con el mismo identificador.
- **II-08:** Reemplazar elimina la colección local y la sustituye por el contenido importado válido.
- **II-09:** JSON inválido, versión incompatible, duplicados internos, campos faltantes o valores fuera de rango deben rechazar el archivo completo.
- **II-10:** La importación debe ser atómica y no aplicar cambios parciales.
- **II-11:** Debe mostrar mensajes de error suficientes para identificar los errores encontrados.

## 11. Criterios de aceptación verificables

- **CA-01:** Al crear una idea válida, existe exactamente una nueva idea con identificador generado, estado `borrador`, prioridad calculada y ambas fechas gestionadas.
- **CA-02:** Un título de 120 caracteres se acepta y uno de 121 se rechaza sin crear o guardar la idea inválida.
- **CA-03:** Una descripción de 2.000 caracteres se acepta y una de 2.001 se rechaza sin crear o guardar la idea inválida.
- **CA-04:** Cada criterio acepta 1 y 10, y rechaza 0, 11, decimales, texto y valores ausentes.
- **CA-05:** Para impacto 8, confianza 5 y facilidad 6, la prioridad mostrada es 240 y no existe un control editable para introducirla.
- **CA-06:** Cambiar un criterio recalcula la prioridad sin recargar y cambia el orden si corresponde; `modificadaEn` se actualiza automáticamente.
- **CA-07:** La lista permite todos los cambios entre los cinco estados, incluido volver a un estado anterior.
- **CA-08:** Con prioridades distintas, el orden es de mayor a menor prioridad.
- **CA-09:** Con igual prioridad, la idea con `modificadaEn` más reciente aparece primero; si también empatan, el título se ordena alfabéticamente.
- **CA-10:** Tras crear, editar o eliminar y cerrar/reabrir el navegador en el mismo dispositivo, la colección refleja la última operación persistida.
- **CA-11:** Exportar una colección de N ideas produce un JSON descargable con N ideas, versión de esquema y fecha de exportación, sin credenciales ni datos personales.
- **CA-12:** Antes de confirmar una importación válida, la colección local permanece sin cambios y la vista previa muestra el conteo y conflictos.
- **CA-13:** En Combinar, un identificador nuevo incrementa la colección y un identificador coincidente actualiza la idea local sin crear un duplicado.
- **CA-14:** En Reemplazar, tras confirmar una importación válida, la colección contiene exactamente las ideas importadas y no las anteriores que no estén en el archivo.
- **CA-15:** Un archivo JSON inválido, incompatible, incompleto, con rango inválido o con identificadores duplicados se rechaza completo; la colección antes y después es idéntica.
- **CA-16:** Cancelar la confirmación de importación no produce cambios.
- **CA-17:** Confirmar una eliminación la quita de la colección y muestra una acción de deshacer durante 10 segundos.
- **CA-18:** Pulsar deshacer dentro de los 10 segundos restaura la idea; no pulsarlo hace definitiva la eliminación al expirar el periodo.
- **CA-19:** Si falla la aplicación de una importación, no queda ningún subconjunto aplicado.
- **CA-20:** Las etiquetas duplicadas en una misma idea se rechazan; etiquetas iguales en ideas distintas no se consideran conflicto.

## 12. Elementos fuera de alcance

- Sincronización entre dispositivos o navegadores.
- Cuentas de usuario, autenticación, autorización o multiusuario.
- Base de datos remota, API de servidor o respaldo automático en la nube.
- Workflow rígido o transiciones condicionadas por estado.
- Papelera permanente o historial de versiones.
- Notificaciones, colaboración, comentarios multiusuario o auditoría remota.
- Datos personales, credenciales o gestión de secretos.
- Arquitectura definitiva, framework o proveedor de almacenamiento específico más allá del almacenamiento local del navegador.

## 13. Riesgos y supuestos

### Riesgos

| Riesgo                                                                                           | Impacto                                           | Mitigación requerida                                                                                                   |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| El almacenamiento local puede borrarse por el navegador, el usuario o políticas del dispositivo. | Pérdida de datos.                                 | Exportación JSON como mecanismo explícito de respaldo y traslado.                                                      |
| Archivos JSON grandes pueden afectar validación o previsualización.                              | Degradación de usabilidad o fallo de importación. | Validar el archivo completo y mostrar errores sin aplicar parciales; el límite de volumen queda pendiente de producto. |
| Colisiones o formato inconsistente de identificadores entre exportaciones.                       | Actualizaciones incorrectas al combinar.          | Validar unicidad interna y tratar `id` como identidad no editable.                                                     |
| Diferencias de formato de fechas o esquema futuro.                                               | Importaciones incompatibles.                      | Incluir versión explícita y rechazar versiones no compatibles.                                                         |
| El temporizador de 10 segundos puede ser interrumpido por cierre o suspensión del navegador.     | Deshacer no disponible.                           | Tratar la disponibilidad del deshacer como temporal; respaldar antes de operaciones importantes mediante exportación.  |

### Supuestos

- El usuario opera una única colección en un navegador y dispositivo.
- El navegador habilita almacenamiento local y descarga/selección de archivos.
- La fecha y hora del dispositivo son suficientemente confiables para ordenar modificaciones.
- La interfaz puede mostrar errores y solicitar confirmaciones explícitas.
- La colección importada usa el esquema compatible definido por el producto.
- No se requiere migración automática de esquemas en esta primera versión.

## 14. Matriz de trazabilidad

| Decisión / necesidad                          | Requisitos                                | Criterios de aceptación |
| --------------------------------------------- | ----------------------------------------- | ----------------------- |
| Estados definidos y cambio manual             | RN-16, RF-04                              | CA-01, CA-07            |
| Título y descripción obligatorios con límites | RN-02, RN-03                              | CA-02, CA-03            |
| Criterios enteros 1–10 y prioridad calculada  | RN-06, RN-07, RF-05                       | CA-04, CA-05, CA-06     |
| Etiquetas sin duplicados y notas opcionales   | RN-04, RN-05                              | CA-20                   |
| Fechas automáticas e identidad no editable    | RN-01, RN-08, RF-01, RF-03                | CA-01, CA-06            |
| Orden por prioridad y desempates              | RN-15, RF-06                              | CA-08, CA-09            |
| Persistencia local automática                 | RN-09, RNF-01, RNF-08, RF-07, RF-08       | CA-10                   |
| Exportación con esquema y fecha               | RF-09, IE-01–IE-06                        | CA-11                   |
| Vista previa y no mutación previa             | RF-10–RF-12, II-01–II-05                  | CA-12, CA-16            |
| Combinar y Reemplazar                         | RN-12, RN-13, RF-13                       | CA-13, CA-14            |
| Rechazo completo y atomicidad                 | RN-11, RN-14, RF-14, II-09, II-10, RNF-02 | CA-15, CA-19            |
| Eliminación confirmada y deshacer             | RN-10, RF-15, RF-16                       | CA-17, CA-18            |
| Privacidad del archivo                        | RNF-06, IE-06                             | CA-11                   |
| Errores comprensibles y decisiones explícitas | RNF-05, RNF-09, II-11                     | CA-12, CA-15, CA-16     |

## 15. Definition of Done de requisitos

El trabajo de requisitos se considera terminado cuando:

- [x] Propósito, problema y objetivos están documentados.
- [x] Alcance incluido y excluido está explícito.
- [x] Actores y responsabilidades están identificados.
- [x] Las historias de usuario cubren creación, evaluación, persistencia, intercambio y eliminación.
- [x] El modelo de dominio define identidad, atributos, colección y operaciones.
- [x] Los cinco estados y la ausencia de workflow rígido están documentados.
- [x] Las reglas de negocio están numeradas y no son ambiguas.
- [x] Los requisitos funcionales y no funcionales están numerados.
- [x] Las validaciones, errores y casos límite están documentados.
- [x] Exportación e importación incluyen esquema, fecha, previsualización, confirmación, modos y atomicidad.
- [x] Cada decisión relevante tiene al menos un criterio de aceptación verificable.
- [x] La matriz de trazabilidad conecta necesidades, requisitos y criterios.
- [x] Riesgos y supuestos están separados de requisitos confirmados.
- [ ] No se ha seleccionado arquitectura definitiva ni se ha escrito código como parte de este entregable.
- [x] No quedan decisiones bloqueantes para iniciar el siguiente gate de diseño, salvo las explícitamente registradas como pendientes.

**Bloqueo de la casilla sin marcar:** el contenido de este documento confirma que no se selecciona una arquitectura definitiva, pero no puede comprobar por sí solo que no se haya escrito código fuera del entregable. Esa parte requiere verificación del repositorio o del proceso de trabajo.

### Estado del gate

Con las decisiones proporcionadas, no queda una decisión funcional bloqueante para GATE 1. Queda como decisión posterior, no bloqueante para este documento, definir el formato exacto de los nombres de propiedades del JSON y la política de límites de tamaño de archivo/colección, siempre que no contradigan los requisitos de validación, atomicidad y privacidad anteriores.

Este alcance queda sujeto al [criterio de aceptación](../../docs/glossary/entries/acceptance-criteria.md#glossary-acceptance-criteria).
