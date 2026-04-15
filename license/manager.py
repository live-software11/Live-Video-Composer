"""
License manager — Live Video Composer.
Gestisce activate, verify, deactivate verso l'API Live Works,
lo storage cifrato locale e il grace period offline.
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any

import requests  # type: ignore

from .fingerprint import compute_fingerprint
from .storage import (
    load_license, save_license, delete_license,
    load_pending, save_pending, delete_pending,
)

logger = logging.getLogger("LiveVideoComposer.license")

# ─── Costanti ────────────────────────────────────────────────────────────────
API_BASE_URL = "https://live-works-app.web.app/api"
PRODUCT_ID = "video-composer"
APP_VERSION = "1.5.0"
OFFLINE_GRACE_DAYS = 30
PENDING_POLL_INTERVAL_S = 30
REQUEST_TIMEOUT_S = 30

# Regex formato chiave (esclude caratteri ambigui I, O, 0, 1)
_KEY_RE = re.compile(
    r"^LIVE-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$"
)
_RAW_ALPHANUM_RE = re.compile(r"^[A-HJ-NP-Z2-9]{16}$")


# ─── Stato licenza ────────────────────────────────────────────────────────────
class LicenseStatus(Enum):
    LICENSED = "licensed"
    NOT_LICENSED = "not_licensed"
    NEEDS_ONLINE_VERIFY = "needs_online_verify"
    PENDING_APPROVAL = "pending_approval"
    EXPIRED = "expired"


# ─── Helper ───────────────────────────────────────────────────────────────────
def normalize_key(raw: str) -> str | None:
    """
    Normalizza la chiave inserita dall'utente.
    Accetta LIVE-XXXX-... oppure 16 caratteri alfanumerici senza trattini.
    Restituisce la chiave nel formato canonico o None se invalida.
    """
    key = raw.strip().upper().replace(" ", "").replace("-", "")
    if _RAW_ALPHANUM_RE.match(key):
        return f"LIVE-{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
    key_with_prefix = raw.strip().upper()
    if _KEY_RE.match(key_with_prefix):
        return key_with_prefix
    return None


def _is_valid_key_format(key: str) -> bool:
    return bool(_KEY_RE.match(key))


def _parse_iso(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _offline_grace_ok(license_data: dict[str, Any]) -> bool:
    """
    Verifica se la licenza è utilizzabile offline.
    Restituisce False se scaduta o se il grace period è terminato.
    """
    now = _now_utc()

    # Controllo scadenza assoluta
    expires_at = _parse_iso(license_data.get("expires_at"))
    if expires_at is not None and now > expires_at:
        return False

    # Controllo grace period su verify_before
    verify_before = _parse_iso(license_data.get("verify_before"))
    if verify_before is None:
        return False  # Dati incompleti: richiede verifica online
    deadline = verify_before + timedelta(days=OFFLINE_GRACE_DAYS)
    return now <= deadline


# ─── API HTTP ─────────────────────────────────────────────────────────────────
def _post(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST a {API_BASE_URL}/{endpoint}. Lancia requests.RequestException su errori di rete."""
    url = f"{API_BASE_URL}/{endpoint}"
    resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_S)
    # L'API Live Works restituisce sempre JSON, anche per errori 4xx.
    # raise_for_status solo su 5xx (errore server reale).
    if resp.status_code >= 500:
        resp.raise_for_status()
    try:
        return resp.json()
    except (ValueError, Exception):
        return {"success": False, "valid": False, "error": f"HTTP {resp.status_code}"}


# ─── Funzioni principali ──────────────────────────────────────────────────────
def get_status() -> tuple[LicenseStatus, dict[str, Any]]:
    """
    Controlla lo stato licenza offline (solo file locale + fingerprint).
    Non fa chiamate di rete.
    Restituisce (status, license_data).
    """
    license_data = load_license()

    if license_data is None:
        # Controlla se c'è un pending in attesa
        pending = load_pending()
        if pending:
            return LicenseStatus.PENDING_APPROVAL, {}
        return LicenseStatus.NOT_LICENSED, {}

    # Verifica fingerprint
    try:
        fp, _ = compute_fingerprint()
    except RuntimeError:
        return LicenseStatus.NOT_LICENSED, {}

    if license_data.get("fingerprint") != fp:
        return LicenseStatus.NOT_LICENSED, license_data

    token = license_data.get("token", "")
    if not token:
        pending = load_pending()
        if pending and pending.get("fingerprint") == fp:
            return LicenseStatus.PENDING_APPROVAL, license_data
        return LicenseStatus.NOT_LICENSED, license_data

    if _offline_grace_ok(license_data):
        return LicenseStatus.LICENSED, license_data

    return LicenseStatus.NEEDS_ONLINE_VERIFY, license_data


