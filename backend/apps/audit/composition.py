"""Racine de composition : le SEUL endroit qui relie les cas d'usage à leurs implémentations."""

from .application.use_cases import GetAuditEntry, RecordAudit, SearchAuditEntries
from .infrastructure.repository import DjangoAuditRepository


def build_record_audit() -> RecordAudit:
    return RecordAudit(entries=DjangoAuditRepository())


def build_search_audit_entries() -> SearchAuditEntries:
    return SearchAuditEntries(entries=DjangoAuditRepository())


def build_get_audit_entry() -> GetAuditEntry:
    return GetAuditEntry(entries=DjangoAuditRepository())
