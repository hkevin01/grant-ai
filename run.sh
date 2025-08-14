#!/usr/bin/env bash
set -euo pipefail

# Default to launching the GUI in Docker when no command is provided
cmd=${1:-gui-docker}
shift || true

venv_dir="venv"

ensure_venv() {
	if [[ ! -d "$venv_dir" ]]; then
		echo "Creating virtual environment..."
		python3 -m venv "$venv_dir"
	fi
	# shellcheck disable=SC1090
	source "$venv_dir/bin/activate"
}

docker_gui() {
	if ! command -v docker >/dev/null 2>&1; then
		echo "Docker is not installed or not in PATH. Falling back to local GUI..." >&2
		# Fallback to local GUI
		ensure_venv
		# Best-effort install for PyQt5 if missing
		python - <<'PY'
try:
	import PyQt5  # noqa: F401
except Exception:
	import subprocess, sys
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyQt5'])
PY
		python -m grant_ai.gui.qt_app
		return 0
	fi

	local image="grant-ai:dev"

	# Build the development image if missing
	if ! docker image inspect "$image" >/dev/null 2>&1; then
		echo "Building Docker image ($image) with development target..."
		docker build -t "$image" --target development .
	fi

	# Loosen X access for local docker if xhost is available (best-effort)
	if command -v xhost >/dev/null 2>&1; then
		xhost +si:localuser:root >/dev/null 2>&1 || \
		xhost +local:root >/dev/null 2>&1 || \
		xhost +local: >/dev/null 2>&1 || true
	fi

	# Ensure bind-mount folders exist
	mkdir -p data reports logs

	echo "Launching GUI inside Docker (X11 forwarding)..."
	docker run --rm \
		--name grant-ai-gui \
		-e DISPLAY="${DISPLAY:-:0}" \
		-e QT_X11_NO_MITSHM=1 \
		-e QT_QPA_PLATFORM=xcb \
		-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
		-v "$(pwd)/data:/app/data" \
		-v "$(pwd)/reports:/app/reports" \
		-v "$(pwd)/logs:/app/logs" \
		-v "$(pwd):/app" \
		--network host \
		"$image" \
		bash -lc "python -m pip install --no-cache-dir PyQt5 && python -m grant_ai.gui.qt_app"
}

case "$cmd" in
	setup)
		ensure_venv
		python -m pip install --upgrade pip
		pip install -e ".[dev]"
		echo "Setup complete. Activate with: source $venv_dir/bin/activate"
		;;

	check)
		ensure_venv
		pip install ruff black mypy isort bandit safety
		echo "Running checks..."
		black --check src/ tests/ scripts/
		isort --check-only src/ tests/ scripts/
		ruff check src/ tests/ scripts/
		mypy src/
		bandit -r src/ -q || true
		safety check || true
		;;

	test)
		ensure_venv
		pytest tests/ -v --cov=src/grant_ai --cov-report=term-missing --cov-report=xml --cov-report=html
		;;

	test-unit)
		ensure_venv
		pytest tests/unit/ -v --cov=src/grant_ai --cov-report=term-missing
		;;

	test-integration)
		ensure_venv
		pytest tests/integration/ -v --cov=src/grant_ai --cov-report=term-missing
		;;

	lint)
		ensure_venv
		ruff check src/ tests/ scripts/
		;;

	format)
		ensure_venv
		black src/ tests/ scripts/
		isort src/ tests/ scripts/
		;;

	gui)
		if [[ "${USE_DOCKER_GUI:-0}" == "1" ]]; then
			docker_gui
		else
			ensure_venv
			python -m grant_ai.gui.qt_app
		fi
		;;

	gui-docker)
		docker_gui
		;;

	gui-check)
		# Headless GUI import smoke test (Docker by default)
		if command -v docker >/dev/null 2>&1; then
			image="grant-ai:dev"
			if ! docker image inspect "$image" >/dev/null 2>&1; then
				echo "Building Docker image ($image) with development target for GUI check..."
				docker build -t "$image" --target development .
			fi
			echo "Running headless GUI smoke test inside Docker..."
			docker run --rm \
				-e QT_QPA_PLATFORM=offscreen \
				-v "$(pwd)":/app \
				"$image" \
				bash -lc "python -m pip install --no-cache-dir PyQt5 && python -c 'import os; os.environ[\"QT_QPA_PLATFORM\"]=\"offscreen\"; from PyQt5.QtWidgets import QApplication; app=QApplication([]); import grant_ai.gui.qt_app as qt_app; print(\"GUI import OK\"); app.quit()'"
		else
			echo "Docker not available; running headless GUI smoke test locally..." >&2
			ensure_venv
			python - <<'PY'
import sys, subprocess, os
try:
    import PyQt5  # noqa: F401
except Exception:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyQt5'])
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt5.QtWidgets import QApplication
app = QApplication([])
import grant_ai.gui.qt_app as qt_app
print('GUI import OK')
app.quit()
PY
		fi
		;;

	wv-offline)
		# Deterministic WV scraper run without network
		ensure_venv
		# Ensure package is installed for import resolution (non-fatal)
		pip install -e ".[dev]" >/dev/null 2>&1 || pip install -e . >/dev/null 2>&1 || true
		python - <<'PY'
from grant_ai.scrapers.wv_grants import scrape_wv_grants
grants = scrape_wv_grants(offline=True, max_results=2)
print(f"Offline WV grants total: {len(grants)}")
for g in grants[:10]:
    print(f"- {g.title} | {g.funder_name}")
PY
		;;

	run)
		ensure_venv
		python -m grant_ai.core.cli "$@"
		;;

	analyze-performance)
		ensure_venv
		python scripts/analyze_performance.py
		;;

	*)
		cat <<USAGE
Grant AI runner
Usage: ./run.sh [command]

Default behavior: launches the GUI inside Docker (falls back to local GUI if Docker is unavailable).

Commands:
	setup               Create venv and install dependencies
	check               Lint, format check, types, security
	test                Run full test suite with coverage
	test-unit           Run unit tests only
	test-integration    Run integration tests only
	lint                Run linter
	format              Auto-format code (black + isort)
	gui                 Launch the GUI locally (set USE_DOCKER_GUI=1 to use Docker)
	gui-docker          Launch the GUI inside Docker (X11 forwarding)
	gui-check           Headless GUI smoke test (Docker by default)
	run [args...]       Run CLI entrypoint with args
	analyze-performance Run performance analysis
USAGE
		;;
esac





