# Privacy & No-PII Policy

How agents and contributors must handle Personal Identifiable Information (PII) across the Lottery Prediction Engine repository.

## 1. Scope of Prohibited PII

Because this project includes numerological, kabbalistic, biorhythm, and esoteric strategies that accept personal parameters (`birth_date`, `full_name`, geographic coordinates), agents must **never** persist real user PII into any tracked or exported file.

Prohibited PII includes:
- **Real Birth Dates**: Any real person's date of birth (e.g., `YYYY-MM-DD` or `YYYYMMDD` integer seeds derived from it) supplied during a prompt or interactive session.
- **Personal Names**: Real first, middle, or full names supplied for Kabbalistic/Gematria strategies.
- **Identifiers & Credentials**: CPF, RG, SSN, email addresses, phone numbers, API keys, or account numbers.
- **Exact Personal Locations**: Home addresses or residential GPS coordinates (use official lottery draw city coordinates such as Caixa Espaço da Sorte in São Paulo `-23.5505, -46.6333` when testing `--weather-seed`).

## 2. Canonical Synthetic Defaults

In source code (`engine/`, `desktop/`, `cockpit/`, `tui/`), docstrings, CLI option defaults, and test suites (`tests/`):
- **Default `birth_date`**: Always use `"1990-01-01"` / `date(1990, 1, 1)` (or `None` resolving via `load_local_config()` to `"1990-01-01"`).
- **Default `full_name`**: Always use `"JOHN DOE"` or `"TREVO DA SORTE"`.
- **Unit Test Fixtures**: Use explicitly named synthetic constants (e.g., `SYNTHETIC_DEFAULT_DATE = "1990-01-01"` or `SYNTHETIC_BIRTH_DATE_LUCKY_7 = "2000-04-16"`).

## 3. Where Users Store Personal Config Locally

Users may store their own parameters locally in git-ignored files:
- `personal.local.yaml` or `*.local.yaml` (loaded automatically by `engine.cli.utils.load_local_config()`)
- `lottery_personal.toml`

These files are excluded via `.gitignore` (`*.local*`, `lottery_personal.toml`, `.scratch/`) and must **never** be staged or force-added to Git.

## 4. Redaction in Exported Markdown / Scratch Artifacts

When a CLI command or agent exports a report to disk (`--export-md`, `.scratch/`, `reports/`):
- **Never write the raw `birth_date` or `full_name` string to disk.**
- Replace the raw PII field with `[REDACTED PII]` and record only the non-reversible reduced numerological attributes (e.g., `Número da Sorte: 7`, `Caminho de Vida: 5`, `Dia Sagrado: Sábado`).
