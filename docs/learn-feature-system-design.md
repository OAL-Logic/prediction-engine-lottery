# System Design: "Learn While You Build" — Prediction Engine

**Date:** April 30, 2026  
**Status:** Draft — Early Prototype Phase  
**Author:** Operator D

---

## 1. What we're building

A **Codecademy-for-algo-trading** learning module embedded inside the Prediction Engine. The target user is a developer or quant who can already write Python — but has no idea what RSI means, why a Sharpe ratio matters, or when to apply a momentum filter. They're not lost because they can't code. They're lost because the domain is opaque.

The feature needs to give them the **conceptual foundation** to use the app confidently, through a learning experience that feels like exploration, not a textbook. Think: split-screen code editor, live backtest feedback, and an AI tutor they can ask anything — all woven together with a badge system that rewards curiosity.

**The core loop:**
> Concept explained simply → Try it in the live sandbox → See real backtest results → Earn a badge → Want to go deeper

---

## 2. Requirements

### Functional

- Structured learning curriculum with progressive modules (Beginner → Intermediate → Advanced)
- Live Python sandbox where users write and run real strategy code with instant feedback
- AI tutor that answers questions in context of what the user is currently working on
- Contextual tooltips and "explain this" triggers throughout the main app UI
- Badge system that awards cosmetic achievements as users complete lessons and milestones
- User progress tracking across sessions (which lessons done, which badges earned)
- Ability to save sandbox work and continue later

### Non-functional

- Sandbox code execution must be isolated and safe — no access to host system, network-limited
- AI tutor response latency should feel conversational (< 3 seconds)
- Learning content must be maintainable by a solo developer (no CMS overkill)
- The system should work at low scale initially (< 1,000 users) and not over-engineer for thousands

### Constraints

- Python backend (FastAPI recommended)
- Solo developer building this — complexity budget is real
- Early prototype stage — ship a working v1, not a perfect system
- Monetization TBD — design should not lock in a specific business model

---

