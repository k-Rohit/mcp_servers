from fastapi import APIRouter, Query
from typing import Optional
from database.queries import list_all_expenses, fetch_expenses_by_category_and_duration, fetch_expenses_by_date

router = APIRouter()

@router.get("/")
def get_expenses(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    if start_date or end_date or category:
        return fetch_expenses_by_category_and_duration(start_date=start_date, end_date=end_date, category=category)
    return list_all_expenses()

@router.get("/by-date")
def get_expenses_by_date(date: str = Query(..., description="YYYY-MM-DD")):
    return fetch_expenses_by_date(date)