"""
Script to capture Phase 4 verification screenshots for visual audit:
- Dark theme Caixa betslip calibrator & printer studio
- Light theme Caixa betslip calibrator
- Millimeter calibration test sheet
"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QImage

from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.perspectives.printer.models import CAIXA_PRESETS
from cockpit.src.perspectives.printer.engine import BetslipPrintEngine

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    os.makedirs("cockpit/docs/assets", exist_ok=True)

    # 1. Capture Dark Theme Printer Perspective in MainWindow
    window = CockpitMainWindow()
    window.resize(1400, 880)
    window.perspective_manager.switch_perspective("Printer")
    app.processEvents()

    pix = window.grab()
    pix.save("cockpit/docs/assets/phase4_dark_printer_caixa_slip.png")
    print("Saved cockpit/docs/assets/phase4_dark_printer_caixa_slip.png")

    # 2. Capture Light Theme
    window.theme_manager.set_theme("Modern Enterprise (Light)")
    app.setStyleSheet(window.theme_manager.generate_stylesheet())
    window.apply_theme()
    app.processEvents()

    pix_light = window.grab()
    pix_light.save("cockpit/docs/assets/phase4_light_printer_caixa_slip.png")
    print("Saved cockpit/docs/assets/phase4_light_printer_caixa_slip.png")

    # 3. Capture High-Res Metric Calibration Test Sheet Image
    template = CAIXA_PRESETS["Caixa Lotofácil"]
    dpi = 200.0
    from cockpit.src.perspectives.printer.engine import mm_to_px
    w_px = int(mm_to_px(template.slip_width_mm, dpi))
    h_px = int(mm_to_px(template.slip_height_mm, dpi))

    img = QImage(w_px, h_px, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0xFFFFFFFF)
    p = QPainter(img)
    BetslipPrintEngine.render_calibration_sheet(p, template, dpi=dpi)
    p.end()

    img.save("cockpit/docs/assets/phase4_calibration_sheet.png")
    print("Saved cockpit/docs/assets/phase4_calibration_sheet.png")

if __name__ == "__main__":
    main()
