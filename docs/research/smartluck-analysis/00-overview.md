---
title: Smart Luck Article — Analysis Overview
sources: https://smartluck.com/3-winning-lotto-methods.htm
date: 2026-04-25
project: Prediction Engine
status: review-needed
---

# Smart Luck → Prediction Engine — Analysis Overview

This folder contains a multi-expert evaluation of three Smart Luck pages
(Gail Howard's lotto methods) and what — if anything — is worth pulling
into the Prediction Engine roadmap.

## Files in this analysis

| File | Purpose |
|------|---------|
| `00-overview.md` | This document. Top-level summary. |
| `01-ideas-evaluation.md` | Idea-by-idea analysis with three experts. |
| `02-sum-ranges-data.md` | Cleaned lookup tables (most-probable range of sums) for pick-4/5/6/7/12. |
| `03-mapping-to-code.md` | Where each idea fits inside the current `lottery-engine/` tree. |
| `04-proposed-additions.md` | Concrete sprint-level additions, ranked. |

## TL;DR

The article's **three "methods"** are: game selection, number selection
(handicapping), and balanced wheels. Around them sits the **70% Most
Probable Range of Sums** rule and several auxiliary heuristics.

What the engine **already has**:

- Hot / cold + chi-squared (`frequency.py`)
- Gap / overdue with explicit "fair lottery → independent draws" disclaimer (`deviation.py`)
- Sum / odd-even / high-low / consecutive envelope via percentile sampling (`strategies/statistical/pattern.py`)

What is **genuinely new and worth adding**:

1. **Sum-range module** — analytical (truncated-normal) lookup, replaces
   the empirical percentile pass in `pattern.py`. Faster + more correct.
2. **Wheels module** (`engine/wheels/`) — full wheels and covering
   designs. Smart Luck sells this; we give it away. Top OSS magnet.
3. **Anti-Popular strategy** (`strategies/popularity.py`) — score combos
   by how *unlike* a typical human pick they are. Maximizes expected
   prize share, not P(win).
4. **Game-Selector / odds comparator** (`engine/odds/`) — rank every
   adapter by jackpot odds and friction. Becomes the Expo onboarding step.
5. **Combo Audit API** — paste numbers, get back: statistical-envelope
   fit + popularity score + sum-range bucket.

What we should **explicitly NOT do**:

- Never sell "due numbers" or hot/cold as predictive without gating on a
  significant chi-squared p-value. That's the gambler's fallacy and it's
  the line between us and Smart Luck.

## Integrity Moat

The Smart Luck copy contradicts itself: it warns against the
"due numbers" fallacy in one paragraph and sells handicapping based on
that fallacy in the next. Our positioning is the opposite — we expose
the math, gate predictions on tests of statistical significance, and
distinguish *expected-value* claims (real) from *P(win)* claims (mostly
fake). That's marketable as engineering integrity.
