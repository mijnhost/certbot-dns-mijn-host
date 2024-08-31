lint:
	ruff check --config ruff.toml

lint-fix:
	ruff check --config ruff.toml --fix

format:
	ruff format
