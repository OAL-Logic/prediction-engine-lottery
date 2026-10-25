# Lottery Prediction Engine — Domain Glossary

Ubiquitous vocabulary for the mathematical, analytical, combinatorial, and multi-jurisdiction lottery prediction engine. All core engine code, strategies, APIs, and documentation standardize on canonical English terminology. Localized jurisdiction terms are retained as registered aliases for cultural context and user interfaces.

---

## Wagering & Multi-Draw Mechanics

**Multi-Draw**:
An advance-play wagering mechanism where the same ticket combinations are systematically registered for a series of consecutive upcoming draws.
- _Local aliases_: Teimosinha (Brazil / Caixa), Advance Play (US), Multi-Draw (US MUSL / UK), Abonnement (France / FDJ), Abo-Spiel (Germany).
- _Avoid_: Stubborn bet, Persistence bet, Consecutive tickets.

**Total Stake**:
The total monetary amount wagered across all tickets and draws, calculated as $\text{unit price} \times \text{combinatorial combinations} \times \text{ticket count} \times \text{draw count}$.
- _Local aliases_: Investimento, Custo Total, Custo da Aposta.
- _Avoid_: Total investment, Capital expenditure, Bankroll deposit.

**Historical Persistence**:
An empirical backtesting metric measuring the frequency with which a static set of tickets wins prize tiers across rolling consecutive blocks of historical draws.
- _Local aliases_: Persistência Histórica, Replay de Blocos Consecutivos.
- _Avoid_: Historic endurance, Draw resilience, Consecutive memory.

**Multiple Bet (Unfolded Bet)**:
A single wager containing more numbers than the game's base pick count ($k' > k$), which combinatorially expands into $\binom{k'}{k}$ standard tickets.
- _Local aliases_: Aposta Múltipla, Jogo Desdobrado, Bolão base.
- _Avoid_: System bet, Big bet.

---

## Numerological & Temporal Alignment

**Lucky Clover**:
A personal numerology and gematria profile that deterministically derives auspicious digits, personal life-path vectors, and harmonic calendar days from a user profile.
- _Local aliases_: Trevo da Sorte (Brazil).
- _Avoid_: Mystic Clover, Luck Trefoil, Magic Square.

**Harmonic Draw Day**:
The specific calendar weekday mathematically or numerologically aligned with a player's personal cycle or the game's historical cadence.
- _Local aliases_: Dia Ideal, Dia Harmônico, Dia de Sorte Pessoal.
- _Avoid_: Lucky day, Best day, Fortune date.

**Temporal Alignment**:
The cross-referencing of upcoming draw dates with planetary, lunar, solar, or numerical cycles to synchronize ticket generation seeds.
- _Local aliases_: Alinhamento Temporal, Sincronia de Data.
- _Avoid_: Astrology bet, Horoscope check.

---

## Combinatorial & Structural Framework

**Candidate Pool**:
The selected subset of numbers ($v$ numbers where $k \le v \le N$) from which tickets or covering designs are constructed.
- _Local aliases_: Conjunto de Dezenas, Pool de Candidatos.
- _Avoid_: Number list, Group.

**Covering Design**:
A combinatorial collection of $b$ tickets guaranteeing that if $m$ drawn winning numbers fall within a pool of $v$ numbers, at least one ticket will match at least $t$ numbers, denoted $C(v, k, t, m) = b$.
- _Local aliases_: Fechamento, Desdobramento Garantido.
- _Avoid_: Wheel system, Combinatorial matrix.

**Harmony Gate**:
The multi-tier statistical and structural constraint pipeline (parity, sums, AC value, skips, decade spans) that validates or prunes generated candidate tickets.
- _Local aliases_: Filtros Estruturais, Portão de Harmonia.
- _Avoid_: Reject list, Ticket filter.

**Arithmetic Complexity (AC Value)**:
A metric quantifying the arithmetic diversity of a ticket, calculated as the count of distinct absolute differences between all pairs minus $(k - 1)$.
- _Local aliases_: Complexidade Aritmética, Valor AC.
- _Avoid_: Spacing metric, Difference count.

---

## Game Matrix & Multi-Pool Archetypes

**Primary Pool**:
The main pool of numbers $N$ from which $k$ numbers are chosen (e.g. 1–60 in Mega-Sena, 1–69 in US Powerball).
- _Local aliases_: Dezenas Principais, Globo Principal.
- _Avoid_: Main numbers, White balls.

**Secondary Pool (Bonus Pool)**:
An independent secondary pool of numbers from which bonus balls are drawn (e.g. 1–26 Powerball, 1–12 EuroMillions Lucky Stars, 1–6 Trevos in +Milionária).
- _Local aliases_: Bola Bônus, Trevos, Estrelas, Powerball, Mega Ball.
- _Avoid_: Extra number, Special ball.
