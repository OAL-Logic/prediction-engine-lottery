"""
Internationalization (i18n) Engine 🌐
====================================
Lightweight, dictionary-driven internationalization framework for universal lottery terminology,
CLI output formatting, desktop localization, and report generation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "pt_br")

_current_locale: str = DEFAULT_LOCALE
_catalogs: Dict[str, Dict[str, Any]] = {}
_LOCALES_DIR = Path(__file__).parent / "locales"


def normalize_locale(locale: Optional[str]) -> str:
    """Normalizes language/locale strings (e.g. 'pt-BR', 'pt', 'PT_BR' -> 'pt_br')."""
    if not locale:
        return DEFAULT_LOCALE
    clean = locale.lower().strip().replace("-", "_")
    if clean in ("pt", "pt_br", "pt_pt"):
        return "pt_br"
    if clean.startswith("en"):
        return "en"
    return clean if clean in SUPPORTED_LOCALES else DEFAULT_LOCALE


def _load_catalog(locale: str) -> Dict[str, Any]:
    """Loads and caches the translation dictionary for a specific locale."""
    norm = normalize_locale(locale)
    if norm in _catalogs:
        return _catalogs[norm]

    yaml_file = _LOCALES_DIR / f"{norm}.yaml"
    if not yaml_file.exists():
        if norm != DEFAULT_LOCALE:
            return _load_catalog(DEFAULT_LOCALE)
        return {}

    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            _catalogs[norm] = data
            return data
    except Exception:
        return {}


def set_locale(locale: str) -> str:
    """Sets the active global locale for this session."""
    global _current_locale
    _current_locale = normalize_locale(locale)
    return _current_locale


def get_locale() -> str:
    """Gets the currently active locale."""
    return _current_locale


def resolve_locale(
    cli_locale: Optional[str] = None,
    game_id: Optional[str] = None,
    config_locale: Optional[str] = None,
) -> str:
    """
    Resolves the appropriate locale using the priority hierarchy:
    1. Explicit CLI argument (--locale / -l)
    2. User configuration file (config.yaml / personal.local.yaml)
    3. Game jurisdiction heuristic (e.g. 'br/*' lotteries default to 'pt_br', others to 'en')
    4. Environment variable (LOTTERY_LOCALE or LANG)
    5. Default fallback ('en')
    """
    if cli_locale:
        return normalize_locale(cli_locale)

    if config_locale:
        return normalize_locale(config_locale)

    if game_id and (game_id.lower().startswith("br/") or game_id.lower().startswith("br-")):
        return "pt_br"

    env_loc = os.environ.get("LOTTERY_LOCALE") or os.environ.get("LANG")
    if env_loc:
        norm_env = normalize_locale(env_loc.split(".")[0])
        if norm_env in SUPPORTED_LOCALES:
            return norm_env

    return DEFAULT_LOCALE


def t(key: str, locale: Optional[str] = None, **kwargs: Any) -> Any:
    """
    Translates a dot-notated key with optional formatting arguments.
    Falls back gracefully from target locale -> 'en' -> key itself.
    """
    active_loc = normalize_locale(locale or _current_locale)
    catalog = _load_catalog(active_loc)

    parts = key.split(".")
    val: Any = catalog
    found = True
    for p in parts:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            found = False
            break

    # Fallback to English if not found in active locale
    if not found and active_loc != DEFAULT_LOCALE:
        en_catalog = _load_catalog(DEFAULT_LOCALE)
        val = en_catalog
        found = True
        for p in parts:
            if isinstance(val, dict) and p in val:
                val = val[p]
            else:
                found = False
                break

    if not found:
        return key

    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, ValueError):
            return val

    return val


def get_weekday_names(short: bool = True, locale: Optional[str] = None) -> List[str]:
    """Returns a list of 7 weekday names (Monday to Sunday) for the given locale."""
    key = "weekdays_short" if short else "weekdays_full"
    res = t(key, locale=locale)
    if isinstance(res, list) and len(res) == 7:
        return res
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if short else [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]
