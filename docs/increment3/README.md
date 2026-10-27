I3 — perfil Frappe y sandbox fail-closed

Estado: gates humanos PASS (BENCH-GPL-GATE=PASS interno; IMAGE-OS-GATE=PASS digest linux/amd64). Inventario PASS. Sandbox listo para validacion de runtime aislado. No distribucion, produccion ni publicacion.

Evidencia reproducible (fuera del repo, expediente del incremento):

- source-evidence-manifest.json (autoritativo) y source-evidence/: referencias oficiales, tags, commits, tamanos, hashes, licencias, advisories, imagen y SBOM.
- docs/increment3/source-evidence-manifest.json: copia completa del inventario con hashes/tamanos reales (sin null).
- ../bench-gpl-review/candidate-frappe-v16.53.0.json: Bench GPL-3.0-only con decision PASS limitado a sandbox interno, sin distribucion.
- ../image-os-gate/candidate-frappe-v16.53.0.json: imagen/OS PASS con digest exacto sha256:9b629e83... linux/amd64, base debian:trixie-slim.
- kit/frappe/: contrato neutral y adaptador separado; ningun import del core depende de Frappe.
- sandbox/compose.yaml: usuario no-root, red internal sin egress, DB/cache sin puertos host, HTTP unicamente en 127.0.0.1 y variables de imagen obligatorias por digest.
- sandbox/.env.example: solo valores sinteticos/no ejecutables. El `.env` local debe ser modo 600 y no se versiona.

Validacion:

    make i3-validate
    python3 kit/scripts/i3_inventory_validate.py
    NODE_ENV=test python3 -m unittest discover -s kit/tests -v
    docker compose --env-file sandbox/.env.example -f sandbox/compose.yaml config

El runtime (instalacion, migrate, backup/restore, rollback, uninstall y exit test) se valida en el sandbox aislado con prefijo exclusivo, sin tocar Producto 02 ni /home/dagalindo/frappe.
