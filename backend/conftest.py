import itertools

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from rest_framework.test import APIClient

PASSWORD = "S3cret-Passw0rd!"


@pytest.fixture
def roles(db):
    call_command("seed_roles")


@pytest.fixture
def make_user(db, roles):
    counter = itertools.count(1)
    User = get_user_model()

    def _make(role: str | None = None, **extra):
        user = User.objects.create_user(username=f"user{next(counter)}", password=PASSWORD, **extra)
        if role:
            user.groups.add(Group.objects.get(name=role))
        return user

    return _make


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(make_user):
    def _make(role: str | None = None) -> APIClient:
        client = APIClient()
        client.user = make_user(role)
        client.force_authenticate(client.user)
        return client

    return _make
