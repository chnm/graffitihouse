.DEFAULT_GOAL := help

preview:
	uv run python manage.py runserver

check:
	uv run python manage.py check

shell:
	uv run python manage.py shell

test:
	uv run python -m pytest

test-coverage:
	uv run python -m pytest --cov --cov-report=term-missing --cov-report=html

mm:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

show-migrations:
	uv run python manage.py showmigrations

collectstatic:
	uv run python manage.py collectstatic --no-input

superuser:
	uv run python manage.py createsuperuser

help:
	@echo "Graffiti House development commands"
	@echo "  preview           Start the Django development server"
	@echo "  check             Run Django system checks"
	@echo "  shell             Open a Django shell"
	@echo "  test              Run the test suite"
	@echo "  test-coverage     Run tests with branch coverage"
	@echo "  mm                Create model migrations"
	@echo "  migrate           Apply model migrations"
	@echo "  show-migrations   Show migration status"
	@echo "  collectstatic     Collect production static files"
	@echo "  superuser         Create an administrative user"

.PHONY: preview check shell test test-coverage mm migrate show-migrations collectstatic superuser help
