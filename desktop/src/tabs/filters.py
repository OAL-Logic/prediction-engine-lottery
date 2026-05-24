import logging
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTreeWidget, QTreeWidgetItem, QGroupBox, QTextEdit, 
    QMessageBox, QSplitter, QProgressBar, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal

from engine.modules.filters import registry
from engine.modules.storage import storage
from engine.cli.utils import get_adapter

logger = logging.getLogger(__name__)

class FiltersTab(QWidget):
    """Cockpit interface for the vectorized 5-Tier Harmony Gate filters with elimination auditing and assistant."""
    
    # Emits when the active filters list changes
    filters_updated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_lottery = "br/lotofacil"
        self._active_filters = []
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Splitter to allow resizing panels
        splitter = QSplitter(Qt.Horizontal)

        # Panel 1: 5-Tier Filter Selection Tree
        left_group = QGroupBox("5-Tier Vectorized Harmony Gate")
        left_layout = QVBoxLayout(left_group)
        
        self.filter_tree = QTreeWidget()
        self.filter_tree.setHeaderLabels(["Filter Name", "Tier ID"])
        self.filter_tree.setColumnWidth(0, 300)
        self.filter_tree.itemChanged.connect(self.on_filter_toggled)
        self.filter_tree.itemClicked.connect(self.on_filter_clicked)
        
        left_layout.addWidget(self.filter_tree)

        # Filter Assistant Button
        self.assistant_button = QPushButton("⚡ RUN FILTER ASSISTANT (LOOKBACK)")
        self.assistant_button.setStyleSheet("""
            QPushButton {
                background-color: #008f11;
                color: #ffffff;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #000000;
            }
        """)
        self.assistant_button.setToolTip("Analyzes the last 50 draws and auto-selects filters with >= 90% stability.")
        self.assistant_button.clicked.connect(self.run_filter_assistant)
        left_layout.addWidget(self.assistant_button)
        
        splitter.addWidget(left_group)

        # Right Panel: Split into Info Panel and Elimination Auditor
        right_splitter = QSplitter(Qt.Vertical)

        # Panel 2.1: Selected Filter Information Details
        info_group = QGroupBox("Filter Specifications")
        info_layout = QVBoxLayout(info_group)
        
        self.info_details = QTextEdit()
        self.info_details.setReadOnly(True)
        self.info_details.setPlaceholderText("Select a filter to inspect its vector description...")
        self.info_details.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 11px;")
        
        info_layout.addWidget(self.info_details)
        right_splitter.addWidget(info_group)

        # Panel 2.2: Elimination Auditor
        auditor_group = QGroupBox("Real-Time Elimination Auditor")
        auditor_layout = QVBoxLayout(auditor_group)
        
        auditor_desc = QLabel("Enter space-separated numbers (one ticket per line) to audit:")
        auditor_layout.addWidget(auditor_desc)

        self.txt_audit_tickets = QTextEdit()
        self.txt_audit_tickets.setPlaceholderText("e.g.\n01 02 03 04 05 06 07 08 09 10 11 12 13 14 15\n02 03 04 05 06 07 08 09 10 11 12 13 14 15 16")
        self.txt_audit_tickets.setStyleSheet("font-family: 'JetBrains Mono';")
        auditor_layout.addWidget(self.txt_audit_tickets, stretch=1)

        self.audit_button = QPushButton("🛡️ AUDIT PASS RATE & ELIMINATIONS")
        self.audit_button.setStyleSheet("padding: 8px; font-weight: bold;")
        self.audit_button.clicked.connect(self.run_elimination_audit)
        auditor_layout.addWidget(self.audit_button)

        self.audit_progress = QProgressBar()
        self.audit_progress.setValue(0)
        self.audit_progress.setTextVisible(True)
        auditor_layout.addWidget(self.audit_progress)

        self.audit_results = QListWidget()
        self.audit_results.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px;")
        auditor_layout.addWidget(self.audit_results, stretch=1)

        right_splitter.addWidget(auditor_group)
        splitter.addWidget(right_splitter)

        main_layout.addWidget(splitter)

        # Load list of filters
        self.populate_filter_tree()

    def set_lottery(self, lottery_id: str):
        self.active_lottery = lottery_id
        # Clear audit results when active game changes
        self.audit_results.clear()
        self.audit_progress.setValue(0)

    def populate_filter_tree(self):
        """Discovers and catalogs all 100+ filters into the 5-Tier tree hierarchy."""
        self.filter_tree.blockSignals(True)
        self.filter_tree.clear()

        # Define the Tiers
        tier_names = {
            1: "Tier 1: Structural Invariants (Odd/Even, Primes)",
            2: "Tier 2: Positional & Distance (Span, runs)",
            3: "Tier 3: Algebraic & Modular (Div N, residues)",
            4: "Tier 4: Historical & Temporal (Repeats, skips)",
            5: "Tier 5: Custom Semantic (Key locks, contains)"
        }

        # Create Tier Root Nodes
        self.tier_items = {}
        for tier in range(1, 6):
            root_node = QTreeWidgetItem(self.filter_tree)
            root_node.setText(0, tier_names[tier])
            root_node.setText(1, f"Tier {tier}")
            root_node.setFlags(root_node.flags() & ~Qt.ItemIsUserCheckable)
            root_node.setExpanded(tier == 1) # Expand structural by default
            self.tier_items[tier] = root_node

        # Query all filters in registry
        try:
            registry._discover()
            for uid, mod in sorted(registry._module_map.items()):
                f = registry.get(uid)
                if f:
                    child_node = QTreeWidgetItem(self.tier_items[f.tier])
                    child_node.setText(0, f.display_name)
                    child_node.setText(1, f.unique_id)
                    child_node.setFlags(child_node.flags() | Qt.ItemIsUserCheckable)
                    child_node.setCheckState(0, Qt.Unchecked)
        except Exception as e:
            logger.exception("Error populating filters tree.")
            QMessageBox.critical(self, "Registry Error", f"Failed to load filter registry:\n{str(e)}")

        self.filter_tree.blockSignals(False)

    def on_filter_clicked(self, item, column):
        """Displays details of the selected filter in the info pane."""
        uid = item.text(1)
        if uid.startswith("Tier"):
            self.info_details.setText(f"🎨 {item.text(0)}\nContains a logical group of analytical filters.")
            return

        f = registry.get(uid)
        if f:
            desc = (
                f"🏷️ DISPLAY NAME : {f.display_name}\n"
                f"🔑 UNIQUE ID    : {f.unique_id}\n"
                f"🏛️ TARGET TIER  : Tier {f.tier}\n"
                f"⚡ DESCRIPTION  : {f.description or 'No vector description available.'}\n"
            )
            self.info_details.setText(desc)

    def on_filter_toggled(self, item, column):
        """Updates internal active filters list when tree checkboxes are clicked."""
        uid = item.text(1)
        if uid.startswith("Tier"):
            return

        is_checked = (item.checkState(0) == Qt.Checked)
        if is_checked:
            if uid not in self._active_filters:
                self._active_filters.append(uid)
        else:
            if uid in self._active_filters:
                self._active_filters.remove(uid)

        self.filters_updated.emit(self._active_filters)

    def get_active_filters(self) -> list:
        return self._active_filters

    def run_filter_assistant(self):
        """Assistant Wizard: back-tests filters on last 50 drawings and checks stable ones."""
        try:
            # 1. Fetch last 50 drawings
            df = storage.load_draws(self.active_lottery, limit=50)
            if df.empty or len(df) < 5:
                QMessageBox.warning(self, "Insufficient Data", "Need at least 10 historical drawings in DuckDB to compute stability.")
                return

            # Parse drawing combinations into array
            combs = np.array(df["numbers"].tolist())
            adapter = get_adapter(self.active_lottery)
            rules = adapter.rules

            stable_filters = []
            
            # 2. Back-test each filter in the registry
            for uid in sorted(registry._module_map.keys()):
                f = registry.get(uid)
                if not f:
                    continue
                try:
                    passed = f.apply(combs, rules)
                    pass_rate = np.sum(passed) / len(passed)
                    
                    # Core rule: Stability >= 90% in historical back-pass
                    if pass_rate >= 0.90:
                        stable_filters.append(uid)
                except Exception:
                    pass

            # 3. Synchronize with the UI Tree
            self.filter_tree.blockSignals(True)
            self._active_filters.clear()

            # Iterate tree and check stable filters
            root = self.filter_tree.invisibleRootItem()
            for i in range(root.childCount()):
                tier_item = root.child(i)
                for j in range(tier_item.childCount()):
                    child = tier_item.child(j)
                    uid = child.text(1)
                    if uid in stable_filters:
                        child.setCheckState(0, Qt.Checked)
                        self._active_filters.append(uid)
                    else:
                        child.setCheckState(0, Qt.Unchecked)

            self.filter_tree.blockSignals(False)
            self.filters_updated.emit(self._active_filters)

            QMessageBox.information(
                self, "Filter Assistant Complete",
                f"Back-pass scan complete on last {len(df)} draws!\n\n"
                f"Auto-selected {len(stable_filters)} stable filters demonstrating >= 90% historical frequency."
            )

        except Exception as e:
            logger.exception("Filter assistant failed.")
            QMessageBox.critical(self, "Assistant Failure", f"Wizard crashed:\n{str(e)}")

    def run_elimination_audit(self):
        """Audits custom ticket lines against active filters, displaying elimination rates."""
        if not self._active_filters:
            QMessageBox.warning(self, "No Active Filters", "Please check at least one filter in the 5-Tier tree first.")
            return

        text = self.txt_audit_tickets.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No Tickets Provided", "Please enter/paste some ticket combinations to evaluate.")
            return

        try:
            # Parse combinations
            lines = text.split("\n")
            tickets_list = []
            for l in lines:
                nums = [int(x) for x in l.replace(",", " ").split() if x.isdigit()]
                if nums:
                    tickets_list.append(nums)

            if not tickets_list:
                QMessageBox.warning(self, "Parsing Error", "No valid integer combinations could be parsed.")
                return

            combinations = np.array(tickets_list)
            adapter = get_adapter(self.active_lottery)
            rules = adapter.rules

            self.audit_results.clear()
            self.audit_progress.setValue(10)

            # Audit each active filter
            eliminated_counts = {}
            passed_mask = np.ones(combinations.shape[0], dtype=bool)

            for idx, uid in enumerate(self._active_filters):
                f = registry.get(uid)
                if not f:
                    continue
                
                passed = f.apply(combinations, rules)
                eliminated = ~passed
                eliminated_counts[uid] = np.sum(eliminated)
                passed_mask &= passed
                
                # Update progress incrementally
                pct = 10 + int((idx + 1) / len(self._active_filters) * 80)
                self.audit_progress.setValue(pct)

            total_tickets = combinations.shape[0]
            passed_tickets = np.sum(passed_mask)
            pass_rate = (passed_tickets / total_tickets) * 100

            # 4. Display report in the list widget
            # Summary header
            header_item = QListWidgetItem(f"═════ AUDIT SUMMARY (Total: {total_tickets}) ═════")
            header_item.setForeground(Qt.green if pass_rate > 0 else Qt.red)
            self.audit_results.addItem(header_item)
            
            self.audit_results.addItem(f"Tickets Passing All: {passed_tickets} / {total_tickets} ({pass_rate:.2f}%)")
            self.audit_results.addItem(f"Tickets Eliminated : {total_tickets - passed_tickets} ({100 - pass_rate:.2f}%)")
            self.audit_results.addItem("")
            
            self.audit_results.addItem("═════ ELIMINATIONS BY VECTOR ═════")
            
            # Sort filters by elimination power
            sorted_elims = sorted(eliminated_counts.items(), key=lambda x: x[1], reverse=True)
            for uid, elim_count in sorted_elims:
                f = registry.get(uid)
                elim_pct = (elim_count / total_tickets) * 100
                display_str = f"[{elim_pct:6.2f}%] ({elim_count:4d} cut) ➔ {f.display_name if f else uid}"
                
                item = QListWidgetItem(display_str)
                if elim_count > 0:
                    item.setForeground(Qt.yellow)
                self.audit_results.addItem(item)

            self.audit_progress.setValue(100)

        except Exception as e:
            logger.exception("Audit crashed.")
            QMessageBox.critical(self, "Audit Failure", f"Failed to run elimination scan:\n{str(e)}")
