from drf_spectacular.generators import SchemaGenerator


def test_openapi_schema_is_generated_without_errors():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]
    assert "/api/v1/patients/" in paths
    assert "/api/v1/auth/login/" in paths
    assert schema["info"]["version"] == "1.0.0"
