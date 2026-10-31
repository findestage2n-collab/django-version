"""Entité du domaine : une trace d'audit. Immuable par construction (dataclass figée)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class AuditEntry:
    """Trace d'une action sensible. Ne JAMAIS y mettre de données médicales."""

    action: str  # ex. "patient.registered"
    target_type: str
    target_id: str  # public_id de la cible
    actor_public_id: UUID | None = None
    actor_username: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    request_id: str = ""
    id: int | None = None
    created_at: datetime | None = None
