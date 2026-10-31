"""Bus d'événements EN MÉMOIRE (aucun service externe : fonctionne hors ligne).

Implémente le port `EventPublisher`. Les abonnés s'exécutent APRÈS validation de la
transaction courante. Pour passer plus tard à un broker, il suffit d'écrire une autre
implémentation du même port : les cas d'usage ne changent pas.
"""

import logging
from collections import defaultdict
from collections.abc import Callable

from django.db import transaction

from core.kernel.events import DomainEvent

logger = logging.getLogger(__name__)


class InProcessEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent]):
        """Décorateur : enregistre un gestionnaire pour un type d'événement."""

        def decorator(handler: Callable):
            self._subscribers[event_type].append(handler)
            return handler

        return decorator

    def publish(self, event: DomainEvent, *, after_commit: bool = True) -> None:
        def _dispatch() -> None:
            for handler in list(self._subscribers[type(event)]):
                try:
                    handler(event)
                except Exception:  # un abonné défaillant ne casse ni la requête ni les autres
                    logger.exception("Gestionnaire d'événement en échec : %s", handler.__qualname__)

        if after_commit:
            transaction.on_commit(_dispatch)
        else:
            _dispatch()

    def clear(self) -> None:
        """Réservé aux tests."""
        self._subscribers.clear()


event_bus = InProcessEventBus()
