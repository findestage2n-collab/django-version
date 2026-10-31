from django.db import models


class AuditLog(models.Model):
    """Table du journal d'audit (détail technique : le domaine ne connaît que `AuditEntry`).

    Pas de clé étrangère vers les utilisateurs : l'audit reste indépendant du module `accounts`
    et conserve la trace même si le compte est supprimé.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor_public_id = models.UUIDField(null=True, blank=True, db_index=True)
    actor_username = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=64, db_index=True)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["target_type", "target_id"])]

    def __str__(self) -> str:
        return f"{self.action} {self.target_type}:{self.target_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise RuntimeError("Un journal d'audit est immuable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Un journal d'audit ne se supprime pas.")
