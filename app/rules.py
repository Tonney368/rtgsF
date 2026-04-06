from decimal import Decimal
from app.config import settings
from app.models import Account

class RuleEngine:
    @staticmethod
    def validate_currency(currency: str):
        if currency.upper() not in settings.supported_currencies:
            raise ValueError(f"Unsupported currency {currency}")

    @staticmethod
    def validate_tx_amount(amount: Decimal):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > settings.max_tx_amount:
            raise ValueError(f"Transaction above max amount {settings.max_tx_amount}")

    @staticmethod
    def validate_daily_limit(account: Account, request_amount: Decimal):
        # placeholder: should be tracked via daily usage. For demo we enforce per-tx only
        return True

    @staticmethod
    def penalty_check(iban: str):
        # sanction list check stub for RTGS
        blocked = ["SANCTIONED001", "SANCTIONED002"]
        if iban in blocked:
            raise ValueError("Sanctioned account")
