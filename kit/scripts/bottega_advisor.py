#!/usr/bin/env python3
"""Bottega Advisor (Incremento 1) — motor determinista, sin LLM ni proveedor.

Sólo lectura. Valida un intake estructurado, produce un reporte conforme a
esquema, separa hechos/supuestos/preguntas abiertas/NO DETERMINABLE, emite la
biblioteca fija de requisitos (I1) y exporta un expediente hasheado y legible
sin sesión viva. Nunca autoriza ejecución, release, publicación ni producción.

Subcomandos: validate-intake, prepare-report, validate-report, export-casefile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - PyYAML es dependencia declarada del contrato
    yaml = None  # type: ignore

ENGINE_NAME = "bottega_advisor.py"
ENGINE_VERSION = "1.0.0"
ADVISOR_ENVELOPE_SCHEMA = "advisor/v1"
INTAKE_SCHEMA_VERSION = "advisor-intake/v1"
REPORT_SCHEMA_VERSION = "advisor-report/v1"

# ---------------------------------------------------------------------------
# Catálogo de errores normalizado (sección 7 del contrato)
# ---------------------------------------------------------------------------
# (code, severity, exit) — severity: blocked | error | warning
# NO_DETERMINABLE y POTENTIAL_SECRET no cambian el código de salida.

# ---------------------------------------------------------------------------
# Enums y campos canónicos (deben coincidir con los .schema.json; TA-021)
# ---------------------------------------------------------------------------
ACTOR_ROLES = {"director", "usuario_advisor", "operador_taller", "revisor", "bot_etapa", "otro"}
SYNTHETIC_CLASSES = {"SYNTHETIC", "SYNTHETIC_FIXTURE"}
NON_SYNTHETIC_CLASSES = {"REAL", "INSTITUTIONAL", "PRODUCTION", "PII", "SECRET", "MIXED"}
REPORT_VERDICTS = {"PASS", "NEEDS_WORK", "BLOCKED"}
CLASIFICACIONES = {"HECHO", "SUPUESTO", "PREGUNTA_ABIERTA", "NO_DETERMINABLE"}
PROXIMO_PASO_ACCIONES = {"solicitar_revision_independiente", "corregir_intake", "detener"}

ID_RE = re.compile(r"^[A-Z][A-Z0-9_-]{2,63}$")
REPORT_ID_RE = re.compile(r"^REP-[A-Z0-9_-]{2,63}$")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")

INTAKE_TOP_LEVEL_ALLOWED = {
    "schema_version", "initiative", "necesidad", "resultado_esperado", "actores",
    "clasificacion_datos", "owner", "alcance", "alternativas", "riesgos",
    "preguntas_explicitas_no_determinable", "proveedor", "modelo", "metadatos",
}
INTAKE_TOP_LEVEL_REQUIRED = {
    "schema_version", "initiative", "necesidad", "resultado_esperado", "actores",
    "clasificacion_datos", "owner", "alcance",
}
INTAKE_INITIATIVE_ALLOWED = {"id", "name", "mode"}
INTAKE_NECESIDAD_ALLOWED = {"descripcion", "contexto"}
INTAKE_RESULTADO_ALLOWED = {"descripcion", "no_definido", "medible"}
INTAKE_MEDIBLE_ALLOWED = {"metrica", "baseline", "denominador"}
INTAKE_ALCANCE_ALLOWED = {"incluido", "excluido"}
INTAKE_METADATOS_ALLOWED = {"entorno", "autor", "fecha"}
INTAKE_ACTOR_ALLOWED = {"id", "rol", "nombre", "trabajo", "autoridad", "limite"}
INTAKE_ALTERNATIVA_ALLOWED = {"id", "descripcion", "tradeoffs"}
INTAKE_RIESGO_ALLOWED = {"id", "descripcion", "mitigacion"}

REPORT_TOP_LEVEL_ALLOWED = {
    "schema_version", "report_id", "initiative_id", "created_at", "engine",
    "verdict", "problema", "resultado_esperado", "actores", "trabajos",
    "alternativas", "alcance", "hechos", "supuestos", "preguntas_abiertas",
    "no_determinable", "requisitos", "criterios_aceptacion", "riesgos",
    "decisiones_humanas", "proximo_paso", "no_autorizado", "trazabilidad",
}
REPORT_TOP_LEVEL_REQUIRED = set(REPORT_TOP_LEVEL_ALLOWED)
REPORT_ENGINE_ALLOWED = {"name", "version", "deterministic", "proveedor_efectivo", "modelo_efectivo"}
REPORT_CLASIFICADO_ALLOWED = {"texto", "clasificacion", "origen"}
REPORT_ACTOR_ALLOWED = {"id", "rol", "nombre", "trabajo", "autoridad", "limite", "clasificacion", "origen"}
REPORT_TRABAJO_ALLOWED = {"id", "actor_id", "descripcion", "clasificacion", "origen"}
REPORT_ALTERNATIVA_ALLOWED = {"id", "descripcion", "tradeoffs", "clasificacion"}
REPORT_ALCANCE_ALLOWED = {"incluido", "excluido", "clasificacion"}
REPORT_HECHO_ALLOWED = {"id", "afirmacion", "origen"}
REPORT_PREGUNTA_ALLOWED = {"id", "pregunta", "campo_faltante"}
REPORT_ND_ALLOWED = {"id", "afirmacion", "razon", "owner_decision"}
REPORT_REQUISITO_ALLOWED = {"id", "descripcion", "criterio", "prueba_planeada", "owner", "estado", "evidencia"}
REPORT_CA_ALLOWED = {"id", "descripcion", "metodo", "estado"}
REPORT_RIESGO_ALLOWED = {"id", "descripcion", "mitigacion", "clasificacion", "origen"}
REPORT_DECISION_ALLOWED = {"id", "decision", "owner", "consecuencia", "autorizacion_ejecucion"}
REPORT_PROXIMO_ALLOWED = {"accion", "detalle"}
REPORT_TRAZABILIDAD_ALLOWED = {"completa", "requisitos_sin_criterio", "requisitos_sin_prueba", "requisitos_sin_owner"}

NO_AUTORIZADO_REQUIRED = {"ejecucion", "release", "publicacion", "produccion"}
NO_AUTORIZADO_FULL = ["ejecucion", "release", "publicacion", "produccion", "merge", "frappe", "llm_proveedor"]

# ---------------------------------------------------------------------------
# Biblioteca fija de requisitos del Advisor (sección 4.1)
# ---------------------------------------------------------------------------
REQUIREMENTS_RF = [
    {"id": "RF-001", "descripcion": "Modo Advisor distinguible con propósito, permisos, salida y límites visibles.", "criterio": "CA-001", "prueba_planeada": "TA-001"},
    {"id": "RF-002", "descripcion": "Advisor produce pregunta, problema, actores, trabajos, alcance, supuestos, riesgos, requisitos y criterios, marcando lo no verificable como NO DETERMINABLE.", "criterio": "CA-003", "prueba_planeada": "TA-008"},
    {"id": "RF-007", "descripcion": "Trazabilidad requisito → criterio → prueba → owner → resultado (documental).", "criterio": "CA-005", "prueba_planeada": "TA-014"},
    {"id": "RF-015", "descripcion": "Datos sintéticos por defecto; sin secretos en artefactos/logs.", "criterio": "CA-012", "prueba_planeada": "TA-004"},
]
REQUIREMENTS_RNF = [
    {"id": "RNF-006", "descripcion": "No se revelan secretos, tokens, credenciales, rutas privadas ni datos institucionales.", "criterio": "CA-012", "prueba_planeada": "TA-005"},
    {"id": "RNF-010", "descripcion": "Cada bloqueo indica condición incumplida, evidencia esperada y responsable.", "criterio": "CA-003", "prueba_planeada": "TA-002"},
    {"id": "RNF-011", "descripcion": "Expediente exportable/revisable sin sesión viva del proveedor.", "criterio": "CA-019", "prueba_planeada": "TA-015"},
]

CRITERIOS_ACEPTACION = [
    {"id": "CA-001", "descripcion": "Dado un expediente nuevo, una revisión de interfaz/documentación muestra los tres modos Advisor, Taller y Auditor, cada uno con objetivo, entrada, salida y límites; falta de cualquiera = FAIL.", "metodo": "Inspección documental y prueba de aceptación."},
    {"id": "CA-003", "descripcion": "Dada una necesidad incompleta, la salida contiene preguntas, hechos, supuestos, preguntas abiertas, requisitos y criterios; cualquier afirmación no sustentada aparece como NO DETERMINABLE.", "metodo": "Fixture fija y revisión contra esquema."},
    {"id": "CA-005", "descripcion": "Para cada requisito requerido, el manifiesto enlaza criterio, prueba, owner y evidencia; se rechaza un manifiesto al que le falte cualquiera.", "metodo": "Validación de manifiesto con caso válido e inválido."},
    {"id": "CA-012", "descripcion": "En una ejecución con datos sintéticos, el escaneo de secretos no encuentra tokens y el expediente no contiene datos institucionales.", "metodo": "Scan de secretos y revisión de artefactos."},
    {"id": "CA-019", "descripcion": "El paquete contiene Summary, Evidence y Merge Danger y no se cierra sin revisión independiente.", "metodo": "Checklist de gate y revisión de expediente."},
]

# Riesgos bibliotecarios (sección 4.2)
LIBRARY_RISKS = [
    {"id": "R-001", "descripcion": "Confundir PASS técnico con autorización institucional.", "mitigacion": "Estados independientes, aceptación humana explícita y CA-007/008/020."},
    {"id": "R-005", "descripcion": "Evidencia sintética presentada como evidencia de producto.", "mitigacion": "Clasificación explícita de datos, fuente y entorno en manifiestos; etiqueta NO DETERMINABLE cuando corresponda."},
    {"id": "R-006", "descripcion": "Producto 02 reabierto por dependencia histórica.", "mitigacion": "Fuera de alcance, bloqueo explícito y CA-015."},
]

# Decisiones humanas (sección 4.3, del AUTONOMY-POLICY)
HUMAN_DECISIONS = [
    {"id": "DH-01", "decision": "Aceptar o rechazar la propuesta del Advisor como insumo de trabajo.", "owner": "Director/owner", "consecuencia": "Sin aceptación no se abre Taller ni se ejecuta nada."},
    {"id": "DH-02", "decision": "Resolver los NO DETERMINABLE antes de avanzar.", "owner": "Director/owner", "consecuencia": "Un NO DETERMINABLE no se rellena con valores inventados."},
    {"id": "DH-03", "decision": "Autorizar el siguiente gate.", "owner": "Director/owner", "consecuencia": "Sin autorización explícita no se avanza de etapa."},
]

# ---------------------------------------------------------------------------
# Scan de secretos (sección 8) — patrones deterministas, orden fijo
# ---------------------------------------------------------------------------
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("generic_api_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("private_key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("credential_assignment", re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|authorization)\s*[:=]\s*\S+")),
    ("bearer_header", re.compile(r"(?i)authorization\s*:\s*bearer\s+\S+")),
    ("private_path", re.compile(r"/(home|root|Users)/\S+|~/\.|\.ssh/|id_rsa|\.env|/home/dagalindo")),
]
BASE64_RUN = re.compile(r"[A-Za-z0-9+/=_-]{40,}")
CRED_KEYWORD = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|credential|authorization|bearer)")

# Patrón textual de fuera de alcance (sección 7, OUT_OF_SCOPE)
OUT_OF_SCOPE_TEXT = re.compile(
    r"(?i)(\bP02_\w*|producto\s*02|producci[oó]n|frappe|\brelease\b|\bpublicaci[oó]n\b|\bmerge\b|llm|openai|anthropic|claude|gpt[-_ ]?[0-9])"
)


# ---------------------------------------------------------------------------
# Serialización canónica e integridad
# ---------------------------------------------------------------------------
def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_canonical(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _short_id(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:8].upper()


def make_report_id(initiative_id: str) -> str:
    return f"REP-{_short_id(initiative_id)}-0001"


def make_casefile_id(initiative_id: str) -> str:
    return f"CF-{_short_id(initiative_id)}-0001"


def system_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Issues y envelope
# ---------------------------------------------------------------------------
def issue(code: str, path: str, value: Any, message: str, severity: str = "error") -> dict[str, Any]:
    if isinstance(value, (str, int, float, bool)) or value is None:
        safe: Any = value
    else:
        safe = type(value).__name__
    return {"code": code, "severity": severity, "path": path, "safe_value": safe, "message": message}


def secret_issue(path: str, kind: str) -> dict[str, Any]:
    return issue("SECRET_DETECTED", path, "[REDACTED]", f"secreto detectado ({kind})", "blocked")


def envelope(command: str, issues: list[dict], observations: list[Any] | None = None) -> dict[str, Any]:
    observations = observations or []
    blocked = [i for i in issues if i["severity"] == "blocked"]
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    if blocked:
        verdict, exit_code = "BLOCKED", 3
    elif errors:
        verdict, exit_code = "NEEDS_WORK", 1
    else:
        verdict, exit_code = "PASS", 0
    return {
        "schema_version": ADVISOR_ENVELOPE_SCHEMA,
        "command": command,
        "verdict": verdict,
        "exit_code": exit_code,
        "counts": {"errors": len(errors), "warnings": len(warnings), "blocked": len(blocked)},
        "issues": issues,
        "observations": observations,
    }


def io_error_envelope(command: str, message: str) -> dict[str, Any]:
    env = envelope(command, [issue("IO_ERROR", "$", None, message, "error")])
    env["exit_code"] = 2
    env["verdict"] = "NEEDS_WORK"
    return env


# ---------------------------------------------------------------------------
# Lectura de documentos (YAML o JSON)
# ---------------------------------------------------------------------------
def load_document(path: str) -> tuple[Any, str | None]:
    p = Path(path)
    if not p.is_file():
        return None, f"archivo no encontrado: {path}"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"no se pudo leer {path}: {exc}"
    if yaml is not None:
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            return None, f"documento malformado: {exc}"
    else:
        try:
            doc = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, f"documento JSON malformado: {exc}"
    if doc is None:
        return None, "documento vacío"
    return doc, None


# ---------------------------------------------------------------------------
# Scan de secretos
# ---------------------------------------------------------------------------
def _entropy(s: str) -> float:
    n = len(s)
    if n == 0:
        return 0.0
    counts = Counter(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def iter_strings(node: Any, path: str = "") -> Any:
    if isinstance(node, dict):
        for k, v in node.items():
            child = f"{path}.{k}" if path else k
            yield from iter_strings(v, child)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def scan_document(doc: Any) -> list[dict]:
    issues: list[dict] = []
    for path, value in iter_strings(doc):
        detected = None
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(value):
                detected = name
                break
        if detected:
            issues.append(secret_issue(path, detected))
            continue
        for run in BASE64_RUN.findall(value):
            if _entropy(run) >= 4.5:
                if CRED_KEYWORD.search(value):
                    issues.append(secret_issue(path, "alta entropía junto a palabra-clave"))
                else:
                    issues.append(issue("POTENTIAL_SECRET", path, "[REDACTED]", "valor de alta entropía sin palabra-clave de credencial", "warning"))
                break
    return issues


# ---------------------------------------------------------------------------
# Validación de intake
# ---------------------------------------------------------------------------
def _check_unknown(doc: dict, allowed: set, path: str, issues: list[dict]) -> None:
    for key in doc:
        if key not in allowed:
            issues.append(issue("SCHEMA_INVALID", f"{path}.{key}" if path != "$" else key, key, "campo desconocido", "error"))


def _check_string(doc: dict, key: str, path: str, issues: list[dict], *, required: bool, min_len: int = 1, max_len: int | None = None, allow_control: bool = False) -> str:
    value = doc.get(key)
    if value is None or (isinstance(value, str) and value == ""):
        if required:
            issues.append(issue("FIELD_MISSING", f"{path}.{key}", None, "campo requerido ausente o vacío", "error"))
        return ""
    if not isinstance(value, str):
        issues.append(issue("SCHEMA_INVALID", f"{path}.{key}", value, "se esperaba string", "error"))
        return ""
    if len(value) < min_len:
        issues.append(issue("SCHEMA_INVALID", f"{path}.{key}", value, f"longitud mínima {min_len}", "error"))
    if max_len is not None and len(value) > max_len:
        issues.append(issue("SCHEMA_INVALID", f"{path}.{key}", value, f"longitud máxima {max_len}", "error"))
    if not allow_control and CONTROL_CHARS_RE.search(value):
        issues.append(issue("SCHEMA_INVALID", f"{path}.{key}", value, "contiene caracteres de control", "error"))
    return value


def _check_id(doc: dict, key: str, path: str, issues: list[dict], seen: set) -> str:
    value = doc.get(key)
    if value is None or value == "":
        issues.append(issue("FIELD_MISSING", f"{path}.{key}", None, "campo requerido ausente o vacío", "error"))
        return ""
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        issues.append(issue("SCHEMA_INVALID", f"{path}.{key}", value, "formato de id inválido (^[A-Z][A-Z0-9_-]{2,63}$)", "error"))
        return value if isinstance(value, str) else ""
    if value in seen:
        issues.append(issue("DUPLICATE_ID", f"{path}.{key}", value, "id duplicado", "error"))
    seen.add(value)
    return value


def validate_intake_schema(doc: Any) -> list[dict]:
    issues: list[dict] = []
    if not isinstance(doc, dict):
        return [issue("SCHEMA_INVALID", "$", doc, "se esperaba un objeto", "error")]
    _check_unknown(doc, INTAKE_TOP_LEVEL_ALLOWED, "$", issues)

    for key in sorted(INTAKE_TOP_LEVEL_REQUIRED):
        if key not in doc:
            issues.append(issue("FIELD_MISSING", key, None, "campo requerido ausente", "error"))

    if doc.get("schema_version") != INTAKE_SCHEMA_VERSION:
        issues.append(issue("SCHEMA_INVALID", "schema_version", doc.get("schema_version"), f"debe ser {INTAKE_SCHEMA_VERSION}", "error"))

    # initiative
    init = doc.get("initiative")
    if isinstance(init, dict):
        _check_unknown(init, INTAKE_INITIATIVE_ALLOWED, "initiative", issues)
        _check_id(init, "id", "initiative", issues, set())
        _check_string(init, "name", "initiative", issues, required=True, max_len=120)
        if init.get("mode") != "advisor":
            issues.append(issue("SCHEMA_INVALID", "initiative.mode", init.get("mode"), "debe ser 'advisor'", "error"))
    elif "initiative" in doc:
        issues.append(issue("SCHEMA_INVALID", "initiative", init, "se esperaba un objeto", "error"))

    # necesidad
    nec = doc.get("necesidad")
    if isinstance(nec, dict):
        _check_unknown(nec, INTAKE_NECESIDAD_ALLOWED, "necesidad", issues)
        _check_string(nec, "descripcion", "necesidad", issues, required=True, max_len=4000)
        if "contexto" in nec:
            _check_string(nec, "contexto", "necesidad", issues, required=False, max_len=2000)
    elif "necesidad" in doc:
        issues.append(issue("SCHEMA_INVALID", "necesidad", nec, "se esperaba un objeto", "error"))

    # resultado_esperado
    re_obj = doc.get("resultado_esperado")
    if isinstance(re_obj, dict):
        _check_unknown(re_obj, INTAKE_RESULTADO_ALLOWED, "resultado_esperado", issues)
        no_definido = re_obj.get("no_definido")
        if not isinstance(no_definido, bool):
            issues.append(issue("SCHEMA_INVALID", "resultado_esperado.no_definido", no_definido, "se esperaba bool", "error"))
            no_definido = False
        desc = re_obj.get("descripcion")
        if no_definido:
            if isinstance(desc, str) and desc != "":
                issues.append(issue("SCHEMA_INVALID", "resultado_esperado.descripcion", desc, "debe estar vacío cuando no_definido es true", "error"))
        else:
            _check_string(re_obj, "descripcion", "resultado_esperado", issues, required=True)
        medible = re_obj.get("medible")
        if medible is not None:
            if isinstance(medible, dict):
                _check_unknown(medible, INTAKE_MEDIBLE_ALLOWED, "resultado_esperado.medible", issues)
                for mk in ("metrica", "baseline", "denominador"):
                    if mk in medible:
                        _check_string(medible, mk, "resultado_esperado.medible", issues, required=False, min_len=0)
            else:
                issues.append(issue("SCHEMA_INVALID", "resultado_esperado.medible", medible, "se esperaba un objeto", "error"))
    elif "resultado_esperado" in doc:
        issues.append(issue("SCHEMA_INVALID", "resultado_esperado", re_obj, "se esperaba un objeto", "error"))

    # actores
    actores = doc.get("actores")
    if isinstance(actores, list):
        if len(actores) < 1:
            issues.append(issue("FIELD_MISSING", "actores", actores, "se requiere al menos un actor", "error"))
        seen = set()
        for i, a in enumerate(actores):
            p = f"actores[{i}]"
            if not isinstance(a, dict):
                issues.append(issue("SCHEMA_INVALID", p, a, "se esperaba un objeto", "error"))
                continue
            _check_unknown(a, INTAKE_ACTOR_ALLOWED, p, issues)
            _check_id(a, "id", p, issues, seen)
            if a.get("rol") not in ACTOR_ROLES:
                issues.append(issue("SCHEMA_INVALID", f"{p}.rol", a.get("rol"), f"rol inválido (debe ser uno de {sorted(ACTOR_ROLES)})", "error"))
            _check_string(a, "nombre", p, issues, required=True, max_len=120)
            for ok in ("trabajo", "autoridad", "limite"):
                if ok in a:
                    _check_string(a, ok, p, issues, required=False, min_len=0)
    elif "actores" in doc:
        issues.append(issue("SCHEMA_INVALID", "actores", actores, "se esperaba una lista", "error"))

    # owner
    _check_string(doc, "owner", "$", issues, required=True, max_len=120)

    # alcance
    alcance = doc.get("alcance")
    if isinstance(alcance, dict):
        _check_unknown(alcance, INTAKE_ALCANCE_ALLOWED, "alcance", issues)
        for key in ("incluido", "excluido"):
            val = alcance.get(key)
            if not isinstance(val, list) or len(val) < 1:
                issues.append(issue("FIELD_MISSING", f"alcance.{key}", val, "se requiere una lista no vacía", "error"))
            else:
                for i, item in enumerate(val):
                    if not isinstance(item, str) or item == "":
                        issues.append(issue("SCHEMA_INVALID", f"alcance.{key}[{i}]", item, "string no vacío requerido", "error"))
    elif "alcance" in doc:
        issues.append(issue("SCHEMA_INVALID", "alcance", alcance, "se esperaba un objeto", "error"))

    # alternativas
    alternativas = doc.get("alternativas")
    if isinstance(alternativas, list):
        seen = set()
        for i, alt in enumerate(alternativas):
            p = f"alternativas[{i}]"
            if not isinstance(alt, dict):
                issues.append(issue("SCHEMA_INVALID", p, alt, "se esperaba un objeto", "error"))
                continue
            _check_unknown(alt, INTAKE_ALTERNATIVA_ALLOWED, p, issues)
            _check_id(alt, "id", p, issues, seen)
            _check_string(alt, "descripcion", p, issues, required=True)
            if "tradeoffs" in alt:
                _check_string(alt, "tradeoffs", p, issues, required=False, min_len=0)

    # riesgos
    riesgos = doc.get("riesgos")
    if isinstance(riesgos, list):
        seen = set()
        for i, r in enumerate(riesgos):
            p = f"riesgos[{i}]"
            if not isinstance(r, dict):
                issues.append(issue("SCHEMA_INVALID", p, r, "se esperaba un objeto", "error"))
                continue
            _check_unknown(r, INTAKE_RIESGO_ALLOWED, p, issues)
            _check_id(r, "id", p, issues, seen)
            _check_string(r, "descripcion", p, issues, required=True)
            if "mitigacion" in r:
                _check_string(r, "mitigacion", p, issues, required=False, min_len=0)

    # preguntas_explicitas_no_determinable
    preguntas = doc.get("preguntas_explicitas_no_determinable")
    if preguntas is not None and not isinstance(preguntas, list):
        issues.append(issue("SCHEMA_INVALID", "preguntas_explicitas_no_determinable", preguntas, "se esperaba una lista", "error"))

    # metadatos
    meta = doc.get("metadatos")
    if meta is not None:
        if isinstance(meta, dict):
            _check_unknown(meta, INTAKE_METADATOS_ALLOWED, "metadatos", issues)
            if "entorno" in meta and meta.get("entorno") != "local-sandbox":
                issues.append(issue("SCHEMA_INVALID", "metadatos.entorno", meta.get("entorno"), "debe ser 'local-sandbox'", "error"))
        else:
            issues.append(issue("SCHEMA_INVALID", "metadatos", meta, "se esperaba un objeto", "error"))

    return issues


def validate_intake_scope(doc: Any) -> list[dict]:
    issues: list[dict] = []
    if not isinstance(doc, dict):
        return issues
    # clasificacion_datos: no sintética ⇒ OUT_OF_SCOPE (bloqueo)
    clasificacion = doc.get("clasificacion_datos")
    if clasificacion is not None and clasificacion not in SYNTHETIC_CLASSES:
        issues.append(issue("OUT_OF_SCOPE", "clasificacion_datos", clasificacion, "clasificación de datos no sintética (sólo SYNTHETIC/SYNTHETIC_FIXTURE)", "blocked"))
    # proveedor/modelo: != none ⇒ OUT_OF_SCOPE (I1 prohíbe LLM/proveedor)
    if doc.get("proveedor") is not None and doc.get("proveedor") != "none":
        issues.append(issue("OUT_OF_SCOPE", "proveedor", doc.get("proveedor"), "proveedor distinto de 'none' está prohibido en I1", "blocked"))
    if doc.get("modelo") is not None and doc.get("modelo") != "none":
        issues.append(issue("OUT_OF_SCOPE", "modelo", doc.get("modelo"), "modelo distinto de 'none' está prohibido en I1", "blocked"))
    # Detección textual de fuera de alcance (Producto 02 / producción / Frappe / LLM / release)
    textual_fields = [
        ("initiative.name", (doc.get("initiative") or {}).get("name")),
        ("necesidad.descripcion", (doc.get("necesidad") or {}).get("descripcion")),
        ("resultado_esperado.descripcion", (doc.get("resultado_esperado") or {}).get("descripcion")),
    ]
    for path, value in textual_fields:
        if isinstance(value, str) and OUT_OF_SCOPE_TEXT.search(value):
            issues.append(issue("OUT_OF_SCOPE", path, value, "contenido fuera de alcance (Producto 02/producción/Frappe/LLM/release)", "blocked"))
    incluido = ((doc.get("alcance") or {}).get("incluido") or [])
    for i, item in enumerate(incluido):
        if isinstance(item, str) and OUT_OF_SCOPE_TEXT.search(item):
            issues.append(issue("OUT_OF_SCOPE", f"alcance.incluido[{i}]", item, "contenido fuera de alcance (Producto 02/producción/Frappe/LLM/release)", "blocked"))
    return issues


def validate_intake(doc: Any) -> list[dict]:
    """Flujo de validate-intake (sección 5.1): secret scan → schema → scope."""
    secret_issues = scan_document(doc)
    if any(i["severity"] == "blocked" for i in secret_issues):
        return secret_issues
    warnings = [i for i in secret_issues if i["severity"] == "warning"]
    return warnings + validate_intake_schema(doc) + validate_intake_scope(doc)


# ---------------------------------------------------------------------------
# Construcción del reporte (sección 4)
# ---------------------------------------------------------------------------
def build_report(intake: dict, now: str, report_id: str) -> dict:
    initiative_id = intake["initiative"]["id"]
    owner = intake.get("owner", "")
    re_obj = intake.get("resultado_esperado", {})
    no_definido = bool(re_obj.get("no_definido", False))
    medible = re_obj.get("medible") or {}

    problema = {
        "texto": intake.get("necesidad", {}).get("descripcion", ""),
        "clasificacion": "HECHO",
        "origen": "intake.necesidad.descripcion",
    }
    resultado_esperado = {
        "texto": re_obj.get("descripcion", ""),
        "clasificacion": "PREGUNTA_ABIERTA" if no_definido else "HECHO",
        "origen": "intake.resultado_esperado.descripcion",
    }

    actores = []
    trabajos = []
    preguntas_abiertas = []
    pid = 1
    for i, a in enumerate(intake.get("actores", [])):
        actores.append({
            "id": a.get("id", ""), "rol": a.get("rol", ""), "nombre": a.get("nombre", ""),
            "trabajo": a.get("trabajo", ""), "autoridad": a.get("autoridad", ""), "limite": a.get("limite", ""),
            "clasificacion": "HECHO", "origen": f"intake.actores[{i}]",
        })
        if a.get("trabajo"):
            trabajos.append({
                "id": f"TRAB-{len(trabajos) + 1:02d}", "actor_id": a.get("id", ""),
                "descripcion": a["trabajo"], "clasificacion": "HECHO", "origen": f"intake.actores[{i}].trabajo",
            })
        else:
            preguntas_abiertas.append({
                "id": f"P-{pid:02d}", "pregunta": f"El actor {a.get('id', '?')} no declara su trabajo crítico.",
                "campo_faltante": f"actores[{i}].trabajo",
            })
            pid += 1
    if no_definido:
        preguntas_abiertas.append({
            "id": f"P-{pid:02d}", "pregunta": "El resultado esperado no está definido.",
            "campo_faltante": "resultado_esperado.descripcion",
        })

    alternativas = []
    for alt in intake.get("alternativas", []):
        alternativas.append({
            "id": alt.get("id", ""), "descripcion": alt.get("descripcion", ""),
            "tradeoffs": alt.get("tradeoffs", ""), "clasificacion": "HECHO",
        })

    alcance = {
        "incluido": list((intake.get("alcance") or {}).get("incluido", [])),
        "excluido": list((intake.get("alcance") or {}).get("excluido", [])),
        "clasificacion": "HECHO",
    }

    hechos = [
        {"id": "H-01", "afirmacion": f"La clasificación de datos declarada es {intake.get('clasificacion_datos', '')}.", "origen": "intake.clasificacion_datos"},
        {"id": "H-02", "afirmacion": "El modo de la iniciativa es advisor.", "origen": "intake.initiative.mode"},
        {"id": "H-03", "afirmacion": "El proveedor y modelo declarados son none (sin LLM).", "origen": "intake.proveedor"},
    ]
    supuestos = [
        {"id": "S-01", "afirmacion": "El entorno de ejecución es local-sandbox (default aplicado).", "origen": "default"},
        {"id": "S-02", "afirmacion": "Los datos sintéticos no demuestran desempeño de producto.", "origen": "default"},
    ]

    no_determinable = []
    ndid = 1
    metrica = medible.get("metrica", "")
    if metrica:
        if not medible.get("baseline"):
            no_determinable.append({"id": f"ND-{ndid:02d}", "afirmacion": f"La métrica '{metrica}' no declara baseline.", "razon": "Sin baseline no puede establecerse verificabilidad (R-007, M-008).", "owner_decision": "Operador/Douglas"})
            ndid += 1
        if not medible.get("denominador"):
            no_determinable.append({"id": f"ND-{ndid:02d}", "afirmacion": f"La métrica '{metrica}' no declara denominador.", "razon": "Sin denominador no puede establecerse verificabilidad (R-007, M-008).", "owner_decision": "Operador/Douglas"})
            ndid += 1
    if not intake.get("alternativas"):
        no_determinable.append({"id": f"ND-{ndid:02d}", "afirmacion": "No hay alternativas declaradas.", "razon": "El motor no sintetiza alternativas sin entrada del operador.", "owner_decision": "Operador/Douglas"})
        ndid += 1
    for q in intake.get("preguntas_explicitas_no_determinable", []):
        if isinstance(q, str):
            no_determinable.append({"id": f"ND-{ndid:02d}", "afirmacion": q, "razon": "Declarado por el operador como no determinable.", "owner_decision": "Operador/Douglas"})
            ndid += 1

    requisitos = {
        "rf": [dict(r, owner=owner, estado="planned", evidencia=None) for r in REQUIREMENTS_RF],
        "rnf": [dict(r, owner=owner, estado="planned", evidencia=None) for r in REQUIREMENTS_RNF],
    }
    criterios = [dict(c, estado="planned") for c in CRITERIOS_ACEPTACION]

    riesgos = [dict(r, clasificacion="HECHO", origen="libreria") for r in LIBRARY_RISKS]
    for i, r in enumerate(intake.get("riesgos", [])):
        riesgos.append({"id": r.get("id", ""), "descripcion": r.get("descripcion", ""), "mitigacion": r.get("mitigacion", ""), "clasificacion": "HECHO", "origen": f"intake.riesgos[{i}]"})

    decisiones = [dict(d, autorizacion_ejecucion=False) for d in HUMAN_DECISIONS]

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_id": report_id,
        "initiative_id": initiative_id,
        "created_at": now,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION, "deterministic": True, "proveedor_efectivo": "none", "modelo_efectivo": "none"},
        "verdict": "PASS",
        "problema": problema,
        "resultado_esperado": resultado_esperado,
        "actores": actores,
        "trabajos": trabajos,
        "alternativas": alternativas,
        "alcance": alcance,
        "hechos": hechos,
        "supuestos": supuestos,
        "preguntas_abiertas": preguntas_abiertas,
        "no_determinable": no_determinable,
        "requisitos": requisitos,
        "criterios_aceptacion": criterios,
        "riesgos": riesgos,
        "decisiones_humanas": decisiones,
        "proximo_paso": {"accion": "solicitar_revision_independiente", "detalle": "Reporte válido; solicitar revisión independiente antes de cualquier transición."},
        "no_autorizado": list(NO_AUTORIZADO_FULL),
        "trazabilidad": {"completa": True, "requisitos_sin_criterio": [], "requisitos_sin_prueba": [], "requisitos_sin_owner": []},
    }


# ---------------------------------------------------------------------------
# Validación de reporte (sección 5.3)
# ---------------------------------------------------------------------------
def _check_clasificado(obj: dict, path: str, issues: list[dict]) -> None:
    for key in ("texto", "clasificacion", "origen"):
        if key not in obj:
            issues.append(issue("FIELD_MISSING", f"{path}.{key}", None, "campo requerido ausente", "error"))
    if obj.get("clasificacion") not in CLASIFICACIONES:
        issues.append(issue("SCHEMA_INVALID", f"{path}.clasificacion", obj.get("clasificacion"), "clasificación inválida", "error"))


def validate_report_schema(doc: Any) -> list[dict]:
    issues: list[dict] = []
    if not isinstance(doc, dict):
        return [issue("SCHEMA_INVALID", "$", doc, "se esperaba un objeto", "error")]
    _check_unknown(doc, REPORT_TOP_LEVEL_ALLOWED, "$", issues)
    for key in sorted(REPORT_TOP_LEVEL_REQUIRED):
        if key not in doc:
            issues.append(issue("FIELD_MISSING", key, None, "campo requerido ausente", "error"))

    if doc.get("schema_version") != REPORT_SCHEMA_VERSION:
        issues.append(issue("SCHEMA_INVALID", "schema_version", doc.get("schema_version"), f"debe ser {REPORT_SCHEMA_VERSION}", "error"))
    if "report_id" in doc and not (isinstance(doc.get("report_id"), str) and REPORT_ID_RE.fullmatch(doc["report_id"])):
        issues.append(issue("SCHEMA_INVALID", "report_id", doc.get("report_id"), "formato de report_id inválido", "error"))
    if doc.get("verdict") not in REPORT_VERDICTS:
        issues.append(issue("SCHEMA_INVALID", "verdict", doc.get("verdict"), "verdict inválido", "error"))

    engine = doc.get("engine")
    if isinstance(engine, dict):
        _check_unknown(engine, REPORT_ENGINE_ALLOWED, "engine", issues)
        for key in REPORT_ENGINE_ALLOWED:
            if key not in engine:
                issues.append(issue("FIELD_MISSING", f"engine.{key}", None, "campo requerido ausente", "error"))
        if engine.get("deterministic") is not True:
            issues.append(issue("SCHEMA_INVALID", "engine.deterministic", engine.get("deterministic"), "debe ser true", "error"))
        if engine.get("proveedor_efectivo") != "none":
            issues.append(issue("SCHEMA_INVALID", "engine.proveedor_efectivo", engine.get("proveedor_efectivo"), "debe ser 'none'", "error"))
        if engine.get("modelo_efectivo") != "none":
            issues.append(issue("SCHEMA_INVALID", "engine.modelo_efectivo", engine.get("modelo_efectivo"), "debe ser 'none'", "error"))
    elif "engine" in doc:
        issues.append(issue("SCHEMA_INVALID", "engine", engine, "se esperaba un objeto", "error"))

    problema = doc.get("problema")
    if isinstance(problema, dict):
        _check_unknown(problema, REPORT_CLASIFICADO_ALLOWED, "problema", issues)
        _check_clasificado(problema, "problema", issues)
    resultado = doc.get("resultado_esperado")
    if isinstance(resultado, dict):
        _check_unknown(resultado, REPORT_CLASIFICADO_ALLOWED, "resultado_esperado", issues)
        _check_clasificado(resultado, "resultado_esperado", issues)

    # actores
    actores = doc.get("actores")
    if isinstance(actores, list):
        for i, a in enumerate(actores):
            p = f"actores[{i}]"
            if not isinstance(a, dict):
                issues.append(issue("SCHEMA_INVALID", p, a, "se esperaba un objeto", "error"))
                continue
            _check_unknown(a, REPORT_ACTOR_ALLOWED, p, issues)
            if a.get("clasificacion") not in CLASIFICACIONES:
                issues.append(issue("SCHEMA_INVALID", f"{p}.clasificacion", a.get("clasificacion"), "clasificación inválida", "error"))

    # alcance
    alcance = doc.get("alcance")
    if isinstance(alcance, dict):
        _check_unknown(alcance, REPORT_ALCANCE_ALLOWED, "alcance", issues)
        if alcance.get("clasificacion") not in CLASIFICACIONES:
            issues.append(issue("SCHEMA_INVALID", "alcance.clasificacion", alcance.get("clasificacion"), "clasificación inválida", "error"))

    # requisitos
    requisitos = doc.get("requisitos")
    if isinstance(requisitos, dict):
        _check_unknown(requisitos, {"rf", "rnf"}, "requisitos", issues)
        for kind in ("rf", "rnf"):
            lst = requisitos.get(kind)
            if not isinstance(lst, list):
                issues.append(issue("SCHEMA_INVALID", f"requisitos.{kind}", lst, "se esperaba una lista", "error"))
                continue
            seen = set()
            for i, r in enumerate(lst):
                p = f"requisitos.{kind}[{i}]"
                if not isinstance(r, dict):
                    issues.append(issue("SCHEMA_INVALID", p, r, "se esperaba un objeto", "error"))
                    continue
                _check_unknown(r, REPORT_REQUISITO_ALLOWED, p, issues)
                for key in ("id", "descripcion", "criterio", "prueba_planeada", "owner", "estado"):
                    if not r.get(key):
                        issues.append(issue("FIELD_MISSING", f"{p}.{key}", None, "campo requerido ausente", "error"))
                if r.get("id") in seen:
                    issues.append(issue("DUPLICATE_ID", f"{p}.id", r.get("id"), "id duplicado", "error"))
                seen.add(r.get("id"))
                if r.get("estado") != "planned":
                    issues.append(issue("SCHEMA_INVALID", f"{p}.estado", r.get("estado"), "en I1 debe ser 'planned'", "error"))
                if r.get("evidencia") is not None:
                    issues.append(issue("SCHEMA_INVALID", f"{p}.evidencia", r.get("evidencia"), "en I1 la evidencia debe ser null", "error"))
    elif "requisitos" in doc:
        issues.append(issue("SCHEMA_INVALID", "requisitos", requisitos, "se esperaba un objeto", "error"))

    # criterios_aceptacion
    cas = doc.get("criterios_aceptacion")
    if isinstance(cas, list):
        seen = set()
        for i, c in enumerate(cas):
            p = f"criterios_aceptacion[{i}]"
            if not isinstance(c, dict):
                issues.append(issue("SCHEMA_INVALID", p, c, "se esperaba un objeto", "error"))
                continue
            _check_unknown(c, REPORT_CA_ALLOWED, p, issues)
            for key in ("id", "descripcion", "metodo", "estado"):
                if not c.get(key):
                    issues.append(issue("FIELD_MISSING", f"{p}.{key}", None, "campo requerido ausente", "error"))
            if c.get("id") in seen:
                issues.append(issue("DUPLICATE_ID", f"{p}.id", c.get("id"), "id duplicado", "error"))
            seen.add(c.get("id"))

    # decisiones_humanas
    decisiones = doc.get("decisiones_humanas")
    if isinstance(decisiones, list):
        for i, d in enumerate(decisiones):
            p = f"decisiones_humanas[{i}]"
            if not isinstance(d, dict):
                issues.append(issue("SCHEMA_INVALID", p, d, "se esperaba un objeto", "error"))
                continue
            _check_unknown(d, REPORT_DECISION_ALLOWED, p, issues)
            if d.get("autorizacion_ejecucion") is not False:
                issues.append(issue("SCHEMA_INVALID", f"{p}.autorizacion_ejecucion", d.get("autorizacion_ejecucion"), "debe ser false (sin autorización implícita)", "error"))

    # proximo_paso
    proximo = doc.get("proximo_paso")
    if isinstance(proximo, dict):
        _check_unknown(proximo, REPORT_PROXIMO_ALLOWED, "proximo_paso", issues)
        if proximo.get("accion") not in PROXIMO_PASO_ACCIONES:
            issues.append(issue("SCHEMA_INVALID", "proximo_paso.accion", proximo.get("accion"), "acción inválida", "error"))

    # no_autorizado
    no_aut = doc.get("no_autorizado")
    if isinstance(no_aut, list):
        if not NO_AUTORIZADO_REQUIRED.issubset(set(no_aut)):
            issues.append(issue("SCHEMA_INVALID", "no_autorizado", no_aut, "debe contener ejecucion, release, publicacion y produccion", "error"))
    else:
        issues.append(issue("FIELD_MISSING", "no_autorizado", no_aut, "campo requerido ausente", "error"))

    # trazabilidad
    traza = doc.get("trazabilidad")
    if isinstance(traza, dict):
        _check_unknown(traza, REPORT_TRAZABILIDAD_ALLOWED, "trazabilidad", issues)
        if not isinstance(traza.get("completa"), bool):
            issues.append(issue("SCHEMA_INVALID", "trazabilidad.completa", traza.get("completa"), "se esperaba bool", "error"))
        for key in ("requisitos_sin_criterio", "requisitos_sin_prueba", "requisitos_sin_owner"):
            if not isinstance(traza.get(key), list):
                issues.append(issue("SCHEMA_INVALID", f"trazabilidad.{key}", traza.get(key), "se esperaba una lista", "error"))

    return issues


def validate_report_traceability(doc: Any) -> list[dict]:
    issues: list[dict] = []
    if not isinstance(doc, dict):
        return issues
    requisitos = doc.get("requisitos") or {}
    all_reqs = list(requisitos.get("rf", [])) + list(requisitos.get("rnf", []))
    ca_ids = {c.get("id") for c in (doc.get("criterios_aceptacion") or []) if isinstance(c, dict)}
    gaps = {"requisitos_sin_criterio": [], "requisitos_sin_prueba": [], "requisitos_sin_owner": []}
    for r in all_reqs:
        if not isinstance(r, dict):
            continue
        rid = r.get("id", "?")
        if not r.get("criterio"):
            gaps["requisitos_sin_criterio"].append(rid)
        elif r.get("criterio") not in ca_ids:
            issues.append(issue("SCHEMA_INVALID", f"requisitos.{rid}.criterio", r.get("criterio"), "CA referenciado no existe en criterios_aceptacion", "error"))
        if not r.get("prueba_planeada"):
            gaps["requisitos_sin_prueba"].append(rid)
        if not r.get("owner"):
            gaps["requisitos_sin_owner"].append(rid)
    if any(gaps.values()):
        issues.append(issue("TRACEABILITY_GAP", "trazabilidad", None, "requisitos con enlace faltante (criterio/prueba/owner)", "error"))
    return issues


def validate_report(doc: Any) -> list[dict]:
    """Flujo de validate-report (sección 5.3): secret scan → schema → trazabilidad."""
    secret_issues = scan_document(doc)
    if any(i["severity"] == "blocked" for i in secret_issues):
        return secret_issues
    warnings = [i for i in secret_issues if i["severity"] == "warning"]
    return warnings + validate_report_schema(doc) + validate_report_traceability(doc)


# ---------------------------------------------------------------------------
# Exportación del expediente (secciones 5.4 y 9)
# ---------------------------------------------------------------------------
def derive_traceability(report: dict) -> dict:
    requisitos = report.get("requisitos", {})
    reqs = []
    for kind in ("rf", "rnf"):
        for r in requisitos.get(kind, []):
            reqs.append({
                "id": r.get("id"),
                "criterio": r.get("criterio"),
                "prueba_planeada": r.get("prueba_planeada"),
                "owner": r.get("owner"),
                "estado": r.get("estado"),
            })
    return {
        "schema_version": "advisor-traceability/v1",
        "initiative_id": report.get("initiative_id"),
        "report_id": report.get("report_id"),
        "requirements": reqs,
    }


def build_case_file_md(casefile_id: str, report: dict, hashes: dict[str, str]) -> str:
    initiative_id = report.get("initiative_id", "")
    report_id = report.get("report_id", "")
    created_at = report.get("created_at", "")
    verdict = report.get("verdict", "")
    return (
        f"# Expediente del Advisor — {casefile_id}\n\n"
        f"Iniciativa: {initiative_id}\n"
        f"Reporte: {report_id}\n"
        f"Creado: {created_at}\n"
        f"Veredicto: {verdict}\n"
        f"proveedor_efectivo: none\n"
        f"modelo_efectivo: none\n\n"
        f"## Summary\n"
        f"Motor determinista sin LLM. Valida un intake sintético y produce un reporte conforme a esquema.\n\n"
        f"## Evidence\n"
        f"- intake.json — sha256:{hashes['intake.json']}\n"
        f"- report.json — sha256:{hashes['report.json']}\n"
        f"- traceability.json — sha256:{hashes['traceability.json']}\n"
        f"- MANIFEST.json — hashes verificables en el manifiesto\n\n"
        f"## Merge Danger\n"
        f"Este expediente no autoriza release, publicación ni producción.\n"
        f"No fusionar sin revisión independiente y autorización humana explícita.\n\n"
        f"Datos sintéticos: esta fixture no demuestra desempeño de producto.\n"
    )


def verify_manifest(target: Path) -> tuple[bool, str | None]:
    manifest_path = target / "MANIFEST.json"
    if not manifest_path.is_file():
        return True, None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"MANIFEST.json ilegible: {exc}"
    for f in manifest.get("files", []):
        path = f.get("path")
        if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
            return False, f"path inseguro en manifiesto: {path}"
        fp = target / path
        if not fp.is_file():
            return False, f"archivo ausente: {path}"
        data = fp.read_bytes()
        if sha256_bytes(data) != f.get("sha256"):
            return False, f"hash mismatch en {path}"
        if len(data) != f.get("size"):
            return False, f"tamaño mismatch en {path}"
    return True, None


def export_casefile(intake_doc: dict, report_doc: dict, out_dir: str) -> dict:
    """Valida intake y reporte, escribe el expediente y re-verifica hashes."""
    # Precondiciones: intake y reporte PASS
    intake_issues = validate_intake(intake_doc)
    intake_env = envelope("export-casefile", intake_issues)
    if intake_env["exit_code"] != 0:
        return intake_env
    report_issues = validate_report(report_doc)
    report_env = envelope("export-casefile", report_issues)
    if report_env["exit_code"] != 0:
        return report_env

    # coherencia intake <-> reporte
    if report_doc.get("initiative_id") != intake_doc["initiative"]["id"]:
        return envelope("export-casefile", [issue("SCHEMA_INVALID", "report.initiative_id", report_doc.get("initiative_id"), "initiative_id del reporte no coincide con el intake", "error")])

    casefile_id = make_casefile_id(intake_doc["initiative"]["id"])
    target = Path(out_dir) / casefile_id

    # Detección de tampering en un expediente preexistente (al leer)
    if target.is_dir():
        ok, err = verify_manifest(target)
        if not ok:
            return envelope("export-casefile", [issue("HASH_MISMATCH", "MANIFEST.json", "[REDACTED]", err or "hash inconsistente", "blocked")])

    target.mkdir(parents=True, exist_ok=True)

    traceability = derive_traceability(report_doc)
    payloads = {
        "intake.json": canonical_json(intake_doc),
        "report.json": canonical_json(report_doc),
        "traceability.json": canonical_json(traceability),
    }
    hashes = {name: sha256_bytes(content.encode("utf-8")) for name, content in payloads.items()}

    case_md = build_case_file_md(casefile_id, report_doc, hashes)
    payloads["CASE-FILE.md"] = case_md
    hashes["CASE-FILE.md"] = sha256_bytes(case_md.encode("utf-8"))

    for name, content in payloads.items():
        (target / name).write_text(content, encoding="utf-8")

    files = []
    for name in ("intake.json", "report.json", "traceability.json", "CASE-FILE.md"):
        data = payloads[name].encode("utf-8")
        files.append({"path": name, "sha256": sha256_bytes(data), "size": len(data)})

    manifest_body = {
        "schema_version": "advisor-casefile/v1",
        "casefile_id": casefile_id,
        "created_at": report_doc.get("created_at", ""),
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION, "deterministic": True},
        "files": files,
    }
    manifest_sha = sha256_canonical(manifest_body)
    manifest = dict(manifest_body, manifest_sha256=manifest_sha)
    (target / "MANIFEST.json").write_text(canonical_json(manifest), encoding="utf-8")

    # Re-verificar hashes después de escribir (self-check)
    ok, err = verify_manifest(target)
    if not ok:
        return envelope("export-casefile", [issue("HASH_MISMATCH", "MANIFEST.json", "[REDACTED]", err or "hash inconsistente tras escritura", "blocked")])

    return envelope("export-casefile", [], [{"casefile_id": casefile_id, "path": str(target)}])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--format", choices=["json", "text"], default="json")
    p.add_argument("--now", help="reloj inyectable ISO-8601 (default: reloj del sistema)")
    p.add_argument("--schema", default="kit/schemas", help="directorio de esquemas (default: kit/schemas)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bottega_advisor.py", description="Bottega Advisor (Incremento 1) — determinista, sin LLM, sólo lectura.")
    parser.add_argument("--version", action="version", version=ENGINE_VERSION)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p = sub.add_parser("validate-intake", help="valida un intake estructurado")
    p.add_argument("--input", required=True, help="ruta al intake (.yaml/.json)")
    _add_common(p)

    p = sub.add_parser("prepare-report", help="produce un reporte desde un intake válido")
    p.add_argument("--intake", required=True, help="ruta al intake")
    p.add_argument("--out", help="ruta de salida del reporte (opcional; si se omite, imprime el reporte en stdout)")
    _add_common(p)

    p = sub.add_parser("validate-report", help="valida un reporte")
    p.add_argument("--input", required=True, help="ruta al reporte (.yaml/.json)")
    _add_common(p)

    p = sub.add_parser("export-casefile", help="exporta el expediente hasheado")
    p.add_argument("--intake", required=True, help="ruta al intake")
    p.add_argument("--report", required=True, help="ruta al reporte")
    p.add_argument("--out", required=True, help="directorio de salida")
    _add_common(p)

    return parser


def _render(env: dict, fmt: str) -> str:
    if fmt == "text":
        lines = [f"verdict: {env['verdict']}", f"exit_code: {env['exit_code']}", f"counts: {env['counts']}"]
        for i in env["issues"]:
            lines.append(f"[{i['severity']}] {i['code']} {i['path']}: {i['message']}")
        for o in env["observations"]:
            lines.append(f"observation: {o}")
        return "\n".join(lines)
    return json.dumps(env, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def cmd_validate_intake(args: argparse.Namespace) -> dict:
    doc, err = load_document(args.input)
    if err:
        return io_error_envelope("validate-intake", err)
    return envelope("validate-intake", validate_intake(doc))


def cmd_prepare_report(args: argparse.Namespace) -> dict:
    doc, err = load_document(args.intake)
    if err:
        return io_error_envelope("prepare-report", err)
    env = envelope("prepare-report", validate_intake(doc))
    if env["exit_code"] != 0:
        if env["verdict"] == "NEEDS_WORK":
            env["observations"].append({"hint": "ejecute validate-intake y corrija antes de generar el reporte"})
        return env
    now = args.now if args.now else system_now()
    report = build_report(doc, now, make_report_id(doc["initiative"]["id"]))
    if args.out:
        Path(args.out).write_text(canonical_json(report), encoding="utf-8")
        env["observations"] = [{"report_id": report["report_id"], "path": args.out}]
        return env
    # Sin --out: imprime el reporte (objeto JSON único) en stdout y no imprime envelope.
    sys.stdout.write(canonical_json(report))
    return None  # type: ignore[return-value]


def cmd_validate_report(args: argparse.Namespace) -> dict:
    doc, err = load_document(args.input)
    if err:
        return io_error_envelope("validate-report", err)
    return envelope("validate-report", validate_report(doc))


def cmd_export_casefile(args: argparse.Namespace) -> dict:
    intake_doc, err = load_document(args.intake)
    if err:
        return io_error_envelope("export-casefile", err)
    report_doc, err = load_document(args.report)
    if err:
        return io_error_envelope("export-casefile", err)
    return export_casefile(intake_doc, report_doc, args.out)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers: dict[str, Callable[[argparse.Namespace], dict]] = {
        "validate-intake": cmd_validate_intake,
        "prepare-report": cmd_prepare_report,
        "validate-report": cmd_validate_report,
        "export-casefile": cmd_export_casefile,
    }
    env = handlers[args.subcommand](args)
    if env is None:  # prepare-report sin --out ya imprimió el reporte
        return 0
    print(_render(env, args.format))
    return int(env["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
