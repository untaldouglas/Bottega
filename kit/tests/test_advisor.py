"""Matriz TDD del Advisor (Incremento 1) — TA-001..TA-022.

Cada test declara qué detecta y qué no (contrato TDD negativo, TEST-SEAMS.yaml).
Comando: python3 -m unittest discover -s kit/tests -p 'test_advisor*.py' -v
Fixtures sintéticas: kit/tests/fixtures/advisor/.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # kit/
REPO = ROOT.parent
SCRIPT = ROOT / "scripts" / "bottega_advisor.py"
FIX = ROOT / "tests" / "fixtures" / "advisor"
SCHEMAS = ROOT / "schemas"

sys.path.insert(0, str(ROOT / "scripts"))
import bottega_advisor as adv  # noqa: E402

NOW = "2026-10-26T00:00:00Z"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        cwd=REPO, capture_output=True, text=True,
    )


def load_env(r):
    return json.loads(r.stdout)


class AdvisorTests(unittest.TestCase):
    """TA-001..TA-022 — positivos y negativos mapeados a RF/RNF/CA."""

    def test_ta001_validate_intake_acepta_valido(self):
        """Detecta: intake válido ⇒ PASS. No detecta: semántica de negocio."""
        r = run_cli("validate-intake", "--input", FIX / "intake-valid.yaml")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(load_env(r)["verdict"], "PASS")

    def test_ta002_owner_ausente_needs_work(self):
        """Detecta: owner ausente ⇒ NEEDS_WORK (FIELD_MISSING). No detecta: bloqueo por sí mismo."""
        r = run_cli("validate-intake", "--input", FIX / "intake-missing-owner.yaml")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        env = load_env(r)
        self.assertEqual(env["verdict"], "NEEDS_WORK")
        self.assertTrue(any(i["code"] == "FIELD_MISSING" and "owner" in i["path"] for i in env["issues"]))

    def test_ta003_necesidad_ausente_needs_work(self):
        """Detecta: necesidad ausente ⇒ NEEDS_WORK. No detecta: clasificación de datos."""
        r = run_cli("validate-intake", "--input", FIX / "intake-missing-necesidad.yaml")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertTrue(any(i["code"] == "FIELD_MISSING" for i in load_env(r)["issues"]))

    def test_ta004_clasificacion_real_blocked(self):
        """Detecta: clasificación REAL ⇒ BLOCKED sin fuga. No detecta: tipos de campo."""
        r = run_cli("validate-intake", "--input", FIX / "intake-real-data.yaml")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        env = load_env(r)
        self.assertEqual(env["verdict"], "BLOCKED")
        self.assertTrue(any(i["code"] == "OUT_OF_SCOPE" for i in env["issues"]))

    def test_ta005_secreto_blocked_y_redactado(self):
        """Detecta: secreto ⇒ BLOCKED y redactado. No detecta: dónde está el secreto."""
        r = run_cli("validate-intake", "--input", FIX / "intake-secret.yaml")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        env = load_env(r)
        self.assertTrue(any(i["code"] == "SECRET_DETECTED" for i in env["issues"]))
        self.assertNotIn("valor-sintetico-no-real", r.stdout)
        for i in env["issues"]:
            self.assertNotIn("valor-sintetico-no-real", json.dumps(i))
        self.assertTrue(any(i.get("safe_value") == "[REDACTED]" for i in env["issues"]))

    def test_ta006_producto02_produccion_blocked(self):
        """Detecta: Producto 02/producción ⇒ BLOCKED. No detecta: mutación real."""
        r = run_cli("validate-intake", "--input", FIX / "intake-out-of-scope.yaml")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertTrue(any(i["code"] == "OUT_OF_SCOPE" for i in load_env(r)["issues"]))

    def test_ta007_proveedor_no_none_blocked(self):
        """Detecta: proveedor/modelo ≠ none ⇒ BLOCKED (sin LLM). No detecta: llamadas de red."""
        r = run_cli("validate-intake", "--input", FIX / "intake-provider.yaml")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertTrue(any(i["code"] == "OUT_OF_SCOPE" for i in load_env(r)["issues"]))

    def test_ta008_prepare_report_determinista(self):
        """Detecta: misma entrada + mismo --now ⇒ bytes idénticos. No detecta: contenido semántico."""
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = Path(d) / "r1.json", Path(d) / "r2.json"
            for p in (p1, p2):
                r = run_cli("prepare-report", "--intake", FIX / "intake-valid.yaml", "--out", p, "--now", NOW)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(p1.read_bytes(), p2.read_bytes())

    def test_ta009_separa_hechos_supuestos_preguntas_nd(self):
        """Detecta: separación mecánica HECHO/SUPUESTO/PREGUNTA/ND. No detecta: mezcla de orígenes."""
        intake, err = adv.load_document(str(FIX / "intake-partial.yaml"))
        self.assertIsNone(err)
        report = adv.build_report(intake, NOW, adv.make_report_id(intake["initiative"]["id"]))
        self.assertEqual(report["problema"]["clasificacion"], "HECHO")
        self.assertEqual(report["resultado_esperado"]["clasificacion"], "PREGUNTA_ABIERTA")
        self.assertTrue(any("ACTOR-SYN-02" in p["pregunta"] for p in report["preguntas_abiertas"]))
        self.assertTrue(any("No hay alternativas" in n["afirmacion"] for n in report["no_determinable"]))
        self.assertTrue(any("Umbral de adopción" in n["afirmacion"] for n in report["no_determinable"]))
        self.assertTrue(report["supuestos"])
        self.assertTrue(all(h["origen"] != "default" for h in report["hechos"]))
        self.assertTrue(all(s["origen"] == "default" for s in report["supuestos"]))

    def test_ta010_metrica_sin_baseline_nd(self):
        """Detecta: métrica sin baseline/denominador ⇒ ND. No detecta: inventar valores."""
        intake, _ = adv.load_document(str(FIX / "intake-no-baseline.yaml"))
        report = adv.build_report(intake, NOW, adv.make_report_id(intake["initiative"]["id"]))
        afirmaciones = [n["afirmacion"] for n in report["no_determinable"]]
        self.assertTrue(any("baseline" in a for a in afirmaciones))
        self.assertTrue(any("denominador" in a for a in afirmaciones))

    def test_ta011_alternativas_vacias_nd(self):
        """Detecta: alternativas vacías ⇒ ND, no sintetiza. No detecta: síntesis de requisitos."""
        intake, _ = adv.load_document(str(FIX / "intake-sin-alternativas.yaml"))
        report = adv.build_report(intake, NOW, adv.make_report_id(intake["initiative"]["id"]))
        self.assertEqual(report["alternativas"], [])
        self.assertTrue(any("No hay alternativas" in n["afirmacion"] for n in report["no_determinable"]))

    def test_ta012_validate_report_acepta_valido(self):
        """Detecta: reporte válido ⇒ PASS. No detecta: trazabilidad profunda."""
        r = run_cli("validate-report", "--input", FIX / "report-valid.yaml")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(load_env(r)["verdict"], "PASS")

    def test_ta013_report_tampered_needs_work(self):
        """Detecta: campo faltante ⇒ SCHEMA_INVALID/NEEDS_WORK. No detecta: hash de evidencia."""
        r = run_cli("validate-report", "--input", FIX / "report-tampered.yaml")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertTrue(any(i["code"] == "SCHEMA_INVALID" for i in load_env(r)["issues"]))

    def test_ta014_trazabilidad_gap(self):
        """Detecta: enlace faltante ⇒ TRACEABILITY_GAP. No detecta: requisitos nuevos."""
        r = run_cli("validate-report", "--input", FIX / "report-trace-gap.yaml")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertTrue(any(i["code"] == "TRACEABILITY_GAP" for i in load_env(r)["issues"]))

    def test_ta015_export_casefile_manifest_hash(self):
        """Detecta: export + manifest con sha256 correctos. No detecta: tampering posterior."""
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            r = run_cli("export-casefile", "--intake", FIX / "intake-valid.yaml",
                        "--report", FIX / "report-valid.yaml", "--out", out, "--now", NOW)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            cid = load_env(r)["observations"][0]["casefile_id"]
            cdir = out / cid
            self.assertTrue((cdir / "MANIFEST.json").is_file())
            manifest = json.loads((cdir / "MANIFEST.json").read_text())
            for f in manifest["files"]:
                data = (cdir / f["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), f["sha256"], f["path"])
                self.assertEqual(len(data), f["size"], f["path"])
            body = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
            self.assertEqual(manifest["manifest_sha256"], adv.sha256_canonical(body))

    def test_ta016_tamper_casefile_hash_mismatch(self):
        """Detecta: tampering en expediente ⇒ HASH_MISMATCH/BLOCKED. No detecta: actor del tampering."""
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            args = ["export-casefile", "--intake", FIX / "intake-valid.yaml",
                    "--report", FIX / "report-valid.yaml", "--out", out, "--now", NOW]
            r1 = run_cli(*args)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            cid = load_env(r1)["observations"][0]["casefile_id"]
            cdir = out / cid
            (cdir / "report.json").write_text((cdir / "report.json").read_text() + "\n")
            r2 = run_cli(*args)
            self.assertEqual(r2.returncode, 3, r2.stdout + r2.stderr)
            self.assertIn("HASH_MISMATCH", r2.stdout)

    def test_ta017_export_sin_secretos(self):
        """Detecta: expediente exportado sin tokens/secretos. No detecta: secretos fuera del expediente."""
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            r = run_cli("export-casefile", "--intake", FIX / "intake-valid.yaml",
                        "--report", FIX / "report-valid.yaml", "--out", out, "--now", NOW)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            cid = load_env(r)["observations"][0]["casefile_id"]
            cdir = out / cid
            blob = "\n".join((cdir / p).read_text() for p in cdir.iterdir() if p.is_file())
            for token in ("ghp_", "AKIA", "xoxb", "xoxp", "sk-", "eyJ", "PRIVATE KEY", "BEGIN RSA"):
                self.assertNotIn(token, blob)

    def test_ta018_catalogo_errores_exit_codes(self):
        """Detecta: mapeo catálogo → exit code. No detecta: mensajes exactos por idioma."""
        cases = [
            ("intake-secret.yaml", 3, "SECRET_DETECTED"),
            ("intake-real-data.yaml", 3, "OUT_OF_SCOPE"),
            ("intake-out-of-scope.yaml", 3, "OUT_OF_SCOPE"),
            ("intake-provider.yaml", 3, "OUT_OF_SCOPE"),
            ("intake-missing-owner.yaml", 1, "FIELD_MISSING"),
        ]
        for fixture, exit_code, code in cases:
            with self.subTest(fixture=fixture):
                r = run_cli("validate-intake", "--input", FIX / fixture)
                self.assertEqual(r.returncode, exit_code, r.stdout + r.stderr)
                self.assertIn(code, r.stdout)
        r = run_cli("validate-intake", "--input", FIX / "no-existe.yaml")
        self.assertEqual(r.returncode, 2)
        self.assertIn("IO_ERROR", r.stdout)

    def test_ta019_no_autorizacion_implicita(self):
        """Detecta: decisiones humanas presentes y sin autorización implícita. No detecta: autorización externa."""
        report, _ = adv.load_document(str(FIX / "report-valid.yaml"))
        self.assertTrue(report["decisiones_humanas"])
        self.assertTrue(all(d["autorizacion_ejecucion"] is False for d in report["decisiones_humanas"]))
        self.assertTrue({"ejecucion", "release", "publicacion", "produccion"}.issubset(set(report["no_autorizado"])))

    def test_ta020_motor_sin_llm(self):
        """Detecta: proveedor/modelo efectivo none (sin LLM/red). No detecta: tráfico de red."""
        report, _ = adv.load_document(str(FIX / "report-valid.yaml"))
        self.assertEqual(report["engine"]["proveedor_efectivo"], "none")
        self.assertEqual(report["engine"]["modelo_efectivo"], "none")
        self.assertTrue(report["engine"]["deterministic"])

    def test_ta021_schemas_coherentes(self):
        """Detecta: schema.json válidos y coherentes con el validador. No detecta: completitud de cada campo."""
        for name, required_const in (
            ("advisor-intake.schema.json", adv.INTAKE_TOP_LEVEL_REQUIRED),
            ("advisor-report.schema.json", adv.REPORT_TOP_LEVEL_REQUIRED),
        ):
            with self.subTest(name=name):
                schema = json.loads((SCHEMAS / name).read_text())
                self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
                self.assertFalse(schema.get("additionalProperties", True))
                self.assertEqual(set(schema.get("required", [])), required_const)
        intake_schema = json.loads((SCHEMAS / "advisor-intake.schema.json").read_text())
        self.assertEqual(set(intake_schema["properties"]["clasificacion_datos"]["enum"]), adv.SYNTHETIC_CLASSES)
        self.assertEqual(set(intake_schema["properties"]["actores"]["items"]["properties"]["rol"]["enum"]), adv.ACTOR_ROLES)
        report_schema = json.loads((SCHEMAS / "advisor-report.schema.json").read_text())
        self.assertEqual(set(report_schema["properties"]["verdict"]["enum"]), adv.REPORT_VERDICTS)

    def test_ta022_subcomando_desconocido(self):
        """Detecta: subcomando desconocido ⇒ exit 2. No detecta: flags desconocidos."""
        r = run_cli("bogus")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
