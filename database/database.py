import sqlite3
from allowance_management.models import User
from expense_tracking.models import Expense


class Storage:
    def __init__(self, filename: str = "expenseko.db"):
        self.filename = filename
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.filename) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    allowance REAL NOT NULL,
                    next_expense_id INTEGER NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                )
            """)

    def save(self, user: User):
        with sqlite3.connect(self.filename) as connection:
            connection.execute("DELETE FROM user")
            connection.execute("DELETE FROM expenses")
            connection.execute(
                "INSERT INTO user (id, name, allowance, next_expense_id) VALUES (1, ?, ?, ?)",
                (user.name, user.allowance, user.next_expense_id),
            )
            for expense in user.expenses.values():
                connection.execute(
                    "INSERT INTO expenses (id, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
                    (expense.id, expense.category, expense.amount, expense.date, expense.note),
                )

    def load(self, default_name: str = "User"):
        with sqlite3.connect(self.filename) as connection:
            user_row = connection.execute(
                "SELECT name, allowance, next_expense_id FROM user WHERE id = 1"
            ).fetchone()
            expense_rows = connection.execute(
                "SELECT id, category, amount, date, note FROM expenses"
            ).fetchall()

        if user_row is None:
            return User(default_name)

        expenses = {}
        for expense_row in expense_rows:
            expense = Expense(*expense_row)
            expenses[expense.id] = expense

        return User(user_row[0], user_row[1], expenses, user_row[2])