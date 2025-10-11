install:
	uv sync
migrate:
	uv run python manage.py migrate
lint:
	uv run ruff check --fix

format:
	uv run ruff format
docker:
	docker compose up -d db redis
	docker compose ps
	docker compose logs -f db
main:
	uv run python main.py
server:
	uv run python manage.py runserver 0.0.0.0:8000
celery:
	uv run celery -A system_monitoring worker -l info
get:
	curl http://127.0.0.1:9001/
collect-now:
	uv run celery -A system_monitoring call system_monitoring.tasks.schedule_collecting

collect-one-1:
	uv run celery -A system_monitoring call system_monitoring.tasks.collect_metrics --kwargs='{"machine_id": 1}'

collect-one-2:
	uv run celery -A system_monitoring call system_monitoring.tasks.collect_metrics --kwargs='{"machine_id": 2}'
