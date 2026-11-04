#!/usr/bin/env python3
"""
scripts/check_popperian_governance.py
=====================================
Automated CI/CD Quality Gate & Strategy Tier Governance Guardrail.

Enforces ADR-0005:
1. All strategies have valid approved tiers.
2. Strategy class attributes match registry tier definitions.
3. Production presets ('default', 'fast') never contain tier='fun' strategies.
4. All 9 fringe theories are isolated in tier='fun' and grouped in preset 'fringe'.
5. Empirical study reports maintain null hypothesis H_0 (p >= 0.01).

Exit codes:
  0 - All Popperian governance invariants hold.
  1 - One or more governance violations detected.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.modules.popperian_governance import run_popperian_governance_audit


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify strategy tier governance and Popperian falsification invariants."
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress verbose output unless errors occur"
    )
    parser.add_argument(
        "--report", type=Path, default=None, help="Custom path to empirical study markdown report"
    )
    args = parser.parse_args()

    audit_kwargs = {}
    if args.report:
        audit_kwargs["report_path"] = args.report

    result = run_popperian_governance_audit(**audit_kwargs)

    if not args.quiet or not result.passed:
        print("=" * 70)
        print("🏛️  POPPERIAN STRATEGY GOVERNANCE QUALITY GATE")
        print("=" * 70)
        print(result.summary())
        print("=" * 70)

    if not result.passed:
        print("\n❌ CI/CD QUALITY GATE REJECTED: Strategy governance invariants violated!", file=sys.stderr)
        return 1

    if not args.quiet:
        print("\n✅ CI/CD QUALITY GATE PASSED: All strategy tiers & Popperian invariants satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
