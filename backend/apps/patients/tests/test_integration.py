"""Tests de l'INFRASTRUCTURE : repository et compteur avec la vraie base."""

from datetime import date

import pytest

from apps.patients.composition import build_get_patient_summary, build_patient_use_cases
from apps.patients.domain.repositories import PatientSearch
from apps.patients.infrastructure.models import Patient as PatientRow
from apps.patients.infrastructure.repositories import DjangoDossierSequence
from apps.patients.public import PatientRegistered, get_patient_summary, patient_exists
from core.infrastructure.events import event_bus
from core.kernel.ports import Actor

DATA = {"nom": "Mbarga", "prenom": "Alice", "sexe": "F", "date_naissance": date(1990, 5, 1)}


def test_sequence_is_sequential_per_year(db):
    sequence = DjangoDossierSequence()
    assert [sequence.next_value(2026), sequence.next_value(2026), sequence.next_value(2027)] == [
        1,
        2,
        1,
    ]


def test_register_persists_and_search_filters(db):
    use_cases = build_patient_use_cases()
    for name in ("Alpha", "Beta", "Gamma"):
        use_cases.register.execute(data={**DATA, "nom": name}, actor=Actor.system())
    assert use_cases.search.execute(PatientSearch()).count() == 3
    found = use_cases.search.execute(PatientSearch(q="beta"))
    assert [p.nom for p in found[:]] == ["Beta"]
    ordered = use_cases.search.execute(PatientSearch(ordering="nom"))
    assert [p.nom for p in ordered[:]] == ["Alpha", "Beta", "Gamma"]


def test_unknown_ordering_falls_back_safely(db):
    build_patient_use_cases().register.execute(data=DATA, actor=Actor.system())
    result = build_patient_use_cases().search.execute(PatientSearch(ordering="password; DROP"))
    assert len(result) == 1


def test_archive_is_soft_in_database(db):
    use_cases = build_patient_use_cases()
    patient = use_cases.register.execute(data=DATA, actor=Actor.system())
    use_cases.archive.execute(public_id=patient.public_id, actor=Actor.system())
    assert not PatientRow.objects.filter(public_id=patient.public_id).exists()
    assert PatientRow.all_objects.filter(
        public_id=patient.public_id, deleted_at__isnull=False
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_registration_publishes_event_after_commit():
    event_bus.clear()
    received = []
    event_bus.subscribe(PatientRegistered)(received.append)
    patient = build_patient_use_cases().register.execute(data=DATA, actor=Actor.system())
    assert [e.patient_public_id for e in received] == [patient.public_id]
    event_bus.clear()


def test_public_api_exposes_summary_not_entity(db):
    patient = build_patient_use_cases().register.execute(data=DATA, actor=Actor.system())
    summary = get_patient_summary(patient.public_id)
    assert summary.numero_dossier == patient.numero_dossier
    assert not hasattr(summary, "update")
    assert patient_exists(patient.public_id)
    assert build_get_patient_summary().execute(patient.public_id) == summary
