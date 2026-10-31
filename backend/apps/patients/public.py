"""API publique du module `patients` : ce que les autres modules ont le droit d'utiliser.

Les autres modules reçoivent des objets simples (`PatientSummary`), jamais l'entité complète
ni la table : ils ne dépendent donc pas du fonctionnement interne de `patients`.
"""

from uuid import UUID

from .application.use_cases import PatientSummary
from .composition import build_get_patient_summary
from .domain.events import PatientRegistered


def get_patient_summary(public_id: UUID) -> PatientSummary | None:
    return build_get_patient_summary().execute(public_id)


def patient_exists(public_id: UUID) -> bool:
    return get_patient_summary(public_id) is not None


__all__ = ["PatientRegistered", "PatientSummary", "get_patient_summary", "patient_exists"]
