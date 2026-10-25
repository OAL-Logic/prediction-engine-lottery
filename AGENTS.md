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
