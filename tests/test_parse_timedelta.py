import pytest
from blackmirror_lite.rollback import parse_timedelta

@pytest.mark.parametrize("delta,expected", [
    ("5s", 5),
    ("3m", 180),
    ("2h", 7200),
    ("1d", 86400),
])
def test_parse_timedelta_valid(delta, expected):
    assert parse_timedelta(delta) == expected

@pytest.mark.parametrize("delta", ["5", "h", "10x", ""])
def test_parse_timedelta_invalid(delta):
    with pytest.raises(ValueError):
        parse_timedelta(delta)