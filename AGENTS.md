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
