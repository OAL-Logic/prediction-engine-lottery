# System Overview: Lottery Engine Architecture

The Lottery Engine is a distributed, multi-language system designed for high-performance lottery analysis and ticket generation. It balances empirical statistical rigor ("Nerd Mode") with esoteric/chaotic exploration ("Chaos Mode").

## 🏗️ The Multi-Part Architecture

### 1. The Analytical Engine (Python 3.11+)
The heart of the system. It handles all data processing, statistical modeling, and strategy execution.
- **CLI**: Built with `Typer` and `Rich`. Isolated commands in `engine/cli/commands/` ensure sub-second startup via strict lazy loading.
- **Sidecar API**: A `FastAPI` instance providing REST access to the engine's intelligence.
- **Intelligence Narrative**: A generative layer (`engine/modules/narrative.py`) that synthesizes data into persona-driven daily briefings.
- **Optimization Layer**: Includes Kelly Criterion bankroll management and combinatorial wheeling systems.
- **Strategy Layer**: 50+ strategies inheriting from `BaseStrategy`, utilizing temperature-based sampling and structural harmony filters.
- **Data Layer**: Hybrid storage using partitioned JSON files (`draw_log.jsonl`) and a SQLite index (`lottery.db`). Includes a `/model_cache` for pre-trained ML models.

### 2. The API Gateway (Go 1.23+)
A high-performance proxy written in Go to handle high-concurrency requests and provide a security/throttling layer.
- **Routing**: Uses `go-chi` for lightweight, idiomatic routing.
- **Middleware**: Implements rate limiting (`httprate`), request deadlining, and caching.
- **Bridge**: Proxies requests to the Python sidecar while propagating timeouts and headers.

### 3. The Universal Synapse App (Expo/React Native)
A cross-platform (Web, Android, iOS) frontend that implements the "Nerd Mode" and "Chaos Mode" interfaces.
- **Aesthetic**: A high-fidelity "Terminal" look using monospaced typography, character-grid layouts, and ASCII-inspired borders.
- **State-as-Narrative**: Streams internal process logs (e.g., `[LOAD]`, `[SCAN]`) during analysis to provide user feedback.

## 🧠 Core Intelligence Patterns

### Strategy Pattern & Temperature Sampling
Strategies do not simply "pick numbers." They assign a 0–1 score to every number in the pool. The `BaseStrategy.suggest` method then uses **Temperature Sampling**:
- **T=0**: Deterministic. Picks the highest-scoring numbers.
- **T=1**: Proportional. Picks numbers based on their relative scores.
- **T>1**: Chaotic. Increases exploration and randomness.

### Structural Harmony (The Filters)
Before a ticket is returned, it must pass through a "Harmony Gate" consisting of 30+ filters (e.g., Sum Range, Parity Balance, Decade Breadth).
- **K-of-N Logic**: Tickets can be required to satisfy at least K of N active filters, allowing for "fuzzy" structural integrity.

### Environmental Jitter & Muon Flux
Chaos Mode incorporates environmental factors:
- **Atmospheric Muon Flux**: Simulated single-event upsets (bit flips) that mutate ticket numbers with a small probability.
- **Chaos Tempering**: Modulates $T$ based on seismic, solar, and lunar environmental data.

## 🔄 Data Flow
1. **Fetch**: Adapters (`engine/adapters/`) download data from official sources (e.g., Caixa Econômica, Powerball API).
2. **Log**: Data is saved to `draw_log.jsonl` and indexed in `lottery.db`.
3. **Analyze**: Modules (`engine/modules/`) compute frequencies, sum ranges, and patterns.
4. **Suggest**: Strategies combine analysis into scores and sample tickets via the Harmony Gate.
5. **Present**: Results are returned to the CLI or the Synapse App.
