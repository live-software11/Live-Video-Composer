# Istruzioni Traduzione i18n — Live Video Composer

> **Ultimo aggiornamento:** 19 Marzo 2026
> **Progetto:** Live Video Composer (Desktop Python — Tkinter)
> **Lingua default app:** Inglese al primo avvio. Salvataggio scelta alla chiusura.
> **Stato workflow:** ✅ Completato 19/03/2026 (audit, revisione, applicazione)

---

## Contesto tecnico

| Campo | Valore |
|-------|--------|
| **Tecnologia i18n** | Custom: `localization.py` (dict Python `_TRANSLATIONS` con chiavi it/en) |
| **File traduzioni** | `localization.py` (dizionari inline) |
| **Uso nel codice** | `t("chiave")` o `t("chiave", arg0, arg1)` |
| **Interpolazione** | `{0}`, `{1}` (str.format Python) |
| **Chiavi** | ~116, flat con prefisso (app., layers., btn., transform., size., fit., mirror., canvas., output., export., preset., status., error., layer., menu.) |
| **Persistenza lingua** | `%LOCALAPPDATA%\LiveVideoComposer\lang.json` → `{"lang": "en"}` |
| **Toggle lingua** | Pulsanti IT/EN in header (cyan per attivo, blu scuro per inattivo) |
| **Default** | `_CURRENT_LANG = "en"` — primo avvio in inglese |

---

## Dominio terminologico

Terminologia professionale per:
- **Compositing:** layer, collage, canvas, output, resolution, aspect ratio
- **Trasformazioni:** scale, rotation, pan, tilt, flip, mirror, crop
- **Adattamento:** contain, cover, fill horizontal, fill vertical
- **Export:** render, encode, frame rate, codec, quality, output format
- **Preset risoluzioni:** Full HD, 4K UHD, LED wall (custom), portrait/landscape

---

## Regole specifiche

1. **Chiavi flat con prefisso:** `canvas.drag_hint`, `export.title`, `preset.fullhd`. Mantenere la convenzione.
2. **Placeholder Python:** `{0}`, `{1}` — stesso ordine in IT e EN.
3. **Preset risoluzioni:** I nomi dei preset (Full HD, 4K UHD, ecc.) sono in inglese in entrambe le lingue.
4. **Emoji nelle chiavi:** Alcune chiavi IT contengono emoji (es. "⭐ Layers"). Mantenere le stesse emoji in EN.
5. **Portable:** Se l'app gira da USB/cartella senza `%LOCALAPPDATA%`, il fallback è `_CURRENT_LANG = "en"`.

---

## Workflow

```bash
git checkout -b revisione-i18n-LiveComposer
```

### FASE 1 — AUDIT

```
Analizza tutti i file del progetto Live Video Composer.

File i18n: localization.py (dizionari _TRANSLATIONS["it"] e _TRANSLATIONS["en"])
Uso: t("chiave") con placeholder {0}

Genera un report strutturato con:

1. STRINGHE HARDCODED
   → file e riga dove il testo è nel codice Python e non in localization.py
   → Cerca in: main.py (classe LiveVideoComposer), inclusi label dimensioni (L:, A:, W:, H:)

2. COPERTURA i18n
   → chiavi presenti in it ma mancanti in en
   → chiavi presenti in en ma mancanti in it

3. CHIAVI IN ITALIANO
   → chiavi con nome in italiano

4. TRADUZIONI SOSPETTE
   → EN identico all'IT
   → traduzioni letterali di termini tecnici video/compositing

5. INCONSISTENZE DI TONO

Salva come docs/audit-i18n-LiveComposer.md
Non correggere — aspetta OK.
```

### FASE 2 — REVISIONE

```
Leggi docs/audit-i18n-LiveComposer.md

Step 1: leggi localization.py dal disco
Step 2: verifica termini video/compositing
Step 3: documenta errori con chiave, IT attuale, EN attuale, problema, proposta
Step 4: salva come docs/revisione-i18n-LiveComposer.md
        Aspetta OK.
```

### FASE 3 — APPLICAZIONE

```
Leggi docs/revisione-i18n-LiveComposer.md e applica.

Step 1: modifica localization.py (entrambi i dizionari)
Step 2: se chiavi rinominate → docs/mappa-chiavi-LiveComposer.md
Step 3: python main.py per verificare che si avvii senza errori
```

### FASE 4 — REFACTOR (solo se chiavi rinominate)

```
Leggi docs/mappa-chiavi-LiveComposer.md
Sostituisci t("vecchia") in main.py.
python main.py e verifica.
```

---

## Checklist finale

- [x] Tutte le chiavi it hanno corrispondente en (e viceversa)
- [x] Nessuna stringa hardcoded in main.py
- [x] Terminologia EN professionale video/compositing
- [x] App si avvia senza errori
- [x] Primo avvio in inglese (_CURRENT_LANG = "en")
- [x] Lingua salvata in lang.json alla chiusura

**Nota:** Workflow completato 19/03/2026. Documenti: `audit-i18n-LiveComposer.md`, `revisione-i18n-LiveComposer.md`.
