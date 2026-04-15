# Live Video Composer — Documentazione Definitiva

> **Versione:** 1.4.1 — 18/03/2026
> **Scopo:** Documento unico di riferimento per sviluppo, manutenzione e preparazione alla vendita

---

## INDICE

1. [Panoramica e Obiettivo](#1-panoramica-e-obiettivo)
2. [Stack Tecnologico](#2-stack-tecnologico)
3. [Dipendenze e Librerie](#3-dipendenze-e-librerie)
4. [Struttura Progetto e Percorsi](#4-struttura-progetto-e-percorsi)
5. [Diagramma Architetturale](#5-diagramma-architetturale)
6. [Mappa Completa File e Funzioni](#6-mappa-completa-file-e-funzioni)
7. [Data Model](#7-data-model)
8. [Logica di Rendering e Compositing](#8-logica-di-rendering-e-compositing)
9. [Flusso di Export](#9-flusso-di-export)
10. [Drag & Drop](#10-drag--drop)
11. [Vincoli e Regole](#11-vincoli-e-regole)
12. [Comandi Build e Workflow](#12-comandi-build-e-workflow)
13. [Ottimizzazioni Implementate](#13-ottimizzazioni-implementate)
14. [Changelog](#14-changelog)

---

## 1. PANORAMICA E OBIETTIVO

**Live Video Composer** è un'applicazione desktop **Python/Tkinter** per la creazione di collage multi-layer con immagini e video. L'utente trascina file, applica trasformazioni e esporta a risoluzioni professionali.

**Funzionalità principali:**

- **Multi-Layer Collage** — immagini sovrapposte con ordine modificabile
- **Trasformazioni** — zoom 1-1000%, rotazione -180/+180°, flip H/V, posizione pixel-perfect
- **Handle visivi** — ridimensiona e ruota con handle stile PowerPoint
- **Export immagine** — JPG, PNG, WebP, BMP con preset qualità (Bassa/Media/Alta)
- **Export video** — MP4, AVI, WebM, GIF animata con preset bitrate/CRF

**Target utente:** Content creator, social media manager, tecnici AV per eventi live.

### Flusso Utente

```
┌───────────────────────────────────────────────────────────┐
│                 LIVE VIDEO COMPOSER                         │
│                                                             │
│  ┌──────────────────┐   ┌────────────────────────────────┐ │
│  │  PANNELLO SINISTRO│   │       CANVAS PREVIEW           │ │
│  │                    │   │                                │ │
│  │  [Layers]          │   │   Anteprima composizione      │ │
│  │  [Trasformazioni]  │   │   (zoom, rotazione, posizione) │ │
│  │  [Dimensioni]      │   │   Handle selezione             │ │
│  │  [Adattamento]     │   │                                │ │
│  │  [Specchio]        │   │                                │ │
│  └──────────────────┘   └────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────┐   ┌────────────────────────────────┐ │
│  │  PANNELLO DESTRO │   │   Output: preset risoluzione    │ │
│  │  [Dimensioni]     │   │   Sfondo, Export Immagine/Video │ │
│  │  [Sfondo]         │   │   Progress + Annulla Export    │ │
│  │  [Export]         │   │                                │ │
│  └──────────────────┘   └────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## 2. STACK TECNOLOGICO

| Tecnologia       | Versione                           | Ruolo                                                 |
| ---------------- | ---------------------------------- | ----------------------------------------------------- |
| **Python**       | 3.10+ (testato 3.13)               | Runtime — Pillow 12 richiede >=3.10                   |
| **Tkinter**      | stdlib                             | GUI                                                   |
| **Pillow (PIL)** | >=12.1.1,<13                       | Elaborazione immagini (12.1.1 security fix)           |
| **OpenCV**       | opencv-python-headless >=4.13.0.92 | Elaborazione video                                    |
| **numpy**        | >=1.26.0                           | Array per video                                       |
| **windnd**       | >=1.0.7                            | Drag & drop nativo Windows                            |
| **PyInstaller**  | >=6.11                             | Build eseguibile                                      |
| **Inno Setup**   | 6                                  | Installer Windows                                     |
| **requests**     | >=2.32.0                           | HTTP client sistema licenze (solo installer build)    |
| **cryptography** | >=44.0.0                           | Storage licenza cifrato Fernet (solo installer build) |
| **wmi**          | >=1.5.1                            | Fingerprint hardware Windows (solo installer build)   |

### Linguaggi e LOC

| Linguaggio | Dove       | LOC appross.               |
| ---------- | ---------- | -------------------------- |
| **Python** | `main.py`  | ~2790                      |
| **Python** | `license/` | ~790 (modulo gate licenze) |

---

## 3. DIPENDENZE E LIBRERIE

### requirements.txt

| Pacchetto              | Versione     | Funzione                                          |
| ---------------------- | ------------ | ------------------------------------------------- |
| Pillow                 | >=12.1.1,<13 | Immagini, resize, composite (12.1.1 security fix) |
| opencv-python-headless | >=4.13.0.92  | Video capture, export MP4/GIF                     |
| numpy                  | >=1.26.0     | Array per cv2                                     |
| windnd                 | >=1.0.7      | Drag & drop (hook Python)                         |
| tkinterdnd2            | >=0.4.3      | Fallback D&D (opzionale)                          |
| requests               | >=2.32.0     | HTTP client API Live Works (solo installer build) |
| cryptography           | >=44.0.0     | Storage licenza cifrato (solo installer build)    |
| wmi                    | >=1.5.1      | Fingerprint hardware (solo installer build)       |

**Nota:** `opencv-python-headless` espone `cv2` con la stessa API di `opencv-python`, ma ~50MB in meno e nessuna dipendenza Qt.

---

## 4. STRUTTURA PROGETTO E PERCORSI

```
Live video composer/
├── main.py                    — Sorgente unico (~2340 righe)
├── localization.py            — Dizionari i18n (it/en), funzione t()
├── requirements.txt
├── Live_Video_Composer.spec           — PyInstaller onedir (installer)
├── Live_Video_Composer_Portable.spec  — PyInstaller onefile (portable)
├── installer.iss              — Inno Setup (v1.4.1, WizardStyle=modern)
├── icon.ico                   — Icona applicazione
├── icons/                     — Icona sorgente (per scripts/create-icon.py)
├── installer-wizard.bmp       — Grafica wizard Inno (164×314, stile broadcast)
├── installer-wizard-small.bmp — Grafica wizard Inno (55×58)
├── scripts/
│   ├── create-icon.py         — Genera icon.ico da logo
│   └── create-installer-wizard.py — Genera BMP wizard (stile dark)
├── _clean_and_build.bat       — Build completa
├── _build_setup.bat           — Solo setup (richiede dist/)
├── build_exe.py               — Script build interattivo
├── .cursor/
│   └── rules/
│       ├── project.mdc
│       ├── doc-sync.mdc
│       ├── build.mdc
│       ├── main-py.mdc
│       ├── git-autonomy.mdc
│       ├── i18n-installer.mdc
│       └── installer-modern.mdc
├── docs/
│   ├── ARCHITETTURA_Live_Video_Composer.md  — QUESTO FILE
│   ├── Istruzioni_Progetto_Claude_Live_Video_Composer.md
│   ├── Primo_Prompt_Avvio_Chat_Claude_Desktop_Live_Video_Composer.md
│   ├── BugFix_Refactor_Implementazioni_Live_Video_Composer.md
│   └── README.md              — Documento vendita IT/EN
├── release/                   — Output build (gitignore)
├── dist/                      — Output PyInstaller (gitignore)
├── build/                     — Cache PyInstaller (gitignore)
└── README.md                  — README progetto (GitHub)
```

### Percorsi eseguibile

| Tipo                | Percorso                                                   |
| ------------------- | ---------------------------------------------------------- |
| **Exe portable**    | `release/Live_Video_Composer_Portable.exe`                 |
| **Setup installer** | `release/Live_Video_Composer_Setup.exe`                    |
| **Log**             | `%LOCALAPPDATA%\LiveVideoComposer\live_video_composer.log` |

---

## 5. DIAGRAMMA ARCHITETTURALE

```
┌─────────────────────────────────────────────────────────────┐
│                  LIVE VIDEO COMPOSER (Tkinter)                │
│                                                               │
│  ┌──────────────────┐  ┌─────────────────────────────────┐  │
│  │  PANNELLO SINISTRO│  │     CANVAS (tk.Canvas)           │  │
│  │  Layers listbox   │  │  create_composite_image()        │  │
│  │  Trasformazioni   │  │  target_size preview            │  │
│  │  Zoom, Rotazione  │  │  _canvas_persistent_ids          │  │
│  │  Pan, Tilt        │  │  debounce 16/33ms                │  │
│  │  Adattamento      │  │  fast_mode durante drag          │  │
│  └────────┬──────────┘  └──────────────▲──────────────────┘  │
│           │                            │                       │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │            ImageLayer[] (PIL.Image, cache, _original_path) │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                                                   │
│  ┌────────▼──────────┐  ┌─────────────────────────────────┐   │
│  │  windnd D&D       │  │  Export (thread)               │   │
│  │  _process_dropped │  │  _do_export_image/video        │   │
│  │  load_image/video │  │  _export_cancelled Event        │   │
│  └──────────────────┘  └────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. MAPPA COMPLETA FILE E FUNZIONI

### main.py — Struttura

| Sezione                    | Righe     | Contenuto                                                                |
| -------------------------- | --------- | ------------------------------------------------------------------------ |
| Imports, logging, costanti | 1-77      | \_get_log_path, logger, IMAGE_FORMATS, VIDEO_FORMATS, RESOLUTION_PRESETS |
| ImageLayer                 | 80-183    | **slots**, get_transformed_image, invalidate_cache, cleanup              |
| LiveVideoComposer.**init** | 185-260   | Stato, setup_style, create_widgets, setup_bindings, setup_drag_and_drop  |
| setup_style                | 261-378   | Tema dark blue, palette, stili ttk                                       |
| create_widgets             | 380-771   | create_left_panel, create_canvas_panel, create_right_panel               |
| setup_drag_and_drop        | 810-920   | windnd, tkinterdnd2 fallback, \_process_dropped_files                    |
| load_image, load_video     | 1080-1235 | Downscale working copy, \_original_path                                  |
| Layer management           | 1237-1420 | add, remove, move, duplicate, fit\_\*                                    |
| Trasformazioni             | 1420-1495 | zoom, rotation, position, flip                                           |
| Canvas rendering           | 1545-1750 | get_layer_bounds, create_composite_image, \_redraw_canvas_internal       |
| Mouse/Keyboard             | 1750-2070 | on_mouse_down/move/up, on_closing                                        |
| Export                     | 2095-2410 | export*image/video, \_do_export*\*, \_process_video_frame_optimized      |
| main()                     | 2420-2435 | Entry point                                                              |

### Funzioni chiave

| Funzione                                                              | Descrizione                                                                |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `ImageLayer.get_transformed_image(use_cache, zoom, fast_mode)`        | Restituisce immagine trasformata. fast_mode=True usa NEAREST (drag).       |
| `create_composite_image(output_w, output_h, for_export, target_size)` | Composita tutti i layer. target_size per preview, for_export per LANCZOS.  |
| `load_image(filepath)`                                                | Carica immagine, downscale se >2× output, salva \_original_path.           |
| `_do_export_image(filepath)`                                          | Ricarica originali da \_original_path, composita, salva, ripristina.       |
| `_process_dropped_files(files)`                                       | Valida dimensione/formato, chiama load_image/load_video.                   |
| `on_closing()`                                                        | WM_DELETE_WINDOW: \_export_cancelled.set(), cleanup layer, root.destroy(). |

---

## 7. DATA MODEL

### ImageLayer

```python
__slots__ = [
    'id', 'original_image', 'name',
    'offset_x', 'offset_y', 'zoom', 'rotation', 'flip_h', 'flip_v',
    'is_video', 'video_path', 'video_fps', 'video_frames',
    'bounds_in_canvas',
    '_cache', '_cache_key',           # Cache rotation+flip
    '_zoom_cache', '_zoom_cache_key',  # Cache zoom per pan
    '_original_path'                   # Path originale per export (downscale)
]
```

### LiveVideoComposer (stato principale)

- **Layer:** `layers: list[ImageLayer]`, `selected_layer: ImageLayer | None`
- **Output:** `output_width`, `output_height`, `bg_color_var`
- **Preview:** `_cached_canvas_size`, `_canvas_persistent_ids`, `preview_scale`
- **Debounce:** `_redraw_job`, `_resize_job`
- **Export:** `_export_cancelled: threading.Event`, `progress`, `cancel_btn`

### RESOLUTION_PRESETS

Full HD, HD, 4K, Verticale 9:16, Quadrato, Banner, Twitter Header, Facebook Cover, YouTube Thumbnail, Instagram Landscape, 4:3.

---

## 8. LOGICA DI RENDERING E COMPOSITING

### Compositing preview

1. `_redraw_canvas_internal()` ottiene `canvas_w`, `canvas_h` da `_cached_canvas_size`
2. `preview_scale = min(canvas_w/output_w, canvas_h/output_h) * 0.9`
3. `preview_w`, `preview_h` = dimensioni preview
4. `create_composite_image(..., target_size=(preview_w, preview_h))` — composita direttamente a risoluzione preview
5. Durante drag: `get_transformed_image(..., fast_mode=True)` — NEAREST

### Compositing export

1. `create_composite_image(..., for_export=True)` — LANCZOS, risoluzione piena
2. Per layer con `_original_path`: ricarica da disco, sostituisce temporaneamente, composita, ripristina in finally

### Downscale working copy

- Condizione: `img_w > output_w*2 or img_h > output_h*2`
- Scala: `min(max_working_w/img_w, max_working_h/img_h)`
- `_original_path = filepath` per reload in export

---

## 9. FLUSSO DI EXPORT

### Export immagine

```
export_image() → _start_export() → Thread: _do_export_image()
  → Per ogni layer con _original_path: Image.open(), sostituisci original_image
  → create_composite_image(..., for_export=True)
  → Salva (JPEG/PNG/WebP)
  → finally: ripristina working copy, gc.collect
  → _stop_export()
```

### Export video

```
export_video() → _start_export() → Thread: _do_export_video()
  → cv2.VideoCapture, cv2.VideoWriter (o loop GIF)
  → Ogni N frame: controlla _export_cancelled.is_set()
  → _process_video_frame_optimized() per ogni frame
  → finally: cap.release(), out.release()
  → _stop_export()
```

### Export cancellabile

- `cancel_export()` → `_export_cancelled.set()` → `_stop_export()`
- Loop video/GIF: `if self._export_cancelled.is_set(): break`

---

## 10. DRAG & DROP

### windnd (preferito)

- Hook Python sulla finestra root — funziona con --onefile (nessuna DLL nativa)
- Setup ritardato 500ms: `root.after(500, _do_setup_drag_and_drop)`
- `_on_drop_windnd(files)` decodifica bytes (utf-8/cp1252), chiama `_process_dropped_files`

### Validazione \_process_dropped_files

- File esistente, estensione in IMAGE_FORMATS/VIDEO_FORMATS
- Dimensione: warning se >500MB (immagine) o >4GB (video)
- Formato non supportato: messagebox con elenco formati
- UnidentifiedImageError: messaggio utente chiaro

### Vincolo critico

**MAI** subclassing Win32 WNDPROC (SetWindowLongPtrW) — crasha Tkinter.

---

## 11. VINCOLI E REGOLE

1. **windnd** — Hook Python, collect_all('windnd') obbligatorio in spec
2. **Setup D&D 500ms** — root.after(500, ...)
3. **Log %LOCALAPPDATA%** — Mai nella cartella exe
4. **Export in thread** — \_start_export, \_stop_export, root.after(0, ...) per GUI
5. **cv2.VideoCapture** — Sempre cap.release() nel finally
6. **GIF max 3000 frame** — Limite memoria
7. **Division-by-zero** — max(1, output_w/h), max(1, fps), max(1, img_w/h)
8. **python -m PyInstaller** — Non pyinstaller diretto
9. **opencv-python-headless** — Preferire a opencv-python
10. **i18n** — Ogni stringa UI via `t("chiave")` da `localization.py`. Dizionari `_TRANSLATIONS["it"]` e `_TRANSLATIONS["en"]` (~116 chiavi flat con prefisso: app., layers., btn., transform., size., fit., mirror., canvas., output., export., preset., status., error., layer., menu.). Placeholder `{0}`, `{1}` (str.format). Primo avvio in inglese (`_CURRENT_LANG = "en"`). Lingua salvata in `%LOCALAPPDATA%\LiveVideoComposer\lang.json`. Toggle IT/EN in header (cyan attivo, blu scuro inattivo). Terminologia EN professionale video/AV. Installer Inno Setup in inglese.

---

## 12. COMANDI BUILD E WORKFLOW

```powershell
python main.py                         # Avvio sviluppo
python -m pip install -r requirements.txt   # Dipendenze (stesso interpreter)

# Build
python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean       # Installer (onedir)
python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean  # Portable (onefile)

# Build completa (doppio click)
_clean_and_build.bat              # clean + installer + portable + Inno Setup
```

**Nota batch (IT):** `_clean_and_build.bat` esegue `cd /d "%~dp0"` all'avvio così la build funziona anche da collegamento, da prompt con directory diversa o dopo "Esegui come amministratore" (altrimenti la cwd poteva essere `System32` e PyInstaller non trovava `main.py` / `license` / `requirements.txt`). Controlli su `rmdir dist`/`build` se file in uso, dipendenze con `python -m pip`, esito PyInstaller/Inno con `if errorlevel 1`.

**Batch note (EN):** `_clean_and_build.bat` runs `cd /d "%~dp0"` at start so the full build works from shortcuts, a shell opened in another folder, or after "Run as administrator" (otherwise the working directory could be `System32` and PyInstaller would not find `main.py`, `license/`, or `requirements.txt`). It also validates removal of `dist`/`build` when files are locked, uses `python -m pip` for installs, and uses `if errorlevel 1` after PyInstaller/Inno Setup.

### Output

| File     | Percorso                                   |
| -------- | ------------------------------------------ |
| Portable | `release/Live_Video_Composer_Portable.exe` |
| Setup    | `release/Live_Video_Composer_Setup.exe`    |

---

## 13. OTTIMIZZAZIONI IMPLEMENTATE

| #   | Ottimizzazione                  | Impatto              |
| --- | ------------------------------- | -------------------- |
| 1   | Compositing target_size preview | 5-10x redraw         |
| 2   | Debounce 16/33ms (mai bypass)   | UI fluida            |
| 3   | \_cached_canvas_size            | -5-15ms/frame        |
| 4   | Cache zoom (\_zoom_cache)       | Pan fluido           |
| 5   | \_canvas_persistent_ids         | -1-3ms/frame         |
| 6   | Downscale working copy          | RAM, velocità        |
| 7   | fast_mode NEAREST durante drag  | 3-4x rotation/resize |
| 8   | opencv-python-headless          | ~50MB build in meno  |

Dettaglio storico in `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md`.

---

## 14. CHANGELOG

### v1.4.2 (2026-04-15) — TASK BATCH 2026-04-15

- **Runtime** — Guard `sys.version_info < (3, 10)` in cima a `main.py`; stack bumpato a Pillow >=12.1.1,<13 (CVE-2026-25990 + fix 12.1.1) e opencv-python-headless >=4.13.0.92.
- **Stabilità export** — `_do_export_video` pulisce file parziale su cancel, `gc.collect()` in finally, release OpenCV in try/except, `_stop_export` SEMPRE in finally (anche su eccezione). Stesso pattern applicato a `_do_export_image`.
- **Thread safety export** — Introdotto `_build_export_snapshot()` + `_create_composite_from_snapshot()`: l'export legge parametri congelati all'avvio, modifiche concorrenti ai layer non corrompono l'output (TASK-008).
- **load_video robusto** — Controlli `isOpened()`, dimensioni >0, primo frame; messaggi granulari per codec mancante / dimensioni invalide / errore cv2.
- **load_image** — Eccezioni PIL granulari (`UnidentifiedImageError`, `DecompressionBombError`, `FileNotFoundError`, `PermissionError`, `OSError`) con i18n dedicate.
- **Preview scale guard** — `max(1e-6, ...)` e `canvas_w/h_safe` per evitare division-by-zero su finestra minimizzata.
- **Progress video** — Label frame-by-frame (`{current}/{total} ({pct}%)`) ogni 10 frame invece di ogni 30.
- **Log rotation** — `RotatingFileHandler` 5MB × 3 backup su `live_video_composer.log`.
- **Magic numbers** — Costanti centralizzate: `MAX_GIF_FRAMES=3000`, `DOWNSCALE_THRESHOLD=2.0`, `DND_SETUP_DELAY_MS=500`, `DEBOUNCE_NORMAL_MS=16`, `DEBOUNCE_DRAG_MS=33`, `PREVIEW_SCALE_MARGIN=0.9`.
- **Type hints** — `from __future__ import annotations` + annotazioni su `ImageLayer`, `load_image`, `load_video`, `create_composite_image`, `get_transformed_image`.
- **PyInstaller** — `.spec` Installer e Portable: `excludes` estesi (sphinx, tkinter.test, unittest, IPython, notebook); Portable esclude esplicitamente il modulo `license` e le sue dipendenze runtime; Installer mantiene `collect_all('windnd')` e include il modulo `license` con runtime hook.
- **Build script** — `_clean_and_build.bat`: `cd /d "%~dp0"`, verifica presenza `main.py`, uscita controllata se `dist`/`build` non eliminabili, `python -m pip`, `if errorlevel 1` dopo PyInstaller e Inno Setup (fix cwd errata e errorlevel in batch).
- **i18n** — Aggiunte 10 chiavi in IT/EN: `error.image_unsupported`, `error.image_too_large`, `error.image_not_found`, `error.image_permission`, `error.image_io`, `error.video_cannot_open`, `error.video_codec_missing`, `error.video_invalid_dimensions`, `error.video_cv2`, `export_video_progress_frames`.

### v1.4.1 (2026-03-18)

- **Stack aggiornato** — Python 3.10+ (Pillow 12 richiede), Pillow >=12.1.1,<13 (CVE-2026-25990 + security fix 12.1.1), opencv-python-headless >=4.13.0.92, numpy >=1.26.0, tkinterdnd2 >=0.4.3, PyInstaller >=6.11. Runtime: `requests >=2.32`, `cryptography >=44`, `wmi >=1.5` per sistema licenze (solo installer).
- **Documentazione** — README, ARCHITETTURA, System_Prompt, Cursor rules allineate

### v1.4.0 (2026-03-18)

- Rename LiveVideoComposer, log LiveVideoComposer/
- Downscale working copy, \_original_path, reload export
- fast_mode NEAREST durante drag
- opencv-python-headless
- WM_DELETE_WINDOW, export cancellabile
- Validazione D&D, guard division-by-zero

### v1.3.1 (2026-02-11)

- Fix D&D portable, log %LOCALAPPDATA%, build scripts

### v1.3.0 (2026-02-11)

- Logging, gestione errori, export GIF ottimizzato, cursor rules
