# SamLotto (Lotto PowerPlayer) - User Stories

## Overview
SamLotto is a comprehensive lottery analysis and prediction application designed for Windows. It allows users to manage drawing results for multiple lotteries, apply complex statistical filters to identify patterns, generate optimized tickets, and check for winnings.

## Personas
- **The Hobbyist:** Plays the lottery occasionally and wants an easy way to pick "smarter" numbers than random quick-picks.
- **The Analyst:** An advanced user who studies number frequencies, historical trends, and applies complex mathematical filters to maximize their odds.
- **The Administrator:** Responsible for keeping the lottery database up-to-date with the latest drawing results.

---

## 1. Lottery Database & Drawing Management

### US.1: Manage Lottery Profiles
**As a** User,
**I want to** select from a list of predefined lotteries or create a new lottery profile,
**so that** I can manage data for different games (e.g., Powerball, Mega Sena, Lotofacil).

**Acceptance Criteria:**
- User can view a list of supported lotteries.
- User can add a new lottery by defining its name, number range, and bonus ball rules.
- User can switch between different lottery contexts.

### US.2: Update Drawing Results
**As an** Administrator,
**I want to** add and edit drawing results in the database,
**so that** my analysis is based on the most recent data.

**Acceptance Criteria:**
- User can manually enter new drawing results (Date, Numbers, Bonus balls).
- User can edit or delete existing drawings to correct errors.
- The system prevents duplicate entries for the same drawing date.

### US.3: External Data Sync (Future/Implicit)
**As a** User,
**I want to** check for drawing updates online,
**so that** I don't have to enter them manually every time.

**Acceptance Criteria:**
- Application provides links to official lottery results websites (samlotto.com, etc.).
- [Implicit] UI contains "Update" buttons that suggest potential web-scraping or API integration for drawings.

---

## 2. Statistical Analysis

### US.4: Analyze Number Frequency
**As an** Analyst,
**I want to** view frequency charts and tables for numbers,
**so that** I can identify "hot" and "cold" numbers over a specific period.

**Acceptance Criteria:**
- User can see how many times each number has appeared.
- User can sort numbers by frequency.
- Results can be visualized in a grid or chart format.

### US.5: View Historical Trends
**As an** Analyst,
**I want to** browse the historical drawing log,
**so that** I can see the progression of winning combinations.

**Acceptance Criteria:**
- User can scroll through a comprehensive grid of all past drawings.
- User can filter the history by date range.

---

## 3. Filtering & Prediction

### US.6: Apply Base Filters
**As a** User,
**I want to** apply standard filters (Sum, Odd/Even, Low/High),
**so that** I can exclude combinations that are statistically unlikely to occur.

**Acceptance Criteria:**
- User can set a range for the "Sum" of the picked numbers.
- User can specify the desired ratio of Odd vs. Even numbers.
- User can specify the desired ratio of Low vs. High numbers.

### US.7: Advanced Pattern Filtering
**As an** Analyst,
**I want to** create and save complex filtering rules (Assistant, Advanced 1/2/3),
**so that** I can refine my number selection based on sophisticated statistical theories.

**Acceptance Criteria:**
- User can combine multiple filters into a single "Filter Group".
- User can save and load filter configurations.
- The system indicates how many combinations are eliminated by each filter.

### US.8: Generate Predicted Combinations
**As a** Hobbyist,
**I want to** generate a set of "winning" combinations based on my selected filters,
**so that** I can buy tickets with optimized odds.

**Acceptance Criteria:**
- System generates a list of combinations that pass all active filters.
- User can specify how many tickets/combinations they want to generate.
- User can use a "Random" generator that respects active filters.

---

## 4. Ticket Management & Winning Verification

### US.9: Build & Export Tickets
**As a** User,
**I want to** format my generated numbers into printable or exportable tickets,
**so that** I can use them at a physical lottery retailer.

**Acceptance Criteria:**
- User can view a print-preview of the tickets.
- User can export the generated numbers to a text or CSV file.

### US.10: Check for Winnings
**As a** User,
**I want to** input my purchased tickets and check them against the latest results,
**so that** I can quickly see if I won and how much.

**Acceptance Criteria:**
- User can load their saved tickets.
- System highlights matching numbers between tickets and drawing results.
- System calculates the number of matches (e.g., 3 hits, 4 hits + bonus).

---

## 5. User Interface & Tools

### US.11: Use Built-in Tools (Calculator/Video)
**As a** User,
**I want to** access utility tools like a calculator or help videos within the app,
**so that** I don't have to leave the application for simple tasks or learning.

**Acceptance Criteria:**
- User can open a built-in calculator.
- User can view tutorial videos or help documentation directly from the menu.

### US.12: Application Registration
**As a** Trial User,
**I want to** register my software with a license key,
**so that** I can unlock the full functionality of the Pro version.

**Acceptance Criteria:**
- System provides a registration form.
- Valid license keys unlock previously restricted filters or database features.
