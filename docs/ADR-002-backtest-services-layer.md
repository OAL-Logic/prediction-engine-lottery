# ADR-002: Introduce `engine/services/` for backtest logic

**Status:** Accepted
**Date:** 2026-08-12
**Deciders:** Operator D

## Context

`POST /games/{name}/backtest` returned a canned `{"message": "Backtest completed"}` regardless of what was actually computed. The real per-draw and per-strategy results only ever reached a `console.print()` call inside `engine/cli/commands/backtest.py`, which the API imported and called directly for its side effects — a CLI-only function pressed into service as the API's business logic, with no return value for the API to hand back. ADR-001 flagged this as a dead stub (R1); it wasn't dead, but the underlying "no return value" problem was never fixed, just relocated.

## Decision

Extract the computation into `engine/services/backtest.py::run_backtest()` — framework-agnostic (no Rich, no FastAPI/Pydantic), returning a `BacktestResult` dataclass. The CLI renders it to the terminal; the API serializes it to JSON via a `BacktestResponse` Pydantic model. Both call the same function; neither depends on the other.

This is the first module under `engine/services/`, which didn't exist before. The alternative — adding a second function to `engine/cli/commands/backtest.py` and having the API import it — was rejected because the API already depended on the CLI package for this endpoint, which was backwards layering (a delivery adapter depending on another delivery adapter). `engine/services/` fixes the dependency direction: CLI and API both sit above it, neither imports the other for business logic.

## Consequences

Future extractions of shared CLI/API logic (e.g. if the CLI command boilerplate deepening from the architecture review happens) have an obvious home to land in rather than each re-deciding where shared logic goes.
