from contextlib import AbstractContextManager

from django.db import transaction


class DjangoUnitOfWork:
    """Implémente le port `UnitOfWork` avec `transaction.atomic`."""

    def atomic(self) -> AbstractContextManager[None]:
        return transaction.atomic()
