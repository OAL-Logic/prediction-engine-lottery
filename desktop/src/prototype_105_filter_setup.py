"""
PROTOTYPE — throwaway code, not production.

Answers wayfinder ticket #105 "Filter setup panel" (docs/wayfinder/tickets/105-filter-setup-panel.md)
on the Lottery Studio Qt Modern Interface Map (docs/wayfinder/lottery-studio-qt-interface-map.md).

Question: how should we lay out the 50 base + 18 advanced filters inside the Setup Dock, and how
should the value editor / N-of-M logic / "Generate Default Condition" flow work?

Three RADICALLY different layouts for the "Base Filters" tab, switchable with the bottom bar
(buttons or Left/Right arrow keys). Everything else (Pool Builder, Ticket Store, Advanced Filters
tab, Logical Condition tab, Generate Default Condition dialog) stays fixed across variants so the
Base Filters layout can be judged in situ, against the rest of the cockpit — not in a vacuum.

  A — Multi-column table   (tabular, all 50 rows visible via per-tier sub-tabs, no drill-down)
  B — Category tree        (master/detail: tree of filters on the left, one filter's editor on the right)
  C — Search-filtered list (search box + category combo over a flat scrollable card list)

Run with:
    .venv/bin/python desktop/src/prototype_105_filter_setup.py

Filter names/tiers are the real ones from engine.modules.filters.registry (99 real filters exist;
this prototype takes the first 50 structural/positional/algebraic ones as "Base" and the 18
historical ones as "Advanced" purely to get realistic density — the actual base/advanced split is
a follow-on decision, not something this prototype settles).
"""
import random
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QSplitter, QScrollArea, QCheckBox,
    QRadioButton, QHeaderView, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QFrame, QListWidget, QDialog, QDialogButtonBox, QInputDialog, QMessageBox,
)

from desktop.src.theme.manager import ThemeManager
from desktop.src.prototype_layout import NumberGrid

# ---------------------------------------------------------------------------
# Filter data — real names/tiers pulled from engine.modules.filters.registry.
# ---------------------------------------------------------------------------

_TIER1_STRUCTURAL = [
    ("structural_ac_value", "Arithmetic Complexity (AC)"),
    ("structural_composite_count", "Composite Number Count"),
    ("structural_decade_1", "Decade 1 (1-10) Count"),
    ("structural_decade_2", "Decade 2 (11-20) Count"),
    ("structural_decade_3", "Decade 3 (21-30) Count"),
    ("structural_decade_4", "Decade 4 (31-40) Count"),
    ("structural_decade_5", "Decade 5 (41-50) Count"),
    ("structural_decade_6", "Decade 6 (51-60) Count"),
    ("structural_digit_sum", "Total Digit Sum"),
    ("structural_even_count", "Even Number Count"),
    ("structural_fibonacci_count", "Fibonacci Number Count"),
    ("structural_high_count", "High Number Count"),
    ("structural_low_count", "Low Number Count"),
    ("structural_low_high_ratio", "Low/High Ratio"),
    ("structural_odd_count", "Odd Number Count"),
    ("structural_odd_even_ratio", "Odd/Even Ratio"),
    ("structural_prime_count", "Prime Number Count"),
    ("structural_square_count", "Square Number Count"),
    ("structural_unit_sum", "Total Unit Sum"),
]

_TIER2_POSITIONAL = [
    ("positional_ball_1_2_sum", "Ball 1+2 Sum"),
    ("positional_ball_1_range", "Ball 1 Range"),
    ("positional_ball_2_range", "Ball 2 Range"),
    ("positional_ball_3_range", "Ball 3 Range"),
    ("positional_ball_4_range", "Ball 4 Range"),
    ("positional_ball_5_6_sum", "Ball 5+6 Sum"),
    ("positional_ball_5_range", "Ball 5 Range"),
    ("positional_ball_6_range", "Ball 6 Range"),
    ("positional_first_last_distance", "First-Last Distance (Span)"),
    ("positional_gap_1_2", "Gap Ball 1-2"),
    ("positional_gap_2_3", "Gap Ball 2-3"),
    ("positional_gap_3_4", "Gap Ball 3-4"),
    ("positional_gap_4_5", "Gap Ball 4-5"),
    ("positional_gap_5_6", "Gap Ball 5-6"),
    ("positional_inner_spread", "Inner Spread (B2 to B5)"),
    ("positional_mad", "Mean Absolute Deviation"),
    ("positional_max_distance", "Maximum Distance"),
    ("positional_median", "Median Value"),
    ("positional_min_distance", "Minimum Distance"),
    ("positional_std_dev", "Standard Deviation"),
    ("positional_successive_groups", "Successive Groups Count"),
    ("positional_variance", "Ticket Variance"),
]

