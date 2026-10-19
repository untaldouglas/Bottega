# Backlog de entrega — Idea Prioritizer

- **Producto:** Idea Prioritizer
- **Documento:** 02 — Delivery Backlog
- **Entrada:** requisitos v1.1 y diseño de solución v1.2
- **Revisión del backlog:** 1.2
- **Estado:** propuesta para revisión del GATE 2; no implica aprobación ni inicio de implementación
- **Regla:** cada unidad es una entrega verificable; no se crea código en esta etapa

### Registro breve de cambios de la revisión 1.2

- Se incorporan validación, medición y conteo de la colección resultante completa para Combinar/Reemplazar y para toda mutación, con rechazo atómico y preservación exacta del estado anterior.
- Se añaden pruebas de capacidad para Combinar con colecciones de 3 MiB, Reemplazar dentro/fuera de límite y crear/editar/deshacer que cruzan límites.
- Se explicita el grafo completo de dependencias y se corrige la frontera GATE 2 → arquitectura → GATE 3 → implementación.

## 1. Criterio de priorización

- **MVP:** necesario para cumplir los requisitos aprobados y los criterios CA-01–CA-20.
- **Posterior:** mejora de operación, documentación o medición que no debe bloquear el primer producto conforme.
- Las prioridades **P0/P1/P2** indican orden dentro de cada clasificación.
- Las dependencias expresan bloqueos reales, no una secuencia burocrática.

## 2. Épicas

| ID  | Épica                              | Resultado                                                           |
| --- | ---------------------------------- | ------------------------------------------------------------------- |
| E1  | Modelo y reglas de ideas           | Ideas válidas, calculadas y ordenadas de forma determinista         |
| E2  | Gestión de colección               | Alta, listado, consulta, edición, estado y eliminación segura       |
| E3  | Persistencia local                 | Recuperación automática en el mismo navegador/dispositivo           |
| E4  | Intercambio JSON                   | Exportación e importación con versión, validación y vista previa    |
| E5  | Atomicidad y capacidad             | Commit completo, manejo de cuota y límites operativos               |
| E6  | Accesibilidad y UX                 | Decisiones explícitas, errores comprensibles y navegación accesible |
| E7  | Calidad y distribución open source | Pruebas, documentación y empaquetado reproducible local             |

## 3. Unidades de entrega

### U01 — Cerrar contrato de dominio y JSON

- **Épica:** E1/E4
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** Ninguna
- **Entrega:** contrato verificable para Idea, colección, estados, cálculo, orden y documento JSON `schemaVersion: "1.0"`.
- **Criterios relacionados:** RN-01–RN-08, RN-15–RN-16, RF-05–RF-06, IE-01–IE-06, CA-01, CA-04–CA-06, CA-08–CA-11, CA-20.
- **Criterios de aceptación de la unidad:**
  - [ ] Los nombres de propiedades son los definidos en el diseño.
  - [ ] Las reglas de campos, rangos, estados, etiquetas y prioridad están expresadas sin ambigüedad.
  - [ ] La versión `1.0` y el rechazo de versiones no compatibles están documentados.
  - [ ] Se dispone de ejemplos sintéticos válidos e inválidos.
- **Pruebas requeridas:** tabla de casos de dominio; valores frontera 1/10, 0/11, 120/121 y 2.000/2.001; duplicados de etiquetas; prioridad 240 y rango 1–1000.
- **Entregables documentales:** contrato lógico JSON, catálogo de errores de validación y tabla de trazabilidad.

### U02 — Implementar reglas de dominio y orden determinista

- **Épica:** E1
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U01
- **Entrega:** una superficie de dominio que crea, valida, actualiza, calcula prioridad y ordena sin depender de APIs del navegador.
- **Criterios relacionados:** RF-01–RF-06, RN-01–RN-08, RN-15–RN-16, CA-01–CA-09, CA-20.
- **Criterios de aceptación de la unidad:**
  - [ ] Crear genera identidad, `borrador`, fechas y prioridad.
  - [ ] Editar solo permite campos editables y actualiza prioridad/fecha cuando corresponde.
  - [ ] El orden aplica prioridad, `modificadaEn` y título.
  - [ ] Los errores no producen una idea inválida.
