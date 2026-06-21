---
name: lottery-analyze
description: Runs the statistical dashboard and interprets metrics into a markdown report. [Use when user says "run analysis" or "analyze the lottery data".]
---

# lottery-analyze

## Overview

This workflow executes the comprehensive statistical dashboard (`./lottery analyze`) for a given game and interprets its 14+ chart types and statistical metrics into an easy-to-read markdown report. 

## Conventions

- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

### Stage 1: Data Gathering
1. Ensure the user has specified the game (e.g., `br/mega-sena`).
2. Run exactly: `{project-root}/lottery analyze {game} --text-only` (or pipe output to a file if visual dashboard is not supported in terminal). If the CLI outputs ANSI colors, ensure you account for it or strip it. Note: If the `analyze` command requires specific flags to be non-interactive, use them. Since you are reading the output, pipe the command output to a scratch file and read it using your tools if it is very long.

### Stage 2: Synthesis and Reporting
Produce a markdown report covering:
- Overall statistical summary (frequent numbers, cold numbers, overdue numbers).
- Key insights from the variance report, entropy scans, and momentum indicators.
- Any notable anomalies or regime shifts detected in the analysis.

Present this report directly to the user.
