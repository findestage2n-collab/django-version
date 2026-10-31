from collections.abc import Iterable
from uuid import UUID

from apps.accounts.domain.entities import NewUser, UserAccount
from apps.accounts.domain.errors import UsernameTakenError, WeakPasswordError
from apps.accounts.domain.repositories import PasswordPolicy, RoleRepository, UserRepository
from core.kernel.errors import NotFoundError, ValidationFailed
from core.kernel.ports import UnitOfWork


class CreateUser:
    """Crée un compte : identifiant unique, mot de passe conforme, rôles existants."""

    def __init__(
        self,
        *,
        users: UserRepository,
        roles: RoleRepository,
        password_policy: PasswordPolicy,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._roles = roles
        self._policy = password_policy
        self._uow = uow

    def execute(self, *, user: NewUser, password: str, roles: Iterable[str] = ()) -> UserAccount:
        if not user.username.strip():
            raise ValidationFailed({"username": ["Identifiant obligatoire."]})
        problems = self._policy.problems(password, user)
        if problems:
            raise WeakPasswordError(problems)
        wanted = set(roles)
        missing = wanted - self._roles.existing_names(wanted)
        if missing:
            raise NotFoundError(f"Rôle(s) inconnu(s) : {', '.join(sorted(missing))}")
        with self._uow.atomic():
            if self._users.username_exists(user.username):
                raise UsernameTakenError()
            return self._users.add(user, password=password, roles=sorted(wanted))


class GetUser:
    def __init__(self, *, users: UserRepository) -> None:
        self._users = users

    def execute(self, public_id: UUID) -> UserAccount | None:
        return self._users.get_active(public_id)
