## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature-slug>/`, matching the existing convention. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Privacy & No-PII Policy (Zero Personal Identifiable Information)

**STRICT RULE — NEVER PERSIST OR COMMIT PII IN REPOSITORY FILES**:
1. **No Real PII in Tracked Files**: Never write, persist, or commit real user Personal Identifiable Information (PII) — including real birth dates (`YYYY-MM-DD`), full names, government IDs (CPF/SSN), personal addresses, exact home GPS coordinates, emails, phone numbers, or personal bankroll/account identifiers — in source code (`engine/`, `desktop/`, `cockpit/`, `tui/`), unit tests (`tests/`), YAML configs (`*.yaml`), documentation (`docs/`), or committed reports (`reports/`).
2. **Use Generic Mock Examples Only**: Whenever an example config (`personal.example.yaml`, `*_backtest.yaml`), fallback default, docstring example, report example, or unit test fixture requires personal numerology/esoteric inputs, always use approved generic mocks:
   - Generic mock names: `"JANE DOE"`, `"JOHN DOE"`, `"TEST USER"`, `"GEMINI ENGINE"`, `"TREVO DA SORTE"`
   - Generic mock birth dates: `"1990-01-01"` (canonical default) or synthetic test fixtures (`"2000-04-16"`, `"1990-05-01"`, `"1985-05-15"`)
3. **Runtime & Local-Only PII Input**: Real user parameters must only be passed at runtime via CLI flags (`--birth-date`, `--full-name`) or stored in git-ignored local files (`personal.local.yaml`, `*.local.yaml`, `lottery_personal.toml`).
4. **Redact PII in Exported Reports & Automated Guardrail**: Any file written to disk via `--export-md`, `.scratch/`, or `reports/` must redact raw PII (`[REDACTED PII]`). The repository enforces this via `python3 scripts/check_no_pii.py` (wired into `.git/hooks/pre-commit` and `pytest`). See `docs/agents/pii-policy.md`, `.agents/rules/no-pii.md`, and `personal.example.yaml`.

### Global Game Compatibility & Jurisdiction Isolation

