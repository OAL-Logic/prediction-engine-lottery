# Story 3.1: Go-Python Bridge Hardening

Status: complete

## Story

As an **Architect**,
I want the Go Gateway to propagate deadlines to the Python sidecar,
so that long-running analytical requests are cancelled across the entire triad if the user disconnects.

## Acceptance Criteria

1. **Deadline Propagation**: The Go Gateway must include the `X-Request-Deadline` header (ISO-8601 or Unix timestamp) when proxying to Python. (AC: 3.1.1) [x]
2. **Sidecar Context Awareness**: The Python FastAPI sidecar must extract this header and use it to set a `request_timeout` on internal analytical tasks. (AC: 3.1.2) [x]
3. **Task Termination**: If the deadline is exceeded, the Python engine must terminate the CPU-bound task and return a `408 Request Timeout`. (AC: 3.1.3) [x]
4. **Integration Test**: Verify that a simulated long-running request in Go is correctly terminated in Python when the timeout is reached. (AC: 3.1.4) [x]

## Dev Notes

- **Header Propagation**: Implemented in `gateway/main.go` using `r.Context().Deadline()`.
- **Timeout Middleware**: Added to `engine/api/main.py` using `asyncio.wait_for`.
- **Verification**: Verified via `tests/test_bridge_timeout.py`.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Hardened Go Gateway with explicit deadline propagation.
- ✅ Implemented `TimeoutMiddleware` in the FastAPI sidecar.
- ✅ Verified 408 response code for expired request deadlines.

### File List

- `gateway/main.go` (MODIFIED)
- `engine/api/main.py` (MODIFIED)
- `tests/test_bridge_timeout.py` (NEW)
