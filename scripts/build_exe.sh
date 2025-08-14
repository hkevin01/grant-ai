#!/usr/bin/env bash
set -euo pipefail

# Build a standalone GUI executable using PyInstaller.
# Requires: pip install pyinstaller

VENV_DIR="${VENV_DIR:-venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -e ".[gui,viz]" pyinstaller

# Clean previous build artifacts
rm -rf build dist *.spec || true

# Build as a windowed app (no console), single folder for better PyQt5 support
pyinstaller \
  -n grant-ai-gui \
  -w \
  --hidden-import PyQt5.sip \
  --collect-submodules PyQt5 \
  --collect-data PyQt5 \
  -m grant_ai.gui.qt_app

echo "Executable built in dist/grant-ai-gui/"
