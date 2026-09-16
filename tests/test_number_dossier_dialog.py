import pytest
from PySide6.QtCore import QCoreApplication

from desktop.src.widgets.number_dossier_dialog import NumberDossierDialog


@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])


def test_dialog_constructs_with_correct_range(app, qtbot):
    dialog = NumberDossierDialog(lottery_id="br/mega-sena")
    qtbot.addWidget(dialog)
    assert dialog.number_spin.minimum() == 1
    assert dialog.number_spin.maximum() == 60


def test_lookup_populates_result_label(app, qtbot):
    dialog = NumberDossierDialog(lottery_id="br/mega-sena")
    qtbot.addWidget(dialog)
    dialog.number_spin.setValue(10)
    dialog.run_lookup()
    assert "Hits:" in dialog.result_label.text()
    assert "Current gap:" in dialog.result_label.text()
