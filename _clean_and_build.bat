@echo off
echo ============================================
echo   Live Video Composer v1.5.0 - Clean + Build
echo ============================================
echo.
echo   INSTALLER = licenza Live Works attiva (gate al primo avvio)
echo   PORTABLE  = libero, nessun gate licenza
echo ============================================
echo.

REM Check Python
python --version
if %ERRORLEVEL% neq 0 (
    echo ERRORE: Python non trovato!
    echo Assicurati che Python sia nel PATH
    pause
    exit /b 1
)

REM Installa dipendenze da requirements.txt
echo --- Installo/aggiorno dipendenze ---
pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARN] pip install fallito, alcune dipendenze potrebbero mancare
)

REM Check PyInstaller (usa python -m perche' pyinstaller potrebbe non essere nel PATH)
python -m PyInstaller --version
if %ERRORLEVEL% neq 0 (
    echo PyInstaller non trovato, installo...
    pip install pyinstaller
)

echo.
echo --- Genera icon.ico e grafiche wizard (se mancanti) ---
if not exist "icon.ico" (
    python scripts\create-icon.py
    if %ERRORLEVEL% neq 0 (
        echo [ERRORE] Creazione icon.ico fallita. Verifica icons\icona Live Video Composer.jpg
        pause
        exit /b 1
    )
) else (
    echo [OK] icon.ico presente
)
if not exist "installer-wizard.bmp" (
    python scripts\create-installer-wizard.py
    if %ERRORLEVEL% neq 0 (
        echo [ERRORE] Creazione grafiche wizard fallita
        pause
        exit /b 1
    )
) else (
    echo [OK] installer-wizard.bmp presente
)

echo.
echo --- Pulizia vecchie build ---
if exist "dist" (
    rmdir /s /q dist
    echo [OK] Cartella dist rimossa
)
if exist "build" (
    rmdir /s /q build
    echo [OK] Cartella build rimossa
)
echo.

echo ============================================
echo   1/3 - Build INSTALLER (con licenza Live Works)
echo         License gate attivo: LIVEWORKS_LICENSE_ENABLED=true
echo         Runtime hook: scripts\license_runtime_hook.py
echo ============================================
echo.

python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Versione Installer pronta (dist\Live_Video_Composer\)
) else (
    echo [ERRORE] Build Installer fallita!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   2/3 - Build PORTABLE (singolo .exe, SENZA licenza)
echo         Avvio diretto, nessun gate attivazione
echo ============================================
echo.

python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Versione Portable pronta (dist\Live_Video_Composer_Portable.exe)
) else (
    echo [ERRORE] Build Portable fallita!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   3/3 - Build SETUP (Inno Setup)
echo         Include l'exe Installer con licenza
echo ============================================
echo.

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe

if defined ISCC (
    "%ISCC%" installer.iss
    if %ERRORLEVEL% equ 0 (
        echo [OK] Setup creato in release\Live_Video_Composer_Setup.exe
    ) else (
        echo [ERRORE] Compilazione Inno Setup fallita
    )
) else (
    echo Inno Setup non trovato. Compila manualmente:
    echo   1. Apri installer.iss con Inno Setup Compiler
    echo   2. Compila (Ctrl+F9)
)

echo.
echo Copia output in release\...
if not exist "release" mkdir release
if exist "dist\Live_Video_Composer_Portable.exe" (
    copy /y "dist\Live_Video_Composer_Portable.exe" "release\Live_Video_Composer_Portable.exe" >nul
    echo [OK] Portable copiato in release\
)
echo.
echo ============================================
echo   BUILD COMPLETATA!
echo ============================================
echo.
echo Output in release\:
if exist "release\Live_Video_Composer_Portable.exe" (
    for %%F in ("release\Live_Video_Composer_Portable.exe") do echo    Live_Video_Composer_Portable.exe  [%%~zF bytes]  ^(SENZA licenza^)
)
if exist "release\Live_Video_Composer_Setup.exe" (
    for %%F in ("release\Live_Video_Composer_Setup.exe") do echo    Live_Video_Composer_Setup.exe     [%%~zF bytes]  ^(CON licenza Live Works^)
)
echo.
echo NOTA: Solo la versione Setup include il gate licenza Live Works.
echo       La versione Portable e' libera e non richiede attivazione.
echo.
pause
