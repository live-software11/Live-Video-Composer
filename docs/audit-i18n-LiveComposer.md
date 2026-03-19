# Audit i18n — Live Video Composer

> **Data:** 19 Marzo 2026
> **Fase:** 1 — AUDIT (nessuna modifica effettuata)
> **Prossimo step:** Revisione (FASE 2) dopo OK utente

---

## 1. STRINGHE HARDCODED

Testo presente nel codice Python ma non in `localization.py`:

| File | Riga | Testo | Contesto |
|------|------|-------|----------|
| `main.py` | 663 | `"L:"` | Label larghezza layer (Larghezza) — IT |
| `main.py` | 669 | `"A:"` | Label altezza layer (Altezza) — IT |
| `main.py` | 781 | `"W:"` | Label larghezza output (Width) — EN |
| `main.py` | 785 | `"H:"` | Label altezza output (Height) — EN |

**Nota:** In italiano si usano L (Larghezza) e A (Altezza); in inglese W (Width) e H (Height). Attualmente il layer size usa sempre L/A (italiano) e l'output size usa sempre W/H (inglese). Per coerenza i18n servono chiavi `size.label_w` e `size.label_h`:
- IT: "L:", "A:"
- EN: "W:", "H:"

**Accettabili (non modificare):**
- `"IT"`, `"EN"` — Pulsanti toggle lingua (abbreviazioni internazionali)
- `"▲"`, `"▼"`, `"▢"`, `"↻"` — Simboli UI universali
- `"100%"`, `"-90°"`, `"0°"`, `"+90°"`, `"%"`, `"°"` — Unità/numeri
- `"PNG"`, `"JPG"`, `"WebP"`, `"BMP"`, `"MP4"`, `"AVI"`, `"WebM"`, `"GIF"` — Formati file tecnici invariati
- Messaggi logger — Interni, non UI

---

## 2. COPERTURA i18n

**Verifica chiavi It vs En:** ✅ **Simmetrica**

Le 114 chiavi presenti in `it` hanno corrispondente in `en` e viceversa. Nessuna chiave mancante.

---

## 3. CHIAVI IN ITALIANO

**Nessuna.** Tutte le chiavi usano nomi in inglese (`app.title`, `canvas.drag_hint`, `export_img.btn`, ecc.).

---

## 4. TRADUZIONI SOSPETTE (EN identico a IT)

Chiavi dove il valore EN è identico al valore IT:

| Chiave | Valore | Note |
|--------|--------|------|
| `app.title` | Live Video Composer  •  Image & Video Editor | Brand + titolo invariato — OK |
| `layers.title` | ⭐ Layers | Termine tecnico invariato — OK |
| `output.preset` | Preset: | Termine invariato — OK |
| `preset.*` | 1920x1080 (Full HD 16:9) ecc. | Risoluzioni tecniche invariati — OK |
| `filetypes.*` | Images and Video ecc. | Diversi da IT — OK |

**Nessuna copia IT→EN non tradotta.**

---

## 5. INCONSISTENZE DI TONO

- **IT:** Formale, impersonale, professionale
- **EN:** Stesso tono
- **Coerenza:** ✅ Buona. Terminologia video/compositing professionale.

---

## 6. ELEMENTI AGGIUNTIVI

### apply_localization()

`main.py` → `apply_localization()` aggiorna tutti i controlli dopo `_set_lang()`. Copertura completa verificata. I label "L:", "A:", "W:", "H:" non sono aggiornati perché hardcoded — vanno sostituiti con `t()`.

### canvas.instructions

- IT: "Canc = Elimina" (tasto Canc italiano)
- EN: "Del = Delete" (tasto Delete inglese)
- ✅ Corretto: shortcut localizzato per tastiera.

---

## RIEPILOGO AZIONI CONSIGLIATE

| Priorità | Azione |
|----------|--------|
| **Alta** | Aggiungere `size.label_w` IT="L:" EN="W:" e `size.label_h` IT="A:" EN="H:"; sostituire le 4 occorrenze hardcoded in main.py con `t("size.label_w")` e `t("size.label_h")` |

---

## PROSSIMO STEP

**FASE 2 — REVISIONE:** Generare `docs/revisione-i18n-LiveComposer.md` con proposte di correzione dettagliate.

**⏸ Attendere OK utente prima di procedere.**
