import pytest
import sys
from PySide6.QtWidgets import QApplication

from desktop.src.tabs.database import DatabaseTab
from desktop.src.tabs.analysis import AnalysisTab
from desktop.src.tabs.filters import FiltersTab
from desktop.src.tabs.wheeling import WheelingTab
from desktop.src.tabs.verification import VerificationTab
from desktop.src.main import ProphetDashboard

@pytest.fixture(scope="session")
def qapp():
    """Initialises a session-wide QApplication to support headless GUI widget testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_database_tab_init(qapp):
    tab = DatabaseTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert tab.table_view is not None

def test_analysis_tab_init(qapp):
    tab = AnalysisTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert tab.combo_analysis_type is not None

def test_filters_tab_init(qapp):
    tab = FiltersTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab._active_filters) == 0

def test_wheeling_tab_init(qapp):
    tab = WheelingTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab.pool_numbers) == 0
    assert len(tab.key_numbers) == 0

def test_verification_tab_init(qapp):
    tab = VerificationTab()
    assert tab is not None
    assert tab.active_lottery == "br/lotofacil"
    assert len(tab.tickets) == 0

def test_prophet_dashboard_init(qapp):
    dashboard = ProphetDashboard()
    assert dashboard is not None
    assert dashboard.active_lottery == "br/lotofacil"
    
    # Verify exact 8 tabs are registered
    assert dashboard.tabs.count() == 8
    
    # Verify lottery context propagation
    dashboard.change_global_lottery("br/mega-sena")
    assert dashboard.active_lottery == "br/mega-sena"
    assert dashboard.analysis_tab.active_lottery == "br/mega-sena"
    assert dashboard.filters_tab.active_lottery == "br/mega-sena"
    assert dashboard.wheeling_tab.active_lottery == "br/mega-sena"
    assert dashboard.verification_tab.active_lottery == "br/mega-sena"
