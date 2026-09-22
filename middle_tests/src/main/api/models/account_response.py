from typing import List

from middle_tests.src.main.api.models.base_model import BaseModel
from middle_tests.src.main.api.models.transactions_response import TransactionResponse

class AccountResponse(BaseModel):
    id:int
    accountNumber:str
    balance:float
    transactions:list[TransactionResponse]