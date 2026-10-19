# ADR-0002: Persistencia local con IndexedDB

- **Estado:** Propuesto; requiere decisión de GATE 3
- **Fecha:** 2026-10-13
- **Contexto:** La colección debe sobrevivir al cierre/reapertura en el mismo navegador/dispositivo, admitir hasta 10.000 ideas sujeto a 4 MiB compactos, y aplicar importaciones completas o ninguna. No existe servidor ni sincronización.

## Decisión

Usar IndexedDB como adaptador real detrás de `CollectionRepository`.

- Base: `idea-prioritizer`, versión IndexedDB `1`.
- Store `ideas`: keyPath `id`; índices no únicos `prioridad`, `modificadaEn`, `estado`.
- Store `meta`: keyPath `key`; registro `collection` con versión interna, fecha, cantidad y bytes normalizados.
- `load`: transacción readonly, materialización completa y validación.
- `commit`: una transacción readwrite sobre ambos stores; `clear + put` de la colección completa y actualización de metadatos; solo `complete` confirma éxito.
- Upgrade inicial crea stores/índices; migraciones futuras son explícitas, versionadas, abortables y probadas.

El formato JSON externo es independiente: `schemaVersion: "1.0"`, `exportedAt`, `ideas`. Versiones desconocidas se rechazan; no hay conversión silenciosa.

## Atomicidad y capacidad

Antes de commit se valida la colección resultante completa para crear, editar, deshacer, Combinar y Reemplazar. Se mide JSON compacto UTF-8 con `TextEncoder`, máximo 4 MiB, y se cuentan máximo 10.000 ideas. El archivo de entrada se limita a 5 MiB antes de parsearlo. El primer límite excedido rechaza sin mutación.

Una transacción abortada, `QuotaExceededError`, error de cuota o almacenamiento no disponible conserva el último estado confirmado; la UI no declara guardado. La sustitución completa simplifica la demostración de atomicidad para el volumen aprobado y evita que otros módulos conozcan object stores.

## Alternativas

- **localStorage:** síncrono, menos apropiado para crecimiento y errores de cuota; se reserva para prototipo, no para entrega ni fake transaccional.
- **Un único documento en IndexedDB:** sería más simple, pero reduce consultas/indexación y no deja un modelo físico claro para evolución.
- **Servidor/SQLite remoto:** contradice cero servidor y privacidad local.
- **Fake en memoria:** se conserva solo para pruebas de contrato; no demuestra persistencia ni transacciones del navegador.

## Consecuencias

**Positivas:** API asíncrona, transacciones nativas, stores estructurados, índices, evolución de versión y mejor margen que Web Storage.

**Negativas:** API compleja, comportamiento variable en modo privado/cuotas, necesidad de pruebas en navegadores y cuidado con transacciones activas. La transacción no reemplaza la validación previa ni la confirmación explícita.

## Recuperación y privacidad

Exportar JSON es el respaldo explícito; IndexedDB puede ser borrada por usuario, navegador o política del dispositivo. No se guardan credenciales, datos personales ni telemetría. Modo privado puede ser temporal: se informa sin prometer persistencia.

## Verificación requerida por GATE 3

Pruebas de reapertura, commit completo, abort, cuota, stores/índices, upgrade, fixture de migración, datos sintéticos en 0/1/10.000 ideas, límites exactos 4 MiB/5 MiB, Combinar/Reemplazar, round-trip de exportación/importación y ejecución sin red.
