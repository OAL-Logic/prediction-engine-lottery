"""
Daily Ritual & Manifestation Widget 🌟
======================================
Provides a deterministic and randomized 30-second ritual, breathwork,
and manifestation affirmation for lottery luck, calibrated by the current date.
"""

from __future__ import annotations

import datetime
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from desktop.src.theme.manager import THEMES, DEFAULT_THEME


RITUAL_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "golden-inhale",
        "title": "The Golden Inhale",
        "type": "Breathing",
        "affirmation": "I am an open channel for universal abundance and winning serendipity.",
        "action": "Close your eyes. Inhale deeply for 4s visualizing golden light filling your lungs. Hold for 7s feeling magnetic prosperity. Exhale slowly for 8s, releasing doubt.",
        "steps": [
            "Inhale golden abundance light (4s)",
            "Hold breath & feel magnetic prosperity (7s)",
            "Slow exhale, letting go of all doubt (8s)",
        ],
        "vibration": "528 Hz • Solar Plexus Gold",
        "color": "#FFD700",
    },
    {
        "id": "quantum-palms",
        "title": "Quantum Resonance Palms",
        "type": "Somatic",
        "affirmation": "Every cell in my body vibrates with clarity, intuition, and jackpot luck.",
        "action": "Rub your palms vigorously together for 10s until warm. Place them gently over your heart. Breathe softly and whisper your affirmation three times.",
        "steps": [
            "Rub palms together vigorously for warmth (10s)",
            "Place warm hands gently over your heart (10s)",
            "Whisper your affirmation with certainty 3 times (10s)",
        ],
        "vibration": "432 Hz • Heart Chakra Emerald",
        "color": "#00FF66",
    },
    {
        "id": "emerald-ray",
        "title": "The Emerald Ray Anchor",
        "type": "Visualization",
        "affirmation": "Infinite wealth and divine fortune flow directly into my reality today.",
        "action": "Visualize an intense emerald-green ray descending from the cosmos through your crown, bathing your hands and grounding deep into the earth.",
        "steps": [
            "Visualize cosmic emerald light entering crown (10s)",
            "Feel the electric hum of fortune in your hands (10s)",
            "Anchor the vibration deep into the earth (10s)",
        ],
        "vibration": "888 Hz • Abundance Ray",
        "color": "#10B981",
    },
    {
        "id": "gratitude-amplifier",
        "title": "The Gratitude Amplifier",
        "type": "Affirmation",
        "affirmation": "I am deeply grateful for the blessings I have, and ready for extraordinary wins.",
        "action": "Recall three small moments of good fortune from this week. Amplify that warm gratitude in your chest, then project that feeling into today's draw.",
        "steps": [
            "Recall 3 blessings you received this week (10s)",
            "Feel gratitude expand as radiant warmth (10s)",
            "Direct that high frequency to your lucky numbers (10s)",
        ],
        "vibration": "639 Hz • Harmonic Jupiter",
        "color": "#8B5CF6",
    },
    {
        "id": "drum-serendipity",
        "title": "Drum of Serendipity",
        "type": "Visualization",
        "affirmation": "The spinning lottery spheres are magnetically drawn to my chosen numbers.",
        "action": "Picture the lottery drum tumbling in slow motion. See your chosen numbers illuminated, floating with graceful certainty into the winning slots.",
        "steps": [
            "Envision the lottery drum spinning in brilliant light (10s)",
            "See your numbers illuminate with soft golden glow (10s)",
            "Seal the winning visual with calm peace (10s)",
        ],
        "vibration": "741 Hz • Cosmic Drum Harmonic",
        "color": "#06B6D4",
    },
    {
        "id": "temple-tap",
        "title": "Third Eye Temple Tap",
        "type": "Focus",
        "affirmation": "My intuition is razor-sharp. I pick the right numbers at the perfect moment.",
        "action": "With two fingers on each hand, gently tap your temples in rhythmic beats while clearing all mental static and picturing your lucky ticket.",
        "steps": [
            "Gently tap temples in slow rhythmic beats (10s)",
            "Clear mental chatter and trust your gut feeling (10s)",
            "Take one deep centering breath of intuition (10s)",
        ],
        "vibration": "852 Hz • Third Eye Clarity",
        "color": "#6366F1",
    },
    {
        "id": "open-palms",
        "title": "The Open Hands Blessing",
        "type": "Somatic",
        "affirmation": "I release all scarcity mindset. I am worthy and receptive to monumental luck.",
        "action": "Rest your hands on your lap with open palms facing upward. Roll your shoulders back and relax your jaw. Say softly: 'I welcome my fortune.'",
        "steps": [
            "Open palms upward and relax shoulders completely (10s)",
            "Feel receptive cosmic energy resting in your hands (10s)",
            "Whisper 'I welcome my fortune' with calm certainty (10s)",
        ],
        "vibration": "963 Hz • Crown Gateway",
        "color": "#EC4899",
    },
    {
        "id": "box-breath-luck",
        "title": "Box Breath of Certainty",
        "type": "Breathing",
        "affirmation": "Calm confidence is the true frequency of luck. I play from peace, not panic.",
        "action": "Perform a deliberate square breathing cycle: Inhale luck for 4s, hold in calm for 4s, exhale anxiety for 4s, hold in trust for 4s.",
        "steps": [
            "Inhale luck & confidence slowly (4s) • Hold full (4s)",
            "Exhale worry & tension smoothly (4s) • Hold empty (4s)",
            "One final deep breath to lock in steady peace (14s)",
        ],
        "vibration": "432 Hz • Autonomic Nervous Rest",
        "color": "#3B82F6",
    },
    {
        "id": "silver-cord",
        "title": "The Silver Cord Connection",
        "type": "Visualization",
        "affirmation": "An invisible line of synchronicity links my choices to the winning outcome.",
        "action": "Envision a shimmering silver cord connecting your hands directly to the draw machine. Feel the subtle magnetic pulse of synchronicity.",
        "steps": [
            "Envision a shimmering silver thread of synchronicity (10s)",
            "Send positive intent along the thread (10s)",
            "Rest in relaxed anticipation of the result (10s)",
        ],
        "vibration": "396 Hz • Lunar Synchronicity",
        "color": "#E2E8F0",
    },
    {
        "id": "joyful-precelebration",
        "title": "The Joyful Pre-Celebration",
        "type": "Affirmation",
        "affirmation": "I already feel the goosebumps and joy of celebrating my winning ticket.",
        "action": "Close your eyes and feel the physical sensations of matching the winning numbers: the widened eyes, the joyful grin, the wave of relief and excitement.",
        "steps": [
            "Imagine the notification confirming your winning numbers (10s)",
            "Smile wide and feel the genuine goosebumps of relief (10s)",
            "Anchor this victorious feeling into your daily spirit (10s)",
        ],
        "vibration": "528 Hz • High-Frequency Joy",
        "color": "#F59E0B",
    },
    {
        "id": "cleansing-exhale",
        "title": "The Cleansing Wind Exhale",
        "type": "Breathing",
        "affirmation": "I release all pressure and embrace the playful magic of the universe.",
        "action": "Release all stale air with an audible whoosh. Draw in fresh, sparkling vitality. Acknowledge that serendipity loves a relaxed, playful spirit.",
        "steps": [
            "Audible deep exhale, blowing away financial anxiety (10s)",
            "Inhale crisp, sparkling vitality and enthusiasm (10s)",
            "Smile and embrace the game as playful co-creation (10s)",
        ],
        "vibration": "417 Hz • Stagnation Release",
        "color": "#14B8A6",
    },
    {
        "id": "magnetic-sphere",
        "title": "The Golden Number Magnet",
        "type": "Focus",
        "affirmation": "My ticket is a magnet for the exact numbers drawn today.",
        "action": "Cup your hands together as if holding a glowing golden sphere. Whisper your affirmation into the space between your hands, then press them gently to your chest.",
        "steps": [
            "Cup hands to shape an energetic sphere (10s)",
            "Whisper your manifestation affirmation into the center (10s)",
            "Bring hands to chest to seal the magnetic intention (10s)",
        ],
        "vibration": "888 Hz • Magnetic Harmony",
        "color": "#FBBF24",
    },
]


