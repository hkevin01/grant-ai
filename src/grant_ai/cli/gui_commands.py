"""
CLI commands for launching the modernized Grant-AI GUI
"""
import click

from grant_ai.gui.modern_ui import create_modern_app


@click.group()
def gui():
    """GUI interface commands for Grant-AI"""


@gui.command()
def modern():
    """Launch the modern Material Design GUI"""
    click.echo("🚀 Launching Grant-AI Modern Interface...")
    click.echo("✨ Material Design 3.0 theme loaded")

    try:
        app, _ = create_modern_app()
        click.echo("🎯 Modern interface ready!")
        app.exec_()
    except Exception as e:
        click.echo(f"❌ Failed to launch modern GUI: {e}")
        raise click.Abort()


@gui.command()
def classic():
    """Launch the classic PyQt5 GUI"""
    click.echo("🔄 Launching Grant-AI Classic Interface...")

    try:
        import sys

        from PyQt5.QtWidgets import QApplication

        from grant_ai.gui.qt_app import MainWindow

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        click.echo("📱 Classic interface ready!")
        app.exec_()
    except Exception as e:
        click.echo(f"❌ Failed to launch classic GUI: {e}")
        raise click.Abort()


if __name__ == '__main__':
    gui()

if __name__ == '__main__':
    gui()
