#!/usr/bin/env python3
"""
SwiftCopy - Cross-Platform Build Script (with application icon)

Usage:
    python build.py linux
    python build.py windows
    python build.py macos
    python build.py all        (builds for current platform)
    python build.py deps       (install build dependencies)
    python build.py install    (build + run platform installer/deployment)

Produces platform executables with the app icon:
    - Windows: dist/SwiftCopy.exe  (icon.ico) + dist/installers/*.exe (Inno Setup)
    - Linux:   dist/SwiftCopy      (icon.png) + .deb / .AppImage / .tar.gz
    - macOS:   dist/SwiftCopy.app  (icon.icns) + .dmg
"""
import os
import sys
import shutil
import subprocess
import platform
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MAIN = PROJECT / "main.py"
ENGINES = PROJECT / "engines"
ASSETS = PROJECT / "assets"
DIST = PROJECT / "dist"
BUILD = PROJECT / "build"
APP_NAME = "SwiftCopy"


def install_deps():
    print("[*] Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pillow"], check=True)


def _run_make_icons():
    subprocess.run([sys.executable, str(PROJECT / "build_configs" / "make_icons.py")], check=True)


def clean():
    for d in (DIST, BUILD):
        if d.exists():
            shutil.rmtree(d)
    for f in PROJECT.glob("*.spec"):
        f.unlink()


def build_current(extra=None):
    _run_make_icons()
    system = platform.system().lower()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",
        "--clean",
        "--noconfirm",
    ]

    if system == "windows":
        cmd += ["--onefile", "--icon", str(ASSETS / "icon.ico")]
        sep = ";"
    elif system == "darwin":
        cmd += ["--icon", str(ASSETS / "icon.icns")]
        sep = ":"
    else:  # linux
        cmd += ["--onefile", "--icon", str(ASSETS / "icon.png")]
        sep = ":"

    cmd += [
        f"--add-data={ASSETS}{sep}assets",
        f"--add-data={ENGINES}{sep}engines",
    ]
    if extra:
        cmd += extra
    cmd.append(str(MAIN))

    print(f"[*] Building {APP_NAME} for {platform.system()}...")
    subprocess.run(cmd, check=True, cwd=str(PROJECT))
    print(f"[+] Build complete -> {DIST}")


def build_windows():
    if platform.system().lower() != "windows":
        print("[!] Building for Windows must be run ON a Windows machine.")
        return
    build_current()


def build_linux():
    if platform.system().lower() != "linux":
        print("[!] Building for Linux must be run ON a Linux machine.")
        return
    build_current()


def build_macos():
    if platform.system().lower() != "darwin":
        print("[!] Building for macOS must be run ON a macOS machine.")
        return
    build_current()


def run_installer():
    """Build then run the platform-specific deployment/installer script."""
    system = platform.system().lower()
    deploy = PROJECT / "deployment"
    if system == "windows":
        script = deploy / "windows" / "build_installer.bat"
        build_current()
        print("[*] Windows installer: run build_installer.bat (needs Inno Setup)")
    elif system == "darwin":
        script = deploy / "macos" / "build_dmg.sh"
    else:
        script = deploy / "linux" / "build_deb.sh"
    if script and script.exists():
        print(f"[*] Running deployment script: {script}")
        if sys.platform == "win32":
            subprocess.run(["cmd", "/c", str(script)], check=True)
        else:
            subprocess.run(["bash", str(script)], check=True)
    else:
        print(f"[!] No deployment script for {system}")
        build_current()


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "all"
    if task == "deps":
        install_deps()
    elif task == "clean":
        clean()
    elif task == "install":
        run_installer()
    elif task == "linux":
        clean(); build_linux()
    elif task == "windows":
        clean(); build_windows()
    elif task == "macos":
        clean(); build_macos()
    elif task == "all":
        clean(); build_current()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
