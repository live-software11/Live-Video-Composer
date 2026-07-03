# AGENTS.md — Live Video Composer

> **Entry-point unico per agenti AI** (Cursor, Claude Code, Codex, Continue, ecc.) su questo workspace.
> Compatibile con il formato standard `AGENTS.md` (2026). Letto a inizio di ogni sessione.
>
> **Ultimo aggiornamento:** 3 luglio 2026 (ARCHITETTURA 1.5.2: codec export ottimizzati per vMix/Resolume Arena, opacità per-layer, sfondo trasparente PNG/WebP).

---

## 0. Cosa è questo workspace

- **Prodotto:** Live Video Composer — applicazione **desktop** Python 3.10+ (Tkinter + Pillow + OpenCV) per creare collage multi-layer con immagini e video; export immagine (JPG/PNG/WebP/BMP) e video (MP4/AVI/WebM/GIF).
- **Funzionalità:** multi-layer collage con ordine modificabile; trasformazioni (zoom 1-1000%, rotazione ±180°, flip H/V, posizione pixel-perfect); handle visivi stile PowerPoint; preset risoluzione + qualità/bitrate; D&D nativo Windows (windnd); export cancellabile in thread.
- **Target:** Content creator, social media manager, tecnici AV per eventi live.
- **Tipo:** Distribuito in **due build** dal singolo codebase via PyInstaller + spec separate — _portable_ (`.exe` onefile, no licenza) e _installer_ Inno Setup (`.exe` setup, gate licenza Live WORKS APP).
- **Cartella app:** root del workspace (`main.py`, `localization.py`, `license/`, `scripts/`, `docs/`, `icons/`, `requirements.txt`).
- **Lingua agente ↔ utente:** SEMPRE italiano. Tono CTO che parla a un imprenditore (Andrea Rizzari).
- **Account ufficiali (mai incrociare):**
  - **GitHub:** `live-software11` · remote `https://github.com/live-software11/Live-Video-Composer` · branch `master`
  - **Firebase:** **nessuno** per questa app (backend = Live WORKS APP esterno via HTTPS)
  - **Sistema licenze:** Live WORKS APP (`live-works-app.web.app/api`) · `productId = video-composer` · AppData `%LOCALAPPDATA%\LiveVideoComposer\`

---

## 1. Mappa documentazione (dove guardare cosa)

| Vuoi sapere…                                                                      | Apri questo file                                                                                                                                             |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Sintesi viva per Claude Desktop/Code**                                          | [`CLAUDE.md`](./CLAUDE.md) (root)                                                                                                                            |
| **Architettura completa: stack, data model, rendering, export, build, changelog** | [`docs/ARCHITETTURA_Live_Video_Composer.md`](./docs/ARCHITETTURA_Live_Video_Composer.md)                                                                     |
| **Indice canonico documenti**                                                     | [`docs/README.md`](./docs/README.md)                                                                                                                         |
| **Audit pre-vendita (verdetto VERDE — zero superficie rete)**                     | [`docs/AUDIT_PRE_VENDITA.md`](./docs/AUDIT_PRE_VENDITA.md)                                                                                                   |
| **Bug, refactor, roadmap implementazioni**                                        | [`docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md`](./docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md)                               |
| **Integrazione client API licenze LiveWorks**                                     | [`docs/GUIDA_INTEGRAZIONE_LICENZA_APP.md`](./docs/GUIDA_INTEGRAZIONE_LICENZA_APP.md)                                                                         |
| **System prompt Claude Desktop (architetto, legacy)**                             | [`docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md`](./docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md)                                         |
| **Primo prompt avvio chat Claude (legacy)**                                       | [`docs/Primo_Prompt_Avvio_Chat_Claude_Desktop_Live_Video_Composer.md`](./docs/Primo_Prompt_Avvio_Chat_Claude_Desktop_Live_Video_Composer.md)                 |
| **Task batch storico (15/04/2026)**                                               | [`docs/TASK_BATCH_2026-04-15.md`](./docs/TASK_BATCH_2026-04-15.md)                                                                                           |
| **Regole Cursor modulari (10 file)**                                              | [`.cursor/rules/*.mdc`](./.cursor/rules)                                                                                                                     |
| **Modulo Python licensing**                                                       | [`license/`](./license) (incluso solo nello spec installer)                                                                                                  |
| **Spec PyInstaller**                                                              | [`Live_Video_Composer.spec`](./Live_Video_Composer.spec) (installer) · [`Live_Video_Composer_Portable.spec`](./Live_Video_Composer_Portable.spec) (portable) |
| **Inno Setup**                                                                    | [`installer.iss`](./installer.iss)                                                                                                                           |
| **Build script**                                                                  | [`_clean_and_build.bat`](./_clean_and_build.bat) (orchestrazione) · [`_build_setup.bat`](./_build_setup.bat)                                                 |

> **Prima di scrivere codice nuovo:** apri sempre `docs/ARCHITETTURA_Live_Video_Composer.md`. È il single source of truth tecnico.

---

## 2. Stack tecnologico (NON cambiare versioni senza approvazione)

### Runtime e librerie core

| Pacchetto    | Versione (`requirements.txt`)        | Ruolo                                              |
| ------------ | ------------------------------------ | -------------------------------------------------- |
| Python       | **3.10+** (testato 3.13)             | Runtime — Pillow 12 ha droppato 3.9                |
| Tkinter      | stdlib                               | GUI                                                |
| Pillow (PIL) | `>=12.1.1,<13`                       | Immagini, resize, composite (12.1.1 fix sicurezza) |
| OpenCV       | `opencv-python-headless >=4.13.0.92` | Video capture/export (~50 MB in meno vs full)      |
| numpy        | `>=1.26.0`                           | Array per video                                    |
| windnd       | `>=1.0.7`                            | Drag & drop nativo Windows (preferito)             |
| tkinterdnd2  | `>=0.4.3`                            | Fallback D&D (opzionale)                           |

### Modulo licenza Python (incluso solo in build installer)

| Pacchetto    | Versione   | Ruolo                                                                                |
| ------------ | ---------- | ------------------------------------------------------------------------------------ |
| requests     | `>=2.32.0` | HTTP client `live-works-app.web.app/api`                                             |
| cryptography | `>=44.0.0` | **Fernet (AES-128-CBC + HMAC-SHA256)** per `license.enc` + `pending_activation.json` |
| wmi          | `>=1.5.1`  | Fingerprint Windows (`Win32_BaseBoard` + `Win32_Processor` + `Win32_DiskDrive`)      |

### Build & packaging

| Strumento   | Versione | Ruolo                                                      |
| ----------- | -------- | ---------------------------------------------------------- |
| PyInstaller | `>=6.11` | Build eseguibile (`onefile` portable / `onedir` installer) |
| Inno Setup  | 6        | Installer Windows                                          |

### Differenza chiave: Fernet vs AES-GCM

A differenza delle altre 3 desktop (Ledwall/Timer/Teleprompter) che usano **AES-256-GCM**, Video Composer usa **Fernet** (AES-128-CBC + HMAC-SHA256). Limite intrinseco DRM client-side, mitigato da verify online + grace 30gg. **NON** cambiare schema senza valutare migrazione storage.

---

## 3. Le 5 invarianti SACRE (mai violare)

1. **Account GitHub immutabile.** `origin` punta a `live-software11/Live-Video-Composer`. Prima di `git push`: `gh auth status` → account attivo deve essere **`live-software11`**. Mai pushare con `Andraven11`. Branch principale = **`master`**.

2. **Doppia build dal singolo codebase via spec PyInstaller separate.** `Live_Video_Composer_Portable.spec` (onefile, **esclude esplicitamente** modulo `license` + `requests`/`cryptography`/`wmi`); `Live_Video_Composer.spec` (onedir, include `license` + dipendenze, runtime hook). `collect_all('windnd')` obbligatorio in entrambi. **`_clean_and_build.bat`** orchestra: `cd /d "%~dp0"` → clean → installer onedir → portable onefile → Inno Setup wrap.

3. **Sistema licenze come zona protetta.** `license/`:
   - `manager.API_BASE_URL = https://live-works-app.web.app/api`
   - `manager.PRODUCT_ID = video-composer`
   - `storage.FERNET_KEY` hardcoded — limite intrinseco DRM, mitigato da verify online + grace 30gg
   - `manager.verify_before` assente = **rifiuto** (richiede verifica online)
   - `pending_activation` cifrato Fernet (con fallback legacy clear-text)
   - `fingerprint.compute_fingerprint()` errore esplicito su WMI failure (no `UNKNOWN_*`)
   - **`_app_challenge_headers` (T-04)**: header HMAC opzionali emessi a **runtime** se env var `LIVEWORKS_APP_CHALLENGE_SECRET` (≥16 char) impostata. Header: `X-App-Id` / `X-App-Version` / `X-App-Challenge-Ts` / `X-App-Challenge`. Payload HMAC = `productId|version|ts|fingerprint`. Backend match: `APP_CHALLENGE_SECRET_VIDEO_COMPOSER` su Cloud Functions WORKS APP. Modifiche richiedono replica nel backend.

4. **Thread safety GUI Tkinter.** Tutti i callback non-GUI (export thread, windnd D&D, HTTP licenze) DEVONO marshallare risultati su Tk via `root.after(0, lambda: ...)`. **MAI** subclassing Win32 WNDPROC (`SetWindowLongPtrW`) — crasha Tkinter. Setup D&D ritardato 500ms (`root.after(500, _do_setup_drag_and_drop)`).

5. **i18n IT/EN parità totale via `localization.py`.** `t("chiave")` ovunque, mai stringhe hardcoded. ~116 chiavi flat con prefisso (`app.`, `layers.`, `btn.`, `transform.`, `size.`, `fit.`, `mirror.`, `canvas.`, `output.`, `export.`, `preset.`, `status.`, `error.`, `layer.`, `menu.`). Placeholder `{0}`, `{1}` (str.format). Default app **inglese** (`_CURRENT_LANG = "en"`). Lingua salvata in `%LOCALAPPDATA%\LiveVideoComposer\lang.json`. Toggle IT/EN in header (cyan attivo). Installer Inno Setup in inglese.

---

## 4. Invarianti tecniche derivate (sempre verificare)

- **Surface attacco rete = zero.** L'app **NON apre socket server** (no HTTP, no OSC, no NDI). Nessun bind LAN da gestire. Solo `requests` outbound per licenze.
- **Export in thread con cleanup robusto:** `_start_export()` → `Thread(_do_export_image/video)` → `_export_cancelled.set()` su cancel → cleanup file parziale + `gc.collect()` + release `cv2` in `try/except` + `_stop_export()` SEMPRE in `finally`.
- **`_build_export_snapshot()` + `_create_composite_from_snapshot()`** — l'export legge parametri congelati all'avvio, modifiche concorrenti ai layer non corrompono l'output (TASK-008).
- **GIF max 3000 frame** (limite memoria). 4K consigliato evitare per RAM.
- **Division-by-zero guards:** `max(1, output_w/h)`, `max(1, fps)`, `max(1, img_w/h)`, `max(1e-6, ...)` per preview scale.
- **Costanti centralizzate:** `MAX_GIF_FRAMES=3000`, `DOWNSCALE_THRESHOLD=2.0`, `DND_SETUP_DELAY_MS=500`, `DEBOUNCE_NORMAL_MS=16`, `DEBOUNCE_DRAG_MS=33`, `PREVIEW_SCALE_MARGIN=0.9`.
- **Log:** `RotatingFileHandler` 5MB × 3 backup su `%LOCALAPPDATA%\LiveVideoComposer\live_video_composer.log`. **Mai** loggare nella cartella exe.
- **PyInstaller portable:** `excludes` include `license` + `requests` + `cryptography` + `wmi` + `sphinx` + `tkinter.test` + `unittest` + `IPython` + `notebook`. Verifica con `Get-FileHash` differenza vs installer.
- **PyInstaller installer:** include modulo `license` con runtime hook + `collect_all('windnd')`.
- **`load_video` robusto:** `cv2.VideoCapture.isOpened()`, dimensioni > 0, primo frame; messaggi granulari per codec / dimensioni / errori.
- **`load_image` robusto:** eccezioni PIL granulari (`UnidentifiedImageError`, `DecompressionBombError`, `FileNotFoundError`, `PermissionError`, `OSError`) con i18n.
- **Validazione D&D:** estensione in `IMAGE_FORMATS` / `VIDEO_FORMATS`; warning dimensione > 500MB (img) o > 4GB (video); UnidentifiedImageError → messaggio chiaro.
- **Codec export video — target player vMix/Resolume Arena (verificato empiricamente, non solo teoria):** MP4 usa H.264 (`avc1`, fallback automatico a `mp4v` se il sistema non ha il codec) — per distribuzione/archivio. AVI usa **MJPEG** (default consigliato) — unico codec intra-frame genuino disponibile in questa pipeline OpenCV: HAP/DXV/ProRes/DNxHD **falliscono silenziosamente** e vengono sostituiti con H.264 dal backend Media Foundation di Windows (falso positivo pericoloso, testato). MJPEG dà seek/scrub/loop istantanei essenziali per Resolume; H.264 struggles con simultaneous stream multipli (long-GOP). Vero controllo bitrate/CRF **non è ottenibile** via `cv2.VideoWriter` (verificato: né `VIDEOWRITER_PROP_QUALITY` né `OPENCV_FFMPEG_WRITER_OPTIONS` hanno effetto) — richiederebbe una pipeline ffmpeg dedicata (non implementata, decisione separata).
- **Opacità per-layer + sfondo trasparente:** `ImageLayer.opacity` (0-100%) applicato via helper `_apply_opacity()` in tutti e 3 i path di compositing. Sfondo trasparente (`bg_transparent`) preserva canale alpha reale solo in export PNG/WebP (per overlay in vMix Titles/Resolume); JPG/BMP/video restano sempre opachi. **Attenzione:** `Image.paste(img, box, img)` (immagine come propria maschera) eleva impropriamente al quadrato il canale alpha su destinazione non opaca — usare sempre l'helper `_paste_layer()` (usa `Image.alpha_composite` quando `transparent_bg=True`), mai il paste diretto per nuovo codice di compositing con sfondo trasparente.

---

## 5. Comportamento autonomo vs. conferma

### L'agente procede AUTONOMAMENTE

- Bug fix isolati, refactor di una funzione, aggiunta UI minore
- Aggiunta/aggiornamento stringhe i18n in `localization.py` (IT+EN sempre)
- Aggiunta type hints (`from __future__ import annotations`)
- Aggiornamento docs (ARCHITETTURA changelog datato, BugFix, README)
- Aggiornamento Cursor rules dopo modifica strutturale
- Aggiornamento `requirements.txt` con minor versions

### L'agente si FERMA e chiede conferma (formato 3 righe: Cosa / Rischio / Beneficio)

- Modifiche a `license/` (zona protetta — gemello WORKS APP backend)
- Modifiche a `API_BASE_URL`, `PRODUCT_ID`, `FERNET_KEY`
- Modifiche allo schema cifratura (Fernet → altro)
- Modifiche a `.spec` PyInstaller (esclusioni, hidden imports, runtime hooks)
- Modifiche a `installer.iss` (Inno Setup) o batch build
- Cambio versione major Python (3.10 → 3.11 → 3.12 → 3.13) o Pillow major (12 → 13)
- Refactor che tocca >10 funzioni in `main.py`
- Modifiche al thread model (export, D&D)
- Operazioni distruttive

### MAI fare

- Push su repo diverso da `live-software11/Live-Video-Composer`
- Subclassing Win32 WNDPROC (`SetWindowLongPtrW`) — crasha Tkinter
- Aprire socket server (HTTP/OSC/NDI) — superficie rete deve restare zero
- Includere `release/*.exe`, `dist/`, `build/`, `__pycache__/` nel commit
- Includere `cryptography`/`wmi`/`requests` nel build portable
- Bypassare `gh auth switch --user live-software11` prima di push
- Usare `pyinstaller` diretto invece di `python -m PyInstaller`

---

## 6. Checklist obbligatoria per nuove feature / funzioni

- [ ] **Stack invariato?** `requirements.txt` non modificato senza approvazione (no major bumps silenziosi)?
- [ ] **i18n?** Nuove stringhe IT+EN in `localization.py` con prefisso corretto?
- [ ] **Thread safety?** Callback non-GUI usano `root.after(0, ...)`?
- [ ] **Division-by-zero guards** sui nuovi calcoli?
- [ ] **Export cleanup?** Nuovo path I/O ha `try/finally` + release risorse + `gc.collect()`?
- [ ] **Build dual?** Sia spec installer che portable producono `.exe`?
- [ ] **Portable senza licenza?** Spec portable esclude `license`/`requests`/`cryptography`/`wmi`?
- [ ] **Licensing?** Se tocchi `license/`, hai valutato impatto su WORKS APP backend?
- [ ] **T-04 HMAC?** Se modifichi `manager.py`, `_app_challenge_headers` resta opzionale (no break senza env var)?
- [ ] **Surface rete = zero?** Nessun nuovo socket server introdotto?
- [ ] **WNDPROC?** Nessun subclassing Win32 finestra?
- [ ] **Log path?** Nuovi log scrivono in `%LOCALAPPDATA%\LiveVideoComposer\` (mai cartella exe)?
- [ ] **Docs?** Aggiornato `docs/ARCHITETTURA_Live_Video_Composer.md` (changelog dated v1.x.y) e `BugFix`?
- [ ] **Cursor rules?** Se cambia stack/workflow, aggiornato `.cursor/rules/*.mdc` rilevante?
- [ ] **WORKS APP backend?** Se cambia contratto API o webhook Lemon Squeezy, replica in repo `live-works-app`?

---

## 7. Comandi essenziali

```powershell
# DEV
python main.py                                            # Avvio sviluppo
python -m pip install -r requirements.txt                 # Installa dipendenze (stesso interpreter!)
python -m pip install pyinstaller                         # Per build (non in requirements.txt)

# BUILD (sempre python -m PyInstaller, mai pyinstaller diretto)
python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean             # Installer (onedir)
python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean    # Portable (onefile)

# RELEASE COMPLETA (orchestrato — doppio click)
.\_clean_and_build.bat                                    # cd /d %~dp0 + clean + installer + portable + Inno Setup

# QUALITY
python -m py_compile main.py localization.py license/*.py # syntax check rapido

# GIT (account live-software11)
gh auth status
gh auth switch --user live-software11
git remote -v                                             # github.com/live-software11/Live-Video-Composer
git push origin master
```

**PowerShell:** usa `;` al posto di `&&`.
**T-04 secret in build:** imposta `$env:LIVEWORKS_APP_CHALLENGE_SECRET="<≥16char>"` **prima** di lanciare l'eseguibile (runtime env, non compile-time). Per build da distribuire al cliente, l'env var va impostata in installazione (es. via Inno Setup) o tramite servizio Windows wrapper. Altrimenti omettere = nessun header HMAC, comportamento legacy.
**Output finale (`release/`):** `Live_Video_Composer_Portable.exe` + `Live_Video_Composer_Setup.exe`.

---

## 8. Ecosistema (per orientamento)

| Progetto                              | Stack                                         | Account / Repo                              | productId licenze         |
| ------------------------------------- | --------------------------------------------- | ------------------------------------------- | ------------------------- |
| **Live Video Composer** (qui)         | Python 3.10+ + Tkinter + PIL + OpenCV         | `live-software11/Live-Video-Composer`       | `video-composer`          |
| Live 3d Ledwall Render                | Tauri 2 + Rust + React + Three.js             | `live-software11/Live-3d-Ledwall-Render`    | `ledwall-render`          |
| Live Speaker Timer                    | Tauri 2 + Rust + React + Axum                 | `live-software11/Live-Speaker-Timer`        | `speaker-timer`           |
| Live Speaker Teleprompter             | C# WPF .NET 8                                 | `live-software11/Live-Speaker-Teleprompter` | `speaker-teleprompter`    |
| **Live WORKS APP** (backend licenze)  | React 19 + Firebase Functions Node 22 (Blaze) | `live-software11/live-works-app`            | sorgente di verità        |
| Live PLAN / CREW                      | Web SaaS Firebase Blaze                       | `live-software11/...`                       | `live-plan` / `live-crew` |
| Live SLIDE CENTER                     | React + Tauri 2 + Supabase                    | `live-software11/...`                       | (HMAC bidirezionale)      |
| SITO www.liveworksapp.com             | React 19 + Vite 8 + Tailwind 4 (Vercel)       | `live-software11/liveworks-site`            | nessuno (marketing)       |
| Preventivi DHS / Gestionale FREELANCE | React + Firebase Spark                        | `Andraven11/...`                            | nessuno                   |

**Mai incrociare account.** Per repo `Andraven11/*` usa altro workspace + `gh auth switch --user Andraven11`.

**Differenze cifratura:** Video Composer usa **Fernet (AES-128-CBC + HMAC-SHA256)** mentre Ledwall/Timer/Teleprompter usano **AES-256-GCM**. I file `license.enc` NON sono interscambiabili. Layout: Fernet (`urlsafe_b64( version + timestamp + IV + ciphertext + HMAC )`) vs AES-GCM (`nonce || cipher || tag`).

---

## 9. Storia documentale

- **3 luglio 2026 (sessione corrente)** — Audit completo + ottimizzazione per target player reali (**vMix, Resolume Arena**). Bug fix: `duplicate_layer()` non propagava `_original_path` (export a risoluzione preview invece che piena) né `opacity`; DPI export immagine ora scritto realmente nei metadati (prima calcolato ma mai applicato); preset qualità video reso onesto (bitrate/CRF non avevano alcun effetto verificabile su `cv2.VideoWriter`, verificato con test diretti — rimossi dalla UI). **Codec:** MP4 → H.264 (`avc1`, fallback `mp4v`); AVI → MJPEG (era XVID, ora default) — unico codec intra-frame genuino ottenibile da questa pipeline OpenCV (HAP/DXV/ProRes/DNxHD falliscono silenziosamente, verificato). **Nuove funzionalità:** opacità per-layer (0-100%) e sfondo trasparente con canale alpha reale in export PNG/WebP (overlay per vMix Titles/Resolume) — durante l'implementazione scoperto e corretto un bug di compositing alpha (`Image.paste` con maschera=se stesso eleva al quadrato l'alpha su destinazione non opaca), fix con `Image.alpha_composite` in nuovo helper `_paste_layer()`. Pillow venv allineato al floor di sicurezza `>=12.1.1`. Build portable + installer rigenerate e testate end-to-end (PyInstaller + Inno Setup + smoke test exe pacchettizzato). Dettaglio: `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md`, `docs/ARCHITETTURA_Live_Video_Composer.md` v1.5.2.
- **6 maggio 2026** — Creato `AGENTS.md` (questo file) e `CLAUDE.md` come entry-point standard 2026 per agenti AI; aggiunto indice `docs/README.md`. Aggiornato `docs/ARCHITETTURA_Live_Video_Composer.md` a v1.5.0 con nuovo blocco changelog: audit pre-vendita chiuso (commit `739b889`) e T-04 LiveWorks App Challenge HMAC opzionale (commit `ebf5513`, allineato con backend WORKS APP T-04 chiuso 24/04/2026). Cursor rules `ecosystem-context`, `doc-sync` aggiornate per puntare a `AGENTS.md`. Nessuna modifica al codice.
- **24 aprile 2026** — T-04 LiveWorks App Challenge HMAC client (commit `ebf5513`): runtime env var `LIVEWORKS_APP_CHALLENGE_SECRET`. Differenza dalle altre 3 desktop: secret runtime invece di compile-time/build-time.
- **15 aprile 2026** — TASK BATCH (`f87b559`): runtime guard Python 3.10+, stack bumpato (Pillow 12.1.1, OpenCV 4.13), thread safety export con snapshot, log rotation, costanti centralizzate, type hints, build pipeline batch hardening (cd /d %~dp0).
- **14 aprile 2026** — Sistema licenze LiveWorks integrato (`6fae96f`): gate Live Works, PyInstaller dual build, Inno Setup upgrade.
- **Aprile 2026** — Audit pre-vendita chiuso (`739b889`): DnD thread safety, fingerprint strict, pending Fernet, `verify_before` enforcement.
- **18 marzo 2026** — Versione 1.4.1: stack Pillow 12, opencv-headless 4.13.

---

**Regola d'oro per tutta la sessione:**

> Prima di scrivere codice nuovo, controlla se esiste un pattern simile in `main.py`. Riusa, non duplicare. Per la zona licenze: ogni modifica al `manager.py` che cambia il contratto API verso `live-works-app.web.app` richiede replica nel backend WORKS APP (`live-software11/live-works-app`). Per Tkinter: thread safety obbligatoria, mai bypassare `root.after(0, ...)` per callback non-GUI.
