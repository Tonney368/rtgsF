from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app.schemas import PaymentRequest, PaymentResponse
from app.db import get_db
from app.crud import RTGSService

router = APIRouter(prefix="/rtgs/payments", tags=["payments"])

@router.post("/", response_model=PaymentResponse)
def create_payment(req: PaymentRequest, db: Session = Depends(get_db)):
    try:
        txn = RTGSService.execute_payment(
            db=db,
            idempotency_key=req.idempotency_key,
            source_account_id=req.source_account_id,
            destination_account_id=req.destination_account_id,
            amount=Decimal(req.amount),
            currency=req.currency.upper(),
        )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    if txn.status == "FAILED":
        raise HTTPException(status_code=500, detail="Transaction failed")

    return PaymentResponse(transaction_id=txn.id, status=txn.status, settled_at=txn.settled_at)

from app import models

@router.get("/{txn_id}", response_model=PaymentResponse)
def get_payment(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).get(txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return PaymentResponse(transaction_id=txn.id, status=txn.status, settled_at=txn.settled_at)
