---
name: lottery-omni-generator
description: Generate highly optimized lottery tickets using all available p4lottery CLI features, backtesting, Dual-Core 80/20 scoring, and budget-constrained wheels. Use when user wants advanced, esoteric, or fully optimized game predictions.
---
# Lottery Omni Generator (`p4lottery` Workflow Skill)

Use this skill to generate optimized lottery tickets by orchestrating the canonical `./p4lottery` (`lottery`) CLI engine — combining Dual-Core 80/20 statistical/contextual scoring (`dual_core`, `esoteric_statistical`), structural harmony filters, backtesting, and budget-constrained combinatorial wheels (`reduce-coverage` / `reduce-pool`).

> **Strict Rule**: Never create a standalone `cli.py` or separate CLI utility for `lottery-omni-generator`. Always use `./p4lottery` (`engine/cli/main.py`).

## Steps

1. **Clarify scope**: Ask the user which game (e.g., `br/mega-sena`, `br/lotofacil`, `us/powerball`), the target draw date/time, the budget or ticket count, and whether to include esoteric/astronomical context or budget-constrained wheeling (`reduce-coverage` vs `reduce-pool`). Wait for their answer before proceeding.
2. **Reconnaissance & Data Readiness**:
   - Inspect `./p4lottery --help`, `./p4lottery wheel --help`, and `./p4lottery suggest --help`.
   - Ensure historical data is available via `./p4lottery fetch <game>` or `./p4lottery import-drawings <game> <file>`.
3. **Evaluate & Backtest via `p4lottery`**:
   - Run `./p4lottery backtest <game> --strategy dual_core,esoteric_statistical,weighted` or `./p4lottery calibrate <game>` to verify statistical resilience across historical draws.
   - Audit deterministic environmental/astronomical seeds with `./p4lottery seed-audit <game> --date <YYYY-MM-DD> --time <HH:MM>`.
4. **Generate Optimized Tickets or Budget-Bounded Wheels via `p4lottery`**:
   - For budget-constrained combinatorial wheels (80% Statistical + 20% Astronomical Context with `CoverageAudit`):
     ```bash
     ./p4lottery wheel <game> --budget <BRL> --reduction-strategy reduce-coverage --target-date <ISO> --export <path.json>
     ./p4lottery wheel <game> --budget <BRL> --reduction-strategy reduce-pool --target-date <ISO> --export <path.json>
     ```
   - For strategy-driven ticket generation with structural filters and deterministic weather/astronomical seeds:
     ```bash
     ./p4lottery suggest <game> --strategy dual_core --count <N> --target-date <YYYY-MM-DD> --target-time <HH:MM> --weather-seed --filters balanced
     ```
5. **Report**: Provide the user with:
   - The exact `./p4lottery` commands executed.
   - The generated combinations, parity/sum/recurrence breakdown, and combinatorial coverage/financial audit.
   - The mathematical justification connecting the Dual-Core statistical/contextual scores and structural filters to the selected numbers.
