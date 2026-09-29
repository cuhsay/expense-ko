from dataclasses import dataclass, field
from expense_tracking.models import Expense

@dataclass
class User:
    name: str
    allowance: float= 0
    expenses: dict[int, Expense] = field(default_factory=dict)
    next_expense_id: int = 1