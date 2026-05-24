# Kabbalistic Numerology: Theory & Engine Implementation

This document serves as the theoretical foundation and technical blueprint for the Kabbalistic Numerology module within the Prediction Engine. It bridges the gap between esoteric Kabbalistic principles and quantitative algorithmic analysis.

---

## 1. Core Philosophy & Theoretical Foundation

Kabbalistic Numerology is based on the philosophy that the Universe and individuals are interconnected through numerical vibrations. 
*   **The Sepher Yetzirah:** The foundational text of Kabbalah describes the Universe's creation through 32 paths of wisdom (10 Sefirot and 22 Hebrew letters).
*   **The Nature of Numbers:** Numbers (1-9) are not merely counts; they are archetypal patterns that reveal stages of evolution. Each number has a unique positive and negative vibration.
*   **The Power of One:** All numbers are seen as divisions of the original unity ("One"), representing the manifest Higher Power.

---

## 2. The Personal Numerological Profile

A user's profile is generated from their full birth name and birthdate, calculating specific numbers that dictate their energetic resonance:

### 2.1 Core Identity
*   **Motivation (Vowels):** Reflects inner desires and internal feelings.
*   **Impression (Consonants):** Represents the external impression made on others.
*   **Expression (Full Name):** Enunciates how a person acts and interacts, revealing true talents.

### 2.2 The Life Path
*   **Destiny (Birthdate Sum):** Determines the evolutionary path and governs major life decisions (Day + Month + Year).
*   **Mission:** The individual's vocation on Earth.

---

## 3. Karmic Elements & Anomalies

Karmic elements act as structural filters and flags within the engine, warning of potential negative cycles or highlighting high potential.

### 3.1 Karmic Debts
Specific double-digit totals that warn of recurring obstacles:
*   **13/4 (Work/Negligence):** Warns that laziness will result in failure; hard work is required.
*   **14/5 (Physical Excess):** Warns against gambling, addictions, and impulsive behavior.
*   **16/7 (Pride/Ego):** Predicts structural collapse if built on weak or arrogant foundations.
*   **19/1 (Power/Egoism):** Predicts situations requiring selfless help to others.

### 3.2 Master Numbers
Unlike standard numbers, these are not reduced, as they indicate high-vibrational potential:
*   **11 (Intuition):** Strong psychic sensitivity.
*   **22 (Master Builder):** Ability to realize large-scale material projects.

---

## 4. The Arcanos & The Inverted Triangle of Life

The engine maps the user's name into an "Inverted Triangle of Life" using pyramidal addition to extract a sequence of **Arcanos** (Tarot-based vibrational codes).

### 4.1 Key Success Arcanos
*   **Arcano 78:** Sudden windfall (explicitly linked to games of chance and inheritance).
*   **Arcano 70:** Stroke of luck, profit, and abundance.
*   **Arcano 32:** Strategic success and favorable business circumstances.

### 4.2 Traffic Jams (Negative Sequences)
The engine flags sequences where the same number repeats three or more times in the Triangle (e.g., `222` or `5555`). These indicate vibrational stagnation or recurring life obstacles.

---

## 5. Technical Implementation Blueprint

To apply this esoteric philosophy to the statistical Prediction Engine, the qualitative vibrations are converted into quantitative weights via `numerology_engine.py`.

### 5.1 The Alphabet-to-Number Map (Kabbalistic)
Unlike the Pythagorean system, Kabbalistic Numerology uses specific letter values:
*   **1:** A, I, Q, J, Y
*   **2:** B, K, R
*   **3:** C, G, L, S
*   **4:** D, M, T
*   **5:** E, H, N, X
*   **6:** U, V, W
*   **7:** O, Z
*   **8:** F, P

*   **The "Y" Variable Rule:** "Y" is treated as a **vowel** (1) if there are no other vowels in the syllable. If accompanied by another vowel in the same syllable, it acts as a **consonant**.
*   **Accents:** Accented letters maintain their unaccented value.

### 5.2 Temporal Cycle Engine (Timing Gates)
Calculates the optimal timing for user actions:
*   **Personal Year:** `Current Year + Birth Day + Birth Month`. (e.g., Year 9 is flagged as an "Avoid" period for new bets).
*   **Personal Day:** The most granular timing signal for placing a ticket.

### 5.3 Orchestrator Integration
The `numerology_engine.py` operates as a strategy layer. It answers two questions:
1.  **Which numbers suit the user?** (Harmonic number affinity filtering based on Destiny/Expression).
2.  **Is this a favorable cycle?** (Timing gate based on Arcanos and Personal Day).

The final score is a blend:
`final_score = base_statistical_score * timing_multiplier (Biorhythm/Personal Day) * arcano_boost`
