import datetime
from datetime import date, timedelta
import numpy as np
import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.strategies.fun.planetary_transits import (
    get_julian_date,
    get_obliquity,
    get_lst,
    placidus_cusp,
    get_kepler_longitude,
    get_positions_vectorized,
    get_timezone_offset,
    make_ascii_wheel,
    PlanetaryTransitsStrategy
)

def test_julian_date():
    # Test J2000 epoch: Jan 1.5, 2000 (12:00 UT)
    dt = datetime.datetime(2000, 1, 1, 12, 0, 0)
    assert get_julian_date(dt) == 2451545.0

def test_obliquity():
    # Obliquity at J2000 epoch is approx 23.4392911
    obl = get_obliquity(2451545.0)
    assert abs(obl - 23.4392911) < 1e-5

def test_lst():
    # Test LST for a known date and location
    jd = 2451545.0
    lon = -84.2727
    lst = get_lst(jd, lon)
    assert 0.0 <= lst < 360.0

def test_placidus_cusp():
    ramc = 125.755
    lat = 30.4518
    obl = 23.4392911
    
    # House 11
    c11 = placidus_cusp(ramc, lat, obl, 30, 1/3, 1)
    assert 0 <= c11 < 360.0
    
    # House 2
    c2 = placidus_cusp(ramc, lat, obl, 120, 2/3, -1)
    assert 0 <= c2 < 360.0

def test_keplerian_longitude():
    dt = datetime.datetime(2026, 6, 21, 20, 0, 0)
    # Sun
    sun_lon = get_kepler_longitude("sun", dt)
    assert 0 <= sun_lon < 360.0
    # Moon
    moon_lon = get_kepler_longitude("moon", dt)
    assert 0 <= moon_lon < 360.0
    # Pluto
    pluto_lon = get_kepler_longitude("pluto", dt)
    assert 0 <= pluto_lon < 360.0

def test_positions_vectorized():
    dates = [date(2026, 6, 20), date(2026, 6, 21)]
    p = get_positions_vectorized(dates)
    assert len(p["sun"]) == 2
    assert len(p["moon"]) == 2
    assert len(p["pluto"]) == 2
    assert np.all(p["sun"] >= 0) and np.all(p["sun"] < 360.0)

def test_timezone_offset():
    assert get_timezone_offset("br/mega-sena", date(2026, 6, 21)) == -3.0
    assert get_timezone_offset("us/powerball", date(2026, 6, 21)) == -4.0 # DST
    assert get_timezone_offset("us/powerball", date(2026, 12, 21)) == -5.0 # EST

def test_make_ascii_wheel():
    planet_houses = {
        "sun": 9,
        "moon": 5,
        "mercury": 9,
        "venus": 9,
        "mars": 8,
        "jupiter": 6,
        "saturn": 11,
        "uranus": 8,
        "neptune": 12,
        "pluto": 10
    }
    wheel = make_ascii_wheel(planet_houses)
    assert "☉Su" in wheel
    assert "☽Mo" in wheel
    assert "10 (MC)" in wheel

def test_planetary_transits_strategy_score():
    rules = DrawRules(name="test", pick_count=6, number_range=(1, 60))
    # Dummy history of 30 draws
    dates_list = [date(2026, 5, 1) + timedelta(days=i) for i in range(30)]
    df = pd.DataFrame({
        "date": pd.to_datetime(dates_list),
        "numbers": [list(range(1, 7)) for _ in range(30)]
    })
    
    strat = PlanetaryTransitsStrategy(draw_date="2026-06-21")
    scores = strat.score(df, rules)
    
    assert len(scores) == 60
    assert all(0 <= v <= 1 for v in scores.values())
    
    # Suggestion check
    result = strat.suggest(df, rules, count=1)
    assert len(result.tickets) == 1
    assert len(result.tickets[0]) == 6
    assert "placidus_wheel" in result.metadata
    assert "aspects_count" in result.metadata
    assert "matched_draws" in result.metadata
