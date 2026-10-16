from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import QDate


class ExpensePage(QWidget):
    def __init__(self, tracker, storage):
        super().__init__()
        self.tracker = tracker
        self.storage = storage
        self.editing_id = None

        layout = QVBoxLayout(self)

        title = QLabel("Expense")
        title.setObjectName("title")
        layout.addWidget(title)

        form = QFormLayout()
        self.amount_input = QLineEdit()

        category_row = QHBoxLayout()
        self.category_input = QComboBox()
        self.category_input.setEditable(False)
        self.category_input.addItems(self.tracker.get_categories())
        add_cat_button = QPushButton("+ New Category")
        add_cat_button.clicked.connect(self.add_new_category)
        remove_cat_button = QPushButton("- Remove Category")
        remove_cat_button.clicked.connect(self.remove_category)
        category_row.addWidget(self.category_input)
        category_row.addWidget(add_cat_button)
        category_row.addWidget(remove_cat_button)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.note_input = QLineEdit()

        form.addRow("Amount", self.amount_input)
        form.addRow("Category", category_row)
        form.addRow("Date", self.date_input)
        form.addRow("Note", self.note_input)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("Add")
        self.save_button.clicked.connect(self.save_expense)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.hide()
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

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

        table_buttons = QHBoxLayout()
        edit_button = QPushButton("Edit selected")
        edit_button.clicked.connect(self.edit_selected)
        delete_button = QPushButton("Delete selected")
        delete_button.setObjectName("danger")
        delete_button.clicked.connect(self.delete_expense)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        layout.addLayout(table_buttons)

        layout.addStretch()

    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def refresh(self):
        self.reload_categories()
        self.refresh_table()

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
            values = [str(e.id), e.date, e.category, f"\u20b1{e.amount:,.2f}", e.note]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def add_new_category(self):
        new_cat, ok = QInputDialog.getText(self, "New Category", "Enter category name:")
        if not ok or not new_cat.strip():
            return
        new_cat = new_cat.strip()
        try:
            self.tracker.add_category(new_cat)
            self.storage.save(self.tracker.user)
            self.reload_categories()
            self.category_input.setCurrentText(new_cat)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def remove_category(self):
        cat = self.category_input.currentText()
        if not cat:
            return
        reply = QMessageBox.question(
            self, "Remove Category",
            f"Remove category '{cat}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.tracker.remove_category(cat)
            self.storage.save(self.tracker.user)
            self.reload_categories()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def read_amount(self):
        try:
            return float(self.amount_input.text())
        except ValueError:
            self.message.setText("Amount must be a number.")
            return None

    def save_expense(self):
        amount = self.read_amount()
        if amount is None:
            return

        category = self.category_input.currentText().strip()
        if not category:
            self.message.setText("Category cannot be empty.")
            return

        date = self.date_input.date().toString("yyyy-MM-dd")
        note = self.note_input.text()

        if self.editing_id is not None:
            reply = QMessageBox.question(
                self, "Confirm Edit",
                f"Update expense #{self.editing_id} to \u20b1{amount:,.2f}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                self.tracker.edit_expense(self.editing_id, amount, category, date, note)
            except ValueError as e:
                self.message.setText(str(e))
                return
            self.finish("Expense updated!")
        else:
            reply = QMessageBox.question(
                self, "Confirm Add",
                f"Add expense of \u20b1{amount:,.2f} ({category})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                self.tracker.add_expense(amount, category, date, note)
            except ValueError as e:
                self.message.setText(str(e))
                return
            self.finish("Expense recorded!")

    def finish(self, text):
        self.storage.save(self.tracker.user)
        self.refresh()
        self.message.setText(text)
        self.clear_form()
        self.editing_id = None
        self.save_button.setText("Add")
        self.cancel_button.hide()

        allowance = self.tracker.user.allowance
        if allowance < 0:
            QMessageBox.warning(
                self,
                "Overspending warning",
                f"You overspent! You are \u20b1{-allowance:,.2f} over your allowance.",
            )

    def clear_form(self):
        self.amount_input.clear()
        self.note_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def cancel_edit(self):
        self.clear_form()
        self.editing_id = None
        self.save_button.setText("Add")
        self.cancel_button.hide()
        self.message.setText("")

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0:
            self.message.setText("Select an expense to edit first.")
            return

        expense_id = int(self.table.item(row, 0).text())
        expense = self.tracker.user.expenses[expense_id]

        self.editing_id = expense_id
        self.amount_input.setText(str(expense.amount))
        self.category_input.setCurrentText(expense.category)
        self.date_input.setDate(QDate.fromString(expense.date, "yyyy-MM-dd"))
        self.note_input.setText(expense.note)
        self.save_button.setText("Save")
        self.cancel_button.show()
        self.message.setText("")

    def delete_expense(self):
        row = self.table.currentRow()
        if row < 0:
            self.message.setText("Select an expense to delete first.")
            return

        expense_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete expense #{expense_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.tracker.delete_expense(expense_id)
        except ValueError as e:
            self.message.setText(str(e))
            return

        self.storage.save(self.tracker.user)
        self.refresh()
        self.message.setText(
            f"Expense deleted. Remaining allowance: \u20b1{self.tracker.user.allowance:,.2f}"
        )