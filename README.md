# beancount-no-dnb

A Python library for importing DNB Mastercard (Norway) bank statements from Excel format into Beancount accounting format.

## Quickstart

Get from zero to viewing your DNB Mastercard transactions in Fava in under 5 minutes.

### 1. Create a new project

```bash
mkdir finances && cd finances
uv init
```

### 2. Add dependencies

```bash
# Add core dependencies
uv add beancount fava

# Add git-based dependencies
uv add beangulp --git https://github.com/beancount/beangulp
uv add beancount-no-dnb --git https://github.com/staticaland/beancount-no-dnb
```

### 3. Configure as a package (manual edit needed)

Add the following to your `pyproject.toml`:

```toml
[tool.uv]
package = true

[project.scripts]
import-transactions = "finances.importers:main"
```

This enables the `import-transactions` command and makes your project installable.

Then sync to apply the changes:

```bash
uv sync
```

### 4. Create the importer

Create `src/finances/importers.py`:

```python
from beangulp import Ingest
from beancount_no_dnb import DnbMastercardConfig, Importer, match, when, amount


def get_importers():
    return [
        Importer(DnbMastercardConfig(
            account_name="Liabilities:CreditCard:DNB",
            currency="NOK",
            transaction_patterns=[
                # Simple substring match
                match("SPOTIFY") >> "Expenses:Subscriptions:Music",
                match("NETFLIX") >> "Expenses:Subscriptions:Streaming",

                # Case-insensitive matching
                match("starbucks").ignorecase >> "Expenses:Coffee",

                # Regex pattern (handles variations like "REMA 1000", "REMA1000")
                match(r"REMA\s*1000").regex.ignorecase >> "Expenses:Groceries",

                # Amount-based rules
                when(amount < 50) >> "Expenses:PettyCash",
                when(amount.between(50, 200)) >> "Expenses:Shopping:Medium",

                # Combined: merchant + amount threshold
                match("VINMONOPOLET").where(amount > 500) >> "Expenses:Alcohol:Expensive",

                # More examples
                match("GITHUB") >> "Expenses:Cloud:GitHub",
                match("Tesla") >> "Expenses:Transportation:Charging",
                match("COOP") >> "Expenses:Groceries",
                match("KIWI") >> "Expenses:Groceries",
            ],
        )),
    ]


def main():
    ingest = Ingest(get_importers())
    ingest.main()


if __name__ == "__main__":
    main()
```

Also create `src/finances/__init__.py`:

```bash
mkdir -p src/finances
touch src/finances/__init__.py
```

### 5. Create the main ledger file

Create `main.beancount`:

```beancount
option "title" "My Finances"
option "operating_currency" "NOK"

; Account definitions
2020-01-01 open Liabilities:CreditCard:DNB NOK
2020-01-01 open Expenses:Subscriptions:Music NOK
2020-01-01 open Expenses:Subscriptions:Streaming NOK
2020-01-01 open Expenses:Groceries NOK
2020-01-01 open Expenses:PettyCash NOK
2020-01-01 open Expenses:Shopping:Medium NOK
2020-01-01 open Expenses:Alcohol:Expensive NOK
2020-01-01 open Expenses:Cloud:GitHub NOK
2020-01-01 open Expenses:Transportation:Charging NOK
2020-01-01 open Expenses:Uncategorized NOK

; Include imported transactions
include "imports/*.beancount"
```

Create the imports directory:

```bash
mkdir -p imports
```

### 6. Download your DNB Mastercard statement

1. Log in to your DNB account
2. Go to your Mastercard statement
3. Export as Excel (.xlsx)
4. Place it in a `downloads/` folder

### 7. Import transactions

```bash
# Preview what will be imported
uv run import-transactions extract downloads/

# Save to a file
uv run import-transactions extract downloads/ > imports/2024-dnb.beancount
```

### 8. View in Fava

```bash
uv run fava main.beancount
```

Open http://localhost:5000 in your browser.

## Excel Format

The importer expects DNB Mastercard Excel exports with these columns:

| Column | Header          | Description                       |
| ------ | --------------- | --------------------------------- |
| A      | Dato            | Transaction date                  |
| B      | Beløpet gjelder | Description/payee                 |
| C      | Valuta          | Foreign currency amount (ignored) |
| D      | Kurs            | Exchange rate (ignored)           |
| E      | Inn             | Credit/inflow in NOK              |
| F      | Ut              | Debit/outflow in NOK              |

## Configuration Options

```python
DnbMastercardConfig(
    account_name="Liabilities:CreditCard:DNB",
    currency="NOK",
    transaction_patterns=[...],

    # Skip "Skyldig beløp fra forrige faktura" (balance forward) entries
    skip_balance_forward=True,  # default

    # Skip "Innbetaling" (payment) entries
    skip_payments=False,  # default
)
```

## Classification for Humans

The library provides a Pythonic, fluent API for transaction classification:

```python
from beancount_no_dnb import match, when, field, shared, amount

rules = [
    # Simple substring matching
    match("SPOTIFY") >> "Expenses:Music",
    match("NETFLIX") >> "Expenses:Entertainment",

    # Regex patterns
    match(r"REMA\s*1000").regex >> "Expenses:Groceries",

    # Case-insensitive matching
    match("starbucks").ignorecase >> "Expenses:Coffee",
    match("starbucks").i >> "Expenses:Coffee",  # short form

    # Amount-based rules
    when(amount < 50) >> "Expenses:PettyCash",
    when(amount > 1000) >> "Expenses:Large",
    when(amount.between(100, 500)) >> "Expenses:Medium",

    # Combined conditions
    match("VINMONOPOLET").where(amount > 500) >> "Expenses:Alcohol:Fine",

    # Split across multiple accounts
    match("COSTCO") >> [
        ("Expenses:Groceries", 80),
        ("Expenses:Household", 20),
    ],

    # Shared expenses (tracking what roommates owe you)
    match("GROCERIES") >> "Expenses:Groceries" | shared("Assets:Receivables:Alex", 50),
]
```

### API Reference

| Pattern Type        | Example                                       | Description                             |
| ------------------- | --------------------------------------------- | --------------------------------------- |
| Substring           | `match("SPOTIFY") >> "..."`                   | Matches if narration contains "SPOTIFY" |
| Regex               | `match(r"REMA\s*1000").regex >> "..."`        | Regex pattern matching                  |
| Case-insensitive    | `match("spotify").ignorecase >> "..."`        | Case-insensitive match                  |
| Amount less than    | `when(amount < 50) >> "..."`                  | Amount under threshold                  |
| Amount greater than | `when(amount > 500) >> "..."`                 | Amount over threshold                   |
| Amount range        | `when(amount.between(100, 500)) >> "..."`     | Amount within range                     |
| Combined            | `match("STORE").where(amount > 100) >> "..."` | Narration + amount condition            |
| Split               | `match("X") >> [("A", 80), ("B", 20)]`        | Split across accounts                   |
| Shared              | `... >> "X" \| shared("Receivable", 50)`      | Track shared expenses                   |

## Project Structure

After setup, your project should look like:

```
finances/
├── pyproject.toml
├── main.beancount
├── imports/
│   └── 2024-dnb.beancount
├── downloads/
│   └── DNB_Statement_2024-12.xlsx
└── src/
    └── finances/
        ├── __init__.py
        └── importers.py
```
