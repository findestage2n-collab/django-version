import pytest

from apps.accounts.composition import build_create_user
from apps.accounts.domain.entities import NewUser
from apps.accounts.domain.errors import WeakPasswordError
from apps.accounts.domain.roles import ROLE_DEFINITIONS
from apps.accounts.infrastructure.role_seeder import apply_roles


def test_apply_roles_is_idempotent_and_complete(db):
    first = apply_roles()
    second = apply_roles()
    assert first == second
    assert set(first) == set(ROLE_DEFINITIONS)
    assert first["SECRETAIRE"] == 4  # view/add/change/delete sur patients.patient
    assert first["MEDECIN"] == 1


def test_real_create_user_hashes_password_and_assigns_roles(db, roles):
    account = build_create_user().execute(
        user=NewUser(username="amina"), password="Tr3s-Solide-2026", roles=["MEDECIN"]
    )
    assert account.roles == ("MEDECIN",)


def test_django_password_validators_are_applied(db, roles):
    with pytest.raises(WeakPasswordError):
        build_create_user().execute(user=NewUser(username="bob"), password="123")
