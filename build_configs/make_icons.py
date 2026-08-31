#!/usr/bin/env python3
"""
Generate platform-specific application ICONS from the app icon image.

Source image: assets/swiftcopy.png  (the application icon)
Produces:
  - assets/icon.ico      (Windows - multi-size ICO)
  - assets/icon.icns     (macOS - ICNS bundle, requires iconutil - mac only)
  - assets/icon.png      (Linux - 256x256)
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT / "assets"

# Source: the application icon (NOT the logo). Fall back to logo if absent.
APP_ICON = ASSETS / "swiftcopy.png"
if not APP_ICON.exists():
    APP_ICON = ASSETS / "logo.png"


def make_sizes(img: Image.Image, sizes):
    frames = []
    for s in sizes:
        im = img.copy()
        im.thumbnail((s, s), Image.Resampling.LANCZOS)
        # Pad to exact square with alpha
        canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        canvas.paste(im, ((s - im.width) // 2, (s - im.height) // 2), im)
        frames.append(canvas)
    return frames


def win_ico():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    img = Image.open(APP_ICON).convert("RGBA")
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    img.thumbnail((256, 256), Image.Resampling.LANCZOS)
    canvas.paste(img, ((256 - img.width) // 2, (256 - img.height) // 2), img)
    canvas.save(ASSETS / "icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("[+] icon.ico generated")


def png():
    img = Image.open(APP_ICON).convert("RGBA")
    img.thumbnail((256, 256), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    canvas.paste(img, ((256 - img.width) // 2, (256 - img.height) // 2), img)
    canvas.save(ASSETS / "icon.png", format="PNG")
    print("[+] icon.png generated")


def mac_icns():
    if sys.platform != "darwin":
        print("[!] mac_icns skipped (requires macOS iconutil)")
        return
    iconset = ASSETS / "icon.iconset"
    iconset.mkdir(exist_ok=True)
    img = Image.open(APP_ICON).convert("RGBA")
    spec = {
        "icon_16x16.png": 16, "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32, "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128, "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256, "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512, "icon_512x512@2x.png": 1024,
    }
    for name, size in spec.items():
        im = img.copy()
        im.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
        canvas.save(iconset / name, format="PNG")
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(ASSETS / "icon.icns")], check=True)
    shutil.rmtree(iconset)
    print("[+] icon.icns generated")


if __name__ == "__main__":
    win_ico()
    png()
    mac_icns()
    print("[+] Icon generation complete")

