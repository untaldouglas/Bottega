# Arquitectura técnica — PRODUCTO-001 Idea Prioritizer

- **Versión:** 1.0
- **Estado:** propuesta para GATE 3; no autoriza implementación
- **Entradas:** requisitos 1.1, diseño de solución 1.2 y backlog 1.2
- **Alcance:** una colección local por navegador y dispositivo; cero servidor, autenticación, red y datos personales

## 1. Decisión ejecutiva

Se selecciona **TypeScript + Vite sin framework de UI**, con una aplicación web estática y un módulo de dominio independiente del navegador. La persistencia real será **IndexedDB** detrás de un puerto pequeño. La interfaz será DOM accesible, con componentes de presentación simples. La decisión evita sobrecomplejidad en un producto con una sola pantalla principal y un dominio acotado, pero conserva seams sustituibles para persistencia, reloj, identificadores y descarga/selección de archivos.

Se descarta React + Vite para la primera versión: añade runtime, modelo de componentes, convenciones y dependencias sin resolver una necesidad funcional que no esté cubierta por DOM + TypeScript. React podría adoptarse después si la UI supera el alcance actual, sin cambiar dominio, contratos JSON ni puerto de persistencia.

## 2. Comparación de alternativas

| Criterio                    | TypeScript + Vite sin framework                             | TypeScript + React + Vite                                               |
| --------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------- |
| Complejidad inicial         | Menor; una dependencia de build                             | Mayor; runtime, JSX y convenciones adicionales                          |
| Ajuste al alcance           | Alto para formularios, lista, diálogo, vista previa y toast | Alto, pero con capacidad no necesaria inicialmente                      |
| Dominio/persistencia        | Independientes de la UI en ambos casos                      | Independientes de la UI en ambos casos                                  |
| Accesibilidad               | Control directo del DOM y foco                              | Buena, pero depende de disciplina y librería/implementación de diálogos |
| Rendimiento                 | Menor coste de runtime para 10.000 filas                    | Adecuado, requiere estrategia de renderizado y memoización              |
| Test de componentes         | DOM real con navegador                                      | DOM real más pruebas de renderizado/componentes                         |
| Evolución                   | Migrable a React por adaptador de presentación              | Más estructura desde el inicio                                          |
| Dependencias/licencia       | Vite, TypeScript y tooling de pruebas                       | Lo anterior más React y tipos/runtime                                   |
| Riesgo de sobrearquitectura | Bajo                                                        | Medio                                                                   |

**Decisión:** sin framework. No se pretende construir un framework propio: la presentación se divide en módulos por pantalla/flujo, con funciones pequeñas y estado de aplicación explícito.

## 3. Estructura lógica y límites

```text
UI DOM accesible
   ↓ comandos/estado de presentación
Aplicación (casos de uso y orquestación)
   ↓ puertos
Dominio (Idea, colección, reglas, validación, orden)
   ↓ DTOs normalizados
Intercambio JSON ─────── Persistencia IndexedDB
```

### 3.1 Dominio

Responsable de invariantes: Idea, estados, límites de texto, criterios 1–10, prioridad, fechas válidas, etiquetas sin duplicados, identidad, orden determinista y capacidad de la colección resultante. No importa `window`, `File`, `indexedDB`, DOM, JSON ni APIs de red. Recibe dependencias de reloj e identificador por puertos o parámetros.

### 3.2 Aplicación

Coordina crear, editar, cambiar estado, eliminar, deshacer, exportar, previsualizar y aplicar importación. Mantiene la distinción entre estado confirmado y propuesta pendiente. Ejecuta validar → planificar → mostrar vista previa → confirmar → commit. No conoce object stores; solo usa `CollectionRepository` y puertos de archivo/descarga.

### 3.3 UI

