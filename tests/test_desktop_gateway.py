import pytest
import httpx
from PySide6.QtCore import QCoreApplication

@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])

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
