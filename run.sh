#!/usr/bin/env bash
set -euo pipefail

cmd=${1:-help}
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
		ensure_venv
		python -m grant_ai.gui.qt_app
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
Usage: ./run.sh <command>

Commands:
	setup               Create venv and install dependencies
	check               Lint, format check, types, security
	test                Run full test suite with coverage
	test-unit           Run unit tests only
	test-integration    Run integration tests only
	lint                Run linter
	format              Auto-format code (black + isort)
	gui                 Launch the GUI
	run [args...]       Run CLI entrypoint with args
	analyze-performance Run performance analysis
USAGE
		;;
esac





