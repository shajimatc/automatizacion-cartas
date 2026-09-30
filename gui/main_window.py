from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from app.config.settings import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)

from app.gui.pages.home_page import HomePage
from app.gui.pages.process_a_page import ProcessAPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)

        self.resize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        self.setup_pages()

    def setup_pages(self):
        self.stack = QStackedWidget()

        self.home_page = HomePage()
        self.process_a_page = ProcessAPage()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.process_a_page)

        self.setCentralWidget(self.stack)

        self.home_page.open_process_a.connect(
            self.show_process_a
        )

        self.process_a_page.back_requested.connect(
            self.show_home
        )

        self.show_home()

    def show_home(self):
        self.stack.setCurrentWidget(
            self.home_page
        )

    def show_process_a(self):
        self.stack.setCurrentWidget(
            self.process_a_page
        )