Renderiza estado y errores, recoge eventos y envía comandos a la aplicación. No calcula prioridad, no decide conflictos, no valida por segunda vez con reglas divergentes y no escribe directamente en IndexedDB. Gestiona foco, teclado, confirmaciones, mensajes de estado y actualización después del commit.

### 3.4 Intercambio

Convierte texto/bytes JSON en un documento externo versionado, valida forma y contenido completo, calcula diagnósticos y planes para Combinar/Reemplazar, normaliza y mide UTF-8 compacto. Nunca muta la colección ni contiene lógica de almacenamiento.

### 3.5 Persistencia

`IndexedDbCollectionRepository` implementa el puerto y encapsula apertura, versión, stores, índices, transacciones, abortos y errores de cuota. Solo acepta una colección ya validada. El fake en memoria prueba el contrato; `localStorage` no se usa como sustituto transaccional.

## 4. Contratos TypeScript conceptuales

Los siguientes contratos son normativos a nivel conceptual; no son código de implementación.

```ts
type IdeaId = string & { readonly __brand: "IdeaId" };
type Estado =
  "borrador" | "en evaluación" | "aprobada" | "rechazada" | "implementada";
type Score = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

type Idea = Readonly<{
  id: IdeaId;
  titulo: string;
  descripcion: string;
  estado: Estado;
  impacto: Score;
  confianza: Score;
  facilidad: Score;
  prioridad: number;
  creadaEn: string;
  modificadaEn: string;
  etiquetas: readonly string[];
  notas: string;
}>;
type Collection = Readonly<{ ideas: readonly Idea[] }>;
type ExchangeDocument = Readonly<{
  schemaVersion: "1.0";
  exportedAt: string;
  ideas: readonly Idea[];
}>;

type ValidationIssue = Readonly<{
  code: string;
  path: string;
  message: string;
  limit?: string;
  value?: unknown;
}>;
type Result<T> =
  { ok: true; value: T } | { ok: false; issues: readonly ValidationIssue[] };

type CollectionRepository = Readonly<{
  load(): Promise<Result<Collection>>;
  commit(next: Collection): Promise<Result<void>>;
}>;
type Clock = Readonly<{ nowIso(): string }>;
type IdGenerator = Readonly<{ next(): IdeaId }>;
type FileReader = Readonly<{ read(file: File): Promise<Result<Uint8Array>> }>;
type ExportSink = Readonly<{
  download(name: string, bytes: Uint8Array): Result<void>;
}>;

type ImportMode = "combinar" | "reemplazar";
type ImportPreview = Readonly<{
  mode: ImportMode;
  incomingCount: number;
  resultCount: number;
  conflicts: readonly IdeaId[];
  issues: readonly ValidationIssue[];
  normalizedBytes: number;
  limit?: "inputBytes" | "collectionBytes" | "ideaCount";
  proposed: Collection;
}>;
```

Reglas de diseño de los contratos: tipos externos se validan antes de convertirse en `Idea`; el dominio devuelve resultados tipados, no excepciones para errores esperables; no se exponen referencias mutables; `commit` recibe la colección completa y solo resuelve éxito cuando la transacción terminó.

## 5. Modelo de datos e IndexedDB

### 5.1 Base y versión

- Base: `idea-prioritizer`.
- Versión inicial: **1**.
- Se mantiene un registro de metadatos para identificar el formato interno y una colección lógica única.
- El formato externo permanece `schemaVersion: "1.0"`; la versión IndexedDB no se confunde con la versión JSON.

### 5.2 Stores e índices

**Object store `ideas`**

- keyPath: `id`.
- Registro: representación persistible de `Idea`, incluyendo prioridad verificada y fechas ISO.
- Índices: `prioridad` (no único), `modificadaEn` (no único), `estado` (no único). Son índices de consulta; el orden normativo final se aplica en dominio para conservar desempates deterministas.

**Object store `meta`**

