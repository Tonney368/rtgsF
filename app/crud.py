from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app import models
from app.rules import RuleEngine
from datetime import datetime

class RTGSService:
    @staticmethod
    def get_account(db: Session, account_id: int):
        return db.get(models.Account, account_id)

    @staticmethod
    def get_transaction_by_idempotency(db: Session, key: str):
        return db.query(models.Transaction).filter(models.Transaction.idempotency_key == key).first()

    @staticmethod
    def execute_payment(db: Session, idempotency_key: str, source_account_id: int, destination_account_id: int, amount: Decimal, currency: str):
        RuleEngine.validate_currency(currency)
        RuleEngine.validate_tx_amount(amount)

        existing = RTGSService.get_transaction_by_idempotency(db, idempotency_key)
        if existing:
            return existing

        source = RTGSService.get_account(db, source_account_id)
        destination = RTGSService.get_account(db, destination_account_id)

        if not source or not destination:
            raise ValueError("Source or destination account not found")
        if source.id == destination.id:
            raise ValueError("Source and destination cannot be identical")
        if source.currency != currency or destination.currency != currency:
            raise ValueError("Currency mismatch")
        if source.available_balance < amount:
            raise ValueError("Insufficient funds")

        txn = models.Transaction(
            idempotency_key=idempotency_key,
            source_account_id=source.id,
            destination_account_id=destination.id,
            amount=amount,
            currency=currency,
            status=models.TransactionStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.flush()

        source.balance -= amount
        source.available_balance -= amount
        destination.balance += amount
        destination.available_balance += amount

        txn.status = models.TransactionStatus.SETTLED
        txn.settled_at = datetime.utcnow()

        src_entry = models.LedgerEntry(
            transaction_id=txn.id,
            account_id=source.id,
            type=models.LedgerType.DEBIT,
            amount=amount,
            balance_after=source.balance,
            created_at=datetime.utcnow(),
        )
        dst_entry = models.LedgerEntry(
            transaction_id=txn.id,
            account_id=destination.id,
            type=models.LedgerType.CREDIT,
            amount=amount,
            balance_after=destination.balance,
            created_at=datetime.utcnow(),
        )
        db.add_all([src_entry, dst_entry])
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def create_account(db: Session, participant_bic: str, currency: str, initial_balance: Decimal):
        participant = db.query(models.Participant).filter(models.Participant.bic == participant_bic).first()
        if not participant:
            participant = models.Participant(bic=participant_bic, name=f"Bank {participant_bic}")
            db.add(participant)
            db.flush()

        account = models.Account(
            participant_id=participant.id,
            currency=currency.upper(),
            balance=initial_balance,
            available_balance=initial_balance,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
