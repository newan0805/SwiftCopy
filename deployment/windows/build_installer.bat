@echo off
REM ============================================================
REM SwiftCopy - Windows Build & Installer Creator
REM Builds dist\SwiftCopy.exe (with app icon) and, if Inno Setup
REM is installed, creates dist\installers\SwiftCopy-Setup-1.0.0.exe
REM ============================================================
setlocal
cd /d "%~dp0..\.."

echo [*] SwiftCopy Windows Build & Installer
echo [*] Project root: %CD%

REM --- 1. Create & use a virtual environment if none exists ---
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment...
    py -3 -m venv .venv
)
set "PY=.venv\Scripts\python.exe"

REM --- 2. Install build dependencies ---
echo [*] Installing build dependencies...
"%PY%" -m pip install --upgrade pyinstaller pillow

REM --- 3. Build the PyInstaller executable (embeds icon.ico) ---
echo [*] Building executable...
"%PY%" build_configs\build.py windows
if errorlevel 1 goto :error

if not exist "dist\SwiftCopy.exe" (
    echo [!] dist\SwiftCopy.exe not found!
    goto :error
)

REM --- 4. Create installer with Inno Setup (if available) ---
echo [*] Checking for Inno Setup...
where ISCC.exe >nul 2>nul
if errorlevel 1 (
    echo [!] Inno Setup not found. Skipping installer creation.
    echo [i] Install Inno Setup from https://jrsoftware.org/isinfo.php
    echo     then run: iscc deployment\windows\installer.iss
    goto :done
)

echo [*] Compiling installer with Inno Setup...
ISCC.exe "deployment\windows\installer.iss"
if errorlevel 1 goto :error

echo [*] Installer created in dist\installers\
goto :done

:error
echo [X] Build failed. Review the errors above.
exit /b 1

:done
echo.
echo [===========================================]
echo [+] Windows deployment complete!
echo [+] Executable: dist\SwiftCopy.exe
echo [+] Installer:  dist\installers\SwiftCopy-Setup-1.0.0.exe (if Inno Setup present)
echo [===========================================]
endlocal
