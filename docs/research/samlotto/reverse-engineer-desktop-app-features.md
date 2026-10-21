## Summary
Yes—you can reverse-engineer and document an app’s *features* without source code, but for a third‑party desktop app you should keep the work strictly **behavioral and non-circumventing**. The recommended process is to (1) confirm legal/permission scope, (2) perform structured black‑box exploration to inventory user-visible behavior, (3) supplement with safe observations (logs, file I/O, network metadata), (4) optionally add **surface-level** static inspection of binaries (metadata/strings/resources/imports only), and (5) convert evidence into a feature inventory + PRD-style requirements and rebuild guidance.

---

## Current State Analysis
**What you have**
- Desktop application binaries/package files (no source).
- Goal outputs: **Feature inventory doc**, **PRD-style requirements**, and **rebuild/clone guidance**.

**Constraints you stated**
- App is **public/third-party**.
- **No decryption/bypass** (no defeating DRM/licensing/auth, no patching/tampering, no exploit activity).

**Implications**
- The process must prioritize **black-box observation** and documentation.
- Any “static analysis” must remain at **non-circumventing** / surface inspection level.
- The outputs should be phrased as **requirements derived from observed behavior**, not internal implementation details.

---

## Proposed Changes (Process to Follow)
The “changes” here are the concrete artifacts and steps you’ll produce/execute to extract features safely.

### 1) Establish legality + scope guardrails (mandatory)
**What**
- Document your authorization basis and scope boundaries before any analysis.

**Why**
- Third-party reverse engineering is often constrained by EULA and local law; getting this wrong can invalidate the whole effort.

**How**
- Capture:
  - App name/edition/version/build.
  - Your authorization basis (ownership, written permission, interoperability rationale, etc.).
  - Explicit exclusions: no bypassing protections, no decrypting protected assets, no patching binaries, no credential harvesting, no TLS interception via pinning bypass, etc.
- Decide the evidence you will collect and how you will handle privacy (synthetic data, redaction rules).

**Artifact**
- `01-scope-and-guardrails.md`

---

### 2) Set up a controlled observation environment
**What**
- Run the app in an isolated environment where you can observe behavior repeatably.

**Why**
- Prevents accidental data leakage; enables consistent reproduction of flows and error cases.

**How**
- Use a dedicated test machine/VM and a non-production account (if login is required).
- Prepare a small library of synthetic test inputs (dummy files, sample projects, placeholder records).
- Prepare capture methods (screen recordings/screenshots and notes).

**Artifacts**
- `02-environment.md` (OS version, app version, dependencies, test data set list)

---

### 3) Black-box feature discovery (primary method)
**What**
- Systematically walk every user journey and record outcomes.

**Why**
- This is the most defensible, non-circumventing way to “extract features.”

**How**
- Create a “journey script” and iterate:
  - Onboarding / first run
  - Core workflows (create/open/edit/save/export/import)
  - Search/filter/sort/reporting (if applicable)
  - Settings/preferences
  - Error handling (invalid input, missing permissions, offline, cancel/retry)
- For each step, record:
  - Preconditions (account state, settings)
  - Inputs
  - Visible outputs (UI state, files written, messages)
  - Constraints (limits, required fields)

**Artifacts**
- `03-user-journeys.md`
- `04-feature-inventory.md` (feature → subfeatures → constraints → evidence pointers)

---

### 4) UI mapping & information architecture
**What**
- Produce a complete screen catalog and navigation map.

**Why**
- Helps ensure you didn’t miss features hidden in menus/shortcuts/context menus; supports rebuild guidance.

**How**
- Build:
  - Screen catalog: screen IDs, entry/exit points, states (empty/loading/error), key UI components.
  - Navigation graph: how users move between screens.
  - Command/shortcut matrix: menu items, toolbar buttons, context actions, keyboard shortcuts.

**Artifacts**
- `05-screen-catalog.md`
- `06-navigation-map.md` (can be text-based; optionally later convert to diagrams)
- `07-commands-and-shortcuts.md`

---

### 5) Roles/permissions and settings catalog
**What**
- Enumerate roles, entitlements, and configuration options.

**Why**
- Feature access and behavior often vary by role or settings; this matters for PRD and rebuild scope.

**How**
- Identify role types observable without bypass (e.g., admin vs standard, workspace member roles).
- For each setting, record:
  - Location, type, default, scope (global/per-user/per-project), observed effect.

**Artifacts**
- `08-roles-permissions.md`
- `09-settings-catalog.md`

---

### 6) Observe logs and local side effects (read-only)
**What**
- Use app-provided logs and OS-level signals to refine understanding of workflows and errors.

**Why**
- Logs often reveal feature boundaries, error taxonomies, and module names—without any tampering.

