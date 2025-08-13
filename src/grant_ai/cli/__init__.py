"""
CLI commands package for Grant AI.

We intentionally avoid importing submodules here to prevent heavy or optional
dependencies (like PyQt5 for the GUI) from being imported at package import
time. Callers should import specific command modules directly, for example:

    from grant_ai.cli.ai_commands import ai

This keeps the CLI modular and avoids ModuleNotFoundError for optional extras.
"""

# Export list intentionally empty to avoid triggering imports via
# 'from grant_ai.cli import *' which would import submodules.
__all__: list[str] = []
