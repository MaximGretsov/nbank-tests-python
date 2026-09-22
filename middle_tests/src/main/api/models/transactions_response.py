from middle_tests.src.main.api.models.base_model import BaseModel

class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    timestamp: str
    relatedAccountId: int