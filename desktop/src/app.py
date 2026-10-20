"""
Desktop Cockpit Application Entrypoint
======================================
Launches the Next-Gen Lottery Engine Desktop Cockpit (`CockpitMainWindow`).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure local site-packages is in sys.path if running under user environment
user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

from PySide6.QtWidgets import QApplication
from desktop.src.shell.main_window import CockpitMainWindow


def run_cockpit():
    app = QApplication(sys.argv)
    app.setApplicationName("LotteryEngineCockpit")
    app.setOrganizationName("Operator")
    
    window = CockpitMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_cockpit())