- **Pruebas requeridas:** pruebas de comportamiento del módulo, no de implementación; propiedad de determinismo para datos sintéticos; regresiones de límites.
- **Entregables documentales:** decisiones de interfaz del módulo de dominio y matriz de casos.

### U03 — Entregar flujo de colección: listar, editar y estados

- **Épica:** E2/E6
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U02
- **Entrega:** el usuario puede crear, consultar, editar y cambiar libremente el estado de ideas, viendo la prioridad y el orden actualizados.
- **Criterios relacionados:** RF-01–RF-06, RNF-03–RNF-05, RNF-09, CA-01–CA-09.
- **Criterios de aceptación de la unidad:**
  - [ ] Los cinco estados aparecen y se permite cualquier transición manual.
  - [ ] La prioridad se actualiza sin recarga al modificar un criterio.
  - [ ] La lista refleja el desempate definido.
  - [ ] Los campos obligatorios y mensajes de error son comprensibles.
- **Pruebas requeridas:** pruebas de interacción con teclado y foco; pruebas de criterios de aceptación CA-01–CA-09.
- **Entregables documentales:** guía breve de uso local y catálogo de mensajes.

### U04 — Entregar eliminación confirmada y deshacer temporal

- **Épica:** E2/E6
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U03
- **Entrega:** eliminar requiere confirmación y permite restaurar la idea durante 10 segundos; después no queda papelera permanente.
- **Criterios relacionados:** RN-10, RF-15–RF-16, CA-17–CA-18.
- **Criterios de aceptación de la unidad:**
  - [ ] Cancelar la confirmación conserva la colección.
  - [ ] Confirmar elimina y muestra deshacer durante 10 segundos.
  - [ ] Deshacer dentro del periodo restaura la idea.
  - [ ] Expirar el periodo hace definitiva la eliminación.
- **Pruebas requeridas:** reloj controlado en pruebas, cancelación, restauración y expiración; cierre/suspensión documentados como limitación del deshacer.
- **Entregables documentales:** especificación de estados de la acción destructiva.

### U05 — Implementar adaptador de persistencia local estructurada

- **Épica:** E3/E5
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U02
- **Entrega:** la colección se guarda y recupera automáticamente mediante IndexedDB detrás de un seam pequeño, sin que el dominio conozca el navegador; el adaptador en memoria se reserva para pruebas de contrato y `localStorage` solo para prototipo.
- **Criterios relacionados:** RF-07–RF-08, RN-09, RNF-01, RNF-08, CA-10.
- **Criterios de aceptación de la unidad:**
  - [ ] Crear, editar, eliminar confirmado e importar aplicado guardan automáticamente.
  - [ ] Reabrir en el mismo navegador/dispositivo recupera el último estado confirmado.
  - [ ] Un error de lectura o escritura se comunica sin declarar guardado lo no confirmado.
  - [ ] Existe una implementación de prueba del seam sin depender de IndexedDB.
- **Pruebas requeridas:** contrato del adaptador, recuperación tras reapertura, transacción abortada y almacenamiento no disponible.
- **Entregables documentales:** decisión física de almacenamiento, procedimiento de limpieza local y limitaciones por navegador.

### U06 — Exportar colección JSON

- **Épica:** E4
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U01, U05
- **Entrega:** descarga de toda la colección vigente como JSON versionado, con fecha de exportación y sin información personal o credenciales.
- **Criterios relacionados:** RF-09, IE-01–IE-06, RNF-06, CA-11.
- **Criterios de aceptación de la unidad:**
  - [ ] El archivo incluye exactamente N ideas vigentes.
  - [ ] Incluye `schemaVersion: "1.0"` y `exportedAt` válido.
  - [ ] Conserva identidad, campos, prioridad coherente y fechas.
  - [ ] No agrega credenciales, datos personales ni telemetría.
