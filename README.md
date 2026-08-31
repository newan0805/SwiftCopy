# SwiftCopy

**Ultra-Fast File Transfer Suite** — A modern, cross-platform GUI application for bulk file copying, archiving, and file splitting/merging. Runs on **Windows, Linux, and macOS**.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)

Built with **Python + PyQt6**, with a modern dark GitHub-style UI.

---

## Features

### 📋 Copy
- Bulk copy of large numbers of files & folders
- Native system tools on each platform:
  - **Windows**: `xcopy`
  - **Linux**: `rsync` / `cp`
  - **macOS**: `cp`
- Multi-worker configurable threading (1–32)
- Adjustable buffer size (1–64 MB)
- Optional hash **verification** of every copied file (resume-safe)
- **Resume** support — picks up where it left off
- Pause / Resume / Stop controls
- Preserve file attributes & symlinks
- Skip hidden/system files
- Filter by include/exclude patterns, extensions, min/max size
- Speed limiter, dry-run mode
- Live progress bar, log viewer, and transfer speed display

### 📦 Archive
- **ZIP** (compression level 0–9, optional password + AES encryption)
- **7z** (multi-threaded, split volumes, password protected)
- **ISO** (for building disk images)
- **TAR / TAR.GZ / TAR.BZ2 / TAR.XZ**
- Extract capabilities (ZIP, TAR variants, 7z)

### ✂️ Split / Merge
- Split any file into equal-size parts (from 10 MB up to DVD double-layer)
- Common presets: CD (700 MB), DVD, DVD-DL, FAT32 2 GB limits
- Custom part sizes
- SHA-256 **manifest** creation for safe reassembly
- Verify-on-merge with original hash check
- Auto-detect parts & manifest when merging

### 🎨 UI / UX
- Modern dark theme (GitHub-inspired accent colors)
- **Custom frameless title bar** with minimize / maximize / close controls
- **Fully responsive & resizable** — all layouts scale dynamically with the window
- **Drag anywhere on the title bar** to move the window; double-click to maximize
- Tabbed interface: Copy / Archive / Split-Merge / Settings / History
- Real-time progress, status & log panels
- Transfer **history** table
- Settings for workers, buffer, theme, default paths

---

## Quick Start (Run from source)

Create a virtual environment and install dependencies (recommended):

```bash
cd SwiftCopy

# 1. Create & activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```

The application is fully resizable and responsive — the layouts, title bar, and all panels adapt dynamically as you resize the window.

### Platform-specific system dependencies

| Platform | Requirement |
|----------|-------------|
| All | Python 3.9+, PyQt6 |
| Windows | none extra (xcopy built-in) |
| Linux | `rsync`, `p7zip-full`, `genisoimage` (optional for those features) |
| macOS | none extra |

---

## Building Executables

SwiftCopy uses the **application icon** (`assets/swiftcopy.png`) as its app icon for every platform — Windows, Linux, and macOS. The logo (`assets/logo.png`) is the brand mark and is **not** used as the app icon.

### Requirements
- The app icon source image must be at `assets/swiftcopy.png` (256x256, RGBA)
- [PyInstaller](https://pyinstaller.org/) and [Pillow](https://python-pillow.org/) (installed automatically by the scripts)

### Build for current platform

```bash
cd SwiftCopy

# One command — generates icons from the app icon then builds
python build_configs/build.py linux      # or: windows / macos
```

Or use the helper scripts:

| OS | Command | Output |
|----|---------|--------|
| Windows | `build_windows.bat` | `dist\SwiftCopy.exe` (icon.ico) |
| Linux | `bash build_linux.sh` | `dist/SwiftCopy` (icon.png) |
| macOS | `bash build_macos.sh` | `dist/SwiftCopy.app` (icon.icns) |

---

## Deployment & Installation

One command builds the executable **and** the platform installer:

```bash
python build_configs/build.py install
```

### Windows — `deployment/windows/`
- `installer.iss` — [Inno Setup](https://jrsoftware.org/isinfo.php) installer script → `dist\installers\SwiftCopy-Setup-1.0.0.exe`
- `build_installer.bat` — build + auto-compile installer (if Inno Setup is installed)
- Produces an installation wizard with Start Menu + desktop shortcuts, using the `.ico` app icon.

### macOS — `deployment/macos/`
- `build_dmg.sh` — builds `SwiftCopy.app` (with `icon.icns`) then creates `dist/SwiftCopy-1.0.0-macOS.dmg`
- The `.dmg` supports drag-and-drop into `/Applications`. Includes commented steps for code-signing and notarization (requires an Apple Developer ID).

### Linux — `deployment/linux/`
- `build_deb.sh` — build and package into:
  - `dist/swiftcopy_1.0.0_amd64.deb`  (Debian/Ubuntu install)
  - `dist/SwiftCopy-x86_64.AppImage` (portable)
  - `dist/swiftcopy-1.0.0-linux-x86_64.tar.gz`
- Install the `.deb` with: `sudo dpkg -i dist/swiftcopy_1.0.0_amd64.deb`

> **Note:** PyInstaller does not cross-compile, so build each executable on its own OS (run `build.py install` on each platform).

---

## Project Structure

```
SwiftCopy/
├── main.py                  # PyQt6 application + entry point
├── requirements.txt
├── engines/                 # Core back-end engines
│   ├── copy_engine.py       # Multi-threaded copy (xcopy/rsync/cp) + verify + resume
│   ├── archive_engine.py    # ZIP / 7z / ISO / TAR + extract
│   └── split_engine.py      # Split & merge with SHA-256 manifests
├── ui/                      # (future) UI helpers
├── assets/
│   ├── logo.png             # <-- brand logo (NOT the app icon)
│   ├── swiftcopy.png        # <-- the application icon source
│   ├── icon.ico / icon.png  # generated app icons (per platform)
│   └── icon.icns            # macOS app icon (generated on macOS)
├── deployment/
│   ├── linux/               # .deb / AppImage / tar.gz packager
│   ├── windows/             # Inno Setup installer
│   └── macos/               # .dmg packager
└── build_configs/
    ├── build.py             # Cross-platform build + installer entry point
    ├── make_icons.py        # Generates .ico / .png / .icns from swiftcopy.png
    ├── build_linux.sh
    ├── build_windows.bat
    └── build_macos.sh
```

---

## Using the App

1. **Copy tab** — pick Source & Destination, configure workers/buffer/verification/filters, hit **Start Copy**.
2. **Archive tab** — choose source folder/file and output path, pick format (ZIP/7z/ISO/TAR), compression, optional password, create.
3. **Split/Merge tab** — split a large file into parts (with size presets), or merge parts back using the manifest.
4. **Settings tab** — configure defaults and paths.
5. **History tab** — review all past transfers. 
6. **Title bar** — use the custom minimize / maximize / close buttons, drag to move, double-click to toggle maximize.

---

## License
© 2026 **ChainIT** — All rights reserved.

**Author:** newan0805

- **ChainIT:** https://chainit.vercel.app
- **Author site:** https://newan0805.vercel.app

