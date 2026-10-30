# Single Canonical CLI Policy (`p4lottery` / `lottery`)

`p4lottery` (invoked via `./p4lottery` or the installed entrypoint `p4lottery` / `lottery` backed by `engine/cli/main.py`) is the **single canonical CLI utility** in this repository.

## Architectural Boundaries

| Need | Where It Belongs | Anti-Pattern (Forbidden) |
| :--- | :--- | :--- |
| New CLI command, flag, strategy, wheel mode, or storage feature | `engine/cli/`, `engine/strategies/`, `engine/wheels/`, `engine/modules/` (invoked via `./p4lottery`) | Creating a standalone `cli.py`, custom root bash launcher, or top-level `core/` / `combinatorics/` / `db/` folders |
| Specific non-CLI evaluation, automation, or repo guardrail | `scripts/<name>.py` (or `.scratch/` for temporary scripts) | Adding a competing CLI tool outside `engine/` |
| Multi-step agentic workflow combining analysis, backtesting, and generation | `.agents/skills/<skill-name>/SKILL.md` invoking `./p4lottery` | Writing a skill-specific standalone CLI binary |
