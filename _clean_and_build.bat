@echo off
echo ============================================
echo   Live Video Composer v1.4.1 - Clean + Build
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

REM Check PyInstaller (usa python -m perche' pyinstaller potrebbe non essere nel PATH)
python -m PyInstaller --version
if %ERRORLEVEL% neq 0 (
    echo PyInstaller non trovato, installo...
    pip install pyinstaller
)

echo.
echo --- Genera icon.ico da logo (se mancante) ---
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
echo   1/2 - Build INSTALLER (cartella per Inno Setup)
echo ============================================
echo.

python -m PyInstaller Live_Video_Composer.spec --noconfirm --clean

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Versione Installer pronta
) else (
    echo [ERRORE] Build Installer fallita!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   2/2 - Build PORTABLE (singolo .exe)
echo ============================================
echo.

python -m PyInstaller Live_Video_Composer_Portable.spec --noconfirm --clean

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Versione Portable pronta
) else (
    echo [ERRORE] Build Portable fallita!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   3/3 - Build SETUP (Inno Setup)
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
)
echo.
echo ============================================
echo   BUILD COMPLETATA!
echo ============================================
echo.
echo Output in release\:
if exist "release\Live_Video_Composer_Portable.exe" (
    for %%F in ("release\Live_Video_Composer_Portable.exe") do echo    Live_Video_Composer_Portable.exe  [%%~zF bytes]
)
if exist "release\Live_Video_Composer_Setup.exe" (
    for %%F in ("release\Live_Video_Composer_Setup.exe") do echo    Live_Video_Composer_Setup.exe  [%%~zF bytes]
)
echo.
pause
