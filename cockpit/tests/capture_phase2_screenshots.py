"""
Script to capture Phase 2 verification screenshots for visual audit.
"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize, QTimer

from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.perspectives.studio.backtest_dialog import BacktestOptimizerDialog
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.core.models import ToleranceRule, ToleranceMode

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    
    bridge = EngineBridge()
    game = bridge.get_game("br/lotofacil")
    filters = bridge.load_catalog_filters(game)
    
    # 1. Capture Studio Perspective in MainWindow
    window = CockpitMainWindow()
    window.resize(1280, 800)
    window.perspective_manager.switch_perspective("Studio")
    app.processEvents()
    
    os.makedirs("cockpit/docs/assets", exist_ok=True)
    pix = window.grab()
    pix.save("cockpit/docs/assets/phase2_dark_studio_105_filters.png")
    print("Saved cockpit/docs/assets/phase2_dark_studio_105_filters.png")
    
    # 2. Capture BacktestOptimizerDialog
    tol = ToleranceRule(mode=ToleranceMode.AND)
    # Enable a few filters to showcase the backtester
    filters[0].enabled = True # Odd count
    filters[5].enabled = True # Sum
    filters[20].enabled = True # AC value
    
    dialog = BacktestOptimizerDialog(game=game, filters=filters, tolerance=tol)
    dialog.resize(900, 620)
    app.processEvents()
    
    pix_dlg = dialog.grab()
    pix_dlg.save("cockpit/docs/assets/phase2_dark_backtest_dialog.png")
    print("Saved cockpit/docs/assets/phase2_dark_backtest_dialog.png")

    # 3. Capture Light Mode Studio
    window.theme_manager.set_theme("Modern Enterprise (Light)")
    app.setStyleSheet(window.theme_manager.generate_stylesheet())
    window.apply_theme()
    app.processEvents()
    pix_light = window.grab()
    pix_light.save("cockpit/docs/assets/phase2_light_studio_105_filters.png")
    print("Saved cockpit/docs/assets/phase2_light_studio_105_filters.png")

if __name__ == "__main__":
    main()
