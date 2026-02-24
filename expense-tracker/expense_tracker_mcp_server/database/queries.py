from database.client import supabase
from datetime import date
from utils import to_ist, _format_row

# expense queries
def add_expense(
    amount: float,
    description: str,
    currency: str = 'INR',
    category: str = None,
    date: str = None,
    tags: list[str] = None,
    notes: str = None) -> dict :
         payload = {
        "amount": amount,
        "description": description,
        "category": category,
        "date": date or str(date.today()),
        "currency": currency,
        "tags": tags,
        "notes": notes,
    }
         res = supabase.table("expenses").insert(payload).execute()
         return _format_row(res.data[0]) if res.data else {}
         
     

     