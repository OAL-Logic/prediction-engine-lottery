# ADR-001 — Cross-Platform Terminal UI Framework

| Field         | Value                    |
| ------------- | ------------------------ |
| Status        | **Proposed**             |
| Date          | 2026-04-29               |
| Deciders      | Operator D (sole author) |
| Supersedes    | —                        |
| Superseded by | —                        |

---

## Context

The prediction engine ships as a Typer + Rich CLI. Power users want an interactive experience
that is richer than `--help` flags but lighter than the Expo mobile app: a persistent terminal
window where they can browse strategies, run suggestions, and see analysis results without
memorizing subcommand syntax.

Constraints that drive the decision:

1. **Cross-platform without a browser** — must work on Windows (CMD / Windows Terminal / PowerShell),
   macOS (Terminal.app / iTerm2), and Linux (xterm, alacritty, gnome-terminal).
2. **Same Python package** — no separate installer, no Electron, no Go binary.
3. **Rich already in core deps** — any new UI framework should compose with, not compete with, Rich.
4. **Async-friendly** — the FastAPI sidecar (Sprint 2.1) is async; the TUI may want to call it
   in the background while keeping the screen responsive.
5. **Maintainable by a solo developer** — framework must reduce boilerplate, not add it.

---

## Options Considered

### Option A — Textual (Textualize)

- Python-native full-featured TUI framework built directly on Rich.
- CSS-like reactive layout (TCSS — Textual CSS).
- Async-native (`asyncio`); built-in `Worker` threads for background tasks.
- First-class Windows support via VT100 emulation (tested on Windows Terminal ≥ 1.18).
- Mouse, keyboard, focus management, screen routing all included.
- PyPI: `textual>=0.47`; ~4 MB wheel.
- Active development; Textualize is the same team that made Rich.

**Pro:** Directly extends the existing Rich investment. CSS layouts are maintainable.
Async workers pair perfectly with the FastAPI sidecar client.
**Con:** Adds ~4 MB to the install footprint (optional extra `[tui]` mitigates this).
Requires terminal with VT100/ANSI support (Windows CMD without WT is degraded).

### Option B — prompt_toolkit

- Excellent for REPL-style UIs and completion-heavy CLIs.
- Layout system exists but is XML/HSplit/VSplit based — harder to read at scale.
- Already transitively used by IPython; well-tested cross-platform.

**Pro:** Very stable, widely deployed.
**Con:** Layout model is more verbose for multi-screen apps. Not built on Rich — would duplicate
rendering logic. Better suited to single-panel input prompts than dashboard-style screens.

### Option C — urwid

- Mature, low-level Python TUI toolkit.
- Cross-platform; powers tools like pudb.
- No async support without bridging; widget set is smaller.

**Pro:** Battle-tested, minimal dependencies.
**Con:** Synchronous event loop requires manual async bridging. Widget API is verbose. No
built-in CSS-like layouts. Community activity is low.

### Option D — curses / windows-curses

- Standard library (with `windows-curses` shim on Windows).
- Lowest-level option; full control.

**Pro:** Zero extra dependencies.
**Con:** Windows `windows-curses` is a notoriously thin shim; color support and resize
handling are fragile. Layout must be hand-coded in pixel coordinates. Maintenance burden
is very high for a solo developer.

### Option E — Enhanced Wizard Only (no persistent TUI)

- Extend the existing `lottery wizard` command with richer `Prompt.ask` flows.
- Zero new dependencies.

**Pro:** Ships in one session; no new concepts.
**Con:** Not a persistent interface. Cannot show live analysis alongside suggestions.
Does not address the "browse and explore" use case. Does not scale to the Expo app story
where a terminal "Nerd mode" is a marketing differentiator.

---

## Decision

**Option A — Textual**, added as an optional extra `pip install lottery-engine[tui]`.

Rationale:

1. Rich is already in core; Textual is the natural next layer. No new rendering concepts.
2. CSS layouts make multi-screen apps maintainable at solo-developer scale.
3. Async workers eliminate the "blocking UI" problem when calling the sidecar.
4. Windows Terminal is the default terminal on Windows 11; VT100 is a safe baseline.
5. Optional extra keeps the base install footprint unchanged for CLI-only users.

---

## Consequences

**Positive:**
- Persistent, navigable dashboard replaces the need to memorize ~20 subcommands.
- `lottery tui` becomes the recommended entry point for non-developer end users.
- The TUI can be demoed as a GIF in Sprint 5 blog posts — higher perceived quality than a
  plain CLI recording.
- `RemoteEngineClient` (TUI data layer) reuses the same FastAPI contract, exercising the
  sidecar API before the Expo app ships.

**Negative / risks:**
- Windows CMD (legacy, without Windows Terminal) degrades to partial rendering.
  Mitigation: document minimum terminal requirements; detect and warn at startup.
- `textual` release cadence is fast; TCSS API had breaking changes between 0.40 and 0.47.
  Mitigation: pin `textual>=0.47,<1.0` and add a CI step that runs `textual diagnose`.
- TUI is a separate screen surface from the CLI. Two surfaces = two things to keep in sync.
  Mitigation: both surfaces share the same `EngineClient` abstraction layer (see System Design).

**Neutral:**
- `lottery-tui` entry point added to `pyproject.toml`; existing `lottery` entry point unchanged.
- TUI sprint is gated behind Sprint 1.5 (wheels promotion) because the TUI's SuggestScreen
  will expose the wheel picker — building it before wheels are promoted would cause churn.

---

## Minimum Terminal Requirements

| Platform | Minimum                  | Recommended            |
| -------- | ------------------------ | ---------------------- |
| Windows  | Windows Terminal 1.18+   | Windows Terminal 1.20+ |
| macOS    | Terminal.app (macOS 12+) | iTerm2 3.5+            |
| Linux    | xterm-256color           | alacritty / kitty      |
| SSH      | PuTTY with UTF-8         | any modern SSH client  |

Textual performs a capability check on startup. If the terminal does not support 256-color or
Unicode, `lottery tui` prints a warning and falls back to `lottery wizard` (the Rich Prompt flow).

---

## Revisit Triggers

- Textual releases 1.0 with breaking TCSS changes → evaluate upgrade cost.
- Expo app ships and TUI usage is negligible → deprioritize TUI maintenance.
- Windows CMD usage is reported by users → evaluate `windows-curses` shim as a fallback.
