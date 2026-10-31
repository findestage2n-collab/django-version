from django.contrib.auth.models import AbstractUser
from django.db import models

from core.infrastructure.models import PublicIdModel, TimeStampedModel


class User(PublicIdModel, TimeStampedModel, AbstractUser):
    """Compte utilisateur Django (AUTH_USER_MODEL). `username` joue le rôle de login.

    Les rôles sont des `Group` Django ; les droits sont des permissions Django
    (view/add/change/delete) attribuées aux rôles par `seed_roles`.
    """

    telephone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return self.get_username()
