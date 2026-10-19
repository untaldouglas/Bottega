# Diseño de solución — Idea Prioritizer

- **Producto:** Idea Prioritizer
- **Documento:** 02 — Solution Design
- **Versión del diseño:** 1.2
- **Entrada:** `docs/01-product-requirements.md`, versión 1.1
- **Estado de entrada:** corregido para revisión del GATE 1 de requisitos; GATE 1 aprobado
- **Estado de este documento:** propuesta para revisión del GATE 2; no constituye aprobación de arquitectura
- **Ámbito:** un navegador y un dispositivo; cero servidor; cero autenticación

### Registro breve de cambios de la versión 1.2

- Se valida la colección resultante completa después de calcular Combinar o Reemplazar, incluyendo bytes UTF-8 compactos y cantidad de ideas, con rechazo atómico y límites visibles en la vista previa.
- Se declara el invariante de capacidad para toda mutación de colección y se añaden pruebas de cruces de límite y preservación exacta del estado previo.
- Se corrige la frontera de gates: GATE 2 aprueba diseño y autoriza iniciar arquitectura; GATE 3 decide la arquitectura y solo su aprobación permite implementar.

### Registro breve de cambios de la versión 1.1

- Se reemplaza la política ambigua de capacidad por límites independientes de archivo de entrada, JSON normalizado y cantidad de ideas, aplicando el primer límite alcanzado.
- Se exige exportación JSON compacta y reimportable por la misma versión, con rechazo atómico ante cualquier exceso.
- Se distingue IndexedDB como adaptador real recomendado, el adaptador en memoria como fake de contrato y `localStorage` como alternativa de prototipo, no como fake transaccional.
- Se incorporan pruebas de frontera de bytes, cantidad y round-trip de exportación/importación.

## 1. Resumen de requisitos recibidos

El producto debe permitir al usuario gestor crear, consultar, editar, ordenar, evaluar, cambiar de estado y eliminar ideas. Cada idea tiene identidad generada, título, descripción, estado, impacto, confianza, facilidad, prioridad calculada, fechas gestionadas, etiquetas y notas.

La prioridad es `impacto × confianza × facilidad`, con rango 1–1000. El listado ordena por prioridad descendente, `modificadaEn` descendente y título alfabético. Las entradas nuevas comienzan en `borrador`; el usuario puede cambiar manualmente entre los cinco estados válidos.

La colección debe persistir automáticamente en el navegador y recuperarse tras cerrar y abrirlo en el mismo dispositivo. Debe existir exportación JSON completa e importación JSON con validación completa, vista previa, confirmación explícita, modos **Combinar** y **Reemplazar**, rechazo total ante errores y aplicación atómica. La eliminación requiere confirmación y ofrece deshacer durante 10 segundos.

La trazabilidad base es la de los requisitos RF-01–RF-16, RN-01–RN-16, RNF-01–RNF-09, IE-01–IE-06, II-01–II-11 y CA-01–CA-20. No se altera ningún requisito aprobado.

## 2. Confirmación de versión y estado del documento de requisitos

La lectura completa de `docs/01-product-requirements.md` confirma:

- Versión: **1.1**.
- Estado declarado: **corregido para revisión del GATE 1 de requisitos**.
- GATE vigente comunicado: **GATE-1 APROBADO**.
- El propio documento deja sin definir la arquitectura, el framework y el proveedor de almacenamiento.
- Las decisiones diferidas explícitas incluyen los nombres exactos del JSON y los límites de volumen; el resto de este documento propone resolverlas sin contradecir los requisitos.

No se encontraron contradicciones bloqueantes en los requisitos recibidos. La casilla de Definition of Done relativa a no escribir código requiere verificación del repositorio/proceso; este entregable no escribe código ni inicializa frameworks.

## 3. Restricciones y principios

### Restricciones obligatorias

