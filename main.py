import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QInputDialog,
)
from database.database import Storage
from allowance_management.allowance_manager import AllowanceManager
from expense_tracking.expense_tracker import ExpenseTracker
from ui.dashboard.home_page import HomePage
from ui.dashboard.expense_page import ExpensePage
from ui.dashboard.allowance_page import AllowancePage
from ui.dashboard.summary_page import SummaryPage
from ui.dashboard.compare_page import ComparePage
from ui.dashboard.login_dialog import LoginDialog

import traceback

def show_error(exc_type, exc, tb):
    traceback.print_exception(exc_type, exc, tb)

sys.excepthook = show_error

STYLE = """
QWidget { background: #FFFFFF; color: #000000; font-size: 14px; }
QLabel { background: transparent; }
QWidget#sidebar { background: #FFF1F4; }
QPushButton[nav="true"] {
    background: transparent; color: #000000; text-align: left;
    padding: 10px 16px; border: none; border-radius: 20px;
}
QPushButton[nav="true"]:hover { background: #FFE0E8; }

QLabel#title { font-size: 22px; font-weight: bold; }
QLabel#welcome { font-size: 30px; font-weight: bold; }
QLabel#tagline { color: #5D4A51; font-size: 15px; }
QFrame#card { background: #FFF1F4; border: 1px solid #F0D4DC; border-radius: 16px; }
QLabel#caption { color: #5D4A51; }
QLabel#value { font-size: 26px; font-weight: bold; color: #B0285A; }
QLabel#message { font-size: 15px; font-weight: bold; color: #B0285A; }

QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #FFFFFF; border: 1px solid #D8B4BF; border-radius: 8px; padding: 6px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #FF7FA6;
}
QPushButton {
    background: #FFB1C8; color: #000000; border: none;
    border-radius: 20px; padding: 8px 18px; font-weight: bold;
}
QPushButton:hover { background: #FF9DBB; }
QPushButton#danger { background: #FFDAD6; color: #410002; }
QPushButton#danger:hover { background: #FFB4AB; }

QTableWidget { background: #FFFFFF; border: 1px solid #F0D4DC; gridline-color: #F0D4DC; }
QTableWidget::item:selected { background: #FFD9E2; color: #000000; }
QHeaderView::section { background: #FFF1F4; color: #000000; padding: 6px; border: none; }
"""


class MainWindow(QMainWindow):
    def __init__(self, tracker, allowance_manager, storage):
        super().__init__()
        self.setWindowTitle("ExpenseKo")
        self.resize(900, 600)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        side_layout = QVBoxLayout(sidebar)

        self.pages = QStackedWidget()

        pages = [
            ("Home", HomePage(tracker)),
            ("Expenses", ExpensePage(tracker, storage)),
            ("Allowance", AllowancePage(allowance_manager, storage)),
            ("Summary", SummaryPage(tracker)),
            ("Compare", ComparePage(tracker)),
        ]

        for index, (name, page) in enumerate(pages):
            button = QPushButton(name)
            button.setProperty("nav", True)
            button.clicked.connect(lambda checked, i=index: self.pages.setCurrentIndex(i))
            side_layout.addWidget(button)
            self.pages.addWidget(page)

        side_layout.addStretch()

        layout.addWidget(sidebar)
        layout.addWidget(self.pages)
        self.setCentralWidget(root)


app = QApplication(sys.argv)
app.setStyleSheet(STYLE)

storage = Storage()
user = storage.load("")

if not user.name:
    dialog = LoginDialog()
    if not dialog.exec():
        sys.exit()
    user.name = dialog.get_name()
    storage.save(user)

tracker = ExpenseTracker(user)
allowance_manager = AllowanceManager(user)

window = MainWindow(tracker, allowance_manager, storage)
window.show()
sys.exit(app.exec())