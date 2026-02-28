from fastapi import APIRouter, Query
from datetime import date, timedelta
import calendar, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../expense_tracker_mcp_server"))
from database.queries import fetch_total_by_period, fetch_total_by_category

router = APIRouter()

@router.get("/kpi")
def get_kpi():
    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    this_week_start = today - timedelta(days=today.weekday())

    today_total = fetch_total_by_period(str(today), str(today))
    this_month_total = fetch_total_by_period(str(this_month_start), str(today))
    last_month_total = fetch_total_by_period(str(last_month_start), str(last_month_end))
    this_week_total = fetch_total_by_period(str(this_week_start), str(today))

    mom_change = round(((this_month_total - last_month_total) / last_month_total) * 100, 1) if last_month_total > 0 else 0
    avg_per_day = round(this_month_total / today.day, 2) if today.day else 0

    return {
        "today": round(today_total, 2),
        "this_week": round(this_week_total, 2),
        "this_month": round(this_month_total, 2),
        "last_month": round(last_month_total, 2),
        "mom_change": mom_change,
        "avg_per_day": avg_per_day,
    }

@router.get("/daily")
def get_daily_stats(days: int = Query(30)):
    today = date.today()
    return [
        {"date": str(today - timedelta(days=i)), "amount": round(fetch_total_by_period(str(today - timedelta(days=i)), str(today - timedelta(days=i))), 2)}
        for i in range(days - 1, -1, -1)
    ]

@router.get("/category")
def get_category_stats(month: str = Query(None)):
    today = date.today()
    if month:
        year, mon = month.split("-")
        start = f"{year}-{mon}-01"
        last_day = calendar.monthrange(int(year), int(mon))[1]
        end = f"{year}-{mon}-{last_day:02d}"
    else:
        start = str(today.replace(day=1))
        end = str(today)

    by_category = fetch_total_by_category(start, end)
    return [{"category": cat, "amount": round(amt, 2)} for cat, amt in by_category.items()]

@router.get("/monthly")
def get_monthly_trend(months: int = Query(6)):
    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year - ((i - today.month + 1) // 12 if i >= today.month else 0)
        start = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day:02d}"
        result.append({"month": f"{year}-{month:02d}", "amount": round(fetch_total_by_period(start, end), 2)})
    return result


@router.get("/category-trend")
def get_category_trend(months: int = Query(6)):
    """Each category's spending across last N months — for stacked bar chart"""
    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year - ((i - today.month + 1) // 12 if i >= today.month else 0)
        start = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day:02d}"
        by_category = fetch_total_by_category(start, end)
        result.append({
            "month": f"{year}-{month:02d}",
            **by_category  # spreads category:amount pairs
        })
    return result


@router.get("/payment-method")
def get_payment_method_stats(month: str = Query(None, description="YYYY-MM, defaults to current month")):
    """Breakdown by payment method — for donut chart"""
    today = date.today()
    if month:
        year, mon = month.split("-")
        start = f"{year}-{mon}-01"
        last_day = calendar.monthrange(int(year), int(mon))[1]
        end = f"{year}-{mon}-{last_day:02d}"
    else:
        start = str(today.replace(day=1))
        end = str(today)

    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../expense_tracker_mcp_server"))
    from database.client import supabase

    res = (
        supabase.table("expenses")
        .select("payment_method, amount")
        .gte("date", start)
        .lte("date", end)
        .execute()
    )
    totals = {}
    for row in res.data:
        method = row["payment_method"] or "cash"
        totals[method] = totals.get(method, 0) + row["amount"]

    return [{"method": k, "amount": round(v, 2)} for k, v in sorted(totals.items(), key=lambda x: x[1], reverse=True)]


@router.get("/top-expenses")
def get_top_expenses(
    limit: int = Query(5),
    month: str = Query(None, description="YYYY-MM, defaults to current month")
):
    """Top N highest expenses — for leaderboard/table widget"""
    today = date.today()
    if month:
        year, mon = month.split("-")
        start = f"{year}-{mon}-01"
        last_day = calendar.monthrange(int(year), int(mon))[1]
        end = f"{year}-{mon}-{last_day:02d}"
    else:
        start = str(today.replace(day=1))
        end = str(today)

    from database.client import supabase
    res = (
        supabase.table("expenses")
        .select("*")
        .gte("date", start)
        .lte("date", end)
        .order("amount", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


@router.get("/daily-average")
def get_daily_average(months: int = Query(3)):
    """Average daily spend per month — for trend insight"""
    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year - ((i - today.month + 1) // 12 if i >= today.month else 0)
        start = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day:02d}"
        total = fetch_total_by_period(start, end)
        result.append({
            "month": f"{year}-{month:02d}",
            "avg_per_day": round(total / last_day, 2)
        })
    return result


@router.get("/weekday-pattern")
def get_weekday_pattern(months: int = Query(1)):
    """Average spending by day of week — for heatmap/bar chart"""
    today = date.today()
    start = str((today.replace(day=1) if months == 1 else today - timedelta(days=30 * months)))
    end = str(today)

    from database.client import supabase
    res = (
        supabase.table("expenses")
        .select("date, amount")
        .gte("date", start)
        .lte("date", end)
        .execute()
    )

    from collections import defaultdict
    day_totals = defaultdict(float)
    day_counts = defaultdict(int)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for row in res.data:
        d = date.fromisoformat(row["date"])
        day_totals[d.weekday()] += row["amount"]
        day_counts[d.weekday()] += 1

    return [
        {
            "day": days[i],
            "avg_amount": round(day_totals[i] / day_counts[i], 2) if day_counts[i] else 0,
            "total": round(day_totals[i], 2)
        }
        for i in range(7)
    ]