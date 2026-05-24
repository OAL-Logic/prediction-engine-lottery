import pytest
import asyncio
import json
import websockets
from PySide6.QtCore import QCoreApplication
from desktop.src.telemetry.client import TelemetryClient

@pytest.fixture
def app(qtbot):
    return QCoreApplication.instance() or QCoreApplication([])

async def mock_ws_server(stop_event):
    async def handler(websocket):
        await websocket.send(json.dumps({
            "source": "engine",
            "level": "INFO",
            "message": "hello from mock"
        }))
        await stop_event.wait()
    
    async with websockets.serve(handler, "127.0.0.1", 8989):
        await stop_event.wait()

@pytest.mark.asyncio
async def test_desktop_client_receives_ws(app, qtbot):
    stop_event = asyncio.Event()
    
    # Start mock server in background
    server_task = asyncio.create_task(mock_ws_server(stop_event))
    await asyncio.sleep(0.5)
    
    client = TelemetryClient(url="ws://127.0.0.1:8989")
    
    # We use a signal blocker to wait for the specific message
    with qtbot.waitSignal(client.new_log, timeout=5000) as blocker:
        client.start()
        
    assert blocker.args[0] == "hello from mock"
    
    client.stop()
    client.wait()
    stop_event.set()
    await server_task
