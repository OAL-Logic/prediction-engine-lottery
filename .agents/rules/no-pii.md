# No-PII Rule (Zero Personal Identifiable Information)

You MUST NOT include, hardcode, or persist Personal Identifiable Information (PII) anywhere in the repository:

1. **Source Code & CLI Defaults**: Never set a user's real `birth_date`, `full_name`, or personal seed as a default argument, fallback constant, or docstring example in `engine/`, `desktop/`, `cockpit/`, or `tui/`. Always use `None` (resolved via `load_local_config()`) or the synthetic placeholder `"1990-01-01"` / `"JOHN DOE"`.
2. **Tests**: Never use a user's real birth date or name from conversation prompts inside `tests/`. Use synthetic constants such as `1990-01-01` or `2000-04-16`.
3. **Exported Reports & `.scratch/`**: Always redact raw birth dates and full names as `[REDACTED PII]` when writing markdown or JSON reports to disk. Only log non-identifying derived mathematical reductions (e.g., Lucky Number `1-9`, Life Path `1-9`).
4. **Local Configs**: Keep user-specific config inside git-ignored `*.local.yaml` or `lottery_personal.toml`. See `docs/agents/pii-policy.md`.
