# Estrategia de pruebas — PRODUCTO-001

- **Versión:** 1.0
- **Estado:** propuesta para GATE 3; no autoriza implementación
- **Objetivo:** demostrar RF-01–RF-16, RN-01–RN-16, RNF-01–RNF-09, IE-01–IE-06, II-01–II-11 y CA-01–CA-20 sin red ni datos personales.

## 1. Principios

- Probar comportamiento observable y contratos, no detalles accidentales.
- Validar cada mutación antes de commit y comparar estado exacto antes/después ante rechazo.
- Usar reloj, generador de IDs y repositorio inyectables.
- Todos los fixtures son sintéticos, reproducibles y pequeños salvo pruebas de capacidad.
- La red se bloquea en CI y E2E; cualquier request inesperado falla la prueba.
- Cada caso enlaza al criterio CA correspondiente.

## 2. Pirámide y herramientas propuestas

### Unitarias de dominio e intercambio

Runner TypeScript (herramienta concreta pendiente de implementación). Cubren creación, edición, estados, prioridad, orden, etiquetas, fechas, IDs, validación JSON, diagnósticos, planes de Combinar/Reemplazar, serialización y medición UTF-8. No requieren DOM ni IndexedDB.

Casos mínimos: score 1/10 válido y 0/11 inválido; título 120/121; descripción 2.000/2.001; prioridad 240 y rango 1–1000; los cinco estados y transiciones libres; etiquetas duplicadas; prioridad inconsistente; fechas inválidas; ID duplicado; esquema ausente/desconocido; JSON vacío válido solo con estructura correcta.

### Contratos de puertos

La misma suite se ejecuta contra fake en memoria y adaptador IndexedDB. Verifica `load`, `commit`, reapertura, actualización sin duplicado, error sin falso éxito y preservación del último estado.

### Integración IndexedDB

Prueba en navegador real y base aislada por caso: creación de stores/índices, `clear + put` dentro de transacción, evento `complete`, `abort`, `QuotaExceededError` simulado donde sea posible, almacenamiento no disponible, upgrade de versión y fixtures de migración. Después de cualquier fallo, `load` debe devolver exactamente el snapshot anterior.

### Componentes/DOM

Prueba formularios, lista, edición, selector de estado, confirmación, vista previa, mensajes, foco y deshacer usando DOM real. Verifica que la UI solo muestra “guardado” tras resolver `commit`, no duplica reglas y no muta antes de confirmar.

### E2E

Playwright o equivalente, en Chromium/Firefox/WebKit según disponibilidad. Flujos CA-01–CA-20: alta, edición, orden, persistencia, exportar, importar, Combinar, Reemplazar, cancelar, errores, eliminación/deshacer/expiración, accesibilidad básica y bloqueo de red.

## 3. Matriz de aceptación

| Criterios    | Cobertura mínima                                                |
| ------------ | --------------------------------------------------------------- |
| CA-01–CA-06  | Unitarias de dominio + componente de formulario                 |
| CA-07–CA-09  | Dominio/orden + interacción de lista                            |
| CA-10        | Integración IndexedDB + E2E de cerrar/abrir contexto            |
| CA-11        | Serialización, privacidad por inspección, round-trip y descarga |
| CA-12, CA-16 | Plan/vista previa y E2E de cancelar sin mutación                |
| CA-13–CA-15  | Plan, integración transaccional y E2E de modos/errores          |
| CA-17–CA-18  | Reloj controlado, componente y E2E de deshacer/expiración       |
| CA-19        | Abort/cuota y comparación exacta de snapshot                    |
| CA-20        | Validación unitaria y flujo de importación                      |

La implementación debe mantener un mapa CA→nombre de prueba y fallar CI si un criterio queda sin cobertura.

## 4. Capacidad y fronteras

Generar fixtures sintéticos deterministas para:

- Archivo exactamente 5 MiB: continúa al parseo si es JSON válido; por encima: rechazo antes de parsear.
- Colección normalizada exactamente 4 MiB: acepta si cumple reglas; por encima: rechaza.
- Exactamente 10.000 ideas: solo acepta si también cumple bytes; 10.001: rechaza.
- Colección local 3 MiB + Combinar 3 MiB: medir resultado completo y rechazar preservando snapshot.
- Reemplazar dentro/fuera de 4 MiB.
- Crear, editar y deshacer que cruzan 4 MiB o 10.000.
- Unicode multibyte, emojis y caracteres combinados para demostrar que se mide UTF-8, no `string.length`.
- Exportar cada colección aceptada y reimportar por la misma versión, comparando identidad, campos, prioridad y fechas.

La prueba de round-trip compara una forma canónica de colección, no el orden incidental de propiedades del objeto en memoria.

## 5. Accesibilidad

Automatizar reglas estáticas disponibles y complementar con revisión manual: teclado completo, foco visible, foco inicial y retorno en diálogo, escape/cancelación, etiquetas, errores asociados, `aria-live`, contraste, zoom 200% y ausencia de dependencia exclusiva del color. Incluir al menos una pasada con lector de pantalla por navegador objetivo disponible.

## 6. Compatibilidad y modo privado

Matriz propuesta: últimas dos versiones estables de Chromium, Firefox y Safari de escritorio; móvil se prueba como objetivo secundario. En cada familia: alta, reapertura, exportación/importación, IndexedDB no disponible, cuota/rechazo y cierre de modo privado. Registrar diferencias reales, sin prometer capacidades que no se hayan verificado.

## 7. Seguridad y privacidad en pruebas

- Bloquear red y fallar requests.
- Inspeccionar que exportación no contiene credenciales, telemetría ni campos desconocidos.
- Importar strings con HTML/JS y comprobar renderizado como texto, nunca ejecución.
- Probar JSON profundamente anidado o con campos inesperados contra límites/diagnósticos sin crashear.
- Verificar que errores no exponen stack, rutas locales ni contenido innecesario.
- Auditar dependencias y licencias en CI.

## 8. CI y Docker propuestos

Sin crear archivos en esta entrega: CI ejecutará instalación reproducible desde lockfile, typecheck, lint, unitarias, integración, build, E2E, accesibilidad y auditoría de dependencias. Docker proporcionará Node LTS no root y servidor estático de prueba; la red de tests permanecerá bloqueada. Los artefactos serán reportes y trazas sintéticas, nunca bases de usuario.

## 9. Criterios de salida documentales para GATE 3 y evidencia para GATE 4

Para GATE 3, todos los CA deben tener una prueba **planificada/no ejecutada**, trazable y etiquetada como tal; las fronteras de capacidad, round-trip, abort/cuota, IndexedDB, accesibilidad, modo privado y red bloqueada deben estar especificadas con resultado esperado; y los contratos de error, versionado/migraciones y navegadores mínimos deben figurar en la matriz de pruebas de `docs/03-architecture.md`. No se requieren resultados ejecutados, fechas, entornos reales ni artefactos porque la implementación está prohibida hasta después de GATE 3.

Después de implementar, GATE 4 y la validación independiente convertirán la matriz en evidencia ejecutada: cada fila debe registrar identificador exacto de prueba, versión del documento, resultado y salida observada, fecha, entorno y versión del navegador cuando aplique, y referencia reproducible al reporte, log, fixture o captura. Una fila sin evidencia reproducible impide cerrar GATE 4. Esta separación evita exigir ejecución antes de autorizar implementación y no implica aprobación de ningún gate.
