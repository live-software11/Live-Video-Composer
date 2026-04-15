# -*- mode: python ; coding: utf-8 -*-
# Live Video Composer — Versione Installer (onedir) con sistema licenze Live Works
# Build: python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean
#
# Questa build include il modulo license/ e imposta LIVEWORKS_LICENSE_ENABLED=true
# tramite runtime hook. Il gate licenza blocca l'avvio finché la chiave non è valida.
# La versione portable (Live_Video_Composer_Portable.spec) NON include il modulo licenza.

from PyInstaller.utils.hooks import collect_all
import os

datas = []
binaries = []
hiddenimports = [
    'PIL', 'PIL.Image', 'PIL.ImageTk',
    'cv2', 'numpy',
    'windnd', 'windnd.windnd',
    'ctypes', 'ctypes.wintypes',
    # Modulo licenza locale (import condizionale in main.py)
    'license',
    'license.fingerprint',
    'license.manager',
    'license.storage',
    'license.gate',
    'wmi',
    'cryptography',
    'cryptography.fernet',
    'requests',
    'requests.adapters',
    'urllib3',
]

# Raccogli tutto il pacchetto windnd (necessario per drag & drop)
tmp_ret = collect_all('windnd')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Inclusione esplicita del package license/ locale (non usare collect_all
# che potrebbe confonderlo con un pacchetto PyPI omonimo).
_license_pkg = os.path.join('.', 'license')
datas += [(_license_pkg, 'license')]

# Runtime hook: imposta LIVEWORKS_LICENSE_ENABLED=true nell'exe installer
_RUNTIME_HOOK = os.path.abspath('scripts/license_runtime_hook.py')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[_RUNTIME_HOOK],
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'pytest', 'sphinx',
        'tkinter.test', 'test', 'unittest', 'setuptools', 'wheel', 'pip',
        'IPython', 'notebook',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='Live_Video_Composer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Live_Video_Composer',
)