- Una sola colección por navegador y dispositivo.
- Cero servidor, API remota, autenticación, cuentas, multiusuario o sincronización.
- Cero información institucional o personal; únicamente datos sintéticos.
- Almacenamiento local del navegador y respaldo explícito mediante JSON.
- Sin workflow rígido, papelera permanente, historial de versiones ni auditoría remota.
- No inicializar frameworks, `package.json`, CI, Docker ni configuración de despliegue como parte de esta etapa.
- Preparación para ejecución local y distribución open source reproducible.

### Principios de diseño

1. **Datos primero:** el archivo JSON exportado es el respaldo portable y legible por humanos; el almacenamiento del navegador no se considera respaldo.
2. **Validar antes de mutar:** ninguna ruta de importación puede cambiar la colección antes de completar sintaxis, esquema, estructura, reglas de dominio, duplicados y capacidad.
3. **Atomicidad observable:** una operación aplicada produce la colección nueva completa o conserva exactamente la colección anterior.
4. **Determinismo:** validación, conflictos y ordenamiento deben producir el mismo resultado con los mismos datos.
5. **Seam único y profundo:** concentrar reglas de dominio, validación, serialización y selección de almacenamiento detrás de interfaces pequeñas. La interfaz es también la superficie de pruebas.
6. **Privacidad por minimización:** no agregar metadatos de usuario, telemetría, identificadores institucionales ni llamadas externas.
7. **Reversibilidad:** preferir decisiones que permitan cambiar el adaptador de persistencia sin alterar la experiencia ni el formato de intercambio.

## 4. Alternativas consideradas

### A. Aplicación web específica con persistencia local sencilla

Una aplicación web pequeña, específica del producto, que mantiene la colección como un documento serializado en `localStorage`. La lógica de dominio, validación, importación/exportación y presentación se construiría para PRODUCTO-001.

- **Fortaleza:** mínima superficie técnica inicial; facilidad de ejecución local y empaquetado.
- **Debilidad:** `localStorage` es síncrono y limitado; la escritura de una colección completa puede bloquear la interfaz y ofrece menos margen para evolución y transacciones estructuradas.
- **Atomicidad:** posible mediante preparar y validar un documento completo antes de una única sustitución, pero con menor margen ante fallos de cuota o crecimiento.

### B. Aplicación web específica con persistencia local estructurada

Una aplicación web pequeña, específica del producto, con un módulo de dominio profundo y un adaptador de persistencia basado en IndexedDB. El adaptador mantiene un documento/catálogo versionado, usa transacciones para sustituir o combinar la colección y separa validación, migraciones explícitas y almacenamiento.

- **Fortaleza:** mejor encaje con importación atómica, evolución de esquema, colecciones mayores y operaciones asíncronas.
- **Debilidad:** más complejidad inicial y mayor necesidad de pruebas de apertura, transacciones, errores de cuota y recuperación.
- **Atomicidad:** la alternativa más sólida dentro de las restricciones; la transacción de almacenamiento complementa la regla de no mutar antes de confirmar.

### C. Adaptación de una solución open source existente

Seleccionar y adaptar una herramienta existente de gestión/priorización de ideas para eliminar servidor, autenticación y datos remotos, y ajustarla al modelo, cálculo, importación, exportación y accesibilidad requeridos.

- **Fortaleza:** podría aportar componentes maduros de interfaz, pruebas o importación.
- **Debilidad:** es improbable que coincida exactamente con el modelo y las restricciones; puede introducir dependencias, deuda de adaptación, telemetría, licencia incompatible o arquitectura remota.
- **Atomicidad:** depende de la arquitectura de la solución elegida y puede requerir reemplazar buena parte de su persistencia.

## 5. Matriz comparativa

Escala: **5** = muy favorable, **3** = aceptable con trabajo, **1** = desfavorable. La puntuación no sustituye al análisis cualitativo.

