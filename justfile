package_path := "src/beancount_no_dnb"

default:
    @just --list

test:
    uv run pytest tests/ -v

lint:
    find src tests -name '*.py' -print | xargs uv run ruff check

typecheck:
    uv run mypy --no-incremental {{package_path}}

check: lint typecheck test

format:
    find src tests -name '*.py' -print | xargs uv run ruff format

fix:
    find src tests -name '*.py' -print | xargs uv run ruff check --fix

all: check

version:
    uv run ruff --version
