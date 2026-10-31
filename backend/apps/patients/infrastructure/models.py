"""Tables de la base de données (détail technique : le domaine ne les connaît pas)."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.infrastructure.models import SoftDeleteModel


class Patient(SoftDeleteModel):
    """Ligne de la table `patients_patient`. Le métier utilise l'entité `domain.Patient`."""

    numero_dossier = models.CharField(max_length=20, unique=True, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[("M", "Masculin"), ("F", "Féminin")])
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=30, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    personne_contact_nom = models.CharField(max_length=150, blank=True)
    personne_contact_telephone = models.CharField(max_length=30, blank=True)
    assurance_nom = models.CharField(max_length=100, blank=True)
    assurance_numero = models.CharField(max_length=50, blank=True)
    taux_prise_en_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage pris en charge par l'assurance (0 à 100).",
    )
    # Identifiant public (pas de clé étrangère) : le module reste indépendant d'accounts.
    created_by_public_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["nom", "prenom"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(taux_prise_en_charge__gte=0)
                & models.Q(taux_prise_en_charge__lte=100),
                name="patient_taux_prise_en_charge_0_100",
            )
        ]

    def __str__(self) -> str:
        return f"{self.numero_dossier} - {self.nom} {self.prenom}"


class NumeroDossierSequence(models.Model):
    """Compteur annuel verrouillé en base : numéros uniques même en accès concurrent."""

    year = models.PositiveSmallIntegerField(primary_key=True)
    last_value = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.year}: {self.last_value}"