| Criterio                                  | A: específica + `localStorage` | B: específica + IndexedDB |        C: adaptar open source |
| ----------------------------------------- | -----------------------------: | ------------------------: | ----------------------------: |
| Cumplimiento de requisitos                |                              4 |                         5 |     2–4, depende del proyecto |
| Complejidad funcional                     |                              4 |                         4 |                             2 |
| Complejidad técnica                       |                      5 inicial |    3 inicial / 4 a escala | 2 inicial / 1 tras adaptación |
| Mantenibilidad                            |                              3 |                         5 |                           2–3 |
| Experiencia de usuario                    |                              4 |                         5 |                           2–4 |
| Persistencia y recuperación               |                              3 |                         5 |                           2–4 |
| Atomicidad de importación                 |                              3 |                         5 |                           2–4 |
| Pruebas automatizadas                     |                              4 |                         4 |                           2–3 |
| Seguridad y privacidad                    |                              5 |                         5 |                           2–4 |
| Accesibilidad                             |                              4 |                         4 |                           2–4 |
| Operación local                           |                              5 |                         4 |                           2–3 |
| Empaquetado reproducible                  |                              5 |                         4 |                           2–3 |
| Facilidad para compartir como open source |                              5 |                         5 |                           2–3 |
| Dependencia de terceros                   |                              5 |                         4 |                           1–3 |
| Riesgo de alcance                         |                              5 |                         4 |                             2 |
| Reversibilidad                            |                              4 |                         5 |                             2 |
| Costo de evolución                        |                              3 |                         5 |                             2 |

### Comparación cualitativa

| Alternativa | Decisión                                | Motivo principal                                                                                                                           |
| ----------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| A           | Viable como prototipo o MVP muy pequeño | La experiencia puede cumplir, pero el almacenamiento síncrono y el límite práctico hacen más frágil la evolución y el manejo de capacidad. |
| B           | **Recomendada**                         | Entrega una aplicación específica, local y portable, con un seam claro para persistencia, transacciones, validación y evolución explícita. |
| C           | No construir/adaptar por ahora          | El costo de descubrir, auditar, despojar y adaptar una solución externa supera el valor para un dominio pequeño y restricciones estrictas. |

## 6. Recomendación

### Alternativa recomendada: B

Construir una aplicación web específica para PRODUCTO-001, sin servidor, con un módulo de dominio profundo y un adaptador de persistencia local estructurada basado en IndexedDB. Mantener el formato JSON de intercambio independiente del almacenamiento interno.

La recomendación se justifica por cuatro razones:

1. **Atomicidad:** IndexedDB organiza lecturas y escrituras en transacciones asíncronas; es un mejor soporte para preparar una nueva colección y comprometerla completa.
2. **Evolución:** un catálogo versionado y migraciones explícitas permiten evolucionar sin convertir silenciosamente archivos incompatibles.
3. **Capacidad:** la colección sintética puede superar con holgura el tamaño cómodo de `localStorage`, aunque las cuotas reales siguen dependiendo del navegador.
4. **Reversibilidad:** la interfaz del adaptador deja abierta una alternativa de `localStorage` para prototipos explícitos, sin cambiar el dominio ni el JSON; no se usa como fake de IndexedDB ni como evidencia de atomicidad transaccional.

La recomendación no autoriza todavía implementación ni constituye aprobación del gate. GATE 2 aprueba el diseño y autoriza iniciar arquitectura; Filippo define y documenta la arquitectura técnica; GATE 3 aprueba o rechaza la arquitectura; solo GATE 3 aprobado permite iniciar implementación.

## 7. Decisiones funcionales y técnicas de alto nivel

### 7.1 Módulos y seams

1. **Módulo de dominio de ideas:** crea, actualiza, elimina, calcula prioridad, valida reglas y ordena. No conoce APIs del navegador.
2. **Módulo de intercambio JSON:** parsea, valida, diagnostica, previsualiza y serializa. Produce un plan de aplicación sin mutar la colección.
3. **Módulo de aplicación:** coordina confirmaciones, modos Combinar/Reemplazar, deshacer de 10 segundos y persistencia.
4. **Seam de persistencia:** interfaz pequeña para leer la colección vigente y comprometer una colección completa. El adaptador inicial es IndexedDB.
5. **Interfaz de usuario:** consume resultados y errores comprensibles; no duplica reglas de dominio.

