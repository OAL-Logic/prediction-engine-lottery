"""Calendar Export CLI Tests 🗓️"""

from __future__ import annotations

from datetime import date

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.calendar_export import next_draw_dates, build_ics

runner = CliRunner()
GAME = "br/mega-sena"  # Wednesday, Saturday


def test_next_draw_dates_only_returns_matching_weekdays():
    dates = next_draw_dates(["Wednesday", "Saturday"], count=6, start=date(2026, 1, 1))  # Thursday
    assert len(dates) == 6
    for d in dates:
        assert d.weekday() in (2, 5)  # Wed=2, Sat=5
    assert dates == sorted(dates)


def test_next_draw_dates_empty_draw_days():
    assert next_draw_dates([], count=3) == []


def test_build_ics_has_valid_structure():
    dates = [date(2026, 3, 4), date(2026, 3, 7)]
    ics = build_ics("Mega-Sena", "br/mega-sena", dates)
    assert ics.startswith("BEGIN:VCALENDAR\r\n")
    assert ics.rstrip().endswith("END:VCALENDAR")
    assert ics.count("BEGIN:VEVENT") == 2
    assert "DTSTART;VALUE=DATE:20260304" in ics
    assert "SUMMARY:Mega-Sena draw" in ics


def test_calendar_export_registered_and_runs():
    result = runner.invoke(app, ["calendar-export", GAME, "--count", "3"])
    assert result.exit_code == 0, result.output
    assert "BEGIN:VCALENDAR" in result.output


def test_calendar_export_writes_file(tmp_path):
    out = tmp_path / "draws.ics"
    result = runner.invoke(app, ["calendar-export", GAME, "--count", "2", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "BEGIN:VCALENDAR" in out.read_text()


def test_calendar_export_rejects_unknown_lottery():
    result = runner.invoke(app, ["calendar-export", "xx/not-a-game"])
    assert result.exit_code != 0
