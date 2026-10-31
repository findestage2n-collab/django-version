"""Erreurs métier. Levées par le domaine et les cas d'usage, traduites en HTTP par l'interface."""


class DomainError(Exception):
    """Violation d'une règle métier."""

    code = "domain_error"
    status_code = 400  # indication pour la couche HTTP ; le domaine ne la lit jamais
    default_message = "Opération refusée par une règle métier."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


class ValidationFailed(DomainError):
    """Données invalides : `details` associe chaque champ fautif à ses messages."""

    code = "validation_error"
    status_code = 400
    default_message = "Les données envoyées sont invalides."

    def __init__(self, details: dict[str, list[str]], message: str | None = None):
        super().__init__(message, details=details)


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404
    default_message = "Ressource introuvable."


class ConflictError(DomainError):
    code = "conflict"
    status_code = 409
    default_message = "Conflit avec l'état actuel de la ressource."
