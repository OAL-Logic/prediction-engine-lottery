# Story 5.5: Real-time Telemetry WebSocket

Status: done

## Story

As a **Strategic Custodian**,
I want to see real-time feedback during long-running model training and quantum distillation jobs,
So that I can monitor the engine's cognitive state and signal fidelity without the interface freezing.

## Acceptance Criteria

1. **Telemetry Hub Implementation**: Develop a WebSocket-based Telemetry Hub in the Go Gateway (`gateway/telemetry_hub.go`) that can broadcast messages to multiple clients. (AC: 5.5.1)
2. **PyQt Signal Bridge**: Implement a `ProphetTelemetryBridge` in the Desktop Client that translates incoming WebSocket messages into PySide6 signals. (AC: 5.5.2)
3. **Semantic Highlighting**: The telemetry stream must support semantic tags (e.g., `[INFO]`, `[RESONANCE]`, `[DECOHERENCE]`) for color-coded rendering in the Desktop and TUI viewports. (AC: 5.5.3)
4. **Non-blocking Emission**: The Python Engine must emit telemetry pulses via a non-blocking UDP or internal socket to the Go Gateway to maintain P99 latency targets. (AC: 5.5.4)
5. **V11 Parity**: Ensure that the telemetry stream includes updates for MARL swarm learning progress and Quantum Sidecar job status. (AC: 5.5.5)

## Tasks / Subtasks

- [x] Implement the `TelemetryHub` in Go using `nhooyr.io/websocket`.
- [x] Develop the `log_emitter.py` utility in the Python Engine for non-blocking status updates.
- [x] Implement the WebSocket client in the Desktop Client (`desktop/src/telemetry/`).
- [x] Connect the `SequenceLogicBrain` and `QuantumSidecar` to the telemetry emitter.
- [x] Add integration tests verifying that a message emitted by Python is received by a Qt-based observer.

## Dev Notes

- **Implementation**: Created a unified Telemetry Hub in Go that bridges internal UDP pulses to external WebSocket subscribers.
- **Python Pulse**: Developed `TelemetryEmitter` in `engine/modules/telemetry.py` using non-blocking UDP for minimal latency impact on the analytical core.
- **Deep Integration**: Added telemetry heartbeats to `LSTMCRFStrategy`, `RegressorHubStrategy`, and `QuantumSidecar` distillation loops.
- **Desktop Connection**: Implemented a `TelemetryClient` `QThread` in PySide6 that translates WebSocket JSON streams into UI log updates.
- **Verification**: Validated Go Hub logic with `telemetry_hub_test.go` and Python emission with `test_python_telemetry.py`.

### Project Structure Notes

- **Go Hub**: `gateway/telemetry_hub.go` (NEW)
- **Python Emitter**: `engine/modules/telemetry.py` (NEW)
- **Desktop Client**: `desktop/src/telemetry/client.py` (NEW)
- **Tests**: `gateway/telemetry_hub_test.go`, `tests/test_python_telemetry.py`

### References

- [Source: LottoProphet/thread_utils.py]
- [Source: docs/research/prophet-concepts.md#3. Real-time Telemetry]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Fixed `nhooyr.io/websocket` dependency persistence in `go.mod`.
- Resolved import path issues in `desktop/src/main.py` by using package-aware absolute imports.
- Handled non-blocking UDP emission to ensure the engine doesn't block on gateway unavailability.

### Completion Notes List

- ✅ Implemented real-time telemetry bridge (Python -> Go -> PySide6).
- ✅ Verified message propagation from engine pulses to WebSocket subscribers.
- ✅ Hardened desktop client robustness with automatic reconnection logic.

### File List

- `gateway/telemetry_hub.go` (NEW)
- `gateway/main.go` (MODIFIED)
- `engine/modules/telemetry.py` (NEW)
- `engine/strategies/deep/lstm_crf.py` (MODIFIED)
- `engine/strategies/ml/regressor_hub.py` (MODIFIED)
- `engine/modules/cosmic.py` (MODIFIED)
- `desktop/src/telemetry/client.py` (NEW)
- `desktop/src/main.py` (MODIFIED)
- `gateway/telemetry_hub_test.go` (NEW)
- `tests/test_python_telemetry.py` (NEW)
- `pyproject.toml` (MODIFIED)
