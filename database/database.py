import sqlite3
from allowance_management.models import User, Allowance
from expense_tracking.models import Expense


class Storage:
    def __init__(self, filename: str = "expenseko.db"):
        self.filename = filename
        self.create_tables()
        self.migrate()

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
            connection.execute("""
                CREATE TABLE IF NOT EXISTS allowances (
                    id INTEGER PRIMARY KEY,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS custom_categories (
                    name TEXT PRIMARY KEY
                )
            """)

    def migrate(self):
        with sqlite3.connect(self.filename) as connection:
            cursor = connection.execute("PRAGMA table_info(user)")
            columns = [row[1] for row in cursor.fetchall()]
            if "next_allowance_id" not in columns:
                connection.execute(
                    "ALTER TABLE user ADD COLUMN next_allowance_id INTEGER NOT NULL DEFAULT 1"
                )

    def save(self, user: User):
        with sqlite3.connect(self.filename) as connection:
            connection.execute("DELETE FROM user")
            connection.execute("DELETE FROM expenses")
            connection.execute("DELETE FROM allowances")
            connection.execute("DELETE FROM custom_categories")
            connection.execute(
                "INSERT INTO user (id, name, allowance, next_expense_id, next_allowance_id) VALUES (1, ?, ?, ?, ?)",
                (user.name, user.allowance, user.next_expense_id, user.next_allowance_id),
            )
            for expense in user.expenses.values():
                connection.execute(
                    "INSERT INTO expenses (id, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
                    (expense.id, expense.category, expense.amount, expense.date, expense.note),
                )
            for allowance in user.allowances.values():
                connection.execute(
                    "INSERT INTO allowances (id, amount, date, note) VALUES (?, ?, ?, '')",
                    (allowance.id, allowance.amount, allowance.date),
                )
            for cat in user.custom_categories:
                connection.execute(
                    "INSERT INTO custom_categories (name) VALUES (?)", (cat,)
                )

    def load(self, default_name: str = "User"):
        with sqlite3.connect(self.filename) as connection:
            user_row = connection.execute(
                "SELECT name, allowance, next_expense_id, next_allowance_id FROM user WHERE id = 1"
            ).fetchone()
            expense_rows = connection.execute(
                "SELECT id, category, amount, date, note FROM expenses"
            ).fetchall()
            allowance_rows = connection.execute(
                "SELECT id, amount, date FROM allowances"
            ).fetchall()
            cat_rows = connection.execute(
                "SELECT name FROM custom_categories"
            ).fetchall()

        if user_row is None:
            return User(default_name)

        expenses = {}
        for expense_row in expense_rows:
            expense = Expense(*expense_row)
            expenses[expense.id] = expense

        allowances = {}
        for allowance_row in allowance_rows:
            allowance = Allowance(*allowance_row)
            allowances[allowance.id] = allowance

        custom_categories = {row[0] for row in cat_rows}

        return User(
            user_row[0], user_row[1], expenses, allowances,
            user_row[2], user_row[3], custom_categories
        )