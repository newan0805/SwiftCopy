#!/bin/bash
# ============================================================
# SwiftCopy - macOS Build & Installer Creator
# Builds SwiftCopy.app (with icon.icns), then packages a .dmg
# installer along with an optional notarization step.
# ============================================================
set -e
cd "$(dirname "$0")/../.."
ROOT="$(pwd)"

PY=python3
if [ -f .venv/bin/python ]; then
    PY=.venv/bin/python
fi

echo "[*] SwiftCopy macOS Build & Installer"
echo "[*] Project root: $ROOT"

# --- 1. Install build dependencies ---
echo "[*] Installing build dependencies..."
"$PY" -m pip install --upgrade pyinstaller pillow

# --- 2. Generate icon.icns (macOS only - uses iconutil) ---
echo "[*] Generating icon.icns..."
"$PY" build_configs/make_icons.py
if [ ! -f assets/icon.icns ]; then
    echo "[!] icon.icns not generated. Ensure you are on macOS."; exit 1
fi

# --- 3. Build the .app bundle ---
echo "[*] Building SwiftCopy.app..."
"$PY" build_configs/build.py macos
APP="$ROOT/dist/SwiftCopy.app"
if [ ! -d "$APP" ]; then
    echo "[!] SwiftCopy.app not found. Build failed."; exit 1
fi

# --- 4. Force the app icon into the bundle (best-effort) ---
find "$APP" -maxdepth 5 -name "*.icns" -exec rm -f {} \; 2>/dev/null || true
mkdir -p "$APP/Contents/Resources"
cp "$ROOT/assets/icon.icns" "$APP/Contents/Resources/SwiftCopy.icns"

# --- 5. Create the .dmg installer ---
echo "[*] Creating .dmg..."
DMG_STAGING="$ROOT/dist/dmg-staging"
rm -rf "$DMG_STAGING"
mkdir -p "$DMG_STAGING"
cp -R "$APP" "$DMG_STAGING/"
# Symlink to /Applications for drag-drop install
ln -sf /Applications "$DMG_STAGING/Applications"

DMG_NAME="SwiftCopy-1.0.0-macOS.dmg"
DMG_PATH="$ROOT/dist/$DMG_NAME"
rm -f "$DMG_PATH"

if command -v hdiutil >/dev/null 2>&1; then
    hdiutil create -volname "SwiftCopy" \
        -srcfolder "$DMG_STAGING" \
        -ov -format UDZO \
        "$DMG_PATH"
    rm -rf "$DMG_STAGING"
    echo "[+] Created dist/$DMG_NAME"
else
    echo "[!] hdiutil not available - .dmg not created."
    echo "    The .app bundle is at: $APP"
fi

# --- 6. Optional: sign & notarize (requires Apple Developer ID) ---
# Uncomment and set your identity to enable:
# CODESIGN_ID="Developer ID Application: Your Name (TEAMID)"
# codesign --force --deep --sign "$CODESIGN_ID" "$APP"
# 
# xcrun notarytool submit "$DMG_PATH" \
#     --apple-id "$APPLE_ID" \
#     --team-id "$TEAM_ID" \
#     --password "$APP_SPECIFIC_PASSWORD" \
#     --wait

echo
echo "[===========================================]"
echo "[+] macOS deployment complete!"
echo "[+] App bundle: dist/SwiftCopy.app"
echo "[+] Installer:  dist/$DMG_NAME"
echo "[===========================================]"
