import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QComboBox, QSpinBox, QGroupBox, 
    QTableWidget, QTableWidgetItem, QTabWidget, QSplitter, QScrollArea, 
    QCheckBox, QRadioButton, QButtonGroup, QHeaderView, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont

class NumberGrid(QWidget):
    """Interactive dynamic grid of numeric balls that toggles numbers into the active pool."""
    number_toggled = Signal(int, bool)  # number, is_selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.buttons = {}
        self.selected_numbers = set()
        self.max_number = 25
        self.build_grid()

    def set_max_number(self, max_num: int):
        self.max_number = max_num
        self.selected_numbers.clear()
        self.build_grid()

    def build_grid(self):
        # Clear existing buttons
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.buttons.clear()

        cols = 5 if self.max_number <= 30 else 10
        for n in range(1, self.max_number + 1):
            btn = QPushButton(f"{n:02d}")
            btn.setCheckable(False)
            btn.setFixedSize(36, 36)
            btn.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            btn.clicked.connect(lambda checked=False, val=n: self.on_ball_clicked(val))
            
            # Stylesheet with responsive states (default, hover, active)
            btn.setStyleSheet(self.get_ball_style(n))

            row = (n - 1) // cols
            col = (n - 1) % cols
            self.layout.addWidget(btn, row, col)
            self.buttons[n] = btn

    def get_ball_style(self, num: int) -> str:
        if num in self.selected_numbers:
            # Active (Neon Red background, white text, subtle border glow)
            return """
                QPushButton {
                    background-color: #FF3366;
                    color: #FFFFFF;
                    border: 2px solid #FF3366;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #FF5588;
                    border-color: #FF5588;
                }
            """
        else:
            # Default (Unselected: border-only accent cyan, dark background)
            return """
                QPushButton {
                    background-color: #1A1A1E;
                    color: #00F0FF;
                    border: 1px solid #222226;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #222226;
                    border: 1px solid #00F0FF;
                }
            """

    def on_ball_clicked(self, num: int):
        if num in self.selected_numbers:
            self.selected_numbers.remove(num)
            is_selected = False
        else:
            self.selected_numbers.add(num)
            is_selected = True
        
        self.buttons[num].setStyleSheet(self.get_ball_style(num))
        self.number_toggled.emit(num, is_selected)

    def select_all(self):
        self.selected_numbers = set(range(1, self.max_number + 1))
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))

    def clear_selection(self):
        self.selected_numbers.clear()
        for n, btn in self.buttons.items():
            btn.setStyleSheet(self.get_ball_style(n))


