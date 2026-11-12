import math

import pytest

from engine.swarm.kelly import MAX_FRACTION, confidence_leverage


def test_above_baseline():
    r = confidence_leverage(0.6, 1000, 1.0)
    assert r.full_kelly == pytest.approx(0.2)
    assert r.fraction == pytest.approx(0.05)
    assert r.stake == pytest.approx(50)
    assert r.active


@pytest.mark.parametrize("p", [0.5, 0.4, 0.0])
def test_at_or_below_baseline(p):
    r = confidence_leverage(p, 1000)
    assert (r.fraction, r.stake, r.active) == (0.0, 0.0, False)


def test_cap():
    r = confidence_leverage(0.99, 1000, 1.0)
    assert r.full_kelly == pytest.approx(0.98)
    assert r.fraction == MAX_FRACTION == 0.10
    assert r.stake == pytest.approx(100)


def test_zero_balance():
    r = confidence_leverage(0.9, 0)
    assert r.fraction > 0 and r.stake == 0 and r.active


def test_negative_edge_gives_zero():
    r = confidence_leverage(0.55, 1000, odds=0.5)  # f* < 0
    assert r.fraction == 0 and not r.active


@pytest.mark.parametrize(
    "args",
    [
        (math.nan, 100),
        (math.inf, 100),
        (1.2, 100),
        (-0.1, 100),
        (0.6, -1),
        (0.6, math.nan),
        (0.6, 100, 0),
        (0.6, 100, -1),
        (0.6, 100, math.nan),
    ],
)
def test_bad_input(args):
    with pytest.raises(ValueError):
        confidence_leverage(*args)