_TIER3_ALGEBRAIC = [
    ("algebraic_div_by_11", "Divided by 11 Count"),
    ("algebraic_div_by_12", "Divided by 12 Count"),
    ("algebraic_div_by_13", "Divided by 13 Count"),
    ("algebraic_div_by_14", "Divided by 14 Count"),
    ("algebraic_div_by_15", "Divided by 15 Count"),
    ("algebraic_div_by_16", "Divided by 16 Count"),
    ("algebraic_div_by_17", "Divided by 17 Count"),
    ("algebraic_div_by_18", "Divided by 18 Count"),
    ("algebraic_div_by_19", "Divided by 19 Count"),
    ("algebraic_div_by_20", "Divided by 20 Count"),
]

_TIER4_HISTORICAL_ADVANCED = [
    ("historical_ac_range", "Historical AC Range", "range"),
    ("historical_cold_numbers", "Cold Numbers Count", "range"),
    ("historical_common_pair", "Common Pair", "set"),
    ("historical_common_triplet", "Common Triplet", "set"),
    ("historical_consecutive_pattern", "Historical Consecutive Pattern", "range"),
    ("historical_decade_pattern", "Historical Decade Pattern", "range"),
    ("historical_digit_sum_pattern", "Historical Digit Sum Pattern", "range"),
    ("historical_hl_pattern", "Historical H/L Pattern", "range"),
    ("historical_hot_cold", "Hot-Cold Distribution", "range"),
    ("historical_median_range", "Historical Median Range", "range"),
    ("historical_oe_pattern", "Historical O/E Pattern", "range"),
    ("historical_overdue", "Overdue Numbers", "range"),
    ("historical_recent_exclusion", "Recent Draws Exclusion", "range"),
    ("historical_repeat", "Historical Repeat", "range"),
    ("historical_spread_range", "Historical Spread Range", "range"),
    ("historical_std_dev_range", "Historical StdDev Range", "range"),
    ("historical_sum_range", "Historical Sum Range", "range"),
    ("historical_unit_pattern", "Historical Unit Pattern", "range"),
]


def _guess_bounds(name: str) -> tuple[int, int]:
    """PROTOTYPE — plausible slider bounds by name pattern. Real bounds come from game rules."""
    n = name.lower()
    if "sum" in n:
        return (0, 400)
    if "ratio" in n:
        return (0, 15)
    if "count" in n:
        return (0, 15)
    if any(k in n for k in ("range", "distance", "span", "gap", "deviation", "variance", "spread")):
        return (0, 60)
    return (0, 50)


def _build_base_filters() -> list[dict]:
    raw = (_TIER1_STRUCTURAL + [(i, n, "Structural") for i, n in []])  # placeholder, replaced below
    items = []
    for tier_name, pairs in (
        ("Structural", _TIER1_STRUCTURAL),
        ("Positional", _TIER2_POSITIONAL),
        ("Algebraic", _TIER3_ALGEBRAIC),
    ):
        for uid, name in pairs:
            lo_b, hi_b = _guess_bounds(name)
            span = hi_b - lo_b
            items.append({
                "id": uid, "name": name, "tier": tier_name, "kind": "range",
                "bound": (lo_b, hi_b),
                "default": (lo_b + int(span * 0.3), lo_b + int(span * 0.65)),
            })
    return items[:50]


def _build_advanced_filters() -> list[dict]:
    items = []
    for uid, name, kind in _TIER4_HISTORICAL_ADVANCED:
        lo_b, hi_b = _guess_bounds(name)
        span = hi_b - lo_b
        items.append({
            "id": uid, "name": name, "tier": "Historical", "kind": kind,
            "bound": (lo_b, hi_b),
            "default": (lo_b + int(span * 0.3), lo_b + int(span * 0.65)),
        })
    return items[:18]


BASE_FILTERS = _build_base_filters()
ADVANCED_FILTERS = _build_advanced_filters()


# ---------------------------------------------------------------------------
# Reusable value editor — shared by all three variants.
# ---------------------------------------------------------------------------

