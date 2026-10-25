# 🎟️ Online Lottery Platforms & Messenger Services

Reference guide and architectural catalog of external platforms, digital lottery ticket messengers, and official state lottery operators.

---

## 🌐 Featured Platforms

### 1. TheLotter
- **URL**: [https://www.thelotter.com/pt/bilhetes-loteria/](https://www.thelotter.com/pt/bilhetes-loteria/)
- **Category**: Online Lottery Ticket Messenger Service (Serviço de Mensageiro de Bilhetes de Loteria Online)
- **Scope**: International & Multi-jurisdiction (Americas, Europe, Australia)

#### 📌 Overview & Capabilities
TheLotter operates as a courier / ticket messenger service:
- Players select numbers online.
- Local agents in the host country (e.g., USA, Spain, Italy) buy physical paper tickets on behalf of the customer from authorized lottery retailers.
- Tickets are scanned and uploaded to the customer's account before the draw, ensuring legal ownership and verification.
- Small prizes are credited directly; jackpot claims are supported with physical ticket delivery.

#### 🎯 Supported Lotteries Matching Engine Adapters
| Region | Games | Engine Adapter Support |
| :--- | :--- | :--- |
| **USA** | Powerball, Mega Millions, Cash4Life | `engine/adapters/us/` (`powerball`, `mega_millions`) |
| **Europe** | EuroMillions, EuroJackpot, SuperEnalotto, La Primitiva | `engine/adapters/eu/` (`euromillions`) |
| **Brazil / LatAm** | Mega-Sena, Quina, Lotofácil (regional coverage & international play) | `engine/adapters/br/` |

---

### 2. The National Lottery (United Kingdom)
- **URL**: [https://www.national-lottery.co.uk/](https://www.national-lottery.co.uk/)
- **Category**: Official State-Regulated National Lottery Operator (Allwyn Entertainment / UK Gambling Commission)
- **Scope**: United Kingdom & Isle of Man

#### 📌 Overview & Key Games
The official UK portal for ticket sales, draw results, game rules, and charity funding:
- **Lotto**: 6/59 matrix with rollover / "Must Be Won" rolldown mechanics (great for Expected Value calculation $EV > 0$).
- **EuroMillions**: UK co-founding operator (5/50 + 2/12) featuring the guaranteed UK Millionaire Maker raffle.
- **Set For Life**: Annuity lottery (£10,000 every month for 30 years, 5/47 + 1/10 Life Ball).
- **Thunderball**: Lower volatility / fixed jackpot draw (5/39 + 1/14 Thunderball).

#### 💡 Relevance & Integration Opportunities
1. **EuroMillions Verification & Cross-Checking**:
   - Primary official validator for EuroMillions draws modeled in `engine/adapters/eu/euromillions.py`.
2. **Rolldown Expected Value (EV) Opportunities**:
   - UK Lotto "Must Be Won" draws distribute the jackpot across lower prize tiers (Match 2 to Match 5 + Bonus) when no ticket matches all 6 numbers. This presents positive expected value ($+EV$) windows for combinatorial ticket wheeling.
3. **UK Draw Adapter Candidate**:
   - Direct candidate for a future `engine/adapters/uk/` adapter family (`uk_lotto`, `thunderball`, `set_for_life`).

---

## 🏢 Platform Landscape & Benchmarks

| Service / Platform | URL | Type | Focus |
| :--- | :--- | :--- | :--- |
| **The National Lottery (UK)** | [national-lottery.co.uk](https://www.national-lottery.co.uk/) | Official State Operator | Official UK games (Lotto 6/59, EuroMillions, Thunderball, Set For Life) |
| **TheLotter** | [thelotter.com/pt/bilhetes-loteria/](https://www.thelotter.com/pt/bilhetes-loteria/) | Courier / Messenger | Global ticket purchasing for international players |
| **Caixa Loterias Online** | [loteriasonline.caixa.gov.br](https://www.loteriasonline.caixa.gov.br/) | Official Government Operator | Direct national betting in Brazil (Mega-Sena, Lotofácil, Quina) |
| **LottoSport** | [lotosport.com.br](https://lotosport.com.br/) | Brazilian SaaS | Lotofácil / Mega-Sena closing tools & statistics |
| **Só Matemática** | [somatematica.com.br/loterias/](https://www.somatematica.com.br/loterias/assine.php) | Educational / Subscription | Brazilian lottery statistics & generators |
| **Lottoland** | [lottoland.com](https://www.lottoland.com/) | Lottery Betting (Insurance Model) | Financial derivatives / betting on draw outcomes |
