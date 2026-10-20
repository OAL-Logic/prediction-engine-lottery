"""
Cockpit Application Entrypoint
==============================
Clean standalone entrypoint for the Next-Gen Lottery Engine Desktop Cockpit.
Can be executed directly via:
    python3 cockpit/src/app.py --game br/lotofacil --perspective studio
Or invoked via CLI:
    lottery cockpit
    lottery desktop
"""

import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure local site-packages is in sys.path
user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists() and str(user_site) not in sys.path:
    sys.path.insert(0, str(user_site))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from cockpit.src.core.models import PerspectiveType
from cockpit.src.shell.main_window import CockpitMainWindow
from cockpit.src.services.file_io import TicketFileIO


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lottery Engine Desktop Cockpit V2 (Next-Gen Operator Suite)"
    )
    parser.add_argument(
        "--game", "-g",
        type=str,
        default="br/lotofacil",
        help="Initial game slug (e.g. br/lotofacil, br/mega-sena, br/quina)",
    )
    parser.add_argument(
        "--perspective", "-p",
        type=str,
        default="express",
        choices=["express", "studio", "esoteric", "printer"],
        help="Initial perspective view workspace",
    )
    parser.add_argument(
        "--theme", "-t",
        type=str,
        default="dark",
        choices=["dark", "light"],
        help="Initial theme (dark or light)",
    )
    parser.add_argument(
        "--import-file", "-i",
        type=str,
        default=None,
        help="Path to .slk, .csv, or .txt file containing ticket combinations to load",
    )
    return parser


def run_cockpit(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = build_arg_parser()
    args, unknown = parser.parse_known_args(argv)

    app = QApplication.instance() or QApplication([sys.argv[0]] + unknown)
    app.setApplicationName("LotteryEngineCockpitV2")
    app.setOrganizationName("Operator")

    window = CockpitMainWindow()

    # 1. Apply Initial Game
    if args.game:
        target_game = window.bridge.get_game(args.game)
        if target_game:
            window.set_active_game(target_game)

    # 2. Apply Theme
    if args.theme == "light":
        window.theme_manager.set_theme("Modern Enterprise (Light)")
        app.setStyleSheet(window.theme_manager.generate_stylesheet())
        window.apply_theme()

    # 3. Apply Perspective
    p_map = {
        "express": PerspectiveType.EXPRESS,
        "studio": PerspectiveType.STUDIO,
        "esoteric": PerspectiveType.ESOTERIC,
        "printer": PerspectiveType.PRINTER,
    }
    target_p = p_map.get(args.perspective.lower(), PerspectiveType.EXPRESS)
    window.perspective_manager.switch_perspective(target_p)

    # 4. Import Tickets if specified
    if args.import_file and Path(args.import_file).exists():
        tickets = TicketFileIO.parse_tickets(args.import_file)
        if tickets:
            window.view_printer.set_tickets(tickets)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_cockpit())
