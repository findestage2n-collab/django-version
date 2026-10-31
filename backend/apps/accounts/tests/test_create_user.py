"""Cas d'usage testé avec des FAUX (aucune base de données)."""

from contextlib import nullcontext
from uuid import uuid4

import pytest

from apps.accounts.application.use_cases import CreateUser
from apps.accounts.domain.entities import NewUser, UserAccount
from apps.accounts.domain.errors import UsernameTakenError, WeakPasswordError
from core.kernel.errors import NotFoundError, ValidationFailed


class FakeUsers:
    def __init__(self, existing=()):
        self.existing = set(existing)
        self.created = []

    def username_exists(self, username):
        return username in self.existing

    def add(self, user, *, password, roles):
        self.created.append((user, password, list(roles)))
        return UserAccount(public_id=uuid4(), username=user.username, roles=tuple(roles))


class FakeRoles:
    def existing_names(self, names):
        return {n for n in names if n in {"MEDECIN", "ADMIN"}}


class FakePolicy:
    def problems(self, password, user):
        return ["trop court"] if len(password) < 8 else []


class FakeUow:
    def atomic(self):
        return nullcontext()


@pytest.fixture
def make():
    def _make(existing=()):
        users = FakeUsers(existing)
        use_case = CreateUser(
            users=users, roles=FakeRoles(), password_policy=FakePolicy(), uow=FakeUow()
        )
        return use_case, users

    return _make


def test_creates_user_with_roles(make):
    use_case, users = make()
    account = use_case.execute(
        user=NewUser(username="amina"), password="Longpass1!", roles=["MEDECIN"]
    )
    assert account.roles == ("MEDECIN",)
    assert users.created[0][1] == "Longpass1!"


def test_weak_password_is_refused(make):
    use_case, _ = make()
    with pytest.raises(WeakPasswordError):
        use_case.execute(user=NewUser(username="bob"), password="123")


def test_unknown_role_is_refused(make):
    use_case, _ = make()
    with pytest.raises(NotFoundError):
        use_case.execute(user=NewUser(username="eve"), password="Longpass1!", roles=["ROI"])


def test_duplicate_username_is_refused(make):
    use_case, _ = make(existing=["amina"])
    with pytest.raises(UsernameTakenError):
        use_case.execute(user=NewUser(username="amina"), password="Longpass1!")


def test_blank_username_is_refused(make):
    use_case, _ = make()
    with pytest.raises(ValidationFailed):
        use_case.execute(user=NewUser(username=" "), password="Longpass1!")
