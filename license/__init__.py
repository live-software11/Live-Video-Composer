"""
Modulo licenza Live Video Composer.
Attivo solo nella build installer (flag LICENSE_ENABLED).
"""

from .fingerprint import compute_fingerprint
from .manager import (
    LicenseStatus,
    get_status,
    activate,
    verify_online,
    deactivate,
    run_deactivate_uninstall,
    normalize_key,
)
from .gate import show_license_gate
from .storage import load_license, save_license, delete_license

__all__ = [
    "LicenseStatus",
    "get_status",
    "activate",
    "verify_online",
    "deactivate",
    "run_deactivate_uninstall",
    "normalize_key",
    "show_license_gate",
    "compute_fingerprint",
    "load_license",
    "save_license",
    "delete_license",
]
