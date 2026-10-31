"""Cas d'usage du module audit. Dépend uniquement du domaine et du noyau (jamais de Django)."""

from collections.abc import Mapping
from typing import Any

from apps.audit.domain.entities import AuditEntry
from apps.audit.domain.repositories import AuditRepository, AuditSearch
from core.kernel.context import request_id_var
from core.kernel.errors import NotFoundError
from core.kernel.ports import Actor, ResultSet


class RecordAudit:
    """Enregistre une action. Implémente le port `AuditTrail` du noyau."""

    def __init__(self, *, entries: AuditRepository) -> None:
        self._entries = entries

    def record(
        self,
        *,
        actor: Actor,
        action: str,
        target_type: str,
        target_id: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        request_id = request_id_var.get()
        self._entries.add(
            AuditEntry(
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                actor_public_id=actor.public_id,
                actor_username=actor.username,
                metadata=dict(metadata or {}),
                ip_address=actor.ip_address,
                request_id="" if request_id == "-" else request_id,
            )
        )


class SearchAuditEntries:
    def __init__(self, *, entries: AuditRepository) -> None:
        self._entries = entries

    def execute(self, criteria: AuditSearch) -> ResultSet[AuditEntry]:
        return self._entries.search(criteria)


class GetAuditEntry:
    def __init__(self, *, entries: AuditRepository) -> None:
        self._entries = entries

    def execute(self, entry_id: int) -> AuditEntry:
        entry = self._entries.get(entry_id)
        if entry is None:
            raise NotFoundError()
        return entry
