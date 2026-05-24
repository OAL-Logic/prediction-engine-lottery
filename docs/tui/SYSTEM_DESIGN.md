# System Design — Cross-Platform Terminal UI (lottery tui)

**Version:** 1.0  
**Date:** 2026-04-29  
**Author:** Operator D  
**Status:** Design / Pre-implementation

---

## 1. Problem Statement

The prediction engine's CLI surfaces ~20 subcommands. First-time users run `lottery --help`, get
overwhelmed, and leave. Power users want to keep a terminal pane open and iteratively explore
strategies without typing full commands. Neither group is served by the current flat CLI.

The TUI (Terminal User Interface) solves this by providing a persistent, navigable dashboard
that wraps the same engine logic behind a menu-driven interface, ships in the same pip package
as an optional extra, and runs identically on Windows, macOS, and Linux.

---

## 2. Goals & Non-Goals

### Goals
- Single `lottery tui` command launches a full-screen interactive terminal app.
- All capabilities of the existing CLI accessible without memorizing flags.
- Works on Windows Terminal, macOS Terminal.app / iTerm2, Linux xterm/alacritty.
- Async — background tasks (fetch, backtest) do not freeze the UI.
- Same Python package; TUI is gated behind `pip install lottery-engine[tui]`.
- Graceful degradation: if terminal does not support VT100/256-color, fall back to `lottery wizard`.

### Non-Goals
- Not a web app. Not Electron. Not a GUI.
- Does not replace the Expo mobile app (Sprint 4) — they coexist.
- Does not replace the existing CLI commands — all subcommands stay.
- Does not support terminals that cannot render ANSI escape codes.

---

## 3. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         USER'S TERMINAL                                    │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  lottery tui   →   engine/tui/app.py  →  LotteryApp(textual.App)    │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │  HEADER BAR                                                  │    │  │
│  │  │  [🎰 Prediction Engine]  [Game: br/mega-sena ▾]  [Nerd|Chaos]│   │  │
│  │  ├─────────────────────────────────────────────────────────────┤    │  │
│  │  │ SIDEBAR  │                   CONTENT AREA                   │    │  │
│  │  │          │                                                   │    │  │
│  │  │▶Dashboard│  ┌─────────────────────────────────────────────┐ │    │  │
│  │  │  Suggest │  │                                             │ │    │  │
│  │  │  Analyze │  │          Active Screen                      │ │    │  │
│  │  │  Backtest│  │                                             │ │    │  │
│  │  │  Wizard  │  │                                             │ │    │  │
│  │  │  Settings│  └─────────────────────────────────────────────┘ │    │  │
│  │  ├─────────────────────────────────────────────────────────────┤    │  │
│  │  │  FOOTER BAR   chi²: p=0.31  |  [?] Help  [q] Quit  [Tab] Nav│   │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   EngineClient       │
                         │   (Protocol / ABC)   │
                         └────┬───────────┬─────┘
                              │           │
               ┌──────────────▼──┐   ┌───▼────────────────┐
               │ LocalEngineClient│   │ RemoteEngineClient  │
               │  direct imports  │   │  httpx → FastAPI    │
               │  engine.* modules│   │  sidecar (Sprint 2) │
               └──────────────────┘   └────────────────────┘
```

### Data Flow (Local Mode — default)

```
User action (keystroke / click)
  → Textual Message → Screen.on_<event>()
    → EngineClient.suggest(...) [async call]
      → LocalEngineClient._run_in_executor(strategy.suggest, ...)
        → BaseStrategy.suggest() [blocking Python, runs in thread]
          → pandas / numpy computation
        → returns SuggestResult
      → Screen updates reactive attribute
        → Textual reactive watch triggers widget update
          → Updated ticket display in terminal
```

### Data Flow (Remote Mode — `--mode remote`)

```
User action
  → Screen.on_<event>()
    → RemoteEngineClient.suggest(...) [async httpx call]
      → POST http://localhost:8000/games/{name}/suggest
        → FastAPI sidecar
      → returns SuggestResult (same dataclass)
    → Screen update (identical to local)
