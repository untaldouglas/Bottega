.PHONY: help setup lint typecheck unit e2e test security licenses audit hallmark-check preflight validate smoke container-build ci clean glossary-add glossary-check docs-check docs doctor bootstrap kit-test guardrails-check guardrails-preflight

APP_DIR := app01
NPM := npm --prefix $(APP_DIR)

help:
	@printf '%s\n' 'Targets: setup lint typecheck unit e2e test security licenses audit hallmark-check preflight validate smoke container-build ci clean glossary-add glossary-check docs-check docs kit-test guardrails-check guardrails-preflight'

kit-test:
	NODE_ENV=test python3 -m unittest discover -s kit/tests -v

guardrails-check:
	@if test -f gate-record.json; then python3 kit/scripts/gate_check.py --project . --manifest gate-record.json --evidence-root . --format json --read-only; else echo '{"status":"SKIPPED","reason":"no gate-record.json"}'; fi

guardrails-preflight:
	python3 kit/scripts/bottega_preflight.py --project . --format json --dry-run --config kit/templates/PREFLIGHT-CONFIG.json

glossary-add:
	@test -n "$(TERM)" || (echo 'Uso: make glossary-add TERM="Concepto" CATEGORY=proceso OWNER=equipo DEFINITION="..." CONTEXT="..." SOURCE=GUIA-DE-USO.md REVIEW_DUE=YYYY-MM-DD' >&2; exit 2)
	python3 scripts/glossary.py add --label "$(TERM)" --alias "$(ALIAS)" --category "$(CATEGORY)" --owner "$(OWNER)" --definition "$(DEFINITION)" --context "$(CONTEXT)" --source "$(SOURCE)" --review-due "$(REVIEW_DUE)" --non-interactive

glossary-check:
	python3 scripts/glossary.py check

# Documentación no instala dependencias ni ejecuta pruebas de aplicación.
docs-check: glossary-check
	python3 scripts/glossary.py render --check
	python3 scripts/docs_check.py

docs:
	python3 scripts/glossary.py render

setup:
	$(NPM) ci --ignore-scripts --no-audit --no-fund

lint:
	$(NPM) run lint

typecheck:
	$(NPM) run typecheck

unit:
	NODE_ENV=test $(NPM) test

e2e:
	$(NPM) run test:e2e

test: lint typecheck unit e2e

security:
	$(NPM) run security:scan

licenses:
	$(NPM) run licenses

audit:
	$(NPM) audit --audit-level=high

hallmark-check:
	$(NPM) run build
	$(NPM) run hallmark:check

preflight:
	@command -v node >/dev/null || (echo 'node is required' >&2; exit 1)
	@command -v npm >/dev/null || (echo 'npm is required' >&2; exit 1)
	@test -f $(APP_DIR)/package-lock.json
	@node -e "const p=require('./$(APP_DIR)/package.json'); for (const s of ['lint','typecheck','test','test:e2e','build']) if (!p.scripts[s]) process.exit(1)"

validate: preflight
	$(NPM) run format
	$(MAKE) test security licenses audit
	$(NPM) run build
	$(NPM) run hallmark:check
	docker compose -f $(APP_DIR)/compose.yaml config >/dev/null

smoke: container-build
	@set -eu; trap 'docker compose -f $(APP_DIR)/compose.yaml down --remove-orphans' EXIT; docker compose -f $(APP_DIR)/compose.yaml up -d; for attempt in $$(seq 1 30); do if curl --fail --silent --show-error http://127.0.0.1:4173/ >/dev/null; then exit 0; fi; sleep 1; done; echo 'container did not become ready' >&2; exit 1

container-build:
	docker compose -f $(APP_DIR)/compose.yaml build

ci: validate smoke

# Validación de prerrequisitos del método (solo lectura, idempotente).
doctor:
	python3 scripts/bottega_doctor.py

# Doctor + checklist ordenado de instalación (cero a listo).
bootstrap:
	python3 scripts/bottega_doctor.py --bootstrap

clean:
	@for path in $(APP_DIR)/dist $(APP_DIR)/playwright-report $(APP_DIR)/test-results; do \
		rm -rf -- "$$path"; \
	done
	@echo 'Removed allowlisted build and test artifacts only.'
