"""
Number Dossier Dialog 🧬
========================
Desktop front-end for the `number-lifecycle` historical dossier: pick a
number, see its first/last appearance, hit rate, gaps and streaks without
leaving the app. Lottery Studio's "nsStat" aggregate-stats equivalent, scoped to
one number at a time, in dialog form.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, QPushButton, QLabel, QGroupBox
)

from engine.cli.utils import get_adapter
from engine.cli.commands.number_lifecycle import compute_lifecycle
from desktop.src.theme.manager import THEMES, DEFAULT_THEME


class NumberDossierDialog(QDialog):
    def __init__(self, parent=None, lottery_id: str = "br/mega-sena", colors: dict | None = None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.setWindowTitle("Number Dossier")
        self.resize(420, 300)
        colors = dict(colors) if colors else dict(THEMES[DEFAULT_THEME])

        adapter = get_adapter(lottery_id)
        lo, hi = adapter.rules.number_range

        self.number_spin = QSpinBox()
        self.number_spin.setRange(lo, hi)

        lookup_btn = QPushButton("Look up")
        lookup_btn.clicked.connect(self.run_lookup)

        form = QFormLayout()
        form.addRow("Number:", self.number_spin)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(f"font-family: 'JetBrains Mono'; font-size: 13px; color: {colors['primary']};")

        box = QGroupBox(f"{adapter.rules.name} — historical dossier")
        box.setLayout(form)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(lookup_btn)
        layout.addWidget(self.result_label)

    def run_lookup(self) -> None:
        adapter = get_adapter(self.lottery_id)
        df = adapter.fetch()
        if df.empty:
            self.result_label.setText("No cached history for this game yet.")
            return

        stats = compute_lifecycle(df, self.number_spin.value())
        if stats["total_hits"] == 0:
            self.result_label.setText(f"{self.number_spin.value()} has never been drawn in {stats['total_draws']} cached draws.")
            return

        self.result_label.setText(
            f"Hits: {stats['total_hits']} / {stats['total_draws']} ({stats['hit_rate']*100:.2f}%)\n"
            f"First seen: draw {stats['first_draw']} ({stats['first_date']})\n"
            f"Last seen: draw {stats['last_draw']} ({stats['last_date']})\n"
            f"Current gap: {stats['current_gap']} draws\n"
            f"Average gap: {stats['avg_gap']:.2f} draws\n"
            f"Longest gap: {stats['longest_gap']} draws\n"
            f"Longest streak: {stats['longest_streak']} draws"
        )
