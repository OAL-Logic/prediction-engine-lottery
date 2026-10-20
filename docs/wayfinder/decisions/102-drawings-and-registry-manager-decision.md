# MDR-102: Drawings and Registry Manager Design

* **Status**: Accepted (Research Complete)
* **Date**: 2026-08-11
* **Author**: Antigravity (AI Assistant)
* **Decides**: DuckDB drawings storage, editable table model class, and conversion scripts for bidirectional import/export between Lottery Studio `.txt` files and DuckDB.

---

## 1. Database and Storage Architecture

We utilize **DuckDB** as the primary storage engine. In [storage.py](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/(P) Prediction Engine/lottery/engine/modules/storage.py), the historical drawings are stored under the `draws` table:

```sql
CREATE TABLE IF NOT EXISTS draws (
    lottery_id TEXT,         -- Game ID slug (e.g. 'br/mega-sena', 'us/powerball')
    draw_id INTEGER,         -- Sequential contest number
    draw_date DATE,          -- Draw date (YYYY-MM-DD)
    numbers INTEGER[],       -- Array of sorted main numbers
    bonus INTEGER[],         -- Array of bonus/powerball numbers
    raw_json JSON,           -- Original API JSON backup
    PRIMARY KEY (lottery_id, draw_id)
);
```

---

## 2. Lottery Studio Flat File Format Specification

Standard Lottery Studio stores drawings under AppData as space-delimited text files (`.Txt`) with no header lines.
- **Implicit Draw ID**: The draw ID is represented by the 1-indexed line number in the file.
- **Date Format**: Standard US dates: `M/D/YYYY` or `MM/DD/YYYY` (e.g. `3/11/1996`, `10/12/2002`).
- **Numbers Format**: Main numbers (ascending order) followed immediately by bonus numbers on the same line, zero-padded to 2 digits.
- **Line Ending**: CRLF (`\r\n`).

### Example (Powerball with 5 Main + 1 Bonus):
```text
10/9/2002 09 10 38 42 43 05
10/12/2002 23 26 46 49 52 28
```

---

## 3. Editable QAbstractTableModel for PySide6

The `DuckDBDrawsTableModel` provides inline editing, row insertion, and row deletion with live database synchronization.

```python
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List, Dict, Optional
import pandas as pd
import duckdb

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from engine.modules.storage import storage

logger = logging.getLogger(__name__)

class DuckDBDrawsTableModel(QAbstractTableModel):
    data_mutated = Signal(str)
    COLUMNS = ["Draw ID", "Draw Date", "Winning Balls", "Bonus Balls"]

    def __init__(self, lottery_id: str = "br/mega-sena", parent=None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self._data: List[Dict[str, Any]] = []
        self.load_data(lottery_id)

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        row_data = self._data[index.row()]
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0:
                return row_data.get("draw_id")
            elif col == 1:
                val = row_data.get("draw_date")
                if isinstance(val, (datetime, pd.Timestamp)):
                    return val.strftime("%Y-%m-%d")
                return str(val) if val else ""
            elif col == 2:
                nums = row_data.get("numbers", [])
                return ", ".join(f"{x:02d}" for x in nums) if isinstance(nums, list) else str(nums)
            elif col == 3:
                bonus = row_data.get("bonus", [])
                return ", ".join(f"{x:02d}" for x in bonus) if isinstance(bonus, list) and bonus else ""

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid(): return Qt.NoItemFlags
        base_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() in (1, 2, 3):  # Date, Main, Bonus are inline editable
            return base_flags | Qt.ItemIsEditable
        return base_flags

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole: return False

        row = index.row()
        col = index.column()
        row_dict = self._data[row].copy()
        draw_id = row_dict["draw_id"]

        try:
            if col == 1:  # Date
                date_str = str(value).strip()
                parsed_dt = datetime.strptime(date_str, "%Y-%m-%d")
                row_dict["draw_date"] = parsed_dt.strftime("%Y-%m-%d")
            elif col == 2:  # Main Balls
                raw_nums = str(value).replace(" ", "")
                if not raw_nums: return False
                nums = [int(x) for x in raw_nums.split(",") if x]
                row_dict["numbers"] = nums
            elif col == 3:  # Bonus Balls
                raw_bonus = str(value).replace(" ", "")
                bonus = [int(x) for x in raw_bonus.split(",") if x] if raw_bonus else []
                row_dict["bonus"] = bonus
            else:
                return False

            # Persist update in DuckDB via Storage Engine
            storage.save_draws(self.lottery_id, [{
                "draw_id": draw_id,
                "draw_date": row_dict["draw_date"],
                "numbers": row_dict["numbers"],
                "bonus": row_dict["bonus"]
            }])

            self._data[row] = row_dict
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.error(f"Failed inline update for Draw #{draw_id}: {e}")
            return False

    def load_data(self, lottery_id: str):
        self.beginResetModel()
        self.lottery_id = lottery_id
        df = storage.load_draws(lottery_id)
        if not df.empty:
            df_sorted = df.sort_values("draw_id", ascending=False)
            self._data = df_sorted.to_dict(orient="records")
        else:
            self._data = []
        self.endResetModel()

    def insert_draw(self, draw_id: int, draw_date: str, numbers: List[int], bonus: List[int]) -> bool:
        payload = {
            "draw_id": draw_id,
            "draw_date": draw_date,
            "numbers": numbers,
            "bonus": bonus
        }
        try:
            storage.save_draws(self.lottery_id, [payload])
            self.beginInsertRows(QModelIndex(), 0, 0)
            self._data.insert(0, payload)
            self.endInsertRows()
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False

    def remove_draw(self, row: int) -> bool:
        if not (0 <= row < len(self._data)): return False
        draw_id = self._data[row]["draw_id"]
        try:
            if storage.use_duckdb:
                with duckdb.connect(str(storage.db_path)) as con:
                    con.execute("DELETE FROM draws WHERE lottery_id = ? AND draw_id = ?", [self.lottery_id, draw_id])
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()
            self.data_mutated.emit(self.lottery_id)
            return True
        except Exception as e:
            logger.error(f"Deletion failed: {e}")
            return False
```

