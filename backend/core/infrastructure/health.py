from django.db import connection
from django.http import JsonResponse


def liveness(request):
    """Le processus répond (sondes de conteneur)."""
    return JsonResponse({"status": "ok"})


def readiness(request):
    """Le processus peut servir du trafic : la base répond (aucun service Internet requis)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ready"})
