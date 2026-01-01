"""Tests for data models."""

import datetime
from decimal import Decimal

import pytest

from beancount_no_dnb.models import (
    ExcelFileData,
    ParsedTransaction,
    RawTransaction,
)


class TestRawTransaction:
    """Tests for RawTransaction model."""

    def test_create_with_all_fields(self):
        """Can create with all fields populated."""
        txn = RawTransaction(
            date=datetime.date(2025, 10, 24),
            description="TEST MERCHANT",
            foreign_currency="12.50 EUR",
            exchange_rate=Decimal("11.85"),
            credit=Decimal("100.00"),
            debit=None,
        )
        assert txn.date == datetime.date(2025, 10, 24)
        assert txn.description == "TEST MERCHANT"
        assert txn.foreign_currency == "12.50 EUR"

    def test_create_minimal(self):
        """Can create with minimal fields."""
        txn = RawTransaction()
        assert txn.date is None
        assert txn.description is None

    def test_debit_transaction(self):
        """Debit transactions have debit populated."""
        txn = RawTransaction(
            date=datetime.date(2025, 10, 24),
            description="PURCHASE",
            debit=Decimal("150.50"),
        )
        assert txn.debit == Decimal("150.50")
        assert txn.credit is None


class TestParsedTransaction:
    """Tests for ParsedTransaction model."""

    def test_create_with_all_fields(self):
        """Can create with all fields populated."""
        txn = ParsedTransaction(
            date=datetime.date(2025, 10, 24),
            amount=Decimal("-150.50"),
            description="TEST MERCHANT",
            is_payment=False,
            is_balance_forward=False,
        )
        assert txn.date == datetime.date(2025, 10, 24)
        assert txn.amount == Decimal("-150.50")

    def test_amount_from_string(self):
        """Amount can be parsed from string."""
        txn = ParsedTransaction(
            date=datetime.date(2025, 10, 24),
            amount="-150.50",
            description="TEST",
        )
        assert txn.amount == Decimal("-150.50")

    def test_amount_from_float(self):
        """Amount can be parsed from float."""
        txn = ParsedTransaction(
            date=datetime.date(2025, 10, 24),
            amount=150.50,
            description="TEST",
        )
        assert txn.amount == Decimal("150.5")

    def test_payment_flag(self):
        """Payment transactions can be flagged."""
        txn = ParsedTransaction(
            date=datetime.date(2025, 10, 24),
            amount=Decimal("5000.00"),
            description="Innbetaling",
            is_payment=True,
        )
        assert txn.is_payment is True


class TestExcelFileData:
    """Tests for ExcelFileData model."""

    def test_create_empty(self):
        """Can create with empty transaction list."""
        data = ExcelFileData()
        assert data.transactions == []
        assert data.sheet_name is None

    def test_create_with_transactions(self):
        """Can create with transactions."""
        txns = [
            RawTransaction(date=datetime.date(2025, 10, 24), description="TXN 1"),
            RawTransaction(date=datetime.date(2025, 10, 25), description="TXN 2"),
        ]
        data = ExcelFileData(transactions=txns, sheet_name="transaksjonsliste")
        assert len(data.transactions) == 2
        assert data.sheet_name == "transaksjonsliste"
