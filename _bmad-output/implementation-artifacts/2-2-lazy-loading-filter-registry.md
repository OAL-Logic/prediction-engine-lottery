# Story 2.2: Lazy Loading Filter Registry

Status: complete

## Story

As a **Senior Dev**,
I want a dynamic discovery system for the 5 filter tiers,
so that only requested filters are imported into the process, preserving the 500ms startup time.

## Acceptance Criteria

1. **On-Demand Instantiation**: Filters must NOT be imported at the module level. They must be loaded only when explicitly requested by ID. (AC: 2.2.1) [x]
2. **Dynamic Discovery**: The registry must use `importlib.util` to scan and load filter modules from the `engine/modules/filters/` directory. (AC: 2.2.2) [x]
3. **Registry Resolution Speed**: Resolving a requested filter by ID must take less than 50ms. (AC: 2.2.3) [x]
4. **__getattr__ Pattern**: The filter tiers should be accessible via a lazy-loading pattern in the main `filters` module. (AC: 2.2.4) [x]

## Tasks / Subtasks

- [x] Refactor `VectorRegistry` in `engine/modules/filters.py` to support lazy loading. (AC: 2.2.1, 2.2.3)
- [x] Implement `discover_filters()` using `importlib.util` to map IDs to module paths. (AC: 2.2.2)
- [x] Move Tier 1-5 implementations into individual files under `engine/modules/filters/`. (AC: 2.2.4)
- [x] Add a unit test to verify that importing `engine.modules.filters` does not eagerly import heavy analytical libraries (like `pandas`). (AC: 2.2.1)

## Dev Notes

- **Package Refactor**: Moved logic to `engine/modules/filters/__init__.py` to avoid directory/module naming conflicts.
- **Dynamic Mapping**: The registry automatically scans `tier*.py` files and builds a module map for 100+ filters.
- **Speed**: Resolution time verified at **< 10ms** on local environment.

### Project Structure Notes

- **Directory**: `engine/modules/filters/`
- **Module**: `engine/modules/filters/__init__.py`

### References

- [Source: _bmad-output/planning-artifacts/prd.md#System Invariants]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2: Lazy Loading Filter Registry]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Verified `sys.modules` isolation in `tests/test_lazy_filters.py`.

### Completion Notes List

- ✅ Refactored filters into a modular package structure.
- ✅ Implemented lazy loading for all 5 tiers of analytical vectors.
- ✅ Verified sub-50ms resolution and on-demand module importing.

### File List

- `engine/modules/filters/__init__.py` (NEW/REFACTORED)
- `engine/modules/filters/tier1_structural.py` (NEW)
- `engine/modules/filters/tier2_positional.py` (NEW)
- `engine/modules/filters/tier3_algebraic.py` (NEW)
- `engine/modules/filters/tier4_historical.py` (NEW)
- `engine/modules/filters/tier5_custom.py` (NEW)
- `tests/test_lazy_filters.py` (NEW)
