import datetime
import pytest

from desktop.src.widgets.daily_ritual import (
    RITUAL_CATALOG,
    get_daily_index,
    get_daily_numerology_root,
    get_daily_ritual,
    DailyRitualWidget,
)


def test_ritual_catalog_integrity():
    assert len(RITUAL_CATALOG) >= 10
    for r in RITUAL_CATALOG:
        assert "id" in r
        assert "title" in r
        assert len(r["affirmation"]) > 15
        assert len(r["action"]) > 15
        assert len(r["steps"]) == 3
        assert "vibration" in r
        assert r["color"].startswith("#")


def test_get_daily_index_deterministic():
    idx1 = get_daily_index("2026-10-25", len(RITUAL_CATALOG))
    idx2 = get_daily_index("2026-10-25", len(RITUAL_CATALOG))
    assert idx1 == idx2
    assert 0 <= idx1 < len(RITUAL_CATALOG)


def test_get_daily_index_distribution():
    indices = {
        get_daily_index(f"2026-10-{day:02d}", len(RITUAL_CATALOG))
        for day in range(1, 15)
    }
    assert len(indices) > 1


def test_get_daily_numerology_root():
    # 2026-10-25 -> 2+0+2+6+1+0+2+5 = 18 -> 1+8 = 9
    assert get_daily_numerology_root("2026-10-25") == 9
    # 2026-01-01 -> 2+0+2+6+0+1+0+1 = 12 -> 1+2 = 3
    assert get_daily_numerology_root("2026-01-01") == 3
    # 1990-01-01 -> 1+9+9+0+0+1+0+1 = 21 -> 2+1 = 3
    assert get_daily_numerology_root("1990-01-01") == 3


def test_get_daily_ritual():
    d = datetime.date(2026, 10, 25)
    packet = get_daily_ritual(d)
    assert packet["date_str"] == "2026-10-25"
    assert "Sunday" in packet["formatted_date"]
    assert packet["numerology_root"] == 9
    assert packet["ritual"]["title"] == RITUAL_CATALOG[get_daily_index("2026-10-25", len(RITUAL_CATALOG))]["title"]


from PySide6.QtWidgets import QApplication

@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication(["-platform", "offscreen"])

def test_daily_ritual_widget_headless(qapp):
    """Test DailyRitualWidget UI elements and state transitions."""
    target_date = datetime.date(2026, 10, 25)
    widget = DailyRitualWidget(target_date=target_date)

    assert widget.seconds_remaining == 30
    assert not widget.is_running
    assert "ROOT #9" in widget.lbl_root.text()

    # Test reroll
    prev_title = widget.lbl_title.text()
    widget.btn_reroll.click()
    assert widget.shuffle_offset == 1
    # Either same or new title depending on offset modulo length
    assert widget.current_ritual is not None

    # Test start and timer tick
    widget.btn_start.click()
    assert widget.is_running
    assert widget.btn_start.text() == "⏸ PAUSE"

    widget._on_tick()
    assert widget.seconds_remaining == 29
    assert widget.progress_bar.value() == 1
    assert widget.lbl_timer.text() == "29s"

    # Fast forward to 0s to trigger completion
    widget.seconds_remaining = 1
    completed_events = []
    widget.ritual_completed.connect(lambda r: completed_events.append(r))
    widget._on_tick()

    assert widget.seconds_remaining == 0
    assert not widget.is_running
    assert len(completed_events) == 1
    assert "COMPLETE" in widget.lbl_timer_status.text()
