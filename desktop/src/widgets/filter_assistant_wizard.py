"""
Filter Assistant Wizard 🧙
==========================
GUI counterpart to `lottery filter-assistant` — SamLotto's "Assistant
Filter" (detailed_features.md §3): a guided, tier-by-tier walk through the
filter registry that doesn't require already knowing unique_ids, ending in
an elimination-funnel report. Deliberately a different workflow from
FiltersTab (which is the full custom-range-editor / AND-OR-N-of-M
experience): here every filter runs with its own built-in default
threshold (VectorizedFilter.apply()'s own logic — no range editors), the
chain is evaluated in strict sequence stopping early at zero survivors, and
each combination of the candidate pool is checked, not a Ticket Store batch
— exactly matching engine.cli.commands.filter_funnel's semantics, which
this reuses rather than reimplements.
"""

from __future__ import annotations

import logging
import traceback
from itertools import combinations
from math import comb

import numpy as np
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QPushButton,
)

from engine.cli.commands.filter_funnel import MAX_COMBINATIONS
from engine.modules.filters import registry

logger = logging.getLogger(__name__)


class FunnelJobSignals(QObject):
    finished = Signal(list, int)   # funnel stage rows, starting total
    failed = Signal(str)


class FilterAssistantFunnelJob(QThread):
    """
    Same computation as engine.cli.commands.filter_funnel.filter_funnel():
    generate every C(pool, pick) combination from the candidate pool, then
    run the chosen filters in order, tracking survivors after each one and
    stopping early if a stage empties the pool. Thin QThread wrapper — reuses
    VectorizedFilter.apply() exactly as the CLI command and PruningJob do;
    no filter logic duplicated.
    """

    def __init__(self, rules, pool_numbers: list[int], filter_ids: list[str], parent: QObject | None = None):
        super().__init__(parent)
        self.rules = rules
        self.pool_numbers = pool_numbers
        self.filter_ids = filter_ids
        self.signals = FunnelJobSignals()

    def run(self) -> None:
        try:
            total = comb(len(self.pool_numbers), self.rules.pick_count)
            if total > MAX_COMBINATIONS:
                raise ValueError(
                    f"Pool of {len(self.pool_numbers)} numbers yields C({len(self.pool_numbers)},"
                    f"{self.rules.pick_count}) = {total:,} combinations, above the "
                    f"{MAX_COMBINATIONS:,} safety cap. Use a smaller pool."
                )

            combos = np.array(list(combinations(self.pool_numbers, self.rules.pick_count)))
            survivors = np.ones(combos.shape[0], dtype=bool)

            rows = [{"stage": 0, "filter": "(starting pool)", "before": None, "after": total, "eliminated": None}]
            for i, uid in enumerate(self.filter_ids, start=1):
                f = registry.get(uid)
                before = int(survivors.sum())
                if f is None:
                    rows.append({"stage": i, "filter": f"{uid} (not found)", "before": before, "after": before, "eliminated": 0})
                    continue
                mask = f.apply(combos, self.rules)
                survivors &= mask
                after = int(survivors.sum())
                rows.append({"stage": i, "filter": f.display_name, "before": before, "after": after, "eliminated": before - after})
                if after == 0:
                    break

            self.signals.finished.emit(rows, total)
        except Exception as exc:
            logger.exception("Filter Assistant funnel job failed.")
            self.signals.failed.emit(str(exc) or type(exc).__name__)


class _TierPage(QWizardPage):
    """One wizard page per non-empty filter tier — multi-select list of that tier's filters."""

    def __init__(self, tier: int, parent=None):
        super().__init__(parent)
        self.tier = tier
        self.setTitle(f"Tier {tier} Filters")
        self.setSubTitle("Select any filters to include from this tier (or none, to skip it).")

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.entries = sorted(registry.list_by_tier(tier), key=lambda f: f.unique_id)
        for f in self.entries:
            item = QListWidgetItem(f"{f.unique_id}  —  {f.display_name}")
            item.setData(1000, f.unique_id)  # Qt.UserRole == 256 is not stable across bindings; 1000 is unused
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

    def selected_ids(self) -> list[str]:
        return [item.data(1000) for item in self.list_widget.selectedItems()]


