# utils/timezone.py
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
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

def _parse_period(period: str) -> tuple[str, str]:
    today = date.today()
    match period.lower().strip():
        case "today":
            return str(today), str(today)
        case "yesterday":
            d = today - relativedelta(days=1)
            return str(d), str(d)
        case "this week":
            start = today - relativedelta(days=today.weekday())
            return str(start), str(today)
        case "last week":
            start = today - relativedelta(days=today.weekday(), weeks=1)
            end = start + relativedelta(days=6)
            return str(start), str(end)
        case "this month":
            return str(today.replace(day=1)), str(today)
        case "last month":
            first = today.replace(day=1)
            end = first - relativedelta(days=1)
            start = end.replace(day=1)
            return str(start), str(end)
        case "this year":
            return str(today.replace(month=1, day=1)), str(today)
        case _:
            return str(today.replace(day=1)), str(today)


def _format_expense_line(e: dict, index: int = None) -> str:
    prefix = f"{index}." if index else "•"
    tags = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
    return (
        f"  {prefix} [{e['id'][:8]}] ₹{e['amount']} | {e['description']} "
        f"| {e.get('category') or 'Uncategorized'} | {e.get('payment_method', 'cash')}{tags}"
    )