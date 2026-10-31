import uuid

from core.kernel.context import request_id_var


class RequestIdMiddleware:
    """Attribue (ou reprend) un X-Request-ID : corrélation des journaux et des erreurs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if 0 < len(incoming) <= 64 else uuid.uuid4().hex
        request.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response["X-Request-ID"] = request_id
        return response
