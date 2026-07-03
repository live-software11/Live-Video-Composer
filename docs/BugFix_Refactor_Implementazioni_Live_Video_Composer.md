# Live Video Composer — Bug Fix, Refactor e Implementazioni

> File di tracciamento per Bug Fix, Refactor e Implementazioni future. Aggiornare di volta in volta.
> **Ultimo aggiornamento:** 3 Luglio 2026 — Opacità per-layer + sfondo trasparente reale (overlay vMix/Resolume)

---

## Bug Fix

| Data       | Versione | Descrizione                                                                                                                                                                                                              |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-07-03 | v1.5.2   | **Bug di compositing alpha scoperto durante l'implementazione della trasparenza**: `Image.paste(img, box, img)` (immagine come propria maschera) eleva impropriamente al quadrato il canale alpha quando la destinazione non è opaca (verificato: layer opacity 50% su sfondo trasparente dava alpha 25% invece di 50%, e il compositing multi-layer risultava errato). Fix: nuovo helper `_paste_layer()` che usa `Image.alpha_composite` (vera compositing Porter-Duff "over") quando lo sfondo è trasparente; il path veloce con paste diretto resta invariato su sfondo opaco (l'alpha finale viene comunque scartato dal `.convert('RGB')`, nessuna regressione). Testato con layer singoli e multi-layer, round-trip di salvataggio incluso. |
| 2026-07-03 | v1.5.1   | `duplicate_layer()` non propagava `_original_path`: un layer duplicato da un'immagine con working copy ridotta esportava a risoluzione di preview invece che piena. Fix: propagazione esplicita del path originale.       |
| 2026-07-03 | v1.5.1   | DPI export immagine calcolato in UI ma mai scritto nel file: ora `dpi=(x,x)` viene passato realmente a `Image.save()` per JPEG/PNG/BMP (verificato round-trip). Rimossa etichetta "Bit depth" fittizia (nessun formato RGB/JPEG la applicava davvero). |
| 2026-07-03 | v1.5.1   | Preset qualità video (Bassa/Media/Alta con numeri kbps/CRF) non aveva alcun effetto sul file esportato — verificato empiricamente: né `VIDEOWRITER_PROP_QUALITY` né `OPENCV_FFMPEG_WRITER_OPTIONS` (bitrate) influenzano l'encoder di sistema usato da `cv2.VideoWriter` in questo ambiente. Rimossi i numeri fuorvianti dalla UI, etichetta ora onesta. Vero controllo bitrate richiederebbe una pipeline ffmpeg dedicata (fuori scope, valutare separatamente). |
| 2026-04-15 | v1.5.0   | `_clean_and_build.bat`: aggiunto `cd /d "%~dp0"` + verifica `main.py`, controlli `rmdir` se `dist`/`build` bloccati, `python -m pip` e `if errorlevel 1` per evitare build che falliscono silenziosamente con cwd errata |
| 2026-02-11 | v1.3.1   | Fix Drag & Drop nella versione portable (windnd hook ritardato 500ms)                                                                                                                                                    |
| 2026-02-11 | v1.3.1   | Log spostato in `%LOCALAPPDATA%\LiveVideoComposer\` (non più nella cartella exe)                                                                                                                                         |
| 2026-03-18 | v1.4.0   | Guard division-by-zero su output_w/h, fps, img_w/h con `max(1, ...)`                                                                                                                                                     |
| 2026-03-18 | v1.4.0   | Validazione robusta D&D: dimensione file, UnidentifiedImageError                                                                                                                                                         |
| 2026-03-19 | v1.4.1   | Fix label dimensioni hardcoded (L:/A:/W:/H:) → localizzati con `t("size.label_w")` / `t("size.label_h")`                                                                                                                 |
| 2026-04-15 | v1.4.2   | [TASK-004] `load_video` validazione robusta: `isOpened()`, dimensioni >0, primo frame; messaggi granulari codec mancante / cv2.error                                                                                     |
| 2026-04-15 | v1.4.2   | [TASK-005] Export video: rimozione file parziale su cancel, `gc.collect()` in finally, release OpenCV in try/except                                                                                                      |
| 2026-04-15 | v1.4.2   | [TASK-006] Pattern `try/except/finally` unificato negli export: `_stop_export` garantito SEMPRE, `logger.exception` per stack trace                                                                                      |
| 2026-04-15 | v1.4.2   | [TASK-007] Preview scale guard con `max(1e-6, ...)` e `canvas_w/h_safe` per evitare division-by-zero su finestra minimizzata                                                                                             |
| 2026-04-15 | v1.4.2   | [TASK-009] `load_image` con eccezioni PIL granulari (`UnidentifiedImageError`, `DecompressionBombError`, `FileNotFoundError`, `PermissionError`, `OSError`)                                                              |

---

## Refactor

| Data       | Versione | Descrizione                                                                                                                                                               |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-03 | v1.5.2   | **Opacità per-layer** (`ImageLayer.opacity`, 0-100%, slider dedicato nel pannello Trasformazioni) applicata in tutti e tre i path di compositing (preview, export immagine, export video) tramite helper `_apply_opacity()`. **Sfondo trasparente** (`bg_transparent`, toggle nel pannello Sfondo): canale alpha vero preservato nell'export PNG/WebP (JPG/BMP e video restano sempre opachi, appiattiti sul colore sfondo scelto — nessun codec disponibile in questa pipeline supporta l'alpha in video). Caso d'uso: overlay/grafiche trasparenti da usare come Titles in vMix o layer di composizione in Resolume. `duplicate_layer()` propaga anche `opacity`. |
| 2026-07-03 | v1.5.1   | **Codec export video ottimizzati per target player vMix/Resolume Arena** (audit + verifica empirica diretta su `cv2.VideoWriter`, non solo documentazione). MP4: `mp4v` → `avc1` (H.264, fallback automatico a `mp4v` se il sistema non ha il codec) — migliore compressione/compatibilità per distribuzione generale. AVI: `XVID` → `MJPEG` — verificato che HAP/DXV/ProRes/DNxHD **non sono realmente producibili** con questa pipeline OpenCV (i fourcc "riescono" ad aprirsi ma vengono silenziosamente sostituiti con H.264 dal backend Media Foundation di Windows — falso positivo pericoloso, testato e confermato). MJPEG è l'unico codec intra-frame genuino disponibile: seek/scrub/loop istantanei, essenziale per Resolume (documentato: H.264 regge ~3 stream 1080p simultanei vs 6+ con codec intra-frame per lo stutter da long-GOP) e più leggero su CPU in vMix (consenso community: AVI più leggero di MP4/H264). Default formato video cambiato da MP4 ad AVI. Aggiunta label UI che spiega quando usare AVI (vMix/Resolume) vs MP4 (distribuzione/archivio). Nessuna modifica a `.spec`/build: bundlare ffmpeg per HAP/DXV reali resta una decisione separata, valutata e non avviata in questo audit. |
| 2026-02-11 | v1.3.0   | Logging integrato con logger Python (eliminati tutti i `print()`)                                                                                                         |
| 2026-02-11 | v1.3.0   | Gestione errori migliorata nei callback Tkinter                                                                                                                           |
| 2026-02-11 | v1.3.0   | Export GIF ottimizzato con `gc.collect()` e limite 3000 frame                                                                                                             |
| 2026-03-18 | v1.4.0   | Rename LiveVideoComposer, namespace log LiveVideoComposer/                                                                                                                |
| 2026-03-18 | v1.4.0   | `opencv-python` → `opencv-python-headless` (~50MB in meno nella build)                                                                                                    |
| 2026-03-18 | v1.4.0   | WM_DELETE_WINDOW con cleanup risorse e export cancellabile (`_export_cancelled Event`)                                                                                    |
| 2026-03-19 | v1.4.1   | i18n completa: `localization.py` con dizionari it/en, `t()` per tutte le stringhe UI, persistenza lingua in `lang.json`                                                   |
| 2026-04-15 | v1.4.2   | [TASK-001/002/003] Stack bumpato: Python 3.10+ guard, Pillow >=12.1.1,<13 (CVE-2026-25990 + fix 12.1.1), opencv-python-headless >=4.13.0.92                               |
| 2026-04-15 | v1.4.2   | [TASK-008] Snapshot immutabile export (`_build_export_snapshot`, `_create_composite_from_snapshot`): thread-safety contro modifiche concorrenti ai layer durante l'export |
| 2026-04-15 | v1.4.2   | [TASK-010] Progress export video frame-by-frame (`{current}/{total} ({pct}%)`) ogni 10 frame invece di 30                                                                 |
| 2026-04-15 | v1.4.2   | [TASK-011] Magic number centralizzati: `MAX_GIF_FRAMES`, `DOWNSCALE_THRESHOLD`, `DND_SETUP_DELAY_MS`, `DEBOUNCE_NORMAL_MS`, `DEBOUNCE_DRAG_MS`, `PREVIEW_SCALE_MARGIN`    |
| 2026-04-15 | v1.4.2   | [TASK-013] `.spec` PyInstaller: `excludes` estesi (sphinx, tkinter.test, unittest, IPython, notebook); Portable esclude `license/`, Installer lo include con runtime hook |
| 2026-04-15 | v1.4.2   | [TASK-014] Log rotation `RotatingFileHandler` 5MB × 3 backup su `live_video_composer.log`                                                                                 |
| 2026-04-15 | v1.4.2   | [TASK-015] Type hints: `from __future__ import annotations` + annotazioni su `ImageLayer`, `load_image`, `load_video`, `create_composite_image`, `get_transformed_image`  |
| 2026-04-15 | v1.4.2   | [TASK-012] SKIP — `_canvas_persistent_ids` è keyed `{bg,img,border}` non per layer: premessa del task errata, nessun leak da fixare                                       |

### Ottimizzazioni Performance (v1.3.0–v1.4.0)

| #   | Ottimizzazione                                                  | Impatto                                    | Versione |
| --- | --------------------------------------------------------------- | ------------------------------------------ | -------- |
| 1   | Compositing a risoluzione preview (`target_size`)               | 5-10x redraw più veloce                    | v1.3.0   |
| 2   | Debounce sempre attivo (16ms normale, 33ms drag)                | UI fluida, no accumulo eventi              | v1.3.0   |
| 3   | Cache dimensioni canvas (`_cached_canvas_size`)                 | -5-15ms/frame                              | v1.3.0   |
| 4   | Cache zoom per pan (`_zoom_cache`, `_zoom_cache_key`)           | Pan fluido senza resize                    | v1.3.0   |
| 5   | Entry aggiornati solo a fine drag                               | -2-5ms/frame                               | v1.3.0   |
| 6   | Riuso oggetti canvas (`_canvas_persistent_ids`)                 | -1-3ms/frame                               | v1.3.0   |
| 7   | Downscale working copy al caricamento (max 2× output)           | RAM ridotta, velocità                      | v1.4.0   |
| 8   | `fast_mode` NEAREST durante drag                                | 3-4x rotation/resize                       | v1.4.0   |
| 9   | Snapshot export immutabile (thread-safety)                      | No race condition su modifiche concorrenti | v1.4.2   |
| 10  | Rilascio frame ogni 100 + `gc.collect()` su export video lunghi | RAM stabile su export lunghi               | v1.4.2   |

---

## Implementazioni future

<!-- Inserire qui le funzionalità o miglioramenti pianificati -->
