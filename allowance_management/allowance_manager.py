from dataclasses import dataclass

from allowance_management.models import User

@dataclass
class AllowanceManager:
    user: User

    def add_allowance(self, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.user.allowance += amount

    def edit_allowance(self, amount: float):
        if amount < 0:
            raise ValueError("Amount must be positive.")
        self.user.allowance = amount


