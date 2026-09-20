import pytest

from app import failure


@pytest.mark.parametrize(
    ("roll", "expected"), [(0.0, True), (0.33, True), (0.34, False), (0.99, False)]
)
def test_should_fail_threshold(monkeypatch, roll, expected):
    """Verify that should_fail compares the random roll against the 1/3 threshold."""
    monkeypatch.setattr(failure.random, "random", lambda: roll)
    assert failure.should_fail() is expected
