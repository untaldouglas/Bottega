.PHONY: help setup lint typecheck unit e2e test security licenses audit hallmark-check preflight validate smoke container-build ci clean glossary-add glossary-check docs-check docs doctor bootstrap kit-test guardrails-check guardrails-preflight advisor-test advisor-smoke advisor-negative advisor-validate taller-test taller-validate auditor-test i2-validate i3-test i3-validate i3-inventory-validate

APP_DIR := app01
NPM := npm --prefix $(APP_DIR)
ADVISOR := python3 kit/scripts/bottega_advisor.py
FIXTURES := kit/tests/fixtures/advisor

help:
	@printf '%s\n' 'Targets: setup lint typecheck unit e2e test security licenses audit hallmark-check preflight validate smoke container-build ci clean glossary-add glossary-check docs-check docs kit-test guardrails-check guardrails-preflight'

kit-test:
	NODE_ENV=test python3 -m unittest discover -s kit/tests -v

guardrails-check:
	@if test -f gate-record.json; then python3 kit/scripts/gate_check.py --project . --manifest gate-record.json --evidence-root . --format json --read-only; else echo '{"status":"SKIPPED","reason":"no gate-record.json"}'; fi

guardrails-preflight:
	python3 kit/scripts/bottega_preflight.py --project . --format json --dry-run --config kit/templates/PREFLIGHT-CONFIG.json

# Advisor del Incremento 1 — determinista, sin LLM, sólo lectura.
advisor-test:
	python3 -m unittest discover -s kit/tests -p 'test_advisor*.py' -v

advisor-smoke:
	$(ADVISOR) validate-intake --input $(FIXTURES)/intake-valid.yaml
	$(ADVISOR) prepare-report --intake $(FIXTURES)/intake-valid.yaml \
	  --out $(FIXTURES)/.smoke-report.json --now 2026-10-26T00:00:00Z
	$(ADVISOR) validate-report --input $(FIXTURES)/.smoke-report.json
	$(ADVISOR) export-casefile --intake $(FIXTURES)/intake-valid.yaml \
	  --report $(FIXTURES)/.smoke-report.json --out $(FIXTURES)/.smoke-casefile

advisor-negative:
	@$(ADVISOR) validate-intake --input $(FIXTURES)/intake-secret.yaml >/dev/null 2>&1; test $$? -eq 3
	@$(ADVISOR) validate-intake --input $(FIXTURES)/intake-out-of-scope.yaml >/dev/null 2>&1; test $$? -eq 3
	@$(ADVISOR) validate-intake --input $(FIXTURES)/intake-missing-owner.yaml >/dev/null 2>&1; test $$? -eq 1
	@echo 'advisor-negative: 3/3 casos negativos con exit code esperado'

advisor-validate: advisor-test advisor-smoke advisor-negative

taller-test:
	NODE_ENV=test python3 -m unittest discover -s kit/tests -p 'test_taller*.py' -v

taller-validate: advisor-validate taller-test

auditor-test:
	NODE_ENV=test python3 -m unittest discover -s kit/tests -p 'test_auditor*.py' -v

i2-validate: taller-validate auditor-test

i3-test:
	NODE_ENV=test python3 -m unittest discover -s kit/tests -p 'test_i3.py' -v

i3-validate: i3-test
	python3 kit/scripts/i3_validate.py
	@echo 'I3 inventory and gates PASS; sandbox validated for isolated runtime.'

i3-inventory-validate:
	python3 kit/scripts/i3_inventory_validate.py


glossary-add:
	@test -n "$(TERM)" || (echo 'Uso: make glossary-add TERM="Concepto" CATEGORY=proceso OWNER=equipo DEFINITION="..." CONTEXT="..." SOURCE=GUIA-DE-USO.md REVIEW_DUE=YYYY-MM-DD' >&2; exit 2)
	python3 scripts/glossary.py add --label "$(TERM)" --alias "$(ALIAS)" --category "$(CATEGORY)" --owner "$(OWNER)" --definition "$(DEFINITION)" --context "$(CONTEXT)" --source "$(SOURCE)" --review-due "$(REVIEW_DUE)" --non-interactive

glossary-check:
	python3 scripts/glossary.py check

# Documentación no instala dependencias ni ejecuta pruebas de aplicación.
docs-check: glossary-check
	python3 scripts/glossary.py render --check
	python3 scripts/docs_check.py
	python3 scripts/check_protected_decisions.py

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
	@set -eu; trap 'docker compose -f $(APP_DIR)/compose.yaml down --remove-orphans' EXIT; docker compose -f $(APP_DIR)/compose.yaml up -d; python3 scripts/smoke_http.py --url http://127.0.0.1:4173/ --attempts 30 --interval 1

container-build:
	docker compose -f $(APP_DIR)/compose.yaml build

ci: validate smoke advisor-validate

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
