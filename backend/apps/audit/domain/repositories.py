"""Port de persistance : le domaine décrit ce dont il a besoin, sans dire comment (SQL, fichier…).

Volontairement SANS méthode de modification ni de suppression : un journal d'audit est immuable.
"""

from dataclasses import dataclass
from typing import Protocol

from core.kernel.ports import ResultSet

from .entities import AuditEntry


@dataclass(frozen=True)
class AuditSearch:
    action: str = ""
    target_type: str = ""
    target_id: str = ""
    oldest_first: bool = False


class AuditRepository(Protocol):
    def add(self, entry: AuditEntry) -> AuditEntry: ...
    def get(self, entry_id: int) -> AuditEntry | None: ...
    def search(self, criteria: AuditSearch) -> ResultSet[AuditEntry]: ...
