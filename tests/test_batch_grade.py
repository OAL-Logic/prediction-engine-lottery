"""Batch Grade CLI Tests 📋"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.batch_grade import parse_tickets_file, score_ticket
from engine.cli.utils import get_adapter

runner = CliRunner()
GAME = "br/mega-sena"


def test_parse_tickets_file_skips_blank_and_comment_lines(tmp_path):
    f = tmp_path / "tickets.txt"
    f.write_text("1 2 3 4 5 6\n\n# a comment\n7 8 9 10 11 12\n")
    tickets = parse_tickets_file(str(f))
    assert tickets == [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]


def test_score_ticket_flags_validity():
    adapter = get_adapter(GAME)
    valid = score_ticket([1, 2, 3, 4, 5, 6], adapter)
    invalid = score_ticket([1, 2, 3], adapter)  # too few numbers for mega-sena
    assert valid["valid"] is True
    assert invalid["valid"] is False
    assert valid["odd_even"] == "3/3"
    assert valid["primes"] == 3  # 2, 3, 5


def test_batch_grade_registered_and_runs(tmp_path):
    f = tmp_path / "tickets.txt"
    f.write_text("1 2 3 4 5 6\n10 20 30 40 50 60\n")
    result = runner.invoke(app, ["batch-grade", GAME, "--file", str(f)])
    assert result.exit_code == 0, result.output
    assert "BATCH GRADE" in result.output
    assert "2/2" in result.output


def test_batch_grade_exports_csv(tmp_path):
    tickets_file = tmp_path / "tickets.txt"
    tickets_file.write_text("1 2 3 4 5 6\n")
    csv_out = tmp_path / "out.csv"
    result = runner.invoke(app, ["batch-grade", GAME, "--file", str(tickets_file), "--export-csv", str(csv_out)])
    assert result.exit_code == 0, result.output
    assert csv_out.exists()
    content = csv_out.read_text()
    assert "numbers" in content
    assert "1 2 3 4 5 6" in content


def test_batch_grade_missing_file_errors():
    result = runner.invoke(app, ["batch-grade", GAME, "--file", "/no/such/file.txt"])
    assert result.exit_code != 0
