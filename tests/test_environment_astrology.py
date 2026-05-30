"""
Unit and integration tests for high-fidelity astrology ecliptic transformation, aspects, and NOAA solar flux.
"""

import pytest
from datetime import datetime

from engine.modules.environment import (
    HAS_ASTROPY,
    EnvironmentalService,
    calculate_great_circles,
    calculate_aspects,
    calculate_environmental_jitter
)

if HAS_ASTROPY:
    from astropy.time import Time


def test_calculate_aspects():
    # Setup planetary positions to produce known aspects
    # Sun = 0 deg, Moon = 120 deg (Trine), Mars = 90 deg (Square), Jupiter = 180 deg (Opposition)
    body_lons = {
        "sun": 0.0,
        "moon": 120.0,
        "mars": 90.0,
        "jupiter": 180.0,
        "venus": 300.0  # Sun sextile Venus (300-360 = 60 deg)
    }
    
    aspects = calculate_aspects(body_lons)
    
    assert len(aspects) > 0
    
    # Check that the aspect keys are present
    aspect_names = [a["aspect"] for a in aspects]
    assert "Trine" in aspect_names
    assert "Square" in aspect_names
    assert "Opposition" in aspect_names
    assert "Sextile" in aspect_names


@pytest.mark.skipif(not HAS_ASTROPY, reason="AstroPy is required for great circles calculation")
def test_great_circles_calculation():
    t = Time.now()
    # São Paulo, BR coordinates
    angles = calculate_great_circles(-23.5505, -46.6333, t)
    
    assert "AC" in angles
    assert "MC" in angles
    assert "DC" in angles
    assert "IC" in angles
    
    for k, v in angles.items():
        assert 0.0 <= v <= 360.0


def test_environmental_service_solar_f107():
    service = EnvironmentalService()
    
    # Fetches solar flux or fallback value
    f107 = service.fetch_solar_f107()
    assert isinstance(f107, float)
    assert f107 > 0.0


def test_calculate_environmental_jitter():
    jitter = calculate_environmental_jitter()
    assert isinstance(jitter, float)
    assert jitter >= 0.0