**How**
- Identify:
  - App log locations (only those the app writes on its own).
  - Crash reports (if produced).
  - OS event entries related to the app (where applicable).
- Correlate “user action → log entries → outcome.”

**Artifacts**
- `10-log-sources.md`
- `11-error-event-taxonomy.md`
- `12-workflow-trace-notes.md`

---

### 7) Network observation (metadata-first, no interception/bypass)
**What**
- Identify what remote services are contacted and when (hostnames, ports, timing).

**Why**
- This informs integration requirements and rebuild guidance while staying within “no bypass” constraints.

**How**
- Capture only safe metadata:
  - DNS lookups, destination domains/IPs, ports, protocol, frequency, triggers.
- Do **not** attempt TLS downgrade, certificate pinning bypass, or any method intended to inspect encrypted payload contents if it requires circumventing protections.

**Artifacts**
- `13-network-endpoints-observed.md`
- `14-network-trigger-notes.md`

---

### 8) Static “surface” inspection of binaries (optional; non-circumventing)
**What**
- Inspect binary/package *metadata* and exposed resources to infer stack/modules and discover feature clues.

**Why**
- Helps you understand technology stack and find user-facing strings/URLs/config keys that point to features.

**How (allowed)**
- Collect:
  - File metadata (version info, manifests, signing info).
  - Resource bundles, localization tables, icons, help files *if accessible without breaking protections*.
  - Plain strings that are already present (e.g., UI labels, error messages, URLs).
  - Dependency hints (framework names, public library references).

**How (avoid)**
- Avoid any step whose intent is to defeat encryption/packing/DRM, bypass licensing/auth, or extract protected secrets.

**Artifacts**
- `15-binary-surface-analysis.md`

---

### 9) Convert evidence into a PRD-style requirements spec
**What**
- Translate observed features into implementable requirements with acceptance criteria.

**Why**
- A feature list alone is not sufficient to rebuild; requirements must be testable and traceable.

**How**
- For each requirement:
  - Summary (user story)
  - Acceptance criteria (black-box verifiable)
  - Edge cases and error states
  - Evidence links: screen IDs, journey step IDs, log/event references
- Include non-functional requirements inferred from behavior (offline behavior, performance expectations, reliability cues, accessibility signals) but clearly mark what is observed vs assumed.

**Artifact**
- `16-prd-requirements.md`

---

### 10) Produce “rebuild guidance” without copying proprietary implementation
**What**
- A reference architecture and module boundaries inferred from behavior and safe observations.

**Why**
- Helps engineering plan a similar system while avoiding copying protected internals.

**How**
- Define subsystems:
  - UI shell/navigation, domain services, persistence, settings, logging/telemetry, update checks (behavioral), network client.
- Specify interfaces in terms of:
  - Inputs/outputs and contracts (what must happen), not “how their code does it.”
- Maintain a risk/unknowns register for ambiguous behaviors.

**Artifacts**
- `17-rebuild-guidance.md`
- `18-open-questions-and-risks.md`

---

### 11) Validation plan (prove completeness and parity)
**What**
- Create a black-box test suite derived from journeys and requirements.

**Why**
- Ensures your feature inventory and PRD are complete and consistent; provides parity checks for a rebuild.

**How**
- Golden test cases:
  - “Given input X, output must be Y”
  - “Given role R, UI shows commands A/B/C”
  - “Given setting S, behavior changes in these ways”
- Coverage checklist mapped to requirements and screens.

**Artifact**
- `19-validation-plan.md`

---

## Assumptions & Decisions
- **Decision:** Stay within a **non-circumventing** scope: no bypassing licensing/auth/DRM, no decryption, no patching binaries, no pinning bypass.
- **Decision:** Outputs will be phrased as **observed behavior → requirements**, with evidence references, avoiding proprietary implementation details.
- **Assumption:** You can run the application in a controlled test environment and exercise its features with test data.
- **Assumption:** Any logs/resources used are those produced or exposed by the app/OS without defeating protections.

---

## Verification Steps (Definition of Done)
- Feature Inventory completeness:
  - All main workflows documented end-to-end (happy path + error path).
  - Every menu/toolbar/context menu item appears in the command matrix.
  - Screen catalog covers all dialogs/wizards and their states.
- Traceability:
  - Each PRD requirement references at least one evidence source (journey step, screen ID, log/event, or observed side effect).
- Constraints compliance:
  - No step requires bypassing protections, decrypting assets, or modifying/poking at security controls.
  - Captured artifacts use synthetic data; any sensitive info is redacted.
- Rebuild usefulness:
  - Rebuild guidance defines subsystem boundaries and interfaces sufficient for an engineering team to start design.
  - Unknowns are explicitly tracked with proposed non-circumventing experiments to resolve them.

