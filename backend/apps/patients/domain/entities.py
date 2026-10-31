"""ENTITÉ du domaine : un patient et ses règles. Python pur : aucun import Django.

Toutes les règles métier du patient (champs autorisés, longueurs, date de naissance,
téléphone, taux de prise en charge, âge) vivent ICI et nulle part ailleurs. Les couches
externes (API, base de données) s'adaptent à ces règles, jamais l'inverse.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from apps.patients.domain.errors import InvalidPatientData


class Sexe(StrEnum):
    MASCULIN = "M"
    FEMININ = "F"


# Liste blanche : seuls ces champs sont modifiables depuis l'extérieur (anti « mass assignment »).
WRITABLE_FIELDS = (
    "nom", "prenom", "sexe", "date_naissance", "lieu_naissance", "telephone", "email",
    "adresse", "profession", "personne_contact_nom", "personne_contact_telephone",
    "assurance_nom", "assurance_numero", "taux_prise_en_charge",
)  # fmt: skip

MAX_LENGTHS = {
    "nom": 100, "prenom": 100, "lieu_naissance": 100, "telephone": 30, "email": 254,
    "adresse": 255, "profession": 100, "personne_contact_nom": 150,
    "personne_contact_telephone": 30, "assurance_nom": 100, "assurance_numero": 50,
}  # fmt: skip
REQUIRED_FIELDS = ("nom", "prenom", "sexe")
PHONE_FIELDS = ("telephone", "personne_contact_telephone")
PHONE_RE = re.compile(r"^\+?[0-9 ()\-.]{6,30}$")


def _normalize(values: Mapping[str, Any], *, today: date) -> dict[str, Any]:
    """Valide et normalise les valeurs reçues ; rassemble TOUTES les erreurs."""
    cleaned: dict[str, Any] = {}
    errors: dict[str, list[str]] = {}

    def fail(name: str, message: str) -> None:
        errors.setdefault(name, []).append(message)

    for name in WRITABLE_FIELDS:
        if name not in values:
            continue
        value = values[name]
        if name == "sexe":
            try:
                cleaned[name] = Sexe(value)
            except ValueError:
                fail(name, "Valeur attendue : M ou F.")
        elif name == "date_naissance":
            if value is not None and not isinstance(value, date):
                fail(name, "Date invalide.")
            elif value is not None and value > today:
                fail(name, "La date de naissance ne peut pas être future.")
            else:
                cleaned[name] = value
        elif name == "taux_prise_en_charge":
            try:
                rate = Decimal(str(value))
            except InvalidOperation:
                fail(name, "Nombre invalide.")
                continue
            if not Decimal(0) <= rate <= Decimal(100):
                fail(name, "Le taux doit être compris entre 0 et 100.")
            else:
                cleaned[name] = rate
        else:
            text = str(value or "").strip()
            if name in REQUIRED_FIELDS and not text:
                fail(name, "Ce champ est obligatoire.")
            elif len(text) > MAX_LENGTHS[name]:
                fail(name, f"{MAX_LENGTHS[name]} caractères maximum.")
            elif name in PHONE_FIELDS and text and not PHONE_RE.match(text):
                fail(name, "Numéro de téléphone invalide.")
            else:
                cleaned[name] = text
    if errors:
        raise InvalidPatientData(errors)
    return cleaned


@dataclass
class Patient:
    public_id: UUID
    numero_dossier: str
    nom: str
    prenom: str
    sexe: Sexe
    date_naissance: date | None = None
    lieu_naissance: str = ""
    telephone: str = ""
    email: str = ""
    adresse: str = ""
    profession: str = ""
    personne_contact_nom: str = ""
    personne_contact_telephone: str = ""
    assurance_nom: str = ""
    assurance_numero: str = ""
    taux_prise_en_charge: Decimal = Decimal(0)
    created_by: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    @classmethod
    def register(
        cls,
        *,
        numero_dossier: str,
        data: Mapping[str, Any],
        created_by: UUID | None,
        today: date,
    ) -> Patient:
        """Crée un nouveau patient valide ; refuse toute donnée hors liste blanche."""
        missing = {
            name: ["Ce champ est obligatoire."] for name in REQUIRED_FIELDS if name not in data
        }
        if missing:
            raise InvalidPatientData(missing)
        cleaned = _normalize(data, today=today)
        return cls(
            public_id=uuid4(), numero_dossier=numero_dossier, created_by=created_by, **cleaned
        )

    def update(self, changes: Mapping[str, Any], *, today: date) -> list[str]:
        """Applique des modifications valides ; retourne les NOMS des champs modifiés."""
        cleaned = _normalize(changes, today=today)
        for name, value in cleaned.items():
            setattr(self, name, value)
        return sorted(cleaned)

    def archive(self, *, now: datetime) -> None:
        """Archivage logique : un dossier médical n'est jamais détruit."""
        self.deleted_at = now

    @property
    def is_archived(self) -> bool:
        return self.deleted_at is not None

    def age_on(self, today: date) -> int | None:
        born = self.date_naissance
        if born is None:
            return None
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def format_numero_dossier(year: int, value: int) -> str:
    """Ex. `P2026-000042`."""
    return f"P{year}-{value:06d}"
