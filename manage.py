#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if "migrate" in sys.argv[1:]:
        if not settings.DATABASE_ALLOW_MIGRATIONS:
            raise SystemExit(
                "Database migrations are disabled by DATABASE_ALLOW_MIGRATIONS. "
                "The deployment process should apply remote schema changes."
            )

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
