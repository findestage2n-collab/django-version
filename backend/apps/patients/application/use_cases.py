"""CAS D'USAGE du module patients : ce que l'application SAIT FAIRE.

Cette couche orchestre le domaine à travers des ports (interfaces). Elle n'importe ni Django,
ni DRF, ni SQL : elle se teste avec des faux en mémoire, sans base de données.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from apps.patients.domain.entities import Patient, Sexe, format_numero_dossier
from apps.patients.domain.errors import DuplicatePatientError
from apps.patients.domain.events import PatientRegistered
from apps.patients.domain.repositories import DossierSequence, PatientRepository, PatientSearch
from core.kernel.errors import NotFoundError
from core.kernel.ports import Actor, AuditTrail, Clock, EventPublisher, ResultSet, UnitOfWork


class RegisterPatient:
    def __init__(
        self,
        *,
        patients: PatientRepository,
        sequence: DossierSequence,
        audit: AuditTrail,
        events: EventPublisher,
        uow: UnitOfWork,
        clock: Clock,
    ) -> None:
        self._patients = patients
        self._sequence = sequence
        self._audit = audit
        self._events = events
        self._uow = uow
        self._clock = clock

    def execute(
        self, *, data: Mapping[str, Any], actor: Actor, allow_duplicate: bool = False
    ) -> Patient:
        today = self._clock.today()
        with self._uow.atomic():
            numero = format_numero_dossier(today.year, self._sequence.next_value(today.year))
            patient = Patient.register(
                numero_dossier=numero, data=data, created_by=actor.public_id, today=today
            )
            if not allow_duplicate and self._patients.has_duplicate(patient):
                raise DuplicatePatientError()
            patient = self._patients.add(patient)
            self._audit.record(
                actor=actor,
                action="patient.registered",
                target_type="patient",
                target_id=str(patient.public_id),
            )
            self._events.publish(PatientRegistered(patient_public_id=patient.public_id))
        return patient


class UpdatePatient:
    def __init__(
        self,
        *,
        patients: PatientRepository,
        audit: AuditTrail,
        uow: UnitOfWork,
        clock: Clock,
    ) -> None:
        self._patients = patients
        self._audit = audit
        self._uow = uow
        self._clock = clock

    def execute(self, *, public_id: UUID, changes: Mapping[str, Any], actor: Actor) -> Patient:
        with self._uow.atomic():
            patient = self._patients.get(public_id)
            if patient is None:
                raise NotFoundError()
            changed = patient.update(changes, today=self._clock.today())
            self._patients.save(patient)
            self._audit.record(
                actor=actor,
                action="patient.updated",
                target_type="patient",
                target_id=str(patient.public_id),
                metadata={"fields": changed},  # noms de champs seulement, jamais les valeurs
            )
        return patient


class ArchivePatient:
    def __init__(
        self, *, patients: PatientRepository, audit: AuditTrail, uow: UnitOfWork, clock: Clock
    ) -> None:
        self._patients = patients
        self._audit = audit
        self._uow = uow
        self._clock = clock

    def execute(self, *, public_id: UUID, actor: Actor) -> None:
        with self._uow.atomic():
            patient = self._patients.get(public_id)
            if patient is None:
                raise NotFoundError()
            patient.archive(now=self._clock.now())
            self._patients.save(patient)
            self._audit.record(
                actor=actor,
                action="patient.archived",
                target_type="patient",
                target_id=str(patient.public_id),
            )


class GetPatient:
    def __init__(self, *, patients: PatientRepository) -> None:
        self._patients = patients

    def execute(self, public_id: UUID) -> Patient:
        patient = self._patients.get(public_id)
        if patient is None:
            raise NotFoundError()
        return patient


class SearchPatients:
    def __init__(self, *, patients: PatientRepository) -> None:
        self._patients = patients

    def execute(self, criteria: PatientSearch) -> ResultSet[Patient]:
        return self._patients.search(criteria)


@dataclass(frozen=True)
class PatientSummary:
    """Ce que les AUTRES modules ont le droit de savoir d'un patient."""

    public_id: UUID
    numero_dossier: str
    nom: str
    prenom: str
    sexe: Sexe
    date_naissance: date | None


class GetPatientSummary:
    def __init__(self, *, patients: PatientRepository) -> None:
        self._patients = patients

    def execute(self, public_id: UUID) -> PatientSummary | None:
        patient = self._patients.get(public_id)
        if patient is None:
            return None
        return PatientSummary(
            public_id=patient.public_id,
            numero_dossier=patient.numero_dossier,
            nom=patient.nom,
            prenom=patient.prenom,
            sexe=patient.sexe,
            date_naissance=patient.date_naissance,
        )
