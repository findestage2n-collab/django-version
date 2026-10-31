from datetime import date, datetime
from zoneinfo import ZoneInfo


class SystemClock:
    """Horloge injectable (les tests la remplacent par une horloge figée)."""

    def __init__(self, timezone: str = "UTC") -> None:
        self._tz = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._tz)

    def today(self) -> date:
        return self.now().date()
