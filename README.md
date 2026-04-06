# RTGS Payment System (Prototype)

This repository contains a prototype RTGS (Real-Time Gross Settlement) payment system built with FastAPI, SQLAlchemy, and pytest.

## Features
- Participant and account registry
- Immediate settlement (debit/credit atomic flow)
- Multi-currency support
- Simple rule engine (daily limits, max transaction, sanctions checks)
- Idempotent transaction processing
- Audit ledger entries

## Setup
```bash
cd rtgs-system
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Run tests
```bash
pytest -q
```

update dashboard;;;..;;;
