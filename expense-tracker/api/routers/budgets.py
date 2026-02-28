from fastapi import APIRouter, Query
from database.queries import fetch_budgets, actual_vs_budget

router = APIRouter()

@router.get("/")
def get_budgets(month: str = Query(None, description="YYYY-MM")):
    return fetch_budgets(month)

@router.get("/vs-actual")
def get_budget_vs_actual(
    month: str = Query(..., description="Two digit month e.g. 02"),
    year: str = Query(..., description="Four digit year e.g. 2026"),
):
    return actual_vs_budget(month, year)