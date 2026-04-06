from pydantic import BaseModel, PositiveFloat, constr
from datetime import datetime
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"

class PaymentRequest(BaseModel):
    idempotency_key: constr(min_length=1, max_length=64)
    source_account_id: int
    destination_account_id: int
    amount: PositiveFloat
    currency: constr(min_length=3, max_length=3)

class PaymentResponse(BaseModel):
    transaction_id: int
    status: TransactionStatus
    settled_at: datetime

from pydantic import NonNegativeFloat

class AccountCreate(BaseModel):
    participant_bic: constr(min_length=8, max_length=11)
    currency: constr(min_length=3, max_length=3)
    initial_balance: NonNegativeFloat = 0

class AccountBalance(BaseModel):
    account_id: int
    currency: str
    balance: float
    available_balance: float
