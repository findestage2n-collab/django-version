"""Tests des CAS D'USAGE avec des doublures en mémoire : pas de base de données."""

from datetime import date
from uuid import uuid4

import pytest

from apps.patients.application.use_cases import (
    ArchivePatient,
    GetPatient,
    RegisterPatient,
    UpdatePatient,
)
from apps.patients.domain.errors import DuplicatePatientError, InvalidPatientData
from apps.patients.domain.events import PatientRegistered
from core.kernel.errors import NotFoundError
from core.kernel.ports import Actor

from .fakes import FakeAudit, FakeEvents, FakeSequence, FakeUow, FixedClock, InMemoryPatients

DATA = {"nom": "Mbarga", "prenom": "Alice", "sexe": "F", "date_naissance": date(1990, 5, 1)}
ACTOR = Actor(public_id=uuid4(), username="secretaire1")


class Env:
    def __init__(self):
        self.patients = InMemoryPatients()
        self.audit = FakeAudit()
        self.events = FakeEvents()
        clock = FixedClock()
        self.register = RegisterPatient(
            patients=self.patients,
            sequence=FakeSequence(),
            audit=self.audit,
            events=self.events,
            uow=FakeUow(),
            clock=clock,
        )
        self.update = UpdatePatient(
            patients=self.patients, audit=self.audit, uow=FakeUow(), clock=clock
        )
        self.archive = ArchivePatient(
            patients=self.patients, audit=self.audit, uow=FakeUow(), clock=clock
        )
        self.get = GetPatient(patients=self.patients)


@pytest.fixture
def env():
    return Env()


def test_register_numbers_audits_and_publishes(env):
    patient = env.register.execute(data=DATA, actor=ACTOR)
    assert patient.numero_dossier == "P2026-000001"
    assert patient.created_by == ACTOR.public_id
    assert env.audit.calls[0]["action"] == "patient.registered"
    assert env.events.published == [PatientRegistered(patient_public_id=patient.public_id)] or (
        env.events.published[0].patient_public_id == patient.public_id
    )


def test_duplicate_is_refused_unless_forced(env):
    env.register.execute(data=DATA, actor=ACTOR)
    with pytest.raises(DuplicatePatientError):
        env.register.execute(data=DATA, actor=ACTOR)
    forced = env.register.execute(data=DATA, actor=ACTOR, allow_duplicate=True)
    assert forced.numero_dossier == "P2026-000003"  # le numéro 2 a été consommé par le refus


def test_invalid_data_registers_nothing(env):
    with pytest.raises(InvalidPatientData):
        env.register.execute(data={**DATA, "telephone": "abc"}, actor=ACTOR)
    assert env.patients.rows == {}
    assert env.audit.calls == []
    assert env.events.published == []


def test_update_audits_field_names_only(env):
    patient = env.register.execute(data=DATA, actor=ACTOR)
    env.update.execute(
        public_id=patient.public_id, changes={"telephone": "+237600000000"}, actor=ACTOR
    )
    last = env.audit.calls[-1]
    assert last["metadata"] == {"fields": ["telephone"]}
    assert "+237" not in str(last)  # aucune donnée personnelle dans le journal


def test_update_unknown_patient_is_not_found(env):
    with pytest.raises(NotFoundError):
        env.update.execute(public_id=uuid4(), changes={}, actor=ACTOR)


def test_archive_hides_patient(env):
    patient = env.register.execute(data=DATA, actor=ACTOR)
    env.archive.execute(public_id=patient.public_id, actor=ACTOR)
    with pytest.raises(NotFoundError):
        env.get.execute(patient.public_id)
    assert env.audit.calls[-1]["action"] == "patient.archived"
