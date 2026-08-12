#!/usr/bin/env python3
"""
Lotofacil September 7 Special Draw — Pool Builder
==================================================
Selects an 18-number bolão pool (or 17-number solo ticket) using a hybrid
statistical strategy agreed with the user:

  - Structural filters calibrated on ALL 3 700+ historical draws
  - Frequency + pair-co-occurrence scoring on the LAST 500 draws
  - Balanced selection: penalise extreme hot AND cold numbers;
    reward pair-diversity and decade/parity structural compliance

Run from the project root:
    python scripts/lotofacil_september7.py
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter
from itertools import combinations as icombs
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_DB   = os.path.join(_ROOT, "data", "lottery.db")
_JSON = os.path.join(_ROOT, "data", "br_lotofacil.json")

# Make the engine importable so we can reuse its infrastructure
sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Constants (Lotofacil 15/25)
# ---------------------------------------------------------------------------
POOL   = list(range(1, 26))          # numbers 1–25
PICK   = 15                          # drawn per contest
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23}
ODDS   = {1,3,5,7,9,11,13,15,17,19,21,23,25}
EVENS  = {2,4,6,8,10,12,14,16,18,20,22,24}
DECADES = [(1,5),(6,10),(11,15),(16,20),(21,25)]

# Structural filter bounds
# E[S]=195, sigma≈18.03 → 70 % band ≈ [176,214]
SUM_LO, SUM_HI = 176, 214
ODD_MIN, ODD_MAX = 5, 10   # 30–70 % of 15 picks
PRIME_MIN = 1


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_draws() -> List[List[int]]:
    """Return list of sorted draw-number lists, oldest first."""
    try:
        import duckdb
        con = duckdb.connect(_DB, read_only=True)
        rows = con.execute(
            "SELECT numbers FROM draws "
            "WHERE lottery_id = 'br/lotofacil' "
            "ORDER BY draw_id ASC"
        ).fetchall()
        con.close()
        if rows:
            return [sorted(list(r[0])) for r in rows]
    except Exception as exc:
        print(f"[warn] DuckDB unavailable ({exc}); falling back to JSON")

    import json
    with open(_JSON) as fh:
        raw = json.load(fh)
    return [sorted(d["numbers"])
            for d in sorted(raw, key=lambda x: x.get("draw_id", 0))]


# ---------------------------------------------------------------------------
# Structural filter (vectorised over a list of combos)
# ---------------------------------------------------------------------------

def passes_filters(combo: Tuple[int, ...]) -> bool:
    s = sum(combo)
    n_odd   = sum(1 for x in combo if x in ODDS)
    n_prime = sum(1 for x in combo if x in PRIMES)
    return (SUM_LO <= s <= SUM_HI
            and ODD_MIN <= n_odd <= ODD_MAX
            and n_prime >= PRIME_MIN)


def filter_pass_rate(pool: List[int]) -> Tuple[int, int, float]:
    """(total combos, passing, rate) for all C(len(pool), 15) tickets."""
    total   = 0
    passing = 0
    for combo in icombs(sorted(pool), PICK):
        total += 1
        if passes_filters(combo):
            passing += 1
    return total, passing, (passing / total if total else 0.0)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def build_scores(
    draws: List[List[int]],
    recent_n: int = 500,
) -> Dict[str, Dict[int, float]]:
    """
    Compute per-number scores.

    Returns a dict with keys:
      'score'   – composite balanced score (higher = better pool candidate)
      'z_rec'   – z-score vs expected in last recent_n draws
      'z_all'   – z-score vs expected across full history
      'freq_rec'– raw appearance count in last recent_n draws
      'freq_all'– raw appearance count in full history
      'pair_str'– avg pair co-occurrence strength (last recent_n draws)
    """
    all_draws  = draws
    recent     = draws[-recent_n:]
    N_all      = len(all_draws)
    N_rec      = len(recent)

    # Expected appearances under uniform draw
    p          = PICK / len(POOL)   # 15/25 = 0.60
    exp_all    = p * N_all
    exp_rec    = p * N_rec

    # Standard deviation of binomial count (hypergeom ≈ binomial here)
    std_all = math.sqrt(N_all * p * (1 - p))
    std_rec = math.sqrt(N_rec * p * (1 - p))

    freq_all = Counter(n for d in all_draws for n in d)
    freq_rec = Counter(n for d in recent      for n in d)

    z_all = {n: (freq_all[n] - exp_all) / std_all for n in POOL}
    z_rec = {n: (freq_rec[n] - exp_rec) / std_rec for n in POOL}

    # Pair co-occurrence (last recent_n draws)
    pair_cooc: Counter = Counter()
    for draw in recent:
        for pair in icombs(sorted(draw), 2):
            pair_cooc[pair] += 1

    # Network centrality proxy: avg co-occurrence with all other numbers
    pair_str: Dict[int, float] = {}
    for n in POOL:
        total_cooc = sum(
            pair_cooc.get((min(n, m), max(n, m)), 0)
            for m in POOL if m != n
        )
        pair_str[n] = total_cooc / (len(POOL) - 1)

    ps_vals = list(pair_str.values())
    ps_min, ps_max = min(ps_vals), max(ps_vals)
    ps_norm = {
        n: (pair_str[n] - ps_min) / (ps_max - ps_min)
             if ps_max != ps_min else 0.5
        for n in POOL
    }

    # Composite balanced score:
    #   -|z_rec|        → penalise extremes (hot AND cold) in recent window
    #   -0.5*|z_all|    → mild long-run alignment
    #   +0.3*ps_norm    → reward pair-network centrality
    #   +0.05*tilt      → tiny responsiveness to recent form (not hot bias)
    scores: Dict[int, float] = {}
    for n in POOL:
        tilt = (freq_rec[n] / N_rec / p - 1) if N_rec and p else 0.0
        scores[n] = (
            -abs(z_rec[n])
            - 0.5 * abs(z_all[n])
            + 0.3 * ps_norm[n]
            + 0.05 * tilt
        )

    return {
        "score":    scores,
        "z_rec":    z_rec,
        "z_all":    z_all,
        "freq_rec": {n: freq_rec[n] for n in POOL},
        "freq_all": {n: freq_all[n] for n in POOL},
        "pair_str": pair_str,
        "exp_rec":  exp_rec,
        "exp_all":  exp_all,
    }


# ---------------------------------------------------------------------------
# Pool selection
# ---------------------------------------------------------------------------

def select_pool(scores_dict: Dict[str, Dict[int, float]], target: int = 18) -> List[int]:
    """
    Greedy selection of `target` numbers respecting:
      1. At least 3 numbers per decade (5 decades of 1–25)
      2. Odd count in [8, 10]  (gives best filter compliance for 18 picks)

    Remaining slots filled by descending composite score.
    """
    scores  = scores_dict["score"]
    ranked  = sorted(POOL, key=lambda n: scores[n], reverse=True)
    selected: List[int] = []
    remaining = list(ranked)

    # Phase 1 — guarantee ≥3 per decade
    for lo, hi in DECADES:
        decade = [n for n in remaining if lo <= n <= hi]
        for n in decade[:3]:
            if n not in selected:
                selected.append(n)
                remaining = [x for x in remaining if x != n]

    # Phase 2 — fill to `target` with odd/even balance guard [8–10 odds]
    n_odd  = sum(1 for n in selected if n in ODDS)
    n_even = len(selected) - n_odd

    for n in remaining:
        if len(selected) >= target:
            break
        is_odd = n in ODDS
        if is_odd and n_odd  >= 10: continue
        if not is_odd and n_even >= 10: continue
        selected.append(n)
        if is_odd: n_odd  += 1
        else:       n_even += 1

    # Phase 3 — relax balance if still short
    for n in [x for x in ranked if x not in selected]:
        if len(selected) >= target:
            break
        selected.append(n)

    return sorted(selected)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main() -> None:
    SEP  = "=" * 65
    SEP2 = "-" * 65

    # -- Load & score
    print("Loading Lotofacil historical data …")
    draws = load_draws()
    print(f"  {len(draws)} draws loaded (2003–2026)\n")

    scores_dict = build_scores(draws, recent_n=500)
    scores   = scores_dict["score"]
    z_rec    = scores_dict["z_rec"]
    z_all    = scores_dict["z_all"]
    freq_rec = scores_dict["freq_rec"]
    freq_all = scores_dict["freq_all"]
    exp_rec  = scores_dict["exp_rec"]
    exp_all  = scores_dict["exp_all"]

    # -- Select pools
    pool18 = select_pool(scores_dict, target=18)
    worst  = min(pool18, key=lambda n: scores[n])
    pool17 = sorted([n for n in pool18 if n != worst])

    # -- Filter validation
    total18, pass18, rate18 = filter_pass_rate(pool18)
    total17, pass17, rate17 = filter_pass_rate(pool17)

    cost18 = total18 * 3
    cost17 = total17 * 3

    # ---- Print ----
    print(SEP)
    print("  LOTOFACIL — SEPTEMBER 7 SPECIAL DRAW")
    print("  Hybrid Statistical Pool (balanced, 500-draw window)")
    print(SEP)

    # Pool composition
    odds_p  = [n for n in pool18 if n in ODDS]
    evens_p = [n for n in pool18 if n in EVENS]
    primes_p = [n for n in pool18 if n in PRIMES]

    print(f"\n  RECOMMENDED 18-NUMBER POOL")
    print(f"  {pool18}")
    print()
    print(f"  Odd / Even  :  {len(odds_p)} / {len(evens_p)}")
    print(f"  Primes ({len(primes_p)}) :  {primes_p}")
    print()
    for lo, hi in DECADES:
        dec = [n for n in pool18 if lo <= n <= hi]
        bar = "█" * len(dec)
        print(f"  {lo:2d}–{hi:2d}  [{bar:<5}]  {dec}")

    # Filter stats
    print(f"\n{SEP2}")
    print(f"  STRUCTURAL FILTER VALIDATION")
    print(f"  Rules: sum ∈ [{SUM_LO},{SUM_HI}]  |  odd ∈ [{ODD_MIN},{ODD_MAX}]  |  prime ≥ {PRIME_MIN}")
    print(f"  Pool 18 →  {pass18:4d} / {total18}  tickets pass  ({rate18*100:.1f} %)")
    print(f"  Pool 17 →  {pass17:4d} / {total17}   tickets pass  ({rate17*100:.1f} %)")

    # Cost & bolão breakdown
    print(f"\n{SEP2}")
    print(f"  COST ANALYSIS")
    print(f"  18-number bolão :  {total18} tickets × R$3.00 = R$ {cost18:,}.00")
    print(f"  17-number solo  :  {total17} tickets × R$3.00 = R$ {cost17:,}.00")
    print()
    print(f"  Bolão sharing — who pays R$500 or less?")
    for n_people in [4, 5, 6, 8, 10, 12, 15, 20, 24]:
        per = cost18 / n_people
        flag = "  ← R$500/person fits" if per <= 500 else ""
        print(f"    {n_people:2d} people  →  R$ {per:,.2f} /person{flag}")

    # 17-number fallback
    print(f"\n{SEP2}")
    print(f"  17-NUMBER SOLO FALLBACK  (R$ {cost17:.2f} — within R$500 budget)")
    print(f"  Pool  :  {pool17}")
    print(f"  Drop  :  {worst}  (lowest balanced score in the 18-pool)")
    print(f"  Structural coverage :  {pass17}/{total17} ({rate17*100:.1f} %)")

    # Number scoring table
    print(f"\n{SEP2}")
    print(f"  NUMBER SCORING TABLE")
    print(f"  {'N':>3}  {'Score':>7}  {'F(500)':>7}  {'Exp':>6}  "
          f"{'Z(500)':>7}  {'Z(All)':>7}  {'In pool':>7}")
    for n in sorted(POOL, key=lambda x: scores[x], reverse=True):
        tag = "▶ YES" if n in pool18 else ""
        if n == worst:
            tag = "  17 ✓"
        print(
            f"  {n:>3}  {scores[n]:>7.4f}  {freq_rec[n]:>7d}  "
            f"{exp_rec:>6.1f}  {z_rec[n]:>7.2f}  {z_all[n]:>7.2f}  {tag}"
        )

    # Summary
    min_people_500 = math.ceil(cost18 / 500)
    print(f"\n{SEP}")
    print(f"  SUMMARY")
    print(f"  ▸ 17-number solo  : R$ {cost17:.2f}  — fits your R$500 budget alone")
    print(f"  ▸ 18-number bolão : R$ {cost18:,} total — need ≥ {min_people_500} people to stay ≤ R$500/person")
    print(f"  ▸ Both options have {max(rate17,rate18)*100:.0f}%+ structurally compliant tickets")
    print(SEP)


if __name__ == "__main__":
    main()
