# Story 8.3: Atmospheric Muon Flux Simulator

Status: done

## Story

As a **Nerd Mode User**,
I want simulated bit-flips in my ticket generation process,
so that I can account for cosmic noise and prevent 100% deterministic traps.

## Acceptance Criteria

1. **Muon Flux Logic**: Implement a "Muon Strike" simulation that has a ~0.5% chance per ticket of causing a single-number mutation. (AC: 8.3.1) [x]
2. **Cosmic Resonance**: The mutation probability should be boosted if real-time solar activity is high (Kp-Index > 5). (AC: 8.3.2) [x]
3. **Forensic Logging**: Any muon strike must be logged in the suggestion metadata with a "COSMIC_RAY_DETECTED" tag. (AC: 8.3.3) [x]
4. **Collision Avoidance**: The mutation logic must ensure the new number is within game boundaries and does not collide with existing numbers in the ticket. (AC: 8.3.4) [x]
5. **Nerd Mode Toggle**: The simulator must be active by default but can be silenced via a configuration setting. (AC: 8.3.5) [x]

## Tasks / Subtasks

- [x] Implement `simulate_muon_strike` in `engine/modules/cosmic.py`. (AC: 8.3.1, 8.3.4)
- [x] Integrate real-time Kp-Index from `EnvironmentalService` to modulate mutation probability. (AC: 8.3.2)
- [x] Update `BaseStrategy.suggest` to replace its placeholder muon logic with the new module. (AC: 8.3.3)
- [x] Add unit tests for muon mutation boundary safety. (AC: 8.3.4)

## Dev Notes

- **Mutation Algorithm**:
  1. Pick a random number in the ticket.
  2. XOR it with a random 1-bit mask (1, 2, 4, 8, 16, 32).
  3. Validate against `rules.number_range` and existing set.
- **Probability**: Base $P = 0.005$. If $Kp > 5$, $P = 0.005 + (Kp - 5) \times 0.002$.
- **Solar Resonance**: Uses `EnvironmentalService` for real-time coupling.

### Project Structure Notes

- **Module**: `engine/modules/cosmic.py`
- **Strategy Integration**: `engine/strategies/__init__.py`

### References

- [Source: docs/research/CRAZY_LOTTERY_THEORIES.md#Atmospheric Muon Flux]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 8.3: Atmospheric Muon Flux Simulator]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- Validated mutation boundary and collision safety in `tests/test_cosmic.py`.
- Verified Kp-Index coupling for probability modulation.

### Completion Notes List

- ✅ Implemented Atmospheric Muon Flux simulator.
- ✅ Integrated with real-time solar activity resonance.
- ✅ Hardened mutation logic with strict collision avoidance.

### File List

- `engine/modules/cosmic.py` (NEW)
- `engine/strategies/__init__.py` (MODIFIED)
- `tests/test_cosmic.py` (NEW)
