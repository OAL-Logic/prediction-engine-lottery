# Reports Organization Rule

Follow the canonical directory and naming structure whenever generating, storing, or managing reports:

1. **Path Layout**: Store reports under `reports/<country_code>/<game_slug>/` (or `reports/<country_code>/studies/`, `reports/<country_code>/teimosinha/`). Never dump unorganized reports directly into `reports/`.
2. **File Naming Taxonomy**:
   - Draw reports: `draw-<ID>-<type>.md` (e.g., `draw-3690-resonance.md`)
   - Strategy presets: `strategy-<name>.md` (e.g., `strategy-random-forest.md`)
   - Narrative examples: `story.example.md`
   - Empirical studies: `reports/<country_code>/studies/<topic>.md`
   - Recurring syndicate bets: `YYYY-MM-DD_<subtype>.md`
3. **No Redundant Prefixes**: Do not include `<game_slug>` in filenames when already inside that game's folder.
4. **Zero-PII Compliance**: Never commit reports containing real personal identifiers, non-mock names, or unapproved birth dates. See `docs/agents/reports.md` and `docs/agents/pii-policy.md`.
