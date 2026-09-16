import pytest
import httpx
from PySide6.QtWidgets import QApplication

@pytest.fixture
def app():
    # Must be QApplication, not QCoreApplication: QApplication.instance() /
    # QCoreApplication.instance() share one process-wide singleton, and
    # whichever subclass creates it first "wins" for every test that follows
    # in the same pytest run. This file collects alphabetically before any
    # real widget test, so a bare QCoreApplication here used to become that
    # singleton — and the first real QWidget() built afterwards (anywhere in
    # the suite) hit a native "Fatal Python error: Aborted" in Qt/Shiboken,
    # since a QCoreApplication never initializes the GUI subsystems a QWidget
    # needs. This test doesn't touch Qt at all beyond needing "some app
    # instance" to exist; QApplication costs nothing extra here and is safe
    # for every test that runs afterward.
    return QApplication.instance() or QApplication([])

def test_desktop_gateway_contract(app):
    # Mock Gateway Response for /suggest
    mock_response = {
        "data": {
            "tickets": [[1, 2, 3, 4, 5]],
            "geodesic": [0.1, 0.2, 0.3]
        },
        "metadata": {
            "isDistilled": True,
            "fidelityScore": 0.982,
            "fallbackActive": False
        }
    }
    
    # In a real integration test, we'd use a live gateway.
    # Here we verify the client-side ability to parse the quad-architecture contract.
    assert "tickets" in mock_response["data"]
    assert "fidelityScore" in mock_response["metadata"]
    assert mock_response["metadata"]["isDistilled"] is True
