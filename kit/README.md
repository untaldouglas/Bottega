# Bottega project kit

Kit operativo reutilizable para iniciar ejercicios con trazabilidad, gates y evidencia sintética.

## Quick start

```bash
python3 scripts/init_bottega_project.py \
  --target ../mi-ejercicio --product-name "Producto sintético" \
  --slug mi-ejercicio --owner "Usuario Ejemplo" --org organizacion-ejemplo \
  --init-git
python3 scripts/bottega_preflight.py --project ../mi-ejercicio --format markdown
python3 scripts/gate_check.py --project ../mi-ejercicio --format markdown
```

El scaffold crea los briefs, manifiestos, `REVIEW-PACKET.md`, `TEST-SEAMS.yaml` y `runs/`. GitHub no se toca salvo que se proporcionen `--create-private-repo`, `--repo-name` y `--confirm-private-repo`. Nunca se crea un repositorio público.

## Smokes read-only

El adaptador es declarativo (`adapters/example.json`); no acepta comandos, shell, heredocs ni credenciales en JSON. Las credenciales, si el producto las necesita, se enlazan únicamente desde variables de entorno declaradas y se mantienen en memoria. El kit sólo ejecuta operaciones allowlistadas y sanea payloads antes de emitir evidencia.

```bash
python3 scripts/smoke_authenticated.py --adapter adapters/example.json \
  --scenario authenticated-smoke.json --read-only --format json
python3 scripts/smoke_navigation.py --adapter adapters/example.json \
  --scenario navigation-smoke.json --read-only --format json
```

El smoke autenticado verifica identidad server-side, acceso propio, rechazo de acceso cruzado y una sonda de mutación prohibida con `before == after`. El smoke de navegación inicia en `/login`, registra requests/redirects saneados y sólo permite hosts/statuses declarados. Si no existe el runtime Playwright/Chromium, el resultado correcto es `BLOCKED` (código 3), nunca `PASS`. Los resultados ejecutados viven en `evidence/<run-id>/`; los criterios no ejecutados permanecen planificados en `TEST-SEAMS.yaml`.

## Flujo

1. Completar `PROJECT-BRIEF.yaml` (alcance, datos sintéticos/permitidos, riesgos, gates y autorización).
2. Ejecutar preflight y conservar su salida como evidencia del run.
3. Registrar cada intento en `runs/<run-id>/attempts/<n>/manifest.json`; los manifiestos son inmutables después de creados.
4. Ejecutar `gate_check.py` para validar coherencia del estado, aceptación, hashes y evidencia.
5. Marcar gates únicamente con evidencia ejecutada. Separar contadores `delivery_attempt`, `provider_retry`, `validation_attempt` y `operational_cleanup`.

Al cerrar la implementación, se completa `REVIEW-PACKET.md` (Summary → Evidence → Merge Danger) y se entrega junto con el manifiesto de evidencia; sin él no se promueve a revisión independiente. La retrospectiva se ejecuta después del cierre humano, fuera del gate, y produce mejoras del método que una persona acepta, pospone o rechaza.

El Kanban debe modelar dependencias Andrea → Leonardo → Filippo → Michelangelo
→ Raffaello y conservar un Bot por etapa. Raffaello no se habilita hasta
`READY_FOR_VALIDATION`. Los estados de decisión son independientes:
`PRODUCT_PASS`, `RELEASE_READY_CONDITIONAL` y `PUBLICATION_AUTHORIZED`; el
último requiere autorización institucional explícita.

El primer HTTP 429 abre el circuit breaker. El fallback se detiene y escala
salvo que `authorization.fallback_allowed: true` esté declarado en
`PROJECT-BRIEF.yaml`. El repositorio privado es opcional y solo se crea con
autorización explícita y los tres flags documentados; nunca se crea un remoto
público ni uno por defecto.

## Circuit breaker

El primer HTTP 429 abre el circuito. El fallback solo puede aplicarse si `authorization.fallback_allowed: true` en el brief; de lo contrario el intento debe detenerse y escalarse. Esta política es declarativa: el kit no activa proveedores ni modifica producción.

## Seguridad

Los datos de ejemplo son sintéticos. La evidencia operativa (`runs/`, reportes locales, secretos, `.env`) queda excluida de los contextos de build mediante las tres plantillas de ignore. No se imprimen tokens ni variables secretas. El gate checker es de solo lectura y no ejecuta comandos destructivos.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
python3 scripts/init_bottega_project.py --help
python3 scripts/bottega_preflight.py --help
python3 scripts/gate_check.py --help
```

La evidencia se define en el [glosario](../docs/glossary/entries/evidence.md#glossary-evidence).
