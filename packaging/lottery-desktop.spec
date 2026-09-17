# PyInstaller spec for the desktop app ("Prophet Dashboard").
#
# Build (from the repo root, with the project installed — `pip install -e ".[desktop]"`
# at minimum, `.[all]` for every strategy tier the desktop app can invoke):
#   pyinstaller packaging/lottery-desktop.spec --distpath dist --workpath build --noconfirm
#
# Produces a --onedir build (dist/ProphetDashboard/) rather than --onefile: this app
# bundles duckdb, matplotlib, PySide6, and optionally torch/sklearn/lightgbm/xgboost/
# catboost, which onefile's extract-every-launch model handles badly (slow startup,
# and some of those libraries' native extensions don't tolerate running from a temp
# extraction dir). See engine/_paths.py for how the bundled app locates data/ at
# runtime — that's the one thing that has to stay in sync with the `datas` entry below.
#
# This produces a build for whatever OS/architecture PyInstaller runs on — there is
# no cross-compilation. Windows/macOS/Linux artifacts come from running this same
# spec on each OS (see .github/workflows/build-desktop.yml for the CI matrix that
# does exactly that).

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None
REPO_ROOT = Path(SPECPATH).resolve().parent

# Every strategy/adapter/CLI-command module is reachable dynamically (get_strategy(),
# get_adapter(), typer's lazy `from engine.cli.commands.X import X as impl` — see
# CHANGELOG 11.7.0 for what silent drift there looks like when this kind of dynamic
# wiring falls out of sync). PyInstaller's static import analysis can't see any of
# that, so collect both packages unconditionally rather than hand-maintaining a
# hiddenimports list that will inevitably drift the same way.
hiddenimports = (
    collect_submodules("engine")
    + collect_submodules("desktop")
    + ["duckdb", "PySide6.QtPrintSupport", "PySide6.QtSvg"]
)

# data/ ships as real data (registry.yaml, lottery.db, cached weather/seismic/solar
# snapshots) — not Python source — so it's a `datas` entry. `datas=[(src, "data")]`
# always lands at sys._MEIPASS/data at runtime regardless of onedir/onefile mode,
# which is exactly what engine._paths.PROJECT_ROOT reads when sys.frozen is set.
datas = [(str(REPO_ROOT / "data"), "data")]
datas += collect_data_files("astropy")  # IERS/leap-second tables etc.

a = Analysis(
    [str(REPO_ROOT / "desktop" / "src" / "main.py")],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["nvidia", "cuda", "cusparselt"],  # multi-GB CUDA redistributables torch's wheel bundles; unused (no GPU dispatch yet)
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProphetDashboard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # GUI app — no terminal window on Windows/macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ProphetDashboard",
)
