# Revisione i18n — Live Video Composer

> **Data:** 19 Marzo 2026
> **Fase:** 2 — REVISIONE (modifiche approvate)
> **Riferimento:** `docs/audit-i18n-LiveComposer.md`
> **Prossimo step:** Applicazione (FASE 3)

---

## 1. MODIFICHE APPROVATE

### 1.1 main.py — Label dimensioni hardcoded (L:, A:, W:, H:)

| Campo | Valore |
|-------|--------|
| **File** | `main.py` |
| **Righe** | 663, 669, 781, 785 |
| **Problema** | Label "L:", "A:", "W:", "H:" non localizzati |
| **Soluzione** | Nuove chiavi `size.label_w` e `size.label_h` + `t()` |

**Nuove chiavi in localization.py:**

| Chiave | IT | EN |
|--------|----|----|
| `size.label_w` | L: | W: |
| `size.label_h` | A: | H: |

**Codice prima (riga 663-669):**
```python
ttk.Label(size_row, text="L:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
...
ttk.Label(size_row, text="A:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
```

**Codice dopo:**
```python
self.size_label_w = ttk.Label(size_row, text=t("size.label_w"), font=('Segoe UI', 9))
self.size_label_w.pack(side=tk.LEFT)
...
self.size_label_h = ttk.Label(size_row, text=t("size.label_h"), font=('Segoe UI', 9))
self.size_label_h.pack(side=tk.LEFT)
```

**Codice prima (riga 781-785):**
```python
ttk.Label(size_frame, text="W:").grid(row=0, column=0)
...
ttk.Label(size_frame, text="H:").grid(row=0, column=2, padx=(10,0))
```

**Codice dopo:**
```python
self.output_label_w = ttk.Label(size_frame, text=t("size.label_w"))
self.output_label_w.grid(row=0, column=0)
...
self.output_label_h = ttk.Label(size_frame, text=t("size.label_h"))
self.output_label_h.grid(row=0, column=2, padx=(10,0))
```

**apply_localization():** Aggiungere aggiornamento dei 4 label:
```python
self.size_label_w.config(text=t("size.label_w"))
self.size_label_h.config(text=t("size.label_h"))
self.output_label_w.config(text=t("size.label_w"))
self.output_label_h.config(text=t("size.label_h"))
```

---

## 2. RIEPILOGO FILE DA MODIFICARE

| File | Azione |
|------|--------|
| `localization.py` | Aggiungere `size.label_w` e `size.label_h` in it e en |
| `main.py` | Sostituire 4 label hardcoded, aggiungere update in apply_localization |

---

## 3. VERIFICA POST-APPLICAZIONE

- [ ] Nessuna stringa UI hardcoded per dimensioni
- [ ] Chiavi presenti in entrambi i dizionari
- [ ] `python main.py` si avvia senza errori
- [ ] Test: cambio lingua IT/EN → label L/A e W/H corretti

---

**Stato:** ✅ Revisione completata — pronto per FASE 3 (Applicazione)
