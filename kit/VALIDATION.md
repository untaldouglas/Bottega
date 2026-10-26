# VALIDATION

Fecha de validación: 2026-10-26 (entorno de ejecución de la tarea).

## Suite completa

Comando:

    python3 -m unittest discover -s tests -v

Salida real:

    test_help_and_preflight (test_kit.KitTests.test_help_and_preflight) ... ok
    test_init_dry_run_does_not_write (test_kit.KitTests.test_init_dry_run_does_not_write) ... ok
    test_invalid_slug_and_unconfirmed_remote (test_kit.KitTests.test_invalid_slug_and_unconfirmed_remote) ... ok
    test_scaffold_and_gate (test_kit.KitTests.test_scaffold_and_gate) ... ok

    Ran 11 tests in 2.255s

    OK

La ejecución anterior es evidencia ejecutada de esta revisión. Los casos T01–T37 que aún no tienen un test materializado permanecen planificados en `TEST-SEAMS.yaml`; no se cuentan como PASS.

## Checks ejecutados en esta revisión

| Comando | Resultado |
|---|---|
| `python3 -m unittest discover -s kit/tests -v` | exit 0, 11 tests PASS |
| `make kit-test` | exit 0, 11 tests PASS |
| `make guardrails-check` | exit 0, SKIPPED explícito por ausencia de gate-record del repo |
| `make guardrails-preflight` | exit 0, dry-run; browser/Chromium no disponible |
| `make lint` | exit 0 |
| `make typecheck` | exit 0 |
| `make test` | exit 0, unit 22 PASS; E2E 47 PASS, 1 skipped |
| `make docs-check` | exit 0 |
| `make security` | exit 0, 0 hallazgos |
| `make licenses` | exit 0, 0 licencias desconocidas |
| `npm run build --prefix app01` + `hallmark:check` | exit 0 |

El init en scratch creó `adapters/example.json`, los contratos y `runs/` sin tocar Producto 02. Los smokes rechazaron comandos libres y el smoke de navegación devuelve BLOCKED cuando falta Playwright/Chromium; ningún runtime externo se instaló.

## Interfaces CLI

Se ejecutaron los tres comandos con `--help` y terminaron con código 0:

    python3 scripts/init_bottega_project.py --help
    python3 scripts/bottega_preflight.py --help
    python3 scripts/gate_check.py --help

## Preflight dry-run

Comando: `python3 scripts/bottega_preflight.py --dry-run --format json`

Resultado observado: código 0 y `ok: true`; Python 3.14.7, Git 2.43.0, gh 2.45.0, Docker 29.9.0, Node v26.7.0, npm 11.19.0 y Hermes Agent v0.21.5+5782.ga1398e9.dirty. GitHub auth fue detectada sin revelar secretos (`secret_exposed: false`). No se creó ningún repositorio remoto.

El reporte indicó navegador no disponible en este entorno (`browser_available: false`), sin bloquear los checks mínimos de Python/Git.

## Alcance y seguridad

Las pruebas usan directorios temporales y datos sintéticos. La prueba de dry-run verificó que no se escribe el target. La prueba inválida verificó slug rechazado y que un repositorio privado no se crea sin confirmación explícita. No se modificó `app01`.
