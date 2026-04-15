# Live Video Composer — Bug Fix, Refactor e Implementazioni

> File di tracciamento per Bug Fix, Refactor e Implementazioni future. Aggiornare di volta in volta.
> **Ultimo aggiornamento:** 15 Aprile 2026 — TASK BATCH 2026-04-15 completato

---

## Bug Fix

| Data | Versione | Descrizione |
|------|----------|-------------|
| 2026-02-11 | v1.3.1 | Fix Drag & Drop nella versione portable (windnd hook ritardato 500ms) |
| 2026-02-11 | v1.3.1 | Log spostato in `%LOCALAPPDATA%\LiveVideoComposer\` (non più nella cartella exe) |
| 2026-03-18 | v1.4.0 | Guard division-by-zero su output_w/h, fps, img_w/h con `max(1, ...)` |
| 2026-03-18 | v1.4.0 | Validazione robusta D&D: dimensione file, UnidentifiedImageError |
| 2026-03-19 | v1.4.1 | Fix label dimensioni hardcoded (L:/A:/W:/H:) → localizzati con `t("size.label_w")` / `t("size.label_h")` |
| 2026-04-15 | v1.4.2 | [TASK-004] `load_video` validazione robusta: `isOpened()`, dimensioni >0, primo frame; messaggi granulari codec mancante / cv2.error |
| 2026-04-15 | v1.4.2 | [TASK-005] Export video: rimozione file parziale su cancel, `gc.collect()` in finally, release OpenCV in try/except |
| 2026-04-15 | v1.4.2 | [TASK-006] Pattern `try/except/finally` unificato negli export: `_stop_export` garantito SEMPRE, `logger.exception` per stack trace |
| 2026-04-15 | v1.4.2 | [TASK-007] Preview scale guard con `max(1e-6, ...)` e `canvas_w/h_safe` per evitare division-by-zero su finestra minimizzata |
| 2026-04-15 | v1.4.2 | [TASK-009] `load_image` con eccezioni PIL granulari (`UnidentifiedImageError`, `DecompressionBombError`, `FileNotFoundError`, `PermissionError`, `OSError`) |

---

## Refactor

| Data | Versione | Descrizione |
|------|----------|-------------|
| 2026-02-11 | v1.3.0 | Logging integrato con logger Python (eliminati tutti i `print()`) |
| 2026-02-11 | v1.3.0 | Gestione errori migliorata nei callback Tkinter |
| 2026-02-11 | v1.3.0 | Export GIF ottimizzato con `gc.collect()` e limite 3000 frame |
| 2026-03-18 | v1.4.0 | Rename LiveVideoComposer, namespace log LiveVideoComposer/ |
| 2026-03-18 | v1.4.0 | `opencv-python` → `opencv-python-headless` (~50MB in meno nella build) |
| 2026-03-18 | v1.4.0 | WM_DELETE_WINDOW con cleanup risorse e export cancellabile (`_export_cancelled Event`) |
| 2026-03-19 | v1.4.1 | i18n completa: `localization.py` con dizionari it/en, `t()` per tutte le stringhe UI, persistenza lingua in `lang.json` |
| 2026-04-15 | v1.4.2 | [TASK-001/002/003] Stack bumpato: Python 3.10+ guard, Pillow >=12.1.1,<13 (CVE-2026-25990 + fix 12.1.1), opencv-python-headless >=4.13.0.92 |
| 2026-04-15 | v1.4.2 | [TASK-008] Snapshot immutabile export (`_build_export_snapshot`, `_create_composite_from_snapshot`): thread-safety contro modifiche concorrenti ai layer durante l'export |
| 2026-04-15 | v1.4.2 | [TASK-010] Progress export video frame-by-frame (`{current}/{total} ({pct}%)`) ogni 10 frame invece di 30 |
| 2026-04-15 | v1.4.2 | [TASK-011] Magic number centralizzati: `MAX_GIF_FRAMES`, `DOWNSCALE_THRESHOLD`, `DND_SETUP_DELAY_MS`, `DEBOUNCE_NORMAL_MS`, `DEBOUNCE_DRAG_MS`, `PREVIEW_SCALE_MARGIN` |
| 2026-04-15 | v1.4.2 | [TASK-013] `.spec` PyInstaller: `excludes` estesi (sphinx, tkinter.test, unittest, IPython, notebook); Portable esclude `license/`, Installer lo include con runtime hook |
| 2026-04-15 | v1.4.2 | [TASK-014] Log rotation `RotatingFileHandler` 5MB × 3 backup su `live_video_composer.log` |
| 2026-04-15 | v1.4.2 | [TASK-015] Type hints: `from __future__ import annotations` + annotazioni su `ImageLayer`, `load_image`, `load_video`, `create_composite_image`, `get_transformed_image` |
| 2026-04-15 | v1.4.2 | [TASK-012] SKIP — `_canvas_persistent_ids` è keyed `{bg,img,border}` non per layer: premessa del task errata, nessun leak da fixare |

### Ottimizzazioni Performance (v1.3.0–v1.4.0)

| # | Ottimizzazione | Impatto | Versione |
|---|----------------|---------|----------|
| 1 | Compositing a risoluzione preview (`target_size`) | 5-10x redraw più veloce | v1.3.0 |
| 2 | Debounce sempre attivo (16ms normale, 33ms drag) | UI fluida, no accumulo eventi | v1.3.0 |
| 3 | Cache dimensioni canvas (`_cached_canvas_size`) | -5-15ms/frame | v1.3.0 |
| 4 | Cache zoom per pan (`_zoom_cache`, `_zoom_cache_key`) | Pan fluido senza resize | v1.3.0 |
| 5 | Entry aggiornati solo a fine drag | -2-5ms/frame | v1.3.0 |
| 6 | Riuso oggetti canvas (`_canvas_persistent_ids`) | -1-3ms/frame | v1.3.0 |
| 7 | Downscale working copy al caricamento (max 2× output) | RAM ridotta, velocità | v1.4.0 |
| 8 | `fast_mode` NEAREST durante drag | 3-4x rotation/resize | v1.4.0 |
| 9 | Snapshot export immutabile (thread-safety) | No race condition su modifiche concorrenti | v1.4.2 |
| 10 | Rilascio frame ogni 100 + `gc.collect()` su export video lunghi | RAM stabile su export lunghi | v1.4.2 |

---

## Implementazioni future

<!-- Inserire qui le funzionalità o miglioramenti pianificati -->

