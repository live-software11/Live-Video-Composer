# TASK BATCH — Live Video Composer

> **Data:** 15 Aprile 2026
> **Versione progetto attuale:** v1.4.1
> **Prodotto da:** Senior Software Architect (Claude Desktop)
> **Destinatario esecutore:** Cursor Composer (operaio AI)
> **Base analisi:** `docs/ARCHITETTURA_Live_Video_Composer.md`, `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md`, `docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md`, `requirements.txt`, verifica CVE/versioni via PyPI (aprile 2026)

---

## 🟩 STATO ESECUZIONE — CHIUSO 15/04/2026 (Claude Code)

**Stato finale:** 14/15 task eseguiti, 1 SKIP motivato. Batch **chiuso**.

**✅ COMPLETATI (14 task):**

| # | Task | File toccati | Note |
|---|---|---|---|
| 001 | Python 3.10+ guard | `main.py`, `requirements.txt`, docs | `sys.exit` se <3.10 |
| 002 | Pillow >=12.1.1,<13 | `requirements.txt`, docs | Security fix 12.1.1 |
| 003 | opencv-python-headless >=4.13.0.92 | `requirements.txt`, docs | — |
| 004 | `load_video` robusto | `main.py`, `localization.py` | `isOpened`, dims, codec msg, cv2.error |
| 005 | Export video cancel cleanup | `main.py` | Flag `cancelled`, rimozione file parziale, gc.collect |
| 006 | Pattern try/except/finally unificato | `main.py` | `_stop_export` SEMPRE + `logger.exception` |
| 007 | Preview scale guard | `main.py` | Floor `1e-6`, `canvas_w/h_safe` |
| 008 | Snapshot immutabile export | `main.py` | `_build_export_snapshot`, `_create_composite_from_snapshot` |
| 009 | Eccezioni PIL granulari | `main.py`, `localization.py` | 5 exception types distinti |
| 010 | Progress video frame-by-frame | `main.py`, `localization.py` | `{current}/{total} ({pct}%)` |
| 011 | Magic number centralizzati | `main.py` | 6 costanti operative applicate ovunque |
| 013 | PyInstaller spec hardening | `.spec` x2 | Excludes estesi, license split installer/portable |
| 014 | Log rotation 5MB×3 | `main.py` | `RotatingFileHandler` |
| 015 | Type hints core APIs | `main.py` | `from __future__`, ImageLayer + load_* |

**⏭️ SKIP motivato:**
- **TASK-012** — `_canvas_persistent_ids` è `{bg, img, border}`, **non** indicizzato per layer. Premessa errata: nessun leak da fixare. `remove_selected_layer` già invoca `layer.cleanup()`. Registrato in `docs/BugFix_Refactor_*.md`.

**📝 DOCUMENTAZIONE SINCRONIZZATA:**
- ✅ `docs/ARCHITETTURA_Live_Video_Composer.md` sez. 2+3 (stack/dipendenze) + sez. 14 (changelog v1.4.2 con tutti i task)
- ✅ `docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md` sez. Stack (Python 3.10+, Pillow 12.1.1, OpenCV 4.13)
- ✅ `docs/README.md` (Python 3.10+ in IT e EN)
- ✅ `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md` — entry per ogni task TASK-001..015, ottimizzazioni #9 e #10 aggiunte
- `README.md` root: nessun riferimento versione da aggiornare

**🔒 VINCOLI SACRI RISPETTATI:**
- #1 `windnd` hook Python — OK (invariato)
- #2 `collect_all('windnd')` in entrambi gli spec — OK
- #3 Setup D&D ritardato `DND_SETUP_DELAY_MS` (500ms) — OK
- #4 Log in `%LOCALAPPDATA%\LiveVideoComposer\` — OK + rotation attiva
- #5 Export in thread con `_start_export`/`_stop_export` + `root.after(0, ...)` — OK
- #6 `cv2.VideoCapture.release()` sempre nel `finally` — OK + try/except
- #7 GIF max `MAX_GIF_FRAMES` (3000) — OK
- #8 `max(1, ...)` su output/fps/img_w/h — OK (esteso a preview_scale)
- #9 `python -m PyInstaller` — OK (invariato)
- #10 `opencv-python-headless` — OK (bumpato a 4.13.0.92)
- #11 i18n IT+EN — OK (10 nuove chiavi in entrambe le lingue)

**🧪 VALIDAZIONE ESEGUITA IN-SESSIONE:**
- `ast.parse(main.py)` → OK
- `ast.parse(localization.py)` → OK
- `import main` su Python 3.13 → OK, tutte le costanti esposte
- Chiavi i18n verificate presenti in `it` e `en`
- Type hints visibili via `__annotations__`

**📋 CHECKLIST MANUALE RESIDUA (da eseguire localmente):**
- [ ] `pip install -r requirements.txt --upgrade` → Pillow 12.1.1+, OpenCV 4.13+
- [ ] `python main.py` smoke test — avvio, D&D immagine+video, transform, export JPG, export MP4 breve, cancel export
- [ ] `_clean_and_build.bat` → portable + installer OK; confronta dimensione Portable vs v1.4.1 (attesa riduzione 10-30 MB)
- [ ] Test `release/Live_Video_Composer_Portable.exe` (D&D + export)
- [ ] Test `release/Live_Video_Composer_Setup_*.exe` (gate licenza + export)
- [ ] Verifica `%LOCALAPPDATA%\LiveVideoComposer\live_video_composer.log` → rotation funzionante
- [ ] Commit atomico: `git commit -m "[v1.4.2] TASK_BATCH_2026-04-15: runtime hardening, export thread-safety, i18n errors"`
- [ ] Archiviare questo file in `docs/archive/` o rimuoverlo