```

---

## 4. Component Inventory

### 4.1 Entry Points

| Component                 | Path                 | Purpose                                 |
| ------------------------- | -------------------- | --------------------------------------- |
| `lottery tui` CLI command | `engine/cli/main.py` | Typer command that launches the TUI app |
| `lottery-tui` script      | `pyproject.toml`     | Direct entry point for `[tui]` extra    |
| `LotteryApp`              | `engine/tui/app.py`  | Root Textual `App` subclass             |

### 4.2 Screens

Each screen is a `textual.screen.Screen` subclass in `engine/tui/screens/`.

| Screen            | File           | Description                                                     |
| ----------------- | -------------- | --------------------------------------------------------------- |
| `DashboardScreen` | `dashboard.py` | Landing page. Data freshness, sparklines, quick-action buttons. |
| `SuggestScreen`   | `suggest.py`   | Strategy tabs (Nerd / Chaos / All), knob panel, ticket output.  |
| `AnalyzeScreen`   | `analyze.py`   | Number frequency DataTable, deviation bars, chi² badge.         |
| `BacktestScreen`  | `backtest.py`  | Draw picker, strategy multi-select, capture-rate results grid.  |
| `WizardScreen`    | `wizard.py`    | 3-step guided flow: pick game → pick mode → generate & review.  |
| `SettingsScreen`  | `settings.py`  | Default game, strategy, theme, adapter refresh interval.        |
| `HelpScreen`      | `help.py`      | Overlay with keybind reference and concept glossary.            |

### 4.3 Widgets (shared across screens)

| Widget           | File                         | Description                                                      |
| ---------------- | ---------------------------- | ---------------------------------------------------------------- |
| `TicketDisplay`  | `widgets/ticket.py`          | Renders a generated ticket as colored numbered balls.            |
| `SparklineBar`   | `widgets/sparkline.py`       | Horizontal in-cell frequency sparkline (Pure Rich).              |
| `ChiSquareBadge` | `widgets/chi2.py`            | Green/amber/red pill showing chi² p-value and verdict.           |
| `StrategyPicker` | `widgets/strategy_picker.py` | Tabbed list: statistical / ml / deep / fun.                      |
| `GameSelector`   | `widgets/game_selector.py`   | Dropdown / select widget bound to game registry.                 |
| `FilterKnobs`    | `widgets/filter_knobs.py`    | Sliders/toggles for `history_limit`, `temperature`, `--filters`. |
| `CaptureGrid`    | `widgets/capture_grid.py`    | DataTable for backtest results (draw × strategy matrix).         |

### 4.4 Data Layer

| Class                | File                   | Description                                          |
| -------------------- | ---------------------- | ---------------------------------------------------- |
| `EngineClient`       | `engine/tui/client.py` | `Protocol` / ABC defining the async interface.       |
| `LocalEngineClient`  | `engine/tui/client.py` | Wraps engine modules via `asyncio.to_thread`.        |
| `RemoteEngineClient` | `engine/tui/client.py` | `httpx.AsyncClient` pointing at the FastAPI sidecar. |
| `ClientFactory`      | `engine/tui/client.py` | Returns the right client based on `--mode` flag.     |

### 4.5 Data Types (shared DTOs)

Defined in `engine/tui/models.py` as `dataclasses`. Kept separate from CLI types to avoid
circular imports.

```python
@dataclass
class GameInfo:
    name: str; alias: str; pick_count: int; pool: int; data_available: bool

@dataclass
class SuggestResult:
    ticket: list[int]; strategy: str; filters_applied: list[str]
    harmony_report: dict[str, bool]; warnings: list[str]

@dataclass
class AnalysisResult:
    frequencies: dict[int, int]; deviations: dict[int, float]
    chi2_pvalue: float; chi2_verdict: str   # "uniform" | "non-uniform" | "insufficient_data"
    hot: list[int]; cold: list[int]

@dataclass
class BacktestResult:
    draw_id: int; strategy: str; ticket: list[int]
    actual: list[int]; matches: int; capture_rate: float
