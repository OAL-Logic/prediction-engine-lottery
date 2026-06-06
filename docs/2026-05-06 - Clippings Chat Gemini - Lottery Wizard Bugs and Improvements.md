---
title: Lottery Wizard Bugs and Improvements
sources:
  - https://gemini.google.com/app/80499a9bc77cc38f
types:
  - "[[Resource]]"
categories:
  - "[[Clippings]]"
  - "[[Chat Gemini]]"
handles:
published:
created: 2026-05-06T15:14:30-03:00
description: Gemini conversation with 2 messages
tags:
  - libraries/clippings/chats/gemini
---
# Lottery Wizard Bugs and Improvements

saved: 2026-05-06T15-14-30

## User Message

You said

analyze and create a series of tasks to fix the issues and also find improvements to make in the docs or implementation

  

it may consider adding more info about the missing or question in the wizard

  

  

❯ lottery wizard

╭───────────────────────────────────────────╮

│ Lottery Engine Wizard                     │

│ Follow the steps to guide your next move. │

╰───────────────────────────────────────────╯

0\. What do you want to do? \[suggest/wheel/backtest\] (suggest): suggest

                      Available Lotteries

  Index    ID                  Name               Format

      1    br/mega-sena        ● Mega-Sena        6/60

      2    br/lotofacil        ● Lotofácil        15/25

      3    us/powerball        ● Powerball        5/69 + 1/26

      4    us/mega-millions    ○ Mega Millions    5/70 + 1/25

      5    eu/euro-millions    ○ EuroMillions     5/50 + 2/12

  

Select a lottery for suggestions (1-5) (1): 2

1.5 Do you want to play a Multiple Bet?

   (e.g. play more than 15 numbers in one ticket) \[yes/no\] (no): no

2\. Select strategy group \[statistical/chaos/fun/ml/deep/all/custom\] (statistical): all

╭─────────────────────────────────── Traceback (most recent call last) ────────────────────────────────────╮

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/wizard.py:167 in       │

│ wizard                                                                                                   │

│                                                                                                          │

│   164 │   │   try:                                                                                       │

│   165 │   │   │   strat\_cls = \_REGISTRY.get(name)                                                        │

│   166 │   │   │   if not strat\_cls:                                                                      │

│ ❱ 167 │   │   │   │   strat\_objects.append(get\_strategy(name))                                           │

│   168 │   │   │   │   strat\_configs.append({})                                                           │

│   169 │   │   │   │   continue                                                                           │

│   170                                                                                                    │

│                                                                                                          │

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/strategies/\_\_init\_\_.py:627 in       │

│ get\_strategy                                                                                             │

│                                                                                                          │

│   624 │                                                                                                  │

│   625 │   if name not in \_REGISTRY:                                                                      │

│   626 │   │   available = ", ".join(sorted(\_REGISTRY))                                                   │

│ ❱ 627 │   │   raise KeyError(f"Unknown strategy {name!r}. Available: {available}")                       │

│   628 │                                                                                                  │

│   629 │   cls = \_REGISTRY\[name\]                                                                          │

│   630                                                                                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

KeyError: "Unknown strategy 'weighted'. Available: biorhythm, entropy\_global, fibonacci, gematria, iching,

kabbalistic, ley\_lines, lorentz, moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot,

seismic, sentiment, solar, vix\_jitter, weather, zodiac"

  

During handling of the above exception, another exception occurred:

  

╭─────────────────────────────────── Traceback (most recent call last) ────────────────────────────────────╮

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/cli/commands/wizard.py:244 in       │

│ wizard                                                                                                   │

│                                                                                                          │

│   241 │   │   │   │   strat\_objects.append(get\_strategy(name, \*\*kwargs))                                 │

│   242 │   │   │   │   strat\_configs.append({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k,  │

│       v in kwargs.items()})                                                                              │

│   243 │   │   except Exception as exc:                                                                   │

│ ❱ 244 │   │   │   strat\_objects.append(get\_strategy(name))                                               │

│   245 │   │   │   strat\_configs.append({})                                                               │

│   246 │                                                                                                  │

│   247 │   # 3. Settings                                                                                  │

│                                                                                                          │

│ /mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction                                          │

│ Engine/lottery/.gemini/worktrees/2026-04-29-02-45-06-737-l63k/engine/strategies/\_\_init\_\_.py:627 in       │

│ get\_strategy                                                                                             │

│                                                                                                          │

│   624 │                                                                                                  │

│   625 │   if name not in \_REGISTRY:                                                                      │

│   626 │   │   available = ", ".join(sorted(\_REGISTRY))                                                   │

│ ❱ 627 │   │   raise KeyError(f"Unknown strategy {name!r}. Available: {available}")                       │

│   628 │                                                                                                  │

│   629 │   cls = \_REGISTRY\[name\]                                                                          │

│   630                                                                                                    │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

KeyError: "Unknown strategy 'weighted'. Available: biorhythm, entropy\_global, fibonacci, gematria, iching,

kabbalistic, ley\_lines, lorentz, moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot,

seismic, sentiment, solar, vix\_jitter, weather, zodiac"

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !2