La interfaz de persistencia debe aceptar una colección ya validada y devolver éxito o error; no debe exponer detalles de object stores al resto de la aplicación. Las pruebas del dominio y del intercambio deben poder ejecutarse sin navegador.

### 7.2 Decisiones diferidas del GATE 1

#### 1. Nombres definitivos de propiedades JSON

Se adopta `camelCase`, coherente con los nombres del documento de requisitos:

- Documento: `schemaVersion`, `exportedAt`, `ideas`.
- Idea: `id`, `titulo`, `descripcion`, `estado`, `impacto`, `confianza`, `facilidad`, `prioridad`, `creadaEn`, `modificadaEn`, `etiquetas`, `notas`.

No se añaden propiedades desconocidas en la exportación inicial. `prioridad`, `creadaEn` y `modificadaEn` se conservan para respaldar el estado, pero se vuelven a verificar contra las reglas antes de aceptar una importación.

#### 2. Versión inicial del esquema

`schemaVersion: "1.0"`.

La versión pertenece al documento de intercambio completo, no a cada idea. La exportación siempre incluye `schemaVersion`, `exportedAt` e `ideas`; `ideas` puede ser una lista vacía válida.

#### 3. Compatibilidad de versiones

La versión inicial acepta exactamente `"1.0"`. Versiones desconocidas, ausentes o con formato incompatible se rechazan antes de la vista de aplicación. No se realiza conversión silenciosa.

Una futura versión deberá declarar una política explícita: compatibilidad directa, migrador determinista o rechazo. Si una migración futura se admite, debe conservar el archivo original sin modificar y mostrar el resultado de la conversión antes de confirmar.

#### 4. Política de capacidad de importación, colección y exportación

La política operativa adopta tres límites independientes:

- **Archivo de entrada:** máximo de **5 MiB (5 × 1024 × 1024 bytes)**, medidos sobre el archivo antes de parsearlo.
- **Colección normalizada:** máximo de **4 MiB (4 × 1024 × 1024 bytes)** para la representación JSON compacta y normalizada de la colección, después de parsear y validar todas las reglas.
- **Cantidad:** techo preventivo de **10.000 ideas** por colección.

Se aplica el primer límite alcanzado: bytes normalizados o cantidad. Por tanto, 10.000 ideas es un techo preventivo y no una capacidad garantizada; una colección puede ser rechazada antes por superar 4 MiB normalizados, y una colección menor también puede ser rechazada si excede ese límite de bytes. La medición normalizada usa JSON UTF-8 compacto, sin espacios ni formato ornamental, y la exportación debe producir exactamente ese formato compacto.

El margen entre 4 MiB normalizados y 5 MiB de entrada cubre metadatos, formato y archivos con espacios, y preserva la portabilidad del respaldo. El límite de entrada se comprueba antes de parsear; el límite normalizado y el de cantidad se comprueban después de validar la colección y antes de aplicar cualquier cambio.

Una operación que exceda cualquiera de los límites se rechaza atómicamente: no se muestra como aplicada, no se guarda un subconjunto y se conserva exactamente el último estado confirmado. La cuota efectiva del navegador continúa siendo una restricción adicional: una escritura puede fallar aun por debajo de estos límites y debe conservar igualmente el estado anterior.

**Invariante general de capacidad:** toda mutación que pueda aumentar o modificar la colección —crear, editar, deshacer una eliminación o aplicar una importación— debe normalizar y validar el tamaño UTF-8 compacto y la cantidad de ideas de la colección resultante antes del commit. Ningún estado persistido puede superar 4 MiB compactos ni 10.000 ideas. El rechazo conserva exactamente la colección anterior y expone el límite excedido.

Todo archivo generado por la función de exportación debe poder ser reimportado por la misma versión del producto, sujeto a la misma validación y límites. La exportación de una colección aceptada debe, por diseño, generar un JSON compacto que no exceda el límite normalizado.

#### 6. Falta de espacio en el navegador

Ante `QuotaExceededError`, almacenamiento no disponible, transacción abortada u otro error de capacidad:

