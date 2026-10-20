---
type: project
date: "2026-04-21"
status: active
priority: high
tags: [project, python, machine-learning, statistics]
---

# Python Prediction Engine

## Objective
Build a Python-based engine to analyze lottery results and predict future draws using statistical and pseudo-scientific correlations (Markov Chains, Moon Phases, Numerology, Weather, Bayesian Inference) for practice and education.

## Project Structure
- **[[PKM/Workspace/(P) Python Prediction Engine/Data/|Data/]]**: Raw CSV results (Lotofácil, Mega-Sena).
- **[[PKM/Workspace/(P) Python Prediction Engine/Modules/|Modules/]]**: Prediction logic and data augmentation scripts.
    - `markov_predictor.py`: Refined 1st-order Markov logic.
    - `astronomy_engine.py`: Moon phase calculation.
    - `numerology_analyzer.py`: Life path number logic.
    - `weather_engine.py`: Weather simulation and correlation.
    - `correlation_analyzer.py`: Advanced matrix generation (Pandas/Seaborn).
    - `bayesian_inference.py`: Hot/Cold number tracking via recursive updating.
    - `statistics_analyzer.py`: Lotofácil pattern analysis (Frame, Center, Fibonacci).
    - `main_engine.py`: Integrated CLI entry point.
- **[[PKM/Workspace/(P) Python Prediction Engine/Research/|Research/]]**: Links, theory, and manifestation techniques.

## Roadmap
1. [x] Gather historical data for Lotofácil/Mega-Sena (Real CSVs).
2. [x] Implement `astronomy_engine` module.
3. [x] Build `markov_predictor` refined logic.
4. [x] Build `numerology_analyzer` module.
5. [x] Implement `weather_engine` module.
6. [x] Create a `main_engine` CLI wrapper with multi-game support.
7. [x] Implement advanced Correlation Matrix (using `pandas`/`seaborn`).
8. [x] Implement Bayesian Inference (Hot/Cold number tracking).
9. [x] Implement Lotofácil Statistical Profile (Frame, Center, Prime, Fibonacci).

## Usage
Run the engine from the `Modules/` directory:
```bash
# Prediction Mode
python3 main_engine.py lotofacil
python3 main_engine.py mega-sena

# Analysis Mode (Generates correlation heatmaps)
python3 main_engine.py lotofacil analyze
```

```
cd "/mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Python Prediction Engine"
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
pip install ipykernel ipywidgets
python3 -m ipykernel install --user --name=lottery-env --display-name "Python (Lottery Engine)"
```


## Key References

Hot Numbers
Cold Numbers
Random Weighted
Monte Carlo
ML Logistic
Markov Chain: Uses transition probabilities to predict which numbers are likely to follow recent drawings.
Hybrid (Freq+ML)
Random Forest
Logistic Regression
Naive Bayes
Ensemble (Voting)
Ensemble (Prob Weighted)
Hybrid Ensemble (Weighted)

Weighted Statistical Model: Analyzes historical frequency, gap patterns, and positional tendencies to score each number.

Pattern Matching Model: Generates combinations matching historical patterns (sum ranges, odd/even ratios, high/low distribution).

---

**Deep Learning Ensemble**
- **Transformer** with multi-head attention for sequence patterns
- **Bidirectional LSTM/GRU** hybrid for temporal dependencies
- Temperature-based sampling to prevent mode collapse
---

**Master Ensemble**
Combines all models with weighted averaging and enforces diversity:
- ✅ No repeated Power Balls across predictions
- ✅ Minimum Hamming distance between number sets
- ✅ Full range coverage (no clustering)
---

- [[PKM/Library/Clippings/2026-04-19 - Clippings Chat Gemini - Can I use Markov chain to predict numbers being play in lotto|Markov Chain Theory]]
- [[Lottery Number Prediction Open Source]]
- [[Building a Number Prediction App]]
- [[2026-04-22 - Clippings - The All-Important Lotto Balanced Game - smartluck.com]]


Repositories

https://github.com/topics/lottery?o=desc&s=updated

