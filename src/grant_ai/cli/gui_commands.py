"""CLI commands for launching Grant-AI GUIs (modern and classic).

PyQt5 is optional. To avoid import-time failures when PyQt5 is not installed,
GUI modules are imported lazily inside command functions.
"""

import click


@click.group()
def gui():
    """GUI interface commands for Grant-AI."""


@gui.command()
def modern():
    """Launch the modern Material Design GUI."""
    click.echo("🚀 Launching Grant-AI Modern Interface...")
    click.echo("✨ Material Design 3.0 theme loaded")

    try:
        # Lazy import to avoid requiring PyQt5 unless this command is used
        from grant_ai.gui.modern_ui import create_modern_app

        app, _ = create_modern_app()
        click.echo("🎯 Modern interface ready!")
        app.exec_()
    except ImportError as e:
        click.echo(f"❌ Missing dependency: {e}")
        click.echo("💡 Install GUI extras: pip install -e .[gui]")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Failed to launch modern GUI: {e}")
        raise click.Abort()


@gui.command()
def classic():
    """Launch the classic PyQt5 GUI."""
    click.echo("🔄 Launching Grant-AI Classic Interface...")

    try:
        import sys

        from PyQt5.QtWidgets import QApplication  # type: ignore[attr-defined]

        from grant_ai.gui.qt_app import MainWindow

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        click.echo("📱 Classic interface ready!")
        app.exec_()
    except ImportError as e:
        click.echo(f"❌ Missing dependency: {e}")
        click.echo("💡 Install GUI extras: pip install -e .[gui]")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Failed to launch classic GUI: {e}")
        raise click.Abort()