---

---

## ⚠️ NOTA IMPORTANTE PER L'OPERAIO

Alcuni task richiedono l'ispezione di `main.py` per verificare lo stato corrente del codice prima della modifica. In questi casi il task indica esplicitamente *"Verificare stato attuale prima di procedere"*. Se un controllo rivela che il fix è **già presente**, marcare il task come `SKIP — già implementato` nel commit message e passare al successivo.

**Vincoli sacri (riepilogo — MAI violare):**
1. `windnd` hook Python — MAI subclassing Win32 WNDPROC
2. `collect_all('windnd')` in entrambi gli spec PyInstaller
3. Setup D&D ritardato 500ms
4. Log in `%LOCALAPPDATA%\LiveVideoComposer\`
5. Export in thread con `_start_export` / `_stop_export` + `root.after(0, ...)`
6. `cv2.VideoCapture.release()` sempre nel `finally`
7. GIF max 3000 frame
8. `max(1, ...)` per output_w/h, fps, img_w/h
9. `python -m PyInstaller` (non `pyinstaller` diretto)
10. `opencv-python-headless` (non `opencv-python`)
11. i18n: ogni modifica stringhe UI in `localization.py` per **entrambe** le lingue (it/en)

---

## 📋 INDICE TASK

### 🔴 PRIORITÀ ALTA
- ✅ [TASK-001] REFACTOR — Aggiornamento requirements.txt: Python 3.10+ (Pillow 12 drop 3.9) — **FATTO (codice + docs sync)**
- ✅ [TASK-002] BUG FIX — Pillow 12.1.1 security fix (CVE-2026-25990) — **FATTO (codice + docs sync)**
- ✅ [TASK-003] REFACTOR — Bump opencv-python-headless >=4.13.0.92 — **FATTO (codice + docs sync)**
- ✅ [TASK-004] BUG FIX — Validazione robusta `load_video` (file corrotti, codec mancante) — **FATTO**
- ✅ [TASK-005] BUG FIX — Memory leak potenziale in `_do_export_video` (frame non rilasciati su cancel) — **FATTO**
- ✅ [TASK-006] REFACTOR — Pattern `try/except/finally` unificato negli export thread — **FATTO**

### 🟡 PRIORITÀ MEDIA
- ✅ [TASK-007] BUG FIX — Guard `max(1, ...)` su tutti i calcoli preview_scale — **FATTO**
- ✅ [TASK-008] FEATURE — Snapshot immutabile dei layer prima dell'export (thread safety) — **FATTO (`_build_export_snapshot`, `_create_composite_from_snapshot`)**
- ✅ [TASK-009] REFACTOR — Eccezioni PIL granulari in `load_image` — **FATTO (5 exception types + 5 chiavi i18n)**
- ✅ [TASK-010] FEATURE — Progress percentuale export video — **FATTO (label `{current}/{total} ({pct}%)`)**
- ✅ [TASK-011] REFACTOR — Centralizzare costanti magic number — **FATTO (6 costanti, sostituzione sistematica)**
- ⏭️ [TASK-012] BUG FIX — `_canvas_persistent_ids` cleanup su rimozione layer — **SKIP — premessa errata (dict `{bg,img,border}` NON keyed per layer)**
- ✅ [TASK-013] REFACTOR — `.spec` PyInstaller: `collect_all('windnd')` + `exclude` moduli pesanti — **FATTO (entrambi gli spec, license split installer/portable)**

### 🟢 PRIORITÀ BASSA (quando possibile)
- ✅ [TASK-014] FEATURE — Log rotation su `live_video_composer.log` (max 5MB × 3 file) — **FATTO**
- ✅ [TASK-015] REFACTOR — Type hints completi su `ImageLayer` e funzioni core — **FATTO (`from __future__ import annotations` + annotazioni)**

---

## 🔴 TASK PRIORITÀ ALTA

### [TASK-001] REFACTOR: Aggiornamento requirements.txt per Python 3.10+

**FILE:** `requirements.txt`, `README.md`, `docs/ARCHITETTURA_Live_Video_Composer.md`, `docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md`

**PROBLEMA:**
`requirements.txt` e documentazione dichiarano "Python 3.9+ richiesto per Pillow 12". **FALSO**: Pillow 12.0.0 (2025-10-15) e successive richiedono **Python >=3.10** (verificato su PyPI 15/04/2026). Installare Pillow 12.x su Python 3.9 fallisce con `ERROR: Package 'pillow' requires a different Python`.

**SOLUZIONE:**
1. In `requirements.txt`:
   - Cambiare commento `# Python 3.9+ richiesto` → `# Python 3.10+ richiesto (Pillow 12 ha droppato 3.9)`
