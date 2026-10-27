"""Perfil Frappe aislado; el core importa sólo el contrato neutral."""
from .contract import FrappeProfile, RuntimeGate
from .adapter import FrappeAdapter

__all__ = ["FrappeAdapter", "FrappeProfile", "RuntimeGate"]
