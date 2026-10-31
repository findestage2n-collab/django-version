"""Contexte d'exécution (identifiant de requête) : `contextvars` est de la bibliothèque standard."""

from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