- keyPath: `key`.
- Registro único `collection`: `{ key, formatVersion, updatedAt, ideaCount, normalizedBytes }`.
- Sirve para diagnóstico y apertura, no como fuente de verdad separada: la colección se reconstruye de `ideas` y se valida.

No se usa un store de papelera permanente. El snapshot para deshacer vive en memoria durante 10 segundos y solo se persiste al confirmar su restauración.

### 5.3 Lectura y commit

`load` abre una transacción readonly sobre `ideas`, materializa todos los registros, valida invariantes y devuelve una colección ordenada. Si encuentra corrupción o una versión interna no compatible, informa error recuperable y no inventa datos.

`commit` recibe una colección ya validada, abre una única transacción readwrite sobre `ideas` y `meta`, limpia `ideas`, inserta todos los registros y actualiza `meta`; el evento `complete` es el único punto que permite declarar persistencia. Un `error`, `abort` o `QuotaExceededError` conserva la última colección confirmada desde la perspectiva de la aplicación y no actualiza la UI como guardada.

Aunque `clear + put` sea una sola transacción, el adaptador debe probar que una transacción abortada no deja subconjunto visible. Para cargas de hasta 10.000 ideas es preferible esta sustitución completa, simple y verificable, frente a sincronizaciones parciales.

### 5.4 Migraciones

La versión 1 crea stores e índices de forma idempotente en `onupgradeneeded`. No se realiza migración silenciosa del JSON externo. Futuras versiones incrementarán la versión IndexedDB, migrarán registros dentro de la transacción de upgrade, validarán el resultado y conservarán la política de rechazo de documentos externos no compatibles salvo migrador explícito y visible.

Una migración fallida aborta el upgrade; la aplicación muestra que no pudo abrir la colección y no sobrescribe exportaciones. Cada migración futura deberá tener fixture de antes/después, rollback por abort de IndexedDB y prueba en al menos un navegador Chromium y uno Firefox.

## 6. Reglas de mutación y capacidad

Toda mutación prepara una colección resultante completa, recalcula/verifica prioridad, valida cada idea, valida unicidad de IDs y etiquetas, normaliza JSON compacto, mide UTF-8 y cuenta ideas antes de `commit`.

- Entrada de importación: máximo **5 MiB = 5 × 1024 × 1024 bytes**, medido sobre bytes originales, antes de parsear.
- Colección resultante: máximo **4 MiB** de JSON compacto UTF-8 normalizado.
- Colección resultante: máximo **10.000 ideas**.
- Se rechaza por el primer límite alcanzado, con diagnóstico específico.
- La salida de exportación usa el mismo JSON compacto normalizado y debe ser reimportable por `"1.0"`.

La medición debe usar `TextEncoder().encode(compactJson).byteLength`, no longitud de JavaScript ni caracteres. La serialización tiene propiedades en orden estable, sin espacios ni saltos ornamentales; los textos Unicode se conservan y su tamaño se mide en UTF-8. No se normalizan silenciosamente contenidos del usuario.

## 7. Identificadores, fechas y errores

### IDs

Se usará UUID v4 generado por `crypto.randomUUID()` cuando exista; el puerto `IdGenerator` permite fallback controlado solo si conserva suficiente aleatoriedad y valida formato/colisión. Cada importación valida IDs no vacíos, formato admitido y unicidad interna; al combinar, un ID coincide exactamente y actualiza, nunca duplica. Colisión inesperada durante commit aborta la operación.

### Fechas

`creadaEn`, `modificadaEn` y `exportedAt` se almacenan como ISO 8601 UTC producido por `toISOString()`. Se validan como fechas finitas y formato canónico aceptado. La UI muestra una representación local, pero el intercambio conserva UTC. El reloj del dispositivo no se corrige ni se trata como autoridad; si retrocede, el orden sigue siendo determinista y el ID queda como desempate interno no presentado.

### Errores

