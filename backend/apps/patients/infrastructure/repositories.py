"""ADAPTATEURS de sortie : implémentent les ports du domaine avec l'ORM Django."""

from uuid import UUID

from django.db import transaction
from django.db.models import Q

from apps.patients.domain.entities import WRITABLE_FIELDS, Patient, Sexe
from apps.patients.domain.repositories import SORTABLE_FIELDS, PatientSearch
from core.infrastructure.orm import MappedQuerySet

from .models import NumeroDossierSequence
from .models import Patient as PatientRow


def to_entity(row: PatientRow) -> Patient:
    values = {name: getattr(row, name) for name in WRITABLE_FIELDS}
    values["sexe"] = Sexe(row.sexe)
    return Patient(
        public_id=row.public_id,
        numero_dossier=row.numero_dossier,
        created_by=row.created_by_public_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        deleted_at=row.deleted_at,
        **values,
    )


def _values(patient: Patient) -> dict:
    values = {name: getattr(patient, name) for name in WRITABLE_FIELDS}
    values["sexe"] = patient.sexe.value
    return values


class DjangoPatientRepository:
    def add(self, patient: Patient) -> Patient:
        row = PatientRow.objects.create(
            public_id=patient.public_id,
            numero_dossier=patient.numero_dossier,
            created_by_public_id=patient.created_by,
            **_values(patient),
        )
        return to_entity(row)

    def get(self, public_id: UUID) -> Patient | None:
        row = PatientRow.objects.filter(public_id=public_id).first()  # exclut les archivés
        return to_entity(row) if row else None

    def save(self, patient: Patient) -> None:
        row = PatientRow.all_objects.get(public_id=patient.public_id)
        for name, value in _values(patient).items():
            setattr(row, name, value)
        row.deleted_at = patient.deleted_at
        row.save()
        patient.updated_at = row.updated_at

    def has_duplicate(self, patient: Patient) -> bool:
        if not patient.date_naissance:
            return False
        return (
            PatientRow.objects.filter(
                nom__iexact=patient.nom,
                prenom__iexact=patient.prenom,
                date_naissance=patient.date_naissance,
            )
            .exclude(public_id=patient.public_id)
            .exists()
        )

    def search(self, criteria: PatientSearch):
        queryset = PatientRow.objects.all()
        if criteria.q:
            queryset = queryset.filter(
                Q(nom__icontains=criteria.q)
                | Q(prenom__icontains=criteria.q)
                | Q(numero_dossier__icontains=criteria.q)
                | Q(telephone__icontains=criteria.q)
            )
        if criteria.sexe:
            queryset = queryset.filter(sexe=criteria.sexe.value)
        if criteria.created_after:
            queryset = queryset.filter(created_at__date__gte=criteria.created_after)
        if criteria.created_before:
            queryset = queryset.filter(created_at__date__lte=criteria.created_before)
        field = criteria.ordering.lstrip("-")
        if field not in SORTABLE_FIELDS:  # défense en profondeur : jamais de champ arbitraire
            field, criteria_ordering = "created_at", "-created_at"
        else:
            criteria_ordering = criteria.ordering
        tie_breaker = "-id" if criteria_ordering.startswith("-") else "id"
        return MappedQuerySet(queryset.order_by(criteria_ordering, tie_breaker), to_entity)


class DjangoDossierSequence:
    """Compteur annuel verrouillé (SELECT ... FOR UPDATE) : pas de doublon en concurrence."""

    def next_value(self, year: int) -> int:
        with transaction.atomic():
            NumeroDossierSequence.objects.get_or_create(year=year)
            sequence = NumeroDossierSequence.objects.select_for_update().get(pk=year)
            sequence.last_value += 1
            sequence.save(update_fields=["last_value"])
            return sequence.last_value