❯ lottery wizard

╭───────────────────────────────────────────╮

│ Lottery Engine Wizard                     │

│ Follow the steps to guide your next move. │

╰───────────────────────────────────────────╯

0\. What do you want to do? \[suggest/wheel/backtest\] (suggest): suggest

                      Available Lotteries

  Index    ID                  Name               Format

      1    br/mega-sena        ● Mega-Sena        6/60

      2    br/lotofacil        ● Lotofácil        15/25

      3    us/powerball        ● Powerball        5/69 + 1/26

      4    us/mega-millions    ○ Mega Millions    5/70 + 1/25

      5    eu/euro-millions    ○ EuroMillions     5/50 + 2/12

  

Select a lottery for suggestions (1-5) (1): 1

1.5 Do you want to play a Multiple Bet?

   (e.g. play more than 6 numbers in one ticket) \[yes/no\] (no): no

2\. Select strategy group \[statistical/chaos/fun/ml/deep/all/custom\] (statistical): custom

  Available: biorhythm, entropy\_global, fibonacci, gematria, iching, kabbalistic, ley\_lines, lorentz,

moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot, seismic, sentiment, solar,

vix\_jitter, weather, zodiac

   Enter strategy name(s) (comma-separated) (weighted): biorhythm, entropy\_global, fibonacci, gematria, iching, kabbalistic, ley\_lines, lorentz, moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot, seismic, sentiment, solar, vix\_jitter, weather, zodiac

  

Settings for biorhythm:

   Customize parameters for biorhythm? \[yes/no\] (no): yes

     Personal birthday. If not provided, a universal epoch (2000-01-01) is used, producing a "universal

biorhythm".

     birth\_date (YYYY-MM-DD): 1900-01-01

     Upcoming Draw Date. The date to score for.

     draw\_date (YYYY-MM-DD):

     Historical data blend. Blend with historical draws that shared similar biorhythm phase states.

     use\_history (True):

     Critical day score. Extra score for numbers whose domain is at a cycle crossing point (high

instability/luck).

     critical\_bonus (0.2): 0.2

  

Settings for entropy\_global:

   Customize parameters for entropy\_global? \[yes/no\] (no): yes

     volatility\_weight (1.0): 1.0

  

Settings for fibonacci:

   Customize parameters for fibonacci? \[yes/no\] (no): yes

     Golden ratio tolerance. How close a ratio must be to φ to count as a golden-ratio pair. 0.05 = within

5% of φ.

     phi\_tolerance (0.05):

     Historical data blend. If True, numbers that appeared often historically get a boost. Keeps the

sequence grounded in data.

     use\_history (True):

  

Settings for gematria:

   Customize parameters for gematria? \[yes/no\] (no): yes

     language (en): en

  

Settings for iching:

   Customize parameters for iching? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD):

  

Settings for kabbalistic:

   Customize parameters for kabbalistic? \[yes/no\] (no): yes

     Full birth name for Kabbalistic calculations.

     full\_name (GEMINI ENGINE): Operator D

     Birthday for Destiny and cycle calculations.

     birth\_date (YYYY-MM-DD) (1990-01-01): 1900-01-01

     Target draw date.

     draw\_date (YYYY-MM-DD):

     Blend with historical data matching Kabbalistic vibrations.

     use\_history (True):

     Optional contextual topic (Universal Gematria).

     topic ():

  

Settings for ley\_lines:

   Customize parameters for ley\_lines? \[yes/no\] (no): yes

     latitude:

     longitude:

  

Settings for lorentz:

   Customize parameters for lorentz? \[yes/no\] (no): yes

     sigma (10.0):

     rho (28.0):

     beta (2.6666666666666665):

  

Settings for moon\_phase:

   Customize parameters for moon\_phase? \[yes/no\] (no): yes

     upcoming\_draw\_date (YYYY-MM-DD):

  

Settings for noosphere:

   Customize parameters for noosphere? \[yes/no\] (no): ye

Please select one of the available options

   Customize parameters for noosphere? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD):

  

Settings for numerology:

   Customize parameters for numerology? \[yes/no\] (no): yes

     Historical data blend. If True, numbers that appeared on matching historical dates get a boost. Keeps

the mysticism grounded in data.

     use\_history (True):

     Draw date. The day the lottery occurs. Used to calculate the "Universal Day" energy that affects

everyone playing on that date.

     target\_date (YYYY-MM-DD):

     Personal birthday. Unlocks your unique "Life Path" number, making the prediction specific to your own

numerical essence.

     birth\_date (YYYY-MM-DD): 1900-01-01

     Personal vibration. If True, computes your unique energy specifically for the draw date. Highly

recommended for the most personalized result.

     use\_personal\_day (True): True

  

Settings for refraction:

   Customize parameters for refraction? \[yes/no\] (no): yes

     args:

     kwargs:

  

Settings for reincarnation:

   Customize parameters for reincarnation? \[yes/no\] (no): yes

     How selective the matching is. Higher = only very close matches.

     sensitivity (1.0):

  

Settings for sefirot:

   Customize parameters for sefirot? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD):

  

