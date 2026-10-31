"""Django cherche les modèles ici. Les vrais modèles sont dans `infrastructure/models.py`."""

from .infrastructure.models import NumeroDossierSequence, Patient

__all__ = ["NumeroDossierSequence", "Patient"]
