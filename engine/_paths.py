"""
Project root resolution 🗂️
==========================
`Path(__file__).parent...` arithmetic (used throughout engine/ and desktop/
to locate data/) assumes a normal source checkout. Under PyInstaller (see
packaging/lottery-desktop.spec), sys.frozen is set and __file__-relative
climbing no longer lands on a real data/ directory — PROJECT_ROOT here is
the one thing that has to stay correct in both cases, since the desktop
app's game registry (engine/adapters/registry.py) and draw database
(engine/modules/storage.py) can't locate anything without it.
"""

from __future__ import annotations

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # sys._MEIPASS is PyInstaller's own answer to "where did you actually put
    # the bundled datas=[...] files" — NOT sys.executable's directory: PyInstaller
    # 6.x's onedir layout puts everything except the executable itself under an
    # _internal/ subdirectory (verified by actually running a packaged build;
    # Path(sys.executable).parent silently pointed at an empty directory).
    PROJECT_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
