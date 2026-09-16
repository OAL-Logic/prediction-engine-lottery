"""
Pattern Search CLI Tests 🔎
===========================
`pattern-search` is the "has anything like this come up before" historical
lookup (SamLotto's nsSearch equivalent). Runs against real cached history —
no network calls, since `fetch()` reads the local cache when present.
"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.pattern_search import _parse_numbers

runner = CliRunner()
GAME = "br/mega-sena"


def test_parse_numbers_dedupes_and_sorts():
    assert _parse_numbers("5, 1, 3, 1") == [1, 3, 5]


def test_pattern_search_registered_and_runs():
    result = runner.invoke(app, ["pattern-search", GAME, "--numbers", "1,2,3,4,5,6", "--min-overlap", "1"])
    assert result.exit_code == 0, result.output
    assert "PATTERN SEARCH" in result.output


def test_pattern_search_rejects_out_of_range_numbers():
    result = runner.invoke(app, ["pattern-search", GAME, "--numbers", "999"])
    assert result.exit_code != 0
    assert "within" in result.output


def test_pattern_search_rejects_empty_numbers():
    result = runner.invoke(app, ["pattern-search", GAME, "--numbers", ""])
    assert result.exit_code != 0


def test_pattern_search_finds_exact_historical_draw():
    """Searching for a real historical draw's own numbers must return a perfect match."""
    from engine.cli.utils import get_adapter
    df = get_adapter(GAME).fetch()
    known = df.iloc[0]
    ticket = ",".join(str(n) for n in known["numbers"])

    result = runner.invoke(app, ["pattern-search", GAME, "--numbers", ticket, "--min-overlap", "6", "--top", "50"])
    assert result.exit_code == 0, result.output
    assert str(known["draw_id"]) in result.output
