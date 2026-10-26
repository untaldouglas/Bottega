# Política de patch calificado para Frappe v16

Estado: PROPUESTA PARA REVISIÓN; no autoriza instalación, PoC, release ni producción.
Fecha: 2026-10-26 (CST, UTC-06:00).
Propietario de decisión: Douglas.
Alcance: perfil Golden Path de Frappe para productos nuevos; no aplica a Producto 02.

## 1. Regla de calificación

`v16.53.0` permanece como baseline candidato hasta completar esta política. `latest`, una etiqueta mutable, una imagen sin digest o un número de patch sin tag y commit no son un pin reproducible ni pueden pasar el gate.

Un patch calificado es una tupla completa e inmutable:

`(framework_major, framework_patch, frappe_tag, frappe_commit, bench_version, python_version, node_version, mariadb_version, redis_or_valkey_version, yarn_version, os_image_digest)`

La tupla debe registrarse junto con `candidate_id`, fecha UTC, fuentes consultadas, entorno, responsable y revisor. Cambiar cualquier elemento crea un candidato nuevo; no se edita el registro anterior.

## 2. Fuentes oficiales y selección

El responsable consulta, fecha y conserva referencias a estas fuentes oficiales antes de seleccionar un candidato:

1. Frappe Framework y ERPNext: repositorios oficiales y releases/tag firmado o verificable.
2. Frappe Bench: repositorio oficial, documentación de instalación y versión compatible.
3. Documentación oficial de Frappe v16: matriz de dependencias y requisitos de instalación.
4. Fuentes oficiales de Python, Node.js, MariaDB, Redis/Valkey, Yarn y la distribución base del sistema operativo.
5. Advisories de seguridad de los proyectos y avisos de la distribución/registries usados.

La fuente debe incluir URL, título o endpoint, fecha de consulta, versión observada, hash descargado cuando exista y evidencia archivada. Una entrada de blog, mirror o comentario puede orientar la búsqueda, pero no sustituye la fuente oficial.

El selector primero fija la línea mayor `v16`, después el patch candidato (`v16.53.0` en I0), y finalmente resuelve la tupla completa. Si las fuentes discrepan, falta una dependencia o no se puede probar el commit, el estado es `BLOCKED`, no se elige por conveniencia.

## 3. Licencias, advisories, SBOM y procedencia

Antes de aceptación se exige:

- inventario de licencias de framework, Bench, dependencias directas y artefactos de imagen;
- revisión de advisories por componente y severidad, con decisión documentada para cada hallazgo;
- SBOM generado en un formato intercambiable (CycloneDX o SPDX), con herramienta y versión;
- procedencia de cada artefacto: URL oficial, tag, commit, digest, método de descarga y hash SHA-256;
- registro de quién ejecutó el análisis, cuándo, en qué entorno y con qué política.

Un SBOM incompleto, una licencia no evaluada, un advisory sin decisión o una procedencia que no llega a tag+commit+hash bloquea la aceptación. No se copian tokens ni datos institucionales al expediente.

## 4. Validación de compatibilidad y pruebas de aceptación

El candidato se prueba en un sandbox reproducible y no destructivo. El expediente debe demostrar la misma tupla de la sección 1 y conservar comandos, versiones efectivas y hashes.

Las pruebas mínimas son:

- instalación limpia y verificación de `framework_major`/patch, Frappe tag y commit;
- compatibilidad declarada y observada de Python, Node.js, MariaDB, Redis/Valkey, Yarn, Bench y OS;
- arranque y health check del sandbox;
- migración o actualización en fixture sintética, con logs redacted;
- pruebas funcionales del alcance del producto y pruebas negativas de autorización;
- ejecución de backup, restore y verificación posterior;
- rollback a la versión anterior en sandbox, comprobando integridad y servicio;
- repetición por una identidad de validación distinta de quien implementó el candidato.

El resultado es `PASS`, `NEEDS_WORK` o `BLOCKED`, con criterio, evidencia hashada y razón. Ninguna prueba local afirma compatibilidad de producción.

## 5. Backup, restore y rollback

Antes de cualquier operación de actualización se crea un backup verificable de base de datos, archivos y configuración permitida, con `backup_id`, timestamp UTC, tamaño, hashes, ubicación controlada, retención definida por la política y prueba de lectura.

La aceptación requiere un restore exitoso en sandbox aislado: el hash restaurado coincide, los datos sintéticos son legibles y el health check pasa. Un backup creado pero no restaurado no es evidencia suficiente.

El rollback debe identificar `from_candidate_id` y `to_candidate_id`, ejecutar un procedimiento versionado y demostrar que el servicio vuelve a operar. Si falla backup, restore, hash, migración o rollback, el candidato queda `BLOCKED` y no se autoriza promoción.

## 6. Aceptación y registro

Sólo el Director puede aceptar el candidato después de revisión independiente. El registro de aceptación contiene:

- `candidate_id`, tupla completa, `status: candidate|validated|rejected`;
- tag, commit y digest aprobados, con SHA-256 y fuentes;
- licencias, advisories, SBOM y procedencia vinculados por hash;
- resultados de compatibilidad, aceptación, backup, restore y rollback;
- backup/restore/rollback IDs, fecha UTC y entorno;
- implementador, validador, revisor y decisor, sin auto-revisión;
- decisión, razón, alcance, expiración y referencia al gate.

En I0 el único resultado permitido para el baseline es `candidate`. `validated` requiere todas las pruebas y la decisión humana; `rejected` conserva la razón y no se reutiliza silenciosamente.

## 7. Comparación con patches posteriores

Un patch posterior se evalúa como candidato nuevo contra el registro validado anterior. La comparación debe publicar una tabla con cambios de la tupla, changelog oficial, advisories nuevos/resueltos, diferencias de SBOM/licencias/procedencia, resultados de compatibilidad, backup/restore/rollback, regresiones y costo/tiempo de validación.

No se promociona el patch posterior por ser más reciente. Se conserva el anterior como rollback target hasta que el nuevo tenga PASS completo y aceptación humana. Si cambia la línea mayor, se abre una decisión de arquitectura y no se trata como patch compatible.

## 8. Gate determinista y límites

El check documental `python3 scripts/docs_check.py` verifica que esta política conserve las secciones obligatorias, la tupla completa, `v16.53.0`, la prohibición de `latest`, los estados `candidate|validated|rejected`, y los controles de backup, restore, rollback, SBOM, advisories, licencias, procedencia y comparación posterior. No instala Frappe ni valida compatibilidad técnica.

Este artefacto no afirma que Frappe esté instalado, que `v16.53.0` sea compatible ni que exista una aceptación. La validación pertenece a I3 y requiere sandbox, evidencia reproducible y decisión humana.
