from fastapi import FastAPI
from app.db import engine, Base
from app.routers import payments, accounts

app = FastAPI(title="RTGS Payment System")

Base.metadata.create_all(bind=engine)

app.include_router(payments.router)
app.include_router(accounts.router)

@app.get("/")
def root():
    return {"message": "RTGS service running"}
