import socket
import json
import time
import threading
from engine.modules.telemetry import pulse

def test_python_emitter_flow():
    # Start a UDP listener to catch the pulse
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 9000))
    sock.settimeout(2.0)
    
    received_msgs = []
    
    def listen():
        try:
            data, _ = sock.recvfrom(4096)
            received_msgs.append(json.loads(data.decode("utf-8")))
        except Exception as e:
            received_msgs.append(str(e))

    t = threading.Thread(target=listen)
    t.start()
    
    # Emit pulse
    pulse("test message from python", "RESONANCE")
    
    t.join()
    sock.close()
    
    assert len(received_msgs) == 1
    assert received_msgs[0]["message"] == "test message from python"
    assert received_msgs[0]["level"] == "RESONANCE"

if __name__ == "__main__":
    test_python_emitter_flow()
    print("Python Emitter Test PASSED")
