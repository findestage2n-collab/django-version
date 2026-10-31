"""Droits par rôle : chaque vue déclare quelle permission exige chaque action.

    permission_map = {"list": "patients.view_patient", "create": "patients.add_patient"}

Une action absente de la table est REFUSÉE (sûr par défaut). La couche HTTP ne dépend ainsi
d'aucun modèle de base de données (contrairement à DjangoModelPermissions).
"""

from rest_framework.permissions import BasePermission


class HasActionPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False  # DRF répond 401 grâce à l'authentification JWT
        if request.method == "OPTIONS":
            return True
        required = getattr(view, "permission_map", {}).get(getattr(view, "action", None))
        return bool(required) and request.user.has_perm(required)
