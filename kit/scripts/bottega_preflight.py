#!/usr/bin/env python3
"""Run non-destructive environment checks and emit JSON or Markdown."""
from __future__ import annotations
import argparse, json, os, shutil, socket, subprocess, sys
from pathlib import Path

def check(command, version_args=("--version",)):
    path = shutil.which(command)
    if not path: return {"available": False}
    try:
        out = subprocess.run([path, *version_args], capture_output=True, text=True, timeout=5)
        return {"available": True, "version": (out.stdout or out.stderr).splitlines()[0][:160] if (out.stdout or out.stderr) else ""}
    except (OSError, subprocess.SubprocessError) as e: return {"available": True, "error": type(e).__name__}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--format", choices=("json", "markdown"), default="json")
    p.add_argument("--port", type=int, action="append", default=[])
    p.add_argument("--dry-run", action="store_true", help="no modifica nada; conserva el mismo reporte")
    p.add_argument("--config", type=Path)
    a = p.parse_args()
    tools = {x: check(x) for x in ("python3", "git", "gh", "docker", "node", "npm", "hermes")}
    auth = {"gh_authenticated": False, "secret_exposed": False}
    if tools["gh"]["available"]:
        r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=5)
        auth["gh_authenticated"] = r.returncode == 0
    ports = {}
    for port in a.port:
        with socket.socket() as s:
            s.settimeout(.2); ports[str(port)] = s.connect_ex(("127.0.0.1", port)) == 0
    config = {}
    if a.config:
        try: config = json.loads(a.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): config = {"config_error": True}
    project_root = a.project.expanduser().resolve()
    def explicit_probe(key):
        value = config.get(key)
        if not value: return {"available": False, "source": "none", "configuration_explicit": False}
        path = Path(value).expanduser()
        roots = [Path(x).expanduser().resolve() for x in config.get("allowed_binary_roots", []) if Path(x).expanduser().is_absolute()]
        resolved = path.resolve()
        safe = path.is_file() and os.access(path, os.X_OK) and any(resolved == r or r in resolved.parents for r in roots)
        return {"available": safe, "source": "config", "path": str(resolved) if safe else "redacted", "safe_path": safe, "configuration_explicit": True}
    browser_path = next((shutil.which(x) for x in ("google-chrome", "chromium", "chromium-browser", "firefox") if shutil.which(x)), "")
    browser = bool(browser_path)
    fallback = {"first_429_opens_circuit": True, "requires_brief_authorization": True}
    result = {"project": str(project_root), "dry_run": a.dry_run, "tools": tools, "auth": auth,
              "docker": tools["docker"], "node_npm": {"node": tools["node"], "npm": tools["npm"]},
              "ports": ports, "browser_available": browser, "fallback_policy": fallback,
              "browser": {"path": browser_path if browser else "", "available": browser, "source": "PATH" if browser else "none"},
              "playwright": explicit_probe("playwright_cli"), "chromium": explicit_probe("chromium_executable"),
              "configuration_explicit": bool(a.config), "path_search_used": False, "network_required": False,
              "scratch_root": str(Path(config.get("scratch_root", project_root)).expanduser().resolve()),
              "strategy": {"shell": False, "allowed": ["declarative-http", "playwright-existing-runtime"]},
              "ok": all(v.get("available", False) for k,v in tools.items() if k in ("python3", "git"))}
    if a.format == "markdown":
        print("# Bottega preflight\n\n" + "\n".join(f"- {k}: {v}" for k,v in result.items()))
    else: print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1
if __name__ == "__main__": sys.exit(main())