```

---

## 5. Screen Designs

### 5.1 DashboardScreen

```
┌─ Dashboard ──────────────────────────────────────────────────────────────┐
│                                                                           │
│  br/mega-sena                       Last draw: #2991  (2026-04-28)       │
│  ─────────────────────────────────────────────────────────────────────   │
│                                                                           │
│  Hot numbers (last 50 draws)                                             │
│   10 ████████████████ 47                                                 │
│   23 ██████████████   42                                                 │
│   37 █████████████    40                                                 │
│    5 ████████████     37                                                 │
│   48 ███████████      35                                                 │
│                                                                           │
│  Chi² gate: p = 0.31  ●  UNIFORM — no statistical edge detected         │
│                                                                           │
│  Last optimize run:  markov@100 draws  top-3 capture: 41.2%             │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  [S] Quick Suggest│  │  [A] Analyze     │  │  [B] Backtest    │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                           │
│  [F] Fetch latest draws                                                  │
└───────────────────────────────────────────────────────────────────────── ┘
```

### 5.2 SuggestScreen

```
┌─ Suggest ─────────────────────────────────────────────────────────────────┐
│  Nerd  │  Chaos  │  All                                                    │
│  ──────────────────────────────────────────────────────────────────────   │
│                                                                            │
│  Strategy   ┌───────────────────────────────┐  ┌────────────────────┐    │
│  ──────────  │ markov                         │  │  History limit     │    │
│  > markov   │ bayesian                       │  │  [──────●──────] 100│    │
│  bayesian   │ monte_carlo                    │  ├────────────────────┤    │
│  monte_carlo│ weighted                       │  │  Temperature       │    │
│  weighted   │ pattern                        │  │  [──●──────────] 0.3│    │
│  pattern    └───────────────────────────────┘  ├────────────────────┤    │
│                                                  │  Filters           │    │
│                                                  │  [✓] balanced      │    │
│                                                  │  [ ] no_repeat     │    │
│                                                  └────────────────────┘    │
│                                                                            │
│  ╔══════════════════════════════════════╗                                  │
│  ║  Generated Ticket                    ║                                  │
│  ║                                      ║                                  │
│  ║   ( 5) (17) (23) (37) (48) (54)      ║                                  │
│  ║                                      ║                                  │
│  ║  sum: 184 ✓  parity: 3/3 ✓           ║                                  │
│  ║  breadth: all 6 decades ✓            ║                                  │
│  ╚══════════════════════════════════════╝                                  │
│                                                                            │
│  [Enter] Regenerate   [C] Copy   [V] Validate                             │
└────────────────────────────────────────────────────────────────────────── ┘
```

### 5.3 AnalyzeScreen

```
┌─ Analyze ─────────────────────────────────────────────────────────────────┐
│  br/mega-sena  │  History: 100 draws  │  Sort: [frequency ▾]              │
│  ──────────────────────────────────────────────────────────────────────   │
│                                                                            │
│  #   Freq   Bar                    Deviation  Status                      │
│  ──  ─────  ─────────────────────  ─────────  ──────                     │
│  10   47   ████████████████████    +21.5%     HOT 🔥                     │
│  23   42   ████████████████        +8.2%      HOT                        │
│  37   40   ███████████████         +3.1%      NEUTRAL                    │
│   5   38   ██████████████          -1.5%      NEUTRAL                    │
│  48   35   █████████████           -9.3%      COLD                       │
│  ...                                                                       │
│  59    8   ██                      -79.2%     COLD ❄️                     │
│                                                                            │
│  Chi² test:  χ²=61.3  df=59  p=0.31  →  UNIFORM (no predictive signal)   │
│                                                                            │
│  [H] History range   [S] Sort   [F] Filter   [E] Export CSV               │
└────────────────────────────────────────────────────────────────────────── ┘
```

### 5.4 BacktestScreen

```
┌─ Backtest ─────────────────────────────────────────────────────────────────┐
│  Game: br/mega-sena    Draw range: [2981] to [2991]   [Run]                │
│  ───────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  Strategies:  [✓] markov  [✓] bayesian  [ ] monte_carlo  [✓] weighted     │
│                                                                             │
│  Draw  │ Actual              │ markov │ bayesian │ weighted │               │
│  ────  │ ─────────────────── │ ────── │ ──────── │ ──────── │               │
│  2991  │  5 17 23 37 48 54   │  2/6   │   3/6    │   2/6    │               │
│  2990  │  8 12 34 41 55 58   │  1/6   │   2/6    │   3/6    │               │
│  2989  │  3 19 27 31 45 52   │  2/6   │   1/6    │   2/6    │               │
│  ...                                                                         │
│                                                                             │
│  ──────────────────────────────────────────────────────────────────────    │
│  Avg matches:          markov: 1.8   bayesian: 2.1   weighted: 2.3        │
│  Top-3 capture rate:   markov: 22%   bayesian: 31%   weighted: 38%        │
│                                                                             │
│  [↑↓] Select draw   [Enter] Expand   [E] Export   [O] Optimize            │
└─────────────────────────────────────────────────────────────────────────── ┘
```

### 5.5 WizardScreen

```
┌─ Wizard — Step 2 of 3 ────────────────────────────────────────────────────┐
│  ① Pick Game  ──●──  ② Pick Mode  ───────  ③ Generate & Review            │
│                                                                             │
│  Choose your prediction mode:                                              │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  🧠  NERD MODE                                                         │  │
│  │  Statistical strategies gated by chi² significance test.              │  │
│  │  Best for: data-driven players who want the honest math.              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  🌀  CHAOS MODE                                                        │  │
│  │  Esoteric strategies: moon phase, kabbalistic numerology, ley lines.  │  │
│  │  Marked is_predictive=False. Pure fun. No pretense of math.           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  ⚡  ENSEMBLE                                                           │  │
│  │  Voting ensemble across all available strategies. Broadest coverage.  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  [←] Back   [Enter/Click] Select & Continue                                │
└─────────────────────────────────────────────────────────────────────────── ┘
```

---

## 6. File Structure

```
engine/
└── tui/
    ├── __init__.py          # exports LotteryApp
    ├── app.py               # LotteryApp(App) — root, screen router, CSS loader
    ├── app.tcss             # Global layout CSS (header, sidebar, content, footer)
    ├── client.py            # EngineClient protocol + LocalEngineClient + RemoteEngineClient
    ├── models.py            # Shared DTOs (GameInfo, SuggestResult, AnalysisResult, BacktestResult)
    ├── screens/
    │   ├── __init__.py
    │   ├── dashboard.py
    │   ├── suggest.py
    │   ├── analyze.py
    │   ├── backtest.py
    │   ├── wizard.py
    │   ├── settings.py
    │   └── help.py
    └── widgets/
        ├── __init__.py
        ├── ticket.py        # TicketDisplay — numbered balls
        ├── sparkline.py     # SparklineBar
        ├── chi2.py          # ChiSquareBadge
        ├── strategy_picker.py
        ├── game_selector.py
        ├── filter_knobs.py
        └── capture_grid.py
