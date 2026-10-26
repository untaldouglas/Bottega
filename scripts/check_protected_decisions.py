#!/usr/bin/env python3
"""Aserción determinista de decisiones protegidas tras Gate 0.

Garantiza que el Product Brief de Bottega 2.0, tras la aprobación humana del
Gate 0, NO eleve ninguna decisión protegida: publicación, merge, release,
producción, inicio del Advisor/Incremento 1 ni instalación/PoC de Frappe.

Falla (exit 1) si:
- el Gate 0 deja de estar APPROVED;
- el estado vigente de publicación no es NOT_AUTHORIZED;
- el estado vigente de release no es NOT_READY;
- la lista ``not_authorized`` del brief omite alguna decisión protegida;
- el catálogo de estados no declara los valores permitidos por dimensión;
- el decision record contradice el brief (decisión distinta de APPROVED o
  ``not_authorized`` sin las decisiones protegidas).

Solo usa la biblioteca estándar (sin PyYAML), para que corra en CI sin
instalar dependencias. El parser cubre el subconjunto YAML usado por estos
dos artefactos (mapas anidados, listas escalares y listas de mapas).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "docs/product/BOTTEGA-2-PRODUCT-BRIEF.yaml"
DECISION_RECORD = ROOT / "docs/product/BOTTEGA-2-DECISION-RECORD.yaml"

# Decisiones protegidas que Gate 0 debe registrar como NO autorizadas.
PROTECTED_NOT_AUTHORIZED = {
    "publicacion",
    "merge",
    "release",
    "produccion",
    "advisor_o_incremento_1",
    "frappe_poc",
}

# Catálogo de valores permitidos por dimensión (BOUNDARIES §5.2).
CATALOG_REQUIRED = {
    "product": {"NOT_ACCEPTED", "PRODUCT_PASS"},
    "release": {"NOT_READY", "RELEASE_READY_CONDITIONAL"},
    "publication": {"NOT_AUTHORIZED", "PUBLICATION_AUTHORIZED"},
}


# --------------------------------------------------------------------------
# Parser YAML de subconjunto (solo stdlib).
# --------------------------------------------------------------------------

def _strip_comment(line: str) -> str:
    """Elimina un comentario ``#`` fuera de comillas."""
    quote = None
    out = []
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def _scalar(raw: str):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    if raw in ("true", "True"):
        return True
    if raw in ("false", "False"):
        return False
    if raw in ("null", "Null", "~", ""):
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _tokenize(text: str):
    lines = []
    for line in text.splitlines():
        stripped = _strip_comment(line).rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    return lines


def _key_value(content: str):
    m = re.match(r"^([^:]+):(.*)$", content)
    if not m:
        return None
    return m.group(1).strip(), m.group(2).strip()


def _parse_map(lines, i, indent):
    result = {}
    while i < len(lines):
        ind, content = lines[i]
        if ind < indent:
            break
        if ind > indent:
            break
        if content.startswith("- "):
            break
        kv = _key_value(content)
        if kv is None:
            i += 1
            continue
        key, rest = kv
        if rest:
            result[key] = _scalar(rest)
            i += 1
        else:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                child_ind = lines[i][0]
                if lines[i][1].startswith("- "):
                    result[key], i = _parse_list(lines, i, child_ind)
                else:
                    result[key], i = _parse_map(lines, i, child_ind)
            else:
                result[key] = None
    return result, i


def _parse_list(lines, i, indent):
    result = []
    while i < len(lines):
        ind, content = lines[i]
        if ind < indent:
            break
        if ind != indent or not content.startswith("- "):
            break
        rest = content[2:].strip()
        kv = _key_value(rest)
        if kv is None:
            result.append(_scalar(rest))
            i += 1
            continue
        key, val = kv
        item = {}
        if val:
            item[key] = _scalar(val)
            i += 1
        else:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                child_ind = lines[i][0]
                if lines[i][1].startswith("- "):
                    item[key], i = _parse_list(lines, i, child_ind)
                else:
                    item[key], i = _parse_map(lines, i, child_ind)
            else:
                item[key] = None
        # claves adicionales con mayor indentación pertenecen al mismo item
        while i < len(lines) and lines[i][0] > indent:
            ind2, content2 = lines[i]
            if ind2 <= indent or content2.startswith("- "):
                break
            kv2 = _key_value(content2)
            if kv2 is None:
                break
            k2, r2 = kv2
            if r2:
                item[k2] = _scalar(r2)
                i += 1
            else:
                i += 1
                if i < len(lines) and lines[i][0] > ind2:
                    child_ind = lines[i][0]
                    if lines[i][1].startswith("- "):
                        item[k2], i = _parse_list(lines, i, child_ind)
                    else:
                        item[k2], i = _parse_map(lines, i, child_ind)
                else:
                    item[k2] = None
        result.append(item)
    return result, i


