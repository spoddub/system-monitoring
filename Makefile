install:
	uv sync
migrate:
	uv run python manage.py migrate
lint:
	uv run ruff check --fix

format:
	uv run ruff format