class RangeIndicator(QWidget):
    """Cheap dual-handle stand-in: a plain bar painted between lo/hi.
    Not draggable — a real dual-handle slider needs a custom-painted widget;
    flagged here as an open implementation detail, not settled by this prototype."""

    def __init__(self, bound_lo: int, bound_hi: int, parent=None):
        super().__init__(parent)
        self.bound_lo, self.bound_hi = bound_lo, bound_hi
        self.lo, self.hi = bound_lo, bound_hi
        self.setFixedHeight(10)
        self.setMinimumWidth(50)

    def set_range(self, lo: int, hi: int):
        self.lo, self.hi = lo, hi
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#222226"))
        span = max(1, self.bound_hi - self.bound_lo)
        x0 = int((self.lo - self.bound_lo) / span * w)
        x1 = int((self.hi - self.bound_lo) / span * w)
        p.fillRect(x0, 0, max(2, x1 - x0), h, QColor("#00F0FF"))
        p.end()


class RangeEditorRow(QWidget):
    """Min spinbox + visual bar + max spinbox. The one value-editor widget reused by
    every variant — the ticket's real open question is macro-layout, not this control."""

    changed = Signal()

    def __init__(self, bound_lo: int, bound_hi: int, lo: int, hi: int, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self.spin_lo = QSpinBox()
        self.spin_lo.setRange(bound_lo, bound_hi)
        self.spin_lo.setValue(lo)
        self.spin_lo.setFixedWidth(50)
        self.bar = RangeIndicator(bound_lo, bound_hi)
        self.bar.set_range(lo, hi)
        self.spin_hi = QSpinBox()
        self.spin_hi.setRange(bound_lo, bound_hi)
        self.spin_hi.setValue(hi)
        self.spin_hi.setFixedWidth(50)
        self.spin_lo.valueChanged.connect(self._on_change)
        self.spin_hi.valueChanged.connect(self._on_change)
        lay.addWidget(self.spin_lo)
        lay.addWidget(self.bar, stretch=1)
        lay.addWidget(self.spin_hi)

    def _on_change(self):
        lo, hi = self.spin_lo.value(), self.spin_hi.value()
        if lo > hi:
            if self.sender() is self.spin_lo:
                self.spin_hi.blockSignals(True); self.spin_hi.setValue(lo); self.spin_hi.blockSignals(False)
                hi = lo
            else:
                self.spin_lo.blockSignals(True); self.spin_lo.setValue(hi); self.spin_lo.blockSignals(False)
                lo = hi
        self.bar.set_range(lo, hi)
        self.changed.emit()

    def get_range(self) -> tuple[int, int]:
        return self.spin_lo.value(), self.spin_hi.value()

    def set_range(self, lo: int, hi: int):
        self.spin_lo.blockSignals(True); self.spin_hi.blockSignals(True)
        self.spin_lo.setValue(lo); self.spin_hi.setValue(hi)
        self.spin_lo.blockSignals(False); self.spin_hi.blockSignals(False)
        self.bar.set_range(lo, hi)


# ---------------------------------------------------------------------------
# Variant A — Multi-column table (grouped by tier sub-tab, dense rows)
# ---------------------------------------------------------------------------

class BaseFiltersVariantA(QWidget):
    NAME = "Multi-column table"

    def __init__(self, filters: list[dict], parent=None):
        super().__init__(parent)
        self.filters = filters
        self.rows: dict[str, tuple[QCheckBox, RangeEditorRow]] = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(QLabel("All 50 base filters, grouped into one dense table per tier — nothing hidden behind a click."))

        tiers = QTabWidget()
        by_tier: dict[str, list[dict]] = {}
        for f in filters:
            by_tier.setdefault(f["tier"], []).append(f)

        for tier_name, items in by_tier.items():
            table = QTableWidget(len(items), 3)
            table.setHorizontalHeaderLabels(["", "Filter", "Range"])
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.verticalHeader().setDefaultSectionSize(26)
            table.verticalHeader().setVisible(False)
            for row, f in enumerate(items):
                cb = QCheckBox()
                table.setCellWidget(row, 0, cb)
                table.setItem(row, 1, QTableWidgetItem(f["name"]))
                editor = RangeEditorRow(*f["bound"], *f["default"])
                table.setCellWidget(row, 2, editor)
                self.rows[f["id"]] = (cb, editor)
            tiers.addTab(table, f"{tier_name} ({len(items)})")

        lay.addWidget(tiers, stretch=1)

    def apply_defaults(self, computed: dict[str, tuple[int, int]]):
        for fid, (lo, hi) in computed.items():
            if fid in self.rows:
                self.rows[fid][1].set_range(lo, hi)


# ---------------------------------------------------------------------------
# Variant B — Category tree with a master/detail inspector
# ---------------------------------------------------------------------------

class BaseFiltersVariantB(QWidget):
    NAME = "Category tree"

    def __init__(self, filters: list[dict], parent=None):
        super().__init__(parent)
        self.filters = filters
        self.by_id = {f["id"]: f for f in filters}
        self.checked: set[str] = set()
        self.values: dict[str, tuple[int, int]] = {f["id"]: f["default"] for f in filters}

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Filter"])
        self.tree.setColumnWidth(0, 240)
        by_tier: dict[str, list[dict]] = {}
        for f in filters:
            by_tier.setdefault(f["tier"], []).append(f)
        self.item_to_id = {}
        for tier_name, items in by_tier.items():
            root = QTreeWidgetItem(self.tree, [f"{tier_name} ({len(items)})"])
            root.setExpanded(tier_name == "Structural")
            for f in items:
                child = QTreeWidgetItem(root, [f["name"]])
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Unchecked)
                self.item_to_id[id(child)] = f["id"]
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemChanged.connect(self._on_item_checked)
        splitter.addWidget(self.tree)

        inspector = QGroupBox("Inspector — select a filter on the left")
        insp_layout = QVBoxLayout(inspector)
        self.lbl_name = QLabel("(no filter selected)")
        self.lbl_name.setStyleSheet("font-weight: bold; color: #00F0FF;")
        insp_layout.addWidget(self.lbl_name)
        self.editor_host = QVBoxLayout()
        insp_layout.addLayout(self.editor_host)
        insp_layout.addStretch()
        self.current_editor: RangeEditorRow | None = None
        self.current_id: str | None = None
        splitter.addWidget(inspector)
        splitter.setSizes([260, 340])

        lay.addWidget(splitter)

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int):
        fid = self.item_to_id.get(id(item))
        if fid is None:
            return
        f = self.by_id[fid]
        self.current_id = fid
        self.lbl_name.setText(f["name"])
        while self.editor_host.count():
            w = self.editor_host.takeAt(0).widget()
            if w:
                w.deleteLater()
        lo, hi = self.values[fid]
        editor = RangeEditorRow(*f["bound"], lo, hi)
        editor.changed.connect(lambda: self.values.__setitem__(fid, editor.get_range()))
        self.current_editor = editor
        self.editor_host.addWidget(editor)

    def _on_item_checked(self, item: QTreeWidgetItem, _col: int):
        fid = self.item_to_id.get(id(item))
        if fid is None:
            return
        if item.checkState(0) == Qt.Checked:
            self.checked.add(fid)
        else:
            self.checked.discard(fid)

    def apply_defaults(self, computed: dict[str, tuple[int, int]]):
        self.values.update(computed)
        if self.current_id in computed and self.current_editor:
            self.current_editor.set_range(*computed[self.current_id])


