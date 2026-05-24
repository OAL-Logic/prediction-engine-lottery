import asyncio
import json
import websockets
from PySide6.QtCore import QThread, Signal, QObject

class TelemetryClient(QThread):
    """
    WebSocket client for the Desktop Client.
    Subscribes to the Go Gateway telemetry stream and emits PySide6 signals.
    """
    new_log = Signal(str, str) # message, level

    def __init__(self, url: str = "ws://127.0.0.1:8080/telemetry"):
        super().__init__()
        self.url = url
        self._stop_event = asyncio.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        asyncio.run(self._listen())

    async def _listen(self):
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self.url) as websocket:
                    self.new_log.emit("Connected to Telemetry Hub.", "SUCCESS")
                    while not self._stop_event.is_set():
                        try:
                            # Use wait_for to check stop_event periodically
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            data = json.loads(message)
                            self.new_log.emit(data.get("message", ""), data.get("level", "INFO"))
                        except asyncio.TimeoutError:
                            continue
                        except websockets.ConnectionClosed:
                            self.new_log.emit("Connection to Telemetry Hub lost. Retrying...", "WARN")
                            break
            except Exception as e:
                self.new_log.emit(f"Telemetry Hub unreachable: {str(e)}. Retrying in 5s...", "ERROR")
                await asyncio.sleep(5)
