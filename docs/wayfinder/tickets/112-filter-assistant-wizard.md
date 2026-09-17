---
id: "112"
type: task
status: closed
blocked_by: []
map: samlotto-qt-interface-map.md
created: 2026-09-16
---

# Filter Assistant Wizard (GUI counterpart to `lottery filter-assistant`)

## Question

`detailed_features.md` §3 names "Assistant Filter: A guided wizard-like interface for setting up filters" as its own distinct SamLotto capability, separate from the base filter list. `lottery filter-assistant` already implements this at the CLI (tier-by-tier guided picker → candidate pool → elimination-funnel report, with an offer to save as a profile), but `FiltersTab` only has the other workflow — the full custom-range-editor tree (#105). No GUI path to the guided/simple one existed.

## Resolution

Added `desktop/src/widgets/filter_assistant_wizard.py`:
- `FilterAssistantWizard(QWizard)` — one page per non-empty tier (all 5 have filters currently: 19/22/20/18/20), each a multi-select list of that tier's `unique_id — display_name` entries (`registry.list_by_tier()`, the exact call `filter_assistant.py`/`filter_funnel.py --list-filters` already use). Final page: candidate-pool entry + a "Run Elimination Funnel" button.
- `FilterAssistantFunnelJob(QThread)` — the actual computation, and deliberately **not** built on `PruningJob`/`FiltersTab`'s machinery: SamLotto's Assistant Filter and the base filter tabs are different workflows (confirmed by the CLI already having two separate commands, `filter-assistant` and `filter-funnel`/`prune`, with different semantics — sequential elimination stages that stop at zero survivors, each filter using its own built-in default threshold, vs. parallel AND/OR/N-of-M with GUI-configured ranges). Reuses `engine.cli.commands.filter_funnel`'s exact logic (same `MAX_COMBINATIONS` safety cap import, same `VectorizedFilter.apply()` chain) rather than reimplementing it — the CLI module's core loop was extracted into this Job practically unchanged.

Launch point: a "🧙 Launch Filter Assistant..." button added to `FiltersTab`'s header (above its existing 3 tabs, not a 4th tab — it's a self-contained flow, not another configuration surface). Self-contained by design, same as the CLI: no cross-tab pool integration, matching `filter_assistant.py`'s own behavior of prompting for the pool itself rather than inheriting one.

**Verified, rigorously**: rather than just confirming the wizard's job runs without raising, `tests/test_desktop_integrity.py::test_filter_assistant_wizard_matches_cli` runs the *same* filter/pool inputs through both the new `FilterAssistantFunnelJob` and the real `lottery filter-funnel` CLI command (via `CliRunner`) and asserts their survivor counts agree — confirming the GUI reuses the exact same logic, not just similar-looking logic. `test_filter_assistant_launch_button_wired` confirms clicking the actual button constructs and shows the actual wizard class (not just that a correctly-labeled button exists). Full `test_desktop_integrity.py`/`test_desktop_logic.py` (30 tests) pass.

## Not done here

- **Save as profile** — the CLI wizard ends with an optional "save this filter set as a named profile" step (`engine.cli.commands.profile`). The desktop app has no profile concept in its UI at all yet (profiles are CLI-only); adding one is a separate, larger feature, not bundled into this ticket.