- **Pruebas requeridas:** colección vacía, una idea, N ideas, caracteres especiales, privacidad por inspección del JSON.
- **Pruebas de capacidad y portabilidad:** JSON compacto; colección normalizada en 4 MiB y por encima; exportar y reimportar toda colección aceptada con la misma versión.
- **Entregables documentales:** formato de archivo, instrucciones de respaldo y ejemplo sintético.

### U07 — Validar y previsualizar importación completa

- **Épica:** E4/E5
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U01, U05
- **Entrega:** selección de archivo JSON, lectura completa, validación sin mutación y vista previa con válidos, conflictos y errores.
- **Criterios relacionados:** RF-10–RF-12, II-01–II-05, II-09, II-11, RNF-02, RNF-05, RNF-07, CA-12, CA-15–CA-16, CA-19–CA-20.
- **Criterios de aceptación de la unidad:**
  - [ ] Se rechazan sintaxis inválida, versión incompatible, estructura incompleta, tipos/rangos inválidos, estados inválidos y duplicados internos.
  - [ ] Se aplica el límite de 5 MiB antes de parsear y se rechaza atómicamente todo archivo por encima.
  - [ ] Después de calcular el resultado hipotético de Combinar o Reemplazar, se normaliza la colección resultante completa, se miden sus bytes UTF-8 compactos y se cuentan sus ideas; se rechaza el primer límite excedido.
  - [ ] En Combinar la medición incluye ideas locales nuevas o actualizadas por el archivo; en Reemplazar coincide con la colección importada.
  - [ ] La vista previa muestra conteos, conflictos, errores y el límite excedido cuando corresponda.
  - [ ] Antes de confirmar, la colección local permanece idéntica.
- **Pruebas requeridas:** corpus de archivos válidos e inválidos; duplicados, colección vacía, campos ausentes, prioridad inconsistente, archivo sobredimensionado, colección local de 3 MiB más importación Combinar de 3 MiB y preservación exacta del estado anterior ante el rechazo.
- **Entregables documentales:** catálogo de diagnósticos y procedimiento de soporte para importar.

### U08 — Aplicar Combinar y Reemplazar atómicamente

- **Épica:** E4/E5
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U05, U07
- **Entrega:** tras confirmación explícita, Combinar actualiza/agrega por `id` y Reemplazar sustituye la colección completa; cualquier fallo conserva el estado anterior.
- **Criterios relacionados:** RF-13–RF-14, RN-11–RN-14, RNF-02, CA-13–CA-16, CA-19.
- **Criterios de aceptación de la unidad:**
  - [ ] Combinar es la opción predeterminada.
  - [ ] Un `id` existente actualiza sin duplicar; uno nuevo agrega.
  - [ ] Reemplazar deja exactamente las ideas importadas válidas.
  - [ ] El resultado completo se valida en bytes UTF-8 compactos y cantidad antes del commit; cualquier exceso muestra el límite y conserva exactamente la colección anterior.
  - [ ] Cancelar no cambia nada.
  - [ ] Error de aplicación/transacción no deja subconjunto visible.
- **Pruebas requeridas:** pruebas de contrato del plan de aplicación, Reemplazar dentro y fuera de límite, transacción abortada, error de cuota, rollback observable y comparación exacta antes/después.
- **Entregables documentales:** descripción de atomicidad, matriz Combinar/Reemplazar y evidencia de pruebas.

### U09 — Manejar capacidad, recuperación y límites operativos

- **Épica:** E3/E5/E6
- **Prioridad:** P1
- **Clasificación:** MVP
- **Bloqueada por:** U05, U08
- **Entrega:** comportamiento definido y verificable cuando el navegador no tiene espacio, el archivo excede 5 MiB, la colección normalizada excede 4 MiB o la colección supera el techo preventivo de 10.000 ideas.
- **Criterios relacionados:** RNF-01–RNF-05, RNF-08, CA-10, CA-11, CA-15, CA-19.
- **Criterios de aceptación de la unidad:**
  - [ ] Se conserva el último estado persistido ante error de capacidad.
  - [ ] Se muestra un error accionable y se permite reintentar.
  - [ ] No se presentan como guardados cambios no comprometidos.
  - [ ] El mensaje de capacidad distingue archivo de entrada, JSON normalizado y cantidad; no presenta 10.000 ideas como capacidad garantizada ni contradice los límites duros de 5 MiB y 4 MiB.
