import pytest

from apps.audit.composition import build_record_audit
from apps.audit.infrastructure.models import AuditLog
from apps.audit.public import audit_entries_for_target
from core.kernel.ports import Actor


def test_recorded_actions_can_be_read_back(db):
    build_record_audit().record(
        actor=Actor.system(), action="x.done", target_type="x", target_id="7"
    )
    entries = audit_entries_for_target("x", "7")
    assert [e.action for e in entries] == ["x.done"]


def test_audit_table_is_immutable(db):
    row = AuditLog.objects.create(action="x.done", target_type="x", target_id="1")
    row.action = "tampered"
    with pytest.raises(RuntimeError):
        row.save()
    with pytest.raises(RuntimeError):
        row.delete()


def test_only_admin_can_read_logs(auth_client):
    assert auth_client("SECRETAIRE").get("/api/v1/audit/logs/").status_code == 403
    assert auth_client("ADMIN").get("/api/v1/audit/logs/").status_code == 200


def test_admin_sees_entries_and_can_filter(auth_client):
    build_record_audit().record(actor=Actor.system(), action="a.b", target_type="t", target_id="1")
    client = auth_client("ADMIN")
    body = client.get("/api/v1/audit/logs/", {"action": "a.b"}).json()
    assert body["count"] == 1
    entry_id = body["results"][0]["id"]
    assert client.get(f"/api/v1/audit/logs/{entry_id}/").status_code == 200
    assert client.get("/api/v1/audit/logs/999999/").status_code == 404
