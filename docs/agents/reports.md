# Reports Organization & Naming Reference

Canonical rules for organizing, naming, and maintaining prediction reports and analytical studies in version control.

## 1. Directory Hierarchy

Reports are isolated by country code and game slug, matching the engine's modular jurisdiction architecture (`DrawRules` / `LotteryAdapter`):

```
reports/
└── <country_code>/
    ├── <game_slug>/         # Game-specific draw and strategy reports (e.g. lotofacil, mega-sena, quina)
    ├── studies/             # Cross-game backtests, empirical studies, and benchmark analyses
    └── teimosinha/          # Multi-draw syndicate tickets and recurring combo bets
```

Examples:
- `reports/br/lotofacil/`
- `reports/br/mega-sena/`
- `reports/br/quina/`
- `reports/br/studies/`
- `reports/br/teimosinha/`

## 2. Naming Conventions

Never use redundant game prefixes (e.g. do not name files `lotofacil_resonance_report_3690.md` inside `reports/br/lotofacil/`). Follow these standard taxonomy patterns:

| Report Type | Pattern | Examples |
|---|---|---|
| **Target Draw Analysis** | `draw-<ID>-<type>.md` | `draw-3690-resonance.md`, `draw-3027-cycle.md`, `draw-7117-unfolded-bets.md` |
| **Strategy Preset Portfolio** | `strategy-<name>.md` | `strategy-random-forest.md`, `strategy-steiner-wheel.md`, `strategy-bayesian.md` |
| **Narrative Example** | `story.example.md` | `story.example.md` |
| **Empirical / Research Study** | `<topic-slug>.md` | `expert-strategy-backtest.md`, `blind-baseline-vs-predictive-lift.md` |
| **Multi-Draw Syndicate Runs** | `YYYY-MM-DD_<subtype>.md` | `2026-07-11_teimosinha.md`, `2026-08-11_teimosinha.md` |

## 3. Git Version Control & Ignored Artifacts

1. **Curated Value in Git**: Versioning reports preserves reproducible research, backtest audits, and historical performance tracking.
2. **Ignored Ephemeral Files**: Local drafts and ad-hoc runs are ignored by `.gitignore`:
   - `reports/**/*.local.*`
   - `reports/**/*.tmp.*`
   - `reports/**/.scratch/`
3. **No-PII Policy**: All committed reports must contain zero Personal Identifiable Information. Only approved synthetic mocks (`"JANE DOE"`, `"JOHN DOE"`, `"1990-01-01"`) or redacted tags (`[REDACTED PII]`) are permitted. Enforced via `python3 scripts/check_no_pii.py`.
