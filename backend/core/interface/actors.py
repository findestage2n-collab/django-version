from core.kernel.ports import Actor


def actor_from_request(request) -> Actor:
    """Convertit l'utilisateur authentifié du framework en `Actor` (valeur simple du noyau)."""
    user = request.user
    ip = request.META.get("REMOTE_ADDR") or None
    if not getattr(user, "is_authenticated", False):
        return Actor(public_id=None, username="", ip_address=ip)
    return Actor(public_id=user.public_id, username=user.get_username(), ip_address=ip)
