import pytest
from PySide6.QtWidgets import QApplication

from desktop.src.widgets.quick_calculator import combination_cost, QuickCalculatorDialog


def test_combination_cost_basic():
    result = combination_cost(60, 6, ticket_price=5.0)
    assert result["valid"] is True
    assert result["combinations"] == 50_063_860
    assert result["cost"] == 50_063_860 * 5.0


def test_combination_cost_invalid_when_pick_exceeds_pool():
    result = combination_cost(5, 6)
    assert result["valid"] is False
    assert result["combinations"] == 0


def test_combination_cost_zero_price_zero_cost():
    result = combination_cost(10, 3)
    assert result["cost"] == 0.0
    assert result["combinations"] == 120


@pytest.fixture
def app():
    # Must be QApplication — see test_desktop_gateway.py's fixture comment.
    return QApplication.instance() or QApplication([])


def test_dialog_constructs_and_shows_result(app, qtbot):
    dialog = QuickCalculatorDialog(pool_size=15, pick_count=6, ticket_price=3.5)
    qtbot.addWidget(dialog)
    assert "5,005" in dialog.result_label.text()  # C(15,6) = 5005


def test_dialog_recalculates_on_change(app, qtbot):
    dialog = QuickCalculatorDialog(pool_size=10, pick_count=3, ticket_price=1.0)
    qtbot.addWidget(dialog)
    assert "120" in dialog.result_label.text()

    dialog.pool_spin.setValue(20)
    assert "1,140" in dialog.result_label.text()  # C(20,3) = 1140