## 3. High-level architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Next.js)                │
│                                                             │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Main App UI │  │  Learn Section   │  │  AI Tutor    │  │
│  │  (tooltips,  │  │  (curriculum,    │  │  (sidebar    │  │
│  │   "explain   │  │   progress,      │  │   chat,      │  │
│  │    this")    │  │   badges)        │  │   context-   │  │
│  └──────┬───────┘  └────────┬─────────┘  │   aware)     │  │
│         │                   │            └──────┬───────┘  │
└─────────┼───────────────────┼───────────────────┼──────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API  (FastAPI / Python)            │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │  Sandbox    │  │  Learning    │  │  AI Tutor          │ │
│  │  Execution  │  │  Service     │  │  Service           │ │
│  │  Service    │  │  (progress,  │  │  (Claude API +     │ │
│  │  (Docker)   │  │   badges,    │  │   context inject)  │ │
│  │             │  │   content)   │  │                    │ │
│  └──────┬──────┘  └──────┬───────┘  └────────┬───────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          ▼                ▼                    ▼
    ┌──────────┐    ┌─────────────┐    ┌────────────────┐
    │ Docker   │    │  PostgreSQL  │    │  Claude API    │
    │ Sandbox  │    │  (progress, │    │  (Anthropic)   │
    │ (pyodide │    │   badges,   │    │                │
    │  or      │    │   users)    │    └────────────────┘
    │  docker) │    └─────────────┘
    └──────────┘
```

### Data flow for the core learning loop

1. User opens a lesson → Frontend fetches lesson content from Learning Service
2. User reads explanation, opens sandbox editor with pre-filled starter code
3. User writes/modifies strategy → Frontend sends code to Sandbox Execution Service
4. Sandbox runs the code in isolation → Returns backtest results (JSON)
5. Frontend renders results alongside the lesson panel
6. User asks AI tutor a question → AI Tutor Service injects current lesson context + user's code → Calls Claude API → Streams response
7. User completes lesson → Learning Service updates progress, checks badge conditions, awards badge
8. Badge shown with animation → Stored in user profile

---

## 4. Component deep-dives

### 4.1 Curriculum structure

Content is stored as **markdown files in the repo** — not a database. This keeps it editable, versionable, and zero-CMS-overhead for a solo developer. Each lesson is a folder with a `lesson.md` and an optional `starter.py`.

```
content/
  curriculum/
    01-signals-and-indicators/
      01-what-is-rsi/
        lesson.md          ← explanation, Feynman-style
        starter.py         ← pre-filled code in sandbox
        solution.py        ← reference answer
        quiz.json          ← 2-3 multiple choice questions
      02-macd-explained/
      03-bollinger-bands/
    02-your-first-strategy/
      01-combining-signals/
      02-setting-entry-exit/
    03-filters-and-parameters/
      01-volume-filters/
      02-time-of-day-filters/
    04-reading-backtest-results/
      01-sharpe-ratio/
      02-max-drawdown/
      03-win-rate-vs-expectancy/
    05-ml-feature-engineering/
      01-turning-indicators-into-features/
      02-feature-correlation/
```

`lesson.md` frontmatter + structure:

```markdown
---
title: "What is RSI?"
module: 1
lesson: 1
estimated_minutes: 8
badge_on_complete: signal_seeker
---

## The simple version

Imagine you're watching a rubber band stretch. RSI tells you:
"how stretched is this rubber band right now?"

When a stock goes up a lot very fast, RSI goes high (above 70).
When it drops hard, RSI goes low (below 30). The idea: rubber bands
snap back. RSI above 70 → might be time to sell. RSI below 30 →
might be time to buy.

## Try it

The code on the right calculates RSI for AAPL. Change the `period`
value from 14 to 7 — see how the signal becomes more sensitive?

## Quick check

[quiz]
```

### 4.2 Sandbox execution service

This is the highest-risk component technically. Python code from untrusted users must run safely.

**v1 approach: Pyodide in the browser**
Run Python entirely in the browser via WebAssembly. Zero server risk, zero Docker complexity. Trade-off: slower startup, limited library support (ta-lib won't work natively). Good enough for v1 learning exercises with pandas + numpy.

**v2 approach: Docker-per-execution with resource limits**

```python
# sandbox/executor.py

import docker, json, uuid, tempfile

client = docker.from_env()

def execute_strategy(code: str, timeout_seconds: int = 10) -> dict:
    execution_id = str(uuid.uuid4())
    wrapped_code = HARNESS_TEMPLATE.format(user_code=code)
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(wrapped_code)
        script_path = f.name
    
    try:
        output = client.containers.run(
            image="prediction-engine-sandbox:latest",
            command="python /code/strategy.py",
            volumes={script_path: {"bind": "/code/strategy.py", "mode": "ro"}},
            mem_limit="128m",
            cpu_quota=50000,        # 50% of 1 CPU
            network_mode="none",    # no internet access
            read_only=True,
            remove=True,
            timeout=timeout_seconds,
        )
        return json.loads(output.decode("utf-8"))
    except docker.errors.ContainerError as e:
        return {"error": e.stderr.decode("utf-8"), "success": False}
```

The sandbox image pre-installs: `pandas`, `numpy`, `ta-lib`, `scikit-learn`. No network, no file writes outside `/tmp`.

**Decision:** Ship v1 with Pyodide. Migrate to Docker in v2 when users need full ta-lib performance.

### 4.3 AI tutor service

The tutor is context-aware: it knows which lesson the user is on, what code they've written, and what error they got.

```python
# api/routers/tutor.py

from anthropic import Anthropic
from fastapi.responses import StreamingResponse

client = Anthropic()

SYSTEM_PROMPT = """
You are the AI tutor for Prediction Engine, an algorithmic trading platform.
You're talking to a developer who knows Python but is learning trading concepts.

Explain concepts using plain language and analogies — no jargon without explanation.
Guide discovery with questions rather than dumping info. If user code has an error,
help them understand WHY it fails, not just fix it.

Current context:
- Lesson: {lesson_title} (Module {module}, Lesson {lesson})
- User's current code:
{user_code}
- Last execution result: {last_result}
"""

@router.post("/tutor/ask")
async def ask_tutor(question: str, ctx: LessonContext, code: str, result: dict):
    system = SYSTEM_PROMPT.format(
        lesson_title=ctx.title, module=ctx.module, lesson=ctx.lesson,
        user_code=code or "(no code yet)",
        last_result=result or "(not run yet)",
    )
    def stream():
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": question}],
        ) as s:
            for text in s.text_stream:
                yield f"data: {text}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")
