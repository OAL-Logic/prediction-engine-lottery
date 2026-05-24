import socket
import json
import datetime
import logging
from typing import Optional

class TelemetryEmitter:
    """Non-blocking UDP emitter for real-time telemetry."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9000, source: str = "engine"):
        self.host = host
        self.port = port
        self.source = source
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def emit(self, message: str, level: str = "INFO"):
        """Sends a telemetry pulse to the Go Gateway."""
        payload = {
            "source": self.source,
            "level": level.upper(),
            "message": message,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            self.sock.sendto(data, (self.host, self.port))
        except Exception:
            # UDP is fire-and-forget, we don't want to crash the engine if gateway is down
            pass

# Singleton instance
emitter = TelemetryEmitter()

def pulse(message: str, level: str = "INFO"):
    """Global helper for emitting telemetry pulses."""
    emitter.emit(message, level)
