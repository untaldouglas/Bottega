# Modelo de seguridad y privacidad — PRODUCTO-001

- **Versión:** 1.0
- **Estado:** vigente para Hallmark v2; no autoriza release, despliegue ni publicación
- **Ámbito:** aplicación local, una colección por navegador/dispositivo, datos sintéticos, cero servidor y cero red

## 1. Objetivos y límites

El objetivo es preservar integridad de la colección, evitar ejecución de contenido importado, minimizar exposición y hacer explícito que el almacenamiento local no es un respaldo garantizado. No hay autenticación, autorización, multiusuario, secretos ni frontera de confianza remota; cualquier persona con acceso al perfil del navegador puede acceder a los datos.

No se agregan cuentas, cookies de sesión, telemetría, analytics, sincronización, APIs, uploads ni llamadas externas.

## 2. Activos y amenazas

**Activos:** ideas locales, archivo JSON exportado, integridad de prioridad/fechas/IDs, disponibilidad de la última colección confirmada y privacidad del usuario en el dispositivo.

**Amenazas principales:**

- Archivo JSON malicioso o excesivo que consuma CPU/memoria.
- Inyección XSS al renderizar título, descripción, etiquetas o notas.
- Mutación parcial por error de validación, cuota o transacción.
- Corrupción o incompatibilidad de esquema.
- Dependencia o recurso externo que introduzca red/telemetría.
- Acceso local de otra persona o extensión con privilegios.
- Borrado del almacenamiento por navegador, usuario o modo privado.
- Colisión o falsificación de IDs/fechas/prioridad en importación.

## 3. Controles de integridad

1. Medir archivo original en bytes y rechazar >5 MiB antes de parsear.
2. Parsear JSON como datos; exigir objeto raíz, `schemaVersion: "1.0"` e `ideas` array; `exportedAt` es obligatorio al exportar y opcional al importar, pero válido si aparece.
3. Validar todo el documento, incluyendo tipos, campos permitidos, límites de texto, estados, fechas, IDs únicos, etiquetas sin duplicados y prioridad igual a `impacto × confianza × facilidad`.
4. Calcular el resultado completo de Combinar/Reemplazar y validar bytes UTF-8 compactos ≤4 MiB y ≤10.000 ideas antes de confirmar.
5. Confirmación explícita separada de la vista previa; cancelar no muta.
6. Commit completo en una transacción IndexedDB; actualizar UI solo en `complete`.
7. Ante error/abort/cuota, conservar exactamente el snapshot previo y no declarar guardado.
8. Proteger identidad interna con generación automática; no aceptar edición de `id` desde formularios.

La validación se repite en el borde de persistencia como defensa contra errores de orquestación, aunque el dominio sea la fuente normativa.

## 4. Prevención de ejecución y XSS

Los campos del usuario se insertan mediante APIs de texto (`textContent`/equivalente), no HTML interpretado. No se permite HTML, Markdown ejecutable, URLs activas ni plantillas interpoladas sin escape. Importar `<script>`, atributos de evento o payloads similares debe producir texto inocuo. No se usa `eval`, `Function`, HTML dinámico no necesario ni ejecución de contenido del archivo.

Se propone Content Security Policy estricta para una aplicación estática, sin `unsafe-eval` y sin conexiones de red; la configuración concreta se verificará con el servidor local de desarrollo/producción. Descargas usan Blob local y nombre controlado, sin abrir el contenido como página.

## 5. Privacidad y almacenamiento

IndexedDB contiene únicamente las ideas de la colección y metadatos técnicos mínimos. No se guardan credenciales, datos personales, identificadores institucionales, telemetría ni rutas locales. La exportación contiene exactamente `schemaVersion`, `exportedAt` e ideas; no se agregan campos de diagnóstico.

La UI y documentación deben advertir que el almacenamiento puede borrarse y que modo privado puede ser temporal. El respaldo recomendado es exportar JSON y custodiarlo como cualquier archivo local. No se promete cifrado: el producto no administra claves y el perfil del navegador/dispositivo es la frontera de seguridad.

## 6. Errores, disponibilidad y abuso local

Los errores de usuario son agregados, accionables y sin stack traces. Se distinguen límites de entrada, colección, cantidad y cuota. Un JSON inválido no puede dejar cambios parciales. La interfaz debe seguir respondiendo razonablemente ante 5 MiB y 10.000 ideas; si la validación es larga, muestra estado y evita múltiples ejecuciones concurrentes.

La eliminación requiere confirmación y deshacer 10 segundos; al cerrar/suspender no se promete recuperación. El deshacer en memoria no es un registro histórico ni una papelera.

## 7. Dependencias y cadena de suministro

Runtime sin dependencias externas preferidas. Dependencias de desarrollo deben fijarse mediante lockfile, inventariarse con versión y licencia, auditar vulnerabilidades y revisarse para no introducir red, telemetría o código remoto. CI debe bloquear requests de red inesperados y revisar el bundle. La licencia propuesta es MIT, pendiente de aprobación del propietario; las licencias de terceros deben ser compatibles y documentadas.

## 8. Navegadores y modo privado

Se probarán últimas dos versiones estables de Chromium, Firefox y Safari de escritorio. Se requiere detectar ausencia/fallo de IndexedDB y comunicar “persistencia no disponible o temporal”. En modo privado, se informa que el cierre puede borrar datos; no se degrada silenciosamente a `localStorage` ni se declara éxito falso.

## 9. Accesibilidad como control de seguridad de uso

Etiquetas, foco, mensajes de error y confirmaciones reducen acciones destructivas accidentales. Combinar/Reemplazar y cancelar/confirmar deben distinguirse por texto y estructura, no solo color. Los límites y conflictos de importación se anuncian también a tecnologías de asistencia.

## 10. Pruebas de seguridad

- Fuzz/corpus de JSON inválido, campos extra, duplicados, Unicode y estructuras profundas dentro del límite.
- Payloads HTML/JS en todos los campos y verificación de no ejecución.
- Archivo >5 MiB rechazado antes de parsear.
- Colección >4 MiB o >10.000 rechazada antes de commit.
- Combinar que cruza capacidad conserva byte por byte la forma canónica del estado previo.
- Abort y cuota no muestran guardado ni subconjunto.
- Round-trip no agrega campos ni cambia identidad.
- Red bloqueada; auditoría de dependencias/licencias.
- Revisión manual de CSP, foco, errores y superficie de APIs.

## 11. Riesgos residuales y aceptación

El acceso al perfil del navegador, extensiones maliciosas y malware local quedan fuera del control de una aplicación sin autenticación. El reloj del dispositivo no es confiable para seguridad, solo para orden. IndexedDB no garantiza retención permanente. Estos riesgos deben aparecer en la documentación de usuario y ser aceptados explícitamente en GATE 3; este ADR no declara la aprobación.
