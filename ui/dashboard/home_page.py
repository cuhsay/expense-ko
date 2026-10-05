from datetime import date
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from typing import override

KITTY_PATH = Path(__file__).resolve().parent.parent.parent / "images" / "kitty.png"

class HomePage(QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        self.welcome = QLabel()
        self.welcome.setObjectName("welcome")
        layout.addWidget(self.welcome)

        tagline = QLabel("Keep track of your allowance and see where your money goes.")
        tagline.setObjectName("tagline")
        layout.addWidget(tagline)

        cards = QHBoxLayout()
        allowance_card, self.allowance_value = self.make_card("Remaining allowance")
        today_card, self.today_value = self.make_card("Spent today")
        cards.addWidget(allowance_card)
        cards.addWidget(today_card)
        layout.addLayout(cards)

        layout.addSpacing(16)

        kitty = QLabel()
        pixmap = QPixmap(str(KITTY_PATH)).scaled(
            420, 420,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        kitty.setPixmap(pixmap)
        layout.addWidget(kitty, 1, Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def make_card(self, caption):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        caption_label = QLabel(caption)
        caption_label.setObjectName("caption")
        value_label = QLabel()
        value_label.setObjectName("value")
        card_layout.addWidget(caption_label)
        card_layout.addWidget(value_label)
        return card, value_label

    @override
    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def refresh(self):
        user = self.tracker.user
        today = str(date.today())
        _, spent_today = self.tracker.get_category_totals(today, today)
        self.welcome.setText(f"Welcome, {user.name}!")
        self.allowance_value.setText(f"₱{user.allowance:,.2f}")
        self.today_value.setText(f"₱{spent_today:,.2f}")