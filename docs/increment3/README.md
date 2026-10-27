I3 — perfil Frappe y sandbox fail-closed

Estado: gates humanos PASS (BENCH-GPL-GATE=PASS interno; IMAGE-OS-GATE=PASS digest linux/amd64). Inventario PASS. Runtime validado en sandbox aislado. Sin distribucion, produccion ni publicacion.

Evidencia reproducible (fuera del repo, expediente del incremento):

- source-evidence-manifest.json (autoritativo) y source-evidence/: referencias oficiales, tags, commits, tamanos, hashes, licencias, advisories, imagen y SBOM.
- docs/increment3/source-evidence-manifest.json: copia completa del inventario con hashes/tamanos reales (sin null).
- ../bench-gpl-review/candidate-frappe-v16.53.0.json: Bench GPL-3.0-only con decision PASS limitado a sandbox interno, sin distribucion.
- ../image-os-gate/candidate-frappe-v16.53.0.json: imagen/OS PASS con digest exacto sha256:9b629e83... linux/amd64, base debian:trixie-slim.
- kit/frappe/: contrato neutral y adaptador separado; ningun import del core depende de Frappe.
- sandbox/Dockerfile: imagen de app desde la base con digest aceptado; Frappe v16.53.0 (e8d41dd) + Bench v5.31.1, usuario no-root.
- sandbox/compose.yaml: red internal sin egress, DB/cache sin puertos host, HTTP unicamente en 127.0.0.1, imagenes fijadas por digest, cap_drop ALL.
- sandbox/.env.example: solo valores sinteticos/no ejecutables. El `.env` local es modo 600 y no se versiona.

Validacion:

    make i3-validate
    python3 kit/scripts/i3_inventory_validate.py
    NODE_ENV=test python3 -m unittest discover -s kit/tests -v
    docker compose -f sandbox/compose.yaml config

Runtime validado en sandbox aislado (prefijo exclusivo, sin tocar Producto 02 ni /home/dagalindo/frappe): instalacion (bench init), migrate, versiones efectivas (frappe 16.53.0/e8d41dd, bench 5.31.1, python 3.14.8, node 24, yarn 1.22, mariadb 11.8, redis 7.4), backup, restore a sitio nuevo, rollback, uninstall/exit (drop-site), HTTP 200 en 127.0.0.1 (ping), egress deny-by-default, secret scan y restart reproducible. El desk (assets) se omite deliberadamente (--skip-assets): la validacion de runtime no requiere el build del frontend.
