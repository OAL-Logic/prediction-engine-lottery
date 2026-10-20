import logging
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTreeWidget, QTreeWidgetItem, QGroupBox, QTextEdit, 
    QMessageBox, QSplitter, QProgressBar, QListWidget, QListWidgetItem,
    QTabWidget, QRadioButton, QSpinBox, QInputDialog, QHeaderView
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QPainter

from engine.modules.filters import registry
from engine.modules.storage import storage
from engine.cli.utils import get_adapter
from desktop.src.theme.manager import THEMES, DEFAULT_THEME

logger = logging.getLogger(__name__)

def guess_bounds(uid: str, display_name: str) -> tuple[int, int]:
    n = (uid + " " + display_name).lower()
    if "sum" in n:
        return (0, 400)
    if "ratio" in n:
        return (0, 15)
    if "count" in n:
        return (0, 15)
    if any(k in n for k in ("range", "distance", "span", "gap", "deviation", "variance", "spread")):
        return (0, 60)
    return (0, 50)


class RangeIndicator(QWidget):
    def __init__(self, bound_lo: int, bound_hi: int, colors, parent=None):
        super().__init__(parent)
        self.bound_lo, self.bound_hi = bound_lo, bound_hi
        self.lo, self.hi = bound_lo, bound_hi
        self.colors = colors
        self.setFixedHeight(12)
        self.setMinimumWidth(80)

    def set_range(self, lo: int, hi: int):
        self.lo, self.hi = lo, hi
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        # Draw background track
        p.fillRect(0, 2, w, h - 4, QColor(self.colors["border"]))

        span = max(1, self.bound_hi - self.bound_lo)
        x0 = int((self.lo - self.bound_lo) / span * w)
        x1 = int((self.hi - self.bound_lo) / span * w)
        # Draw selected range track
        p.fillRect(x0, 2, max(2, x1 - x0), h - 4, QColor(self.colors["primary"]))
        p.end()


