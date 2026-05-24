# Implementation Spec — Cross-Platform Terminal UI

**Version:** 1.0  
**Date:** 2026-04-29  
**Status:** Ready for Sprint TUI

This document translates the System Design into concrete code scaffolds, task breakdown,
and sequencing guidance for the TUI sprint. Each sub-task maps to a buildable increment
that can be run and demoed independently.

---

## Sprint TUI Task Breakdown

| Sub-task | Deliverable | Est. days | Blocks |
|---|---|---|---|
| TUI.1 | Scaffold + DashboardScreen + navigation shell | 2 | — |
| TUI.2 | SuggestScreen with live strategy output | 1 | TUI.1 |
| TUI.3 | AnalyzeScreen with DataTable + chi² badge | 1 | TUI.1 |
| TUI.4 | BacktestScreen + WizardScreen | 1.5 | TUI.2, TUI.3 |
| TUI.5 | RemoteEngineClient (FastAPI mode) + SettingsScreen | 1 | Sprint 2.1 ✅ |
| TUI.6 | Packaging, CI matrix, `~/.lottery-engine.toml`, docs update | 0.5 | TUI.1–5 |
| **Total** | | **~7 days** | — |

Gate: TUI sprint opens after **Sprint 1.5** (wheels promotion) closes.  
TUI.5 depends on Sprint 2.1 which is already done ✅.

---

## TUI.1 — Scaffold + DashboardScreen + Navigation Shell

### 1.1 pyproject.toml — add `[tui]` extra

```toml
# in [project.optional-dependencies]
tui = [
    "textual>=0.47,<1.0",
    "pyperclip>=1.8",    # cross-platform clipboard (Copy ticket)
]

# in [project.scripts]
lottery-tui = "engine.tui:launch"
```

### 1.2 Global layout CSS — `engine/tui/app.tcss`

```css
/* app.tcss */

Screen {
    layout: vertical;
}

Header {
    height: 1;
    background: $primary;
    color: $text;
}

Footer {
    height: 1;
}

#layout {
    layout: horizontal;
    height: 1fr;
}

#sidebar {
    width: 18;
    border-right: solid $primary;
    padding: 1 0;
}

#content {
    width: 1fr;
    padding: 1 2;
}

ListView {
    background: transparent;
}

ListItem.--highlight {
    background: $accent;
    color: $text;
}
```

### 1.3 Root App — `engine/tui/app.py`

```python
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical

from engine.tui.client import EngineClient, make_client
from engine.tui.screens.dashboard import DashboardScreen
from engine.tui.screens.suggest import SuggestScreen
from engine.tui.screens.analyze import AnalyzeScreen
from engine.tui.screens.backtest import BacktestScreen
from engine.tui.screens.wizard import WizardScreen
from engine.tui.screens.settings import SettingsScreen


_SCREENS = [
    ("Dashboard",  "1", DashboardScreen),
    ("Suggest",    "2", SuggestScreen),
    ("Analyze",    "3", AnalyzeScreen),
    ("Backtest",   "4", BacktestScreen),
    ("Wizard",     "5", WizardScreen),
    ("Settings",   "6", SettingsScreen),
]


class LotteryApp(App):
    """Cross-platform terminal UI for lottery-engine."""

    CSS_PATH = "app.tcss"
    TITLE = "🎰 Prediction Engine"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "push_screen('help')", "Help"),
        ("f", "fetch", "Fetch"),
        *[(key, f"switch_screen_{key}", label) for label, key, _ in _SCREENS],
    ]

    def __init__(self, client: EngineClient | None = None, initial_game: str | None = None):
        super().__init__()
        self.client = client or make_client()
        self.initial_game = initial_game or "br/mega-sena"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="layout"):
            with Vertical(id="sidebar"):
                yield ListView(
                    *[ListItem(Label(f" {label}"), id=f"nav-{key}")
                      for label, key, _ in _SCREENS],
                )
            with Vertical(id="content"):
                yield DashboardScreen(client=self.client, game=self.initial_game)
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        nav_id = event.item.id or ""
        for label, key, ScreenClass in _SCREENS:
            if nav_id == f"nav-{key}":
                self.query_one("#content").remove_children()
                self.query_one("#content").mount(
                    ScreenClass(client=self.client, game=self.initial_game)
                )
                break

    async def action_fetch(self) -> None:
        from engine.tui.client import LocalEngineClient
        if isinstance(self.client, LocalEngineClient):
            await self.client.fetch(self.initial_game)
            self.notify("Fetch complete", title="Data Updated")


def launch() -> None:
    """Entry point for `lottery-tui` script."""
    LotteryApp().run()
```

### 1.4 DashboardScreen — `engine/tui/screens/dashboard.py`