Taxonomía mínima: `InvalidInput`, `InvalidJson`, `UnsupportedSchema`, `DuplicateId`, `DuplicateTag`, `InconsistentPriority`, `CapacityExceeded`, `StorageUnavailable`, `QuotaExceeded`, `TransactionAborted`, `OperationCancelled` y `UnexpectedFailure`. Cada error esperable incluye código, ruta, mensaje accionable y límite cuando aplica. Los errores se agregan para validación de archivo; un error de aplicación aborta la operación completa. Nunca se muestran stack traces, rutas locales, contenido completo sensible ni detalles de IndexedDB al usuario.

## 8. Navegadores, privado, rendimiento y accesibilidad

### Navegadores y modo privado

Matriz mínima propuesta para GATE 3: últimas dos versiones estables de Chromium, Firefox y Safari en escritorio; soporte móvil se documenta como objetivo secundario hasta probar selección/descarga. Se requiere IndexedDB, `TextEncoder`, `crypto.randomUUID` o fallback aprobado, File API y descarga local. Si IndexedDB no está disponible, la aplicación queda en modo no disponible, sin fingir persistencia.

El modo privado/incógnito puede ofrecer almacenamiento temporal, cuota menor o borrado al cerrar. La aplicación debe detectar fallo de apertura/escritura, mostrar “almacenamiento local no disponible o temporal” y recomendar exportar; nunca prometer persistencia al cerrar. Se prueba explícitamente en cada familia soportada.

### Rendimiento

No se fija un presupuesto inventado antes de medir. Como objetivos verificables de arquitectura: primera interacción después de cargar sin red; validación de 10.000 ideas sin bloquear indefinidamente; operaciones largas con indicador de progreso o estado; renderizado de la lista con actualización por lotes si la medición lo exige. La UI puede paginar o virtualizar la presentación sin alterar la colección completa ni el JSON. La validación debe evitar duplicar copias innecesarias, y la importación debe rechazar 5 MiB antes de parsear.

### Accesibilidad

HTML semántico, etiquetas asociadas, foco visible, orden de tabulación, `aria-describedby` para errores, `aria-live` para estados de guardado/error, diálogo modal con foco atrapado y retorno de foco, confirmación destructiva con botones inequívocos, contraste suficiente y operación completa por teclado. Color no es único indicador. La vista previa anuncia conteos, conflictos y límite excedido. Se prueba zoom, lector de pantalla disponible y navegación sin ratón.

## 9. Seguridad y privacidad resumidas

La superficie es local y sin red: no hay endpoints, autenticación, cookies de aplicación, telemetría ni secretos. El JSON importado se trata como datos: nunca se ejecuta, nunca se inserta como HTML y se escapa al renderizar. Se recomienda CSP sin `unsafe-inline`/`unsafe-eval`, dependencias mínimas fijadas y auditoría de licencias. Los mensajes no deben filtrar rutas o contenido innecesario. La política de privacidad debe declarar almacenamiento local, respaldo manual y riesgo de borrado por navegador/dispositivo.

## 10. Pruebas, Docker y CI propuestos

La estrategia detallada está en `docs/03-test-strategy.md`. En resumen: unitarias para dominio/intercambio, contrato para puertos, integración real de IndexedDB, componentes/DOM para UI y E2E para CA-01–CA-20 y fallos de persistencia. Todo con datos sintéticos y red bloqueada.

Se propone Docker solo como entorno reproducible de desarrollo/CI: imagen Node LTS no privilegiada, instalación reproducible desde lockfile, ejecución de lint/typecheck/tests/build y servidor estático de prueba. No se debe escribir Docker ahora. CI propuesto ejecuta en cada cambio, además de una matriz de navegador en un runner con navegadores instalados. No se crea CI en esta entrega.

## 11. Licencia y dependencias

