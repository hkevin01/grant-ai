#!/usr/bin/env bash
set -euo pipefail

# Create venv if missing and install GUI deps, then launch GUI
VENV_DIR="${VENV_DIR:-venv}"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
# Install core + GUI optional deps (viz optional for analytics dashboards)
pip install -e ".[gui,viz]"
# Launch classic Qt GUI
exec python -m grant_ai.gui.qt_app
