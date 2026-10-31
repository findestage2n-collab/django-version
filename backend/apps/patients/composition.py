"""RACINE DE COMPOSITION : le seul fichier qui choisit les implémentations concrètes.

Pour changer de technologie (autre base, autre audit…), on modifie ICI ; les cas d'usage
et le domaine restent intacts.
"""

from dataclasses import dataclass

from django.conf import settings

from apps.audit.public import get_audit_trail
from core.infrastructure.events import event_bus
from core.infrastructure.unit_of_work import DjangoUnitOfWork
from core.kernel.clock import SystemClock

from .application.use_cases import (
    ArchivePatient,
    GetPatient,
    GetPatientSummary,
    RegisterPatient,
    SearchPatients,
    UpdatePatient,
)
from .infrastructure.repositories import DjangoDossierSequence, DjangoPatientRepository


@dataclass(frozen=True)
class PatientUseCases:
    register: RegisterPatient
    update: UpdatePatient
    archive: ArchivePatient
    get: GetPatient
    search: SearchPatients


def build_patient_use_cases() -> PatientUseCases:
    patients = DjangoPatientRepository()
    audit = get_audit_trail()
    uow = DjangoUnitOfWork()
    clock = SystemClock(settings.TIME_ZONE)
    return PatientUseCases(
        register=RegisterPatient(
            patients=patients,
            sequence=DjangoDossierSequence(),
            audit=audit,
            events=event_bus,
            uow=uow,
            clock=clock,
        ),
        update=UpdatePatient(patients=patients, audit=audit, uow=uow, clock=clock),
        archive=ArchivePatient(patients=patients, audit=audit, uow=uow, clock=clock),
        get=GetPatient(patients=patients),
        search=SearchPatients(patients=patients),
    )


def build_get_patient_summary() -> GetPatientSummary:
    return GetPatientSummary(patients=DjangoPatientRepository())