**STRICT RULE — UNIVERSAL LOTTERY COMPATIBILITY & JURISDICTION ISOLATION**:
1. **Universal Core Architecture (Zero Hardcoded Assumptions)**: Every feature (filters, generators, analyzers, wheel algorithms, UI dashboards, export tools, CLI commands, strategies) must be game-agnostic and operate against abstract contracts (`DrawRules`, `GameDefinition`, `LotteryAdapter`). Never hardcode game-specific numbers or assumptions into core engine pipelines (e.g., assuming pool size $N=60$, pick count $k=6$, 1-based indexing, single-draw events, fixed ticket costs, or absence of bonus balls).
2. **Modular Jurisdiction & Game Structuring**: Isolate jurisdiction-specific rules, APIs, and syndicate mechanics under `engine/adapters/<country_code>/` (e.g., `engine/adapters/br/` for Caixa Loterias, `engine/adapters/us/`, `engine/adapters/eu/`). Shared national rules belong in `<jurisdiction>_base.py` (e.g., `caixa_base.py`), while game-specific rules live in `<game_slug>.py`.
3. **Pluggable Feature Overrides (Hook Pattern)**: When a specific game requires unique handling or workarounds for a feature (e.g. Lotomania's 00-99 mirroring, Lotofácil's high-density clustering, Dupla Sena's dual draws, Dia de Sorte's Month of Luck, or Powerball's bonus pool), features must provide pluggable hook/parameter overrides with analytical fallbacks rather than scattered inline conditionals.
4. **Multi-Archetype Support & Verification Bar**: Features must accommodate global lottery archetypes (sparse single-pool, high-density single-pool, multi-pool/bonus ball, zero-indexed, multi-draw, categorical attributes, multiple bets). Every new or modified feature must be validated across at least 3 distinct game archetypes (e.g., Mega-Sena 6/60, Lotofácil 15/25, and Powerball 5/69+1/26). See `docs/agents/game-compatibility.md`, `.agents/rules/game-compatibility.md`, and `docs/adr/0004-global-lottery-game-compatibility-and-feature-isolation.md`.

### Reports Organization & Naming Rules

**STRICT RULE — JURISDICTION HIERARCHY & TAXONOMY**:
1. **Directory Structure**: Reports must be structured by jurisdiction and game under `reports/<country_code>/<game_slug>/` (or `reports/<country_code>/studies/`, `reports/<country_code>/teimosinha/`). Never write loose, unorganized reports directly to `reports/`.
2. **Standard File Taxonomy**:
   - Target draw reports: `draw-<ID>-<type>.md` (e.g. `draw-3690-resonance.md`, `draw-3027-cycle.md`, `draw-7117-unfolded-bets.md`)
   - Strategy presets: `strategy-<name>.md` (e.g. `strategy-random-forest.md`, `strategy-bayesian.md`)
   - Narrative examples: `story.example.md`
   - Empirical studies: `reports/<country_code>/studies/<topic>.md`
   - Recurring syndicate runs: `YYYY-MM-DD_<subtype>.md`
3. **Zero Redundant Prefixes**: Never prefix files with `<game_slug>_` when already residing within `<game_slug>/`.
4. **Git Maintenance & PII Bar**: Curated markdown reports are tracked in version control. Ephemeral local drafts (`*.local.*`, `*.tmp.*`, `.scratch/`) are git-ignored. All committed reports must strictly comply with the No-PII policy (`python3 scripts/check_no_pii.py`). See `docs/agents/reports.md` and `.agents/rules/reports.md`.

### Single Canonical CLI Policy (`p4lottery` / `lottery`)

**STRICT RULE — `p4lottery` IS THE ONLY CLI UTILITY IN THIS PROJECT**:
1. **No Standalone or Parallel CLIs**: Never create separate CLI utilities, standalone root-level entrypoints (e.g., `cli.py`, `lottery-omni-generator`), or shadow top-level packages (`core/`, `combinatorics/`, `db/`) outside `engine/`. `./p4lottery` (and its Python package entrypoint alias `lottery` in `engine/cli/main.py`) is the single canonical CLI utility for the entire repository.
2. **Embed Engine Features into `p4lottery`**: Any new prediction strategy, statistical/contextual scorer, combinatorial wheel algorithm, budget reduction mode, or data ingestion capability that belongs to the engine must be integrated directly into `engine/` (`engine/cli/`, `engine/modules/`, `engine/strategies/`, `engine/wheels/`) and exposed through `./p4lottery` (`lottery`).
3. **Targeted Scripts vs. CLI Engine**: If you need to evaluate or automate something very specific that is not part of the core CLI engine (e.g., repository guardrails, browser dispatchers, one-off benchmarks), create an isolated script under `scripts/` (or `.scratch/` for ephemeral experiments) rather than creating a competing CLI.
4. **Skills Orchestrate `p4lottery`**: Agent workflows and multi-step pipelines (such as `.agents/skills/lottery-omni-generator/SKILL.md`, `lottery-suggest`, `lottery-wheel`, `lottery-backtest`, `lottery-analyze`, `lottery-scan`) must be implemented as Agent Skills under `.agents/skills/` that invoke and interact with `./p4lottery` (`lottery`). See `docs/agents/cli-policy.md` and `.agents/rules/cli-policy.md`.

### Browser Dispatch & Playwright Automation Policy

**STRICT RULE — ASSISTED BROWSER DISPATCH FOR CAIXA LOTERIAS**:
1. **Canonical Caixa Browser Dispatcher**: When requested to automate, dispatch, or inject generated bets via browser/Playwright for Caixa Loterias games (`br/*` in registry, e.g. `br/mega-sena`, `br/lotofacil`, `br/quina`, etc.), use the dedicated assisted script `scripts/playwright_caixa_universal.py` (e.g., passing `--file <path_to_bets.json>` or dynamic presets).
2. **Human-in-the-Loop Architecture (Assisted, Never Autonomous)**: The script runs interactively with a visible browser (`headless=False`) and persistent session (`.browser_session/`). It pauses for the user to authenticate (CPF/password) and confirm payment. It does NOT bypass credentials, solve CAPTCHAs, or execute financial transactions autonomously; it merely automates mechanical number-filling on the bet slip.
3. **Jurisdiction Scoping**: `scripts/playwright_caixa_universal.py` is specifically built for Caixa Econômica Federal (Brazil). Do not attempt to use it for non-Brazilian jurisdictions (`us/*`, `eu/*`); other lotteries must rely on manual mark sheets or jurisdiction-specific dispatchers if available. See `docs/agents/browser-dispatch.md` and `.agents/rules/browser-dispatch.md`.



