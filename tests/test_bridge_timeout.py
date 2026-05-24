import time
import pytest
from fastapi.testclient import TestClient
from engine.api.main import app

client = TestClient(app)

def test_timeout_middleware_exceeded():
    """STORY 3.1: Verify that a request with an expired deadline returns 408."""
    # Set a deadline that is already in the past
    past_deadline = time.time() - 10
    response = client.get("/", headers={"X-Request-Deadline": str(past_deadline)})
    
    assert response.status_code == 408
    assert "deadline already exceeded" in response.json()["detail"]

def test_timeout_middleware_active():
    """STORY 3.1: Verify that a request with a valid deadline passes."""
    future_deadline = time.time() + 10
    response = client.get("/", headers={"X-Request-Deadline": str(future_deadline)})
    
    assert response.status_code == 200
    assert response.json()["status"] == "online"