class RangeEditorRow(QWidget):
    changed = Signal()

    def __init__(self, bound_lo: int, bound_hi: int, lo: int, hi: int, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.spin_lo = QSpinBox()
        self.spin_lo.setRange(bound_lo, bound_hi)
        self.spin_lo.setValue(lo)
        self.spin_lo.setFixedWidth(50)

        self.bar = RangeIndicator(bound_lo, bound_hi, colors)
        self.bar.set_range(lo, hi)

        self.spin_hi = QSpinBox()
        self.spin_hi.setRange(bound_lo, bound_hi)
        self.spin_hi.setValue(hi)
        self.spin_hi.setFixedWidth(50)

        self._style_spins()

        self.spin_lo.valueChanged.connect(self._on_change)
        self.spin_hi.valueChanged.connect(self._on_change)
        
        lay.addWidget(self.spin_lo)
        lay.addWidget(self.bar, stretch=1)
        lay.addWidget(self.spin_hi)

    def _on_change(self):
        lo, hi = self.spin_lo.value(), self.spin_hi.value()
        if lo > hi:
            if self.sender() is self.spin_lo:
                self.spin_hi.blockSignals(True)
                self.spin_hi.setValue(lo)
                self.spin_hi.blockSignals(False)
                hi = lo
            else:
                self.spin_lo.blockSignals(True)
                self.spin_lo.setValue(hi)
                self.spin_lo.blockSignals(False)
                lo = hi
        self.bar.set_range(lo, hi)
        self.changed.emit()

    def _style_spins(self):
        style = (
            f"background-color: {self.colors['panel']}; "
            f"border: 1px solid {self.colors['border']}; "
            f"color: {self.colors['text']};"
        )
        self.spin_lo.setStyleSheet(style)
        self.spin_hi.setStyleSheet(style)

    def apply_theme(self, colors: dict):
        self.colors = colors
        self.bar.colors = colors
        self.bar.update()
        self._style_spins()

    def get_range(self) -> tuple[int, int]:
        return self.spin_lo.value(), self.spin_hi.value()

    def set_range(self, lo: int, hi: int):
        self.spin_lo.blockSignals(True)
        self.spin_hi.blockSignals(True)
        self.spin_lo.setValue(lo)
        self.spin_hi.setValue(hi)
        self.spin_lo.blockSignals(False)
        self.spin_hi.blockSignals(False)
        self.bar.set_range(lo, hi)


class FiltersTab(QWidget):
    """Cockpit interface for the vectorized 5-Tier Harmony Gate filters with elimination auditing and assistant."""
    
    # Emits when the active filters list changes
    filters_updated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self._active_filters = []
        self.adv_active = {}  # uid -> value summary (str)
        self.range_editors: list[RangeEditorRow] = []
        # Default-theme fallback; apply_theme() overwrites these once main.py
        # wires up the real ThemeManager tokens.
        self.colors = THEMES[DEFAULT_THEME]

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header: launches the guided Filter Assistant wizard — a separate,
        # simpler workflow from the tabs below (built-in default thresholds,
        # sequential elimination funnel) rather than a replacement for them.
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Manual Setup (below) or:"))
        self.btn_filter_assistant = QPushButton("🧙 Launch Filter Assistant...")
        self.btn_filter_assistant.setToolTip(
            "Lottery Studio's 'Assistant Filter' equivalent — a guided, tier-by-tier filter\n"
            "picker ending in an elimination-funnel report. Simpler than the tabs below:\n"
            "no custom ranges, just pick filters by name and see what survives."
        )
        self.btn_filter_assistant.clicked.connect(self.launch_filter_assistant)
        header_layout.addWidget(self.btn_filter_assistant)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Tab 1: Base Filters (Tiers 1, 2, 3)
        self.base_tab = QWidget()
        base_layout = QVBoxLayout(self.base_tab)
        base_layout.setContentsMargins(4, 4, 4, 4)
        
        self.base_tree = QTreeWidget()
        self.base_tree.setHeaderLabels(["Filter Name", "Range Bounds"])
        self.base_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.base_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.base_tree.itemChanged.connect(self.on_filter_toggled)
        base_layout.addWidget(self.base_tree)
        
        self.tab_widget.addTab(self.base_tab, "Base Filters")

        # Tab 2: Advanced Filters (Tiers 4, 5)
        self.adv_tab = QWidget()
        adv_layout = QHBoxLayout(self.adv_tab)
        adv_layout.setContentsMargins(8, 8, 8, 8)
        
        left_box = QVBoxLayout()
        left_box.addWidget(QLabel("Available Advanced Filters"))
        self.adv_available = QListWidget()
        left_box.addWidget(self.adv_available)
        
        mid_box = QVBoxLayout()
        self.btn_add_adv = QPushButton("Add >>")
        self.btn_remove_adv = QPushButton("<< Remove")
        self.btn_add_adv.clicked.connect(self.add_advanced_filter)
        self.btn_remove_adv.clicked.connect(self.remove_advanced_filter)
        mid_box.addStretch()
        mid_box.addWidget(self.btn_add_adv)
        mid_box.addWidget(self.btn_remove_adv)
        mid_box.addStretch()
        
        right_box = QVBoxLayout()
        right_box.addWidget(QLabel("Active Advanced Filters"))
        self.adv_active_list = QListWidget()
        right_box.addWidget(self.adv_active_list)
        
        adv_layout.addLayout(left_box, stretch=1)
        adv_layout.addLayout(mid_box)
        adv_layout.addLayout(right_box, stretch=1)
        
        self.tab_widget.addTab(self.adv_tab, "Advanced Filters")

        # Tab 3: Logical Conditions
        self.logic_tab = QWidget()
        logic_layout = QVBoxLayout(self.logic_tab)
        logic_layout.setContentsMargins(12, 12, 12, 12)
        logic_layout.setSpacing(10)
        
        self.radio_and = QRadioButton("Strict Logical AND (all active filters must pass)")
        self.radio_and.setChecked(True)
        self.radio_or = QRadioButton("Strict Logical OR (any active filter may pass)")
        self.radio_nofm = QRadioButton("Fault-Tolerant N-of-M (pass count must fall in a range)")
        
        logic_layout.addWidget(self.radio_and)
        logic_layout.addWidget(self.radio_or)
        logic_layout.addWidget(self.radio_nofm)
        
        nofm_row = QHBoxLayout()
        nofm_row.addWidget(QLabel("Pass if between"))
        self.spin_n_min = QSpinBox()
        self.spin_n_min.setRange(0, 100)
        self.spin_n_min.setValue(3)
        nofm_row.addWidget(self.spin_n_min)
        nofm_row.addWidget(QLabel("and"))
        self.spin_n_max = QSpinBox()
        self.spin_n_max.setRange(0, 100)
        self.spin_n_max.setValue(5)
        nofm_row.addWidget(self.spin_n_max)
        nofm_row.addWidget(QLabel("of the active filters match"))
        nofm_row.addStretch()
        logic_layout.addLayout(nofm_row)
        logic_layout.addStretch()
        
        self.tab_widget.addTab(self.logic_tab, "Logical Fault-Tolerance")

        # Load lists of filters
        self.populate_base_tree()
        self.populate_advanced_lists()

    def apply_theme(self, colors: dict):
        self.colors = colors
        for editor in self.range_editors:
            editor.apply_theme(colors)

    def set_lottery(self, lottery_id: str):
        self.active_lottery = lottery_id

    def populate_base_tree(self):
        self.base_tree.blockSignals(True)
        self.base_tree.clear()
        self.range_editors.clear()

        # Define Tiers
        tier_names = {
            1: "Tier 1: Structural Invariants",
            2: "Tier 2: Positional & Distance",
            3: "Tier 3: Algebraic & Modular"
        }

        # Create root items
        self.tier_items = {}
        for tier in range(1, 4):
            root_node = QTreeWidgetItem(self.base_tree)
            root_node.setText(0, tier_names[tier])
            root_node.setFlags(root_node.flags() & ~Qt.ItemIsUserCheckable)
            root_node.setExpanded(tier == 1)
            self.tier_items[tier] = root_node

        try:
            registry._discover()
            for uid, mod in sorted(registry._module_map.items()):
                f = registry.get(uid)
                if f and f.tier in (1, 2, 3):
                    child_node = QTreeWidgetItem(self.tier_items[f.tier])
                    child_node.setText(0, f.display_name)
                    child_node.setFlags(child_node.flags() | Qt.ItemIsUserCheckable)
                    child_node.setCheckState(0, Qt.Unchecked)
                    # Hidden reference to unique ID in column 2
                    child_node.setText(2, f.unique_id)
                    
                    # Create range editor widget
                    lo_b, hi_b = guess_bounds(f.unique_id, f.display_name)
                    span = hi_b - lo_b
                    lo = lo_b + int(span * 0.25)
                    hi = lo_b + int(span * 0.75)
                    
                    editor = RangeEditorRow(lo_b, hi_b, lo, hi, self.colors)
                    editor.changed.connect(self.on_base_filter_changed)
                    self.range_editors.append(editor)

                    self.base_tree.setItemWidget(child_node, 1, editor)
        except Exception as e:
            logger.exception("Error populating base filters tree.")
            QMessageBox.critical(self, "Registry Error", f"Failed to load filter registry:\n{str(e)}")

        self.base_tree.blockSignals(False)

    def populate_advanced_lists(self):
        self.adv_available.clear()
        try:
            registry._discover()
            for uid, mod in sorted(registry._module_map.items()):
                f = registry.get(uid)
                if f and f.tier in (4, 5):
                    item = QListWidgetItem(f"{f.display_name} (Tier {f.tier})")
                    item.setData(Qt.UserRole, f.unique_id)
                    self.adv_available.addItem(item)
        except Exception as e:
            logger.exception("Error populating advanced filter lists.")

    def add_advanced_filter(self):
        item = self.adv_available.currentItem()
        if not item:
            return
        uid = item.data(Qt.UserRole)
        f = registry.get(uid)
        if not f:
            return
            
        if uid.startswith("custom_") or "set" in uid.lower():
            text, ok = QInputDialog.getText(
                self, "Configure Advanced Filter", 
                f"Enter numbers (comma-separated) for '{f.display_name}':"
            )
            if not ok or not text.strip():
                return
            val = text.strip()
        else:
            lo_b, hi_b = guess_bounds(uid, f.display_name)
            span = hi_b - lo_b
            lo = lo_b + int(span * 0.3)
            hi = lo_b + int(span * 0.6)
            text, ok = QInputDialog.getText(
                self, "Configure Range", 
                f"Enter range 'min-max' between {lo_b} and {hi_b} for '{f.display_name}':",
                text=f"{lo}-{hi}"
            )
            if not ok or not text.strip():
                return
            val = text.strip()

        self.adv_active[uid] = val
        self.refresh_active_advanced_list()
        self.filters_updated.emit(self.get_active_filters())

    def remove_advanced_filter(self):
        item = self.adv_active_list.currentItem()
        if not item:
            return
        uid = item.data(Qt.UserRole)
        if uid in self.adv_active:
            del self.adv_active[uid]
            self.refresh_active_advanced_list()
            self.filters_updated.emit(self.get_active_filters())

    def refresh_active_advanced_list(self):
        self.adv_active_list.clear()
        for uid, val in self.adv_active.items():
            f = registry.get(uid)
            display_name = f.display_name if f else uid
            item = QListWidgetItem(f"{display_name}: {val}")
            item.setData(Qt.UserRole, uid)
            self.adv_active_list.addItem(item)

    def on_filter_toggled(self, item, column):
        self.filters_updated.emit(self.get_active_filters())

    def on_base_filter_changed(self):
        self.filters_updated.emit(self.get_active_filters())

    def get_active_filters(self) -> list:
        active = []
        active_ids = []
        root = self.base_tree.invisibleRootItem()
        for i in range(root.childCount()):
            tier_node = root.child(i)
            for j in range(tier_node.childCount()):
                child = tier_node.child(j)
                if child.checkState(0) == Qt.Checked:
                    uid = child.text(2)
                    active_ids.append(uid)
                    editor = self.base_tree.itemWidget(child, 1)
                    if isinstance(editor, RangeEditorRow):
                        lo, hi = editor.get_range()
                        active.append({
                            "id": uid,
                            "type": "base",
                            "lo": lo,
                            "hi": hi
                        })
                        
        for uid, val in self.adv_active.items():
            active_ids.append(uid)
            active.append({
                "id": uid,
                "type": "advanced",
                "val": val
            })
        self._active_filters = active_ids
        return active

    def get_logical_condition(self) -> dict:
        mode = "AND"
        if self.radio_or.isChecked():
            mode = "OR"
        elif self.radio_nofm.isChecked():
            mode = "N-of-M"
        return {
            "mode": mode,
            "n_min": self.spin_n_min.value(),
            "n_max": self.spin_n_max.value()
        }

    def apply_computed_limits(self, limits: dict):
        self.base_tree.blockSignals(True)
        root = self.base_tree.invisibleRootItem()
        for i in range(root.childCount()):
            tier_node = root.child(i)
            for j in range(tier_node.childCount()):
                child = tier_node.child(j)
                uid = child.text(2)
                if uid in limits:
                    lo, hi = limits[uid]
                    editor = self.base_tree.itemWidget(child, 1)
                    if isinstance(editor, RangeEditorRow):
                        editor.set_range(lo, hi)
                        child.setCheckState(0, Qt.Checked)
        self.base_tree.blockSignals(False)
        self.filters_updated.emit(self.get_active_filters())

    def launch_filter_assistant(self):
        """Opens the guided Filter Assistant wizard (Lottery Studio 'Assistant Filter')
        for the active lottery. Self-contained — the wizard runs its own
        elimination-funnel job and doesn't touch this tab's own filter state,
        matching how the CLI's filter-assistant is independent of filter-funnel."""
        try:
            rules = get_adapter(self.active_lottery).rules
        except Exception as e:
            QMessageBox.critical(self, "Registry Error", f"Failed to load rules for '{self.active_lottery}':\n{str(e)}")
            return

        main_win = self.window()
        thread_manager = getattr(main_win, "thread_manager", None)

        from desktop.src.widgets.filter_assistant_wizard import FilterAssistantWizard
        wizard = FilterAssistantWizard(rules, thread_manager=thread_manager, parent=self)
        wizard.exec()
