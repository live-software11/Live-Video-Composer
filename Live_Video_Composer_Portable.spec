# -*- mode: python ; coding: utf-8 -*-
# Live Video Composer — Versione Portable (onefile = singolo .exe) SENZA licenza
# Build: python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean
#
# Questa build NON include il modulo license/ e NON imposta LIVEWORKS_LICENSE_ENABLED.
# L'app si avvia direttamente senza gate licenza (versione portable libera).
# La versione installer (Live_Video_Composer.spec) include il modulo licenza.

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'PIL', 'PIL.Image', 'PIL.ImageTk',
    'cv2', 'numpy',
    'windnd', 'windnd.windnd',
    'ctypes', 'ctypes.wintypes',
]

# Raccogli tutto il pacchetto windnd (necessario per drag & drop)
tmp_ret = collect_all('windnd')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],  # Nessun runtime hook → LIVEWORKS_LICENSE_ENABLED rimane non impostato
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'pytest', 'sphinx',
        'tkinter.test', 'test', 'unittest', 'setuptools', 'wheel', 'pip',
        'IPython', 'notebook',
        # Escludi esplicitamente il modulo licenza dalla build portable
        'license',
        'license.fingerprint',
        'license.manager',
        'license.storage',
        'license.gate',
        'wmi',
        'cryptography',
        'cryptography.fernet',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='Live_Video_Composer_Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
