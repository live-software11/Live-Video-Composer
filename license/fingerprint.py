"""
Hardware fingerprint — Live Video Composer.
Windows only: WMI (Win32_BaseBoard, Win32_Processor, Win32_DiskDrive[0]) → SHA-256.
Allineato alla formula documentata in GUIDA_INTEGRAZIONE_LICENZA_APP.md §3.
"""

import hashlib
import logging

logger = logging.getLogger("LiveVideoComposer.license")

_UNKNOWN_MB = "UNKNOWN_MB"
_UNKNOWN_CPU = "UNKNOWN_CPU"
_NO_DISK = "NO_DISK"


def _wmi_query(wql: str, field: str) -> str:
    """Esegue una singola query WMI e restituisce il valore del campo richiesto (stripped)."""
    try:
        import wmi  # type: ignore
        c = wmi.WMI()
        for obj in c.query(wql):
            val = getattr(obj, field, "") or ""
            val = str(val).strip()
            if val:
                return val
    except Exception as exc:
        logger.debug("WMI query failed (%s, %s): %s", wql, field, exc)
    return ""


def compute_fingerprint() -> tuple[str, str]:
    """
    Calcola (fingerprint_hex, hardware_details) per il PC corrente.
    fingerprint_hex: SHA-256 64-char hex di "MB|CPU|DISK".
    hardware_details: stringa leggibile "MB:...|CPU:...|DISK:..." (per dashboard admin).
    Lancia RuntimeError su piattaforme non-Windows.
    """
    import sys
    if sys.platform != "win32":
        raise RuntimeError("License hardware fingerprint is Windows-only.")

    mb = _wmi_query("SELECT SerialNumber FROM Win32_BaseBoard", "SerialNumber")
    cpu = _wmi_query("SELECT ProcessorId FROM Win32_Processor", "ProcessorId")
    disk = _wmi_query(
        "SELECT SerialNumber FROM Win32_DiskDrive WHERE Index=0", "SerialNumber"
    )

    if not mb or not cpu or not disk:
        missing = [k for k, v in [("MB", mb), ("CPU", cpu), ("DISK", disk)] if not v]
        raise RuntimeError(
            f"Hardware fingerprint incomplete — missing: {', '.join(missing)}. "
            "WMI query failed; license activation requires real hardware identifiers."
        )

    raw = f"{mb}|{cpu}|{disk}"
    fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    details = f"MB:{mb}|CPU:{cpu}|DISK:{disk}"

    logger.debug("Fingerprint computed (partial): %s...", fingerprint[:16])
    return fingerprint, details