def parse_yaml(path: Path):
    lines = _tokenize(path.read_text(encoding="utf-8"))
    if not lines:
        return None
    value, _ = _parse_map(lines, 0, 0)
    return value


# --------------------------------------------------------------------------
# Aserciones.
# --------------------------------------------------------------------------

def _list_values(node):
    if isinstance(node, list):
        return {_scalar(str(x)) if isinstance(x, str) else str(x) for x in node}
    return set()


def main() -> int:
    findings = []

    if not BRIEF.is_file():
        findings.append("missing Product Brief")
    if not DECISION_RECORD.is_file():
        findings.append("missing decision record")

    brief = parse_yaml(BRIEF) if BRIEF.is_file() else None
    record = parse_yaml(DECISION_RECORD) if DECISION_RECORD.is_file() else None

    # 1. Gate 0 sigue APPROVED en el brief y en el decision record.
    if brief is not None:
        if brief.get("status") != "APPROVED_GATE_0":
            findings.append(
                f"Product Brief status != APPROVED_GATE_0 (found {brief.get('status')!r})"
            )
    if record is not None:
        if record.get("decision") != "APPROVED":
            findings.append(
                f"decision record decision != APPROVED (found {record.get('decision')!r})"
            )

    # 2. El estado vigente no eleva publicación ni release.
    current = (brief or {}).get("current_decision_state") or {}
    if current.get("publication") != "NOT_AUTHORIZED":
        findings.append(
            "current_decision_state.publication != NOT_AUTHORIZED "
            f"(found {current.get('publication')!r})"
        )
    if current.get("release") != "NOT_READY":
        findings.append(
            "current_decision_state.release != NOT_READY "
            f"(found {current.get('release')!r})"
        )
    if current.get("product") != "PRODUCT_PASS":
        findings.append(
            "current_decision_state.product != PRODUCT_PASS "
            f"(found {current.get('product')!r})"
        )

    # 3. El catálogo declara las dimensiones y los valores permitidos.
    catalog = (brief or {}).get("decision_state_catalog") or {}
    for dimension, allowed in CATALOG_REQUIRED.items():
        node = catalog.get(dimension)
        if isinstance(node, list):
            present = {_scalar(str(x)) for x in node}
        elif isinstance(node, str):
            present = {node}
        else:
            present = set()
        missing = allowed - present
        if missing:
            findings.append(
                f"decision_state_catalog.{dimension} missing values {sorted(missing)}"
            )

    # 4. La lista not_authorized del brief cubre todas las decisiones protegidas.
    not_auth = _list_values((brief or {}).get("not_authorized"))
    missing_protected = PROTECTED_NOT_AUTHORIZED - not_auth
    if missing_protected:
        findings.append(
            "Product Brief not_authorized missing: " + ", ".join(sorted(missing_protected))
        )

    # 5. El decision record también registra las decisiones protegidas.
    record_not_auth = _list_values((record or {}).get("not_authorized"))
    if record is not None:
        joined = " ".join(str(x) for x in record_not_auth)
        lowered = joined.lower()
        for token in ("release", "publicación", "producción"):
            if token not in lowered:
                findings.append(f"decision record not_authorized missing token: {token}")

    if findings:
        print("protected-decisions-check: FAIL (" + str(len(findings)) + " findings)")
        for finding in findings:
            print("  - " + finding)
        return 1

    print(
        "protected-decisions-check: OK "
        "(Gate 0 APPROVED; publication NOT_AUTHORIZED; release NOT_READY; "
        "6 protected decisions not authorized)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
