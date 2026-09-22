from src.main.api.models.base_model import BaseModel


class TransferResponse(BaseModel):
    message: str
    amount: float
    senderAccountId: int
    receiverAccountId: int