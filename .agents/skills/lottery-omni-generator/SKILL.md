---
name: lottery-omni-generator
description: Generate highly optimized lottery tickets using all available CLI features, backtesting, and translating esoteric variables into deterministic seeds. Use when user wants advanced, esoteric, or fully optimized game predictions.
---
# Lottery Omni Generator

Use this skill to generate optimized lottery tickets by extracting maximum value from the CLI engine, incorporating all available filters, and implementing deterministic seeds from esoteric or environmental variables.

## Steps

1. **Clarify scope**: Ask the user which game (e.g., Lotofácil, Quina), the target contest, the pool size/ticket count, and whether to include esoteric conditions (weather, date, moon phase). Wait for their answer before proceeding.
2. **Reconnaissance**: Read `README.md` and execute the CLI's help command (e.g. `lottery --help`) to discover every available argument, model, and filter.
3. **Refactor for esoteric seeds**: If the user requested esoteric conditions, modify the Python engine to translate these environmental variables into deterministic parameters (e.g., high-entropy PRNG seeds, historical time-series correlations). Expose them via CLI flags.
4. **Backtest**: Execute the CLI to run backtests crossing traditional structural boundaries (parity, sum, primes, frequency z-score) with the new esoteric parameters. Iterate until you find the parameter configuration that maximizes statistical resilience.
5. **Generate**: Run the final CLI command to output the candidate tickets. 
6. **Report**: The task is complete when you provide the user with:
   - Code diffs of the engine refactor (if any).
   - The exact CLI commands executed.
   - The final generated combinations.
   - The mathematical justification connecting the environmental inputs and structural filters to the chosen numbers.
