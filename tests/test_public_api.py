import pytest

from beancount_no_dnb import Config, DnbConfig, DnbMastercardConfig, Importer
from beancount_no_dnb.importer import Config as ModuleConfig


def test_canonical_importer_api():
    assert ModuleConfig is Config
    assert DnbConfig is Config

    importer = Importer(Config(account_name="Liabilities:CreditCard:DNB"))

    assert importer.account_name == "Liabilities:CreditCard:DNB"


def test_deprecated_config_alias_warns():
    with pytest.warns(DeprecationWarning, match="DnbMastercardConfig is deprecated"):
        config = DnbMastercardConfig(account_name="Liabilities:CreditCard:DNB")

    assert isinstance(config, Config)
