# Lottery Engine

A statistical analysis engine and ticket suggestion tool for lottery draws. It distinguishes itself by passing every prediction through a **chi² fairness gate**—distinguishing sober quantitative analysis ("Nerd Mode") from intentional, esoteric "Absurdity Engine" strategies ("Chaos Mode").

## 🎯 The Philosophy

*   **Nerd Mode (Statistical):** Quantitative analysis (frequency, gap, correlation) and backtest infrastructure for those who want to think about the lottery like a quant.
*   **Chaos Mode (Esoteric):** An "Absurdity Engine" using kabbalistic numerology, moon phases, and simulated quantum signals.
*   **The Integrity Moat:** Unlike paid "prediction" services, this engine clearly labels heuristic outputs. If historical draws are statistically indistinguishable from uniform randomness (via chi² p-value), the engine declares itself a tool for **intentional seeding**, not guaranteed winning.

---

## 🚀 Quick Start (The Golden Path)

The project includes a zero-config launcher (`./lottery`) that automatically handles environment setup. Alternatively, you can use the `lottery` command directly after installation.

```bash
# 1. Run the full daily diagnostic pipeline (Recommended)
./lottery daily mega-sena

# 2. Start the interactive setup and analysis wizard
./lottery wizard
```

## 🏗️ Commands Overview

Use `lottery <command>` for a seamless experience.

- `lottery daily <lottery>`: Full 5-stage diagnostic & suggestion pipeline.
- `lottery scan <lottery>`: Run a 6-layer GO/NO-GO condition check.
- `lottery fetch <lottery>`: Download historical draws.
- `lottery board <lottery> --view heatmap`: Visualize the physical grid.
- `lottery forecast <lottery>`: Weighted ensemble consensus ticket.
- `lottery suggest <lottery>`: Manual/Direct strategy suggestion.
- `lottery check <lottery> "nums"`: Audit a ticket's structural health.

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.11+** installed.

### 2. Clone and Environment
```bash
# Clone the repository
git clone https://github.com/your-repo/lottery-engine
cd lottery-engine

# Create and activate a virtual environment (Recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install the Engine
Install in "editable" mode so that changes to the code are reflected immediately in the CLI:

```bash
pip install -e .
```

On Windows, you can also use:

```bash
.venv/bin/pip install -e .
```

**Optional extras:**
*   `pip install -e ".[ml]"` — Adds `scikit-learn` and `lightgbm` for ML strategies.
*   `pip install -e ".[deep]"` — Adds `torch` for Deep Learning (Transformer/LSTM) strategies.
*   `pip install -e ".[all]"` — Installs everything.

### 4. Verify Installation
```bash
lottery --help
```
*Note: If the `lottery` command is not in your path, you can use `python3 -m engine.cli.main` instead.*

## 🛠️ CLI Workflow

### 1. Fetch & Update Data
Ensure you have the latest historical data before running any analysis.
```bash
lottery fetch mega-sena
```

### 2. The Daily Digest (Recommended)
The most robust way to use the engine. It runs regime detection, condition scanning, and ensemble forecasting in one go.
```bash
lottery daily mega-sena
```

### 3. Condition Scan (GO/NO-GO)
Check if the current lottery state is statistically "detectable" or purely random before playing.
```bash
lottery scan mega-sena
```

### 4. Direct Suggestion (Manual Mode)
Generate tickets using specific strategy tiers. Pass multiple strategies for an **automatic voting ensemble**.
```bash
# Nerd Mode: Weighted frequency + Bayesian posterior
lottery suggest mega-sena --strategy weighted,bayesian --count 5

# Chaos Mode: Kabbalistic seeding based on your name/birthdate
lottery suggest mega-sena --strategy kabbalistic --full-name "Your Name" --birth-date 1990-01-01
```

### 4. Backtesting & Optimization
Evaluate performance against real history. The engine "time travels" to a past draw and tests if the strategy would have caught the winners.
```bash
# Backtest 'weighted' on draw 2990
lottery backtest mega-sena 2990 --strategy weighted

# Grid-search the best (strategy, history_limit, temp) combo over the last 20 draws
lottery optimize mega-sena --strategies all --prev 1-20
```

---

## 🧠 Strategy Tiers

| Tier                 | Strategies                                                                                                      |
| :------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **Statistical**      | `markov`, `bayesian`, `weighted`, `monte_carlo`, `pattern`, `momentum`, `spectral`, `streak`, `crowd_avoidance` |
| **Machine Learning** | `logistic`, `random_forest`, `gradient_boost`, `knn`                                                            |
| **Deep Learning**    | `transformer`, `lstm_gru`, `cnn_1d`                                                                             |
| **Esoteric (Fun)**   | `numerology`, `kabbalistic`, `iching`, `moon_phase`, `weather`, `zodiac`, `solar`, `ley_lines`, `sefirot`       |

---

## 📖 Documentation

Detailed guides and specifications are available in the `docs/` folder:
- `docs/USER_GUIDE.md` — Detailed guide for the "Chaos Mode" / esoteric features.
- `docs/TECHNICAL_SPEC.md` — Mathematical formulas and logic behind each strategy.
- `docs/versions/` — Historical feature-batch notes.

For in-CLI help, use:
```bash
lottery docs [topic]
```

---

## 🗺️ Roadmap

The authoritative roadmap is maintained in `SPRINT_PLAN.md`. 

- ✅ **Sprint 1 (Completed):** Core Engine, 8 CLI commands, 23+ strategies.
- ✅ **Sprint 1.3:** Absurdity Engine (Kabbalistic, I Ching, Solar, etc.).
- ✅ **Sprint 1.4:** In-engine Balanced Wheel filters (Resampling/Parity).
- ⏳ **Sprint 2 (In Progress):** FastAPI Sidecar, `lottery check`, and expanded `analyze` modules.
- ⏳ **Sprint 3:** Go Gateway + Global Game Registry (150+ lotteries).
- ⏳ **Sprint 4:** Mobile UI (Expo) for Nerd and Chaos modes.

---

## 🧪 Testing
```bash
pytest
```

## ⚠️ Disclaimer
This tool is for statistical exploration and entertainment. A fair lottery consists of independent random events; no algorithm can escape that. Play for fun, and gamble responsibly.

## 📄 License
MIT
