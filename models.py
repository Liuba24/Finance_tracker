from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    category: str
    amount: float
    date: date
    type: str
    id: int = None

@dataclass
class Budget:
    category: str
    period: str
    budget_limit: float