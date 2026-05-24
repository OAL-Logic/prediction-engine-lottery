# Story 6.1: Disassembly Indexing & Constant Extraction

Status: complete

## Story

As a **Reverse Engineer**,
I want to extract the exact algorithmic constants and function entry points from the SamLotto disassembly,
so that I can recreate its core logic with 100% parity.

## Acceptance Criteria

1. **Feature Mapping**: Index all 90+ analytical vectors in the 64MB disassembly. (AC: 6.1.1) [x]
2. **Constant Extraction**: Extract the mathematical thresholds and bit-weights for Tier 1-5 filters. (AC: 6.1.2) [x]
3. **Registry Logic**: Map the jump-table entry point (`0x00585f5c`) and its modular discovery pattern. (AC: 6.1.3) [x]

## Dev Notes

- **Findings**: Discovered SSE vectorization and a modular registry pattern in the original binary.
- **Parity**: Successfully mapped 37+ core statistical filters from the manual to their internal offsets.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Completed exhaustive landmark indexing of the 1.5M line disassembly.
- ✅ Synthesized the SamLotto feature map in `docs/research/samlotto-feature-map.md`.
- ✅ Extracted the logic for the 5-Tier Harmony Gate.

### File List

- `docs/research/samlotto-feature-map.md` (NEW)
