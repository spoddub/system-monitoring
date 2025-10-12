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
main:  # мок-эндпоинт метрик на :9001
	uv run python main.py
server:
	uv run python manage.py runserver 0.0.0.0:8000
celery:
	uv run celery -A system_monitoring worker -l info
get:
	curl http://127.0.0.1:9001/
collect-now:  # поставить сбор метрик всем активным машинам
	uv run celery -A system_monitoring call system_monitoring.tasks.schedule_collecting
evaluate:  # пересчитать инциденты (создать/обновить/закрыть)
	run celery -A system_monitoring call system_monitoring.tasks.evaluate_incidents
login-demo:     # создать/обновить UI-пользователя demo/demo
	run python manage.py shell -c \"from system_monitoring.models import MonitorUser; from django.contrib.auth.hashers import make_password; MonitorUser.objects.update_or_create(username='demo', defaults={'password': make_password('demo')}); print('demo:demo ready')\"


# === ДЕМО-СЦЕНАРИИ НАГРУЗКИ ===

spike:  # включить высокий CPU на всех машинах
	run python manage.py shell -c \"from system_monitoring.models import Machine as M; M.objects.all().update(url='http://127.0.0.1:9001/?cpu=96', is_active=True, jitter_sec=0); print('spike ON')\"
calm: # вернуть норму (снять нагрузку)
	run python manage.py shell -c \"from system_monitoring.models import Machine as M; M.objects.all().update(url='http://127.0.0.1:9001/'); print('spike OFF')\"
