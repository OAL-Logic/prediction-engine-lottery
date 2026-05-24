# Story 2.5: The K-of-N Harmony Gate Orchestrator

Status: complete

## Story

As a **User**,
I want to define "Fuzzy" structural requirements (e.g., pass 18 of 20 filters),
so that I don't lose winning tickets due to a single outlier property.

## Acceptance Criteria

1. **K-of-N Logic**: The registry must support a `validate_batch` mode where a ticket passes if it satisfies at least $K$ of $N$ active filters. (AC: 2.5.1) [x]
2. **Consensus Scoring**: The system must track and return the total number of filters passed for each candidate ticket. (AC: 2.5.2) [x]

## Dev Notes

- **Vectorized Consensus**: Used `np.sum(axis=1)` on the boolean results matrix for O(1) consensus calculation.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Completion Notes List

- ✅ Implemented `validate_batch` in `VectorRegistry` with K-of-N support.
- ✅ Integrated consensus scoring into the ticket suggestion flow.

### File List

- `engine/modules/filters/__init__.py` (MODIFIED)
