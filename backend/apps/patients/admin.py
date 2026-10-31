from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("numero_dossier", "nom", "prenom", "sexe", "created_at")
    search_fields = ("numero_dossier", "nom", "prenom")
    readonly_fields = ("numero_dossier", "public_id", "created_by_public_id")

    def get_queryset(self, request):
        return Patient.all_objects.all()  # l'admin voit aussi les dossiers archivés
