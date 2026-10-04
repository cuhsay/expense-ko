from PyQt6.QtWidgets import(
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
)
from pathlib import Path
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

CAT_PATH = Path(__file__).resolve().parent.parent.parent / "images" / "cat.jpg"

class AllowancePage(QWidget):
    def __init__(self, manager, storage):
        super().__init__()
        self.manager = manager
        self.storage = storage

        layout = QVBoxLayout(self)

        title = QLabel("Allowance")
        title.setObjectName("title")
        layout.addWidget(title)

        self.current_label = QLabel()
        layout.addWidget(self.current_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        layout.addWidget(self.amount_input)

        buttons = QHBoxLayout()
        add_button = QPushButton("Add allowance")
        add_button.clicked.connect(self.add_allowance)
        edit_button = QPushButton("Set allowance")
        edit_button.clicked.connect(self.edit_allowance)
        buttons.addWidget(add_button)
        buttons.addWidget(edit_button)
        layout.addLayout(buttons)

        self.message = QLabel("")
        layout.addWidget(self.message)

        cat = QLabel()
        pixmap = QPixmap(str(CAT_PATH)).scaled(
            420, 420,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        cat.setPixmap(pixmap)
        layout.addWidget(cat, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()


    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def refresh(self):
        self.current_label.setText(
            f"Current allowance: ₱{self.manager.user.allowance:,.2f}"
        )

    def read_amount(self):
        try:
            return float(self.amount_input.text())
        except ValueError:
            self.message.setText("Amount must be a number.")
            return None

    def add_allowance(self):
        amount = self.read_amount()
        if amount is None:
            return
        try:
            self.manager.add_allowance(amount)
        except ValueError as e:
            self.message.setText(str(e))
            return
        self.finish("Allowance added!")

    def edit_allowance(self):
        amount = self.read_amount()
        if amount is None:
            return
        try:
            self.manager.edit_allowance(amount)
        except ValueError as e:
            self.message.setText(str(e))
            return
        self.finish("Allowance updated!")

    def finish(self, text):
        self.storage.save(self.manager.user)
        self.refresh()
        self.message.setText(text)
        self.amount_input.clear()