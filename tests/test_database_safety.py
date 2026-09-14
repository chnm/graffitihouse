import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_migrations_can_be_disabled_before_connecting_to_the_database():
    environment = os.environ.copy()
    environment.update(
        DJANGO_READ_DOT_ENV_FILE="False",
        DATABASE_URL="sqlite:///:memory:",
        DATABASE_ALLOW_MIGRATIONS="False",
    )

    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--plan"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Database migrations are disabled" in result.stderr


def test_migrations_are_allowed_by_default():
    environment = os.environ.copy()
    environment.update(
        DJANGO_READ_DOT_ENV_FILE="False",
        DATABASE_URL="sqlite:///:memory:",
        DATABASE_READ_ONLY="False",
    )
    environment.pop("DATABASE_ALLOW_MIGRATIONS", None)

    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--plan"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_read_only_database_disables_migrations_by_default():
    environment = os.environ.copy()
    environment.update(
        DJANGO_READ_DOT_ENV_FILE="False",
        DATABASE_URL="sqlite:///:memory:",
        DATABASE_READ_ONLY="True",
    )
    environment.pop("DATABASE_ALLOW_MIGRATIONS", None)

    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--plan"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Database migrations are disabled" in result.stderr
