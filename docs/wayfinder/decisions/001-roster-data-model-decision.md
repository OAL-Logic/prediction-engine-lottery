# MDR-001: Roster Data Model Design

* **Status**: Accepted (Research Complete)
* **Date**: 2026-08-11
* **Author**: Antigravity (AI Assistant)
* **Decides**: Persistent representation, file path, JSON schema, and command integration for the per-game strategy roster.

---

## 1. Context & Constraints

The Lottery Prediction Engine currently has over 80 strategies spanning statistical, machine learning, deep learning, and esoteric categories. Run times and predictive power vary significantly. Currently:
- The active strategies used in ensembles (e.g., `lottery forecast`) are dictated by hardcoded presets (`default`, `fast`, `statistical`, etc.) or manually supplied lists.
- There is no mechanism to dynamically exclude poorly performing strategies on a per-game basis based on empirical out-of-sample evidence.
- "Retirement" of a strategy must mean **runtime exclusion only**: strategies must remain available on disk and selectable when explicitly named by the user (no hard deletions).

We need a design for a persistent roster system that allows a command (e.g. `lottery select-strategies` or similar) to save a filtered set of active strategies per game, which ensemble commands then consume.

---

## 2. Storage Location Comparison

We evaluated four options for where to store the roster:

| Option | Path | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Option A (Recommended)** | `data/strategy_roster.json` | Centralized, highly inspectable, matches existing `calibration_cache.json` and `watchlist.json` patterns, simple text-diff in Git. | Concurrent writes across games could theoretically conflict (minimal risk in CLI context). |
| **Option B** | `data/inspections/<game>/roster.json` | Isolated per game, no write conflicts. | Fragmented; harder to audit globally or commit/track collectively. |
| **Option C** | `data/lottery.db` (DuckDB) | Relational structure, transaction safety. | Not easily human-readable or diffable in Git; adds DB schema overhead for a simple key-value structure. |
| **Option D** | `data/strategy_rosters.yaml` | Human-readable, supports comments. | Adds parse-overhead via PyYAML; less standard than JSON in core data folder. |

**Decision**: Store all rosters in a single centralized JSON file: **`data/strategy_roster.json`**.

---

## 3. Schema Design

The file maps a game ID (e.g., `br/lotofacil`) to its roster details. It includes the active strategy list, last update timestamp, the policy ID that generated it, detailed records of excluded strategies (with reasons and metrics for auditability), and future-proof placeholders for regime-switching overrides.

### JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StrategyRosterMap",
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "required": ["game_id", "updated_at", "active_strategies", "exclusions"],
    "properties": {
      "game_id": { "type": "string" },
      "updated_at": { "type": "string", "format": "date-time" },
      "policy_id": { "type": "string" },
      "active_strategies": {
        "type": "array",
        "items": { "type": "string" }
      },
      "exclusions": {
        "type": "object",
        "additionalProperties": {
          "type": "object",
          "required": ["reason", "metrics"],
          "properties": {
            "reason": { "type": "string" },
            "metrics": {
              "type": "object",
              "additionalProperties": { "type": "number" }
            }
          }
        }
      },
      "regime_overrides": {
        "type": "object",
        "description": "Future-proof hook for regime-aware sub-rosters (e.g. STABLE, DRIFT, SHIFT)",
        "additionalProperties": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

### JSON Instance Example
```json
{
  "br/lotofacil": {
    "game_id": "br/lotofacil",
    "updated_at": "2026-08-11T22:08:33Z",
    "policy_id": "calibration-lift-threshold-v1",
    "active_strategies": [
      "weighted",
      "markov",
      "bayesian",
      "monte_carlo"
    ],
    "exclusions": {
      "esoteric": {
        "reason": "Calibration lift (0.85) fell below minimum threshold (1.00)",
        "metrics": {
          "lift": 0.85,
          "roi": -12.4
        }
      },
      "moon_phase": {
        "reason": "Exceeded maximum runtime latency threshold of 5.0s",
        "metrics": {
          "latency_seconds": 6.2
        }
      }
    },
    "regime_overrides": {
      "STABLE": ["weighted", "markov", "bayesian", "monte_carlo"],
      "DRIFT": ["bayesian", "monte_carlo", "momentum"]
    }
  }
}
```

---

## 4. CLI & Command Integration

To query and apply this roster cleanly, we will introduce a new preset value `roster` to the `--strategies` CLI option.

### Command Invocation
- Ensembles and rankings are run with the roster by specifying `roster` as the strategy group:
  ```bash
  lottery forecast br/lotofacil --strategies roster
  lottery rank-numbers br/lotofacil --strategies roster
  ```

### Fallback Policy
If `--strategies roster` is specified, the engine attempts to load `data/strategy_roster.json`.
1. **Missing File or Missing Game Entry**:
   - The engine logs a warning to stderr:
     `[yellow]Warning: No strategy roster found for br/lotofacil. Falling back to 'default' group.[/yellow]`
   - It proceeds using the standard `"default"` strategy preset list.
2. **Empty `active_strategies` list**:
   - Logs a warning and falls back to the `"default"` preset list.

### Compatibility & Overrides
- **User Override**: If a user runs `lottery forecast br/lotofacil --strategies markov,bayesian,esoteric`, it ignores the roster file and forces those specific strategies. This honors the requirement that retired strategies remain executable when explicitly requested.
- **Other presets**: Using `--strategies statistical` or `--strategies fast` continues to load those hardcoded lists directly, bypassing the roster.

### Strategy Load Failure Handling
If a roster contains a strategy that fails to load (e.g. `transformer` is rostered, but the current environment lacks PyTorch):
1. Log a warning:
   `[yellow]Warning: Rostered strategy 'transformer' failed to load. Skipping...[/yellow]`
2. Continue running the forecast/ranking with the remaining successfully loaded strategies.
3. If **all** strategies in the roster fail to load, abort execution with exit code `1` and print:
   `[red]Error: No valid strategies could be loaded from the roster.[/red]`

---

## 5. Unified Seam Implementation

We will implement a unified helper function in `engine/cli/utils.py` to resolve strategy lists across all commands:

```python
def resolve_strategies(strategies_arg: str, lottery_id: str) -> list[str]:
    """
    Resolves the --strategies CLI argument into a list of strategy names.
    Supports preset groups (default, fast, statistical, esoteric), comma-separated
    lists of individual strategies, and the 'roster' option.
    """
    # 1. Handle 'roster' resolution
    if strategies_arg.strip().lower() == "roster":
        roster_path = DATA_DIR / "strategy_roster.json"
        if roster_path.exists():
            try:
                roster_data = json.loads(roster_path.read_text())
                game_roster = roster_data.get(lottery_id)
                if game_roster and game_roster.get("active_strategies"):
                    return game_roster["active_strategies"]
            except Exception as e:
                rprint(f"[yellow]Warning: Failed to read roster file: {e}[/yellow]")
        
        # Fallback if file missing or parse failed
        rprint(f"[yellow]Warning: No active roster found for {lottery_id}. Falling back to 'default' preset.[/yellow]")
        strategies_arg = "default"

    # 2. Handle group/preset maps
    # (Extract the _STRATEGY_GROUPS lookup logic from forecast.py / rank_numbers.py)
    ...
```

This ensures `forecast`, `rank-numbers`, and any future tools resolve strategies in a single, identical manner.

---

## 6. Migration & Rollback Story

### Rollback (Abandoning the Roster)
- To cease using the roster, a user simply stops passing `--strategies roster` to CLI commands. Commands will default to the standard `"default"` preset.
- The roster file `data/strategy_roster.json` can be safely deleted or kept for record-keeping; its presence does not affect default CLI behavior.

### Migration (Resetting / Initializing)
- To reset or re-create a roster, the CLI command that writes the roster (e.g. `lottery select-strategies`) will overwrite or update the specific game entry in `data/strategy_roster.json`.
- Deleting the `data/strategy_roster.json` file completely resets all rosters globally.
