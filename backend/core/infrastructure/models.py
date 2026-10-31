"""Classes abstraites ORM communes (couche infrastructure : dépend de Django)."""

import uuid

from django.db import models
from django.utils import timezone


class PublicIdModel(models.Model):
    """Identifiant public (UUID) exposé par l'API ; la clé primaire entière reste interne.

    Évite l'énumération d'identifiants (IDOR) tout en gardant une clé primaire compacte
    et séquentielle, bien adaptée à InnoDB (MySQL).
    """

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(PublicIdModel, TimeStampedModel):
    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Par défaut, masque les enregistrements archivés."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(BaseModel):
    """Archivage logique : une donnée médicale ne se supprime pas physiquement."""

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # noqa: DJ012

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)
