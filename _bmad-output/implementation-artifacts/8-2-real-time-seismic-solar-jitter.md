# Story 8.2: Real-time Seismic & Solar Jitter

Status: done

## Story

As a **Chaos Researcher**,
I want the engine to modulate sampling temperature based on real-time environmental noise,
so that my predictions resonate with the physical world.

## Acceptance Criteria

1. **Environmental Data Fetching**: The system must be able to fetch real-time solar (Kp-Index) and seismic magnitude data from official OSINT sources (e.g., NOAA, USGS). (AC: 8.2.1) [x]
2. **Temperature Modulation Logic**: Implement a "Chaos Jitter" formula that boosts sampling temperature $T$ proportionally to environmental intensity. (AC: 8.2.2) [x]
3. **Chaos Mode Integration**: The jitter must be automatically applied when the `--chaos` flag is used in `lottery suggest`. (AC: 8.2.3) [x]
4. **Metadata Transparency**: The active jitter factors (e.g., `+0.15 solar jitter`) must be displayed in the OSINT Evidence Panel. (AC: 8.2.4) [x]
5. **Caching**: Environmental data must be cached for 1 hour to prevent excessive API calls. (AC: 8.2.5) [x]

## Tasks / Subtasks

- [x] Implement `EnvironmentalService` in `engine/modules/environment.py`. (AC: 8.2.1, 8.2.5)
  - [x] Add NOAA Kp-Index fetcher.
  - [x] Add USGS Seismic event fetcher.
- [x] Implement `calculate_environmental_jitter` logic. (AC: 8.2.2)
  - [x] Define jitter weights for solar storms and seismic tremors.
- [x] Update `BaseStrategy.suggest` to incorporate environmental jitter when in Chaos Mode. (AC: 8.2.3)
- [x] Update the TUI and CLI OSINT panels to display active environmental factors. (AC: 8.2.4)
- [x] Add a unit test to verify jitter calculation based on mock environment data. (AC: 8.2.2)

## Dev Notes

- **Formulas**: 
  - $J_{solar} = \max(0, (Kp - 4) \times 0.05)$
  - $J_{seismic} = \max(0, (Mag - 5) \times 0.1)$
  - $T_{chaos} = T_{base} + J_{solar} + J_{seismic}$
- **Sources**: 
  - Solar: NOAA Swpc API.
  - Seismic: USGS Earthquake Feed.
- **Caching**: Implemented in `data/cache/env_jitter.json`.

### Project Structure Notes

- **Module**: `engine/modules/environment.py`
- **Integration**: `engine/strategies/__init__.py` (BaseStrategy)

### References

- [Source: docs/architecture/technical-spec.md#The Chaos Temperature Governor]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 8: Hyper-Explorer & Advanced OSINT]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Verified real-time OSINT fetching from NOAA and USGS.
- Validated temperature modulation logic in `tests/test_environment.py`.

### Completion Notes List

- ✅ Implemented real-time environmental jitter service.
- ✅ Integrated with core suggestion sampling via `--chaos` flag.
- ✅ Added OSINT panel transparency for active jitter factors.

### File List

- `engine/modules/environment.py` (NEW)
- `engine/strategies/__init__.py` (MODIFIED)
- `engine/cli/commands/suggest.py` (MODIFIED)
- `engine/cli/main.py` (MODIFIED)
- `tests/test_environment.py` (NEW)