```

---

## 7. Data Layer Design

### 7.1 Protocol

```python
# engine/tui/client.py

from typing import Protocol, runtime_checkable

@runtime_checkable
class EngineClient(Protocol):
    async def get_games(self) -> list[GameInfo]: ...
    async def fetch(self, game: str) -> None: ...
    async def get_analysis(self, game: str, history_limit: int = 100) -> AnalysisResult: ...
    async def suggest(
        self,
        game: str,
        strategy: str,
        history_limit: int = 100,
        temperature: float = 0.3,
        filters: list[str] | None = None,
        **kwargs: Any,
    ) -> SuggestResult: ...
    async def backtest(
        self, game: str, draw_ids: list[int], strategies: list[str]
    ) -> list[BacktestResult]: ...
```

### 7.2 LocalEngineClient

```python
class LocalEngineClient:
    """Direct import — same process as the TUI. Zero network latency."""

    async def suggest(self, game: str, strategy: str, **kwargs) -> SuggestResult:
        adapter = _get_adapter(game)
        df = adapter.load()
        rules = adapter.rules()
        strat = _load_strategy(strategy)
        # run blocking code in a thread so Textual event loop stays responsive
        ticket = await asyncio.to_thread(strat.suggest, df=df, rules=rules, **kwargs)
        return SuggestResult(ticket=ticket, strategy=strategy, ...)
