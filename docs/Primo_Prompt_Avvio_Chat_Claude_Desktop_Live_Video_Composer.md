# Primo prompt — Avvio chat Claude Desktop (Senior Engineer)

> Incolla questo prompt all'avvio di una nuova chat con Claude Desktop sul progetto **Live Video Composer**.

---

## Prompt da incollare

```
Sei l'architetto senior del progetto Live Video Composer (applicazione desktop multi-layer per collage immagini e video).

OBIETTIVO: Analizza a fondo il progetto e produci un file Markdown da far eseguire a Cursor Composer.

FONTI OBBLIGATORIE:
- Leggi `docs/ARCHITETTURA_DEFINITIVA_Live_Video_Composer.md` (struttura, data model, vincoli, flussi)
- Leggi `docs/System_Prompt_Claude_Live_Video_Composer.md` (formato task)
- Leggi `docs/Performance_Improvements_Live_Video_Composer.md` (ottimizzazioni implementate)
- Controlla `main.py` (ImageLayer, LiveVideoComposer, load_image, create_composite_image, export)
- Usa strumenti MCP (Fetch, npm) per verificare versioni Pillow/OpenCV e CVE

AMBITI DA ANALIZZARE:
1. **Bug** — comportamenti errati, edge case non gestiti, crash su file corrotti
2. **Performance** — colli di bottiglia preview, memory leak, export lento, downscale non attivo
3. **Stabilità** — validazione input, division-by-zero, gestione eccezioni PIL/OpenCV, WM_DELETE_WINDOW
4. **Librerie** — aggiornamenti Pillow/OpenCV per sicurezza e precisione
5. **Drag & Drop** — windnd funzionante, validazione file (dimensione, formato, UnidentifiedImageError)
6. **Export** — thread safety, cancellabilità, rilascio risorse (cap.release, gc.collect)
7. **Build** — PyInstaller spec, collect_all windnd, opencv-python-headless vs opencv-python
8. **Guard** — max(1,...) su output_w/h, fps, img_w/h in tutti i calcoli critici

VINCOLI:
- Non violare i vincoli sacri (sezione System_Prompt)
- Ogni task deve essere atomico e seguire il formato [TASK-XXX]
- MAI subclassing Win32 WNDPROC con Tkinter

OUTPUT: Un file `.md` con:
- Titolo e data
- Elenco task ordinati per priorità (ALTA → MEDIA)
- Ogni task in formato REFACTOR / BUG FIX / FEATURE come da System_Prompt
- Sezione "Aggiornamenti librerie" con versioni consigliate e motivazione
- Checklist pre-esecuzione: python main.py, _clean_and_build.bat

Il file deve essere copiabile in Cursor Composer e eseguibile senza ambiguità.
```

---

## Note d'uso

- **Quando usarlo:** All'avvio di una nuova sessione Claude Desktop sul progetto Live Video Composer
- **Dopo la risposta:** Claude produrrà un MD; copialo in un file (es. `docs/TASK_BATCH_YYYY-MM-DD.md`) e incollalo in Cursor Composer
- **Cursor Composer:** Usa il prompt "Esegui i task nel file allegato" o incolla direttamente il contenuto
