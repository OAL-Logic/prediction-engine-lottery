---
title: Issue 04 — Phase 4: Physical Betslip Calibrator & CLI Subcommands
status: resolved
labels:
  - ready-for-agent
  - phase-4
  - completed
---

# Issue 04: Phase 4 — Physical Betslip Calibrator, File I/O & CLI Subcommands

## Scope
- Caixa betslip layout calibrator & printer (Lotofácil, Mega-Sena, Quina, Lotomania).
- File format support: `.slk`, `.csv`, `.txt`, and SamLotto space-delimited text.
- Bidirectional Profile JSON <-> Headless Engine YAML translation.
- CLI subcommands `lottery cockpit` and `lottery desktop`.

## Implemented Deliverables
1. `cockpit/src/services/file_io.py`:
   - `TicketFileIO`: Parsers and serializers for SamLotto SYLK (`.slk`), space-delimited text (`.txt`), and CSV (`.csv`).
   - `ProfileManager`: Bidirectional save/load of native desktop `.json` profiles and headless engine CLI `.yaml` profiles.
2. `cockpit/src/perspectives/printer/`:
   - `models.py`: `BetslipTemplate` and official Brazilian Caixa Econômica Federal presets (`Caixa Lotofácil`, `Caixa Mega-Sena`, `Caixa Quina`, `Caixa Lotomania`, `Caixa Dupla Sena`) with sub-millimeter coordinates and hardware compensation.
   - `engine.py`: `BetslipPrintEngine` with high-precision vector rendering to `QPainter`, multi-page PDF generation via `QPdfWriter`, and metric calibration test sheets with millimeter rulers and crosshairs.
   - `widgets.py`: `BetslipCanvasWidget` interactive slip preview with zoom, real-time millimeter coordinate tracking, and origin drag adjustment.
   - `view.py`: `PrinterPerspectiveView` complete studio with preset switching, live calibration spinboxes, ticket queue inspector, pagination, and direct print/PDF actions.
3. Shell & CLI Integration:
   - `cockpit/src/shell/main_window.py`: Registered `PerspectiveType.PRINTER`, added toolbar capsule pill and menu items, and connected ticket import/export dialogs.
   - `cockpit/src/app.py`: Added CLI argument parsing (`--game`, `--perspective`, `--theme`, `--import-file`).
   - `engine/cli/main.py`: Registered `lottery cockpit` and `lottery desktop` subcommands in primary Typer CLI panel.
4. Automated tests:
   - `cockpit/tests/test_phase4.py`: 7/7 tests passing.
   - Total test suite: 31/31 passing across all 4 phases.
5. Visual verification artifacts:
   - `cockpit/docs/assets/phase4_dark_printer_caixa_slip.png`
   - `cockpit/docs/assets/phase4_light_printer_caixa_slip.png`
   - `cockpit/docs/assets/phase4_calibration_sheet.png`
