"""
Esoteric Pipeline Tests 🔮
==========================
Unit tests for the deterministic seed-derivation used by `suggest --weather-seed`,
`suggest --esoteric-mode`, and `genetic-wheel --weather-seed`.

These use explicit `override_*` values (no network) so they run fast and
deterministically in any environment. Network-fetch fallback behaviour is
exercised indirectly by the CLI smoke tests, which tolerate `None` weather
values gracefully (matching production behaviour when Open-Meteo/NOAA/USGS
are unreachable).
"""

from __future__ import annotations

from datetime import date

from engine.modules.esoteric_pipeline import EsotericPipeline, build_environmental_seed


def _context(**overrides):
    pipeline = EsotericPipeline()
    params = dict(
        coords=(-23.5505, -46.6333),
        target_date="2026-09-15",
        override_solar_kp=3.0,
        override_seismic_mag=0.0,
        override_lunar_phase=0.13,
        override_tide_level=0.47,
        override_temp_c=15.8,
        override_precip_mm=5.5,
    )
    params.update(overrides)
    return pipeline, pipeline.compile_context(**params)


def test_no_personal_data_required():
    """compile_context() must work with zero personal data (pure environmental use)."""
    pipeline, ctx = _context()
    assert ctx["full_name"] == ""
    assert ctx["numerology"]["destiny"] is not None  # still computed from placeholder birth_date


def test_seed_is_deterministic():
    """Same inputs -> same seed, every time (this is the entire point of the feature)."""
    pipeline, ctx = _context()
    seed_a = pipeline.derive_seed(ctx)
    seed_b = pipeline.derive_seed(ctx)
    assert seed_a == seed_b
    assert isinstance(seed_a, int)


def test_seed_changes_with_real_inputs():
    """Changing an actual environmental reading must change the seed (it's a real hash, not a stub)."""
    pipeline, ctx_a = _context()
    _, ctx_b = _context(override_temp_c=30.0)
    seed_a = pipeline.derive_seed(ctx_a)
    seed_b = pipeline.derive_seed(ctx_b)
    assert seed_a != seed_b


def test_generate_weights_returns_full_pool():
    pipeline, ctx = _context()
    seed, weights = pipeline.generate_weights(ctx, 1, 25)
    assert isinstance(seed, int)
    assert set(weights.keys()) == set(range(1, 26))
    assert all(0.0 <= w <= 1.0 for w in weights.values())


def test_build_environmental_seed_convenience(monkeypatch):
    """build_environmental_seed() should not require network when overrides cover everything."""
    seed, ctx = build_environmental_seed(
        coords=(-23.5505, -46.6333),
        target_date=date(2026, 9, 15),
        override_solar_kp=3.0,
        override_seismic_mag=0.0,
        override_lunar_phase=0.13,
        override_tide_level=0.47,
        override_temp_c=15.8,
        override_precip_mm=5.5,
    )
    assert isinstance(seed, int)
    assert ctx["environmental"]["temperature_c"] == 15.8
    assert ctx["target_date"] == "2026-09-15"


def test_celestial_ephemeris_and_vortex_seed_determinism():
    """Verify celestial ephemeris (Sun/Moon/Earth/Sidereal/Season/Diurnal/Vortex) computes deterministically."""
    pipeline, ctx_20 = _context(
        target_date="2026-10-29",
        target_time="20:00",
        override_wind_kmh=42.0,
        override_pressure_hpa=1004.5,
    )
    _, ctx_12 = _context(
        target_date="2026-10-29",
        target_time="12:00",
        override_wind_kmh=42.0,
        override_pressure_hpa=1004.5,
    )
    assert "celestial_ephemeris" in ctx_20
    eph = ctx_20["celestial_ephemeris"]
    assert eph["season"] == "Spring"  # Southern hemisphere in October
    assert eph["diurnal_period"] == "Evening/Nocturnal"
    assert 0.0 <= eph["sun_longitude_deg"] < 360.0
    assert 0.0 <= eph["moon_longitude_deg"] < 360.0
    assert 0.0 <= eph["earth_heliocentric_lon_deg"] < 360.0
    assert 0.98 <= eph["earth_sun_distance_au"] <= 1.02
    assert eph["vortex_convective_index"] > 0.0

    # Changing draw time or vortex parameters must deterministically shift the seed and weights
    seed_20, weights_20 = pipeline.generate_weights(ctx_20, 1, 60)
    seed_12, weights_12 = pipeline.generate_weights(ctx_12, 1, 60)
    assert seed_20 != seed_12
    assert weights_20 != weights_12


def test_esoteric_statistical_multi_archetype():
    """Validate EsotericStatisticalStrategy across 3 distinct game archetypes (Mega-Sena 6/60, Lotofacil 15/25, Powerball 5/69+1/26)."""
    import pandas as pd
    from engine.cli.utils import get_adapter
    from engine.strategies.fun.esoteric_statistical import EsotericStatisticalStrategy

    strat = EsotericStatisticalStrategy(
        full_name="GEMINI ENGINE",
        birth_date="1990-01-01",
        target_date="2026-10-29",
        target_time="20:00",
        wind_kmh=28.0,
        pressure_hpa=1009.0,
    )
    for slug in ("br/mega-sena", "br/lotofacil", "us/powerball"):
        adapter = get_adapter(slug)
        rules = adapter.rules
        lo, hi = rules.number_range
        # Synthetic minimal dataframe for fast offline verification
        df = pd.DataFrame({
            "draw_id": [1, 2, 3],
            "numbers": [
                list(range(lo, lo + rules.pick_count)),
                list(range(lo + 1, lo + 1 + rules.pick_count)),
                list(range(lo + 2, lo + 2 + rules.pick_count)),
            ],
        })
        res = strat.suggest(df, rules, count=2)
        assert len(res.tickets) == 2
        for t in res.tickets:
            assert len(t) == rules.pick_count
            assert all(lo <= n <= hi for n in t)
            assert len(set(t)) == rules.pick_count
