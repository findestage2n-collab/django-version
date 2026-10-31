"""PORTS de sortie du module : le domaine dit ce dont il a besoin, l'infrastructure le fournit."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from core.kernel.ports import ResultSet

from .entities import Patient, Sexe

SORTABLE_FIELDS = ("nom", "prenom", "created_at", "numero_dossier")


@dataclass(frozen=True)
class PatientSearch:
    q: str = ""  # nom, prénom, n° de dossier ou téléphone (contient)
    sexe: Sexe | None = None
    created_after: date | None = None
    created_before: date | None = None
    ordering: str = "-created_at"  # champ de SORTABLE_FIELDS, préfixé de « - » pour décroissant


class PatientRepository(Protocol):
    def add(self, patient: Patient) -> Patient: ...
    def get(self, public_id: UUID) -> Patient | None:
        """Retourne un patient NON archivé, ou None."""
        ...

    def save(self, patient: Patient) -> None: ...
    def has_duplicate(self, patient: Patient) -> bool:
        """Un AUTRE patient de mêmes nom, prénom et date de naissance existe-t-il ?"""
        ...

    def search(self, criteria: PatientSearch) -> ResultSet[Patient]: ...


class DossierSequence(Protocol):
    def next_value(self, year: int) -> int:
        """Prochain numéro d'ordre de l'année (sûr en accès concurrent)."""
        ...
