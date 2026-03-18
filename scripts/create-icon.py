#!/usr/bin/env python3
"""Crea icon.ico dal logo JPG per PyInstaller e Inno Setup."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
src = root / "icons" / "icona Live Video Composer.jpg"
dest = root / "icon.ico"

if not src.exists():
    raise SystemExit(f"Logo non trovato: {src}")

img = Image.open(src).convert("RGBA")
sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(dest, format="ICO", sizes=sizes)
print(f"OK: {dest}")
