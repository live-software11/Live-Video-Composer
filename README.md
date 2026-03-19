# Live Video Composer

**Convertitore di Immagini e Video con supporto Multi-Layer Collage**

> Versione 1.4.1 | Windows 10/11

---

## Caratteristiche

### Core
- **Multi-Layer Collage** — Crea composizioni con immagini sovrapposte
- **Drag & Drop** — Trascina file nella finestra (funziona anche nella versione portable .exe singolo)
- **Handle di Selezione** — Ridimensiona e ruota con handle visivi stile PowerPoint
- **Zoom 1-1000%** — Scroll delicato (1% per tick) per controllo preciso
- **Trasformazioni Complete** — Rotazione -180/+180, specchio H/V, posizionamento pixel-perfect
- **Adattamento Automatico** — 4 modalità: Adatta, Riempi, Riempi H, Riempi V
- **Blocco Proporzioni** — Toggle per mantenere aspect ratio durante ridimensionamento

### Esportazione
- **Multi-formato Immagine** — JPG, PNG, WebP, BMP con preset qualità
- **Multi-formato Video** — MP4, AVI, WebM, GIF animata
- **Preset Qualità** — Bassa/Media/Alta con DPI e bitrate ottimizzati
- **Sfondo Personalizzabile** — 9 colori preset + color picker

### UI/UX
- **Tema Dark Moderno** — Interfaccia blu notte con accenti cyan
- **Fullscreen all'avvio** — Massimizza spazio di lavoro
- **Pannello Scrollabile** — Tutti i controlli accessibili con scroll
- **Sezioni Colorate** — Differenziazione visiva: Layers (blu), Transform (cyan), Size (teal), Fit (viola), Mirror (arancio)
- **Logging integrato** — File di log per diagnostica (in `%LOCALAPPDATA%\LiveVideoComposer\`)

---

## Installazione

### Versione Portable
Scarica `Live_Video_Composer_Portable.exe` — un singolo file .exe, nessuna installazione richiesta.

### Versione Installer
Scarica `Live_Video_Composer_Setup.exe` per l'installazione guidata con icona desktop e menu Start.

**Requisiti:** Windows 10/11, 4GB RAM minimo (8GB consigliato per video), ~100MB disco.

---

## Avvio

- **Portable:** Doppio click su `Live_Video_Composer_Portable.exe` — funziona da qualsiasi posizione, anche da chiavetta USB.
- **Installer:** Avvia dal menu Start o dall'icona desktop.

---

## Guida all'uso

### Workflow Base

1. **Carica file** — `Aggiungi File` o `Ctrl+O` o trascina file nella finestra
2. **Imposta canvas** — Scegli un preset (Full HD, 4K, Instagram, etc.) o dimensioni personalizzate
3. **Trasforma layer** — Zoom, rotazione, posizione, flip con slider o mouse
4. **Esporta** — `ESPORTA IMMAGINE` o `ESPORTA VIDEO` o `Ctrl+S`

### Controlli Layer

| Azione | Mouse | Tastiera | Slider |
|--------|-------|----------|--------|
| Seleziona | Click su immagine | Click lista | — |
| Sposta | Drag centrale | — | Pan X / Tilt Y |
| Zoom | Scroll wheel | — | Zoom % |
| Ridimensiona | Drag handle angolo | — | Zoom % |
| Ruota | Drag handle rotazione (verde) | — | Rotazione |
| Elimina | — | Canc/Delete | Pulsante Rimuovi |
| Deseleziona | Click area vuota | Esc | — |

### Preset Risoluzioni Disponibili

| Preset | Dimensioni | Uso tipico |
|--------|-----------|------------|
| Full HD 16:9 | 1920x1080 | Video, presentazioni |
| HD 16:9 | 1280x720 | Web, streaming |
| 4K 16:9 | 3840x2160 | Ultra HD |
| Full HD Verticale 9:16 | 1080x1920 | Stories, Reels |
| Quadrato 1:1 | 1080x1080 | Instagram, profilo |
| Banner 3:1 | 1200x400 | Banner web |
| Twitter Header | 1500x500 | Copertina Twitter/X |
| Facebook Cover | 820x312 | Copertina Facebook |
| YouTube Thumbnail | 1280x720 | Miniature YouTube |
| Instagram Landscape | 1080x608 | Post Instagram |
| 4:3 | 800x600, 1024x768 | Formato classico |

### Preset Qualità

#### Immagini
| Preset | DPI | Bit Depth | Compressione | Uso |
|--------|-----|-----------|-------------|-----|
| Bassa | 72 | 8-bit | 40% | Web, preview |
| Media | 150 | 16-bit | 15% | Stampa casalinga |
| Alta | 300 | 24-bit | 0% | Stampa professionale |

#### Video
| Preset | Bitrate | CRF | Uso |
|--------|---------|-----|-----|
| Bassa | 2000 kbps | 28 | Web, file piccoli |
| Media | 5000 kbps | 23 | Qualità bilanciata |
| Alta | 8000 kbps | 18 | Massima qualità |

### Scorciatoie

| Tasto | Azione |
|-------|--------|
| `Ctrl+O` | Apri file |
| `Ctrl+S` | Esporta immagine |
| `Canc` | Elimina layer selezionato |
| `Esc` | Deseleziona tutto |
| `Scroll` | Zoom +/-1% |
| `Drag` | Sposta layer |

---

## Risoluzione Problemi

### Errori Comuni

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| "OpenCV non installato" | Supporto video mancante | Reinstalla l'applicazione |
| Video non si carica | Codec mancante | Installa K-Lite Codec Pack |
| Export lento | File/risoluzione grande | Usa preset qualità inferiore |
| Crash su immagini grandi | RAM insufficiente | Riduci risoluzione sorgente |
| D&D non funziona | Esecuzione come admin | Avvia senza "Esegui come admin" |

### Diagnostica

Il file `live_video_composer.log` (in `%LOCALAPPDATA%\LiveVideoComposer\`) contiene informazioni dettagliate per la diagnostica.

### Nota su Drag & Drop

Il drag & drop non funziona se l'applicazione viene eseguita "come Amministratore" e i file vengono trascinati da un processo non-admin (limitazione Windows). Soluzione: avviare normalmente senza privilegi elevati.

---

## Changelog

### v1.4.1 (2026-03-18)
- Aggiornamenti dipendenze e documentazione

### v1.4.0 (2026-03-18)
- Downscale al caricamento per immagini grandi
- Export cancellabile con pulsante "Annulla Export"
- Chiusura sicura con cleanup risorse
- Validazione robusta per file grandi e formati non supportati

### v1.3.1 (2026-02-11)
- Fix Drag & Drop nella versione portable
- Log spostato in `%LOCALAPPDATA%\LiveVideoComposer\`

### v1.3.0 (2026-02-11)
- Logging integrato per diagnostica
- Gestione errori migliorata
- Export GIF ottimizzato

---

## Licenza

MIT License - Libero per uso personale e commerciale.
