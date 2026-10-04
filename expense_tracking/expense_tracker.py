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
            raise ValueError("Category cannot be an empty string.")

        expense = Expense(self.user.next_expense_id, category, amount, expense_date, note)
        self.user.expenses[expense.id] = expense
        self.user.next_expense_id += 1
        self.user.allowance -= amount
        return expense

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

    def get_category_totals(self, start_date: str, end_date: str):  # "YYYY-MM-DD"
        category_totals = {}
        total = 0
        for expense in self.user.expenses.values():
            if start_date <= expense.date <= end_date:
                category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount
                total += expense.amount
        return category_totals, total

    def get_categories(self):
        categories = list(CATEGORIES)
        for expense in self.user.expenses.values():
            if expense.category not in categories:
                categories.insert(-1, expense.category)
        return categories



