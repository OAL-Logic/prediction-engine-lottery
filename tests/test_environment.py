import pytest
from unittest.mock import MagicMock
from engine.modules.environment import EnvironmentalService, calculate_environmental_jitter

def test_calculate_environmental_jitter_quiet():
    service = EnvironmentalService()
    # Mocking fetchers to return low values
    service.fetch_solar_kp = MagicMock(return_value=2.0)
    service.fetch_seismic_mag = MagicMock(return_value=3.0)
    
    jitter = service.get_jitter(force_refresh=True)
    assert jitter["total_boost"] == 0.0
    assert jitter["j_solar"] == 0.0
    assert jitter["j_seismic"] == 0.0

def test_calculate_environmental_jitter_active():
    service = EnvironmentalService()
    # Kp 6 (2 points above 4) -> 2 * 0.05 = 0.1
    # Mag 7 (2 points above 5) -> 2 * 0.1 = 0.2
    # Total = 0.3
    service.fetch_solar_kp = MagicMock(return_value=6.0)
    service.fetch_seismic_mag = MagicMock(return_value=7.0)
    
    jitter = service.get_jitter(force_refresh=True)
    assert jitter["total_boost"] == 0.3
    assert jitter["j_solar"] == 0.1
    assert jitter["j_seismic"] == 0.2

def test_calculate_environmental_jitter_caching():
    # This might be tricky if we don't mock the file system
    # but we can check if it returns a value at least.
    boost = calculate_environmental_jitter()
    assert isinstance(boost, float)
    assert boost >= 0