def activate(license_key: str) -> dict[str, Any]:
    """
    Tenta l'attivazione online con il backend Live Works.
    Restituisce il payload JSON della risposta.
    Lancia ValueError su formato chiave invalido.
    Lancia requests.RequestException su errori di rete.
    """
    normalized = normalize_key(license_key)
    if normalized is None or not _is_valid_key_format(normalized):
        raise ValueError(f"Invalid license key format: {license_key!r}")

    fp, details = compute_fingerprint()

    payload = {
        "licenseKey": normalized,
        "hardwareFingerprint": fp,
        "hardwareDetails": details,
        "productId": PRODUCT_ID,
        "appVersion": APP_VERSION,
    }

    data = _post("activate", payload)

    if data.get("success"):
        # Attivazione riuscita: salva licenza cifrata
        license_data = {
            "license_key": normalized,
            "fingerprint": fp,
            "token": data.get("token", ""),
            "expires_at": data.get("expiresAt"),
            "verify_before": data.get("verifyBeforeDate"),
            "product_ids": data.get("productIds", []),
            "customer_name": data.get("customerName", ""),
        }
        save_license(license_data)
        delete_pending()
    elif data.get("pendingApproval"):
        # In attesa approvazione admin: salva pending
        save_pending(normalized, fp)

    return data


def verify_online() -> dict[str, Any]:
    """
    Verifica online la licenza esistente.
    Aggiorna token e date se il server restituisce newToken.
    Lancia requests.RequestException su errori di rete.
    Lancia RuntimeError se non c'è licenza locale.
    """
    license_data = load_license()
    if license_data is None:
        # Nessuna licenza: prova comunque con pending se presente
        pending = load_pending()
        if pending:
            return _verify_pending(pending)
        raise RuntimeError("No local license to verify.")

    try:
        fp, _ = compute_fingerprint()
    except RuntimeError as exc:
        raise RuntimeError("Cannot compute fingerprint.") from exc

    payload = {
        "licenseKey": license_data.get("license_key", ""),
        "hardwareFingerprint": fp,
        "token": license_data.get("token", ""),
        "productId": PRODUCT_ID,
        "appVersion": APP_VERSION,
    }

    data = _post("verify", payload)

    if data.get("valid"):
        # Aggiorna dati licenza locali
        license_data["verify_before"] = data.get("nextVerifyDate", license_data.get("verify_before"))
        if data.get("newToken"):
            license_data["token"] = data["newToken"]
        if data.get("expiresAt"):
            license_data["expires_at"] = data["expiresAt"]
        save_license(license_data)
    elif data.get("pendingApproval"):
        save_pending(license_data.get("license_key", ""), fp)

    return data


def _verify_pending(pending: dict[str, Any]) -> dict[str, Any]:
    """Riprova /activate per un pending in coda (polling durante attesa approvazione)."""
    try:
        fp, details = compute_fingerprint()
    except RuntimeError:
        return {"valid": False, "error": "Cannot compute fingerprint"}

    payload = {
        "licenseKey": pending.get("license_key", ""),
        "hardwareFingerprint": fp,
        "hardwareDetails": details,
        "productId": PRODUCT_ID,
        "appVersion": APP_VERSION,
    }
    data = _post("activate", payload)

    if data.get("success"):
        license_data = {
            "license_key": pending.get("license_key", ""),
            "fingerprint": fp,
            "token": data.get("token", ""),
            "expires_at": data.get("expiresAt"),
            "verify_before": data.get("verifyBeforeDate"),
            "product_ids": data.get("productIds", []),
            "customer_name": data.get("customerName", ""),
        }
        save_license(license_data)
        delete_pending()

    return data


def deactivate(reason: str) -> bool:
    """
    Deattiva la licenza (uninstall o pc_change).
    Restituisce True se il server ha accettato, False altrimenti (best-effort).
    """
    license_data = load_license()
    if license_data is None:
        return False

    try:
        fp, _ = compute_fingerprint()
    except RuntimeError:
        return False

    payload = {
        "licenseKey": license_data.get("license_key", ""),
        "hardwareFingerprint": fp,
        "token": license_data.get("token", ""),
        "reason": reason,
    }

    success = False
    try:
        data = _post("deactivate", payload)
        success = data.get("success", False)
    except Exception as exc:
        logger.warning("Deactivate API call failed (best-effort): %s", exc)

    delete_license()
    delete_pending()
    return success


def run_deactivate_uninstall() -> None:
    """
    Entry point headless per la disinstallazione.
    Chiamato con --deactivate da riga di comando prima di rimuovere l'app.
    """
    logger.info("Running deactivate on uninstall...")
    result = deactivate("uninstall")
    logger.info("Deactivate result: %s", result)
