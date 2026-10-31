import logging

from django.contrib.auth.models import Group, Permission

from apps.accounts.domain.roles import ROLE_DEFINITIONS

logger = logging.getLogger(__name__)


def apply_roles() -> dict[str, int]:
    """Crée/met à jour les groupes et leurs permissions (idempotent)."""
    summary: dict[str, int] = {}
    for role, grants in ROLE_DEFINITIONS.items():
        group, _ = Group.objects.get_or_create(name=role)
        permissions = []
        for target, actions in grants.items():
            app_label, model = target.split(".")
            codenames = [f"{action}_{model}" for action in actions]
            found = list(
                Permission.objects.filter(
                    content_type__app_label=app_label,
                    content_type__model=model,
                    codename__in=codenames,
                )
            )
            if len(found) != len(codenames):
                logger.warning("Permissions introuvables pour %s (%s)", target, role)
            permissions.extend(found)
        group.permissions.set(permissions)
        summary[role] = len(permissions)
    return summary
