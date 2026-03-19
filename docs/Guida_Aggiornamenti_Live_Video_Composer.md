# Guida aggiornamenti — Live Video Composer

> Documento di riferimento per aggiornare dipendenze Python in modo sicuro.  
> **Ultimo aggiornamento:** Marzo 2026

---

## 1. Principi generali

- **Stabilità prioritaria:** Evitare aggiornamenti major senza test approfonditi.
- **Aggiornamenti safe:** Patch e minor sono generalmente sicuri.
- **Pre-commit:** Dopo ogni aggiornamento eseguire test manuale e build.

---

## 2. Stack attuale

| Pacchetto | Versione | Note |
|-----------|----------|------|
| Python | 3.9+ | — |
| Pillow | >=12.1.0 | Elaborazione immagini |
| opencv-python-headless | >=4.10.0 | Elaborazione video |
| numpy | >=1.26.0 | Array processing |
| windnd | >=1.0.7 | Drag & drop Windows |
| PyInstaller | >=6.0 | Build eseguibile |

---

## 3. Aggiornamenti sicuri (routine)

```bash
pip install -r requirements.txt --upgrade
```

Verificare compatibilità Pillow/OpenCV per export immagine/video.

---

## 4. Build release

```bash
# Doppio click su
_clean_and_build.bat
```

Output in `release/` — verificare Portable.exe e Setup.exe.

---

*Aggiornare questo documento ogni volta che si modificano versioni stack o procedure.*
