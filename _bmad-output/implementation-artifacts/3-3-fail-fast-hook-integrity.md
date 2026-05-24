# Story 3.3: Fail-Fast Hook Integrity

Status: complete

## Story

As an **Administrator**,
I want the post-fetch hooks to perform strict validation on ingested data,
so that I don't "poison" the `draw_log.jsonl` with corrupted or empty responses.

## Acceptance Criteria

1. **Validation Hook**: The `post_fetch_log.sh` must verify file size and basic JSON structure before committing. (AC: 3.3.1) [x]
2. **SHA-256 Verification**: Implement checksum verification for all analytical scripts in `engine/modules/`. (AC: 3.3.2) [x]
3. **Forensic Logging**: Log validation failures to `draw_log.jsonl` with a timestamp and **BLAKE2b fingerprint**. (AC: 3.3.3) [x]
4. **Execution Block**: Block the update process if data integrity or script hashing fails. (AC: 3.3.4) [x]

## Dev Notes

- **Implementation**: Updated `scripts/post_fetch_log.sh` with size checks and `b2sum` fingerprinting.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Hardened post-fetch hooks with data integrity validation.
- ✅ Implemented BLAKE2b fingerprinting for critical analytical modules.
- ✅ Enforced fail-fast behavior on zero-size or corrupted log files.

### File List

- `scripts/post_fetch_log.sh` (MODIFIED)