```python
from __future__ import annotations

import asyncio
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button
from textual.reactive import reactive

from engine.tui.client import EngineClient
from engine.tui.models import AnalysisResult


class DashboardScreen(Widget):
    """Landing dashboard: data freshness + hot numbers + quick actions."""

    analysis: reactive[AnalysisResult | None] = reactive(None)

    def __init__(self, client: EngineClient, game: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.game = game

    def compose(self) -> ComposeResult:
        yield Static(id="dash-summary")
        yield Static(id="dash-hot")
        yield Static(id="dash-chi2")
        yield Button("Quick Suggest [S]", id="btn-suggest", variant="primary")
        yield Button("Analyze [A]",       id="btn-analyze")
        yield Button("Backtest [B]",       id="btn-backtest")
        yield Button("Fetch latest [F]",   id="btn-fetch")

    async def on_mount(self) -> None:
        self.run_worker(self._load_analysis(), exclusive=True)

    async def _load_analysis(self) -> None:
        try:
            result = await self.client.get_analysis(self.game)
            self.analysis = result
        except Exception as exc:
            self.query_one("#dash-summary", Static).update(f"[red]Error: {exc}[/]")

    def watch_analysis(self, result: AnalysisResult | None) -> None:
        if result is None:
            return
        self.query_one("#dash-summary", Static).update(
            f"[bold]{self.game}[/]  —  Chi²: p={result.chi2_pvalue:.2f}  {result.chi2_verdict}"
        )
        hot_lines = "\n".join(
            f"  {n:>3}  {'█' * int(result.frequencies.get(n, 0) / 3)}"
            for n in result.hot[:5]
        )
        self.query_one("#dash-hot", Static).update(f"Hot numbers:\n{hot_lines}")
```

---

## TUI.2 — SuggestScreen

### Key behaviors

1. Left panel: strategy list filtered by Nerd / Chaos / All tabs.
2. Right panel: `FilterKnobs` widget (history_limit slider, temperature slider, filters checkboxes).
3. Output area: `TicketDisplay` widget with harmony report.
4. `Enter` or "Regenerate" button triggers `_run_suggest` worker.
5. Worker calls `self.client.suggest(...)` and updates `self.result` reactive.
6. `c` key copies the ticket numbers to clipboard via `pyperclip`.

### `engine/tui/screens/suggest.py` (scaffold)

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button, TabbedContent, TabPane, Select
from textual.reactive import reactive

from engine.tui.client import EngineClient
from engine.tui.models import SuggestResult
from engine.tui.widgets.ticket import TicketDisplay
from engine.tui.widgets.filter_knobs import FilterKnobs
from engine.tui.widgets.strategy_picker import StrategyPicker


