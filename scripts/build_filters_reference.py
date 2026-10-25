#!/usr/bin/env python3
"""
Build Complete Filter Reference Encyclopedia 🛡️
================================================
Generates docs/filters/LOTTERY_FILTERS_REFERENCE.md containing ASCII diagrams,
Mermaid flowcharts, mathematical formulations, and dynamic evaluations for all
99 filters across Tiers 1-5.
"""

from pathlib import Path
from engine.adapters import DrawRules
from engine.modules.filters import registry

OUT_FILE = Path(__file__).resolve().parent.parent / "docs" / "filters" / "LOTTERY_FILTERS_REFERENCE.md"

RULES_MEGA = DrawRules(name="Mega-Sena", pick_count=6, number_range=(1, 60))
SAMPLE_TICKET = [4, 11, 23, 35, 48, 59]

TIER_NAMES = {
    1: "Structural & Parity Filters",
    2: "Positional, Gaps & Dispersion Filters",
    3: "Algebraic, Modular & Digit Sum Filters",
    4: "Historical, Empirical & Co-occurrence Filters",
    5: "Custom, Spatial & Graph-Theoretic Filters",
}

def main():
    registry._discover()
    lines = []

    total_count = len(registry._module_map)
    lines.append("# Lottery Engine: Comprehensive Mathematical Filter Reference 🛡️\n")
    lines.append("> A definitive mathematical guide, architecture specification, visual diagram collection,")
    lines.append(f"> and dynamic evaluation manual for all {total_count} filters implemented across the **5-Tier Consolidated")
    lines.append("> Vectorized Harmony Gate** and the **Harmony Scalar Engine**.\n")
    lines.append("---\n")

    # Section 1: Executive Architecture
    lines.append("## 1. Executive Architecture & Filter Philosophy\n")
    lines.append("The core purpose of the Lottery Engine's filtering subsystem is **combinatorial search space distillation**.")
    lines.append("For example, Mega-Sena represents a search space of $\\binom{60}{6} = 50,063,860$ combinations.")
    lines.append("While every individual combination has equal prior probability under physical uniform randomness,")
    lines.append("the **macroscopic attributes** of drawn tickets follow tightly bound combinatorial distributions")
    lines.append("(hypergeometric, Gaussian approximations, and modular congruence classes). Combinations exhibiting extreme")
    lines.append("clustering—such as consecutive streaks, all-odd balls, or narrow spreads—fall in asymptotic tails ($p < 10^{-6}$)")
    lines.append("and historically fail to appear across thousands of contests.\n")

    lines.append("### Pipeline Architecture Overview\n")
    lines.append("```mermaid")
    lines.append("graph TD")
    lines.append('    Pool["Combinatorial Ticket Candidates"] --> Bridge["Bi-Directional Registry Bridge & Alias Resolver"]')
    lines.append('    Bridge --> T1["Tier 1: Structural Gates (Parity, Prime, AC Value)"]')
    lines.append('    T1 --> T2["Tier 2: Positional & Dispersion (Spans, MAD, Gaps)"]')
    lines.append('    T2 --> T3["Tier 3: Algebraic & Modular (Sums, Digital Roots, Div-by-N)"]')
    lines.append('    T3 --> T4["Tier 4: Historical & Patterns (Dual-Mode Adaptive Bounds)"]')
    lines.append('    T4 --> T5["Tier 5: Custom & Graph (Lockers, Anti-Pairs, Partitions)"]')
    lines.append('    T5 --> KofN{"K-of-N Relaxation Decider"}')
    lines.append('    KofN -->|100% Passes| PrimePool["Accepted Candidate Tickets"]')
    lines.append('    KofN -->|Attempts > 50% & Not Strict| Degrade["Gradual K-of-N Relaxation (N-1, N-2)"]')
    lines.append('    Degrade --> Warn["CLI Warning & Metadata Audit Entry"]')
    lines.append('    Warn --> PrimePool')
    lines.append('    KofN -->|Attempts > Max & --strict-filters| Abort["Abort: ValueError Exception"]')
    lines.append("```\n")

    lines.append("### End-to-End Pipeline ASCII Box-Flow\n")
    lines.append("```text")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("|                            CANDIDATE GENERATION ENGINE                            |")
    lines.append("|                  (Weighted Softmax / Entropy Temperature Sampling)                |")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("                                          |")
    lines.append("                                          v  [Candidate Ticket (x_1, ..., x_k)]")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("|                        BI-DIRECTIONAL HARMONY BRIDGE GATE                         |")
    lines.append("|   Maps Aliases ('parity', 'spread', 'sum_range') <--> 5 Vectorized Tiers (1..5)   |")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("                                          |")
    lines.append("        +---------------------------------+---------------------------------+")
    lines.append("        |                                 |                                 |")
    lines.append("        v                                 v                                 v")
    lines.append("+------------------+             +------------------+             +------------------+")
    lines.append("|  TIER 1 & 2      |             |  TIER 3          |             |  TIER 4 & 5      |")
    lines.append("|  Parity, Bounds, |             |  Modular, Roots, |             |  Empirical Skips,|")
    lines.append("|  AC Complexity   |             |  Hypergeometric  |             |  Co-occurrences  |")
    lines.append("+------------------+             +------------------+             +------------------+")
    lines.append("        |                                 |                                 |")
    lines.append("        +---------------------------------+---------------------------------+")
    lines.append("                                          |  [Filter Pass/Fail Vector]")
    lines.append("                                          v")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("|                      GRADUAL K-OF-N FAULT TOLERANCE DECIDER                       |")
    lines.append("|   Attempts <= 50% max  :  Enforce strict K = N                                    |")
    lines.append("|   Attempts <= 75% max  :  Relax to K = max(1, N - 1)  [If not --strict-filters]   |")
    lines.append("|   Attempts >  75% max  :  Relax to K = max(1, N - 2)  [If not --strict-filters]   |")
    lines.append("+-----------------------------------------------------------------------------------+")
    lines.append("                     |                                         |")
    lines.append("     [Meets K threshold]                        [Fails under --strict-filters]")
    lines.append("                     v                                         v")
    lines.append("+--------------------------------------+     +--------------------------------------+")
    lines.append("|  ACCEPTED PREDICTION TICKET          |     |  SYSTEM ABORT / EXCEPTION            |")
    lines.append("|  - Injects metadata audit            |     |  - Preserves exact user constraints  |")
    lines.append("|  - Emits clear CLI warning if relaxed|     |  - Explains starvation cause         |")
    lines.append("+--------------------------------------+     +--------------------------------------+")
    lines.append("```\n")

    lines.append("### Dual-Mode Game-Adaptive Decision Tree\n")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append('    Rules["DrawRules Input (N, k)"] --> HistCheck{"Historical Draw Context Present?"}')
    lines.append('    HistCheck -->|">= 20 Historical Draws"| Empirical["Empirical Quantile Mode"]')
    lines.append('    Empirical --> Quantiles["Compute 2.5% - 97.5% Historical Quantiles (mu +/- 2.5 sigma_hist)"]')
    lines.append('    HistCheck -->|"Cold Start / Synthetic Vector"| Hypergeometric["Analytical Hypergeometric Fallback"]')
    lines.append('    Hypergeometric --> ClosedForm["Evaluate Discrete Uniform Moments without Replacement"]')
    lines.append('    ClosedForm --> Moments["mu = k(lo + hi)/2, sigma^2 = [k(N-k)/(N-1)] * [(N^2 - 1)/12]"]')
    lines.append('    Quantiles --> AdaptiveBounds["Dynamic Parameter Envelope [min_val .. max_val]"]')
    lines.append('    Moments --> AdaptiveBounds')
    lines.append('    AdaptiveBounds --> Evaluate["Vectorized Evaluation over Combinations"]')
    lines.append("```\n")

    lines.append("---\n")

    # Loop through each tier and write every filter
    for tier_num in range(1, 6):
        tier_title = TIER_NAMES[tier_num]
        filters = sorted(registry.list_by_tier(tier_num), key=lambda x: x.unique_id)
        lines.append(f"## {tier_num + 1}. Tier {tier_num}: {tier_title} ({len(filters)} Filters)\n")
        
        for idx, f in enumerate(filters, 1):
            doc = f.generate_documentation(RULES_MEGA, SAMPLE_TICKET)
            # Retitle from H3 to include number
            lines.append(f"#### {tier_num}.{idx} `{f.unique_id}` — {f.display_name}")
            lines.append(f"- **Tier**: Tier {f.tier} ({f.category})")
            lines.append(f"- **Description**: {f.description}")
            if f.formula:
                lines.append(f"- **Mathematical Formulation**: `{f.formula}`")
            if f.diagram:
                lines.append("\n```text")
                lines.append(f.diagram)
                lines.append("```")
            if f.mermaid:
                lines.append("\n```mermaid")
                lines.append(f.mermaid)
                lines.append("```")
            
            exp = f.explain(SAMPLE_TICKET, RULES_MEGA)
            lines.append(f"\n**Dynamic Evaluation Example** (Ticket: `{SAMPLE_TICKET}`):")
            lines.append(f"- **Verdict**: `{'PASS' if exp.passed else 'FAIL'}`")
            lines.append(f"- **Metric Value**: `{exp.actual_value}` (Allowed Range: `{exp.allowed_range}`)")
            lines.append(f"- **Gauge**: `{exp.gauge}`")
            lines.append(f"- **Summary**: {exp.summary}\n")
            lines.append("---\n")

    # Section 7: CLI Usage
    lines.append("## 7. CLI Usage & Interactive Filter Inspection\n")
    lines.append("Users can interact with the filter catalog and dynamically test any ticket using the CLI:\n")
    lines.append("```bash")
    lines.append("# 1. View Full Catalog")
    lines.append("lottery docs filters")
    lines.append("lottery docs filters --tier 1\n")
    lines.append("# 2. Inspect a Specific Filter with Diagrams & Dynamic Gauge")
    lines.append("lottery docs --filter structural_odd_count --ticket 5,12,23,34,45,56")
    lines.append("lottery docs --filter historical_ac_range --ticket 4,11,23,35,48,59\n")
    lines.append("# 3. Run Filter Elimination Funnel with Inspection")
    lines.append("lottery filter-funnel br/mega-sena --info structural_odd_count")
    lines.append("lottery filter-funnel br/mega-sena --pool 1,2,3,4,5,6,7,8,9,10,11,12 --filters parity,spread,historical_ac_range\n")
    lines.append("# 4. Interactive Filter Assistant Wizard")
    lines.append("lottery filter-assistant br/mega-sena")
    lines.append("```\n")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    OUT_FILE.write_text(content, encoding="utf-8")
    print(f"Successfully generated {OUT_FILE} with {len(lines)} lines covering all {total_count} filters.")

if __name__ == "__main__":
    main()
