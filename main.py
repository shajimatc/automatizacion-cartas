import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


def load_stylesheet():
    project_root = Path(__file__).resolve().parent

    style_path = (
        project_root
        / "app"
        / "styles"
        / "app.qss"
    )

    return style_path.read_text(
        encoding="utf-8"
    )


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet(
        load_stylesheet()
    )

    window = MainWindow()
    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()