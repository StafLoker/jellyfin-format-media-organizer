.PHONY: lint lint-fix format format-check test test-ci

lint:
	uv run ruff check src/ tests/

lint-fix:
	uv run ruff check src/ tests/ --fix

format:
	uv run ruff format src/ tests/

format-check:
	uv run ruff format src/ tests/ --check

test:
	uv run pytest
