from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QMessageBox,
)
from PyQt6.QtCore import QDate


class AllowancePage(QWidget):
    def __init__(self, manager, storage):
        super().__init__()
        self.manager = manager
        self.storage = storage
        self.editing_id = None

        layout = QVBoxLayout(self)

        title = QLabel("Allowance")
        title.setObjectName("title")
        layout.addWidget(title)

        self.current_label = QLabel()
        layout.addWidget(self.current_label)

        form = QFormLayout()
        self.amount_input = QLineEdit()
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        form.addRow("Amount", self.amount_input)
        form.addRow("Date", self.date_input)
        layout.addLayout(form)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("Add")
        self.save_button.clicked.connect(self.save_allowance)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.hide()
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

        self.message = QLabel("")
        layout.addWidget(self.message)

        table_title = QLabel("Allowance history")
        layout.addWidget(table_title)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Amount"])
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
        delete_button.clicked.connect(self.delete_selected)
        table_buttons.addWidget(edit_button)
        table_buttons.addWidget(delete_button)
        layout.addLayout(table_buttons)

        layout.addStretch()

    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def refresh(self):
        self.current_label.setText(
            f"Current allowance: \u20b1{self.manager.user.allowance:,.2f}"
        )
        self.refresh_table()

    def refresh_table(self):
        entries = sorted(
            self.manager.user.allowances.values(),
            key=lambda a: (a.date, a.id),
            reverse=True,
        )
        self.table.setRowCount(len(entries))
        for row, a in enumerate(entries):
            values = [str(a.id), a.date, f"\u20b1{a.amount:,.2f}"]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def read_amount(self):
        try:
            return float(self.amount_input.text())
        except ValueError:
            self.message.setText("Amount must be a number.")
            return None

    def save_allowance(self):
        amount = self.read_amount()
        if amount is None:
            return

        date = self.date_input.date().toString("yyyy-MM-dd")

        if self.editing_id is not None:
            reply = QMessageBox.question(
                self, "Confirm Edit",
                f"Update allowance entry #{self.editing_id} to \u20b1{amount:,.2f}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                self.manager.edit_allowance(self.editing_id, amount, date)
            except ValueError as e:
                self.message.setText(str(e))
                return
            self.finish("Allowance entry updated!")
        else:
            reply = QMessageBox.question(
                self, "Confirm Add",
                f"Add allowance of \u20b1{amount:,.2f}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                self.manager.add_allowance(amount, date)
            except ValueError as e:
                self.message.setText(str(e))
                return
            self.finish("Allowance added!")

    def finish(self, text):
        self.storage.save(self.manager.user)
        self.refresh()
        self.message.setText(text)
        self.clear_form()
        self.editing_id = None
        self.save_button.setText("Add")
        self.cancel_button.hide()

    def clear_form(self):
        self.amount_input.clear()
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
            self.message.setText("Select an entry to edit first.")
            return

        entry_id = int(self.table.item(row, 0).text())
        entry = self.manager.user.allowances[entry_id]

        self.editing_id = entry_id
        self.amount_input.setText(str(entry.amount))
        self.date_input.setDate(QDate.fromString(entry.date, "yyyy-MM-dd"))
        self.save_button.setText("Save")
        self.cancel_button.show()
        self.message.setText("")

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            self.message.setText("Select an entry to delete first.")
            return

        entry_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete allowance entry #{entry_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.manager.delete_allowance(entry_id)
        except ValueError as e:
            self.message.setText(str(e))
            return

        self.storage.save(self.manager.user)
        self.refresh()
        self.message.setText(
            f"Allowance entry deleted. Current allowance: \u20b1{self.manager.user.allowance:,.2f}"
        )