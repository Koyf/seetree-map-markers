import random

FAILURE_PROBABILITY = 1 / 3


def should_fail() -> bool:
    """Random failure injection for marker creation. Kept separate so tests can monkeypatch it."""
    return random.random() < FAILURE_PROBABILITY
