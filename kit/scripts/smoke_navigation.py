#!/usr/bin/env python3
"""Execute a canonical navigation smoke with an existing Playwright runtime."""
from __future__ import annotations
import argparse, json, subprocess, sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from guardrails import validate_navigation
from smoke_runtime import RuntimeBlocked, load_json, output, reject_unsafe_contract, safe_text, issue, allowed_url, canonical_step_path


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
        errors.extend(reject_unsafe_contract(adapter, "adapter", allow_secret_names=True))
        errors.extend(reject_unsafe_contract(scenario, "scenario"))
        if adapter.get("schema_version") != "guardrails/v1" or scenario.get("schema_version") != "guardrails/v1": errors.append(issue("NAV000", "unsupported schema"))
        if not args.read_only: errors.append(issue("NAV005", "--read-only is mandatory"))
        if scenario.get("diagnostic_routes_are_not_canonical") and scenario.get("canonical_start") in scenario.get("diagnostic_routes", []): errors.append(issue("NAV001", "diagnostic route cannot be canonical"))
        base = str(adapter.get("base_url", scenario.get("base_url", "")))
        hosts = set(scenario.get("allowed_hosts", adapter.get("allowed_hosts", [])))
        path_allowlist = set(adapter.get("allowed_navigation_paths", scenario.get("allowed_navigation_paths", [])))
        if not base or not hosts: errors.append(issue("NAV000", "base_url and allowed_hosts are required"))
        if not errors:
            try:
                start = allowed_url(base, str(scenario.get("canonical_start", "/login")), hosts)
            except ValueError as exc:
                errors.append(issue("NAV003", str(exc)))
                start = ""
            if start:
                try:
                    from playwright.sync_api import sync_playwright
                except ImportError:
                    module_path = adapter.get("playwright_module")
                    if not module_path:
                        raise RuntimeBlocked("Playwright runtime is unavailable")
                    node_report = subprocess.run(
                        ["node", str(Path(__file__).with_name("navigation_runtime.mjs")), str(args.adapter), str(args.scenario)],
                        capture_output=True, text=True, timeout=int(adapter.get("timeout_ms", 10000)) / 1000 + 10,
                    )
                    try:
                        report = json.loads(node_report.stdout)
                    except json.JSONDecodeError:
                        report = {"schema_version": "guardrails/v1", "verdict": "FAIL", "exit_code": 1, "issues": [issue("NAV000", "node runtime returned invalid report")], "mode": "read-only", "observations": observations}
                    output(report, args.format == "text")
                    return int(report.get("exit_code", 1))
                browser_path = adapter.get("chromium_executable")
                with sync_playwright() as playwright:
                    launch = {"headless": True}
                    if browser_path:
                        p = Path(str(browser_path)).expanduser().resolve()
                        roots = [Path(x).expanduser().resolve() for x in adapter.get("allowed_binary_roots", [])]
                        if not p.is_file() or not roots or not any(p == root or root in p.parents for root in roots):
                            errors.append(issue("PREFLIGHT001", "unsafe browser executable"))
                        else: launch["executable_path"] = str(p)
                    if not errors:
                        browser = playwright.chromium.launch(**launch)
                        context = browser.new_context()
                        for cookie_name, env_name in (adapter.get("auth_cookie_bindings") or {}).items():
                            if not isinstance(cookie_name, str) or not isinstance(env_name, str) or not env_name.isidentifier():
                                errors.append(issue("SECURITY002", "invalid auth cookie binding", "adapter.auth_cookie_bindings")); continue
                            cookie_value = os.environ.get(env_name)
                            if not cookie_value:
                                raise RuntimeBlocked(f"missing auth cookie binding: {env_name}")
                            context.add_cookies([{"name": cookie_name, "value": cookie_value, "url": base}])
                        page = context.new_page()
                        def on_request(req):
                            try: host = req.url.split("/", 3)[2].split(":", 1)[0]
                            except IndexError: host = ""
                            observations.append({"kind": "request", "host": host, "method": req.method, "path": req.url.split(host, 1)[-1][:240] if host else ""})
                            if host not in hosts: errors.append(issue("NAV003", "external host denied", "requests"))
                        page.on("request", on_request)
                        def on_response(response):
                            parsed = response.url.split("/", 3)
                            path = "/" + parsed[3].split("?", 1)[0] if len(parsed) > 3 else "/"
                            if response.status in set(scenario.get("allowed_statuses", [])):
                                return
                            allowed_error = any(
                                isinstance(item, dict)
                                and item.get("status") == response.status
                                and item.get("path") == path
                                and item.get("decision_ref")
                                for item in scenario.get("known_errors", [])
                            )
                            if not allowed_error:
                                errors.append(issue("NAV002", "status not allowlisted", f"responses.{path}"))
                        page.on("response", on_response)
                        response = page.goto(start, wait_until="networkidle", timeout=int(adapter.get("timeout_ms", 10000)))
                        if response is None or response.status not in set(scenario.get("allowed_statuses", [])): errors.append(issue("NAV002", "canonical start status not allowlisted"))
                        for step in adapter.get("canonical_steps", []):
                            if not isinstance(step, dict):
                                errors.append(issue("NAV004", "only declarative navigation steps are allowed", "canonical_steps")); continue
                            if step.get("action") == "goto":
                                try:
                                    target = canonical_step_path(base, step.get("path"), hosts, path_allowlist)
                                except ValueError as exc:
                                    errors.append(issue("NAV004", str(exc), "canonical_steps")); continue
                                page.goto(target, wait_until="networkidle", timeout=int(adapter.get("timeout_ms", 10000)))
                            elif step.get("action") == "click" and isinstance(step.get("selector"), str) and step["selector"].startswith(("#", ".", "[")):
                                page.locator(step["selector"]).click(timeout=3000)
                            else:
                                errors.append(issue("NAV004", "only declarative goto paths and CSS click selectors are allowed", "canonical_steps")); continue
                            page.wait_for_load_state('networkidle')
                        current_host = page.url.split("/", 3)[2].split(":", 1)[0]
                        if current_host not in hosts: errors.append(issue("NAV003", "final host not allowlisted"))
                        observations.append({"kind": "final", "status": response.status if response else None, "path": page.url.split(current_host, 1)[-1][:240]})
                        context.close()
                        browser.close()
    except RuntimeBlocked as exc:
        report = {"schema_version": "guardrails/v1", "verdict": "BLOCKED", "exit_code": 3, "issues": [issue("NAV_RUNTIME", str(exc))], "mode": "read-only", "observations": observations}
        output(report, args.format == "text"); return 3
    except (ValueError, OSError, TimeoutError) as exc:
        errors.append(issue("NAV000", str(exc)))
    report = {"schema_version": "guardrails/v1", "verdict": "FAIL" if errors else "PASS", "exit_code": 1 if errors else 0, "issues": errors, "mode": "read-only", "observations": observations}
    output(report, args.format == "text")
    return report["exit_code"]

if __name__ == "__main__": sys.exit(main())
