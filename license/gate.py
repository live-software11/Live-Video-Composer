"""
License gate — Live Video Composer.
Finestra Tkinter modale che blocca l'avvio dell'app principale
finché la licenza non è attiva (o in stato di grace offline).
"""

import logging
import threading
import tkinter as tk
from typing import Callable

import requests  # type: ignore

from .manager import (
    LicenseStatus, get_status, activate, verify_online,
    normalize_key, PENDING_POLL_INTERVAL_S,
)
from localization import t

logger = logging.getLogger("LiveVideoComposer.license")

# ─── Colori coerenti con il tema dark dell'app ─────────────────────────────
_BG = "#0d1117"
_SURFACE = "#161b22"
_BORDER = "#30363d"
_ACCENT = "#00b4d8"
_TEXT = "#e6edf3"
_TEXT_DIM = "#7d8590"
_ERROR = "#f85149"
_SUCCESS = "#3fb950"
_WARNING = "#d29922"


class LicenseGateWindow(tk.Toplevel):
    """
    Finestra modale di attivazione licenza.
    Callback `on_licensed` viene chiamata quando la licenza è valida.
    """

    def __init__(self, parent: tk.Tk, on_licensed: Callable[[], None]):
        super().__init__(parent)
        self._parent = parent
        self._on_licensed = on_licensed
        self._poll_job: str | None = None
        self._pending_key: str | None = None

        self.title(t("license.window_title"))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.configure(bg=_BG)

        # Centra la finestra
        self.update_idletasks()
        w, h = 480, 380
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        self._build_ui()
        self._check_status_async()

    # ─── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=_SURFACE, pady=20)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="⚡ Live Video Composer",
            bg=_SURFACE, fg=_ACCENT,
            font=("Segoe UI", 15, "bold"),
        ).pack()
        tk.Label(
            header, text=t("license.activation_required"),
            bg=_SURFACE, fg=_TEXT_DIM,
            font=("Segoe UI", 9),
        ).pack(pady=(2, 0))

        # Separatore
        tk.Frame(self, bg=_BORDER, height=1).pack(fill=tk.X)

        # Corpo
        body = tk.Frame(self, bg=_BG, padx=30, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Status label
        self._status_var = tk.StringVar(value=t("license.checking"))
        self._status_label = tk.Label(
            body, textvariable=self._status_var,
            bg=_BG, fg=_TEXT_DIM,
            font=("Segoe UI", 9), wraplength=400, justify=tk.LEFT,
        )
        self._status_label.pack(anchor=tk.W, pady=(0, 16))

        # Input chiave
        tk.Label(
            body, text=t("license.enter_key"),
            bg=_BG, fg=_TEXT,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)

        entry_frame = tk.Frame(body, bg=_BORDER, padx=1, pady=1)
        entry_frame.pack(fill=tk.X, pady=(4, 12))

        self._key_var = tk.StringVar()
        self._key_entry = tk.Entry(
            entry_frame, textvariable=self._key_var,
            bg=_SURFACE, fg=_TEXT, insertbackground=_TEXT,
            font=("Courier New", 12), relief=tk.FLAT,
            width=32,
        )
        self._key_entry.pack(fill=tk.X, padx=6, pady=6)
        self._key_entry.bind("<Return>", lambda _e: self._on_activate())

        # Placeholder hint
        tk.Label(
            body, text="LIVE-XXXX-XXXX-XXXX-XXXX",
            bg=_BG, fg=_TEXT_DIM,
            font=("Courier New", 9),
        ).pack(anchor=tk.W, pady=(0, 16))

        # Pulsante attiva
        self._activate_btn = tk.Button(
            body, text=t("license.activate_btn"),
            bg=_ACCENT, fg="#000000",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, padx=16, pady=8,
            cursor="hand2",
            command=self._on_activate,
        )
        self._activate_btn.pack(anchor=tk.W)

        # Error/info label
        self._info_var = tk.StringVar()
        self._info_label = tk.Label(
            body, textvariable=self._info_var,
            bg=_BG, fg=_ERROR,
            font=("Segoe UI", 9), wraplength=400, justify=tk.LEFT,
        )
        self._info_label.pack(anchor=tk.W, pady=(8, 0))

    # ─── Logica stato ─────────────────────────────────────────────────────────
    def _check_status_async(self):
        """Controlla lo stato licenza in un thread separato per non bloccare la UI."""
        threading.Thread(target=self._check_status_worker, daemon=True).start()

    def _check_status_worker(self):
        status, _data = get_status()
        self.after(0, self._apply_status, status)

    def _apply_status(self, status: LicenseStatus):
        if status == LicenseStatus.LICENSED:
            self._grant_access()
        elif status == LicenseStatus.NEEDS_ONLINE_VERIFY:
            self._set_status(t("license.verifying_online"), _TEXT_DIM)
            threading.Thread(target=self._verify_online_worker, daemon=True).start()
        elif status == LicenseStatus.PENDING_APPROVAL:
            self._show_pending_state()
        else:
            self._set_status(t("license.enter_key_hint"), _TEXT_DIM)

    def _verify_online_worker(self):
        try:
            data = verify_online()
            if data.get("valid"):
                self.after(0, self._grant_access)
            elif data.get("pendingApproval"):
                self.after(0, self._show_pending_state)
            else:
                msg = data.get("error", t("license.verify_failed"))
                self.after(0, self._set_info, msg, _ERROR)
                self.after(0, self._set_status, t("license.enter_key_hint"), _TEXT_DIM)
        except requests.RequestException:
            self.after(0, self._set_info, t("license.network_error"), _WARNING)
            self.after(0, self._set_status, t("license.offline_hint"), _TEXT_DIM)
        except RuntimeError as exc:
            self.after(0, self._set_info, str(exc), _ERROR)

    def _on_activate(self):
        raw = self._key_var.get().strip()
        if not raw:
            self._set_info(t("license.key_required"), _ERROR)
            return

        normalized = normalize_key(raw)
        if normalized is None:
            self._set_info(t("license.invalid_key_format"), _ERROR)
            return

        self._set_info("", _TEXT_DIM)
        self._activate_btn.config(state=tk.DISABLED, text=t("license.activating"))
        self._key_entry.config(state=tk.DISABLED)
        threading.Thread(
            target=self._activate_worker, args=(normalized,), daemon=True
        ).start()

    def _activate_worker(self, key: str):
        try:
            data = activate(key)
            if data.get("success"):
                self.after(0, self._grant_access)
            elif data.get("pendingApproval"):
                self._pending_key = key
                self.after(0, self._show_pending_state)
            else:
                msg = data.get("error") or t("license.activation_failed")
                self.after(0, self._restore_activate_btn)
                self.after(0, self._set_info, msg, _ERROR)
        except ValueError as exc:
            self.after(0, self._restore_activate_btn)
            self.after(0, self._set_info, str(exc), _ERROR)
        except requests.RequestException:
            self.after(0, self._restore_activate_btn)
            self.after(0, self._set_info, t("license.network_error"), _ERROR)
        except Exception as exc:
            logger.exception("Unexpected error during activation")
            self.after(0, self._restore_activate_btn)
            self.after(0, self._set_info, t("license.unexpected_error"), _ERROR)

    def _restore_activate_btn(self):
        self._activate_btn.config(state=tk.NORMAL, text=t("license.activate_btn"))
        self._key_entry.config(state=tk.NORMAL)

    def _show_pending_state(self):
        self._set_status(t("license.pending_approval"), _WARNING)
        self._set_info(t("license.pending_hint"), _TEXT_DIM)
        self._activate_btn.config(state=tk.DISABLED)
        self._schedule_pending_poll()

    def _schedule_pending_poll(self):
        self._poll_job = self.after(
            PENDING_POLL_INTERVAL_S * 1000, self._poll_pending
        )

    def _poll_pending(self):
        threading.Thread(target=self._poll_pending_worker, daemon=True).start()

    def _poll_pending_worker(self):
        try:
            data = verify_online()
            if data.get("valid"):
                self.after(0, self._grant_access)
            elif data.get("pendingApproval"):
                self.after(0, self._schedule_pending_poll)
            else:
                self.after(0, self._set_status, t("license.enter_key_hint"), _TEXT_DIM)
                self.after(0, self._restore_activate_btn)
        except Exception as exc:
            logger.debug("Pending poll failed: %s", exc)
            self.after(0, self._schedule_pending_poll)

    # ─── Azioni ───────────────────────────────────────────────────────────────
    def _grant_access(self):
        if self._poll_job:
            self.after_cancel(self._poll_job)
            self._poll_job = None
        self.destroy()
        self._on_licensed()

    def _on_close(self):
        """Chiusura della finestra = chiusura dell'intera app."""
        if self._poll_job:
            self.after_cancel(self._poll_job)
        self._parent.destroy()

    # ─── Helper UI ────────────────────────────────────────────────────────────
    def _set_status(self, text: str, color: str = _TEXT_DIM):
        self._status_var.set(text)
        self._status_label.config(fg=color)

    def _set_info(self, text: str, color: str = _ERROR):
        self._info_var.set(text)
        self._info_label.config(fg=color)


def show_license_gate(parent: tk.Tk, on_licensed: Callable[[], None]) -> None:
    """
    Mostra la finestra gate licenza.
    `on_licensed` viene chiamata quando la licenza è valida.
    """
    gate = LicenseGateWindow(parent, on_licensed)
    gate.grab_set()
    parent.wait_window(gate)
