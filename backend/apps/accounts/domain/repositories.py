from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from .entities import NewUser, UserAccount


class UserRepository(Protocol):
    def username_exists(self, username: str) -> bool: ...
    def add(self, user: NewUser, *, password: str, roles: Iterable[str]) -> UserAccount: ...
    def get_active(self, public_id: UUID) -> UserAccount | None: ...


class RoleRepository(Protocol):
    def existing_names(self, names: Iterable[str]) -> set[str]: ...


class PasswordPolicy(Protocol):
    def problems(self, password: str, user: NewUser) -> list[str]:
        """Liste des défauts du mot de passe (vide = accepté)."""
        ...
