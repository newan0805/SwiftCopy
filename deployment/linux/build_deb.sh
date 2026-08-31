#!/bin/bash
# ============================================================
# SwiftCopy - Linux Deployment Script
# Builds the executable then creates:
#   1. dist/SwiftCopy           (PyInstaller binary with app icon)
#   2. dist/SwiftCopy.AppImage  (portable AppImage)
#   3. dist/swiftcopy_*.deb     (Debian/Ubuntu installer)
#   4. dist/swiftcopy-*.tar.gz  (portable tarball)
# ============================================================
set -e
cd "$(dirname "$0")/../.."
ROOT="$(pwd)"

echo "[*] SwiftCopy Linux Deployment"
echo "[*] Project root: $ROOT"

# --- 1. Install build dependencies ---
PY=python3
if [ -f .venv/bin/python ]; then
    PY=.venv/bin/python
fi
"$PY" -m pip install pyinstaller pillow 2>/dev/null || \
    "$PY" -m pip install --user pyinstaller pillow

# --- 2. Build the executable with PyInstaller ---
echo "[*] Building executable..."
"$PY" build_configs/build.py linux

# --- 3. Verify binary exists ---
BIN="$ROOT/dist/SwiftCopy"
if [ ! -f "$BIN" ]; then
    echo "[!] Binary not found: $BIN"; exit 1
fi

# --- 4. Install icon to app icon set ---
echo "[*] Installing icon..."
mkdir -p "$ROOT/dist/icons"
cp "$ROOT/assets/icon.png" "$ROOT/dist/icons/swiftcopy.png"

# --- 5. Create AppImage (portable) ---
echo "[*] Preparing AppImage..."
APPDIR="$ROOT/dist/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps" \
         "$APPDIR/usr/share/icons/hicolor/scalable/apps"
cp "$BIN" "$APPDIR/usr/bin/SwiftCopy"
cp "$ROOT/deployment/linux/SwiftCopy.desktop" "$APPDIR/usr/share/applications/"
cp "$ROOT/assets/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/swiftcopy.png"
cp "$ROOT/assets/icon.png" "$APPDIR/usr/share/icons/hicolor/scalable/apps/swiftcopy.png"
chmod +x "$APPDIR/usr/bin/SwiftCopy"

# Try to build an actual .AppImage by downloading linuxdeploy (best effort)
if [ ! -x "$ROOT/dist/linuxdeploy-x86_64.AppImage" ]; then
    echo "[*] Downloading linuxdeploy..."
    curl -sL -o "$ROOT/dist/linuxdeploy-x86_64.AppImage" \
        "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage" \
        && chmod +x "$ROOT/dist/linuxdeploy-x86_64.AppImage" \
        || echo "[i] Could not download linuxdeploy (AppImage skipped)."
fi
if [ -x "$ROOT/dist/linuxdeploy-x86_64.AppImage" ]; then
    echo "[*] Building AppImage..."
    # linuxdeploy needs an Exec that resolves inside the AppDir, so create a
    # dedicated desktop file pointing at the bundled binary (usr/bin/SwiftCopy).
    cat > "$APPDIR/usr/share/applications/SwiftCopy.desktop" <<DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=SwiftCopy
GenericName=File Transfer
Comment=Bulk file copy, archive, and split-merge tool
Exec=SwiftCopy
Icon=swiftcopy
Terminal=false
Categories=Utility;FileTools;Archiving;
StartupNotify=true
DESKTOP
    ( cd "$ROOT/dist" && \
      ARCH=x86_64 ./linuxdeploy-x86_64.AppImage \
        --appdir "$APPDIR" \
        --output appimage \
        --icon-file "$ROOT/assets/icon.png" \
        --desktop-file "$APPDIR/usr/share/applications/SwiftCopy.desktop" ) || \
        echo "[!] AppImage build failed (continuing with .deb)."
fi

# --- 6. Create .deb package (Debian/Ubuntu) ---
echo "[*] Creating .deb package..."
PKG="$ROOT/dist/debpkg"
PKGVER="1.0.0"
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" \
         "$PKG/usr/bin" \
         "$PKG/usr/share/applications" \
         "$PKG/usr/share/icons/hicolor/256x256/apps" \
         "$PKG/usr/share/doc/swiftcopy"

cat > "$PKG/DEBIAN/control" <<EOF
Package: swiftcopy
Version: $PKGVER
Section: utils
Priority: optional
Architecture: amd64
Maintainer: newan0805 <newan0805@example.com>
Homepage: https://newan0805.vercel.app
Description: Bulk file copy, archive, and split-merge tool
 A modern cross-platform file transfer application with bulk copy,
 archiving (ZIP/7z/ISO/TAR), and file split/merge capabilities.
Depends: libc6 (>= 2.28)
EOF

cp "$BIN" "$PKG/usr/bin/SwiftCopy"
cp "$ROOT/deployment/linux/SwiftCopy.desktop" "$PKG/usr/share/applications/"
sed -i 's|Exec=/usr/bin/SwiftCopy|Exec=/usr/bin/SwiftCopy|' "$PKG/usr/share/applications/SwiftCopy.desktop"
cp "$ROOT/assets/icon.png" "$PKG/usr/share/icons/hicolor/256x256/apps/swiftcopy.png"
echo "SwiftCopy package builder" > "$PKG/usr/share/doc/swiftcopy/changelog.Debian.gz" 2>/dev/null || true
# Placeholder changelog (gzip)
echo "SwiftCopy v$PKGVER" | gzip > "$PKG/usr/share/doc/swiftcopy/changelog.Debian.gz"

chmod -R 755 "$PKG"
# Build deb with dpkg if available, else warn
if command -v dpkg-deb >/dev/null 2>&1; then
    dpkg-deb --build --root-owner-group "$PKG" "$ROOT/dist/swiftcopy_${PKGVER}_amd64.deb"
    echo "[+] Created dist/swiftcopy_${PKGVER}_amd64.deb"
else
    echo "[!] dpkg-deb not found - .deb not created (install dpkg or use the raw binary)"
fi

# --- 7. Create portable tarball ---
echo "[*] Creating tarball..."
tar -czf "$ROOT/dist/swiftcopy-${PKGVER}-linux-x86_64.tar.gz" -C "$ROOT/dist" SwiftCopy icons
echo "[+] Created dist/swiftcopy-${PKGVER}-linux-x86_64.tar.gz"

echo
echo "[===========================================]"
echo "[+] Linux deployment complete!"
echo "[+] Artifacts in dist/:"
ls -lh "$ROOT/dist"/SwiftCopy* 2>/dev/null || true
echo "[===========================================]"