1. https://github.com/kuamoto/LotoFacil_Lottery
2. https://github.com/camilafbarcellos/AG-LotofacilPreditor
3. https://github.com/LucasMoraesMarques/AppLoteria
4. https://github.com/meloluan/Estudo_Lotofacil
5. https://github.com/fcanato/megasena-ai
6. https://github.com/moshang-ax/lottery
7. https://github.com/chengstone/LotteryPredict
8. https://github.com/rouze-d/Malaysia-Lottery-Prediction
9. https://github.com/JohannesFriedrich/LottoNumberArchive
10. https://github.com/daowa89/lottery-archive
11. https://github.com/thanhnhu/vietlott
12. https://github.com/rahulvigneswaran/Lottery-Ticket-Hypothesis-in-Pytorch
13. https://github.com/LOG1997/log-lottery
14. https://github.com/rag-fish/loto6-deeplearning
15. https://github.com/cpeoples/powerpredict
16. https://github.com/engineer1982/Machine-Learning-Lottery-Prediction
17. https://github.com/Ishanoshada/Lottery-Predict
18. https://github.com/CrazyTrain93/Lottery_6_aus_49_predictions
19. https://github.com/kuamoto/LotoFacil_Lottery
20. https://github.com/JeffMv/Lofea

Others
- [[Links Manifestation Lotofacil|Manifestation & External Links]]
- https://www.youtube.com/@jotasilvalotto

Some ideas
- https://www.youtube.com/watch?v=nMIq_Y5lNrQ
- [Google Software Lottery](https://www.google.com/search?q=software+lottery&newwindow=1&sca_esv=903386efdd046f5a&biw=1620&bih=1016&sxsrf=ANbL-n4oiiviMZRZ854ajHOhyuAM4JxloQ%3A1777135797702&ei=tfDsafrOKv_T1sQPutHqsQQ&ved=0ahUKEwi6_cHfuomUAxX_qZUCHbqoOkY4ChDh1QMIEQ&uact=5&oq=software+lottery&gs_lp=Egxnd3Mtd2l6LXNlcnAiEHNvZnR3YXJlIGxvdHRlcnlIrBlQjQRY3hNwAXgBkAEAmAGiAaABwBCqAQQwLjE2uAEDyAEA-AEBmAINoAKmDcICChAAGEcY1gQYsAPCAhcQLhjcBhi4BhjaBhjYAhjIAxiwA9gBAcICChAjGIAEGIoFGCfCAgQQIxgnwgIKEAAYgAQYigUYQ8ICBRAAGIAEwgILEAAYgAQYigUYkQLCAhEQLhiABBiKBRiRAhjHARjRA8ICChAuGIAEGIoFGEPCAgoQABiABBgUGIcCwgILEC4YgAQYigUYkQLCAhoQLhiABBiKBRiRAhiXBRjcBBjeBBjgBNgBAsICCxAuGIAEGMcBGNEDwgIGEAAYFhgewgIaEC4YgAQYxwEY0QMYlwUY3AQY3gQY4ATYAQKYAwCIBgGQBgy6BgQIARgZugYGCAIQARgUkgcEMS4xMqAH9GqyBwQwLjEyuAebDcIHBjItMTIuMcgHPYAIAQ&sclient=gws-wiz-serp)
- Create same app as: https://www.brsoftech.com/blog/best-lottery-software-and-analysis-tools/
	- https://powerfall.com/
	- https://example.org/lottery-studio
		- https://example.org/lottery-studio
	- https://www.timersoft.com/downloads/
	- https://smartluck.com/
		- https://www.youtube.com/watch?v=8CrTpJSZqZ0


- https://neoday.com/gamified-experiences/lottery-software/

SaaS idea to compete with [lotosport](https://lotosport.com.br/) ou https://www.somatematica.com.br/loterias/assine.php

lottery optimize with AI at the end to summarize the results (how to show best value having an AI vs the person getting the output and sending to any LLM)

```
🏆 Top Findings:
   1. Winner: pattern strategy (with Limit 100, Temp 0.5) achieved the best combination of
      20.0% Top-6 Capture and the lowest Average Rank of 24.0. This means it's doing the
      best job of keeping winning numbers near the top of its list.
   2. Runner Up: crowd_avoidance was remarkably consistent across almost all history limits
      and temperatures, holding a steady 20% capture rate with an average rank of 28.4. This
      suggests the recent winners were numbers that have been historically "ignored" or are
      less frequent, which is exactly what this strategy looks for.
   3. Recency Bias is Real: For the pattern strategy, focusing on the last 100 draws (Limit
      100) performed significantly better (Avg Rank 24.0) than looking at 200 draws (Avg
      Rank 29.5).

  💡 Recommendation for Mega-Sena:
  Based on this empirical data, your best move for the next game is to use the
  pattern-recognition algorithm with a focused history window:

   1 lottery suggest mega-sena --strategy pattern --limit 100 --temp 0.5

  Alternatively, since crowd_avoidance showed such high stability across different settings,
  it serves as a very strong "hedge" strategy to use in an ensemble:

   1 lottery suggest mega-sena --strategy pattern,crowd_avoidance --limit 100 --temp 0.5
```
## MOC
→ [[Prediction Engine]]
