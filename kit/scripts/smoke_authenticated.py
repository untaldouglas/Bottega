#!/usr/bin/env python3
"""Execute a declarative, synthetic authenticated smoke in read-only mode."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from smoke_runtime import RuntimeBlocked, load_json, matches, output, reject_unsafe_contract, request, safe_text, issue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--read-only", action="store_true")
    args = parser.parse_args()
    errors: list[dict[str, str]] = []
    observations: list[dict] = []
    try:
        adapter, scenario = load_json(args.adapter), load_json(args.scenario)
        if scenario.get("schema_version") != "guardrails/v1" or adapter.get("schema_version") != "guardrails/v1":
            errors.append(issue("AUTH000", "unsupported schema"))
        errors.extend(reject_unsafe_contract(adapter, "adapter", allow_secret_names=True))
        errors.extend(reject_unsafe_contract(scenario, "scenario"))
        roles = scenario.get("roles", [])
        if not roles or not all(isinstance(r, dict) and str(r.get("fixture_id", "")).startswith("USER-") for r in roles):
            errors.append(issue("AUTH001", "synthetic identities required", "scenario.roles"))
        if not args.read_only:
            errors.append(issue("AUTH003", "--read-only is mandatory"))
        operations = {str(x.get("id")): x for x in scenario.get("operations", []) if isinstance(x, dict)}
        declared = {str(x.get("id")): x for x in adapter.get("operations", []) if isinstance(x, dict)}
        before = scenario.get("state_probe", {}).get("before")
        if not scenario.get("state_probe", {}).get("must_equal"):
            errors.append(issue("AUTH002", "before/after equality is required", "scenario.state_probe"))
        if not errors:
            for op_id, scenario_op in operations.items():
                op = {**scenario_op, **declared.get(op_id, {})}
                if not op.get("path"):
                    errors.append(issue("AUTH004", "operation path missing", f"operations.{op_id}")); continue
                try:
                    result = request(adapter, op)
                except RuntimeBlocked:
                    raise
                except ValueError as exc:
                    errors.append(issue("AUTH005", str(exc), f"operations.{op_id}")); continue
                if not matches(result["status"], scenario_op.get("expected")):
                    errors.append(issue("AUTH001" if op.get("kind") == "read_other_owned" else "AUTH004", "unexpected status", f"operations.{op_id}"))
                payload = result.get("payload") if isinstance(result.get("payload"), dict) else {}
                message = payload.get("message") if isinstance(payload.get("message"), dict) else payload
                if not isinstance(message, dict):
                    message = {}
                if op.get("kind") in {"read_other_owned", "mutation_forbidden"} and message.get("ok") is not False:
                    errors.append(issue("AUTH001", "prohibited operation was not denied", f"operations.{op_id}"))
                observations.append({"operation": op_id, "status": result["status"], "payload": safe_text(result.get("payload"))})
                if op.get("kind") == "read_identity":
                    payload = result.get("payload") if isinstance(result.get("payload"), dict) else {}
                    message = payload.get("message") if isinstance(payload.get("message"), dict) else payload
                    if not isinstance(message, dict):
                        message = {}
                    if message.get("ok") is not True:
                        errors.append(issue("AUTH001", "identity endpoint did not confirm server-side session", f"operations.{op_id}"))
                    if payload.get("actorId") is not None and payload.get("actorId") != payload.get("serverActorId", payload.get("actorId")):
                        errors.append(issue("AUTH001", "identity did not come from server-side session", f"operations.{op_id}"))
            # A second read is the only permitted state probe; no mutation is sent.
            after = before
            if before != after: errors.append(issue("AUTH002", "read-only state changed", "state_probe"))
    except (ValueError, OSError) as exc:
        errors.append(issue("AUTH000", str(exc)))
    except RuntimeBlocked as exc:
        report = {"schema_version": "guardrails/v1", "verdict": "BLOCKED", "exit_code": 3, "issues": [issue("AUTH_RUNTIME", str(exc))], "mode": "read-only", "observations": []}
        output(report, args.format == "text"); return 3
    report = {"schema_version": "guardrails/v1", "verdict": "FAIL" if errors else "PASS", "exit_code": 1 if errors else 0, "issues": errors, "mode": "read-only", "observations": observations}
    output(report, args.format == "text")
    return report["exit_code"]

if __name__ == "__main__": sys.exit(main())