# ---------------------------------------------------------------------------
# Variant C — Search-filtered flat card list
# ---------------------------------------------------------------------------

class BaseFiltersVariantC(QWidget):
    NAME = "Search-filtered list"

    def __init__(self, filters: list[dict], parent=None):
        super().__init__(parent)
        self.filters = filters
        self.cards: list[tuple[dict, QFrame, QCheckBox, RangeEditorRow]] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search 50 base filters by name...")
        self.category = QComboBox()
        self.category.addItems(["All tiers", "Structural", "Positional", "Algebraic"])
        top.addWidget(self.search, stretch=1)
        top.addWidget(self.category)
        lay.addLayout(top)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: #8A8A95; font-size: 11px;")
        lay.addWidget(self.lbl_count)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self.list_layout = QVBoxLayout(inner)
        self.list_layout.setSpacing(4)

        for f in filters:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #1A1A1E; border: 1px solid #222226; border-radius: 3px; }")
            row = QHBoxLayout(card)
            row.setContentsMargins(8, 4, 8, 4)
            cb = QCheckBox()
            name_lbl = QLabel(f["name"])
            name_lbl.setMinimumWidth(220)
            editor = RangeEditorRow(*f["bound"], *f["default"])
            row.addWidget(cb)
            row.addWidget(name_lbl, stretch=1)
            row.addWidget(editor)
            self.list_layout.addWidget(card)
            self.cards.append((f, card, cb, editor))

        self.list_layout.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll, stretch=1)

        self.search.textChanged.connect(self._refilter)
        self.category.currentTextChanged.connect(self._refilter)
        self._refilter()

    def _refilter(self):
        query = self.search.text().strip().lower()
        cat = self.category.currentText()
        shown = 0
        for f, card, _cb, _editor in self.cards:
            match_text = query in f["name"].lower()
            match_cat = (cat == "All tiers") or (f["tier"] == cat)
            visible = match_text and match_cat
            card.setVisible(visible)
            shown += int(visible)
        self.lbl_count.setText(f"Showing {shown} of {len(self.cards)} base filters")

    def apply_defaults(self, computed: dict[str, tuple[int, int]]):
        for f, _card, _cb, editor in self.cards:
            if f["id"] in computed:
                editor.set_range(*computed[f["id"]])