---

## 4. Import / Export Scripts (Lottery Studio Bidirectional Converter)

```python
from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import duckdb

from engine.adapters.registry import registry
from engine.modules.storage import storage, LotteryStorage

logger = logging.getLogger(__name__)

def parse_studio_txt(file_path: Path, lottery_id: str) -> List[Dict[str, Any]]:
    game = registry.get_game(lottery_id)
    pick_count = game.pick_count if game else 6
    bonus_count = game.bonus_count if game else 0

    draws: List[Dict[str, Any]] = []
    if not file_path.exists():
        raise FileNotFoundError(f"Lottery Studio file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        line_idx = 0
        for line in f:
            line_str = line.strip()
            if not line_str: continue
            
            line_idx += 1
            parts = line_str.split()
            if len(parts) < (1 + pick_count): continue

            # Parse date (M/D/YYYY) -> YYYY-MM-DD
            raw_date = parts[0]
            try:
                dt = datetime.strptime(raw_date, "%m/%d/%Y")
                iso_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

            # Parse numbers
            try:
                all_nums = [int(x) for x in parts[1:]]
            except ValueError:
                continue

            main_numbers = all_nums[:pick_count]
            bonus_numbers = all_nums[pick_count:pick_count + bonus_count] if bonus_count > 0 else []

            draws.append({
                "draw_id": line_idx,  # Line number is implicit draw ID
                "draw_date": iso_date,
                "numbers": sorted(main_numbers),
                "bonus": bonus_numbers
            })
    return draws

def import_drawings_to_duckdb(txt_path: Path, lottery_id: str, storage_engine: LotteryStorage = storage) -> int:
    draws = parse_studio_txt(txt_path, lottery_id)
    if draws:
        storage_engine.save_draws(lottery_id, draws)
    return len(draws)

def export_duckdb_to_studio(lottery_id: str, output_path: Path, storage_engine: LotteryStorage = storage) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not storage_engine.use_duckdb:
        df = storage_engine.load_draws(lottery_id)
    else:
        with duckdb.connect(str(storage_engine.db_path)) as con:
            df = con.execute("SELECT draw_id, draw_date, numbers, bonus FROM draws WHERE lottery_id = ? ORDER BY draw_id ASC", [lottery_id]).df()

    if df.empty: return 0

    lines: List[str] = []
    for _, row in df.iterrows():
        dt = pd.to_datetime(row["draw_date"])
        date_str = f"{dt.month}/{dt.day}/{dt.year}"

        nums = row["numbers"]
        if isinstance(nums, str):
            import json
            nums = json.loads(nums)
        num_strs = [f"{int(x):02d}" for x in nums]

        bonus_strs = []
        bonus = row.get("bonus")
        if bonus is not None and not (isinstance(bonus, float) and pd.isna(bonus)):
            if isinstance(bonus, str):
                import json
                bonus = json.loads(bonus)
            bonus_strs = [f"{int(x):02d}" for x in bonus]

        full_tokens = [date_str] + num_strs + bonus_strs
        lines.append(" ".join(full_tokens))

    with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)
```
