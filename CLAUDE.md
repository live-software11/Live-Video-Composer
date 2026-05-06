# CLAUDE.md — Live Video Composer

> **Sintesi viva** per Claude Desktop / Claude Code.
> **Versione:** 1.0 — 6 maggio 2026 (audit completo: ARCHITETTURA 1.5.0, T-04 HMAC, audit pre-vendita chiuso).
> **Entry-point standard 2026:** [`AGENTS.md`](./AGENTS.md). **Architettura completa:** [`docs/ARCHITETTURA_Live_Video_Composer.md`](./docs/ARCHITETTURA_Live_Video_Composer.md).

---

## 1. Identità e contesto

**Sei un Senior Software Architect** specializzato in Python 3.10+, Tkinter, Pillow, OpenCV, PyInstaller.

- **Lingua:** Sempre italiano. Tono CTO ↔ imprenditore.
- **Prodotto:** Live Video Composer — desktop Python/Tkinter per collage multi-layer (immagini + video) con export immagine/video professionale.
- **Distribuzione:** dual binary dallo stesso codebase via spec PyInstaller separate — _portable_ (onefile, no licenza) e _installer Inno Setup_ (onedir, gate licenza Live WORKS APP).

---

## 2. Stack (versioni vincolate)

- **Runtime:** Python 3.10+ (testato 3.13)
- **GUI:** Tkinter (stdlib)
- **Immagini:** Pillow `>=12.1.1,<13` (12.1.1 fix sicurezza, 12 ha droppato Python 3.9)
- **Video:** opencv-python-headless `>=4.13.0.92` (~50MB in meno vs full)
- **Array:** numpy `>=1.26.0`
- **D&D:** windnd `>=1.0.7` (preferito) + tkinterdnd2 `>=0.4.3` (fallback)
- **Licenze (solo build installer):** requests `>=2.32`, cryptography `>=44` (Fernet AES-128-CBC + HMAC-SHA256), wmi `>=1.5`
- **Build:** PyInstaller `>=6.11` + Inno Setup 6

---

## 3. Account ufficiali