- conservar intacta la última colección confirmada;
- no mostrar la operación como guardada;
- no aplicar subconjuntos;
- mostrar un error comprensible y accionable;
- ofrecer exportar la colección vigente si todavía es posible;
- recomendar liberar espacio del sitio o reducir la colección/archivo;
- permitir reintentar.

La UI debe distinguir “cambio en memoria aún no guardado” de “cambio persistido”. Cerrar o recargar después de un fallo no debe fingir recuperación de un cambio no confirmado.

#### 7. Criterio para IndexedDB, fake en memoria y `localStorage`

- **IndexedDB es el adaptador real recomendado** para la entrega: proporciona persistencia local estructurada y transacciones asíncronas que deben verificarse con pruebas de commit y aborto.
- **El adaptador en memoria es un fake de pruebas de contrato**: permite probar el seam, reglas de aplicación y escenarios deterministas sin depender del navegador; no representa persistencia ni sustituye las pruebas de IndexedDB.
- **`localStorage` queda únicamente como alternativa de prototipo**: puede servir para explorar una implementación mínima, pero no es el fake de IndexedDB ni evidencia de atomicidad transaccional. No se recomienda para la entrega.

Otra tecnología local solo sería admisible si conserva el mismo seam, mantiene cero servidor, ofrece atomicidad verificable, es reproducible sin dependencias innecesarias y demuestra ventajas mediante una prueba de capacidad y recuperación.

## 8. Formato lógico del JSON

Ejemplo no normativo de forma, con datos sintéticos:

```json
{
  "schemaVersion": "1.0",
  "exportedAt": "2026-01-01T12:00:00.000Z",
  "ideas": [
    {
      "id": "idea-01",
      "titulo": "Reducir tiempo de revisión",
      "descripcion": "Explorar una mejora sintética para el proceso.",
      "estado": "en evaluación",
      "impacto": 8,
      "confianza": 5,
      "facilidad": 6,
      "prioridad": 240,
      "creadaEn": "2026-01-01T11:00:00.000Z",
      "modificadaEn": "2026-01-01T11:30:00.000Z",
      "etiquetas": ["proceso", "experimento"],
      "notas": "Validar con datos sintéticos."
    }
  ]
}
```

La importación valida tipos, campos requeridos, estados, rangos, límites de texto, duplicados de etiquetas, unicidad de `id`, fechas y coherencia de prioridad. Los errores se agregan a un diagnóstico comprensible; la colección solo se reemplaza o combina tras confirmación.

### Plan lógico de importación

1. Comprobar selección y tamaño del archivo.
2. Leer el archivo completo sin tocar la colección vigente.
3. Parsear JSON.
4. Validar `schemaVersion`, estructura y todas las ideas.
5. Detectar duplicados internos y conflictos con la colección local.
6. Calcular el resultado hipotético de Combinar o Reemplazar; en Combinar incluye ideas locales nuevas o actualizadas por el archivo, y en Reemplazar coincide con la colección importada.
7. Normalizar la colección resultante completa a JSON UTF-8 compacto, medir sus bytes y contar sus ideas; rechazar si supera 4 MiB o 10.000 ideas.
8. Mostrar conteos, conflictos, errores y el límite excedido, si lo hay, en la vista previa.
9. Esperar confirmación explícita sin mutar la colección vigente.
10. Comprometer el resultado completo en una transacción de persistencia.
11. Actualizar la vista solo después del compromiso exitoso.

### Pruebas de frontera de capacidad y portabilidad