Settings for seismic:

   Customize parameters for seismic? \[yes/no\] (no): yes

     args:

     kwargs:

  

Settings for sentiment:

   Customize parameters for sentiment? \[yes/no\] (no): yes

     A keyword or phrase to seed the sentiment simulation.

     topic (lottery):

     'follow' (boost popular) or 'avoid' (penalize popular).

     mode (follow):

  

Settings for solar:

   Customize parameters for solar? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD):

     timeout (10.0):

  

Settings for vix\_jitter:

   Customize parameters for vix\_jitter? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD):

     kwargs:

  

Settings for weather:

   Customize parameters for weather? \[yes/no\] (no): yes

     Location search (e.g. Sao Paulo, Brazil) (Sao Paulo, Brazil):

     Regional data source. Used to pick default coordinates if none provided.

     country\_hint (br): br

     Draw date. Used to fetch the forecast for the day of the lottery.

     upcoming\_draw\_date (YYYY-MM-DD):

     API patience. How long to wait for the weather server to respond in seconds.

     timeout (15.0):

  

Settings for zodiac:

   Customize parameters for zodiac? \[yes/no\] (no): yes

     Upcoming Draw Date. The date to score for, determining the active Western zodiac sign.

     draw\_date (YYYY-MM-DD):

3\. Number of tickets per strategy (1): 1

4\. Sampling temperature (0=top picks, 1=balanced) (1.0): 0.1

5\. History Limit (Recency bias: draws to look at, or 'none') (100): 500

6\. Draw Date (Alias for date-dependent strategies, YYYY-MM-DD or 'none') (none): 2026-05-05

  

🚀 Launching customized analysis for br/mega-sena...

  

  Checking for new megasena draws…

  Cache is up to date (Draw 3003).

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching SUGGESTION ENGINE                                                                              │

│   Lottery:  Mega-Sena (br/mega-sena)                                                                     │

│   Strategies:  \['biorhythm', 'entropy\_global', 'fibonacci', 'gematria', 'iching', 'kabbalistic',         │

│ 'ley\_lines', 'lorentz', 'moon\_phase', 'noosphere', 'numerology', 'refraction', 'reincarnation',          │

│ 'sefirot', 'seismic', 'sentiment', 'solar', 'vix\_jitter', 'weather', 'zodiac'\]                           │

│   Temp:  0.1                                                                                             │

│   Limit:  500                                                                                            │

│   Pick:  6                                                                                               │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

