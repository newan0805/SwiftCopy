@echo off
cd /d "%~dp0.."
pip install pyinstaller pillow
python build_configs\build.py windows
pause