class _PoolAndRunPage(QWizardPage):
    """Final page: candidate pool entry + selected-filter summary + the funnel report itself."""

    def __init__(self, rules, tier_pages: list[_TierPage], thread_manager, parent=None):
        super().__init__(parent)
        self.rules = rules
        self.tier_pages = tier_pages
        self.thread_manager = thread_manager
        self.setTitle("Candidate Pool & Elimination Funnel")
        self.setSubTitle(f"{rules.name} — pick {rules.pick_count} numbers per ticket from a pool within {rules.number_range}.")
        self.setFinalPage(True)

        layout = QVBoxLayout(self)

        self.lbl_selected = QLabel("Selected filters: (none yet)")
        self.lbl_selected.setWordWrap(True)
        layout.addWidget(self.lbl_selected)

        pool_row = QHBoxLayout()
        pool_row.addWidget(QLabel("Candidate pool (comma-separated numbers):"))
        self.txt_pool = QLineEdit()
        self.txt_pool.setPlaceholderText(f"e.g. {','.join(str(n) for n in range(rules.number_range[0], rules.number_range[0] + rules.pick_count + 3))}")
        pool_row.addWidget(self.txt_pool, stretch=1)
        layout.addLayout(pool_row)

        self.btn_run = QPushButton("▶ Run Elimination Funnel")
        self.btn_run.clicked.connect(self._run_funnel)
        layout.addWidget(self.btn_run)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["Stage", "Filter", "Before", "After", "Eliminated"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.result_table, stretch=1)

        self.lbl_summary = QLabel("")
        self.lbl_summary.setWordWrap(True)
        layout.addWidget(self.lbl_summary)

    def initializePage(self):
        ids = [uid for page in self.tier_pages for uid in page.selected_ids()]
        self.lbl_selected.setText(f"Selected filters ({len(ids)}): {', '.join(ids) if ids else '(none — go back and pick some)'}")

    def _run_funnel(self):
        filter_ids = [uid for page in self.tier_pages for uid in page.selected_ids()]
        if not filter_ids:
            QMessageBox.warning(self, "No Filters Selected", "Go back and select at least one filter from a tier page.")
            return

        raw = self.txt_pool.text().replace(" ", "")
        if not raw:
            QMessageBox.warning(self, "No Pool Entered", "Enter a candidate pool of numbers first.")
            return
        try:
            pool = sorted({int(x) for x in raw.split(",") if x})
        except ValueError:
            QMessageBox.warning(self, "Invalid Pool", "Pool must be comma-separated integers.")
            return

        lo, hi = self.rules.number_range
        if any(not (lo <= n <= hi) for n in pool):
            QMessageBox.warning(self, "Pool Out of Range", f"All pool numbers must be within {self.rules.number_range}.")
            return
        if len(pool) < self.rules.pick_count:
            QMessageBox.warning(self, "Pool Too Small", f"Pool needs at least {self.rules.pick_count} numbers for {self.rules.name}.")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⚙ Running...")

        job = FilterAssistantFunnelJob(self.rules, pool, filter_ids)
        job.signals.finished.connect(self._on_finished)
        job.signals.failed.connect(self._on_failed)
        # Keep a reference so the QThread isn't garbage-collected mid-run.
        self._job = job
        if self.thread_manager is not None:
            self.thread_manager.active_jobs[f"filter_assistant_funnel_{id(self)}"] = job
            job.finished.connect(lambda: self.thread_manager.active_jobs.pop(f"filter_assistant_funnel_{id(self)}", None))
        job.start()

    def _on_finished(self, rows: list[dict], total: int):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶ Run Elimination Funnel")

        self.result_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            before = "—" if row["before"] is None else f"{row['before']:,}"
            eliminated = "—" if row["eliminated"] is None else f"{row['eliminated']:,}"
            for c, val in enumerate([str(row["stage"]), row["filter"], before, f"{row['after']:,}", eliminated]):
                self.result_table.setItem(r, c, QTableWidgetItem(val))

        final = rows[-1]["after"] if rows else 0
        pct = (final / total * 100) if total else 0.0
        self.lbl_summary.setText(f"<b>{final:,} / {total:,} combinations ({pct:.4f}%) survive the full chain.</b>")

    def _on_failed(self, message: str):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶ Run Elimination Funnel")
        QMessageBox.critical(self, "Funnel Failed", message)


class FilterAssistantWizard(QWizard):
    """
    Guided, tier-by-tier filter picker ending in an elimination-funnel report
    — the GUI counterpart to `lottery filter-assistant`.
    """

    def __init__(self, rules, thread_manager=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🧙 Filter Assistant — {rules.name}")
        self.resize(700, 550)

        self.tier_pages: list[_TierPage] = []
        for tier in range(1, 6):
            if not registry.list_by_tier(tier):
                continue
            page = _TierPage(tier)
            self.tier_pages.append(page)
            self.addPage(page)

        self.addPage(_PoolAndRunPage(rules, self.tier_pages, thread_manager))
