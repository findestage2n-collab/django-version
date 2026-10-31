from django.core.management.base import BaseCommand

from apps.accounts.infrastructure.role_seeder import apply_roles


class Command(BaseCommand):
    help = "Crée les rôles (groupes) et leur affecte les permissions. Idempotent."

    def handle(self, *args, **options):
        for role, count in apply_roles().items():
            self.stdout.write(f"{role}: {count} permission(s)")
