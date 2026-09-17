from src.main.api.models.base_model import BaseModel

class TransferRequest(BaseModel):
    senderAccountId: int
    receiverAccountId: int
    amount: float