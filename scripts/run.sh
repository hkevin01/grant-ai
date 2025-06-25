#!/bin/bash
# Run the Grant Research AI Project (CLI or GUI)

# Activate virtual environment if exists
test -d .venv && source .venv/bin/activate

# Run the CLI or GUI based on argument
if [ "$1" == "gui" ]; then
    python3 -m grant_ai.gui.qt_app
else
    python3 -m grant_ai.cli "$@"
fi
