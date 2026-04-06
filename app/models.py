from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import enum

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"

class LedgerType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    bic = Column(String(11), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)

    accounts = relationship("Account", back_populates="participant")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    currency = Column(String(3), nullable=False)
    balance = Column(Numeric(precision=20, scale=6), default=0)
    available_balance = Column(Numeric(precision=20, scale=6), default=0)

    participant = relationship("Participant", back_populates="accounts")
    ledger_entries = relationship("LedgerEntry", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    source_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    destination_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(precision=20, scale=6), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

    source_account = relationship("Account", foreign_keys=[source_account_id])
    destination_account = relationship("Account", foreign_keys=[destination_account_id])
    ledger_entries = relationship("LedgerEntry", back_populates="transaction")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    type = Column(Enum(LedgerType), nullable=False)
    amount = Column(Numeric(precision=20, scale=6), nullable=False)
    balance_after = Column(Numeric(precision=20, scale=6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="ledger_entries")
    account = relationship("Account", back_populates="ledger_entries")
