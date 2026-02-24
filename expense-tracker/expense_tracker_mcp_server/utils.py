# utils/timezone.py
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def to_ist(utc_str: str) -> str:
    if not utc_str:
        return utc_str
    utc_dt = datetime.fromisoformat(utc_str)
    ist_dt = utc_dt.astimezone(IST)
    return ist_dt.strftime("%Y-%m-%d %I:%M %p IST")  # e.g. "2026-02-24 08:54 AM IST"


def _format_row(row: dict) -> dict:
    """Convert UTC timestamps to IST for display"""
    if "created_at" in row:
        row["created_at"] = to_ist(row["created_at"])
    if "updated_at" in row:
        row["updated_at"] = to_ist(row["updated_at"])
    return row