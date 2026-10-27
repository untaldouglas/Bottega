I3 — perfil Frappe y sandbox fail-closed

Estado: BLOCKED operativo; PASS sólo para inventario y contrato. No se instaló Frappe/Bench ni se arrancó una imagen, porque faltan IMAGE-OS-GATE aceptado y bench-gpl-review con decisión PASS de Douglas.

Evidencia reproducible:

- source-evidence-manifest.json: referencias oficiales, tags, commits, tamaños, hashes, licencia y snapshot de advisories.
- ../bench-gpl-review/candidate-frappe-v16.53.0.json: Bench GPL-3.0-only bloqueado hasta revisión competente.
- ../image-os-gate/candidate-frappe-v16.53.0.json: imagen/OS bloqueada hasta digest y aceptación del Director.
- kit/frappe/: contrato neutral y adaptador separado; ningún import del core depende de Frappe.
- sandbox/compose.yaml: usuario no-root, red internal sin egress, DB/cache sin puertos host, HTTP únicamente en 127.0.0.1 y variables de imagen obligatorias por digest.
- sandbox/.env.example: sólo valores sintéticos/no ejecutables. El `.env` local debe ser modo 600 y no se versiona.

Validación:

    make i3-validate
    NODE_ENV=test python3 -m unittest discover -s kit/tests -v
    docker compose --env-file sandbox/.env.example -f sandbox/compose.yaml config

La instalación, migrate, backup/restore, rollback, uninstall, restart y exit-test quedan deliberadamente pendientes de los gates independientes; no se afirma compatibilidad runtime.