```

**Model choice:** Claude Haiku for tutor chat (fast, cheap, excellent for Q&A). Haiku at ~10 questions/user/day across 100 active users ≈ ~$2–5/day.

### 4.4 Badge system

Badges are cosmetic only but should feel meaningful — they're awarded on specific trigger conditions evaluated server-side after any relevant event.

**Badge definitions** (`content/badges.json`):

```json
[
  { "id": "signal_seeker",   "name": "Signal Seeker",    "icon": "📡", "description": "Completed your first indicator lesson",          "condition": { "type": "lesson_complete", "lesson_id": "01-01" } },
  { "id": "first_backtest",  "name": "First Blood",      "icon": "⚡", "description": "Ran your first backtest in the sandbox",          "condition": { "type": "sandbox_runs", "count": 1 } },
  { "id": "strategy_rookie", "name": "Strategy Rookie",  "icon": "🧪", "description": "Completed the Your First Strategy module",        "condition": { "type": "module_complete", "module_id": "02" } },
  { "id": "filter_master",   "name": "Filter Master",    "icon": "🔬", "description": "Applied 3+ filters to a single strategy",         "condition": { "type": "filters_applied", "count": 3 } },
  { "id": "sharpe_hunter",   "name": "Sharpe Hunter",    "icon": "🎯", "description": "Achieved a Sharpe ratio above 1.5 in a backtest", "condition": { "type": "backtest_metric", "metric": "sharpe_ratio", "threshold": 1.5 } },
  { "id": "curious_mind",    "name": "Curious Mind",     "icon": "🧠", "description": "Asked the AI tutor 10 questions",                 "condition": { "type": "tutor_questions", "count": 10 } },
  { "id": "full_quant",      "name": "Full Stack Quant", "icon": "🏆", "description": "Completed all 5 modules",                         "condition": { "type": "all_modules_complete" } }
]
```

Badge evaluation is a simple function called after every trigger event — no rules engine needed at this scale.

### 4.5 Contextual tooltips in the main app

Every indicator, filter, and parameter in the main app UI gets a `?` button. Clicking it shows a compact popover with a plain-language 2-sentence explanation and a link to the full lesson.

These live in `content/glossary.json`:

```json
{
  "rsi": {
    "short": "Measures how overbought or oversold an asset is. Think rubber band — RSI above 70 means stretched up, below 30 means stretched down.",
    "lesson_link": "01-01"
  },
  "sharpe_ratio": {
    "short": "Your return divided by your risk. A Sharpe of 1.0 means you earned 1 unit of return per unit of risk taken — higher is better.",
    "lesson_link": "04-01"
  },
  "max_drawdown": {
    "short": "The biggest drop from a peak to a trough during the backtest period. It tells you the worst pain a strategy could have caused.",
    "lesson_link": "04-02"
  }
}
```

---

## 5. Data model

```sql
-- Learning progress
user_progress (
  id           UUID PRIMARY KEY,
  user_id      UUID REFERENCES users(id),
  lesson_id    TEXT,           -- e.g. "01-01"
  module_id    TEXT,           -- e.g. "01"
  status       TEXT CHECK (status IN ('not_started','in_progress','complete')),
  started_at   TIMESTAMP,
  completed_at TIMESTAMP,
  UNIQUE(user_id, lesson_id)
)

-- Sandbox sessions (saved per user per lesson)
sandbox_sessions (
  id           UUID PRIMARY KEY,
  user_id      UUID REFERENCES users(id),
  lesson_id    TEXT,
  code         TEXT,
  last_result  JSONB,
  runs_count   INT DEFAULT 0,
  updated_at   TIMESTAMP,
  UNIQUE(user_id, lesson_id)
)

-- Badges
user_badges (
  user_id      UUID REFERENCES users(id),
  badge_id     TEXT,           -- matches badges.json id
  earned_at    TIMESTAMP,
  PRIMARY KEY (user_id, badge_id)
)

-- Tutor questions (for badge counting + future analytics)
tutor_sessions (
  id           UUID PRIMARY KEY,
  user_id      UUID REFERENCES users(id),
  lesson_id    TEXT,
  question     TEXT,
  created_at   TIMESTAMP
)
```

---

## 6. API design

```
# Curriculum
GET  /api/learn/curriculum                → all modules + lessons + user progress
GET  /api/learn/lessons/{lesson_id}       → lesson content + starter code
POST /api/learn/lessons/{lesson_id}/complete  → mark done, trigger badge check → returns any new badges

# Sandbox
POST /api/sandbox/run                     → { code, lesson_id } → backtest results
GET  /api/sandbox/{lesson_id}             → saved code + last result for this user
PUT  /api/sandbox/{lesson_id}             → save code draft

# AI Tutor
POST /api/tutor/ask                       → { question, lesson_context, code, last_result }
                                             → SSE stream of tutor response

# Badges
GET  /api/badges                          → all badge definitions + earned status
GET  /api/badges/mine                     → current user's earned badges + timestamps

