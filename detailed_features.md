# SamLotto (Lotto PowerPlayer Pro) - Detailed Technical Feature Catalog

## 1. Database & Data Architecture
The application uses **Microsoft Jet OLEDB 4.0** (Access/MDB files) for its backend.
- **Connection Strings:** `Provider=Microsoft.Jet.OLEDB.4.0;Data Source=...LottoWinner_Data.mdb;Password=yangbaoshan;`
- **Primary Tables:**
  - `lottery`: Stores lottery profiles (Name, Country_State, Groups, Game Rules).
  - `drawings`: Historical winning numbers (Date, Draw numbers).
  - `filters`: Definitions and parameters for user-defined filtering rules.
  - `perdiction`: Stores results of prediction/generation runs.
  - `nsSearch` / `nsSearchDetails`: Likely related to advanced historical search/pattern matching.
  - `nsStat`: Statistical aggregate data (AppearCount, Hot/Cold).
  - `tmpDrawings` / `tmp`: Intermediate tables for calculation processing.

## 2. Statistical Analysis Engine
The application performs multi-dimensional analysis on drawing history.
- **Frequency Analysis:** `AppearCount`, `Hot/Cold` number tracking.
- **Interval Analysis:** Tracking the gaps between number appearances.
- **Sum Analysis:** Calculation of total sum ranges for historical draws.
- **Odd/Even & Low/High Ratios:** Distribution analysis across drawing sets.
- **Consecutive Numbers:** Identification of adjacent number patterns.
- **Prime Number Analysis:** Tracking the frequency of prime numbers in draws.

## 3. Filtering Systems
The application uses a tiered filtering architecture to eliminate unlikely combinations.
- **Base Filters:** Standard statistical thresholds (Sum, Odd/Even, Low/High).
- **Advanced Filters (Units: Adv1, Adv2, Adv3):** Complex multi-variable logic.
- **Assistant Filter:** A guided wizard-like interface for setting up filters.
- **Pattern Matching:** Filtering based on historical sequence similarities.
- **Filter Groups:** Logical groupings of filters that can be toggled or combined.
- **Elimination Tracking:** Real-time feedback on how many combinations each filter removes.

## 4. Number Generation & Prediction
- **Random Generation:** Basic random number picker.
- **Filtered Generation:** Generates combinations that must satisfy all active filtering rules.
- **Grooved Spacers/Mapping:** UI hints suggest advanced "Wheeling" systems (mapping selected numbers onto optimized templates).
- **Prediction Runs:** Batch generation of tickets stored in the `perdiction` table.

## 5. UI/UX & Components
Built with **Embarcadero Delphi/C++ Builder** using high-end component libraries:
- **VCL Framework:** Core Windows UI.
- **Raize Components (Rz):** Used for advanced tabs (`TRzPageControl`), buttons (`TRzBitBtn`), and specialized edits (`TRzNumericEdit`, `TRzSpinEdit`).
- **EhLib (DBGridEh):** Powerful data grids for displaying lottery results and statistics with sorting/filtering capabilities.
- **LMD Tools:** Additional UI utilities (Docking labels, Image lists).
- **Built-in Utilities:**
  - `PopupCalculator`: Integrated financial/math calculator.
  - `DrawingsUpdate`: Form for fetching/entering new results.
  - `CheckWinning`: Form for verifying tickets against drawings.

## 6. Connectivity & Licensing
- **Update System:** `update.exe` and `updateForm` for drawing and software updates.
- **Web Integration:** Links to `samlotto.com`, `lotto-007.com`, and `samlottery.xyz`.
- **Licensing:** Password-protected MDB access and `reg` (Registration) forms for license key validation.
- **Support:** Integrated support email (`support@lotto-007.com`).