# ---------------------------------------------------------------------------
# Advanced Filters tab (shared, constant across variants)
# ---------------------------------------------------------------------------

class AdvancedFiltersTab(QWidget):
    def __init__(self, filters: list[dict], parent=None):
        super().__init__(parent)
        self.filters = {f["id"]: f for f in filters}
        self.active: dict[str, str] = {}  # id -> human-readable value summary

        lay = QHBoxLayout(self)
        lay.addWidget(QLabel("(S04) 18 advanced filters — add/replace/delete against the active set:"))

        left = QVBoxLayout()
        left.addWidget(QLabel("Available"))
        self.available = QListWidget()
        for f in filters:
            self.available.addItem(f"{f['name']}  [{f['kind']}]")
        left.addWidget(self.available)

        mid = QVBoxLayout()
        btn_add = QPushButton("Add >>")
        btn_remove = QPushButton("<< Remove")
        btn_add.clicked.connect(self._add_selected)
        btn_remove.clicked.connect(self._remove_selected)
        mid.addStretch()
        mid.addWidget(btn_add)
        mid.addWidget(btn_remove)
        mid.addStretch()

        right = QVBoxLayout()
        right.addWidget(QLabel("Active"))
        self.active_list = QListWidget()
        right.addWidget(self.active_list)

        outer_left = QWidget(); outer_left.setLayout(left)
        outer_mid = QWidget(); outer_mid.setLayout(mid)
        outer_right = QWidget(); outer_right.setLayout(right)
        lay.addWidget(outer_left, stretch=1)
        lay.addWidget(outer_mid)
        lay.addWidget(outer_right, stretch=1)

    def _add_selected(self):
        item = self.available.currentItem()
        if not item:
            return
        name = item.text().split("  [")[0]
        f = next(f for f in self.filters.values() if f["name"] == name)
        if f["kind"] == "set":
            text, ok = QInputDialog.getText(self, "Set value", f"{f['name']} — enter numbers (comma-separated):")
            if not ok or not text.strip():
                return
            value = text.strip()
        else:
            lo, hi = f["default"]
            value = f"{lo}-{hi}"
        self.active[f["id"]] = value
        self.active_list.addItem(f"{f['name']}: {value}")

    def _remove_selected(self):
        row = self.active_list.currentRow()
        if row < 0:
            return
        self.active_list.takeItem(row)


# ---------------------------------------------------------------------------
# Logical Condition tab (shared) — AND / OR / N-of-M as a PASS RANGE
# ---------------------------------------------------------------------------

class LogicalConditionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        self.radio_and = QRadioButton("Strict Logical AND (all active filters must pass)")
        self.radio_and.setChecked(True)
        self.radio_or = QRadioButton("Strict Logical OR (any active filter may pass)")
        self.radio_nofm = QRadioButton("Fault-Tolerant N-of-M (pass count must fall in a range)")
        lay.addWidget(self.radio_and)
        lay.addWidget(self.radio_or)
        lay.addWidget(self.radio_nofm)

        nofm_row = QHBoxLayout()
        nofm_row.addWidget(QLabel("Pass if between"))
        self.spin_n_min = QSpinBox(); self.spin_n_min.setRange(0, 68); self.spin_n_min.setValue(3)
        nofm_row.addWidget(self.spin_n_min)
        nofm_row.addWidget(QLabel("and"))
        self.spin_n_max = QSpinBox(); self.spin_n_max.setRange(0, 68); self.spin_n_max.setValue(5)
        nofm_row.addWidget(self.spin_n_max)
        nofm_row.addWidget(QLabel("of the active filters match"))
        nofm_row.addStretch()
        lay.addLayout(nofm_row)
        lay.addStretch()


