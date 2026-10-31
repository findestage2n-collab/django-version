"""Couche HTTP : forme des données échangées. Les RÈGLES métier restent dans le domaine."""

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.patients.domain.entities import MAX_LENGTHS, Sexe
from apps.patients.domain.repositories import SORTABLE_FIELDS


class PatientListSerializer(serializers.Serializer):
    public_id = serializers.UUIDField(read_only=True)
    numero_dossier = serializers.CharField(read_only=True)
    nom = serializers.CharField(read_only=True)
    prenom = serializers.CharField(read_only=True)
    sexe = serializers.ChoiceField(choices=[s.value for s in Sexe], read_only=True)
    date_naissance = serializers.DateField(read_only=True, allow_null=True)
    telephone = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class PatientDetailSerializer(PatientListSerializer):
    age = serializers.SerializerMethodField()
    lieu_naissance = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    adresse = serializers.CharField(read_only=True)
    profession = serializers.CharField(read_only=True)
    personne_contact_nom = serializers.CharField(read_only=True)
    personne_contact_telephone = serializers.CharField(read_only=True)
    assurance_nom = serializers.CharField(read_only=True)
    assurance_numero = serializers.CharField(read_only=True)
    taux_prise_en_charge = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_age(self, patient) -> int | None:
        return patient.age_on(timezone.localdate())


def _text(name: str, *, required: bool = False) -> serializers.CharField:
    return serializers.CharField(
        max_length=MAX_LENGTHS[name], required=required, allow_blank=not required
    )


class PatientWriteSerializer(serializers.Serializer):
    """Entrée de création/modification. Les champs non listés ici sont ignorés."""

    nom = _text("nom", required=True)
    prenom = _text("prenom", required=True)
    sexe = serializers.ChoiceField(choices=[s.value for s in Sexe])
    date_naissance = serializers.DateField(required=False, allow_null=True)
    lieu_naissance = _text("lieu_naissance")
    telephone = _text("telephone")
    email = serializers.EmailField(required=False, allow_blank=True)
    adresse = _text("adresse")
    profession = _text("profession")
    personne_contact_nom = _text("personne_contact_nom")
    personne_contact_telephone = _text("personne_contact_telephone")
    assurance_nom = _text("assurance_nom")
    assurance_numero = _text("assurance_numero")
    taux_prise_en_charge = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    allow_duplicate = serializers.BooleanField(
        write_only=True,
        required=False,
        help_text="Forcer la création malgré un doublon probable (défaut : faux).",
    )


ORDERING_CHOICES = [*SORTABLE_FIELDS, *(f"-{field}" for field in SORTABLE_FIELDS)]


class PatientSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False, allow_blank=True, help_text="Recherche (nom, prénom, n° dossier, téléphone)"
    )
    sexe = serializers.ChoiceField(choices=[s.value for s in Sexe], required=False)
    created_after = serializers.DateField(required=False)
    created_before = serializers.DateField(required=False)
    ordering = serializers.ChoiceField(choices=ORDERING_CHOICES, required=False)

    def to_criteria_kwargs(self) -> dict:
        data = dict(self.validated_data)
        if "sexe" in data:
            data["sexe"] = Sexe(data["sexe"])
        return data


__all__ = [
    "PatientDetailSerializer",
    "PatientListSerializer",
    "PatientSearchQuerySerializer",
    "PatientWriteSerializer",
]
