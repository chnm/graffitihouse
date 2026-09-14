from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Report whether the application can connect to its database."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})
