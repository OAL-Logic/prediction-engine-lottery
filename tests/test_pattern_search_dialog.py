import pandas as pd
import pytest
from PySide6.QtCore import QCoreApplication

from desktop.src.widgets.pattern_search_dialog import rank_by_overlap, PatternSearchDialog


def _df(rows):
    return pd.DataFrame([{"draw_id": i + 1, "date": f"2026-01-{i+1:02d}", "numbers": nums} for i, nums in enumerate(rows)])


def test_rank_by_overlap_orders_best_first():
    df = _df([[1, 2, 3], [1, 2, 9], [1, 8, 9]])
    matches = rank_by_overlap(df, {1, 2, 3}, min_overlap=1)
    assert matches[0][0] == 1  # draw_id 1 has overlap 3, ranked first
    assert matches[0][3] == 3


def test_rank_by_overlap_respects_min_overlap():
    df = _df([[1, 2, 3], [4, 5, 6]])
    matches = rank_by_overlap(df, {1, 2, 3}, min_overlap=2)
    assert len(matches) == 1


@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])


def test_dialog_constructs(app, qtbot):
    dialog = PatternSearchDialog(lottery_id="br/mega-sena")
    qtbot.addWidget(dialog)
    assert dialog.table.columnCount() == 4


def test_dialog_rejects_empty_input(app, qtbot):
    dialog = PatternSearchDialog(lottery_id="br/mega-sena")
    qtbot.addWidget(dialog)
    dialog.numbers_input.setText("")
    dialog.run_search()
    assert "at least one number" in dialog.status_label.text()


def test_dialog_runs_real_search(app, qtbot):
    dialog = PatternSearchDialog(lottery_id="br/mega-sena")
    qtbot.addWidget(dialog)
    dialog.numbers_input.setText("1,2,3,4,5,6")
    dialog.min_overlap_spin.setValue(1)
    dialog.run_search()
    assert "matched" in dialog.status_label.text()