2. In `README.md`: aggiornare riga "Python: 3.9+" → "Python: 3.10+"
3. In `docs/ARCHITETTURA_Live_Video_Composer.md`, tabella Stack Tecnologico: `Python | 3.9+` → `Python | 3.10+ (testato 3.13)`
4. In `docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md`: aggiornare sezione Stack
5. In `localization.py` (se presente un eventuale errore di avvio per versione Python): aggiungere chiave `error.python_version = "Python 3.10 or higher required"` + versione IT
6. In `main.py` (in cima, subito dopo gli import `sys`): aggiungere guard:
   ```python
   if sys.version_info < (3, 10):
       sys.exit("Python 3.10+ required (current: %s)" % sys.version)
   ```

**VINCOLI:**
- Non modificare `.spec` PyInstaller (il bundle ha il suo Python interno)
- Aggiornare entrambe le lingue in `localization.py`

**TEST:**
- `python --version` → verifica 3.10+
- `python main.py` → avvio OK
- Se disponibile, `python3.9 main.py` → deve uscire con messaggio chiaro

---

### [TASK-002] BUG FIX: Bump Pillow a >=12.1.1 per fix di sicurezza

**FILE:** `requirements.txt`

**SINTOMO:**
Il progetto dichiara `Pillow>=12.1.0`. Pillow **12.1.1** (2026-02-11) contiene fix di sicurezza (sezione "Security" nelle release notes). `docs/ARCHITETTURA_Live_Video_Composer.md` menziona "CVE-2026-25990" come motivo del bump, ma il constraint attuale `>=12.1.0` permette ancora l'installazione della versione vulnerabile.

**CAUSA ROOT:**
Il vincolo `>=12.1.0` non esclude 12.1.0 che è vulnerabile. Va alzato a `>=12.1.1`.

**FIX:**
In `requirements.txt`:
```diff
- Pillow>=12.1.0
+ Pillow>=12.1.1  # 12.1.1 contiene fix di sicurezza (vedi release notes 2026-02-11)
```

Considerazione aggiuntiva: la versione stabile più recente è **Pillow 12.2.0** (2026-04-01). Se non ci sono breaking change relativi a `Image.open`, `Image.resize`, `ImageOps`, `Image.ROTATE_*`, si può puntare a `>=12.1.1,<13`. Verificare le release notes 12.2.0 prima di bumpare oltre 12.1.1.

**VINCOLI:**
- Non rimuovere il constraint `<13` (per evitare breaking change Pillow 13 futuro)
- Aggiornare anche `docs/ARCHITETTURA_Live_Video_Composer.md` sezione 3 e 14 (changelog)

**TEST:**
- `pip install -r requirements.txt --upgrade` → installa 12.1.1 o 12.2.0
- `python main.py` → carica immagine JPG/PNG/WebP, export OK

---

### [TASK-003] REFACTOR: Bump opencv-python-headless a >=4.13.0.92

**FILE:** `requirements.txt`, `docs/ARCHITETTURA_Live_Video_Composer.md`

**PROBLEMA:**
Attualmente `opencv-python-headless>=4.10.0`. La versione stabile corrente è **4.13.0.92** (2026-02-05, verificato PyPI). Le versioni 4.11, 4.12, 4.13 introducono: supporto AVIF/GIF nativo migliorato, libjpeg-turbo più veloce su Windows, minimo macOS 13. **Nessun breaking change API** su `VideoCapture`/`VideoWriter`/`imwrite`.

**SOLUZIONE:**
1. In `requirements.txt`:
   ```diff
   - opencv-python-headless>=4.10.0
   + opencv-python-headless>=4.13.0.92
   ```
2. In `docs/ARCHITETTURA_Live_Video_Composer.md` sezione 3 (Dipendenze) e 14 (changelog): aggiornare versione
3. In `docs/Istruzioni_Progetto_Claude_Live_Video_Composer.md` sezione Stack

