from database.client import supabase
from datetime import date
from utils import to_ist, _format_row
import calendar

# expense queries
def add_expense(
    amount: float,
    description: str,
    currency: str = 'INR',
    category: str = None,
    expense_date: str = None, 
    tags: list[str] = None,
    notes: str = None,
) -> dict:
    payload = {
        "amount": amount,
        "description": description,
        "category": category,
        "date": expense_date or str(date.today()),
        "currency": currency,
        "tags": tags,
        "notes": notes,
    }
    res = supabase.table("expenses").insert(payload).execute()
    return _format_row(res.data[0]) if res.data else {}

def fetch_expenses_by_date(expense_date: str) -> list[dict]:
    res = (
        supabase.table("expenses")
        .select("*")
        .eq("date", expense_date)
        .order("created_at", desc=True)
        .execute()
    )
    return [_format_row(row) for row in res.data]

def _resolve_full_id(short_id: str) -> str | None:
    """Get full UUID from 8-char short ID"""
    res = supabase.table("expenses").select("id").execute()
    for row in res.data:
        if row["id"].startswith(short_id):
            return row["id"]
    return None

def fetch_expense_by_id(short_id: str) -> dict | None:
    full_id = _resolve_full_id(short_id)
    if not full_id:
        return None
    res = supabase.table("expenses").select("*").eq("id", full_id).execute()
    return _format_row(res.data[0]) if res.data else None

def update_expense(short_id: str, updates: dict) -> dict | None:
    updates = {k: v for k, v in updates.items() if v is not None}
    full_id = _resolve_full_id(short_id)
    if not full_id:
        return None
    res = supabase.table("expenses").update(updates).eq("id", full_id).execute()
    return _format_row(res.data[0]) if res.data else None

def delete_expense(short_id: str) -> bool:
    full_id = _resolve_full_id(short_id)
    if not full_id:
        return False
    res = supabase.table("expenses").delete().eq("id", full_id).execute()
    return len(res.data) > 0
         
def fetch_expenses_by_category_and_duration(
    start_date: str = None,
    end_date: str = None,
    category: str = None,
) -> list[dict]:
    query = supabase.table("expenses").select("*").order("date", desc=True)

    if start_date:
        query = query.gte("date", start_date)
    if end_date:
        query = query.lte("date", end_date)
    if category:
        query = query.eq("category", category)

    res = query.execute()
    return [_format_row(row) for row in res.data]

def list_all_expenses(
     ) -> list[dict]:
     query = supabase.table("expenses").select("*").order("date",desc=True)
     res = query.execute()
     return [_format_row(row) for row in res.data]

def fetch_total_by_period(start_date: str, end_date: str) -> float:
    res = (
        supabase.table("expenses")
        .select("amount")
        .gte("date", start_date)
        .lte("date", end_date)
        .execute()
    )
    return sum(row["amount"] for row in res.data)

def fetch_total_by_category(start_date: str, end_date: str) -> dict[str, float]:
    res = (
        supabase.table("expenses")
        .select("category, amount")
        .gte("date", start_date)
        .lte("date", end_date)
        .execute()
    )
    totals = {}
    for row in res.data:
        cat = row["category"] or "Uncategorized"
        totals[cat] = totals.get(cat, 0) + row["amount"]
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

def fetch_total_by_month_year(month : str, year: str) -> dict:
     '''
     Fetch total spending for a specific month year
     '''
     start_date = f"{year}-{month}-01"
     last_day = calendar.monthrange(int(year), int(month))[1]
     end_date = f"{year}-{month}-{last_day:02d}"
     res = (
          supabase.table("expenses")
          .select("amount")
          .gte("date",start_date)
          .lte("date",end_date)
          .execute()
     )
     
     total = sum(row["amount"] for row in res.data)
     return {
          "month" : f"{year}-{month}",
          "total": round(total, 2),
     }

# budget queries

def add_budget(month:str, amount: float) -> dict:
     payload = {
          "month" : month,
          "amount" : amount
     }
     res = supabase.table("budgets").insert(payload).execute()
     return res.data[0] if res.data else {}

def fetch_budgets(month: str = None) -> list[dict]:
    query = supabase.table("budgets").select("*")
    if month:
        query = query.eq("month", month)
    res = query.execute()
    return res.data

def actual_vs_budget(month: str, year: str) -> dict:
    """
    Compare total budget vs actual spending for a specific month and year.
    - month: "02"
    - year: "2026"
    """
    # get actual total
    result = fetch_total_by_month_year(month, year)
    actual_total = result["total"]

    # get budget for this month
    month_str = f"{year}-{month}"
    res = (
        supabase.table("budgets")
        .select("*")
        .eq("month", month_str)
        .execute()
    )

    budget_total = sum(row["amount"] for row in res.data) if res.data else 0

    return {
        "month": month_str,
        "budget": round(budget_total, 2),
        "actual": round(actual_total, 2),
        "remaining": round(budget_total - actual_total, 2),
        "percent_used": round((actual_total / budget_total) * 100, 1) if budget_total else 0,
        "status": "🔴 OVER BUDGET" if actual_total > budget_total else "🟢 WITHIN BUDGET"
    }
     



     