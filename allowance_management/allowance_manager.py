from dataclasses import dataclass

from allowance_management.models import User, Allowance


@dataclass
class AllowanceManager:
    user: User

    def add_allowance(self, amount: float, date: str):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        allowance = Allowance(self.user.next_allowance_id, amount, date)
        self.user.allowances[allowance.id] = allowance
        self.user.next_allowance_id += 1
        self.user.allowance += amount
        return allowance

    def edit_allowance(self, allowance_id: int, amount: float, date: str):
        if allowance_id not in self.user.allowances:
            raise ValueError("Allowance entry not found.")
        if amount < 0:
            raise ValueError("Amount must be positive.")
        entry = self.user.allowances[allowance_id]
        old_amount = entry.amount
        entry.amount = amount
        entry.date = date
        self.user.allowance += amount - old_amount

    def delete_allowance(self, allowance_id: int):
        if allowance_id not in self.user.allowances:
            raise ValueError("Allowance entry not found.")
        entry = self.user.allowances.pop(allowance_id)
        self.user.allowance -= entry.amount