"""
New adapter parsing tests 🌍
=============================
Pure, network-free tests for MegaMillionsAdapter / EuroMillionsAdapter row
parsing. No adapter in this repo has direct unit tests today (fetch() hits
live networks; CLI smoke tests cover the integrated path instead) — these
cover just the pure `_parse_draw` functions, which take plain dicts and
have no I/O, so they're cheap to test directly.

Registry <-> adapter wiring is covered separately in
test_adapters_registry_consistency.py.
"""

from __future__ import annotations

from engine.adapters.us.mega_millions import MegaMillionsAdapter
from engine.adapters.eu.euro_millions import EuroMillionsAdapter


# ── Mega Millions (NY Socrata JSON row shape) ────────────────────────────────

def test_mega_millions_parse_draw_socrata_row():
    adapter = MegaMillionsAdapter()
    row = {
        "draw_date": "2026-09-15T00:00:00.000",
        "winning_numbers": "27 36 43 57 58",
        "mega_ball": "16",
    }
    draw = adapter._parse_draw(row)
    assert draw is not None
    assert draw.draw_id == 20260915
    assert draw.date == "2026-09-15"
    assert draw.numbers == [27, 36, 43, 57, 58]
    assert draw.bonus == [16]


def test_mega_millions_parse_draw_rejects_missing_fields():
    adapter = MegaMillionsAdapter()
    assert adapter._parse_draw({"draw_date": "2026-09-15T00:00:00.000"}) is None


def test_mega_millions_parse_draw_rejects_short_number_list():
    adapter = MegaMillionsAdapter()
    row = {"draw_date": "2026-09-15T00:00:00.000", "winning_numbers": "1 2 3", "mega_ball": "5"}
    assert adapter._parse_draw(row) is None


# ── EuroMillions (community CSV row shape) ───────────────────────────────────

def test_euro_millions_parse_draw_csv_row():
    adapter = EuroMillionsAdapter()
    row = {"date": "2026-09-12", "n1": "16", "n2": "29", "n3": "32", "n4": "36", "n5": "41", "s1": "7", "s2": "9"}
    draw = adapter._parse_draw(row)
    assert draw is not None
    assert draw.draw_id == 20260912
    assert draw.date == "2026-09-12"
    assert draw.numbers == [16, 29, 32, 36, 41]
    assert draw.bonus == [7, 9]


def test_euro_millions_parse_draw_rejects_missing_fields():
    adapter = EuroMillionsAdapter()
    assert adapter._parse_draw({"date": "2026-09-12"}) is None


# ── Rules sanity (catches transposed pick/pool typos) ────────────────────────

def test_mega_millions_rules_shape():
    rules = MegaMillionsAdapter().rules
    assert rules.pick_count == 5
    assert rules.number_range == (1, 70)
    assert rules.bonus_range == (1, 25)


def test_euro_millions_rules_shape():
    rules = EuroMillionsAdapter().rules
    assert rules.pick_count == 5
    assert rules.number_range == (1, 50)
    assert rules.bonus_range == (1, 12)
