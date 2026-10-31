from datetime import date

from core.kernel.clock import SystemClock
from core.kernel.ports import Actor


def test_clock_returns_a_date_in_its_timezone():
    assert isinstance(SystemClock("Africa/Douala").today(), date)


def test_system_actor_has_no_identity():
    assert Actor.system().public_id is None
