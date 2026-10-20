"""
Script to capture Phase 3 verification screenshots for visual audit (Esoteric & Chaos Observatory).
"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import sys
from PySide6.QtWidgets import QApplication

from cockpit.src.shell.main_window import CockpitMainWindow

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    
    # 1. Capture Esoteric Perspective in MainWindow (Dark Theme)
    window = CockpitMainWindow()
    window.resize(1360, 840)
    window.perspective_manager.switch_perspective("Esoteric")
    app.processEvents()
    
    os.makedirs("cockpit/docs/assets", exist_ok=True)
    pix = window.grab()
    pix.save("cockpit/docs/assets/phase3_dark_esoteric.png")
    print("Saved cockpit/docs/assets/phase3_dark_esoteric.png")
    
    # 2. Capture Light Theme
    window.theme_manager.set_theme("Modern Enterprise (Light)")
    app.setStyleSheet(window.theme_manager.generate_stylesheet())
    window.apply_theme()
    app.processEvents()
    
    pix_light = window.grab()
    pix_light.save("cockpit/docs/assets/phase3_light_esoteric.png")
    print("Saved cockpit/docs/assets/phase3_light_esoteric.png")

if __name__ == "__main__":
    main()
