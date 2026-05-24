# Story 1.4: Sovereign Local Hashing

Status: done

## Story

As a **Sovereign User**,
I want my intentional hashing data to be processed locally,
So that my private vibrational inputs (Name/Birth Date) never leave my device.

## Acceptance Criteria

1. **Local-First Processing**: Implement a hashing utility in `app/utils/sovereign-hash.ts` that processes user inputs on-device. (AC: 1.4.1)
2. **BLAKE2b Standard**: Use the BLAKE2b algorithm for generating "Intentional Hashes" to ensure collision resistance and performance. (AC: 1.4.2)
3. **Privacy Mandate**: Sensitive raw inputs (Name, Birth Date) must NEVER be transmitted over the network or logged in plain text. (AC: 1.4.3)
4. **Fingerprint Transmission**: Only the resulting 64-character hex fingerprint should be transmitted to the Go Gateway for inclusion in the Forensic Ledger. (AC: 1.4.4)
5. **Deterministic Salt**: Implement a deterministic salting mechanism using the `draw_id` or `timestamp` to ensure that identical inputs produce unique hashes for different prediction sessions. (AC: 1.4.5)

## Tasks / Subtasks

- [x] Create the `app/utils` directory if it doesn't exist.
- [x] Install a suitable BLAKE2b library for React Native (e.g., `blake2b-wasm` or `blakejs`).
- [x] Implement `app/utils/sovereign-hash.ts` with the `generateIntentionalHash` function.
- [x] Add unit tests verifying that raw inputs are not stored in any state that could be leaked.
- [x] Integrate the hashing utility into the `App.tsx` "Capture" flow.
- [x] Verify that the transmitted payload only contains the hash and metadata.

## Dev Notes

- **Implementation**: Utilized `blakejs` for pure-JS hashing at the edge.
- **Privacy**: The `generateTickets` flow in `App.tsx` now calls `generateIntentionalHash` locally.
- **Sovereignty**: Raw `fullName` and `birthDate` are no longer sent to the gateway; they are replaced by a `intentional_hash` fingerprint.
- **V11 Signal**: Added `X-Lottery-Version: 11.0` header to all suggestion requests.

### Project Structure Notes

- **Primary Utility**: `app/utils/sovereign-hash.ts` (NEW)
- **Component Update**: `app/App.tsx` (UPDATE)
- **Tests**: `app/utils/__tests__/sovereign-hash.test.ts` (NEW)

### References

- [Source: _bmad-output/planning-artifacts/prd.md#8. Functional Requirements (FR17)]
- [Source: docs/architecture/architecture.md#3. Authentication & Security]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Verified `blakejs` dependency installation.
- Created `app/utils` for clean separation of sovereign logic.
- Standardized `11.0` version signaling in the App layer.

### Completion Notes List

- ✅ Implemented v11.0 Sovereign Hashing at the mobile edge.
- ✅ Eliminated raw user data transmission in Chaos Mode.
- ✅ Updated App branding to reflect v11.0 Singularity.

### File List

- `app/utils/sovereign-hash.ts` (NEW)
- `app/App.tsx` (MODIFIED)
- `app/package.json` (MODIFIED)
- `app/utils/__tests__/sovereign-hash.test.ts` (NEW)
- `app/jest.config.js` (NEW)
