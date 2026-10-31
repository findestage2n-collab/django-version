from collections.abc import Callable
from typing import Any


class MappedQuerySet:
    """Adapte un QuerySet en `ResultSet` : le total et les tranches sont lus à la demande,
    et chaque ligne ORM est convertie en entité du domaine (le reste du code ignore l'ORM)."""

    def __init__(self, queryset, mapper: Callable[[Any], Any]) -> None:
        self._queryset = queryset
        self._mapper = mapper

    def count(self) -> int:
        return self._queryset.count()

    def __len__(self) -> int:
        return self.count()

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self._mapper(row) for row in self._queryset[index]]
        return self._mapper(self._queryset[index])
