import sqlite3
from allowance_management.models import User
from expense_tracking.models import Expense

class Storage:
    def __init__(self, filename: str = "expenseko.db"):
        self.filename = filename
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.filename) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    allowance REAL NOT NULL,
                    next_expense_id INTEGER NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                )
            """)

    def save(self, user: User):
        with sqlite3.connect(self.filename) as conn:
            conn.execute("DELETE FROM user")
            conn.execute("DELETE FROM expenses")
            conn.execute(
                "INSERT INTO user (id, name, allowance, next_expense_id) VALUES (1, ?, ?, ?)",
                (user.name, user.allowance, user.next_expense_id),
            )
            for e in user.expenses.values():
                conn.execute(
                    "INSERT INTO expenses (id, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
                    (e.id, e.category, e.amount, e.date, e.note),
                )

    def load(self, default_name: str = "User"):
        with sqlite3.connect(self.filename) as conn:
            row = conn.execute(
                "SELECT name, allowance, next_expense_id FROM user WHERE id = 1"
            ).fetchone()
            if row is None:
                return User(default_name)
            expense_rows = conn.execute(
                "SELECT id, category, amount, date, note FROM expenses"
            ).fetchall()

        expenses = {}
        for r in expense_rows:
            expense = Expense(*r)
            expenses[expense.id] = expense

        return User(row[0], row[1], expenses, row[2])