BIORHYTHM  confidence=0.481 (48.1%)

  Parameters: birth\_date=1900-01-01, draw\_date=2026-05-05, use\_history=True, critical\_bonus=0.2

  Ticket 1: \[2, 8, 26, 31, 49, 58\]  (sum=174)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[1, 7, 40, 43, 22, 46, 31, 8\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ENTROPY\_GLOBAL  confidence=0.526 (52.6%)

  Ticket 1: \[2, 11, 25, 32, 42, 51\]  (sum=163)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[1, 21, 25, 32, 46, 54, 27, 2\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

FIBONACCI  confidence=0.364 (36.4%)

  Parameters: phi\_tolerance=0.05, use\_history=True

  Ticket 1: \[1, 2, 6, 8, 10, 21\]  (sum=48)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[1, 55, 2, 5, 3, 8, 21, 34\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

GEMATRIA  confidence=0.330 (33.0%)

  Parameters: language=en

  Ticket 1: \[1, 2, 19, 28, 38, 39\]  (sum=127)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[1, 2, 19, 30, 36, 38, 8, 17\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ICHING  confidence=0.142 (14.2%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[4, 8, 16, 20, 32, 39\]  (sum=119)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[4, 58, 20, 40, 5, 25, 45, 16\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

KABBALISTIC  confidence=0.588 (58.8%)

  Parameters: full\_name=Operator D, birth\_date=1900-01-01, draw\_date=2026-05-05,

use\_history=True, topic=

  Ticket 1: \[10, 14, 22, 27, 46, 55\]  (sum=174)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[15, 34, 50, 30, 14, 33, 55, 56\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

LEY\_LINES  confidence=0.378 (37.8%)

  Parameters: latitude=None, longitude=None

  Ticket 1: \[9, 12, 24, 33, 39, 51\]  (sum=168)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[3, 6, 9, 12, 15, 18, 21, 24\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Strategy failed: can't multiply sequence by non-int of type 'numpy.float64'

  

MOON\_PHASE  confidence=0.253 (25.2%)

  Parameters: upcoming\_draw\_date=2026-05-05

  Ticket 1: \[5, 24, 27, 30, 34, 36\]  (sum=156)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[15, 34, 5, 17, 27, 55, 60, 6\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

NOOSPHERE  confidence=0.543 (54.3%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[6, 22, 32, 33, 36, 52\]  (sum=181)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[7, 16, 46, 55, 28, 44, 36, 14\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

NUMEROLOGY  confidence=0.400 (40.0%)

  Parameters: use\_history=True, target\_date=2026-05-05, birth\_date=1900-01-01, use\_personal\_day=True

  Ticket 1: \[8, 33, 38, 47, 50, 52\]  (sum=228)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[15, 33, 34, 52, 51, 35, 50, 8\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

REFRACTION  confidence=0.515 (51.5%)

  Ticket 1: \[32, 36, 43, 51, 53, 56\]  (sum=271)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[15, 27, 32, 46, 54, 8, 1, 5\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

REINCARNATION  confidence=0.356 (35.6%)

  Parameters: sensitivity=1.0

  Ticket 1: \[12, 21, 22, 51, 56, 58\]  (sum=220)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[10, 21, 32, 38, 51, 58, 11, 31\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SEFIROT  confidence=0.687 (68.7%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[13, 30, 36, 39, 50, 57\]  (sum=225)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[10, 33, 34, 35, 43, 44, 49, 50\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SEISMIC  confidence=0.554 (55.4%)

  Ticket 1: \[1, 2, 17, 30, 37, 54\]  (sum=141)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[10, 37, 38, 49, 54, 24, 55, 1\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SENTIMENT  confidence=0.135 (13.5%)

  Parameters: topic=lottery, mode=follow

  Ticket 1: \[3, 42, 43, 44, 48, 49\]  (sum=229)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[42, 44, 48, 49, 5, 3, 23, 43\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SOLAR  confidence=0.000 (0.0%)

  Parameters: draw\_date=2026-05-05, timeout=10.0

  Ticket 1: \[5, 6, 7, 11, 36, 49\]  (sum=114)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[1, 2, 3, 4, 5, 6, 7, 8\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

VIX\_JITTER  confidence=0.394 (39.4%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[2, 8, 10, 32, 38, 56\]  (sum=146)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[15, 46, 54, 27, 32, 5, 1, 60\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

WEATHER  confidence=0.521 (52.1%)

  Parameters: latitude=-23.5506507, longitude=-46.6333824, upcoming\_draw\_date=2026-05-05, timeout=15.0

  Ticket 1: \[1, 8, 16, 26, 27, 35\]  (sum=113)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[6, 15, 27, 24, 56, 8, 37, 50\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ZODIAC  confidence=0.301 (30.1%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[5, 13, 28, 46, 48, 53\]  (sum=193)

            Hist wins: match 4: 0 | match 5: 0 | match 6: 0

  Top scored: \[2, 24, 5, 6, 8, 23, 27, 4\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

──────────────────────────────────────────── CONSENSUS ANALYSIS ────────────────────────────────────────────

      2  █████░░░░░░░░░░  6 votes

      8  █████░░░░░░░░░░  6 votes

     32  ████░░░░░░░░░░░  5 votes

     36  ████░░░░░░░░░░░  5 votes

     51  ███░░░░░░░░░░░░  4 votes

      1  ███░░░░░░░░░░░░  4 votes

     39  ███░░░░░░░░░░░░  4 votes

     49  ██░░░░░░░░░░░░░  3 votes

      6  ██░░░░░░░░░░░░░  3 votes

     10  ██░░░░░░░░░░░░░  3 votes

  

───────────────────────────────────── LEARN — How to use these results ─────────────────────────────────────

  • Look for Convergence: Numbers that multiple strategies agree on.

  • Respect Harmony: The engine auto-filters for sum-range and parity balance.

  • Play Diversified: Use different strategy tiers (Statistical, ML, Esoteric).

  

⚠  Skipped: lorentz

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !2

❯ lottery wizard

╭───────────────────────────────────────────╮

│ Lottery Engine Wizard                     │

│ Follow the steps to guide your next move. │

╰───────────────────────────────────────────╯

0\. What do you want to do? \[suggest/wheel/backtest\] (suggest): suggest

                      Available Lotteries

  Index    ID                  Name               Format

      1    br/mega-sena        ● Mega-Sena        6/60

      2    br/lotofacil        ● Lotofácil        15/25

      3    us/powerball        ● Powerball        5/69 + 1/26

      4    us/mega-millions    ○ Mega Millions    5/70 + 1/25

      5    eu/euro-millions    ○ EuroMillions     5/50 + 2/12

  

Select a lottery for suggestions (1-5) (1): 2

1.5 Do you want to play a Multiple Bet?

   (e.g. play more than 15 numbers in one ticket) \[yes/no\] (no): no

2\. Select strategy group \[statistical/chaos/fun/ml/deep/all/custom\] (statistical): biorhythm, entropy\_global, fibonacci, gematria, iching, kabbalistic, ley\_lines, lorentz, moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot, seismic, sentiment, solar, vix\_jitter, weather, zodiac

Please select one of the available options

2\. Select strategy group \[statistical/chaos/fun/ml/deep/all/custom\] (statistical): custom

  Available: biorhythm, entropy\_global, fibonacci, gematria, iching, kabbalistic, ley\_lines, lorentz,

moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot, seismic, sentiment, solar,

vix\_jitter, weather, zodiac

   Enter strategy name(s) (comma-separated) (weighted): biorhythm, entropy\_global, fibonacci, gematria, iching, kabbalistic, ley\_lines, lorentz, moon\_phase, noosphere, numerology, refraction, reincarnation, sefirot, seismic, sentiment, solar, vix\_jitter, weather, zodiac

  

Settings for biorhythm:

   Customize parameters for biorhythm? \[yes/no\] (no): yes

     Personal birthday. If not provided, a universal epoch (2000-01-01) is used, producing a "universal

biorhythm".

     birth\_date (YYYY-MM-DD): 1900-01-01

     Upcoming Draw Date. The date to score for.

     draw\_date (YYYY-MM-DD): 2026-05-05

     Historical data blend. Blend with historical draws that shared similar biorhythm phase states.

     use\_history (True):

     Critical day score. Extra score for numbers whose domain is at a cycle crossing point (high

instability/luck).

     critical\_bonus (0.2):

  

Settings for entropy\_global:

   Customize parameters for entropy\_global? \[yes/no\] (no): yes

     volatility\_weight (1.0):

  

Settings for fibonacci:

   Customize parameters for fibonacci? \[yes/no\] (no): yes

     Golden ratio tolerance. How close a ratio must be to φ to count as a golden-ratio pair. 0.05 = within

5% of φ.

     phi\_tolerance (0.05):

     Historical data blend. If True, numbers that appeared often historically get a boost. Keeps the

sequence grounded in data.

     use\_history (True):

  

Settings for gematria:

   Customize parameters for gematria? \[yes/no\] (no): yes

     language (en):

  

Settings for iching:

   Customize parameters for iching? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD): 2026-05-05

  

Settings for kabbalistic:

   Customize parameters for kabbalistic? \[yes/no\] (no): yes

     Full birth name for Kabbalistic calculations.

     full\_name (GEMINI ENGINE): Operator D

     Birthday for Destiny and cycle calculations.

     birth\_date (YYYY-MM-DD) (1990-01-01): 1900-01-01

     Target draw date.

     draw\_date (YYYY-MM-DD): 2026-05-05

     Blend with historical data matching Kabbalistic vibrations.

     use\_history (True):

     Optional contextual topic (Universal Gematria).

     topic ():

  

Settings for ley\_lines:

   Customize parameters for ley\_lines? \[yes/no\] (no): yes

     latitude:

     longitude:

  

Settings for lorentz:

   Customize parameters for lorentz? \[yes/no\] (no): yes

     sigma (10.0):

     rho (28.0):

     beta (2.6666666666666665):

  

Settings for moon\_phase:

   Customize parameters for moon\_phase? \[yes/no\] (no): yes

     upcoming\_draw\_date (YYYY-MM-DD): 2026-05-05

  

Settings for noosphere:

   Customize parameters for noosphere? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD): 2026-05-05

  

Settings for numerology:

   Customize parameters for numerology? \[yes/no\] (no): yes

     Historical data blend. If True, numbers that appeared on matching historical dates get a boost. Keeps

the mysticism grounded in data.

     use\_history (True):

     Draw date. The day the lottery occurs. Used to calculate the "Universal Day" energy that affects

everyone playing on that date.

     target\_date (YYYY-MM-DD): 2026-05-05

     Personal birthday. Unlocks your unique "Life Path" number, making the prediction specific to your own

numerical essence.

     birth\_date (YYYY-MM-DD): 1900-01-01

     Personal vibration. If True, computes your unique energy specifically for the draw date. Highly

recommended for the most personalized result.

     use\_personal\_day (True): True

  

Settings for refraction:

   Customize parameters for refraction? \[yes/no\] (no): yes

     args:

     kwargs:

  

Settings for reincarnation:

   Customize parameters for reincarnation? \[yes/no\] (no): yes

     How selective the matching is. Higher = only very close matches.

     sensitivity (1.0):

  

Settings for sefirot:

   Customize parameters for sefirot? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD): 2026-05-05

  

Settings for seismic:

   Customize parameters for seismic? \[yes/no\] (no): yes

     args:

     kwargs:

  

Settings for sentiment:

   Customize parameters for sentiment? \[yes/no\] (no): yes

     A keyword or phrase to seed the sentiment simulation.

     topic (lottery): Melancolical

     'follow' (boost popular) or 'avoid' (penalize popular).

     mode (follow): avoid

  

Settings for solar:

   Customize parameters for solar? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD): 2026-06-06

     timeout (10.0): 30

  

Settings for vix\_jitter:

   Customize parameters for vix\_jitter? \[yes/no\] (no): yes

     draw\_date (YYYY-MM-DD): 2026-05-05

     kwargs:

  

Settings for weather:

   Customize parameters for weather? \[yes/no\] (no):

  

Settings for zodiac:

   Customize parameters for zodiac? \[yes/no\] (no): yes

     Upcoming Draw Date. The date to score for, determining the active Western zodiac sign.

     draw\_date (YYYY-MM-DD): 2026-05-05

3\. Number of tickets per strategy (1): 1

4\. Sampling temperature (0=top picks, 1=balanced) (1.0): 0.15

5\. History Limit (Recency bias: draws to look at, or 'none') (100): 250

6\. Draw Date (Alias for date-dependent strategies, YYYY-MM-DD or 'none') (none): 2026-05-05

  

🚀 Launching customized analysis for br/lotofacil...

  

  Checking for new lotofacil draws…

  Cache is up to date (Draw 3676).

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮

│ Launching SUGGESTION ENGINE                                                                              │

│   Lottery:  Lotofácil (br/lotofacil)                                                                     │

│   Strategies:  \['biorhythm', 'entropy\_global', 'fibonacci', 'gematria', 'iching', 'kabbalistic',         │

│ 'ley\_lines', 'lorentz', 'moon\_phase', 'noosphere', 'numerology', 'refraction', 'reincarnation',          │

│ 'sefirot', 'seismic', 'sentiment', 'solar', 'vix\_jitter', 'weather', 'zodiac'\]                           │

│   Temp:  0.15                                                                                            │

│   Limit:  250                                                                                            │

│   Pick:  15                                                                                              │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

BIORHYTHM  confidence=0.543 (54.3%)

  Parameters: birth\_date=1900-01-01, draw\_date=2026-05-05, use\_history=True, critical\_bonus=0.2

  Ticket 1: \[1, 4, 5, 7, 8, 10, 13, 15, 16, 17, 19, 20, 22, 23, 25\]  (sum=205)

            Hist wins: match 11: 299 | match 12: 51 | match 13: 6 | match 14: 1 | match 15: 0

  Top scored: \[4, 13, 25, 1, 19, 22, 10, 7\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ENTROPY\_GLOBAL  confidence=0.510 (51.0%)

  Ticket 1: \[1, 3, 4, 6, 7, 8, 9, 12, 13, 14, 15, 16, 19, 22, 25\]  (sum=174)

            Hist wins: match 11: 304 | match 12: 60 | match 13: 6 | match 14: 0 | match 15: 0

  Top scored: \[20, 4, 14, 13, 19, 7, 8, 15\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

FIBONACCI  confidence=0.455 (45.5%)

  Parameters: phi\_tolerance=0.05, use\_history=True

  Ticket 1: \[1, 2, 3, 4, 5, 6, 8, 11, 12, 13, 19, 20, 21, 23, 25\]  (sum=173)

            Hist wins: match 11: 335 | match 12: 73 | match 13: 2 | match 14: 0 | match 15: 0

  Top scored: \[1, 2, 5, 21, 3, 8, 11, 12\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

GEMATRIA  confidence=0.375 (37.5%)

  Parameters: language=en

  Ticket 1: \[1, 2, 6, 8, 9, 10, 11, 14, 17, 18, 19, 20, 21, 22, 25\]  (sum=203)

            Hist wins: match 11: 343 | match 12: 59 | match 13: 4 | match 14: 0 | match 15: 0

  Top scored: \[1, 2, 19, 8, 17, 20, 25, 6\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ICHING  confidence=0.221 (22.1%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 22, 25\]  (sum=191)

            Hist wins: match 11: 318 | match 12: 73 | match 13: 5 | match 14: 0 | match 15: 0

  Top scored: \[8, 14, 20, 10, 15, 16, 4, 5\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

KABBALISTIC  confidence=0.663 (66.3%)

  Parameters: full\_name=Operator D, birth\_date=1900-01-01, draw\_date=2026-05-05,

use\_history=True, topic=

  Ticket 1: \[1, 3, 4, 5, 6, 9, 10, 11, 13, 16, 18, 19, 20, 21, 24\]  (sum=180)

            Hist wins: match 11: 359 | match 12: 66 | match 13: 8 | match 14: 0 | match 15: 0

  Top scored: \[21, 3, 24, 12, 10, 15, 2, 6\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

LEY\_LINES  confidence=0.374 (37.4%)

  Parameters: latitude=None, longitude=None

  Ticket 1: \[2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 21, 22, 24, 25\]  (sum=184)

            Hist wins: match 11: 332 | match 12: 66 | match 13: 8 | match 14: 0 | match 15: 0

  Top scored: \[3, 6, 9, 12, 15, 18, 21, 24\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Strategy failed: can't multiply sequence by non-int of type 'numpy.float64'

  

MOON\_PHASE  confidence=0.612 (61.2%)

  Parameters: upcoming\_draw\_date=2026-05-05

  Ticket 1: \[1, 3, 4, 5, 6, 7, 10, 11, 13, 15, 17, 19, 23, 24, 25\]  (sum=183)

            Hist wins: match 11: 359 | match 12: 62 | match 13: 5 | match 14: 0 | match 15: 0

  Top scored: \[1, 4, 5, 6, 19, 23, 24, 25\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

NOOSPHERE  confidence=0.593 (59.3%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[1, 3, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 20, 21, 25\]  (sum=185)

            Hist wins: match 11: 292 | match 12: 53 | match 13: 8 | match 14: 0 | match 15: 0

  Top scored: \[16, 11, 7, 14, 8, 6, 9, 12\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

NUMEROLOGY  confidence=0.450 (45.0%)

  Parameters: use\_history=True, target\_date=2026-05-05, birth\_date=1900-01-01, use\_personal\_day=True

  Ticket 1: \[2, 4, 6, 7, 9, 10, 11, 12, 15, 16, 18, 20, 21, 23, 25\]  (sum=199)

            Hist wins: match 11: 317 | match 12: 69 | match 13: 5 | match 14: 0 | match 15: 0

  Top scored: \[11, 16, 7, 15, 24, 25, 6, 4\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

REFRACTION  confidence=0.497 (49.7%)

  Ticket 1: \[2, 4, 5, 6, 7, 10, 11, 12, 14, 15, 17, 18, 20, 24, 25\]  (sum=190)

            Hist wins: match 11: 319 | match 12: 76 | match 13: 7 | match 14: 0 | match 15: 0

  Top scored: \[6, 15, 7, 12, 25, 5, 17, 14\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

REINCARNATION  confidence=0.738 (73.8%)

  Parameters: sensitivity=1.0

  Ticket 1: \[1, 4, 7, 8, 9, 10, 11, 12, 13, 16, 17, 20, 23, 24, 25\]  (sum=200)

            Hist wins: match 11: 328 | match 12: 73 | match 13: 6 | match 14: 0 | match 15: 0

  Top scored: \[1, 3, 5, 7, 9, 10, 11, 12\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SEFIROT  confidence=0.664 (66.4%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25\]  (sum=265)

            Hist wins: match 11: 339 | match 12: 68 | match 13: 6 | match 14: 0 | match 15: 0

  Top scored: \[10, 11, 12, 13, 14, 15, 16, 17\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SEISMIC  confidence=0.642 (64.2%)

  Ticket 1: \[1, 3, 4, 6, 10, 11, 13, 15, 17, 18, 20, 22, 23, 24, 25\]  (sum=212)

            Hist wins: match 11: 357 | match 12: 78 | match 13: 5 | match 14: 0 | match 15: 0

  Top scored: \[4, 5, 23, 25, 1, 2, 18, 22\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SENTIMENT  confidence=0.888 (88.8%)

  Parameters: topic=Melancolical, mode=avoid

  Ticket 1: \[1, 2, 3, 6, 8, 9, 14, 16, 17, 18, 20, 21, 23, 24, 25\]  (sum=207)

            Hist wins: match 11: 272 | match 12: 65 | match 13: 1 | match 14: 0 | match 15: 0

  Top scored: \[1, 3, 4, 6, 8, 9, 10, 11\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

SOLAR  confidence=0.648 (64.8%)

  Parameters: draw\_date=2026-05-05, timeout=30.0

  Ticket 1: \[4, 5, 6, 7, 9, 10, 12, 13, 15, 17, 19, 20, 21, 22, 23\]  (sum=203)

            Hist wins: match 11: 315 | match 12: 60 | match 13: 3 | match 14: 0 | match 15: 0

  Top scored: \[4, 6, 15, 16, 19, 21, 22, 23\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

VIX\_JITTER  confidence=0.625 (62.5%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[1, 2, 4, 6, 7, 8, 10, 12, 13, 15, 18, 20, 21, 23, 25\]  (sum=185)

            Hist wins: match 11: 340 | match 12: 56 | match 13: 4 | match 14: 0 | match 15: 0

  Top scored: \[1, 4, 25, 6, 15, 21, 23, 13\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

WEATHER  confidence=0.689 (68.9%)

  Parameters: latitude=-23.5505, longitude=-46.6333, upcoming\_draw\_date=2026-05-05, timeout=15.0

  Ticket 1: \[1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 15, 17, 21, 22, 25\]  (sum=165)

            Hist wins: match 11: 311 | match 12: 58 | match 13: 4 | match 14: 0 | match 15: 0

  Top scored: \[1, 4, 5, 15, 25, 22, 6, 7\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

ZODIAC  confidence=0.532 (53.2%)

  Parameters: draw\_date=2026-05-05

  Ticket 1: \[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 18, 23, 24\]  (sum=170)

            Hist wins: match 11: 325 | match 12: 52 | match 13: 2 | match 14: 0 | match 15: 0

  Top scored: \[5, 23, 24, 6, 2, 8, 13, 4\]

╭────────────────────────────────────────── Correlation Evidence ──────────────────────────────────────────╮

│ 🌕 Moon phase: Waning Gibbous (62.8% through cycle) | Distance: Neutral | Tide: normal                   │

│ ☀️ Solar Weather: storm (Planetary K-index: 5.0)                                                         │

│ 🧠 Noosphere Jitter: Volatile (Jitter Score: 0.845) | Regime: High Focus                                 │

│ 🌀 Chaos Entropy Boost: +0.5 applied to sampling temperature                                             │

╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  

──────────────────────────────────────────── CONSENSUS ANALYSIS ────────────────────────────────────────────

     25  █████████████░░  16 votes

      6  ████████████░░░  15 votes

      4  ███████████░░░░  14 votes

     10  ███████████░░░░  14 votes

     20  ███████████░░░░  14 votes

     15  ██████████░░░░░  13 votes

     12  ██████████░░░░░  13 votes

     11  ██████████░░░░░  13 votes

      1  █████████░░░░░░  12 votes

      7  █████████░░░░░░  12 votes

  

───────────────────────────────────── LEARN — How to use these results ─────────────────────────────────────

  • Look for Convergence: Numbers that multiple strategies agree on.

  • Respect Harmony: The engine auto-filters for sum-range and parity balance.

  • Play Diversified: Use different strategy tiers (Statistical, ML, Esoteric).

  

⚠  Skipped: lorentz

 /mnt/c/U/a/Documents/Obsidian/PKM/W/(/lottery/.ge/w/2026-04-29-02-45-06-737-l63k  worktree-202…-06-737-l63k !10

❯

## Model Response

> [!Model Thoughts]

## Gemini said

**TL;DR:** Your wizard CLI has poor state management and exposes raw Python implementation details to the user. It crashes on empty mathematical inputs, fails to load missing strategy registries, and forces the user through redundant prompts. I have broken down the necessary fixes into critical bugs, UX/architectural improvements, and documentation updates.

Here is a rigorous analysis of your CLI's output. You have some glaring blind spots in how this wizard is designed. Exposing `args:` and `kwargs:` directly in a user-facing prompt is lazy design—it breaks the fourth wall and offloads your internal data structures onto the user. Furthermore, asking for `draw_date` multiple times per strategy, only to ask for a "Global Draw Date" at the very end (Step 6), indicates a flawed assumption about how user context should flow through your application.

Here are the tasks to fix these issues and improve the implementation.

### 1\. Critical Bug Fixes (The Crashes)

- **Task 1.1: Fix the `weighted` Strategy KeyError.**
	- *Issue:* When selecting the `all` strategy group, the engine tries to load a strategy named `weighted`, which does not exist in `_REGISTRY`.
		- *Action:* Either implement and register the `weighted` strategy, or remove it from the hardcoded list associated with the `all` (and potentially `statistical`) group alias in `engine/strategies/__init__.py`.
- **Task 1.2: Patch `LEY_LINES` Float Math Exception.**
	- *Issue:* `Strategy failed: can't multiply sequence by non-int of type 'numpy.float64'`. Because the user left `latitude` and `longitude` blank, the strategy received `None` or an empty string, which likely fell back to a default sequence or uninitialized state, causing a mathematical crash when multiplied by a NumPy float.
		- *Action:* Implement strict type casting and validation for coordinates. If inputs are empty, either abort the strategy cleanly with a warning or inject default `float` coordinates.
- **Task 1.3: Fix `LORENTZ` Silent Failure.**
	- *Issue:* The Lorentz strategy was skipped (`⚠ Skipped: lorentz`) because the user pressed Enter on `sigma`, `rho`, and `beta`.
		- *Action:* The prompt shows defaults (e.g., `(10.0)`), but the underlying parser isn't applying them correctly when an empty string is passed. Fix the parameter fallback logic so empty inputs automatically inherit the displayed default float values.

### 2\. Architectural & UX Improvements (The Wizard Flow)

- **Task 2.1: Hoist Global Variables (Context Inheritance).**
	- *Issue:* You ask for `draw_date` or `upcoming_draw_date` in almost every strategy (I Ching, Moon Phase, Noosphere, Sefirot, Solar, Vix Jitter, Zodiac), and then ask for it *again* at Step 6.
		- *Action:* Move Step 6 (Draw Date) up to Step 1.5. Store it in a global wizard context. When configuring individual strategies, hide the `draw_date` prompt and automatically inject the global date into their `kwargs`. Only prompt for a date if it explicitly differs from the global context (e.g., historical backtesting).
- **Task 2.2: Eradicate `args` and `kwargs` from Prompts.**
	- *Issue:* `refraction`, `seismic`, and `vix_jitter` ask the user to input `args:` and `kwargs:`.
		- *Action:* Map these internal catch-alls to actual, human-readable parameters specific to the strategy. If they don't have user-configurable parameters, hide the `Customize parameters?` prompt entirely for those specific strategies.
- **Task 2.3: Smart Input Parsing for Strategy Groups.**
	- *Issue:* In Run 3, the user pasted a comma-separated list of strategies into the "Select strategy group" prompt, triggering a validation error.
		- *Action:* Improve the prompt validation. If the input contains commas or matches multiple known keys in `_REGISTRY`, automatically intercept it, switch the mode to `custom`, and bypass the "Enter strategy name(s)" prompt.
- **Task 2.4: Smart Geolocation Defaults.**
	- *Issue:* `ley_lines` and `weather` ask for coordinates or locations.
		- *Action:* You already know the user selected `br/mega-sena` or `br/lotofacil`. Use the `br/` prefix to inject a default country hint (Brazil) or default central coordinates so the user doesn't have to manually look up lat/long unless they want to override it.

### 3\. Documentation Tasks

- **Task 3.1: Document the `custom` Wizard Flow.**
	- Clearly state in the CLI help docs how to pass multiple strategies (comma-separated) and how default parameters are applied if the wizard is skipped.
- **Task 3.2: Update Strategy Parameter Definitions.**
	- Document exactly what is required for esoteric strategies. `ley_lines` needs a note about valid coordinate formats. `lorentz` needs a brief explanation of chaotic constants so the user isn't guessing what `sigma=10.0` means in the context of lottery tickets.

---

Which architectural approach do you want to tackle first: fixing the crash vulnerabilities in the mathematical models, or rewriting the wizard's state management to properly handle global variables?

---

------



