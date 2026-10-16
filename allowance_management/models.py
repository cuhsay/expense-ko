from dataclasses import dataclass, field
from expense_tracking.models import Expense


@dataclass
class Allowance:
    id: int
    amount: float
    date: str


@dataclass
class User:
    name: str
    allowance: float = 0
    expenses: dict[int, Expense] = field(default_factory=dict)
    allowances: dict[int, Allowance] = field(default_factory=dict)
    next_expense_id: int = 1
    next_allowance_id: int = 1
    custom_categories: set[str] = field(default_factory=set)