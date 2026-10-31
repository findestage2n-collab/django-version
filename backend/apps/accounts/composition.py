from core.infrastructure.unit_of_work import DjangoUnitOfWork

from .application.use_cases import CreateUser, GetUser
from .infrastructure.repositories import (
    DjangoPasswordPolicy,
    DjangoRoleRepository,
    DjangoUserRepository,
)


def build_create_user() -> CreateUser:
    return CreateUser(
        users=DjangoUserRepository(),
        roles=DjangoRoleRepository(),
        password_policy=DjangoPasswordPolicy(),
        uow=DjangoUnitOfWork(),
    )


def build_get_user() -> GetUser:
    return GetUser(users=DjangoUserRepository())
