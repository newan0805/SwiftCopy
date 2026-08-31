# SwiftCopy v1.0.0 — Release Notes

**August 31, 2026 · © 2026 ChainIT · Author: newan0805**
**Sites:** [chainit.vercel.app](https://chainit.vercel.app) · [newan0805.vercel.app](https://newan0805.vercel.app)

---

## What's New

### 🖥️ Cross-Platform Deployment & Installation
SwiftCopy can now be built and installed on **Windows, macOS, and Linux** with real installers:

- **Windows** — Inno Setup installer (`SwiftCopy-Setup-1.0.0.exe`) with Start Menu + desktop shortcuts
- **macOS** — Drag-and-drop `.dmg` installer (`SwiftCopy-1.0.0-macOS.dmg`) with optional code-signing/notarization support
- **Linux** — `.deb` package, portable `.AppImage`, and `.tar.gz`

Build everything with one command: `python build_configs/build.py install`

### 🎨 Application Icon (not the logo)
- Executables now use the dedicated **application icon** (`swiftcopy.png`) — converted to `.ico` (Windows), `.icns` (macOS), and `.png` (Linux)
- The icon is embedded directly in Windows/macOS binaries and shown in the window, title bar, and taskbar
- The brand logo (`logo.png`) is kept separate as a branding asset

### 🚀 Existing Features (from earlier work)
- **Bulk copy** with cross-platform engines (xcopy / rsync / cp), MD5 verification, resume support
- **Archiving** — ZIP / 7z / ISO / TAR creation and extraction
- **File split & merge** with SHA-256 manifests for integrity
- **Modern dark GitHub-style UI** — frameless window with custom title bar, drag/resize, minimize/maximize/close
- **"Include parent folder"** option for copy operations
- **Responsive UI** — content tabs scroll on small windows
- **Crash-proofing** — guards against duplicate operations and safe worker shutdown
- Full branding: status bar, About dialog, and footer with copyright + site links

---

## Artifacts

| Platform | Installer | Portable binary |
|----------|-----------|-----------------|
| Windows | `SwiftCopy-Setup-1.0.0.exe` | `SwiftCopy.exe` |
| macOS | `SwiftCopy-1.0.0-macOS.dmg` | `SwiftCopy.app` |
| Linux | `swiftcopy_1.0.0_amd64.deb` | `SwiftCopy-x86_64.AppImage` |

---

## Installation

| Platform | Command |
|----------|---------|
| Windows | Run `SwiftCopy-Setup-1.0.0.exe` |
| macOS | Open the `.dmg`, drag `SwiftCopy.app` to Applications |
| Linux (Debian/Ubuntu) | `sudo dpkg -i swiftcopy_1.0.0_amd64.deb` |
| Linux (portable) | `./SwiftCopy-x86_64.AppImage` |

---

## Notes
- Binaries must be built on their respective OS (PyInstaller does not cross-compile)
- macOS `.icns` is generated automatically when building on a Mac

---

## Changelog

### v1.0.0 (2026-08-31)
- **Added:** Cross-platform deployment & installers (Inno Setup `.exe`, macOS `.dmg`, Linux `.deb`/`.AppImage`/`.tar.gz`)
- **Changed:** Application icon now derived from `swiftcopy.png`; executables embed the app icon for all platforms
- **Added:** One-command build+install: `python build_configs/build.py install`
- **Added:** Platform build helper scripts and README deployment documentation
