import pytest
from rest_framework.test import APIClient

PASSWORD = "S3cret-Passw0rd!"


@pytest.fixture
def secretaire(make_user):
    return make_user("SECRETAIRE")


def login(client, username):
    return client.post("/api/v1/auth/login/", {"username": username, "password": PASSWORD})


def test_login_returns_tokens_and_profile(api_client, secretaire):
    response = login(api_client, secretaire.username)
    assert response.status_code == 200
    body = response.json()
    assert {"access", "refresh", "user"} <= body.keys()
    assert body["user"]["roles"] == ["SECRETAIRE"]
    assert "patients.add_patient" in body["user"]["permissions"]


def test_login_wrong_password_is_rejected(api_client, secretaire):
    response = api_client.post(
        "/api/v1/auth/login/", {"username": secretaire.username, "password": "nope"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_failed"


def test_me_requires_authentication(api_client):
    assert api_client.get("/api/v1/auth/me/").status_code == 401


def test_me_returns_current_user(api_client, secretaire):
    access = login(api_client, secretaire.username).json()["access"]
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert client.get("/api/v1/auth/me/").json()["username"] == secretaire.username


def test_refresh_rotates_and_blacklists_old_token(api_client, secretaire):
    refresh = login(api_client, secretaire.username).json()["refresh"]
    first = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh})
    assert first.status_code == 200
    assert first.json()["refresh"] != refresh
    reuse = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh})
    assert reuse.status_code == 401


def test_logout_blacklists_refresh_token(api_client, secretaire):
    refresh = login(api_client, secretaire.username).json()["refresh"]
    assert api_client.post("/api/v1/auth/logout/", {"refresh": refresh}).status_code == 204
    assert api_client.post("/api/v1/auth/refresh/", {"refresh": refresh}).status_code == 401