**VINCOLI:**
- Mantenere `opencv-python-headless` (MAI `opencv-python`, vincolo sacro #10)
- Non toccare la logica `cap.release()` (vincolo sacro #6)

**TEST:**
- `pip install -r requirements.txt --upgrade`
- `python main.py` → carica MP4, export MP4/AVI/WebM/GIF → verifica nessuna regressione

---

### [TASK-004] BUG FIX: Validazione robusta in `load_video` per file corrotti/codec mancante

**FILE:** `main.py`

**SINTOMO:**
Quando l'utente trascina un file video corrotto, con codec non supportato (es. HEVC senza K-Lite), o con estensione valida ma contenuto non-video, l'applicazione può mostrare messaggi di errore poco chiari o — nei casi peggiori — bloccarsi in `cv2.VideoCapture.read()` durante l'estrazione del primo frame.

**CAUSA ROOT:**
Probabile assenza di controllo esplicito su `cap.isOpened()` prima di `read()`, e nessuna gestione del caso `ret=False` al primo frame (= video illeggibile dal codec).

**FIX:**
Nella funzione `load_video(filepath)` (riga ~1080-1235 secondo l'architettura), ristrutturare così:

```python
def load_video(self, filepath):
    cap = None
    try:
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            messagebox.showerror(
                t("error.video_title"),
                t("error.video_cannot_open").format(os.path.basename(filepath))
            )
            logger.error("VideoCapture.isOpened() False: %s", filepath)
            return

        # Metadata con guard division-by-zero
        fps = max(1, int(cap.get(cv2.CAP_PROP_FPS) or 1))
        frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        if w <= 0 or h <= 0:
            messagebox.showerror(
                t("error.video_title"),
                t("error.video_invalid_dimensions")
            )
            return

        # Primo frame
        ret, frame = cap.read()
        if not ret or frame is None:
            messagebox.showerror(
                t("error.video_title"),
                t("error.video_codec_missing").format(os.path.basename(filepath))
            )
            logger.error("First frame read failed: %s", filepath)
            return

        # ... resto logica esistente (conversione BGR→RGB→PIL, crea ImageLayer)
    except cv2.error as e:
        messagebox.showerror(t("error.video_title"), t("error.video_cv2").format(str(e)))
        logger.exception("cv2.error in load_video: %s", filepath)
    except Exception as e:
        messagebox.showerror(t("error.video_title"), t("error.video_generic").format(str(e)))
        logger.exception("Unexpected error in load_video: %s", filepath)
    finally:
        if cap is not None:
            cap.release()  # VINCOLO SACRO #6
```

Aggiungere a `localization.py` (entrambe le lingue):
- `error.video_title`: "Errore video" / "Video error"
- `error.video_cannot_open`: "Impossibile aprire il video: {0}" / "Cannot open video: {0}"
- `error.video_codec_missing`: "Codec non disponibile per {0}. Installa K-Lite Codec Pack." / "Codec missing for {0}. Install K-Lite Codec Pack."
- `error.video_invalid_dimensions`: "Dimensioni video non valide" / "Invalid video dimensions"
- `error.video_cv2`: "Errore OpenCV: {0}" / "OpenCV error: {0}"
- `error.video_generic`: "Errore durante il caricamento: {0}" / "Error during loading: {0}"

**VINCOLI:**
- `cap.release()` SEMPRE nel `finally` (vincolo sacro #6)
- `max(1, fps)` / `max(1, frames)` (vincolo sacro #8)
- Stringhe UI tramite `t()` (vincolo i18n)
- NON modificare la logica di creazione `ImageLayer` esistente

**TEST:**
- Caricare un MP4 valido → OK
- Caricare un file `.mp4` rinominato da `.txt` → messaggio chiaro, no crash
- Caricare un video HEVC senza K-Lite → messaggio "codec mancante", no freeze
- Verificare in `live_video_composer.log` che gli errori siano tracciati

---

### [TASK-005] BUG FIX: Memory leak in `_do_export_video` su cancel

**FILE:** `main.py`

**SINTOMO:**
Durante l'export video, se l'utente clicca "Annulla Export" a metà processo, è possibile che: (a) `VideoCapture`/`VideoWriter` non vengano rilasciati subito, (b) i `numpy.ndarray` dei frame accumulati in memoria non vengano liberati, (c) il file di output parziale resti sul disco come "spazzatura".

**CAUSA ROOT:**
Il loop di export controlla `_export_cancelled.is_set()` ed esce con `break`, ma probabilmente non esegue `gc.collect()` né elimina il file parziale.

**FIX:**
Nel blocco `_do_export_video` (riga ~2095-2410 secondo architettura), strutturare il loop così:

```python
def _do_export_video(self, filepath, ...):
    cap = None
    out = None
    partial_file = filepath
    cancelled = False
    try:
        cap = cv2.VideoCapture(...)
        out = cv2.VideoWriter(...)
        if not cap.isOpened() or not out.isOpened():
            raise RuntimeError("Cannot open video capture/writer")

        frame_idx = 0
        total = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))
        while True:
            if self._export_cancelled.is_set():
                cancelled = True
                logger.info("Export video cancellato dall'utente al frame %d/%d", frame_idx, total)
                break
            ret, frame = cap.read()
            if not ret:
                break
            processed = self._process_video_frame_optimized(frame)
            out.write(processed)
            frame_idx += 1
            # Update progress every 10 frames
            if frame_idx % 10 == 0:
                pct = int(100 * frame_idx / total)
                self.root.after(0, lambda p=pct: self._update_progress(p))
            # Libera memoria aggressiva ogni 100 frame per video lunghi
            if frame_idx % 100 == 0:
                del frame, processed
    except Exception as e:
        logger.exception("Errore export video")
        self.root.after(0, lambda: messagebox.showerror(
            t("error.export_title"), t("error.export_video").format(str(e))
        ))
    finally:
        if out is not None:
            try:
                out.release()
            except Exception:
                logger.exception("out.release() fallito")
        if cap is not None:
            try:
                cap.release()
            except Exception:
                logger.exception("cap.release() fallito")
        gc.collect()

        # Rimuovi file parziale se cancellato
        if cancelled and os.path.exists(partial_file):
            try:
                os.remove(partial_file)
                logger.info("File parziale rimosso: %s", partial_file)
            except OSError as e:
                logger.warning("Impossibile rimuovere file parziale %s: %s", partial_file, e)

        self.root.after(0, self._stop_export)
```

**VINCOLI:**
- `cap.release()` e `out.release()` SEMPRE nel `finally` (vincolo sacro #6)
- Mai `root.after(0, ...)` fuori dal thread GUI
- Non toccare `_process_video_frame_optimized`

**TEST:**
- Export MP4 lungo (>30s) → click "Annulla Export" a metà → verificare che il file parziale non resti sul disco
- Monitorare RAM in Task Manager: deve tornare a baseline dopo cancel
- Log deve contenere "Export video cancellato dall'utente"

---

### [TASK-006] REFACTOR: Pattern `try/except/finally` unificato negli export

**FILE:** `main.py`

**PROBLEMA:**
Gli export immagine e video condividono logica comune (start_export → thread → stop_export → cleanup → callback GUI), ma presumibilmente hanno duplicazione di codice. Un errore non gestito in `_do_export_image` potrebbe lasciare la progress bar bloccata se `_stop_export` non viene invocato nel `finally`.

**SOLUZIONE:**
1. Verificare che sia `_do_export_image` che `_do_export_video` abbiano questa struttura:
   ```python
   def _do_export_X(self, ...):
       try:
           # logica export
       except Exception as e:
           logger.exception("Export fallito")
           self.root.after(0, lambda: messagebox.showerror(...))
       finally:
           # cleanup risorse SEMPRE
           gc.collect()
           self.root.after(0, self._stop_export)  # SEMPRE, anche su exception
   ```
2. Se uno dei due non lo rispetta, allinearlo.
3. Per `_do_export_image`: verificare che il ripristino delle working copy (da `_original_path`) sia nel `finally` (altrimenti un errore lascia i layer con gli originali a piena risoluzione → memory leak).

**VINCOLI (non toccare):**
- Logica `_original_path` reload
- `create_composite_image` target_size per preview
- windnd setup

**TEST:**
- Export immagine JPG → OK, progress si ferma
- Export video MP4 → OK, progress si ferma
- Simulare errore (es. path output non scrivibile) → messagebox, progress si ferma, layer ripristinati

---

## 🟡 TASK PRIORITÀ MEDIA

### [TASK-007] BUG FIX: Guard `max(1, ...)` sistematico su calcoli preview

**FILE:** `main.py`

**SINTOMO:**
Edge case teorico: se `canvas_w` o `canvas_h` valgono 0 (finestra minimizzata al limite), `preview_scale = min(canvas_w/output_w, canvas_h/output_h) * 0.9` può produrre 0, e i successivi calcoli `preview_w`, `preview_h` diventano 0 → `create_composite_image(target_size=(0,0))` può crashare in `Image.resize`.

**CAUSA ROOT:**
Il vincolo sacro #8 (`max(1, ...)`) non è applicato a `preview_w`/`preview_h` in `_redraw_canvas_internal`.

**FIX:**
In `_redraw_canvas_internal()`:
```python
canvas_w = max(1, self._cached_canvas_size[0])
canvas_h = max(1, self._cached_canvas_size[1])
output_w = max(1, self.output_width)
output_h = max(1, self.output_height)
preview_scale = min(canvas_w / output_w, canvas_h / output_h) * 0.9
preview_w = max(1, int(output_w * preview_scale))
preview_h = max(1, int(output_h * preview_scale))
```

**VINCOLI:**
- Non toccare debounce, `_cached_canvas_size`, cache zoom
- `create_composite_image` signature invariata

**TEST:**
- Minimizzare/restore finestra rapidamente → nessun crash
- `python main.py` → avvio normale, redraw OK

---

### [TASK-008] FEATURE: Snapshot immutabile dei layer prima dell'export

**FILE:** `main.py`

**SPEC:**
Durante l'export (che gira in thread separato), l'utente potrebbe continuare a modificare i layer nella GUI (aggiungere, rimuovere, trasformare). Questo può causare race condition: il thread export legge `self.layers` mentre il main thread lo modifica → output inconsistente o crash.

**IMPLEMENTAZIONE:**
1. In `_start_export`: prima di lanciare il thread, creare una lista snapshot con deep-copy dei parametri rilevanti:
   ```python
   def _start_export(self):
       # Snapshot immutabile (copia parametri, non PIL.Image — quella resta condivisa)
       self._export_snapshot = [
           {
               'id': layer.id,
               'original_image': layer.original_image,  # riferimento, non copia profonda
               'offset_x': layer.offset_x,
               'offset_y': layer.offset_y,
               'zoom': layer.zoom,
               'rotation': layer.rotation,
               'flip_h': layer.flip_h,
               'flip_v': layer.flip_v,
               'is_video': layer.is_video,
               'video_path': layer.video_path,
               '_original_path': layer._original_path,
               'name': layer.name,
           }
           for layer in self.layers
       ]
       self._export_output_w = self.output_width
       self._export_output_h = self.output_height
       self._export_bg_color = self.bg_color_var.get()
       # ... poi lancia thread
   ```
2. `_do_export_image` / `_do_export_video` devono usare **esclusivamente** `self._export_snapshot` e i campi `_export_*`, mai `self.layers` né `self.output_width`.
3. In `finally` del thread: `self._export_snapshot = None` per liberare riferimenti.
4. Disabilitare i controlli di modifica layer durante l'export (già fatto? verificare), oppure lasciarli abilitati sapendo che lo snapshot protegge l'export.

**VINCOLI:**
- Export rimane in thread separato
- `root.after(0, ...)` per ogni callback GUI
- Non modificare il data model `ImageLayer`
- Aggiornare `docs/ARCHITETTURA_Live_Video_Composer.md` sezione 7 (Data Model) e 9 (Flusso Export)

**TEST:**
- Avviare export video lungo, aggiungere un nuovo layer durante l'export → output del video deve contenere solo i layer originali
- Nessun crash durante la modifica concorrente

---

### [TASK-009] REFACTOR: Eccezioni PIL granulari

**FILE:** `main.py`

**PROBLEMA:**
In `load_image` e `_process_dropped_files`, probabilmente c'è un `except Exception` generico. Meglio catturare le eccezioni PIL specifiche per messaggi chiari all'utente.

**SOLUZIONE:**
```python
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError

def load_image(self, filepath):
    try:
        img = Image.open(filepath)
        img.load()  # forza decodifica immediata
        # ... resto logica
    except UnidentifiedImageError:
        messagebox.showerror(t("error.image_title"), t("error.image_unsupported").format(filepath))
        logger.warning("UnidentifiedImageError: %s", filepath)
    except DecompressionBombError:
        messagebox.showerror(t("error.image_title"), t("error.image_too_large").format(filepath))
        logger.warning("DecompressionBombError: %s", filepath)
    except FileNotFoundError:
        messagebox.showerror(t("error.image_title"), t("error.image_not_found").format(filepath))
    except PermissionError:
        messagebox.showerror(t("error.image_title"), t("error.image_permission").format(filepath))
    except OSError as e:
        messagebox.showerror(t("error.image_title"), t("error.image_io").format(str(e)))
        logger.exception("OSError in load_image: %s", filepath)
    except Exception as e:
        messagebox.showerror(t("error.image_title"), t("error.image_generic").format(str(e)))
        logger.exception("Unexpected error in load_image: %s", filepath)
```

Aggiungere a `localization.py` (it/en) le nuove chiavi (`error.image_unsupported`, `error.image_too_large`, ecc.).

**Nota Decompression Bomb:** Pillow di default blocca immagini >89M pixel. Per immagini legit oltre questa soglia, si può impostare `Image.MAX_IMAGE_PIXELS = None` — ma attenzione: disabilita una protezione di sicurezza. Lasciare la protezione attiva e mostrare il messaggio è più sicuro.

**VINCOLI:**
- i18n entrambe le lingue
- Non modificare la logica di downscale working copy
- `_original_path` deve essere popolato correttamente

**TEST:**
- Drag & drop di file `.txt` rinominato in `.jpg` → messaggio "formato non supportato"
- Immagine 100MP → messaggio "immagine troppo grande"
- Immagine PNG di 4K → caricamento OK con downscale

---

### [TASK-010] FEATURE: Progress percentuale export video

**FILE:** `main.py`

**SPEC:**
Attualmente la progress bar è indeterminata (`progress.start()`). Per video lunghi l'utente non sa a che punto è. Mostrare percentuale reale (es. "Export 45% — 270/600 frame").

**IMPLEMENTAZIONE:**
1. In `create_widgets` (pannello destro), aggiungere una `ttk.Label` sotto la progress bar: `self.progress_label = ttk.Label(..., text="")`.
2. Cambiare `ttk.Progressbar` da `mode='indeterminate'` a `mode='determinate'`, `maximum=100`.
3. In `_do_export_video`, nel loop frame:
   ```python
   if frame_idx % 10 == 0:
       pct = int(100 * frame_idx / total_frames)
       label_text = t("export.progress_frames").format(frame_idx, total_frames, pct)
       self.root.after(0, lambda p=pct, lt=label_text: self._update_progress(p, lt))
   ```
4. Nuovo metodo `_update_progress(self, pct, label_text)`:
   ```python
   def _update_progress(self, pct, label_text):
       self.progress['value'] = pct
       self.progress_label.config(text=label_text)
   ```
5. Per export immagine (single shot): resta indeterminato/hide o 0→100.
6. i18n: `export.progress_frames = "Export {0}/{1} frame ({2}%)"` / `"Export {0}/{1} frames ({2}%)"`

**VINCOLI:**
- Export cancellabile deve continuare a funzionare
- `_stop_export` deve resettare label e progress a 0

**TEST:**
- Export MP4 di 10s → progress avanza da 0% a 100%
- Export MP4 e cancel a 30% → progress torna a 0, label vuota
- Export JPG → progress indeterminato o 0→100 istantaneo

---

### [TASK-011] REFACTOR: Centralizzare magic number in costanti

**FILE:** `main.py`

**PROBLEMA:**
Valori come `3000` (max GIF frame), `2.0` (soglia downscale working copy), `500` (delay setup D&D), `16`/`33` (debounce) sono sparsi nel codice come magic number.

**SOLUZIONE:**
In testa a `main.py`, subito dopo gli import, aggiungere una sezione:
```python
# ============================================================================
# COSTANTI OPERATIVE
# ============================================================================
MAX_GIF_FRAMES = 3000               # Limite memoria per GIF animate
DOWNSCALE_THRESHOLD = 2.0           # Se img > 2x output → working copy ridotta
DND_SETUP_DELAY_MS = 500            # Ritardo setup windnd (vincolo sacro #3)
DEBOUNCE_NORMAL_MS = 16             # Redraw ~60fps
DEBOUNCE_DRAG_MS = 33               # Redraw ~30fps durante drag
PREVIEW_SCALE_MARGIN = 0.9          # Margine preview sul canvas
MAX_IMAGE_FILE_SIZE_MB = 500        # Warning D&D immagine >500MB
MAX_VIDEO_FILE_SIZE_MB = 4096       # Warning D&D video >4GB
```

Sostituire ogni occorrenza nel codice.

**VINCOLI:**
- Nessun cambiamento comportamentale (refactoring puro)
- `docs/ARCHITETTURA_Live_Video_Composer.md` sezione 11 (Vincoli) riferisce `DND_SETUP_DELAY_MS`

**TEST:**
- `python main.py` → comportamento identico
- `grep "3000\|500\|0.9" main.py` → solo nelle costanti dichiarate

---

### [TASK-012] BUG FIX: Cleanup `_canvas_persistent_ids` alla rimozione layer

**FILE:** `main.py`

**SINTOMO:**
`_canvas_persistent_ids` è una dict che mantiene riferimenti agli oggetti canvas Tk per riuso tra redraw. Quando un layer viene rimosso tramite `remove_layer()`, il suo entry in `_canvas_persistent_ids` potrebbe restare orfano → leak di oggetti canvas e potenziale disegno di layer fantasma.

**CAUSA ROOT:**
Presumibilmente `remove_layer()` elimina il layer da `self.layers` ma non pulisce `_canvas_persistent_ids[layer.id]`.

**FIX:**
In `remove_layer(self, layer)`:
```python
def remove_layer(self, layer):
    # Cleanup canvas persistent ID
    if layer.id in self._canvas_persistent_ids:
        canvas_id = self._canvas_persistent_ids.pop(layer.id)
        try:
            self.canvas.delete(canvas_id)
        except tk.TclError:
            pass  # id già eliminato
    # Cleanup risorse layer
    try:
        layer.cleanup()
    except Exception:
        logger.exception("layer.cleanup() fallito")
    # Rimuovi dalla lista
    self.layers.remove(layer)
    if self.selected_layer is layer:
        self.selected_layer = None
    self.update_layer_list()
    self.redraw_canvas(immediate=False)
```

Verificare che `ImageLayer.cleanup()` esista e liberi `_cache`, `_zoom_cache`, `original_image` (se not in `_export_snapshot`).

**VINCOLI:**
- Debounce redraw resta attivo
- `_canvas_persistent_ids` struttura invariata

**TEST:**
- Caricare 5 immagini, rimuoverne 3 → verificare via log che `_canvas_persistent_ids` contenga solo 2 entry
- Ripetere 20 volte → nessun aumento RAM anomalo

---

### [TASK-013] REFACTOR: Verifica `.spec` PyInstaller

**FILE:** `Live_Video_Composer.spec`, `Live_Video_Composer_Portable.spec`

**PROBLEMA:**
I due spec PyInstaller devono contenere `collect_all('windnd')` (vincolo sacro #2). Se manca in uno dei due, il D&D si rompe nella build corrispondente. Inoltre, per ridurre la dimensione del .exe, si possono escludere moduli pesanti non usati (matplotlib, scipy, pytest, tkinter.test).

**SOLUZIONE:**
1. Verificare che entrambi gli spec contengano in cima:
   ```python
   from PyInstaller.utils.hooks import collect_all
   datas_windnd, binaries_windnd, hiddenimports_windnd = collect_all('windnd')
   ```
2. Negli `Analysis(...)`:
   - `datas=datas_windnd + [...]`
   - `binaries=binaries_windnd + [...]`
   - `hiddenimports=hiddenimports_windnd + ['PIL._tkinter_finder', ...]`
3. Aggiungere `excludes`:
   ```python
   excludes=[
       'matplotlib', 'scipy', 'pandas', 'pytest', 'sphinx',
       'tkinter.test', 'test', 'unittest', 'setuptools', 'pip',
       'IPython', 'notebook',
   ]
   ```
4. Lasciare invariato il resto (icon, onefile vs onedir, ecc.)

**VINCOLI:**
- `windnd` collect_all OBBLIGATORIO (vincolo sacro #2)
- `python -m PyInstaller` (vincolo sacro #9)
- Non cambiare `--onefile` / `--onedir`

**TEST:**
- `python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean` → build OK
- Eseguire `release/Live_Video_Composer_Portable.exe` → avvio, D&D funziona, carica immagini/video, export OK
- Confrontare dimensione prima/dopo `excludes` (attesa: riduzione 10-30 MB)

---

## 🟢 TASK PRIORITÀ BASSA

### [TASK-014] FEATURE: Log rotation

**FILE:** `main.py`

**SPEC:**
`live_video_composer.log` cresce indefinitamente. Aggiungere `RotatingFileHandler` per limitare a 5MB × 3 backup.

**IMPLEMENTAZIONE:**
Nella configurazione del logger (sezione imports iniziale):
```python
from logging.handlers import RotatingFileHandler
log_path = _get_log_path()
handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)
```

**VINCOLI:**
- Log resta in `%LOCALAPPDATA%\LiveVideoComposer\` (vincolo sacro #4)

**TEST:**
- Simulare 6MB di log → verifica rotazione `.log.1`, `.log.2`, `.log.3`

---

### [TASK-015] REFACTOR: Type hints completi

**FILE:** `main.py`

**SPEC:**
Aggiungere type hints a `ImageLayer` (tutti gli `__slots__`), costruttore `LiveVideoComposer.__init__`, funzioni core (`load_image`, `load_video`, `create_composite_image`, `get_transformed_image`).

**VINCOLI:**
- Solo annotazioni, nessun cambiamento runtime
- `from __future__ import annotations` in cima a `main.py` per forward references

**TEST:**
- `python main.py` → OK
- Opzionale: `mypy main.py` → ridurre errori progressivamente

---

## 📦 AGGIORNAMENTI LIBRERIE (RIEPILOGO)

Verificato su PyPI il **15 aprile 2026**.

| Libreria | Versione attuale (req.txt) | Ultima stabile | Consigliata | Motivazione |
|---|---|---|---|---|
| **Pillow** | `>=12.1.0` | **12.2.0** (01/04/2026) | **`>=12.1.1,<13`** | 12.1.1 contiene fix sicurezza (release 11/02/2026). 12.2.0 aggiunge solo feature non breaking ma è più recente. Tenere `<13` per evitare breaking Pillow 13. **Pillow 12 richiede Python >=3.10.** |
| **opencv-python-headless** | `>=4.10.0` | **4.13.0.92** (05/02/2026) | **`>=4.13.0.92`** | 4.11 → min macOS 13. 4.12 → AVIF/GIF nativo, libjpeg-turbo più veloce su Windows. 4.13 → minor fixes. Nessun breaking API rispetto a 4.10. |
| **numpy** | `>=1.26.0` | **2.2.x** | **`>=1.26.0`** (invariato) | opencv 4.12+ usa NumPy 2.x per Python 3.9+, ma compatibile con 1.26. Lasciare `>=1.26.0` permette entrambe. Non alzare finché non verifichi compatibilità con codice esistente. |
| **windnd** | `>=1.0.7` | invariato | **`>=1.0.7`** | Pacchetto maturo, nessun update recente. Nessun CVE noto. |
| **tkinterdnd2** | `>=0.4.3` | — | **`>=0.4.3`** | Fallback D&D, invariato. |
| **PyInstaller** | `>=6.0` (commento) | 6.x | **`>=6.11`** | Versioni >6.11 supportano meglio Python 3.13. Aggiornare in caso di problemi build. |

**Comando aggiornamento massivo:**
```powershell
pip install --upgrade Pillow opencv-python-headless numpy
pip install -r requirements.txt --upgrade
```

**Verifica post-upgrade:**
```powershell
python -c "import PIL; print('Pillow', PIL.__version__)"
python -c "import cv2; print('OpenCV', cv2.__version__)"
python -c "import numpy; print('NumPy', numpy.__version__)"
```

---

## ✅ CHECKLIST PRE-ESECUZIONE

Prima di lanciare i task in Cursor Composer:

- [ ] **Backup:** `git add -A && git commit -m "Pre-TASK_BATCH_2026-04-15 baseline"` (oppure zip manuale)
- [ ] **Ambiente:** `python --version` → 3.10+ (se 3.9 → aggiornare Python PRIMA di TASK-001)
- [ ] **Dipendenze attuali:** `pip list | findstr /i "pillow opencv numpy windnd"` → stato iniziale
- [ ] **Smoke test pre-fix:** `python main.py` → avvio OK, carica 1 immagine, D&D funziona, export JPG OK
- [ ] **Build test pre-fix:** `_clean_and_build.bat` → verifica che la build funzioni prima di toccare `.spec`

## ✅ CHECKLIST POST-ESECUZIONE

Dopo ogni blocco di task:

- [ ] **Esecuzione:** `python main.py` → avvio OK
- [ ] **D&D:** trascina immagine nella finestra → layer creato
- [ ] **D&D video:** trascina MP4 → frame mostrato
- [ ] **D&D invalido:** trascina .txt rinominato .jpg → messaggio chiaro
- [ ] **Transform:** zoom, rotazione, flip su layer → preview aggiornata
- [ ] **Export immagine:** JPG/PNG/WebP → file creato, dimensioni corrette
- [ ] **Export video:** MP4 breve (5s) → file creato, riproducibile
- [ ] **Cancel export:** avvia export MP4 lungo, clicca Annulla → stop entro 1s, nessun file parziale residuo
- [ ] **Build completa:** `_clean_and_build.bat` → portable e setup in `release/` senza errori
- [ ] **Test portable:** `release/Live_Video_Composer_Portable.exe` → avvio, D&D, export (versione onefile critica per D&D)
- [ ] **Log:** `%LOCALAPPDATA%\LiveVideoComposer\live_video_composer.log` → nessun ERROR imprevisto
- [ ] **Sync doc:** `docs/ARCHITETTURA_Live_Video_Composer.md` aggiornato (sezioni 3, 7, 9, 14)
- [ ] **Sync BugFix:** `docs/BugFix_Refactor_Implementazioni_Live_Video_Composer.md` → aggiungere righe per ogni task completato
- [ ] **i18n:** `localization.py` → nuove chiavi presenti in **both** `it` ed `en`
- [ ] **Git commit:** commit atomici per task, messaggio format `[TASK-XXX] <tipo>: <titolo>`

---

## 🧭 ORDINE DI ESECUZIONE CONSIGLIATO

1. **Fase 1 — Librerie e runtime** (TASK-001, 002, 003) → base stabile
2. **Fase 2 — Stabilità critica** (TASK-004, 005, 006, 007) → no crash/leak
3. **Fase 3 — Thread safety** (TASK-008) → correctness export
4. **Fase 4 — UX** (TASK-009, 010) → migliore esperienza utente
5. **Fase 5 — Manutenibilità** (TASK-011, 012, 013) → cleanup e build
6. **Fase 6 — Nice-to-have** (TASK-014, 015) → log rotation e types

**Dopo ogni fase:** eseguire la checklist post-esecuzione, committare, pushare (se `.cursor/rules/git-autonomy.mdc` lo prevede).

---

**FINE TASK BATCH 2026-04-15**
