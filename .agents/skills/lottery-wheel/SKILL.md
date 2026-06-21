---
name: lottery-wheel
description: Generates combinatorial covering designs. [Use when user says "generate wheel" or "create a covering design".]
---

# lottery-wheel

## Overview

This utility skill generates combinatorial covering designs for lottery tickets. A wheeling system allows a player to choose a larger pool of numbers and generate a set of tickets that mathematically guarantees a specific prize tier if the drawn numbers fall within the selected pool.

## Conventions

- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

### Inputs
Ensure you have the following from the user before executing:
1. `game` - The lottery game (e.g., `br/mega-sena`).
2. Parameters for the wheel (e.g. pool size, pick size, guarantee tier, match condition) or specific `--help` to see exact arguments.

### Execution
Run exactly: `{project-root}/lottery wheel {args}` based on the user's requirements.
Present the generated tickets or output to the user clearly.
