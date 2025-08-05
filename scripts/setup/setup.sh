#!/bin/bash

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in development mode
pip install -e .[dev]

# Run setup script
python scripts/setup.py
