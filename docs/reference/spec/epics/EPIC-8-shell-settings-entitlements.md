# EPIC 8 — Shell · Settings · Entitlements · Reusable Components

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win](EPIC-7-tickets-lifecycle.md) · End

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F8.1 — App shell + toolbar + navigation](#f8-1-app-shell-toolbar-navigation)
- [F8.2 — Settings store (per-game + global)](#f8-2-settings-store-per-game-global)
- [F8.3 — Entitlements (Free / Pro gate)](#f8-3-entitlements-free-pro-gate)
- [F8.4 — Reusable components](#f8-4-reusable-components)
- [F8.5 — Charts (FrequencyChart, TrendChart)](#f8-5-charts-frequencychart-trendchart)
  - [Epic 8 exit criteria](#epic-8-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** the app frame that hosts everything — toolbar navigation, persisted
settings, the Free/Pro capability gate, and the shared UI components every screen
reuses. **Verified source:** Doc 00 (edition matrix), Doc 07 §6, Doc 08 (screens).
**Depends on:** nothing to start (F8.1/F8.4 built alongside Phase 1); F8.2/F8.3 as
features land. **Phase:** 1→7 (cross-cutting).

**Features:** F8.1 App shell + navigation · F8.2 Settings store · F8.3 Entitlements ·
F8.4 Reusable components · F8.5 Charts.

---

## F8.1 — App shell + toolbar + navigation
**User stories** — *As a player,* a top toolbar exposes the 8 verbs (Lottery,
Drawings, Statistics, Prediction, Search, Optimization, Check-Win, Help) with the
active game + draw count in a status bar; a persistent split view keeps Pool builder
↔ Ticket store visible while feature panels open over it (Doc 08 §1).
**Acceptance:** AC-X1. **Module:** `apps/desktop` shell + router.

**Chain**
- **S1:** shell layout: toolbar → routes (screens S10/S12/S20/S30/S32/S31/S33/help); center split (Generation ↔ TicketStore); status bar.
- **S2 (E2E):** each toolbar verb routes to its screen; the ticket store stays mounted.
- **S3:** implement router + layout matching Doc 08 §1 IA.
- **S4:** mount feature panels as routes/modals.
- **S5:** launch app; click all 8 verbs.
- **Gate:** `{{ACCEPTANCE}}`=AC-X1; navigation map (Doc 08 §3) reproduced.

---

## F8.2 — Settings store (per-game + global)
**User stories** — *As a player,* my range, filters, selections, and window survive
reopen — per game where it matters, globally where it doesn't (Doc 07 §4.3).
**Acceptance:** AC-X1. **Module:** `SettingsStore` port + `data/settings`.

**Chain**
- **S1:** port `SettingsStore { load(scope: {kind:'global'} | {kind:'game'; id}): State; save(scope, state) }`; layered read (global ⊕ per-game override).
- **S2:** save per-game filter set + range; reopen → restored; global settings shared across games.
- **S3:** JSON store (mirrors the original `Current_Set.ini` groups: LotteryParam, Position, Search, depth…).
- **S4:** every screen reads/writes through it.
- **S5:** set state, restart app, confirm persistence.
- **Gate:** `{{ACCEPTANCE}}`=AC-X1; layering correct.

---

## F8.3 — Entitlements (Free / Pro gate)
**User stories** — *As the business,* the Free edition blocks pool >10, wheels,
optimization, and prediction — each with its message; Pro unlocks all (Doc 00 matrix).
**Acceptance:** AC-X2. **Module:** `core/entitlements`.

**Chain**
- **S1:** `Entitlements { can(cap: 'poolOver10'|'wheels'|'optimize'|'predict'|'allFilters'): boolean }` from an edition config.
- **S2:** Free denies the 4 caps + filter subset; Pro allows all; each denial exposes a message key.
- **S3:** single capability set (not two binaries).
- **S4:** generation (≤10), wheeling, optimization, prediction screens check `can()` and show the gate message.
- **S5:** run as Free; hit each gate; switch to Pro; gates open.
- **Gate:** `{{ACCEPTANCE}}`=AC-X2; all 6 rows of the matrix enforced.

---

## F8.4 — Reusable components
**User stories** — *As a developer,* one implementation each of NumberGrid,
RangeSelector, PositionSelector, SkipsInspector, ExportMenu is reused across screens
(Doc 07 §6).
**Acceptance:** supports AC-G*, AC-S8. **Module:** `packages/ui`.

**Chain**
- **S1:** component contracts: `<NumberGrid pool selected onToggle max/>` (selected = highlighted; enforces max via entitlements), `<RangeSelector value onChange/>` (prev 2/3/5/10/20/30/50/current/custom), `<PositionSelector k value onChange/>`, `<SkipsInspector skips/>`, `<ExportMenu onExport/>`.
- **S2:** unit/interaction tests per component (selection cap, range options).
- **S3:** implement; theme-aware.
- **S4:** consumed by EPIC 2/3/4/7 screens.
- **S5:** storybook/manual render of each.
- **Gate:** each component has a test + is used by ≥2 screens (real seam, not hypothetical).

---

## F8.5 — Charts (FrequencyChart, TrendChart)
**User stories** — *As an analyst,* every statistic and filter shows a consistent
frequency bar chart and trend line (Doc 08 §4 pattern #3).
**Acceptance:** supports AC-F6, AC-S8. **Module:** `packages/ui` charts.

**Chain**
- **S1:** `<FrequencyChart data/>`, `<TrendChart series/>` — one design system, light+dark, accessible; follow the `/dataviz` guidance.
- **S2:** render golden data; snapshot; a11y check.
- **S3:** implement once; reuse in Statistics tabs, Filter assistant, Drawings-Trend.
- **S4:** consumed by F2.12, F4.6, F6.4.
- **S5:** render across all three consumers.
- **Gate:** used by ≥3 screens; consistent axis/legend/tooltip.

### Epic 8 exit criteria
Shell navigates all screens; settings persist per-game + global; the Free/Pro matrix
is fully enforced; shared components + charts back every screen.

---
> **Next Steps**: [⬅️ EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win](EPIC-7-tickets-lifecycle.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · End
