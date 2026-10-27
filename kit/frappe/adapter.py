"""Adaptador Frappe sin dependencia: sólo metadatos y comandos permitidos."""
from .contract import FrappeProfile, RuntimeGate

class FrappeAdapter:
    def __init__(self, profile: FrappeProfile | None = None, gate: RuntimeGate = RuntimeGate.BLOCKED):
        self.profile = profile or FrappeProfile()
        self.gate = gate
        self.profile.validate()

    def metadata(self) -> dict:
        return {"version": self.profile.version, "commit": self.profile.commit,
                "bench_version": self.profile.bench_version, "bench_commit": self.profile.bench_commit,
                "environment": self.profile.environment, "provider": self.profile.provider,
                "gate": self.gate.value}

    def command(self, operation: str) -> list[str]:
        if self.gate is not RuntimeGate.PASS:
            raise RuntimeError("Frappe runtime bloqueado por gate")
        allowed = {"install": ["bench", "new-site"], "migrate": ["bench", "migrate"],
                   "backup": ["bench", "backup"], "restore": ["bench", "restore"],
                   "uninstall": ["bench", "drop-site"]}
        if operation not in allowed:
            raise ValueError("operación Frappe no permitida")
        return allowed[operation]