def get_daily_index(date_str: str, total: int = len(RITUAL_CATALOG)) -> int:
    """Calculates a deterministic index from an ISO date string (YYYY-MM-DD)."""
    h = 0
    for ch in date_str:
        h = ((h << 5) - h) + ord(ch)
        h &= 0xFFFFFFFF
    return abs(h) % total


def get_daily_numerology_root(date_str: str) -> int:
    """Reduces the digits of a date string (YYYY-MM-DD) to a single digit (1-9)."""
    digits = [int(c) for c in date_str if c.isdigit()]
    if not digits:
        return 7
    s = sum(digits)
    while s > 9:
        s = sum(int(c) for c in str(s))
    return s


def get_daily_ritual(target_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """Returns the daily ritual, formatted date, and numerology root for the given date."""
    if target_date is None:
        target_date = datetime.date.today()
    date_str = target_date.isoformat()
    idx = get_daily_index(date_str, len(RITUAL_CATALOG))
    ritual = RITUAL_CATALOG[idx]
    numerology_root = get_daily_numerology_root(date_str)
    formatted_date = target_date.strftime("%A, %b %d, %Y")

    return {
        "ritual": ritual,
        "date_str": date_str,
        "formatted_date": formatted_date,
        "numerology_root": numerology_root,
    }


class DailyRitualWidget(QWidget):
    """
    Component 'DailyRitual' providing a daily 30-second ritual or manifestation affirmation
    related to lottery luck, based on the current date, with a live countdown timer and audio-visual cues.
    """

    ritual_completed = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None, target_date: Optional[datetime.date] = None, colors: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        self.colors = dict(colors) if colors else dict(THEMES[DEFAULT_THEME])
        self.target_date = target_date or datetime.date.today()
        self.shuffle_offset = 0

        self.seconds_remaining = 30
        self.is_running = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._init_ui()
        self._load_current_ritual()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Container Frame
        self.frame = QFrame(self)
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('panel', '#181a20')};
                border: 1px solid {self.colors.get('border', '#2e3442')};
                border-radius: 8px;
            }}
        """)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(14, 14, 14, 14)
        frame_layout.setSpacing(8)

        # Header Row: Badge, Date, Root, and Reroll Button
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        self.lbl_type_badge = QLabel("RITUAL")
        self.lbl_type_badge.setStyleSheet("""
            QLabel {
                background-color: #263043;
                color: #00FF66;
                font-weight: bold;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 4px;
            }
        """)
        header_row.addWidget(self.lbl_type_badge)

        self.lbl_date = QLabel("Today")
        self.lbl_date.setStyleSheet(f"color: {self.colors.get('text_dim', '#9ca3af')}; font-size: 11px; font-weight: 600;")
        header_row.addWidget(self.lbl_date)

        self.lbl_root = QLabel("ROOT #7")
        self.lbl_root.setStyleSheet("""
            QLabel {
                background-color: #2A1F3D;
                color: #D8B4FE;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            }
        """)
        header_row.addWidget(self.lbl_root)

        header_row.addStretch()

        self.btn_reroll = QPushButton("🎲 Reroll")
        self.btn_reroll.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e2433;
                color: {self.colors.get('text', '#f3f4f6')};
                border: 1px solid {self.colors.get('border', '#2e3442')};
                padding: 4px 8px;
                font-size: 11px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #2b3548;
            }}
        """)
        self.btn_reroll.clicked.connect(self._on_reroll)
        header_row.addWidget(self.btn_reroll)

        frame_layout.addLayout(header_row)

        # Title & Vibration
        self.lbl_title = QLabel("Title")
        self.lbl_title.setStyleSheet(f"color: {self.colors.get('text', '#f3f4f6')}; font-size: 15px; font-weight: bold;")
        frame_layout.addWidget(self.lbl_title)

        self.lbl_vibration = QLabel("⚡ Vibration")
        self.lbl_vibration.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        frame_layout.addWidget(self.lbl_vibration)

        # Affirmation Box
        self.lbl_affirmation = QLabel("Affirmation")
        self.lbl_affirmation.setWordWrap(True)
        self.lbl_affirmation.setStyleSheet(f"""
            QLabel {{
                background-color: #131722;
                border-left: 3px solid #00FF66;
                color: #E2E8F0;
                font-size: 12px;
                font-style: italic;
                padding: 8px 10px;
                border-radius: 4px;
            }}
        """)
        frame_layout.addWidget(self.lbl_affirmation)

        # Steps
        self.step_labels: List[QLabel] = []
        for i in range(3):
            lbl_step = QLabel(f"Step {i+1}")
            lbl_step.setStyleSheet("color: #94A3B8; font-size: 11px;")
            self.step_labels.append(lbl_step)
            frame_layout.addWidget(lbl_step)

        # Progress & Timer
        timer_box = QHBoxLayout()
        self.lbl_timer_status = QLabel("30-SECOND PROTOCOL")
        self.lbl_timer_status.setStyleSheet("color: #64748B; font-size: 10px; font-weight: bold;")
        timer_box.addWidget(self.lbl_timer_status)

        timer_box.addStretch()

        self.lbl_timer = QLabel("30s")
        self.lbl_timer.setStyleSheet("color: #00FF66; font-size: 14px; font-weight: bold;")
        timer_box.addWidget(self.lbl_timer)
        frame_layout.addLayout(timer_box)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 30)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e2433;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00FF66;
                border-radius: 2px;
            }
        """)
        frame_layout.addWidget(self.progress_bar)

        # Action Buttons
        btn_box = QHBoxLayout()
        self.btn_start = QPushButton("▶ START 30s RITUAL")
        self.btn_start.setStyleSheet("""
            QPushButton {{
                background-color: #00FF66;
                color: #0B0C10;
                font-weight: bold;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #10B981;
            }}
        """)
        self.btn_start.clicked.connect(self._toggle_timer)
        btn_box.addWidget(self.btn_start)

        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setStyleSheet("""
            QPushButton {{
                background-color: #1e2433;
                color: #94A3B8;
                font-size: 11px;
                padding: 6px 10px;
                border-radius: 4px;
                border: 1px solid #334155;
            }}
            QPushButton:hover {{
                background-color: #2b3548;
            }}
        """)
        self.btn_reset.clicked.connect(self._reset_timer)
        btn_box.addWidget(self.btn_reset)

        frame_layout.addLayout(btn_box)
        layout.addWidget(self.frame)

    def _load_current_ritual(self) -> None:
        data = get_daily_ritual(self.target_date)
        total = len(RITUAL_CATALOG)
        idx = (get_daily_index(data["date_str"], total) + self.shuffle_offset) % total
        ritual = RITUAL_CATALOG[idx]

        self.current_ritual = ritual
        self.lbl_type_badge.setText(ritual["type"].upper())
        self.lbl_type_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #1E2433;
                color: {ritual['color']};
                font-weight: bold;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid {ritual['color']};
            }}
        """)

        self.lbl_date.setText(f"📅 {data['formatted_date']}")
        self.lbl_root.setText(f"ROOT #{data['numerology_root']}")
        self.lbl_title.setText(ritual["title"])
        self.lbl_vibration.setText(f"⚡ {ritual['vibration']}")
        self.lbl_affirmation.setText(f"“{ritual['affirmation']}”")
        self.lbl_affirmation.setStyleSheet(f"""
            QLabel {{
                background-color: #131722;
                border-left: 3px solid {ritual['color']};
                color: #E2E8F0;
                font-size: 12px;
                font-style: italic;
                padding: 8px 10px;
                border-radius: 4px;
            }}
        """)

        for i, step_text in enumerate(ritual["steps"]):
            if i < len(self.step_labels):
                self.step_labels[i].setText(f"{i+1}. {step_text}")

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1e2433;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {ritual['color']};
                border-radius: 2px;
            }}
        """)

    def _on_reroll(self) -> None:
        self._reset_timer()
        self.shuffle_offset += 1
        self._load_current_ritual()

    def _toggle_timer(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.timer.start()
            self.btn_start.setText("⏸ PAUSE")
            self.lbl_timer_status.setText("ALIGNING FREQUENCY...")
        else:
            self.is_running = False
            self.timer.stop()
            self.btn_start.setText("RESUME")
            self.lbl_timer_status.setText("PAUSED")

    def _reset_timer(self) -> None:
        self.timer.stop()
        self.is_running = False
        self.seconds_remaining = 30
        self.progress_bar.setValue(0)
        self.lbl_timer.setText("30s")
        self.btn_start.setText("▶ START 30s RITUAL")
        self.lbl_timer_status.setText("30-SECOND PROTOCOL")

    def _on_tick(self) -> None:
        if self.seconds_remaining > 0:
            self.seconds_remaining -= 1
            elapsed = 30 - self.seconds_remaining
            self.progress_bar.setValue(elapsed)
            self.lbl_timer.setText(f"{self.seconds_remaining}s")

            phase = min(3, (elapsed // 10) + 1)
            self.lbl_timer_status.setText(f"PHASE {phase}/3 • ALIGNING")

        if self.seconds_remaining <= 0:
            self.timer.stop()
            self.is_running = False
            self.lbl_timer.setText("✓ 0s")
            self.lbl_timer_status.setText("✨ RITUAL COMPLETE — LUCK ANCHORED")
            self.btn_start.setText("↺ REPEAT RITUAL")
            self.ritual_completed.emit(self.current_ritual)