- Archivo de entrada de exactamente 5 MiB: se evalúa según el formato de archivo y continúa al parseo si no excede el límite; archivo por encima de 5 MiB: se rechaza antes de parsear y sin mutación.
- Colección normalizada de exactamente 4 MiB: se acepta si también cumple la cantidad y las demás reglas; colección por encima de 4 MiB: se rechaza antes de confirmar y sin mutación.
- Colección de exactamente 10.000 ideas: se evalúa como techo preventivo y solo se acepta si cumple el límite normalizado; colección de 10.001 ideas: se rechaza atómicamente.
- Colección local de 3 MiB más una importación Combinar de 3 MiB: se mide la colección resultante completa (incluidas ideas locales nuevas o actualizadas) y se rechaza por superar 4 MiB, mostrando ese límite y preservando exactamente el estado anterior.
- Reemplazar con resultado dentro de 4 MiB y hasta 10.000 ideas: se acepta; Reemplazar fuera de cualquiera de esos límites: se rechaza antes del commit, muestra el límite excedido y conserva exactamente la colección anterior.
- Crear, editar y deshacer una eliminación que harían superar 4 MiB o 10.000 ideas: cada operación se rechaza antes del commit, muestra el límite excedido y preserva exactamente la colección anterior.
- Para toda colección aceptada, exportar y reimportar el archivo completo con la misma versión debe conservar la colección, identidad, campos y reglas; el archivo exportado se verifica como JSON compacto y reimportable.

## 9. Límites, capacidad y recuperación

- El almacenamiento local puede ser borrado por el usuario, el navegador o políticas del dispositivo; la exportación JSON es el respaldo explícito.
- La cuota real varía por navegador, modo privado, origen y dispositivo; nunca se debe prometer una capacidad fija de almacenamiento persistente.
- Antes de operaciones de alto volumen se puede estimar disponibilidad cuando el navegador lo permita, pero la operación real debe seguir manejando errores de cuota.
- Una transacción abortada conserva la colección anterior.
- El deshacer de 10 segundos es temporal y no se promete después de cerrar, suspender o recargar la página.
- No hay papelera ni recuperación histórica permanente.

## 10. Riesgos y mitigaciones

| Riesgo                                          | Impacto                                             | Mitigación                                                                                                                                                           |
| ----------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cuota insuficiente o almacenamiento borrado     | Pérdida aparente o real de datos                    | Exportación explícita, manejo de cuota, no sobrescribir el último estado confirmado, mensajes accionables                                                            |
| Complejidad de IndexedDB                        | Errores de transacción y pruebas más difíciles      | Encapsular en un adaptador profundo; pruebas de contrato y de recuperación                                                                                           |
| Archivo grande o JSON malicioso                 | Bloqueo, consumo de memoria o mala UX               | Límite de 5 MiB antes de parsear, límite de 4 MiB normalizado y techo preventivo de 10.000 ideas, validación completa, errores agregados, sin ejecución de contenido |
| Esquema futuro incompatible                     | Importaciones incorrectas                           | Versión exacta, rechazo explícito, migradores futuros separados y visibles                                                                                           |
| Reloj del dispositivo inconsistente             | Orden de desempate inesperado                       | Conservar fechas ISO, documentar supuesto y usar `id` solo como desempate interno no presentado                                                                      |
| Datos derivados inconsistentes                  | Prioridad incorrecta                                | Recalcular/verificar prioridad durante validación; no permitir edición directa                                                                                       |
| Dependencia externa introducida accidentalmente | Privacidad o falta de reproducibilidad              | Cero red por diseño, revisión de dependencias y documentación de empaquetado                                                                                         |
| Accesibilidad insuficiente en confirmaciones    | Errores de uso o acciones destructivas accidentales | Pruebas con teclado, foco, etiquetas, mensajes de estado y lector de pantalla                                                                                        |

## 11. Trazabilidad hacia requisitos y criterios de aceptación

| Decisión del diseño                                            | Requisitos cubiertos                | Criterios cubiertos |
| -------------------------------------------------------------- | ----------------------------------- | ------------------- |
| Módulo de dominio y formulario validado                        | RF-01–RF-06, RN-01–RN-08            | CA-01–CA-09, CA-20  |
| Adaptador local automático                                     | RF-07–RF-08, RNF-01, RNF-08         | CA-10               |
| JSON versionado con propiedades definitivas                    | RF-09, IE-01–IE-06, RNF-06–RNF-07   | CA-11               |
| Pipeline parsear-validar-previsualizar-confirmar               | RF-10–RF-12, II-01–II-05            | CA-12, CA-15, CA-16 |
| Modos Combinar y Reemplazar                                    | RF-13, RN-12–RN-13, II-06–II-08     | CA-13–CA-14         |
| Transacción y resultado completo                               | RF-14, RN-11, RN-14, RNF-02         | CA-15, CA-19        |
| Confirmación y deshacer temporal                               | RF-15–RF-16, RN-10                  | CA-17–CA-18         |
| Manejo de cuota y límites de entrada, normalización y cantidad | RNF-01–RNF-05                       | CA-10, CA-11, CA-15 |
| Sin servidor, sin identidad y datos sintéticos                 | Alcance y exclusiones de sección 12 | CA-11               |