# Glossary (contextual tooltips)
GET  /api/glossary/{term}                 → short description + lesson_link
```

---

## 7. Tech stack recommendation

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | React + Next.js | App Router, SSR, massive ecosystem |
| Code editor | Monaco Editor | VS Code's engine — syntax highlighting, familiar to developers |
| Python sandbox v1 | Pyodide (browser WASM) | Zero server risk, ships in days |
| Python sandbox v2 | Docker + FastAPI | Full library support (ta-lib), proper isolation |
| Backend | FastAPI (Python) | Already your stack, async, fast to build |
| Database | PostgreSQL | Reliable, queryable progress data |
| AI tutor | Anthropic Claude API — Haiku model | Fast, cheap, excellent for conversational Q&A |
| Content | Markdown files in repo | No CMS needed, fully versionable, solo-developer-friendly |
| Auth | Supabase Auth | Don't build auth from scratch |
| Hosting | Railway or Render | Simple, Python-friendly, affordable at early scale |

---

## 8. Frontend layout — the learn screen

```
┌──────────────────────────────────────────────────────────────────┐
│  LEARN > Module 1 > What is RSI?                   [Progress 1/5]│
├────────────────────────┬─────────────────────────────────────────┤
│                        │  ┌──────────────────────────────────── ┐│
│  LESSON PANEL          │  │  strategy.py                    ▶  ││
│                        │  │────────────────────────────────────││
│  What is RSI?          │  │  import pandas as pd               ││
│                        │  │  import ta                         ││
│  Think of it like a    │  │                                    ││
│  rubber band. When a   │  │  def strategy(df):                 ││
│  stock shoots up very  │  │    df['rsi'] = ta.momentum         ││
│  fast, RSI goes high   │  │      .RSIIndicator(                ││
│  (>70). When it drops  │  │        df['close'],                ││
│  hard, RSI goes low    │  │        window=14  # try 7!         ││
│  (<30).                │  │      ).rsi()                       ││
│                        │  │    return df                       ││
│  Try it: change        │  └────────────────────────────────────┘│
│  window=14 to window=7 │  ┌────────────────────────────────────┐│
│  and re-run. Notice    │  │  BACKTEST RESULTS                  ││
│  how the signal fires  │  │  Sharpe: 0.82   Drawdown: -14.2%  ││
│  more often?           │  │  Win rate: 54%  Trades: 47         ││
│                        │  │  [equity curve chart]              ││
│  ──────────────────    │  └────────────────────────────────────┘│
│  Quick check:          │  ┌────────────────────────────────────┐│
│  [2-question quiz]     │  │  🤖 AI TUTOR                       ││
│                        │  │  You: what does window=14 mean?    ││
│  ──────────────────    │  │                                    ││
│  [Complete Lesson ✓]   │  │  Tutor: The window is how many     ││
│                        │  │  candles RSI looks back to calc... ││
└────────────────────────┴──┴────────────────────────────────────┘
```

---

## 9. Phased roadmap

### Phase 1 — Foundation (2–3 weeks)

Ship and validate the core learning loop. Nothing more.

- 5 lessons in Module 1 (Signals & Indicators) — RSI, MACD, Bollinger Bands, momentum, volume
- Pyodide sandbox with 3 pre-built backtest starter scripts
- Badge awards on lesson complete and first sandbox run
- AI tutor (single Q&A, no conversation history)
- PostgreSQL progress tracking (lessons + badges)

Skip: glossary tooltips in main app, conversation history, all modules 2–5, leaderboards.

### Phase 2 — Depth (3–4 weeks after v1)

- Complete Modules 2 and 3 (First Strategy, Filters & Parameters)
- Replace Pyodide with Docker sandbox for full Python library support
- AI tutor gets multi-turn conversation history
- Glossary `?` tooltips wired into the main app's indicator/filter UI
- Badge animation on award + profile page with badge showcase

### Phase 3 — Polish & monetization signal (ongoing)

- Complete Modules 4 and 5
- Drop-off analytics: identify which lessons kill engagement
- Consider gating Modules 4–5 behind a paid tier as a monetization signal test
- Community profile sharing (show off badges)

---

## 10. Trade-offs to revisit as you grow

**Markdown content vs. database-backed CMS:** Markdown is fast to ship and easy to edit solo. It becomes painful if you want A/B testing, non-developer content editors, or adaptive learning paths. Revisit if curriculum exceeds 30+ lessons.

**Pyodide vs. Docker sandbox:** Pyodide can't run ta-lib or heavy pandas operations at full speed. Fine for teaching exercises. The moment users want to test real strategies on real market data, switch to Docker.

**Cosmetic-only badges:** Right design for v1. If retention data later shows engagement dropping after users collect all badges, revisit adding meaningful unlocks — e.g., earning "Filter Master" could unlock an advanced filter panel in the main app.

**AI tutor cost:** At 500 active users asking 10 questions/day with Haiku — roughly $5–20/day. Monitor from day one and add rate limiting (e.g., 20 free questions/day) before it becomes painful.

**Solo scope:** Phase 1 is 2–3 weeks. Phase 2 is another 3–4 weeks. Do not start Phase 2 before validating that real users complete at least 3 lessons in Phase 1.

---

## 11. The one insight that makes or breaks this feature

The learning feature succeeds only if the sandbox gives **real, immediate feedback** — not toy fake data. A developer who earns "Signal Seeker" by reading a prebuilt chart is not the same as one who changed `window=14` to `window=7`, hit run, and watched the Sharpe ratio drop. The second person is hooked.

**Build the sandbox first. The curriculum is secondary.**
