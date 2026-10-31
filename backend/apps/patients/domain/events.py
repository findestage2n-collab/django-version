from dataclasses import dataclass
from uuid import UUID

from core.kernel.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PatientRegistered(DomainEvent):
    """Publié après la validation de la transaction d'enregistrement d'un patient."""

    patient_public_id: UUID
