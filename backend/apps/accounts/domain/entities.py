from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class UserAccount:
    """Compte utilisateur vu par le métier (sans mot de passe)."""

    public_id: UUID
    username: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    telephone: str = ""
    is_active: bool = True
    roles: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NewUser:
    username: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    telephone: str = ""
