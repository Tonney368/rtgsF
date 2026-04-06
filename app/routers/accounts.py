from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db import get_db
from app.crud import RTGSService
from app.schemas import AccountCreate, AccountBalance

router = APIRouter(prefix="/rtgs/accounts", tags=["accounts"])

@router.post("/", response_model=AccountBalance)
def create_account(req: AccountCreate, db: Session = Depends(get_db)):
    try:
        account = RTGSService.create_account(db, participant_bic=req.participant_bic, currency=req.currency.upper(), initial_balance=Decimal(req.initial_balance))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    return AccountBalance(
        account_id=account.id,
        currency=account.currency,
        balance=float(account.balance),
        available_balance=float(account.available_balance),
    )

@router.get("/{account_id}/balance", response_model=AccountBalance)
def get_balance(account_id: int, db: Session = Depends(get_db)):
    account = RTGSService.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountBalance(
        account_id=account.id,
        currency=account.currency,
        balance=float(account.balance),
        available_balance=float(account.available_balance),
    )
