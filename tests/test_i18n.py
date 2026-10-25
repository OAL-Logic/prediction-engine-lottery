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
