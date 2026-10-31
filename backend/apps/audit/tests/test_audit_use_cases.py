"""Test du cas d'usage SANS base de données : un faux dépôt en mémoire suffit."""

from uuid import uuid4

from apps.audit.application.use_cases import RecordAudit
from apps.audit.domain.entities import AuditEntry
from core.kernel.ports import Actor


class InMemoryAuditRepository:
    def __init__(self):
        self.entries: list[AuditEntry] = []

    def add(self, entry):
        self.entries.append(entry)
        return entry


def test_record_builds_an_entry_from_the_actor():
    repo = InMemoryAuditRepository()
    actor = Actor(public_id=uuid4(), username="amina", ip_address="10.0.0.5")
    RecordAudit(entries=repo).record(
        actor=actor, action="x.done", target_type="x", target_id=42, metadata={"k": 1}
    )
    entry = repo.entries[0]
    assert (entry.actor_username, entry.target_id, entry.ip_address) == ("amina", "42", "10.0.0.5")
    assert entry.metadata == {"k": 1}


def test_audit_entry_is_immutable():
    import dataclasses

    entry = AuditEntry(action="a", target_type="t", target_id="1")
    try:
        entry.action = "b"
    except dataclasses.FrozenInstanceError:
        return
    raise AssertionError("AuditEntry devrait être figée")
