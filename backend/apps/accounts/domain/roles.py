"""Définition déclarative des rôles et de leurs permissions (données pures, sans Django).

Ajouter un module = ajouter ses permissions ici, puis relancer `seed_roles`.
Les clés "app.modele" désignent les permissions Django `view_/add_/change_/delete_<modele>`.
"""

CRUD = ("view", "add", "change", "delete")
VIEW = ("view",)

ROLE_DEFINITIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "ADMIN": {"accounts.user": CRUD, "audit.auditlog": VIEW, "patients.patient": CRUD},
    "SECRETAIRE": {"patients.patient": CRUD},
    "MEDECIN": {"patients.patient": VIEW},
    "INFIRMIER": {"patients.patient": VIEW},
    "PHARMACIEN": {"patients.patient": VIEW},
    "LABORANTIN": {"patients.patient": VIEW},
    "CAISSIER": {"patients.patient": VIEW},
}
