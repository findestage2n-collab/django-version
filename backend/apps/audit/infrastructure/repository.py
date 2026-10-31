from apps.audit.domain.entities import AuditEntry
from apps.audit.domain.repositories import AuditSearch
from core.infrastructure.orm import MappedQuerySet

from .models import AuditLog


def to_entity(row: AuditLog) -> AuditEntry:
    return AuditEntry(
        id=row.pk,
        created_at=row.created_at,
        actor_public_id=row.actor_public_id,
        actor_username=row.actor_username,
        action=row.action,
        target_type=row.target_type,
        target_id=row.target_id,
        metadata=row.metadata,
        ip_address=row.ip_address,
        request_id=row.request_id,
    )


class DjangoAuditRepository:
    """Implémente `AuditRepository` avec l'ORM Django."""

    def add(self, entry: AuditEntry) -> AuditEntry:
        row = AuditLog.objects.create(
            actor_public_id=entry.actor_public_id,
            actor_username=entry.actor_username,
            action=entry.action,
            target_type=entry.target_type,
            target_id=entry.target_id,
            metadata=entry.metadata,
            ip_address=entry.ip_address,
            request_id=entry.request_id,
        )
        return to_entity(row)

    def get(self, entry_id: int) -> AuditEntry | None:
        row = AuditLog.objects.filter(pk=entry_id).first()
        return to_entity(row) if row else None

    def search(self, criteria: AuditSearch):
        queryset = AuditLog.objects.all()
        if criteria.action:
            queryset = queryset.filter(action=criteria.action)
        if criteria.target_type:
            queryset = queryset.filter(target_type=criteria.target_type)
        if criteria.target_id:
            queryset = queryset.filter(target_id=criteria.target_id)
        ordering = ("created_at", "id") if criteria.oldest_first else ("-created_at", "-id")
        queryset = queryset.order_by(*ordering)
        return MappedQuerySet(queryset, to_entity)
