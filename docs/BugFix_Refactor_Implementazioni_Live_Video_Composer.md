# Live Video Composer — Bug Fix, Refactor e Implementazioni

> File di tracciamento per Bug Fix, Refactor e Implementazioni future. Aggiornare di volta in volta.
> **Ultimo aggiornamento:** 19 Marzo 2026

---

## Bug Fix

| Data | Versione | Descrizione |
|------|----------|-------------|
| 2026-02-11 | v1.3.1 | Fix Drag & Drop nella versione portable (windnd hook ritardato 500ms) |
| 2026-02-11 | v1.3.1 | Log spostato in `%LOCALAPPDATA%\LiveVideoComposer\` (non più nella cartella exe) |
| 2026-03-18 | v1.4.0 | Guard division-by-zero su output_w/h, fps, img_w/h con `max(1, ...)` |
| 2026-03-18 | v1.4.0 | Validazione robusta D&D: dimensione file, UnidentifiedImageError |
| 2026-03-19 | v1.4.1 | Fix label dimensioni hardcoded (L:/A:/W:/H:) → localizzati con `t("size.label_w")` / `t("size.label_h")` |

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

---

## Implementazioni future

<!-- Inserire qui le funzionalità o miglioramenti pianificati -->