## 12. Elementos expresamente diferidos al gate técnico posterior

Para evitar que esta etapa se convierta en implementación, quedan deliberadamente para el siguiente gate:

- elección del mecanismo concreto de empaquetado y servidor estático de desarrollo local;
- diseño físico de object stores, índices y política de transacción de IndexedDB;
- estrategia exacta de generación de identificadores y prueba de colisiones;
- librería o implementación concreta de validación JSON, si se usa alguna;
- presupuesto de rendimiento medido con 1.000, 5.000 y 10.000 ideas sintéticas;
- matriz concreta de navegadores soportados y prueba de modo privado;
- taxonomía final de mensajes de error y textos de interfaz;
- selección final de herramientas de pruebas automatizadas;
- reglas de licencias y revisión de dependencias del empaquetado open source.

Estos puntos no contradicen requisitos aprobados; son decisiones de arquitectura o ejecución que deben cerrarse antes de construir.

## 13. Definition of Ready para arquitectura

La arquitectura está **lista para pasar a diseño técnico detallado** cuando todas estas condiciones estén satisfechas:

- [x] Se conoce el problema, alcance y restricciones.
- [x] Se compararon tres alternativas: construir con persistencia sencilla, construir con persistencia estructurada y adaptar open source.
- [x] Se recomienda una alternativa y se explican sus motivos.
- [x] El formato lógico JSON y los nombres iniciales están definidos.
- [x] La versión inicial y la regla de rechazo de incompatibles están definidas.
- [x] Hay límites iniciales de archivo y colección, con carácter y justificación explícitos.
- [x] Existe comportamiento definido ante falta de capacidad.
- [x] La atomicidad y el orden de no mutación están descritos.
- [x] Se identificaron módulos, interfaces, seam y responsabilidades.
- [x] Hay riesgos, mitigaciones y criterios de reversibilidad.
- [x] La trazabilidad cubre requisitos y criterios de aceptación.
- [x] Se enumeraron decisiones diferidas sin ocultarlas como decisiones aprobadas.
- [ ] GATE 2 aprueba el diseño y autoriza transformar el diseño en trabajo de arquitectura; las decisiones técnicas diferidas se cierran durante arquitectura y se evalúan en GATE 3.
- [ ] Filippo define y documenta la arquitectura técnica.
- [ ] GATE 3 aprueba la arquitectura; solo entonces se autoriza iniciar implementación.

**Conclusión:** la Definition of Ready está cumplida para revisión y decisión del GATE 2, pero no afirma aprobación. La aprobación de GATE 2 solo autorizaría iniciar arquitectura; la implementación queda bloqueada hasta un GATE 3 aprobado.

## 14. Fuentes de investigación técnica

- MDN, _Web Storage API_: `localStorage` persiste al cerrar y reabrir el navegador, pero las operaciones de Web Storage son síncronas: <https://developer.mozilla.org/en-US/docs/DOM/Storage>
- MDN, _Storage quotas and eviction criteria_: Web Storage tiene límites por origen y puede producir `QuotaExceededError`; las cuotas varían según navegador y contexto: <https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria>
- MDN, _IndexedDB API_: API local asíncrona para almacenamiento estructurado: <https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API>
- MDN, _IDBTransaction_: lecturas y escrituras de IndexedDB se realizan dentro de transacciones: <https://developer.mozilla.org/en-US/docs/Web/API/IDBTransaction>

Estas fuentes respaldan la comparación tecnológica; no sustituyen las pruebas concretas del producto.
