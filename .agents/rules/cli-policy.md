# Single Canonical CLI Policy (`p4lottery` / `lottery`)

## Rule Summary

**`./p4lottery` (and its Python package alias `lottery` in `engine/cli/main.py`) is the ONLY CLI utility in this project.**

1. **Zero Parallel CLIs or Shadow Packages**:
   - Never create standalone CLI entrypoints at the repository root (such as `cli.py` or custom bash wrappers like `lottery-omni-generator`).
   - Never create shadow top-level packages (`core/`, `combinatorics/`, `db/`) that duplicate `engine/modules/`, `engine/strategies/`, `engine/wheels/`, or `engine/adapters/`.
2. **Embed CLI Engine Features into `p4lottery`**:
   - New strategies belong in `engine/strategies/` (registered in `STRATEGY_REGISTRY`).
   - New wheel algorithms and budget reduction modes (`reduce-coverage`, `reduce-pool`) belong in `engine/wheels/` and are exposed via `./p4lottery wheel`.
   - New data ingestion formats (`.csv`, `.json`, `.txt`) belong in `engine/modules/storage.py` and are exposed via `./p4lottery import-drawings` or `./p4lottery fetch`.
3. **Isolated Evaluation Scripts (`scripts/`)**:
   - When evaluating or automating a narrow, standalone task that is not part of the `p4lottery` CLI engine (e.g., PII checks, Playwright automation, one-off mathematical verifications), place it under `scripts/` (or `.scratch/` if ephemeral).
4. **Agent Skills Interact with `p4lottery` (`.agents/skills/`)**:
   - High-level workflows (such as `lottery-omni-generator`, `lottery-suggest`, `lottery-wheel`, `lottery-backtest`, `lottery-analyze`, `lottery-scan`) must live as skills under `.agents/skills/<skill-name>/SKILL.md` that orchestrate `./p4lottery` commands rather than spawning separate CLI binaries.
