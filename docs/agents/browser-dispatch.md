# Browser Dispatch & Playwright Automation Policy

This document defines the rules and operational boundaries for browser-based bet dispatching and automation within the project.

## 1. Canonical Caixa Browser Dispatcher (`scripts/playwright_caixa_universal.py`)

For Caixa Loterias (`br/*` in registry: Mega-Sena, Lotofácil, Quina, Dupla Sena, Dia de Sorte, Lotomania, etc.), the repository provides `scripts/playwright_caixa_universal.py` as the canonical browser automation tool.

When a user requests browser-based bet injection or Playwright automation for Caixa games:
- Use `scripts/playwright_caixa_universal.py`.
- Feed generated bets either by preparing an `apostas.json` file (`--file apostas.json`) or using built-in presets (`--interactive`, `--preset`).

## 2. Assisted (Human-in-the-Loop) Architecture

The script is strictly **assisted** and human-supervised, not an autonomous bot:
- **Visible Browser (`headless=False`)**: Always runs visibly so the user has full oversight.
- **Persistent Session (`.browser_session/`)**: Preserves legitimate browser session state without storing raw credentials in source or config files.
- **Interactive Authentication & Check-Out**: The script explicitly pauses (`input()`) allowing the human user to perform login, 2FA, and solve any CAPTCHAs directly in the browser UI, and pauses again before final payment confirmation.
- **Zero Bypasses**: The script does not crack CAPTCHAs, bypass security gates, or execute payments autonomously. Its role is mechanical: accurately clicking the chosen numbers on the digital lottery slip to prevent human marking errors.

## 3. Jurisdiction Scoping

`scripts/playwright_caixa_universal.py` operates exclusively against Caixa Econômica Federal's portal (`loteriasonline.caixa.gov.br`). For lotteries in other jurisdictions (`us/*`, `eu/*`, etc.), browser dispatch must not be attempted unless a dedicated, jurisdiction-specific dispatcher is developed following the same human-in-the-loop safeguards.
