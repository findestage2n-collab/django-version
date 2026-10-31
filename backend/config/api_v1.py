"""Routes de l'API v1 : un préfixe par module métier (web et mobile)."""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.api.urls")),
    path("audit/", include("apps.audit.api.urls")),
    path("personnel/", include("apps.personnel.api.urls")),
    path("patients/", include("apps.patients.api.urls")),
    path("rendez-vous/", include("apps.rendezvous.api.urls")),
    path("consultations/", include("apps.consultations.api.urls")),
    path("hospitalisations/", include("apps.hospitalisations.api.urls")),
    path("laboratoire/", include("apps.laboratoire.api.urls")),
    path("pharmacie/", include("apps.pharmacie.api.urls")),
    path("facturation/", include("apps.facturation.api.urls")),
    path("paiements/", include("apps.paiements.api.urls")),
    path("rapports/", include("apps.rapports.api.urls")),
    path("notifications/", include("apps.notifications.api.urls")),
]
