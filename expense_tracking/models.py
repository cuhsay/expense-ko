from dataclasses import dataclass
from datetime import date

CATEGORIES = ["Food", "Load", "Transportation", "Others"]

@dataclass
class Expense:
    id: int
    category: str
    amount: float
    date: str
    note: str = ""