- **Pruebas requeridas:** `QuotaExceededError`, almacenamiento denegado, archivo exactamente en 5 MiB y por encima, colección normalizada exactamente en 4 MiB y por encima, colecciones de exactamente 10.000 y 10.001 ideas, creación, edición y deshacer que cruzan el límite, y preservación exacta del último estado confirmado ante cada rechazo.
- **Entregables documentales:** tabla de límites, guía de recuperación y reporte de rendimiento.

### U10 — Accesibilidad y experiencia de decisiones explícitas

- **Épica:** E6
- **Prioridad:** P1
- **Clasificación:** MVP
- **Bloqueada por:** U03, U04, U07, U08
- **Entrega:** formularios, errores, vista previa, confirmaciones y deshacer son utilizables con teclado y tecnologías de asistencia.
- **Criterios relacionados:** RNF-05, RNF-09, II-04, II-11, CA-12, CA-16–CA-18.
- **Criterios de aceptación de la unidad:**
  - [ ] Todo control tiene etiqueta y estado perceptible.
  - [ ] El foco se gestiona en confirmaciones y errores.
  - [ ] Se distingue cancelar de confirmar y Combinar de Reemplazar.
  - [ ] Los mensajes no dependen únicamente de color.
- **Pruebas requeridas:** navegación completa por teclado, foco visible, lector de pantalla disponible, zoom y validación de contraste.
- **Entregables documentales:** checklist de accesibilidad y decisiones de UX.

### U11 — Pruebas automatizadas de aceptación y regresión

- **Épica:** E7
- **Prioridad:** P0
- **Clasificación:** MVP
- **Bloqueada por:** U02, U04, U05, U07, U08, U10
- **Entrega:** suite reproducible que cubre CA-01–CA-20 desde el comportamiento observable, incluyendo persistencia y fallos.
- **Criterios relacionados:** todos los CA-01–CA-20.
- **Criterios de aceptación de la unidad:**
  - [ ] Cada criterio tiene al menos una prueba trazable.
  - [ ] Se prueban límites, errores, cancelaciones, reabrir y atomicidad.
  - [ ] Las pruebas no dependen de red ni de datos personales.
  - [ ] Los fallos de persistencia y cuota están cubiertos.
- **Pruebas requeridas:** dominio, contrato del seam, integración con IndexedDB, aceptación de UI y pruebas de regresión.
- **Entregables documentales:** mapa CA→prueba, instrucciones de ejecución local y política de datos sintéticos.

### U12 — Empaquetado local y documentación open source

- **Épica:** E7
- **Prioridad:** P1
- **Clasificación:** MVP para distribución; no bloquea el diseño
- **Bloqueada por:** U11
- **Entrega:** instrucciones reproducibles para ejecutar localmente, documentación de alcance, privacidad, límites, formato JSON, licencias y contribución.
- **Criterios relacionados:** RNF-01, RNF-06–RNF-09 y restricciones de operación local.
- **Criterios de aceptación de la unidad:**
  - [ ] Una persona puede ejecutar el producto localmente siguiendo la documentación.
  - [ ] Se declara que no existe servidor, autenticación ni sincronización.
  - [ ] Se documenta el respaldo JSON y la pérdida posible del almacenamiento del navegador.
  - [ ] Se incluyen licencia, contribución, código de conducta si aplica y revisión de dependencias.
  - [ ] El empaquetado no incluye datos institucionales, personales o credenciales.
- **Pruebas requeridas:** ejecución desde un entorno limpio y verificación de que no se realizan llamadas de red inesperadas.
- **Entregables documentales:** README, guía de desarrollo, guía de usuario, privacidad, seguridad, formato JSON, límites, licencia y contribución.

## 4. Orden sugerido de implementación

