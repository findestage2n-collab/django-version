"""Traduction des erreurs en réponse HTTP, au format unique :
{"error": {"code": "...", "message": "...", "details": {...}}, "request_id": "..."}
"""

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.kernel.errors import DomainError


def _payload(code, message, details, context):
    request = context.get("request") if context else None
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    request_id = getattr(request, "request_id", None)
    if request_id:
        body["request_id"] = request_id
    return body


def api_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(
            _payload(exc.code, exc.message, exc.details, context), status=exc.status_code
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        return None  # erreur 500 : laissée à Django (journalisée, sans fuite d'information)

    if isinstance(exc, ValidationError):
        code, message, details = (
            "validation_error",
            "Les données envoyées sont invalides.",
            response.data,
        )
    else:
        if isinstance(exc, APIException):
            code = exc.default_code
        elif isinstance(exc, Http404):
            code = "not_found"
        elif isinstance(exc, PermissionDenied):
            code = "permission_denied"
        else:
            code = "error"
        data = response.data
        message = (
            str(data.get("detail")) if isinstance(data, dict) and "detail" in data else str(data)
        )
        details = None

    response.data = _payload(code, message, details, context)
    return response
