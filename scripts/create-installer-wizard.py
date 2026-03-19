#!/usr/bin/env python3
"""Genera immagini wizard per Inno Setup (164x314, 55x58).
Stile broadcast: sfondo scuro #0f172a, logo centrato.
Uso: python scripts/create-installer-wizard.py
"""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
src = root / "icons" / "icona Live Video Composer.jpg"
out_dir = root

if not src.exists():
    raise SystemExit(f"Logo non trovato: {src}")

img = Image.open(src).convert("RGBA")
dark = (15, 23, 42, 255)

# WizardImageFile: 164x314 (left side welcome/finish)
wizard = Image.new("RGB", (164, 314), dark[:3])
logo = img.resize((120, 120))
mask = logo.split()[3] if logo.mode == "RGBA" else None
wizard.paste(logo.convert("RGB"), (22, 97), mask)
wizard.save(out_dir / "installer-wizard.bmp", "BMP")
print("OK: installer-wizard.bmp")

# WizardSmallImageFile: 55x58 (top right)
small = Image.new("RGB", (55, 58), dark[:3])
logo_s = img.resize((45, 45))
mask_s = logo_s.split()[3] if logo_s.mode == "RGBA" else None
small.paste(logo_s.convert("RGB"), (5, 6), mask_s)
small.save(out_dir / "installer-wizard-small.bmp", "BMP")
print("OK: installer-wizard-small.bmp")
