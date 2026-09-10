import logging
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_samlotto_txt(file_content: str, pick_count: int, bonus_count: int) -> List[Dict[str, Any]]:
    """
    Parses SamLotto space-delimited text files.
    Maps line numbers to implicit 1-based draw IDs and converts M/D/YYYY date styles.
    """
    draws = []
    lines = file_content.strip().splitlines()
    for idx, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
            
        date_str = parts[0]
        # Parse M/D/YYYY date style to YYYY-MM-DD
        try:
            date_str_clean = date_str.replace("-", "/").replace(".", "/")
            dt = datetime.strptime(date_str_clean, "%m/%d/%Y")
            formatted_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                logger.warning(f"Failed to parse date string: {date_str} on line {idx}")
                continue

        # Parse numbers
        try:
            nums = [int(x) for x in parts[1:]]
        except ValueError:
            logger.warning(f"Failed to parse numbers on line {idx}: {parts[1:]}")
            continue

        # Split into main numbers and bonus numbers using pick count rules
        main_numbers = sorted(nums[:pick_count])
        bonus_numbers = nums[pick_count:pick_count + bonus_count]

        draws.append({
            "draw_id": idx,  # implicit draw ID from line number
            "draw_date": formatted_date,
            "numbers": main_numbers,
            "bonus": bonus_numbers
        })
    return draws

def export_duckdb_to_samlotto(lottery_id: str) -> str:
    """
    Queries draws from DuckDB, formats dates to M/D/YYYY, zero-pads numbers
    to 2-digit strings, and writes the output with CRLF endings.
    """
    from engine.modules.storage import storage
    df = storage.load_draws(lottery_id)
    if df.empty:
        return ""
    
    # Sort chronologically so line numbers map correctly to implicit draw IDs
    df = df.sort_values("draw_id", ascending=True)
    
    lines = []
    for row in df.itertuples():
        # Parse date and format to M/D/YYYY
        try:
            date_val = getattr(row, "draw_date")
            if isinstance(date_val, str):
                dt = datetime.strptime(date_val, "%Y-%m-%d")
            else:
                dt = pd.to_datetime(date_val)
            date_str = f"{dt.month}/{dt.day}/{dt.year}"
        except Exception:
            date_str = str(getattr(row, "draw_date"))

        # Parse and format main numbers
        main_nums = getattr(row, "numbers")
        if isinstance(main_nums, str):
            main_nums = [int(x) for x in main_nums.split(",") if x.strip()]
        
        # Parse and format bonus numbers
        bonus_nums = getattr(row, "bonus", [])
        if pd.isna(bonus_nums):
            bonus_nums = []
        elif isinstance(bonus_nums, str):
            bonus_nums = [int(x) for x in bonus_nums.split(",") if x.strip()]

        # Format as zero-padded 2-digit strings
        main_str_list = [f"{n:02d}" for n in main_nums]
        bonus_str_list = [f"{n:02d}" for n in bonus_nums]
        
        all_parts = [date_str] + main_str_list + bonus_str_list
        line = " ".join(all_parts)
        lines.append(line)
        
    return "\r\n".join(lines) + "\r\n"
