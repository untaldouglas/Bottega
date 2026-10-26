"""Safe declarative runtime helpers for read-only guardrail smokes."""
from __future__ import annotations
import json, os, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from typing import Any

SCHEMA = "guardrails/v1"
_SECRET = re.compile(r"(?i)(password|passwd|token|secret|cookie|authorization|bearer|api[_-]?key|ssn|email|phone|dni)")
_UNSAFE = re.compile(r"[;&|`$<>\n\r]|\b(?:sh|bash|zsh|powershell|cmd|python|node)\b", re.I)

class RuntimeBlocked(Exception):
    pass

def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid contract: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise ValueError("contract must be an object")
    return value

def safe_text(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _SECRET.sub("[REDACTED]", text)

def reject_unsafe_contract(value: Any, path: str = "$", *, allow_secret_names=False) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if _UNSAFE.search(key_text) or (not allow_secret_names and _SECRET.search(key_text)):
                issues.append({"code": "SECURITY002", "path": f"{path}.{key_text}", "message": "free command or secret field rejected"})
            issues.extend(reject_unsafe_contract(item, f"{path}.{key_text}", allow_secret_names=allow_secret_names))
    elif isinstance(value, list):
        for i, item in enumerate(value): issues.extend(reject_unsafe_contract(item, f"{path}[{i}]", allow_secret_names=allow_secret_names))
    elif isinstance(value, str) and not path.endswith(".expected") and _UNSAFE.search(value):
        issues.append({"code": "SECURITY002", "path": path, "message": "shell-like command rejected"})
    return issues

def allowed_url(base_url: str, path: str, hosts: set[str]) -> str:
    if not isinstance(path, str) or not path.startswith("/") or ".." in Path(urllib.parse.urlsplit(path).path).parts:
        raise ValueError("PATH001: safe absolute relative path required")
    source = urllib.parse.urlsplit(path)
    if source.scheme or source.netloc or source.fragment:
        raise ValueError("PATH001: absolute URL, host, or fragment is forbidden")
    if any(_SECRET.search(key) for key in urllib.parse.parse_qs(source.query, keep_blank_values=True)):
        raise ValueError("SECURITY002: sensitive query parameter is forbidden")
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in hosts:
        raise ValueError("NAV003: host is not allowlisted")
    return url

def canonical_step_path(base_url: str, path: Any, hosts: set[str], allowlist: set[str]) -> str:
    if not isinstance(path, str):
        raise ValueError("PATH001: goto path must be a string")
    parsed = urllib.parse.urlsplit(path)
    if parsed.path not in allowlist:
        raise ValueError("PATH001: goto path is outside the declared allowlist")
    return allowed_url(base_url, path, hosts)

def env_headers(adapter: dict[str, Any], bindings: dict[str, str] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for name, env_name in (bindings if bindings is not None else adapter.get("secret_bindings") or {}).items():
        if not isinstance(name, str) or not isinstance(env_name, str) or not re.fullmatch(r"[A-Z_][A-Z0-9_]*", env_name):
            raise ValueError("invalid secret binding")
        value = os.environ.get(env_name)
        if not value: raise RuntimeBlocked(f"missing secret binding: {env_name}")
        headers[name] = value
    return headers

def request(adapter: dict[str, Any], operation: dict[str, Any], *, timeout: float = 10,
            bindings: dict[str, str] | None = None) -> dict[str, Any]:
    url = allowed_url(str(adapter.get("base_url", "")), str(operation.get("path", "")), set(adapter.get("allowed_hosts", [])))
    method = str(operation.get("method", "GET")).upper()
    if method not in {"GET", "HEAD", "OPTIONS"}:
        if operation.get("kind") != "mutation_forbidden": raise ValueError("AUTH003: mutation not allowed")
    body = operation.get("body")
    if body is not None and method not in {"GET", "HEAD", "OPTIONS"}: raise ValueError("AUTH003: request body forbidden")
    headers = {"Accept": "application/json", **env_headers(adapter, bindings)}
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(128 * 1024)
            status = response.status
            response_headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        raw = exc.read(128 * 1024); status = exc.code; response_headers = dict(exc.headers)
    except (OSError, urllib.error.URLError) as exc:
        raise RuntimeBlocked(f"runtime request unavailable: {type(exc).__name__}") from exc
    try: payload: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError): payload = {"text": raw.decode("utf-8", "replace")[:1000]}
    return {"operation": operation.get("id"), "status": status, "headers": {"content-type": response_headers.get("Content-Type", "")}, "payload": payload}

def matches(status: int, expected: Any) -> bool:
    if expected is None: return True
    return str(status) in {x.strip() for x in str(expected).split("|")}

def issue(code: str, message: str, path: str = "$") -> dict[str, str]:
    return {"code": code, "path": path, "message": message}

def output(report: dict[str, Any], text: bool) -> None:
    print("SMOKE_" + str(report["verdict"]) if text else json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