Propuesta: licencia **MIT** para el producto, pendiente de confirmación del propietario; cada dependencia debe conservar su licencia compatible y aparecer en un inventario. Dependencias de ejecución: ninguna aparte de APIs estándar del navegador. Dependencias de desarrollo propuestas: TypeScript, Vite, runner unitario, DOM runner, Playwright y herramienta de accesibilidad; las versiones concretas se decidirán al implementar y se fijarán en lockfile. No se incorpora librería JSON grande si `JSON.parse/stringify` y validadores propios cubren el contrato; si se adopta un validador, deberá justificar tamaño, licencia y diagnóstico.

## 12. Riesgos y reversibilidad

- **Complejidad IndexedDB:** mitigada por adaptador profundo, fake de contrato y pruebas reales.
- **Cuota/modo privado:** mitigada por exportación, errores explícitos y no declarar guardado antes de `complete`.
- **10.000 filas en UI:** mitigado por medir y aislar renderizado; dominio no depende de estrategia visual.
- **Cambios de esquema:** versión externa exacta, migradores visibles y ADR futuro.
- **Dependencias:** mínimo runtime y revisión de licencia.
- **Reloj/IDs:** puertos sustituibles y validación determinista.

## 13. Definition of Ready para GATE 3

La arquitectura está lista para que GATE 3 decida cuando: los cinco documentos de esta entrega existen y se revisan; los contratos, stores, índices, versión y migraciones están cerrados; los límites y medición UTF-8 están trazados; la matriz de navegadores, modo privado, rendimiento y accesibilidad tiene pruebas propuestas; seguridad, licencia, dependencias, Docker/CI y riesgos tienen responsable; y cada requisito RF/RN/RNF/IE/II y CA-01–CA-20 tiene una prueba o justificación trazable.

### Matriz planificada requerida para GATE 3

GATE 3 debe verificar que existe una matriz de pruebas especificadas y trazadas, con cada fila etiquetada inequívocamente **planificada/no ejecutada**; no son resultados ejecutados. La matriz tendrá al menos estas filas y un procedimiento definido para completarlas después de implementar:

| Área        | Contrato o alcance                                                         | Prueba planificada                                               | Trazabilidad                            |
| ----------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------- |
| Errores     | Taxonomía de validación, cuota, abort y almacenamiento no disponible       | Unitarias, contrato de repositorio e integración de fallo        | RF/RNF, CA-15 y CA-19                   |
| IndexedDB   | Versión 1, stores, índices, upgrade y migraciones futuras                  | Apertura, upgrade, fixture antes/después y abort                 | ADR-0002, RF-07/RF-08                   |
| Navegadores | Últimas dos versiones estables de Chromium, Firefox y Safari de escritorio | E2E de persistencia, intercambio, modo privado y APIs requeridas | RNF-01/RNF-08, matriz de compatibilidad |
| Capacidad   | 5 MiB, 4 MiB, 10.000, UTF-8 y primer límite                                | Pruebas de frontera y preservación del snapshot                  | RNF-02–RNF-04, CA-11, CA-15, CA-19      |
| Producto    | CA-01–CA-20                                                                | Suite unitaria, integración, componentes y E2E                   | Backlog U11 y matriz CA→prueba          |

Para GATE 3, cada fila debe tener contrato, caso de prueba, criterio cubierto, datos sintéticos y resultado esperado. No se exige fecha, navegador ejecutado ni artefacto porque la implementación aún está prohibida.

### Evidencia ejecutada para GATE 4 y validación independiente

Después de GATE 3 y de la implementación, la matriz se convertirá en una tabla de resultados reales con: identificador exacto de prueba, versión del documento, estado y salida observada, fecha de ejecución, entorno y versión exacta del navegador cuando aplique, y referencia reproducible al reporte, log, fixture o captura. GATE 4/validación independiente comprobará que cada fila tiene evidencia; una fila faltante o no reproducible impide cerrar GATE 4, pero no convierte GATE 3 en un gate circular.

Esta documentación **no declara GATE 3 aprobado** y no autoriza implementación.
