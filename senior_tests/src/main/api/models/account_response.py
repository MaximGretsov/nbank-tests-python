from typing import List

from src.main.api.models.base_model import BaseModel

class AccountResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List