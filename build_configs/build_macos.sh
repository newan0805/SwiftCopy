#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 -m pip install --user pyinstaller pillow
python3 build_configs/build.py macos
