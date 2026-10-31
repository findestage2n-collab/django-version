from core.interface.exceptions import api_exception_handler
from core.kernel.errors import ConflictError, NotFoundError, ValidationFailed


def test_domain_errors_map_to_status_and_envelope():
    for exc, status, code in [
        (NotFoundError(), 404, "not_found"),
        (ConflictError("x"), 409, "conflict"),
        (ValidationFailed({"nom": ["requis"]}), 400, "validation_error"),
    ]:
        response = api_exception_handler(exc, {})
        assert response.status_code == status
        assert response.data["error"]["code"] == code


def test_validation_details_are_exposed():
    response = api_exception_handler(ValidationFailed({"nom": ["requis"]}), {})
    assert response.data["error"]["details"] == {"nom": ["requis"]}