# ---------------------------------------------------------------------------
# Generate Default Condition — dialog + mocked computation
# ---------------------------------------------------------------------------

class GenerateDefaultsDialog(QDialog):
    """PROTOTYPE — the 'Compute' step below is a deterministic mock. The real
    implementation replaces it with storage.load_draws(limit=N) + a per-filter
    percentile pass over the historical combinations (see engine.modules.filters)."""

    def __init__(self, filters: list[dict], parent=None):
        super().__init__(parent)
        self.filters = filters
        self.computed: dict[str, tuple[int, int]] = {}
        self.setWindowTitle("Generate Default Condition")
        self.resize(360, 160)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Lookback window:"))
        self.combo = QComboBox()
        self.combo.addItems(["Last 30 Draws", "Last 50 Draws", "Last 100 Draws"])
        self.combo.setCurrentIndex(1)
        lay.addWidget(self.combo)

        self.status = QLabel("Not computed yet.")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        btn_compute = QPushButton("⚙ Compute")
        btn_compute.clicked.connect(self._compute)
        lay.addWidget(btn_compute)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("Apply to current view")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        lay.addWidget(self.buttons)

    def _compute(self):
        lookback = int(self.combo.currentText().split()[1])
        rnd = random.Random(lookback)  # deterministic mock, seeded by lookback only
        self.computed.clear()
        for f in self.filters:
            lo_b, hi_b = f["bound"]
            span = hi_b - lo_b
            lo = lo_b + int(span * rnd.uniform(0.15, 0.35))
            hi = lo_b + int(span * rnd.uniform(0.55, 0.8))
            self.computed[f["id"]] = (lo, hi)
        self.status.setText(
            f"Computed defaults for {len(self.computed)} filters from the {lookback}-draw window."
        )
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)


# ---------------------------------------------------------------------------
# Prototype shell — cockpit chrome (fixed) + Base Filters variant switcher
# ---------------------------------------------------------------------------

VARIANT_CLASSES = {
    "A": BaseFiltersVariantA,
    "B": BaseFiltersVariantB,
    "C": BaseFiltersVariantC,
}
VARIANT_ORDER = ["A", "B", "C"]