1. **U01** — cerrar contrato de dominio y JSON.
2. **U02** — reglas de dominio y orden.
3. **U03** — flujo de colección y estados.
4. **U05** — persistencia local estructurada.
5. **U04** — eliminación y deshacer.
6. **U06** — exportación.
7. **U07** — validación y vista previa.
8. **U08** — Combinar/Reemplazar atómicos.
9. **U09** — capacidad y recuperación.
10. **U10** — accesibilidad y UX transversal.
11. **U11** — cobertura automatizada completa y regresión.
12. **U12** — empaquetado y documentación open source.

La secuencia permite demostrar temprano el dominio y la colección, y luego integrar persistencia e intercambio sin ocultar la atomicidad. Respeta todos los bloqueos declarados: U06 y U07 esperan U01/U05; U08 espera U05/U07; U09 espera U05/U08; U10 espera U03/U04/U07/U08; U11 espera U02/U04/U05/U07/U08/U10; y U12 espera U11. U06 y U07 pueden desarrollarse en paralelo después de U01/U05 si la coordinación conserva el contrato de intercambio.

## 5. Dependencias resumidas

```text
U01 → U02 → U03
U03 → U04
U02 → U05
U01 + U05 → U06
U01 + U05 → U07
U05 + U07 → U08
U05 + U08 → U09
U03 + U04 + U07 + U08 → U10
U02 + U04 + U05 + U07 + U08 + U10 → U11
U11 → U12
```

## 6. Requisitos documentales open source

Antes de distribuir el producto deben existir:

- README con propósito, alcance, límites y ejecución local.
- Declaración explícita de cero servidor, cero autenticación y datos sintéticos.
- Guía de usuario: alta, edición, estados, orden, exportación, importación, Combinar, Reemplazar y deshacer.
- Especificación JSON v1.0 con ejemplo y política de compatibilidad.
- Guía de recuperación ante cuota, borrado del almacenamiento o archivo inválido.
- Política de privacidad que explique que los datos permanecen en el navegador y no se envían.
- Guía de desarrollo con pruebas, estructura de módulos y seam de persistencia.
- Inventario de dependencias y licencias; instrucciones de empaquetado reproducible.
- Guía de contribución y convenciones para datos sintéticos.
- Checklist de accesibilidad y matriz de navegadores soportados.
- Registro de limitaciones conocidas: deshacer temporal tras cierre/suspensión, cuotas variables y recomendación de 10.000 ideas.

## 7. Definition of Ready del backlog

- [x] Cada unidad tiene una entrega verificable.
- [x] Cada unidad declara prioridad, dependencias y clasificación MVP/posterior.
- [x] Las unidades cruzan dominio, interfaz, persistencia y pruebas cuando corresponde; no son tareas horizontales aisladas sin resultado verificable.
- [x] Cada unidad enlaza requisitos o criterios de aceptación.
- [x] Se incluyen pruebas, documentación y distribución open source.
- [x] El orden sugerido respeta los bloqueos reales.
- [ ] El GATE 2 aprueba el diseño y autoriza transformar estas unidades en trabajo de arquitectura, no en implementación.
- [ ] Se cierran las decisiones técnicas diferidas del documento de diseño.

## 8. Elementos posteriores al MVP

No bloquean el cumplimiento de la primera versión, pero podrían considerarse después de demostrar CA-01–CA-20:

- importadores explícitos para versiones futuras del esquema;
- búsqueda y filtros avanzados;
- mediciones de rendimiento más allá de 10.000 ideas;
- exportación de subconjuntos, si se aprueba como requisito nuevo;
- pruebas ampliadas de compatibilidad entre navegadores;
- mejoras visuales no necesarias para accesibilidad o comprensión de acciones.

No se incluyen sincronización, cuentas, servidor, multiusuario, nube, workflow rígido, papelera permanente ni datos personales: permanecen fuera de alcance.

## 9. Punto de detención

Este backlog queda listo para revisión del GATE 2. GATE 2 solo puede aprobar el diseño y autorizar iniciar arquitectura; Filippo debe definir y documentar la arquitectura técnica, GATE 3 debe aprobarla o rechazarla, y solo un GATE 3 aprobado permite iniciar implementación. Este documento no afirma aprobación, no inicia implementación y no modifica los requisitos aprobados.