class SleekCockpitPrototype(QMainWindow):
    """High-density consolidated dashboard matching SamLotto features in Sleek Dark Mode."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prophet Cockpit - Sleek Dark Workspace")
        self.resize(1300, 850)
        self.setup_menu_bar()
        self.initUI()
        self.apply_theme()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Import SamLotto TXT...")
        file_menu.addAction("Export SamLotto TXT...")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction("Draws History...")
        view_menu.addAction("Statistics Cockpit...")

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("Formula Guide")
        help_menu.addAction("About")

    def initUI(self):
        # Vertical splitter partitions Main Workspace and the Bottom Dock
        main_splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(main_splitter)

        # Upper central area split horizontally: Pool Builder (Left) vs Ticket Store (Right)
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(10)
        upper_splitter = QSplitter(Qt.Horizontal)
        upper_layout.addWidget(upper_splitter)

        # -------------------------------------------------------------
        # Left Rail: Pool Builder
        # -------------------------------------------------------------
        pool_group = QGroupBox("Active Pool Builder")
        pool_layout = QVBoxLayout(pool_group)
        pool_layout.setSpacing(10)

        # Game Selector Header
        game_selector_layout = QHBoxLayout()
        game_selector_layout.addWidget(QLabel("Active Game:"))
        self.game_combo = QComboBox()
        self.game_combo.addItems(["Lotofácil (br/lotofacil)", "Mega-Sena (br/mega-sena)", "Quina (br/quina)"])
        self.game_combo.currentTextChanged.connect(self.on_game_changed)
        game_selector_layout.addWidget(self.game_combo)
        pool_layout.addLayout(game_selector_layout)

        # Interactive grid of numbers
        self.number_grid_scroll = QScrollArea()
        self.number_grid_scroll.setWidgetResizable(True)
        self.number_grid_scroll.setStyleSheet("QScrollArea { border: 1px solid #222226; background-color: #121214; }")
        
        self.number_grid = NumberGrid()
        self.number_grid_scroll.setWidget(self.number_grid)
        pool_layout.addWidget(self.number_grid_scroll, stretch=1)

        # Quick Select Action Toolbar
        quick_select_layout = QHBoxLayout()
        btn_hot = QPushButton("HOT")
        btn_cold = QPushButton("COLD")
        btn_clear = QPushButton("CLEAR")
        btn_all = QPushButton("ALL")
        
        btn_hot.clicked.connect(self.select_hot_numbers)
        btn_cold.clicked.connect(self.select_cold_numbers)
        btn_clear.clicked.connect(self.number_grid.clear_selection)
        btn_all.clicked.connect(self.number_grid.select_all)

        quick_select_layout.addWidget(btn_hot)
        quick_select_layout.addWidget(btn_cold)
        quick_select_layout.addWidget(btn_clear)
        quick_select_layout.addWidget(btn_all)
        pool_layout.addLayout(quick_select_layout)

        # Counter Status Label
        self.lbl_pool_status = QLabel("Active Pool Size: 0 numbers selected")
        self.lbl_pool_status.setStyleSheet("color: #00F0FF; font-weight: bold; font-size: 11px;")
        self.number_grid.number_toggled.connect(self.update_pool_counter)
        pool_layout.addWidget(self.lbl_pool_status)

        upper_splitter.addWidget(pool_group)

        # -------------------------------------------------------------
        # Right Rail: Ticket Store Cockpit
        # -------------------------------------------------------------
        store_group = QGroupBox("Ticket Store Cockpit")
        store_layout = QVBoxLayout(store_group)
        store_layout.setSpacing(10)

        # Controls Header
        controls_header = QHBoxLayout()
        self.btn_smart_gen = QPushButton("⚡ SMART SUGGEST")
        self.btn_smart_gen.setToolTip("Generates suggestions biased by mathematical strategy weights")
        self.btn_wheel_gen = QPushButton("🎡 COMBINATORIAL WHEEL")
        
        controls_header.addWidget(self.btn_smart_gen)
        controls_header.addWidget(self.btn_wheel_gen)
        store_layout.addLayout(controls_header)

        # Ticket Table
        self.ticket_table = QTableWidget()
        self.ticket_table.setColumnCount(3)
        self.ticket_table.setHorizontalHeaderLabels(["Index", "Ticket Combination", "Score"])
        self.ticket_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ticket_table.setAlternatingRowColors(True)
        store_layout.addWidget(self.ticket_table, stretch=1)

        # Table Action Toolbar
        table_actions = QHBoxLayout()
        btn_dedupe = QPushButton("DEDUPLICATE")
        btn_export = QPushButton("EXPORT TXT")
        btn_print = QPushButton("PRINT")
        
        table_actions.addWidget(btn_dedupe)
        table_actions.addWidget(btn_export)
        table_actions.addWidget(btn_print)
        store_layout.addLayout(table_actions)

        upper_splitter.addWidget(store_group)

        # Set split ratio for top section
        upper_splitter.setSizes([380, 820])
        main_splitter.addWidget(upper_widget)

        # -------------------------------------------------------------
        # Bottom Dock: Setup Tabbed Workspace
        # -------------------------------------------------------------
        bottom_dock = QGroupBox("Harmony Gate Filtering Setup Dock")
        bottom_layout = QHBoxLayout(bottom_dock)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(15)

        self.setup_tabs = QTabWidget()
        bottom_layout.addWidget(self.setup_tabs, stretch=1)

        # Tab 1: Base Filters Layout
        base_tab = QWidget()
        base_layout = QGridLayout(base_tab)
        base_layout.setSpacing(10)
        
        # Mock checkboxes and inputs
        base_layout.addWidget(QCheckBox("Sum Range Filter"), 0, 0)
        base_layout.addWidget(QLabel("Min:"), 0, 1)
        spin_min = QSpinBox()
        spin_min.setRange(50, 400)
        spin_min.setValue(150)
        base_layout.addWidget(spin_min, 0, 2)
        base_layout.addWidget(QLabel("Max:"), 0, 3)
        spin_max = QSpinBox()
        spin_max.setRange(50, 400)
        spin_max.setValue(220)
        base_layout.addWidget(spin_max, 0, 4)

        base_layout.addWidget(QCheckBox("Odd-Even Ratio Filter"), 1, 0)
        base_layout.addWidget(QLabel("Preferred:"), 1, 1)
        combo_oe = QComboBox()
        combo_oe.addItems(["7 Odd / 8 Even", "8 Odd / 7 Even", "Any Ratio"])
        base_layout.addWidget(combo_oe, 1, 2, 1, 3)

        base_layout.addWidget(QCheckBox("Consecutive Numbers Filter"), 2, 0)
        base_layout.addWidget(QLabel("Max Run:"), 2, 1)
        spin_run = QSpinBox()
        spin_run.setRange(2, 10)
        spin_run.setValue(4)
        base_layout.addWidget(spin_run, 2, 2)

        base_layout.addWidget(QCheckBox("Prime Numbers Filter"), 3, 0)
        base_layout.addWidget(QLabel("Count:"), 3, 1)
        spin_prime = QSpinBox()
        spin_prime.setRange(0, 15)
        spin_prime.setValue(5)
        base_layout.addWidget(spin_prime, 2, 2)

        self.setup_tabs.addTab(base_tab, "Base Filters")

        # Tab 2: Advanced Filters Layout
        adv_tab = QWidget()
        adv_layout = QVBoxLayout(adv_tab)
        adv_layout.addWidget(QCheckBox("AC Value Range (8-10)"))
        adv_layout.addWidget(QCheckBox("Last-10 Repeat Count (1-3)"))
        adv_layout.addWidget(QCheckBox("Average Skips Limit (<= 4.5)"))
        self.setup_tabs.addTab(adv_tab, "Advanced Filters")

        # Tab 3: Logical Logic
        logic_tab = QWidget()
        logic_layout = QVBoxLayout(logic_tab)
        
        self.radio_and = QRadioButton("Strict Logical AND (All active filters must pass)")
        self.radio_and.setChecked(True)
        self.radio_or = QRadioButton("Strict Logical OR (Any active filter may pass)")
        self.radio_nofm = QRadioButton("Fault-Tolerant N-of-M Logic (N active filters must pass)")
        
        logic_layout.addWidget(self.radio_and)
        logic_layout.addWidget(self.radio_or)
        logic_layout.addWidget(self.radio_nofm)
        
        nofm_sub = QHBoxLayout()
        nofm_sub.addWidget(QLabel("Required filters (N):"))
        spin_n = QSpinBox()
        spin_n.setRange(1, 50)
        spin_n.setValue(3)
        nofm_sub.addWidget(spin_n)
        nofm_sub.addStretch()
        logic_layout.addLayout(nofm_sub)

        self.setup_tabs.addTab(logic_tab, "Logical Fault-Tolerance")

        # Action Panel Right on Bottom Dock
        action_panel = QVBoxLayout()
        action_panel.setSpacing(8)
        
        btn_calc_defaults = QPushButton("⚙ AUTO CALCULATE LIMITS")
        btn_calc_defaults.setStyleSheet("padding: 6px; font-size: 11px;")
        
        self.btn_run_prune = QPushButton("⚡ RUN HARMONY GATE PRUNING")
        self.btn_run_prune.setStyleSheet("""
            QPushButton {
                background-color: #FF3366;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 13px;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #FF3366;
            }
            QPushButton:hover {
                background-color: #FF5588;
                border-color: #FF5588;
            }
        """)
        
        action_panel.addWidget(btn_calc_defaults)
        action_panel.addWidget(self.btn_run_prune, stretch=1)
        bottom_layout.addLayout(action_panel)

        main_splitter.addWidget(bottom_dock)

        # Set vertical ratios: top workspace is 65%, bottom dock is 35%
        main_splitter.setSizes([550, 300])

    def on_game_changed(self, text: str):
        if "Lotofácil" in text:
            self.number_grid.set_max_number(25)
        elif "Mega-Sena" in text:
            self.number_grid.set_max_number(60)
        elif "Quina" in text:
            self.number_grid.set_max_number(80)
        self.lbl_pool_status.setText("Active Pool Size: 0 numbers selected")

    def update_pool_counter(self, num: int, is_selected: bool):
        sz = len(self.number_grid.selected_numbers)
        self.lbl_pool_status.setText(f"Active Pool Size: {sz} numbers selected")

    def select_hot_numbers(self):
        self.number_grid.clear_selection()
        hot = [1, 3, 5, 8, 12, 15, 20, 22]
        self.number_grid.selected_numbers = set([x for x in hot if x <= self.number_grid.max_number])
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def select_cold_numbers(self):
        self.number_grid.clear_selection()
        cold = [2, 7, 11, 14, 18, 25]
        self.number_grid.selected_numbers = set([x for x in cold if x <= self.number_grid.max_number])
        for n, btn in self.number_grid.buttons.items():
            btn.setStyleSheet(self.number_grid.get_ball_style(n))
        self.update_pool_counter(0, True)

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121214;
            }
            QWidget {
                background-color: #121214;
                color: #E0E0E5;
                font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
            }
            QGroupBox {
                border: 1px solid #222226;
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
                text-transform: uppercase;
                background-color: #1A1A1E;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
                color: #00F0FF;
            }
            QTabWidget::pane {
                border: 1px solid #222226;
                background-color: #1A1A1E;
            }
            QTabBar::tab {
                background-color: #141418;
                border: 1px solid #222226;
                padding: 8px 12px;
                color: #8A8A95;
            }
            QTabBar::tab:selected {
                background-color: #1A1A1E;
                color: #E0E0E5;
                border-bottom: 2px solid #00F0FF;
            }
            QPushButton {
                background-color: #1A1A1E;
                color: #00F0FF;
                border: 1px solid #00F0FF;
                border-radius: 4px;
                padding: 8px 16px;
                text-transform: uppercase;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #121214;
            }
            QPushButton:pressed {
                background-color: #00C3CF;
            }
            QTableWidget {
                background-color: #121214;
                gridline-color: #222226;
                border: 1px solid #222226;
                color: #E0E0E5;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #FF3366;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #141418;
                color: #00F0FF;
                padding: 4px;
                border: 1px solid #222226;
            }
            QComboBox, QSpinBox {
                background-color: #121214;
                color: #E0E0E5;
                border: 1px solid #222226;
                border-radius: 2px;
                padding: 4px;
            }
            QCheckBox, QRadioButton {
                spacing: 8px;
                font-size: 11px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #00F0FF;
                background-color: #121214;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #FF3366;
                border-color: #FF3366;
            }
            QScrollBar:vertical {
                border: none;
                background: #141418;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #222226;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00F0FF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMenuBar {
                background-color: #141418;
                color: #E0E0E5;
                border-bottom: 1px solid #222226;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 10px;
                color: #8A8A95;
            }
            QMenuBar::item:selected {
                background-color: #00F0FF;
                color: #121214;
            }
            QMenu {
                background-color: #1A1A1E;
                border: 1px solid #222226;
                color: #E0E0E5;
            }
            QMenu::item:selected {
                background-color: #00F0FF;
                color: #121214;
            }
        """)

def main():
    app = QApplication(sys.argv)
    window = SleekCockpitPrototype()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
