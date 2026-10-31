from collections.abc import Iterable
from uuid import UUID

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.accounts.domain.entities import NewUser, UserAccount

from .models import User


def to_entity(user: User) -> UserAccount:
    return UserAccount(
        public_id=user.public_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        telephone=user.telephone,
        is_active=user.is_active,
        roles=tuple(sorted(user.groups.values_list("name", flat=True))),
    )


class DjangoUserRepository:
    def username_exists(self, username: str) -> bool:
        return User.objects.filter(username__iexact=username).exists()

    def add(self, user: NewUser, *, password: str, roles: Iterable[str]) -> UserAccount:
        row = User.objects.create_user(
            username=user.username,
            password=password,  # haché par Django (Argon2)
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            telephone=user.telephone,
        )
        row.groups.set(Group.objects.filter(name__in=list(roles)))
        return to_entity(row)

    def get_active(self, public_id: UUID) -> UserAccount | None:
        row = User.objects.filter(public_id=public_id, is_active=True).first()
        return to_entity(row) if row else None


class DjangoRoleRepository:
    def existing_names(self, names: Iterable[str]) -> set[str]:
        return set(Group.objects.filter(name__in=list(names)).values_list("name", flat=True))


class DjangoPasswordPolicy:
    """Réutilise les validateurs de mots de passe configurés dans les réglages Django."""

    def problems(self, password: str, user: NewUser) -> list[str]:
        candidate = User(username=user.username, first_name=user.first_name, email=user.email)
        try:
            validate_password(password, user=candidate)
        except ValidationError as exc:
            return list(exc.messages)
        return []
