"""Contrato neutral para un adaptador Frappe versionado y fail-closed."""
from dataclasses import dataclass
from enum import Enum

class RuntimeGate(str, Enum):
    BLOCKED = "BLOCKED"
    PASS = "PASS"

@dataclass(frozen=True)
class FrappeProfile:
    version: str = "16.53.0"
    commit: str = "e8d41dd0061a32ee781caefe5d0b0d2bb7c15362"
    bench_version: str = "5.31.1"
    bench_commit: str = "660bc2898500dc33828056c1228e5a1d538573b1"
    environment: str = "local-sandbox"
    recorded_at: str = "2026-10-27T16:30:00Z"
    provider: str = "synthetic-local"

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.version == "latest" or self.bench_version == "latest":
            raise ValueError("latest no está permitido")
        if len(self.commit) != 40 or len(self.bench_commit) != 40:
            raise ValueError("commit pin inválido")
        if self.environment != "local-sandbox":
            raise ValueError("sólo sandbox local")
        if self.provider != "synthetic-local":
            raise ValueError("proveedor real no permitido")
