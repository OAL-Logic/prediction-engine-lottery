"""
Capture light mode studio screenshot cleanly.
"""

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.core.models import PerspectiveType

def main():
    # Pre-configure light theme in settings
    settings = QSettings("Operator", "LotteryEngineCockpitV2")
    settings.setValue("theme_name", "Modern Enterprise Light")
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = CockpitMainWindow()
    window.resize(1280, 800)
    window.perspective_manager.switch_perspective(PerspectiveType.STUDIO)
    app.processEvents()

    pix = window.grab()
    os.makedirs("cockpit/docs/assets", exist_ok=True)
    pix.save("cockpit/docs/assets/phase2_light_studio_105_filters.png")
    print("Saved cockpit/docs/assets/phase2_light_studio_105_filters.png")
    
    # Restore dark theme for regular use
    settings.setValue("theme_name", "Trading Terminal (Default)")

if __name__ == "__main__":
    main()
