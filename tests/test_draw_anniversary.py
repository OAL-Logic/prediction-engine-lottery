"""Draw Anniversary CLI Tests 📅"""

from __future__ import annotations

from datetime import date

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.draw_anniversary import anniversary_matches
from engine.cli.utils import get_adapter

runner = CliRunner()
GAME = "br/mega-sena"


def test_anniversary_matches_filters_by_month_day():
    df = get_adapter(GAME).fetch()
    known = df.iloc[0]
    d = known["date"].date() if hasattr(known["date"], "date") else known["date"]

    matches = anniversary_matches(df, d.month, d.day)
    assert any(m[0] == known["draw_id"] for m in matches)
    assert all(m[1].month == d.month and m[1].day == d.day for m in matches)


def test_draw_anniversary_registered_and_runs():
    result = runner.invoke(app, ["draw-anniversary", GAME, "--date", "2026-01-01"])
    assert result.exit_code == 0, result.output
    assert "DRAW ANNIVERSARY" in result.output


def test_draw_anniversary_rejects_bad_date():
    result = runner.invoke(app, ["draw-anniversary", GAME, "--date", "not-a-date"])
    assert result.exit_code != 0
