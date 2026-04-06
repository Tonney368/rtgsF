from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./rtgs.db"
    max_tx_amount: float = 10000000.0
    daily_limit_per_account: float = 50000000.0
    supported_currencies: tuple[str, ...] = ("USD", "EUR", "GBP", "JPY")

settings = Settings()
