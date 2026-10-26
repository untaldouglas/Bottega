#!/usr/bin/env python3
"""Execute a declarative, synthetic authenticated smoke in read-only mode."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from smoke_runtime import RuntimeBlocked, load_json, matches, output, reject_unsafe_contract, request, safe_text, issue


def _message(payload):
    if not isinstance(payload, dict): return {}
    value = payload.get("message", payload)
    return value if isinstance(value, dict) else {}


def _server_actor(payload):
    message = _message(payload)
    value = message.get("value") if isinstance(message.get("value"), dict) else message
    return value.get("serverActorId") if isinstance(value, dict) else None


def _identities(scenario, adapter):
    declared = scenario.get("identities")
    if not isinstance(declared, list):
        # v1 compatibility is deliberately explicit: roles are accepted only
        # when they already describe two independent fixture identities.
        declared = scenario.get("roles")
    if not isinstance(declared, list) or len(declared) < 2:
        raise ValueError("AUTH001: at least two identities are required")
    result = []
    seen = set(); bindings_seen = set()
    configured = adapter.get("identity_bindings", {})
    for item in declared:
        if not isinstance(item, dict): raise ValueError("AUTH001: invalid identity")
        identity_id = str(item.get("id", "")); fixture = str(item.get("fixture_id", ""))
        binding = item.get("binding") or item.get("binding_ref") or identity_id
        if not identity_id or not fixture.startswith("USER-") or identity_id in seen or binding in bindings_seen:
            raise ValueError("AUTH001: duplicate or invalid synthetic identity")
        if binding not in configured or not isinstance(configured[binding], dict):
            raise RuntimeBlocked(f"missing identity binding: {binding}")
        seen.add(identity_id); bindings_seen.add(binding); result.append((identity_id, fixture, configured[binding]))
    return result


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
        identities = []
        try: identities = _identities(scenario, adapter)
        except (ValueError, RuntimeBlocked) as exc: errors.append(issue("AUTH001", str(exc)))
        if not args.read_only:
            errors.append(issue("AUTH003", "--read-only is mandatory"))
        operations = {str(x.get("id")): x for x in scenario.get("operations", []) if isinstance(x, dict)}
        declared = {str(x.get("id")): x for x in adapter.get("operations", []) if isinstance(x, dict)}
        identity_ids = {x[0] for x in identities}
        for op_id, scenario_op in operations.items():
            if scenario_op.get("kind") == "read_other_owned":
                target = scenario_op.get("target_identity") or scenario_op.get("target_role")
                if target not in identity_ids or scenario_op.get("identity") == target:
                    errors.append(issue("AUTH001", "cross-read must name a different target identity", f"operations.{op_id}"))
        probe = scenario.get("state_probe", {})
        if not probe.get("must_equal"):
            errors.append(issue("AUTH002", "before/after equality is required", "scenario.state_probe"))
        if not errors:
            actors = []
            for identity_id, fixture, bindings in identities:
                for op_id, scenario_op in operations.items():
                    if scenario_op.get("identity") not in (None, identity_id) and scenario_op.get("role") not in (None, identity_id): continue
                    op = {**scenario_op, **declared.get(op_id, {})}
                    if not op.get("path"):
                        errors.append(issue("AUTH004", "operation path missing", f"operations.{op_id}")); continue
                    try: result = request(adapter, op, bindings=bindings)
                    except RuntimeBlocked: raise
                    except ValueError as exc: errors.append(issue("AUTH005", str(exc), f"operations.{op_id}")); continue
                    if not matches(result["status"], scenario_op.get("expected")):
                        errors.append(issue("AUTH001" if op.get("kind") == "read_other_owned" else "AUTH004", "unexpected status", f"operations.{op_id}"))
                    message = _message(result.get("payload"))
                    if op.get("kind") in {"read_other_owned", "mutation_forbidden"} and message.get("ok") is not False:
                        errors.append(issue("AUTH001", "prohibited operation was not denied", f"operations.{op_id}"))
                    observations.append({"identity": identity_id, "operation": op_id, "status": result["status"], "payload": safe_text(result.get("payload"))})
                    if op.get("kind") == "read_identity":
                        if message.get("ok") is not True or not _server_actor(result.get("payload")):
                            errors.append(issue("AUTH001", "identity endpoint did not confirm server-side actor", f"operations.{op_id}"))
                        actors.append(_server_actor(result.get("payload")))
            if len(actors) != len(identities) or len(set(actors)) != len(actors):
                errors.append(issue("AUTH001", "server-side actors must be non-empty and distinct", "identities"))
            merged_ops = [{**x, **declared.get(str(x.get("id")), {})} for x in operations.values()]
            before_ops = [x for x in merged_ops if x.get("kind") == "state_probe_before"]
            after_ops = [x for x in merged_ops if x.get("kind") == "state_probe_after"]
            if not before_ops or not after_ops:
                errors.append(issue("AUTH002", "real before/after probes are required", "state_probe"))
            else:
                # Probe payloads are observed from the runtime, never copied from input.
                before_values = [o for o in observations if o["operation"] in {x.get("id") for x in before_ops}]
                after_values = [o for o in observations if o["operation"] in {x.get("id") for x in after_ops}]
                if not before_values or not after_values or [x["payload"] for x in before_values] != [x["payload"] for x in after_values]:
                    errors.append(issue("AUTH002", "read-only state changed or probe missing", "state_probe"))
    except (ValueError, OSError) as exc:
        errors.append(issue("AUTH000", str(exc)))
    except RuntimeBlocked as exc:
        report = {"schema_version": "guardrails/v1", "verdict": "BLOCKED", "exit_code": 3, "issues": [issue("AUTH_RUNTIME", str(exc))], "mode": "read-only", "observations": []}
        output(report, args.format == "text"); return 3
    report = {"schema_version": "guardrails/v1", "verdict": "FAIL" if errors else "PASS", "exit_code": 1 if errors else 0, "issues": errors, "mode": "read-only", "observations": observations}
    output(report, args.format == "text")
    return report["exit_code"]

if __name__ == "__main__": sys.exit(main())
