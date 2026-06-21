---
name: lottery-scan
description: Executes the 6-layer diagnostic scan to get a quick GO/NO-GO verdict. [Use when user says "scan the game" or "run a diagnostic scan".]
---

# lottery-scan

## Overview

This simple utility wraps the `./lottery scan` command. It runs a 6-layer diagnostic check on a specified lottery game and returns a GO/NO-GO verdict based on current statistical conditions.

## Conventions

- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

### Inputs
Ensure you know which game to scan (e.g., `br/mega-sena`).

### Execution
Run exactly: `{project-root}/lottery scan {game}`
Present the output, explicitly highlighting the final GO or NO-GO verdict.
