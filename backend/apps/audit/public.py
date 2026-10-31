"""API publique du module `audit` : seule surface utilisable par les autres modules.

Les autres modules reçoivent un `AuditTrail` (port du noyau) ; ils ne voient ni la table
ni le repository.
"""

from core.kernel.ports import AuditTrail

from .application.use_cases import SearchAuditEntries
from .composition import build_record_audit, build_search_audit_entries
from .domain.entities import AuditEntry
from .domain.repositories import AuditSearch


def get_audit_trail() -> AuditTrail:
    return build_record_audit()


def audit_entries_for_target(target_type: str, target_id: str) -> list[AuditEntry]:
    """Historique d'une ressource, du plus ancien au plus récent."""
    use_case: SearchAuditEntries = build_search_audit_entries()
    criteria = AuditSearch(target_type=target_type, target_id=str(target_id), oldest_first=True)
    return list(use_case.execute(criteria)[:])


__all__ = ["AuditEntry", "audit_entries_for_target", "get_audit_trail"]
