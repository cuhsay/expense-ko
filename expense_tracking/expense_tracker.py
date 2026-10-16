from dataclasses import dataclass
from allowance_management.models import User
from expense_tracking.models import Expense, CATEGORIES


@dataclass
class ExpenseTracker:
    user: User

    def add_expense(self, amount: float, category: str, expense_date: str, note: str):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not category.strip():
            raise ValueError("Category cannot be empty.")

        expense = Expense(self.user.next_expense_id, category, amount, expense_date, note)
        self.user.expenses[expense.id] = expense
        self.user.next_expense_id += 1
        self.user.allowance -= amount
        return expense

    def edit_expense(self, expense_id: int, amount: float, category: str, expense_date: str, note: str):
        if expense_id not in self.user.expenses:
            raise ValueError("Expense not found.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not category.strip():
            raise ValueError("Category cannot be empty.")

        expense = self.user.expenses[expense_id]
        old_amount = expense.amount
        expense.amount = amount
        expense.category = category
        expense.date = expense_date
        expense.note = note
        self.user.allowance += amount - old_amount

    def delete_expense(self, expense_id: int):
        if expense_id not in self.user.expenses:
            raise ValueError("Expense not found.")
        expense = self.user.expenses.pop(expense_id)
        self.user.allowance += expense.amount

    def get_expense_summary(self, selected_month: str):
        results = []
        for expense in self.user.expenses.values():
            if expense.date.startswith(selected_month):
                results.append(expense)
        return results

    def get_category_totals(self, start_date: str, end_date: str):
        category_totals = {}
        total = 0
        for expense in self.user.expenses.values():
            if start_date <= expense.date <= end_date:
                category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount
                total += expense.amount
        return category_totals, total

    def get_categories(self):
        used = set()
        for expense in self.user.expenses.values():
            used.add(expense.category)
        return list(CATEGORIES) + sorted(self.user.custom_categories - set(CATEGORIES))

    def add_category(self, name: str):
        if not name.strip():
            raise ValueError("Category name cannot be empty.")
        self.user.custom_categories.add(name.strip())

    def remove_category(self, name: str):
        if name in CATEGORIES:
            raise ValueError("Cannot remove a default category.")
        if name not in self.user.custom_categories:
            raise ValueError("Category not found.")
        # check if any expenses use it
        for expense in self.user.expenses.values():
            if expense.category == name:
                raise ValueError(f"Cannot remove '{name}' — it is used by existing expenses.")
        self.user.custom_categories.discard(name)