.PHONY: format \
		lint 

format:
	uv run ruff format gem_runner.py
	uv run ruff check gem_runner.py --fix

lint:
	uv lock --check
	uv run mypy gem_runner.py
	uv run ruff check gem_runner.py
	uv run ruff format gem_runner.py --check
