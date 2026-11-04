"""
Unit tests for the Internationalization (i18n) Engine.
"""

import pytest
from engine.i18n import (
    DEFAULT_LOCALE,
    get_locale,
    get_weekday_names,
    normalize_locale,
    resolve_locale,
    set_locale,
    t,
)


def test_normalize_locale():
    assert normalize_locale("pt-BR") == "pt_br"
    assert normalize_locale("pt_br") == "pt_br"
    assert normalize_locale("PT") == "pt_br"
    assert normalize_locale("en") == "en"
    assert normalize_locale("en_US") == "en"
    assert normalize_locale("en-GB") == "en"
    assert normalize_locale(None) == DEFAULT_LOCALE
    assert normalize_locale("unknown_lang") == DEFAULT_LOCALE


def test_resolve_locale_hierarchy(monkeypatch):
    monkeypatch.delenv("LOTTERY_LOCALE", raising=False)
    monkeypatch.delenv("LANG", raising=False)

    # 1. Flag overrides everything
    assert resolve_locale(cli_locale="en", game_id="br/mega-sena") == "en"
    assert resolve_locale(cli_locale="pt_br", game_id="us/powerball") == "pt_br"

    # 2. Config overrides heuristic
    assert resolve_locale(config_locale="en", game_id="br/mega-sena") == "en"

    # 3. Game jurisdiction heuristic
    assert resolve_locale(game_id="br/mega-sena") == "pt_br"
    assert resolve_locale(game_id="br/lotofacil") == "pt_br"
    assert resolve_locale(game_id="us/powerball") == "en"
    assert resolve_locale(game_id="eu/euro-millions") == "en"

    # 4. Fallback default
    assert resolve_locale() == DEFAULT_LOCALE


def test_translation_lookup_and_formatting():
    # English
    en_title = t("suggest.title", locale="en")
    assert en_title == "SUGGESTION ENGINE"

    en_clover = t(
        "suggest.lucky_clover_profile",
        locale="en",
        birth_date="1990-01-01",
        lucky_num=7,
        day="Sunday",
        lucky_days="[7, 16]",
        life_path=3,
    )
    assert "Lucky Clover Profile" in en_clover
    assert "Harmonic Day: Sunday" in en_clover

    # Portuguese
    pt_title = t("suggest.title", locale="pt_br")
    assert pt_title == "MOTOR DE SUGESTÕES"

    pt_clover = t(
        "suggest.lucky_clover_profile",
        locale="pt_br",
        birth_date="1990-01-01",
        lucky_num=7,
        day="Domingo",
        lucky_days="[7, 16]",
        life_path=3,
    )
    assert "Trevo da Sorte" in pt_clover
    assert "Dia Ideal: Domingo" in pt_clover


def test_fallback_behavior():
    # If key doesn't exist, returns key itself
    missing_key = "non.existent.key.xyz"
    assert t(missing_key, locale="pt_br") == missing_key


def test_weekday_names():
    en_short = get_weekday_names(short=True, locale="en")
    assert en_short == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    pt_short = get_weekday_names(short=True, locale="pt_br")
    assert pt_short == ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    en_full = get_weekday_names(short=False, locale="en")
    assert en_full[0] == "Monday"

    pt_full = get_weekday_names(short=False, locale="pt_br")
    assert pt_full[0] == "Segunda-feira"


def test_set_and_get_locale():
    original = get_locale()
    try:
        set_locale("pt_br")
        assert get_locale() == "pt_br"
        assert t("suggest.title") == "MOTOR DE SUGESTÕES"

        set_locale("en")
        assert get_locale() == "en"
        assert t("suggest.title") == "SUGGESTION ENGINE"
    finally:
        set_locale(original)


