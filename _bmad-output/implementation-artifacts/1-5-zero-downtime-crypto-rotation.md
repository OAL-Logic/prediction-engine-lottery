# Story 1.5: Zero-Downtime Crypto Rotation

Status: done

## Story

As a **Swarm Architect**,
I want to rotate cryptographic algorithms and keys without interrupting the live swarm,
So that the platform remains secure from the latest quantum threats without predictive downtime.

## Acceptance Criteria

1. **Algorithm Agility**: The Go Gateway must support multiple PQC algorithms (e.g., Kyber/ML-KEM and Dilithium/ML-DSA) concurrently. (AC: 1.5.1)
2. **Seamless Negotiation**: Clients must be able to negotiate a new algorithm during an active session without dropping the WebSocket/TCP connection. (AC: 1.5.2)
3. **Key Versioning**: Implement a key versioning system in the `PQCMiddleware` that allows overlapping validity of old and new keys. (AC: 1.5.3)
4. **Interruption-Free**: Existing predictive agent trajectories must continue without interruption during a rotation event (FR18). (AC: 1.5.4)
5. **Rotation Signal**: The Gateway must broadcast a `ROTATION_EVENT` signal to the Telemetry Hub when a key update is triggered. (AC: 1.5.5)

## Tasks / Subtasks

- [x] Update `gateway/pqc_middleware.go` to support a `KeyRegistry` with versioning.
- [x] Implement a rotation trigger (admin endpoint or signal handler) in the Gateway.
- [x] Implement "Algorithm Fallback/Overlap" logic to handle clients using the previous version.
- [x] Update `gateway/main.go` to expose a secure rotation management endpoint.
- [x] Add integration tests verifying that requests pass through during a simulated key rotation.

## Dev Notes

- **Implementation Strategy**: Updated `CryptoRegistry` to generate and manage hybrid key pairs including X25519, ML-KEM-768, and ML-DSA-44.
- **Library**: Used `cloudflare/circl` for FIPS-compliant PQC implementations.
- **Rotation**: Implemented `/gateway/rotate-crypto` endpoint and integrated it with the `TelemetryHub` to broadcast `ROTATION_EVENT` signals.
- **Grace Period**: Maintained a 5-second overlap for old keys to ensure zero-downtime for active sessions.
- **Handshake Negotiation**: Clients can specify `X-PQC-Key-Version` to pin a specific session to a key version during rotation.

### Project Structure Notes

- **Primary Logic**: `gateway/pqc_middleware.go` (UPDATED)
- **Management API**: `gateway/main.go` (UPDATED)
- **Telemetry Integration**: `gateway/telemetry_hub.go` (INTEGRATED)
- **Tests**: `gateway/pqc_test.go` (NEW: `TestPQCMiddleware_Rotation`)

### References

- [Source: docs/architecture/architecture.md#3. Authentication & Security]
- [Source: _bmad-output/planning-artifacts/prd.md#8. Functional Requirements (FR18)]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Fixed ML-DSA `GenerateKey` function name mismatch.
- Verified telemetry broadcast during rotation events.
- Validated grace period expiry in integration tests.

### Completion Notes List

- ✅ Successfully implemented zero-downtime crypto rotation.
- ✅ Hardened gateway with algorithm agility (ML-KEM + ML-DSA).
- ✅ Verified with automated integration tests.

### File List

- `gateway/pqc_middleware.go`
- `gateway/main.go`
- `gateway/pqc_test.go`
- `gateway/telemetry_hub.go`
