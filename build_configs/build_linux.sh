#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 -m pip install --user pyinstaller pillow 2>/dev/null || pip install pyinstaller pillow
python3 build_configs/build.py linux