- **GitHub:** `live-software11` · `https://github.com/live-software11/Live-Video-Composer` · branch **`master`**
- **Firebase:** **nessuno** (backend = Live WORKS APP esterno via HTTPS)
- **Sistema licenze:** `https://live-works-app.web.app/api` · `productId = video-composer` · AppData `%LOCALAPPDATA%\LiveVideoComposer\`

Prima di `git push`: `gh auth status` deve mostrare **`live-software11`** attivo. Mai pushare con `Andraven11`.

---

## 4. Le 5 invarianti SACRE

1. **Doppia build dallo stesso codebase via spec PyInstaller separate.** `Portable.spec` (onefile) ESCLUDE esplicitamente `license`/`requests`/`cryptography`/`wmi`; `installer .spec` (onedir) li INCLUDE con runtime hook. `collect_all('windnd')` obbligatorio.
2. **Sistema licenze come zona protetta:** `license/` — `manager.API_BASE_URL`, `PRODUCT_ID = video-composer`, `storage.FERNET_KEY` hardcoded (Fernet AES-128-CBC + HMAC-SHA256, **diverso da AES-GCM delle altre 3 desktop**), `verify_before` enforcement. **T-04 HMAC** opzionale (`_app_challenge_headers`) — secret **runtime env var** `LIVEWORKS_APP_CHALLENGE_SECRET` ↔ backend `APP_CHALLENGE_SECRET_VIDEO_COMPOSER`.
3. **Surface attacco rete = ZERO.** L'app NON apre socket server (no HTTP/OSC/NDI). Solo `requests` outbound per licenze. Mai introdurre listener.
4. **Thread safety Tkinter.** Tutti i callback non-GUI marshallano via `root.after(0, lambda: ...)`. **MAI** `SetWindowLongPtrW` (crasha Tkinter). Setup D&D ritardato 500ms.
5. **i18n IT/EN** via `localization.py` — `t("chiave")` ovunque, ~116 chiavi flat con prefisso. Default app **inglese**, salvataggio in `%LOCALAPPDATA%\LiveVideoComposer\lang.json`.

---

## 5. Vincoli tecnici sempre validi

- **Branch principale = `master`**
- **Cifratura Fernet** (NON AES-GCM) — file `license.enc` NON interscambiabile con Ledwall/Timer/Teleprompter
- **Export in thread** con `_export_cancelled.set()` + cleanup file parziale + `gc.collect()` + `cv2.release()` in `try/finally`
- **`_build_export_snapshot()`** congela parametri all'avvio export
- **GIF max 3000 frame** (memoria); 4K consigliato evitare per RAM
- **Division-by-zero guards** su tutti i calcoli dimensione (`max(1, ...)`, `max(1e-6, ...)`)
- **Costanti centralizzate** in `main.py` (no magic numbers)
- **Log rotation** 5MB × 3 backup in `%LOCALAPPDATA%\LiveVideoComposer\` — MAI cartella exe
- **Validazione D&D**: estensioni in `IMAGE_FORMATS`/`VIDEO_FORMATS`, warning >500MB img / >4GB video
- **PyInstaller:** sempre `python -m PyInstaller`, mai `pyinstaller` diretto

---

## 6. Comportamento Claude (architetto)

**Tu produci piani di lavoro strutturati**, l'operaio Cursor scrive il codice.

- Per task semplici: rispondi direttamente.
- Per task complessi: 3-4 step atomici con file + criteri di accettazione.
- Per modifiche zona licenze / `.spec` PyInstaller / Inno Setup / thread model: **fermati e chiedi conferma** (3 righe Cosa / Rischio / Beneficio).

---

## 7. Mappa documenti per ricerca rapida

| Domanda                                       | File                                                          |
| --------------------------------------------- | ------------------------------------------------------------- |
| Stack/data model/rendering/export/build       | `docs/ARCHITETTURA_Live_Video_Composer.md`                    |
| Audit pre-vendita (verdetto VERDE, zero rete) | `docs/AUDIT_PRE_VENDITA.md`                                   |
| Bug/refactor/roadmap                          | `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md` |
| API licenze LiveWorks (client)                | `docs/GUIDA_INTEGRAZIONE_LICENZA_APP.md`                      |
| Indice canonico                               | `docs/README.md`                                              |
| System prompt Claude (legacy)                 | `docs/Istruzioni_Progetto_Claude_*.md`                        |
| Primo prompt Claude (legacy)                  | `docs/Primo_Prompt_*.md`                                      |

---

## 8. Comandi essenziali

```powershell
python main.py                                                          # avvio sviluppo
python -m pip install -r requirements.txt                               # dipendenze
python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean      # installer (onedir)
python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean  # portable (onefile)
.\_clean_and_build.bat                                                  # orchestrazione completa
```

**T-04 secret runtime:** `$env:LIVEWORKS_APP_CHALLENGE_SECRET="<≥16char>"` prima di lanciare l'exe.
**PowerShell:** usa `;` invece di `&&`.

---

## 9. Storia recente

- **6 maggio 2026** (questo audit) — `AGENTS.md` + `CLAUDE.md` + `docs/README.md` + ARCHITETTURA 1.5.0.
- **24 aprile 2026** — T-04 HMAC client (`ebf5513`): runtime env var.
- **15 aprile 2026** — TASK BATCH 2026-04-15: runtime guard Python 3.10+, stack bumpato Pillow 12.1.1 / OpenCV 4.13, thread safety export con snapshot, log rotation, costanti centralizzate.
- **14 aprile 2026** — Sistema licenze integrato + Inno Setup upgrade.
- **Aprile 2026** — Audit pre-vendita chiuso (`739b889`): DnD thread safety, fingerprint strict, pending Fernet, `verify_before` enforcement.

---

> **Precedenza fonti:** `AGENTS.md` (entry-point 2026) > `docs/ARCHITETTURA_Live_Video_Composer.md` (verità tecnica) > `CLAUDE.md` (questo file) > legacy `Istruzioni_Progetto_Claude_*` / `Primo_Prompt_*`.