def test_materialize_and_variations_i18n():
    """Verify materialize, variations, and chamber translations in en and pt_br."""
    # English
    assert "LET THE DRUMS ROLL" in t("materialize.title", locale="en")
    assert "Variation 1 — Celestial" in t("variations.celeste", locale="en")
    assert "Variation 2 — Magnetic Force" in t("variations.magnetica", locale="en")
    assert "Variation 3 — Quantum Force" in t("variations.quantica", locale="en")
    assert "Variation 4 — Overdue Lag" in t("variations.atrasao", locale="en")
    assert "Variation 5 — 4-Force Synthesis" in t("variations.sintese", locale="en")
    assert "Extension #3" in t("variations.extension", locale="en", idx=3)

    # Portuguese
    assert "QUE RUFEM OS TAMBORES" in t("materialize.title", locale="pt_br")
    assert "Variação 1 — Celeste" in t("variations.celeste", locale="pt_br")
    assert "Variação 2 — Força Magnética" in t("variations.magnetica", locale="pt_br")
    assert "Variação 3 — Força Quântica" in t("variations.quantica", locale="pt_br")
    assert "Variação 4 — Atrasão" in t("variations.atrasao", locale="pt_br")
    assert "Variação 5 — Síntese 4 Forças" in t("variations.sintese", locale="pt_br")
    assert "Extensão #3" in t("variations.extension", locale="pt_br", idx=3)


def test_html_materialization_chamber_multilanguage(tmp_path):
    """Verify HTML5 chamber generates valid language tags and localized buttons."""
    from engine.cli.commands.materialize import generate_html_materialization_chamber

    dummy_pacote = [{"modalidade": "mega-sena", "jogos": [[1, 2, 3, 4, 5, 6]], "rotulos": ["Var 1"]}]
    dummy_eph = {
        "target_date": "2026-10-29",
        "target_time": "20:00",
        "lunar_phase_name": "Full Moon",
        "lunar_phase_ratio": 0.62,
        "sun_longitude_deg": 216.5,
        "sun_zodiac_sign": "Scorpio",
        "earth_heliocentric_lon_deg": 36.5,
        "earth_zodiac_sign": "Taurus",
        "earth_orbital_speed_kms": 29.99,
    }

    # EN
    en_file = tmp_path / "chamber_en.html"
    generate_html_materialization_chamber(dummy_pacote, dummy_eph, 12345, out_path=en_file, locale="en")
    en_content = en_file.read_text(encoding="utf-8")
    assert '<html lang="en">' in en_content
    assert "LET THE DRUMS ROLL" in en_content
    assert "Roll Drums" in en_content
    assert "Consecrate & Seal" in en_content
    assert "INHALE (4s)" in en_content

    # PT_BR
    pt_file = tmp_path / "chamber_pt.html"
    generate_html_materialization_chamber(dummy_pacote, dummy_eph, 12345, out_path=pt_file, locale="pt_br")
    pt_content = pt_file.read_text(encoding="utf-8")
    assert '<html lang="pt-BR">' in pt_content
    assert "QUE RUFEM OS TAMBORES" in pt_content
    assert "Rufar Tambores" in pt_content
    assert "Consagrar & Selar" in pt_content
    assert "INSPIRAR (4s)" in pt_content


def test_esoteric_surgical_variations_multilanguage():
    """Verify EsotericPipeline.generate_surgical_variations supports explicit locale."""
    import pandas as pd
    from engine.cli.utils import get_adapter
    from engine.modules.esoteric_pipeline import EsotericPipeline

    adapter = get_adapter("br/mega-sena")
    lo, hi = adapter.rules.number_range
    df = pd.DataFrame({
        "draw_id": list(range(1, 16)),
        "date": [f"2025-10-{15 + i:02d}" for i in range(15)],
        "numbers": [list(range(lo + (i % 5), lo + (i % 5) + 6)) for i in range(15)],
    })

    ep = EsotericPipeline()
    res_en = ep.generate_surgical_variations(df, adapter.rules, target_date="2026-10-29", extra_wheel_tickets=1, locale="en")
    assert any("Variation 1 — Celestial" in v["label"] for v in res_en["variations"])
    assert "Extension #1" in res_en["extensions"][0]["label"]

    res_pt = ep.generate_surgical_variations(df, adapter.rules, target_date="2026-10-29", extra_wheel_tickets=1, locale="pt_br")
    assert any("Variação 1 — Celeste" in v["label"] for v in res_pt["variations"])
    assert "Extensão #1" in res_pt["extensions"][0]["label"]