```

### 7.3 RemoteEngineClient

```python
class RemoteEngineClient:
    """HTTP client for the FastAPI sidecar (Sprint 2.1)."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self._http = httpx.AsyncClient(base_url=base_url, timeout=30)

    async def suggest(self, game: str, strategy: str, **kwargs) -> SuggestResult:
        r = await self._http.post(
            f"/games/{game}/suggest",
            json={"strategy": strategy, **kwargs}
        )
        r.raise_for_status()
        return SuggestResult(**r.json())
```

### 7.4 ClientFactory

```python
def make_client(mode: str = "local", remote_url: str = "http://localhost:8000") -> EngineClient:
    if mode == "remote":
        return RemoteEngineClient(base_url=remote_url)
    return LocalEngineClient()
```

---

## 8. CLI Integration

New command added to `engine/cli/main.py`:

```python
@app.command()
def tui(
    game: Annotated[Optional[str], typer.Option("--game", "-g")] = None,
    mode: Annotated[str, typer.Option("--mode")] = "local",
    remote_url: Annotated[str, typer.Option("--remote-url")] = "http://localhost:8000",
) -> None:
    """Launch the interactive terminal UI."""
    try:
        from engine.tui import LotteryApp
    except ImportError:
        rprint("[red]TUI not installed.[/] Run: pip install 'lottery-engine[tui]'")
        raise typer.Exit(1)

    client = make_client(mode=mode, remote_url=remote_url)
    app_instance = LotteryApp(client=client, initial_game=game)
    app_instance.run()
```

---

## 9. `pyproject.toml` Changes

```toml
[project.optional-dependencies]
# ... existing extras unchanged ...
tui = [
    "textual>=0.47,<1.0",
]

[project.scripts]
lottery     = "engine.cli.main:app"
lottery-tui = "engine.tui:launch"   # direct entry point, bypasses Typer
```

---

## 10. Keybind Reference

| Key                 | Action                                                                            |
| ------------------- | --------------------------------------------------------------------------------- |
| `Tab` / `Shift+Tab` | Cycle sidebar items                                                               |
| `1`–`6`             | Jump to screen by index (Dashboard, Suggest, Analyze, Backtest, Wizard, Settings) |
| `Enter`             | Activate selection / run action                                                   |
| `?`                 | Open help overlay                                                                 |
| `q`                 | Quit                                                                              |
| `f`                 | Fetch latest draws (any screen)                                                   |
| `Escape`            | Close overlay / go back one step                                                  |
| `c`                 | Copy current ticket to clipboard (Suggest screen)                                 |
| `e`                 | Export current table as CSV (Analyze / Backtest screens)                          |
| `r`                 | Regenerate ticket (Suggest screen)                                                |

---

## 11. Cross-Platform Terminal Compatibility

### Detection at startup

```python
# engine/tui/app.py  (inside on_mount)

import shutil, os

def _check_terminal(self) -> bool:
    """Return True if the terminal can run the full TUI."""
    cols, rows = shutil.get_terminal_size((80, 24))
    if cols < 80 or rows < 24:
        return False
    # Textual's own check
    from textual.app import TEXTUAL_SUPPORTS_SMOOTH_ANIMATION
    return True  # textual raises internally if VT100 missing
```

### Windows-specific notes

- Windows Terminal (WT) 1.18+ supports VT100, Unicode, 256-color — full TUI works.
- ConHost (legacy `cmd.exe` window) supports VT100 from Windows 10 v1511 but lacks
  proper mouse event delivery for resize. The TUI detects this and disables mouse interactions,
  remaining keyboard-only.
- PowerShell 7+ in Windows Terminal: identical to WT behavior — fully supported.

### SSH / remote sessions

- `TERM=xterm-256color` must be set on the remote end (usual default for most distros).
- Mouse events require `TERM` to support mouse reporting (`xterm-256color` qualifies).

---

## 12. Testing Strategy

| Layer                   | Framework                                                          | What is tested                                                       |
| ----------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `EngineClient` (local)  | `pytest` + `asyncio`                                               | All methods return correct DTOs; no engine regression                |
| `EngineClient` (remote) | `pytest` + `httpx.MockTransport`                                   | HTTP contract matches FastAPI schema                                 |
| `LotteryApp`            | `textual.testing.Pilot`                                            | Mount, screen transitions, key presses, DOM assertions               |
| Widgets                 | `textual.testing.Pilot`                                            | TicketDisplay renders correct ball count; ChiSquareBadge color logic |
| Cross-platform          | GitHub Actions matrix: ubuntu-latest, macos-latest, windows-latest | `textual diagnose` exits 0; `pytest` passes on all three             |

---

## 13. Dependency on Sprint 1.5

The TUI's `SuggestScreen` exposes the wheel picker (`FilterKnobs` includes a "Use wheel" toggle).
This feature requires `steiner_wheel.py` to be promoted to `engine/wheels/` (Sprint 1.5).

**Gate:** TUI sprint starts only after Sprint 1.5 is closed. If Sprint 1.5 slips, the wheel
toggle is hidden behind a `data-available=false` state and replaced with a "Coming soon" badge
(the same pattern used by stub-game adapters).

---

## 14. Trade-offs and Risks

| Decision                        | Trade-off                                                             | Mitigation                                             |
| ------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------ |
| Textual over curses             | +Productivity, +Windows; but +4 MB, Textual API churn                 | Pin `<1.0`; CI `textual diagnose`                      |
| LocalEngineClient               | Zero latency, no server needed; but couples TUI to Python import path | `EngineClient` Protocol — easy swap to Remote          |
| Optional `[tui]` extra          | Keeps base install clean; but users need `pip install ... [tui]`      | `lottery tui` prints install hint on ImportError       |
| Screens as full-screen switches | Clean UX; but no split-pane comparison view                           | Accept trade-off; split-pane is a post-1.0 feature     |
| No persistence of settings      | Stateless; but users re-enter preferred game each session             | Sprint TUI.6 adds `~/.lottery-engine.toml` config file |
