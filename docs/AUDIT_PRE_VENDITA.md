# Live Video Composer — Audit pre-vendita

> Generato: Aprile 2026 | Stack: Python 3.10+ / Tkinter / PIL / OpenCV
> Ultimo aggiornamento: fix applicati Aprile 2026

---

## Verdetto: VERDE — Pronto per la vendita

L'app non espone socket di rete. Tutti i fix MEDIUM sono stati applicati: DnD thread-safe, fingerprint robusto, pending cifrato, grace period conservativo.

---

## Fix applicati in questo audit

### MEDIUM — Risolti

- **DnD thread safety** (`main.py`) — `windnd` callback ora usa `root.after(0, ...)` per garantire esecuzione sul thread Tk
- **Fingerprint WMI** (`fingerprint.py`) — `RuntimeError` con dettagli se WMI fallisce, invece di `UNKNOWN_*` fallback
- **`verify_before` assente = rifiuto** (`manager.py`) — restituisce `False` (richiede verifica online) invece di `True` grace illimitato
- **Pending cifrato** (`storage.py`) — `save_pending` usa Fernet; `load_pending` con fallback legacy in chiaro

---

## Punti residui (accettabili per vendita)

### Limite architetturale

- Chiave Fernet hardcoded — limite intrinseco DRM client-side; mitigato da verify online
- Build portable senza gate licenza — scelta commerciale documentata

### LOW

- Export GIF con RAM elevata su risoluzioni 4K — consigliare limite risoluzione
- `except Exception` generici in alcuni punti — restringere dove possibile
- Divisione per zero su `orig_h == 0` — mitigato da load che scarta dimensioni zero

---

## Nessun rischio di rete

A differenza delle altre 3 app, Live Video Composer **non apre socket server** (nessun HTTP, OSC, NDI). Superficie di attacco da rete = zero.

---

## Checklist pre-rilascio

- [x] DnD thread-safe
- [x] Fingerprint errore su WMI failure
- [x] Pending cifrato
- [x] verify_before assente = rifiuto
- [ ] `_clean_and_build.bat` → portable + setup
- [ ] Test: file immagine corrotto → messaggio errore
- [ ] Test: activate → verify → deactivate su PC reale
- [ ] Test: upgrade Inno Setup preserva licenza