class SuggestScreen(Widget):
    BINDINGS = [
        ("r", "regenerate", "Regenerate"),
        ("c", "copy_ticket", "Copy"),
    ]

    result: reactive[SuggestResult | None] = reactive(None)

    def __init__(self, client: EngineClient, game: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.game = game

    def compose(self) -> ComposeResult:
        with TabbedContent("Nerd", "Chaos", "All"):
            for tab in ("nerd", "chaos", "all"):
                with TabPane(tab.capitalize(), id=f"tab-{tab}"):
                    yield StrategyPicker(mode=tab, id=f"picker-{tab}")
        yield FilterKnobs(id="knobs")
        yield TicketDisplay(id="ticket-display")
        yield Button("Regenerate", id="btn-regen", variant="success")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-regen":
            await self.action_regenerate()

    async def action_regenerate(self) -> None:
        knobs = self.query_one("#knobs", FilterKnobs)
        strategy = self._get_selected_strategy()
        self.run_worker(
            self.client.suggest(
                self.game,
                strategy=strategy,
                history_limit=knobs.history_limit,
                temperature=knobs.temperature,
                filters=knobs.active_filters or None,
            ),
            exclusive=True,
        )

    def watch_result(self, result: SuggestResult | None) -> None:
        if result:
            self.query_one("#ticket-display", TicketDisplay).update(result)

    async def action_copy_ticket(self) -> None:
        if self.result:
            import pyperclip
            pyperclip.copy(" ".join(map(str, self.result.ticket)))
            self.notify("Ticket copied to clipboard")

    def _get_selected_strategy(self) -> str:
        # resolve from active tab's StrategyPicker — placeholder
        return "markov"
```

---

## TUI.3 — AnalyzeScreen

### Key behaviors

1. Full-screen `DataTable` with columns: Number | Frequency | Bar | Deviation% | Status.
2. `ChiSquareBadge` widget pinned above the table.
3. Sortable by any column (click header or `s` key).
4. Export to CSV via `e` key (uses `csv` stdlib — no extra dep).
5. Data loaded once on `on_mount` via worker; refreshable via `f`.

### `engine/tui/widgets/chi2.py`

```python
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static


class ChiSquareBadge(Widget):
    DEFAULT_CSS = "ChiSquareBadge { height: 1; }"

    def __init__(self, pvalue: float = 1.0, verdict: str = "unknown", **kwargs):
        super().__init__(**kwargs)
        self._pvalue = pvalue
        self._verdict = verdict

    def compose(self) -> ComposeResult:
        color = "green" if self._pvalue < 0.05 else ("yellow" if self._pvalue < 0.20 else "red")
        yield Static(
            f"[{color}]Chi²  p={self._pvalue:.3f}  —  {self._verdict.upper()}[/]"
        )

    def update(self, pvalue: float, verdict: str) -> None:
        self._pvalue = pvalue
        self._verdict = verdict
        color = "green" if pvalue < 0.05 else ("yellow" if pvalue < 0.20 else "red")
        self.query_one(Static).update(
            f"[{color}]Chi²  p={pvalue:.3f}  —  {verdict.upper()}[/]"
        )
```

---

## TUI.4 — BacktestScreen + WizardScreen

### BacktestScreen key behaviors

1. Input row: game, start draw, end draw (or `--prev N` style range), strategy multi-select.
2. "Run" button fires a `Worker` that calls `self.client.backtest(...)`.
3. Progress bar during run (backtest can take seconds for 50+ draws).
4. Results `DataTable`: rows=draw IDs, columns=strategy names, cells=matches/6.
5. Summary row: avg matches, top-3 capture rate.

### WizardScreen key behaviors

1. Uses Textual's `ContentSwitcher` to implement 3 panels: Step 1 (game), Step 2 (mode), Step 3 (generate + review).
2. Progress breadcrumb rendered as plain `Static` (no extra widget needed).
3. Step 3 is the same `TicketDisplay` + `FilterKnobs` as SuggestScreen — share the widget classes.
4. "Back" button pops to previous step; "Copy" and "Redo" on final step.

### `engine/tui/screens/wizard.py` (scaffold)

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button, ContentSwitcher
from textual.reactive import reactive

from engine.tui.client import EngineClient
from engine.tui.widgets.ticket import TicketDisplay


class WizardScreen(Widget):
    step: reactive[int] = reactive(1)

    def __init__(self, client: EngineClient, game: str, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.game = game
        self._mode: str = "nerd"

    def compose(self) -> ComposeResult:
        yield Static(id="wizard-breadcrumb")
        with ContentSwitcher(initial="step-1"):
            yield self._step1()
            yield self._step2()
            yield self._step3()
        yield Button("← Back", id="btn-back")

    def _step1(self) -> Widget:
        from textual.widgets import Select
        from textual.containers import Vertical
        with Vertical(id="step-1"):
            yield Static("Step 1 — Choose a lottery game")
            yield Select(
                [("br/mega-sena", "br/mega-sena"),
                 ("br/lotofacil", "br/lotofacil"),
                 ("us/powerball", "us/powerball")],
                id="game-select",
            )
            yield Button("Next →", id="btn-next-1", variant="primary")
        return Vertical(id="step-1")

    def _step2(self) -> Widget:
        from textual.containers import Vertical
        with Vertical(id="step-2"):
            yield Static("Step 2 — Choose a prediction mode")
            yield Button("🧠 Nerd Mode",   id="mode-nerd",     variant="primary")
            yield Button("🌀 Chaos Mode",  id="mode-chaos",    variant="warning")
            yield Button("⚡ Ensemble",     id="mode-ensemble", variant="default")
        return Vertical(id="step-2")

    def _step3(self) -> Widget:
        from textual.containers import Vertical
        with Vertical(id="step-3"):
            yield Static("Step 3 — Your ticket")
            yield TicketDisplay(id="wizard-ticket")
            yield Button("Regenerate", id="btn-regen-wiz", variant="success")
            yield Button("Copy",        id="btn-copy-wiz")
        return Vertical(id="step-3")

    def watch_step(self, step: int) -> None:
        self.query_one(ContentSwitcher).current = f"step-{step}"
        breadcrumb = " ──●── ".join(
            f"[bold underline]{s}[/]" if i + 1 == step else s
            for i, s in enumerate(["Pick Game", "Pick Mode", "Generate"])
        )
        self.query_one("#wizard-breadcrumb", Static).update(breadcrumb)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-next-1":
            self.step = 2
        elif bid in ("mode-nerd", "mode-chaos", "mode-ensemble"):
            self._mode = bid.replace("mode-", "")
            self.step = 3
            await self._generate()
        elif bid == "btn-back":
            self.step = max(1, self.step - 1)
        elif bid == "btn-regen-wiz":
            await self._generate()
        elif bid == "btn-copy-wiz":
            await self._copy()

    async def _generate(self) -> None:
        strategy = {"nerd": "markov", "chaos": "kabbalistic", "ensemble": "ensemble"}.get(
            self._mode, "markov"
        )
        result = await self.client.suggest(self.game, strategy=strategy)
        self.query_one("#wizard-ticket", TicketDisplay).update(result)
```

---

## TUI.5 — RemoteEngineClient + SettingsScreen

### RemoteEngineClient

Full implementation in `engine/tui/client.py`. Uses `httpx.AsyncClient`.
The base URL defaults to `http://localhost:8000` and matches the FastAPI sidecar routes
added in Sprint 2.1 (`/games`, `/games/{name}/analysis`, `/games/{name}/suggest`).

Key: the `RemoteEngineClient` must return the same `SuggestResult` / `AnalysisResult`
dataclasses. Parse from JSON using `dacite.from_dict` or manual construction.

### SettingsScreen persisted config

Settings are saved to `~/.lottery-engine.toml` using `tomllib` (stdlib in Python 3.11) for
reading and `tomli_w` or manual string serialization for writing.

```toml
# ~/.lottery-engine.toml

[tui]
default_game    = "br/mega-sena"
default_strategy = "markov"
mode            = "local"       # "local" | "remote"
remote_url      = "http://localhost:8000"
theme           = "dark"        # "dark" | "light"
history_limit   = 100
temperature     = 0.3
```

---

## TUI.6 — Packaging + CI + Docs

### CI matrix (`.github/workflows/tui.yml`)

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11", "3.12"]

steps:
  - run: pip install -e ".[tui,dev]"
  - run: textual diagnose            # exits 1 if terminal is unusable
  - run: pytest tests/tui/ -v
```

### `lottery tui --help` output

```
Usage: lottery tui [OPTIONS]

  Launch the interactive terminal UI.

Options:
  -g, --game TEXT        Initial game  [default: br/mega-sena]
  --mode TEXT            Client mode: local | remote  [default: local]
  --remote-url TEXT      FastAPI sidecar URL (remote mode)  [default: http://localhost:8000]
  --help                 Show this message and exit.
```

### Documentation deliverables (Sprint TUI.6)

1. `docs/tui/README.md` — user-facing quickstart, minimum terminal requirements, keybind table.
2. `docs/tui/CONTRIBUTING.md` — how to add a new screen, how to add a new widget, how to extend
   `EngineClient` with a new method.
3. Update root `README.md` to mention `lottery tui` in the Quick Start section.
4. Update `docs/USER_GUIDE.md` to mention TUI as the preferred entry point for new users.
5. Sprint 5 blog post draft: "From 20 CLI flags to one beautiful terminal dashboard" — uses
   GIF recording of the TUI (record with `asciinema` + `svg-term-cli`).

---

## TicketDisplay Widget

This widget is the visual keystone of the TUI — numbered balls used on every screen that
shows a generated ticket.

```python
# engine/tui/widgets/ticket.py

from __future__ import annotations
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from engine.tui.models import SuggestResult


_BALL_COLORS = {
    "hot":     "bold red on dark_red",
    "neutral": "bold white on blue",
    "cold":    "bold cyan on dark_cyan",
}


class TicketDisplay(Widget):
    """Renders a lottery ticket as colored numbered balls with harmony report."""

    DEFAULT_CSS = "TicketDisplay { height: auto; border: round $primary; padding: 1 2; }"

    def compose(self) -> ComposeResult:
        yield Static(id="balls")
        yield Static(id="report")

    def update(self, result: SuggestResult) -> None:
        balls = "  ".join(f"({n:>2})" for n in result.ticket)
        report_lines = []
        for check, passed in result.harmony_report.items():
            icon = "✓" if passed else "✗"
            color = "green" if passed else "red"
            report_lines.append(f"[{color}]{icon}[/] {check}")
        self.query_one("#balls", Static).update(f"[bold]{balls}[/]")
        self.query_one("#report", Static).update("  ".join(report_lines))
```

---

## Acceptance Criteria

Sprint TUI is complete when:

- [ ] `pip install 'lottery-engine[tui]'` succeeds on Python 3.11 on Ubuntu, macOS, Windows.
- [ ] `lottery tui` launches without error on all three platforms.
- [ ] All 6 screens are navigable via sidebar or number keys.
- [ ] SuggestScreen generates a ticket and displays it in TicketDisplay.
- [ ] AnalyzeScreen renders a DataTable with frequency + deviation data.
- [ ] BacktestScreen runs a 5-draw backtest and shows capture rates.
- [ ] WizardScreen completes a 3-step flow and produces a ticket.
- [ ] `lottery tui --mode remote` connects to the running FastAPI sidecar.
- [ ] `pytest tests/tui/` passes on all platforms in CI.
- [ ] `textual diagnose` exits 0 in CI.
- [ ] `docs/tui/README.md` written and linked from root README.
- [ ] `pyproject.toml` includes `[tui]` extra and `lottery-tui` script entry point.
