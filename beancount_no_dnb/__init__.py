from .mastercard import DnbMastercardConfig, Importer

# Classification components (re-exported from beancount-classifier)
from beancount_classifier import (
    # Fluent API
    match,
    when,
    field,
    shared,
    amount,
    # Core classes
    AccountSplit,
    AmountCondition,
    AmountOperator,
    ClassificationResult,
    ClassifierMixin,
    SharedExpense,
    TransactionClassifier,
    TransactionPattern,
)

# Data models
from .models import (
    ExcelFileData,
    ParsedTransaction,
    RawTransaction,
)

__all__ = [
    # Main importer classes
    "DnbMastercardConfig",
    "Importer",
    # Fluent API
    "match",
    "when",
    "field",
    "shared",
    "amount",
    # Classification
    "AccountSplit",
    "AmountCondition",
    "AmountOperator",
    "ClassificationResult",
    "ClassifierMixin",
    "SharedExpense",
    "TransactionClassifier",
    "TransactionPattern",
    # Data models
    "ExcelFileData",
    "ParsedTransaction",
    "RawTransaction",
]
