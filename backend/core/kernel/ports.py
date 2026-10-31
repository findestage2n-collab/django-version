"""PORTS partagés : interfaces que les cas d'usage exigent et que l'infrastructure fournit.

Principe d'inversion des dépendances : le cas d'usage possède l'interface, l'infrastructure
l'implémente. Ainsi la base de données, le bus d'événements ou l'audit sont remplaçables
(par un faux en test, ou par une autre technologie plus tard) sans toucher aux règles métier.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

from .events import DomainEvent

T_co = TypeVar("T_co", covariant=True)


@dataclass(frozen=True)
class Actor:
    """Qui agit (valeur simple, indépendante du modèle utilisateur du framework)."""

    public_id: UUID | None
    username: str = ""
    ip_address: str | None = None

    @classmethod
    def system(cls) -> Actor:
        return cls(public_id=None, username="system")


class ResultSet(Protocol[T_co]):
    """Résultat paginable : le total et des tranches sont lus à la demande (pas tout en mémoire)."""

    def count(self) -> int: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: Any) -> Any: ...


class AuditTrail(Protocol):
    def record(
        self,
        *,
        actor: Actor,
        action: str,
        target_type: str,
        target_id: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None: ...


class UnitOfWork(Protocol):
    """Transaction : tout réussit ou rien n'est enregistré."""

    def atomic(self) -> AbstractContextManager[None]: ...


class EventPublisher(Protocol):
    """Publie un événement ; l'implémentation décide quand (ici : après le commit)."""

    def publish(self, event: DomainEvent) -> None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
    def today(self) -> date: ...
