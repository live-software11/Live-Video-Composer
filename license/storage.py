"""
License storage — Live Video Composer.
Cifra i dati licenza con Fernet (AES-128-CBC + HMAC-SHA256) in %LOCALAPPDATA%.
File:
  - license.enc   → dati licenza cifrati (JSON)
  - pending_activation.json → chiave in attesa di approvazione admin (in chiaro)
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("LiveVideoComposer.license")

# Identificatore app per AppData (allineato all'app)
_APP_DATA_NAME = "com.livesoftware.live-video-composer"


def _get_app_data_dir() -> Path:
    """Restituisce la directory dati dell'app in %LOCALAPPDATA%."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        d = Path(base) / _APP_DATA_NAME
    else:
        d = Path.home() / f".{_APP_DATA_NAME}"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        d = Path.home()
    return d


def _get_fernet():
    """Inizializza e restituisce un'istanza Fernet con la chiave embedded."""
    from cryptography.fernet import Fernet  # type: ignore
    # Chiave embedded: protezione anti-tamper basilare (allineata agli altri client LiveWorks).
    # Non è un segreto forte contro reverse engineering — è un limite noto per client desktop.
    _KEY = b"dW5pUXVlTGl2ZVdvcmtzVmlkZW9Db21wb3Nlck9LMT0="
    return Fernet(_KEY)


def load_license() -> dict[str, Any] | None:
    """Carica e decifra i dati licenza. Restituisce dict o None se assenti/corrotti."""
    path = _get_app_data_dir() / "license.enc"
    if not path.exists():
        return None
    try:
        f = _get_fernet()
        ciphertext = path.read_bytes()
        plaintext = f.decrypt(ciphertext)
        return json.loads(plaintext.decode("utf-8"))
    except Exception as exc:
        logger.warning("Failed to load license file: %s", exc)
        return None


def save_license(data: dict[str, Any]) -> bool:
    """Cifra e salva i dati licenza. Restituisce True se riuscito."""
    path = _get_app_data_dir() / "license.enc"
    try:
        f = _get_fernet()
        plaintext = json.dumps(data).encode("utf-8")
        ciphertext = f.encrypt(plaintext)
        path.write_bytes(ciphertext)
        return True
    except Exception as exc:
        logger.error("Failed to save license file: %s", exc)
        return False


def delete_license() -> None:
    """Rimuove il file licenza locale."""
    path = _get_app_data_dir() / "license.enc"
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Failed to delete license file: %s", exc)


def load_pending() -> dict[str, Any] | None:
    """Carica il file pending_activation cifrato (con fallback legacy in chiaro)."""
    path = _get_app_data_dir() / "pending_activation.json"
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
        try:
            f = _get_fernet()
            plaintext = f.decrypt(raw)
            return json.loads(plaintext.decode("utf-8"))
        except Exception:
            return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        logger.warning("Failed to load pending activation: %s", exc)
        return None


def save_pending(license_key: str, fingerprint: str) -> None:
    """Salva i dati di attivazione in attesa di approvazione admin (cifrati)."""
    path = _get_app_data_dir() / "pending_activation.json"
    try:
        f = _get_fernet()
        plaintext = json.dumps({"license_key": license_key, "fingerprint": fingerprint}).encode("utf-8")
        path.write_bytes(f.encrypt(plaintext))
    except Exception as exc:
        logger.warning("Failed to save pending activation: %s", exc)


def delete_pending() -> None:
    """Rimuove il file pending_activation.json."""
    path = _get_app_data_dir() / "pending_activation.json"
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Failed to delete pending activation: %s", exc)
