# Browser Dispatch & Playwright Automation Policy

## Rule Summary

**For browser-assisted bet placement in Caixa Loterias (`br/*`), use `scripts/playwright_caixa_universal.py`.**

1. **Canonical Assisted Dispatcher**:
   - When requested to use Playwright or browser automation for Caixa Loterias (`br/*`), dispatch via `scripts/playwright_caixa_universal.py` with `--file <path>` or interactive/preset options.
2. **Human-in-the-Loop Safeguards (Assisted, Never Autonomous)**:
   - The dispatcher is explicitly human-assisted: runs visible (`headless=False`), pauses for the user to log in and confirm/pay, and does not crack CAPTCHAs, bypass anti-bot protections, or persist payment credentials.
   - Its primary role is mechanical accuracy: filling the bet slip and injecting chosen combinations into the cart.
3. **Jurisdiction Isolation**:
   - `scripts/playwright_caixa_universal.py` applies exclusively to Brazilian Caixa games (`br/*`). Never attempt to use it for non-Caixa lotteries (`us/*`, `eu/*`).
