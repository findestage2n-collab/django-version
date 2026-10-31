"""Doublures en mémoire des ports : permettent de tester les cas d'usage SANS base de données."""

from contextlib import nullcontext
from datetime import UTC, date, datetime

from apps.patients.domain.entities import Patient


class InMemoryPatients:
    def __init__(self):
        self.rows: dict = {}

    def add(self, patient):
        self.rows[patient.public_id] = patient
        return patient

    def get(self, public_id):
        patient = self.rows.get(public_id)
        return None if patient is None or patient.is_archived else patient

    def save(self, patient):
        self.rows[patient.public_id] = patient

    def has_duplicate(self, patient: Patient) -> bool:
        return any(
            other.public_id != patient.public_id
            and not other.is_archived
            and (other.nom.lower(), other.prenom.lower(), other.date_naissance)
            == (patient.nom.lower(), patient.prenom.lower(), patient.date_naissance)
            and patient.date_naissance is not None
            for other in self.rows.values()
        )

    def search(self, criteria):
        return list(self.rows.values())


class FakeSequence:
    def __init__(self):
        self.value = 0

    def next_value(self, year):
        self.value += 1
        return self.value


class FakeAudit:
    def __init__(self):
        self.calls = []

    def record(self, **kwargs):
        self.calls.append(kwargs)


class FakeEvents:
    def __init__(self):
        self.published = []

    def publish(self, event):
        self.published.append(event)


class FakeUow:
    def atomic(self):
        return nullcontext()


class FixedClock:
    def __init__(self, today=date(2026, 10, 25)):
        self._today = today

    def now(self):
        return datetime(self._today.year, self._today.month, self._today.day, tzinfo=UTC)

    def today(self):
        return self._today
