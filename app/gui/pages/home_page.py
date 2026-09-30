from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)


class HomePage(QWidget):
    open_process_a = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 50, 60, 50)
        main_layout.setSpacing(30)

        title = QLabel("Generación de Cartas")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Seleccione el tipo de proceso que desea gestionar."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        card_a = self.create_process_card(
            title="Proceso A",
            description="Generación de cartas correspondientes al Proceso A.",
            button_text="Ingresar",
            enabled=True,
        )

        card_b = self.create_process_card(
            title="Proceso B",
            description="Módulo preparado para desarrollo posterior.",
            button_text="Próximamente",
            enabled=False,
        )

        card_c = self.create_process_card(
            title="Proceso C",
            description="Módulo preparado para desarrollo posterior.",
            button_text="Próximamente",
            enabled=False,
        )

        cards_layout.addWidget(card_a)
        cards_layout.addWidget(card_b)
        cards_layout.addWidget(card_c)

        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

    def create_process_card(
        self,
        title,
        description,
        button_text,
        enabled,
    ):
        card = QFrame()
        card.setObjectName("processCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        card_title = QLabel(title)
        card_title.setObjectName("cardTitle")

        card_description = QLabel(description)
        card_description.setObjectName("cardDescription")
        card_description.setWordWrap(True)

        button = QPushButton(button_text)
        button.setEnabled(enabled)

        if title == "Proceso A":
            button.clicked.connect(self.open_process_a.emit)

        layout.addWidget(card_title)
        layout.addWidget(card_description)
        layout.addStretch()
        layout.addWidget(button)

        return card