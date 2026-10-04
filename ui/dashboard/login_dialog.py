from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExpenseKo")
        self.setFixedSize(380, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        title = QLabel("Welcome to ExpenseKo")
        title.setObjectName("title")
        layout.addWidget(title)

        hbox1 = QHBoxLayout()
        subtitle = QLabel("What should we call you?")
        subtitle.setObjectName("tagline")

        pixmap = QPixmap("images/mingming.png").scaled(
            60, 60,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        image = QLabel()
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hbox1.addWidget(subtitle)
        hbox1.addWidget(image)
        layout.addLayout(hbox1)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your preferred name")
        self.name_input.returnPressed.connect(self.submit)
        layout.addWidget(self.name_input)

        button = QPushButton("Continue")
        button.clicked.connect(self.submit)
        layout.addWidget(button)

        self.message = QLabel("")
        layout.addWidget(self.message)

        layout.addStretch()

    def submit(self):
        if not self.name_input.text().strip():
            self.message.setText("Please enter a name.")
            return
        self.accept()

    def get_name(self):
        return self.name_input.text().strip()