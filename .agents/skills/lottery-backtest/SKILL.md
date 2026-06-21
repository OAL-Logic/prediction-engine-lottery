---
name: lottery-backtest
description: Runs historical blind tests on strategies and summarizes hit rates/ROI. [Use when user says "run a backtest", "test this strategy", or "historical performance".]
---

# lottery-backtest

## Overview

This workflow wraps the `./lottery backtest` command to execute blind historical tests on any prediction strategy or ensemble. It parses the dense metrics (Hit Rates, ROI, Confidence intervals) and summarizes them for the user in an actionable format, enabling them to evaluate if a strategy is genuinely predictive before putting money on it.

## Conventions

- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

### Stage 1: Parameter Setup
If missing, ask the user:
- The game to backtest (e.g., `br/mega-sena`).
- The strategy or ensemble to test.
- The depth of the backtest (number of historical draws to test against).

### Stage 2: Execution
Run exactly: `{project-root}/lottery backtest {game} --strategy {strategies} --depth {depth}`

### Stage 3: Results Synthesis
Review the output, focusing on:
- ROI (Return on Investment).
- Overall hit rate vs expected random hit rate.
- Whether the Chi² gate validates the strategy as predictive.
Present a clear summary to the user highlighting if the strategy passed or failed the empirical test.
