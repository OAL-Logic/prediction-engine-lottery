---
name: lottery-suggest
description: Generates tickets using prediction strategies and ensembles. [Use when user says "suggest numbers", "generate tickets", or "predict the next draw".]
---

# lottery-suggest

## Overview

This workflow wraps the `./lottery suggest` command. It allows the agent to generate predicted ticket sets using single strategies (e.g., `weighted`), manual ensembles (e.g., `weighted,markov`), or named meta-ensembles (e.g., `stacking`). It will present the generated tickets and rationale to the user.

## Conventions

- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

### Stage 1: Parameter Elicitation
If not already provided, ask the user:
- Which game to predict (e.g., `br/lotofacil`).
- Which strategy or strategies to use. Note that comma-separated lists trigger automatic voting ensembles, and named ensembles like `stacking` are also available.
- How many tickets to generate (`--count`).

### Stage 2: Execution
Run exactly: `{project-root}/lottery suggest {game} --strategy {strategies} --count {ticket_count}`

### Stage 3: Presentation
Present the generated tickets clearly to the user. If the output provides rationale or confidence scores for the strategies used, summarize them so the user understands why these numbers were chosen.
