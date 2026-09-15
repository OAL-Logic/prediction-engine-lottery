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
