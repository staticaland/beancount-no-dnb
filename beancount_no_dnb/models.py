"""Data models for DNB Excel file parsing."""

import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class RawTransaction(BaseModel):
    """Raw transaction data extracted from DNB Excel file."""

    date: datetime.date | None = None
    description: str | None = None
    foreign_currency: str | None = None  # Valuta column
    exchange_rate: Decimal | None = None  # Kurs column
    credit: Decimal | None = None  # Inn column (inflow)
    debit: Decimal | None = None  # Ut column (outflow)


class ParsedTransaction(BaseModel):
    """Processed transaction with proper types."""

    date: datetime.date
    amount: Decimal  # Positive for credits, negative for debits
    description: str
    is_payment: bool = False  # True for "Innbetaling" entries
    is_balance_forward: bool = False  # True for "Skyldig beløp fra forrige faktura"

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is a valid decimal."""
        return Decimal(str(v)) if not isinstance(v, Decimal) else v


class ExcelFileData(BaseModel):
    """Data extracted from a DNB Excel file."""

    transactions: list[RawTransaction] = Field(default_factory=list)
    sheet_name: str | None = None
