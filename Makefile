.PHONY: format \
		lint 

format:
	uv run ruff format .
	uv run ruff check . --fix

lint:
	uv lock --check
	uv run mypy .
	uv run ruff check .
	uv run ruff format . --check
