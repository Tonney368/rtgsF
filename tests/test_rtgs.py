import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models import Participant, Account

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        p1 = Participant(bic="BANKAUS6XXX", name="Bank A")
        p2 = Participant(bic="BANKBUS6XXX", name="Bank B")
        db.add_all([p1, p2])
        db.flush()
        a1 = Account(participant_id=p1.id, currency="USD", balance=100000.00, available_balance=100000.00)
        a2 = Account(participant_id=p2.id, currency="USD", balance=50000.00, available_balance=50000.00)
        db.add_all([a1, a2])
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_rtgs_payment_settlement():
    payload = {
        "idempotency_key": "test-op-1",
        "source_account_id": 1,
        "destination_account_id": 2,
        "amount": 10000,
        "currency": "USD"
    }
    resp = client.post("/rtgs/payments/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SETTLED"

    bal_src = client.get("/rtgs/accounts/1/balance")
    bal_dst = client.get("/rtgs/accounts/2/balance")
    assert bal_src.json()["balance"] == 90000.0
    assert bal_dst.json()["balance"] == 60000.0

def test_idempotent_payment():
    payload = {
        "idempotency_key": "test-op-2",
        "source_account_id": 1,
        "destination_account_id": 2,
        "amount": 5000,
        "currency": "USD"
    }
    resp1 = client.post("/rtgs/payments/", json=payload)
    resp2 = client.post("/rtgs/payments/", json=payload)
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["transaction_id"] == resp2.json()["transaction_id"]