class Prototype105Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PROTOTYPE #105 — Filter Setup Panel Layouts")
        self.resize(1360, 900)
        self.theme_manager = ThemeManager()
        self.variant_key = "A"

        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.setCentralWidget(central)

        outer.addWidget(self._build_cockpit(), stretch=1)
        outer.addWidget(self._build_switcher_bar())

        self._apply_theme()
        self.setFocusPolicy(Qt.StrongFocus)

    # -- cockpit chrome (fixed across variants) ----------------------------
    def _build_cockpit(self) -> QWidget:
        main_splitter = QSplitter(Qt.Vertical)

        upper = QSplitter(Qt.Horizontal)

        pool_group = QGroupBox("Active Pool Builder")
        pool_layout = QVBoxLayout(pool_group)
        game_row = QHBoxLayout()
        game_row.addWidget(QLabel("Active Game:"))
        combo = QComboBox()
        combo.addItems(["Lotofácil (br/lotofacil)", "Mega-Sena (br/mega-sena)"])
        game_row.addWidget(combo)
        pool_layout.addLayout(game_row)
        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setWidget(NumberGrid())
        pool_layout.addWidget(grid_scroll, stretch=1)
        upper.addWidget(pool_group)

        store_group = QGroupBox("Ticket Store Cockpit (static mock)")
        store_layout = QVBoxLayout(store_group)
        table = QTableWidget(6, 3)
        table.setHorizontalHeaderLabels(["Index", "Ticket Combination", "Score"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        store_layout.addWidget(table)
        upper.addWidget(store_group)
        upper.setSizes([380, 820])

        main_splitter.addWidget(upper)

        dock = QGroupBox("Setup Dock")
        dock_layout = QHBoxLayout(dock)

        self.setup_tabs = QTabWidget()
        self.variant_stack_host = QWidget()
        self.variant_stack_layout = QVBoxLayout(self.variant_stack_host)
        self.variant_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.base_filters_widgets = {}
        self._show_variant("A", initial=True)
        self.setup_tabs.addTab(self.variant_stack_host, "Base Filters")
        self.setup_tabs.addTab(AdvancedFiltersTab(ADVANCED_FILTERS), "Advanced Filters")
        self.setup_tabs.addTab(LogicalConditionTab(), "Logical Condition")
        dock_layout.addWidget(self.setup_tabs, stretch=1)

        action_panel = QVBoxLayout()
        btn_defaults = QPushButton("⚙ GENERATE DEFAULT CONDITION")
        btn_defaults.clicked.connect(self._open_generate_defaults)
        btn_prune = QPushButton("⚡ RUN HARMONY GATE PRUNING")
        btn_prune.setStyleSheet("background-color: #FF3366; color: white; font-weight: bold; padding: 14px;")
        action_panel.addWidget(btn_defaults)
        action_panel.addWidget(btn_prune, stretch=1)
        dock_layout.addLayout(action_panel)

        main_splitter.addWidget(dock)
        main_splitter.setSizes([550, 350])
        return main_splitter

    def _show_variant(self, key: str, initial: bool = False):
        if not initial and self.variant_stack_layout.count():
            old = self.variant_stack_layout.takeAt(0).widget()
            if old:
                old.setParent(None)
        widget = self.base_filters_widgets.get(key)
        if widget is None:
            widget = VARIANT_CLASSES[key](BASE_FILTERS)
            self.base_filters_widgets[key] = widget
        self.variant_stack_layout.addWidget(widget)
        self.variant_key = key

    def _open_generate_defaults(self):
        dlg = GenerateDefaultsDialog(BASE_FILTERS, self)
        if dlg.exec() == QDialog.Accepted and dlg.computed:
            current = self.base_filters_widgets.get(self.variant_key)
            if current:
                current.apply_defaults(dlg.computed)
            QMessageBox.information(
                self, "Defaults Applied",
                f"Applied computed defaults to {len(dlg.computed)} filters in variant {self.variant_key}."
            )

    # -- switcher bar --------------------------------------------------------
    def _build_switcher_bar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet("background-color: #FF007F;")
        bar.setFixedHeight(40)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)

        btn_prev = QPushButton("←")
        btn_next = QPushButton("→")
        for b in (btn_prev, btn_next):
            b.setFixedWidth(36)
            b.setStyleSheet("background-color: #1A0010; color: white; font-weight: bold; border-radius: 4px;")

        self.lbl_variant = QLabel()
        self.lbl_variant.setAlignment(Qt.AlignCenter)
        self.lbl_variant.setStyleSheet("color: white; font-weight: bold;")

        btn_prev.clicked.connect(lambda: self._cycle(-1))
        btn_next.clicked.connect(lambda: self._cycle(1))

        lay.addStretch()
        lay.addWidget(btn_prev)
        lay.addWidget(self.lbl_variant, stretch=0)
        lay.addWidget(btn_next)
        lay.addStretch()

        self._update_variant_label()
        return bar

    def _update_variant_label(self):
        cls = VARIANT_CLASSES[self.variant_key]
        self.lbl_variant.setText(f"{self.variant_key} — {cls.NAME}   (←/→ to switch)")

    def _cycle(self, direction: int):
        idx = VARIANT_ORDER.index(self.variant_key)
        idx = (idx + direction) % len(VARIANT_ORDER)
        self._show_variant(VARIANT_ORDER[idx])
        self._update_variant_label()

    def keyPressEvent(self, event):
        focused = QApplication.focusWidget()
        if isinstance(focused, (QLineEdit, QSpinBox, QComboBox)):
            return super().keyPressEvent(event)
        if event.key() == Qt.Key_Left:
            self._cycle(-1)
            return
        if event.key() == Qt.Key_Right:
            self._cycle(1)
            return
        super().keyPressEvent(event)

    def _apply_theme(self):
        base = self.theme_manager.generate_stylesheet("Sleek Dark Mode")
        extra = """
            QCheckBox::indicator, QRadioButton::indicator {
                width: 14px; height: 14px;
                border: 1px solid #00F0FF;
                background-color: #121214;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #FF3366;
                border-color: #FF3366;
            }
            QTreeWidget {
                background-color: #121214;
                border: 1px solid #222226;
            }
            QLineEdit {
                padding: 4px;
            }
        """
        self.setStyleSheet(base + extra)


def main():
    app = QApplication(sys.argv)
    window = Prototype105Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
