import datetime
import logging

import pytest

from beancount_no_dnb import Config, DnbConfig, DnbMastercardConfig, Importer
from beancount_no_dnb.importer import Config as ModuleConfig
from beancount_no_dnb.models import ExcelFileData, RawTransaction


def test_canonical_importer_api():
    assert ModuleConfig is Config
    assert DnbConfig is Config

    importer = Importer(Config(account_name="Liabilities:CreditCard:DNB"))

    assert importer.account_name == "Liabilities:CreditCard:DNB"


def test_deprecated_config_alias_warns():
    with pytest.warns(DeprecationWarning, match="DnbMastercardConfig is deprecated"):
        config = DnbMastercardConfig(account_name="Liabilities:CreditCard:DNB")

    assert isinstance(config, Config)


def test_debug_output_uses_logging_not_stderr(caplog, capsys):
    importer = Importer(
        Config(account_name="Liabilities:CreditCard:DNB", skip_balance_forward=True),
        debug=True,
    )
    importer._parse_excel_file = lambda _filepath: ExcelFileData(
        transactions=[
            RawTransaction(
                date=datetime.date(2025, 1, 1),
                description="Skyldig beløp fra forrige faktura",
                credit=None,
                debit=100,
            )
        ]
    )

    with caplog.at_level(logging.DEBUG, logger="beancount_no_dnb.mastercard"):
        assert importer.extract("statement.xlsx", []) == []

    assert "Skipping balance forward entry at row 1" in caplog.text
    assert capsys.readouterr().err == ""


def test_skipped_rows_warn_without_debug(caplog, monkeypatch):
    importer = Importer(Config(account_name="Liabilities:CreditCard:DNB"))
    monkeypatch.setattr(
        importer,
        "_parse_excel_file",
        lambda _filepath: ExcelFileData(
            transactions=[
                RawTransaction(
                    date=datetime.date(2025, 1, 1),
                    description="NO AMOUNT",
                    credit=None,
                    debit=None,
                )
            ]
        ),
    )

    with caplog.at_level(logging.WARNING, logger="beancount_no_dnb.mastercard"):
        assert importer.extract("statement.xlsx", []) == []

    assert "Skipping transaction 1: no amount" in caplog.text
