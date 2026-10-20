# Reverse Engineering Kit (Desktop App Features)

This folder contains **templates** to help you document a third‑party desktop app’s behavior into:
- a **Feature Inventory**
- a **PRD-style requirements spec**
- **rebuild guidance** (architecture/implementation guidance based on observed behavior)

## Guardrails (important)
- Do **not** decrypt, bypass licensing/DRM/auth, patch binaries, or defeat protections.
- Prefer **black-box observation** (what the app does) over internal analysis.
- Use **synthetic test data** and redact any sensitive info from screenshots/logs.

## How to use
1. Fill out `01-scope-and-guardrails.md` and `02-environment.md`.
2. Run through journeys in `03-user-journeys.md` and log findings.
3. As you discover things, update:
   - `04-feature-inventory.md`
   - `05-screen-catalog.md`
   - `07-commands-and-shortcuts.md`
   - settings/roles/logs/network docs
4. Convert what you observed into `16-prd-requirements.md`.
5. Summarize rebuild ideas in `17-rebuild-guidance.md`.
6. Capture unknowns in `18-open-questions-and-risks.md` and design non-circumventing experiments.

## Evidence IDs (recommended convention)
- Journey steps: `J###` (e.g., `J014`)
- Screens: `S###`
- Requirements: `R###`
- Errors/events: `E###`

