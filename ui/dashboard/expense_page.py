from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
)
from PyQt6.QtCore import QDate


class ExpensePage(QWidget):
    def __init__(self, tracker, storage):
        super().__init__()
        self.tracker = tracker
        self.storage = storage

        layout = QVBoxLayout(self)

        title = QLabel("New expense")
        title.setObjectName("title")
        layout.addWidget(title)

        form = QFormLayout()
        self.amount_input = QLineEdit()

        self.custom_label = QLabel("New category")
        self.custom_input = QLineEdit()
        self.custom_label.hide()
        self.custom_input.hide()

        self.category_input = QComboBox()
        self.category_input.addItems(self.tracker.get_categories())
        self.category_input.currentTextChanged.connect(self.toggle_custom)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.note_input = QLineEdit()

        form.addRow("Amount", self.amount_input)
        form.addRow("Category", self.category_input)
        form.addRow(self.custom_label, self.custom_input)
        form.addRow("Date", self.date_input)
        form.addRow("Note", self.note_input)
        layout.addLayout(form)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_expense)
        layout.addWidget(save_button)

        self.message = QLabel("")
        layout.addWidget(self.message)

        table_title = QLabel("Your expenses")
        layout.addWidget(table_title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Note"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        delete_button = QPushButton("Delete selected")
        delete_button.setObjectName("danger")
        delete_button.clicked.connect(self.delete_expense)
        layout.addWidget(delete_button)

        self.refresh_table()

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def toggle_custom(self, text):
        is_others = text == "Others"
        self.custom_label.setVisible(is_others)
        self.custom_input.setVisible(is_others)

    def reload_categories(self):
        current = self.category_input.currentText()
        self.category_input.clear()
        self.category_input.addItems(self.tracker.get_categories())
        index = self.category_input.findText(current)
        if index >= 0:
            self.category_input.setCurrentIndex(index)

    def refresh_table(self):
        expenses = sorted(
            self.tracker.user.expenses.values(),
            key=lambda e: (e.date, e.id),
            reverse=True,
        )
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            values = [str(e.id), e.date, e.category, f"₱{e.amount:,.2f}", e.note]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def save_expense(self):
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            self.message.setText("Amount must be a number.")
            return

        category = self.category_input.currentText()
        if category == "Others":
            custom = self.custom_input.text().strip()
            if custom:
                category = custom

        #ga add si tracker ug expense sa user
        try:
            self.tracker.add_expense(
                amount,
                category,
                self.date_input.date().toString("yyyy-MM-dd"),
                self.note_input.text(),
            )
        except ValueError as e:
            self.message.setText(str(e))
            return

        self.storage.save(self.tracker.user)
        self.message.setText(
            f"Expense recorded! Remaining allowance: ₱{self.tracker.user.allowance:,.2f}"
        )
        self.amount_input.clear()
        self.note_input.clear()
        self.custom_input.clear()
        self.reload_categories()
        self.refresh_table()

        allowance = self.tracker.user.allowance
        if allowance < 0:
            QMessageBox.warning(
                self,
                "Overspending warning",
                f"You overspent! You are ₱{-allowance:,.2f} over your allowance.",
            )

    def delete_expense(self):
        row = self.table.currentRow()
        if row < 0:
            self.message.setText("Select an expense to delete first.")
            return

        expense_id = int(self.table.item(row, 0).text())
        try:
            self.tracker.delete_expense(expense_id)
        except ValueError as e:
            self.message.setText(str(e))
            return

        self.storage.save(self.tracker.user)
        self.message.setText(
            f"Expense deleted. Remaining allowance: ₱{self.tracker.user.allowance:,.2f}"
        )
        self.reload_categories()
        self.refresh_table()