import pytest

from core.infrastructure.events import InProcessEventBus
from core.kernel.events import DomainEvent


class Ping(DomainEvent):
    pass


@pytest.fixture
def bus():
    return InProcessEventBus()


def test_publish_calls_subscribers(bus):
    received = []
    bus.subscribe(Ping)(received.append)
    bus.publish(Ping(), after_commit=False)
    assert len(received) == 1


def test_failing_subscriber_does_not_break_others(bus):
    received = []

    def boom(event):
        raise RuntimeError("boom")

    bus.subscribe(Ping)(boom)
    bus.subscribe(Ping)(received.append)
    bus.publish(Ping(), after_commit=False)
    assert len(received) == 1
