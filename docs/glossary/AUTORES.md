# Guía breve para autores

1. Busca el concepto y sus aliases en `docs/glossary/terms.yaml` antes de crear uno.
2. Reutiliza el ID existente si el concepto ya está registrado; no cambies anclas estables.
3. Para un término nuevo usa `make glossary-add` con definición, contexto, fuente, propietario y fechas completas.
4. Enlaza solo la primera aparición significativa por documento o sección autónoma. No enlaces cada coincidencia, encabezados, tablas ni código.
5. Ejecuta `make glossary-check`, `make docs-check` y `python scripts/glossary.py render --check`.
6. Revisa manualmente los enlaces relativos desde el directorio del documento que editaste.
7. No edites `GLOSSARY.md` a mano: se genera desde `terms.yaml` con `make docs` y es el glosario que leen las skills de agentes (`pr`, `domain-modeling`, `grill-with-docs`, `wait-what`).

Las entradas `deprecated` se conservan para enlaces históricos y no reciben enlaces nuevos. No agregues PII, credenciales ni fuentes externas que requieran red en CI.
