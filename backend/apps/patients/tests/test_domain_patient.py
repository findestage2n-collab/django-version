"""Tests du DOMAINE : Python pur, instantanés, sans Django ni base de données."""

from datetime import date
from decimal import Decimal

import pytest

from apps.patients.domain.entities import Patient, Sexe, format_numero_dossier
from apps.patients.domain.errors import InvalidPatientData

TODAY = date(2026, 10, 25)
DATA = {"nom": " Mbarga ", "prenom": "Alice", "sexe": "F", "date_naissance": date(1990, 5, 1)}


def register(**overrides):
    return Patient.register(
        numero_dossier="P2026-000001", data={**DATA, **overrides}, created_by=None, today=TODAY
    )


def test_register_normalizes_and_applies_defaults():
    patient = register()
    assert patient.nom == "Mbarga"  # espaces retirés
    assert patient.sexe is Sexe.FEMININ
    assert patient.taux_prise_en_charge == Decimal(0)


def test_unknown_fields_are_ignored():
    patient = register(numero_dossier="HACK", deleted_at="x", created_by=7)
    assert patient.numero_dossier == "P2026-000001"
    assert patient.deleted_at is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("date_naissance", date(2999, 1, 1)),
        ("telephone", "abc"),
        ("sexe", "X"),
        ("taux_prise_en_charge", 120),
        ("nom", "x" * 101),
    ],
)
def test_invalid_values_are_refused(field, value):
    with pytest.raises(InvalidPatientData) as error:
        register(**{field: value})
    assert field in error.value.details


def test_missing_required_fields_are_all_reported():
    with pytest.raises(InvalidPatientData) as error:
        Patient.register(numero_dossier="P", data={}, created_by=None, today=TODAY)
    assert set(error.value.details) == {"nom", "prenom", "sexe"}


def test_update_returns_changed_field_names_only():
    patient = register()
    assert patient.update({"telephone": "+237 650 00 00 00"}, today=TODAY) == ["telephone"]
    assert patient.telephone == "+237 650 00 00 00"


def test_update_rejects_invalid_value_without_changing_anything():
    patient = register()
    with pytest.raises(InvalidPatientData):
        patient.update({"telephone": "+237650000000", "sexe": "Z"}, today=TODAY)
    assert patient.telephone == ""


def test_archive_is_logical():
    patient = register()
    patient.archive(now=__import__("datetime").datetime(2026, 1, 1))
    assert patient.is_archived


@pytest.mark.parametrize(("today", "expected"), [(date(2026, 5, 1), 36), (date(2026, 4, 30), 35)])
def test_age_accounts_for_birthday(today, expected):
    assert register().age_on(today) == expected


def test_age_unknown_without_birth_date():
    assert register(date_naissance=None).age_on(TODAY) is None


def test_numero_dossier_format():
    assert format_numero_dossier(2026, 42) == "P2026-000042"
