from datetime import date, datetime
from typing import Annotated
from pydantic import Field
from dateutil.relativedelta import relativedelta
from mcp_init import mcp
from utils import _format_expense_line, _parse_period

from database.queries import (
    add_expense as db_add_expense,
    fetch_expenses_by_date,
    fetch_expenses_by_category_and_duration,
    list_all_expenses,
    fetch_total_by_period,
    fetch_total_by_category,
    fetch_total_by_month_year,
    fetch_expense_by_id,
    update_expense,
    delete_expense,
    add_budget,
    fetch_budgets,
    actual_vs_budget,
)

@mcp.tool()
def add_expense(
    amount: Annotated[float, Field(description="Expense amount in INR e.g. 450.0")],
    description: Annotated[str, Field(description="What the expense was for e.g. 'Zomato dinner', 'Uber to airport'")],
    category: Annotated[str | None, Field(description="Category: Food, Travel, Shopping, Bills, Entertainment, Health, Other")] = None,
    expense_date: Annotated[str | None, Field(description="Date in YYYY-MM-DD format e.g. '2026-02-24'. Defaults to today if not provided.")] = None,
    currency: Annotated[str, Field(description="Currency code, defaults to INR")] = "INR",
    tags: Annotated[list[str] | None, Field(description="Optional tags e.g. ['work', 'reimbursable']")] = None,
    notes: Annotated[str | None, Field(description="Any extra notes about this expense")] = None,
) -> str:
    """
    Add a new expense to the tracker.
    Use this when the user mentions spending money on something.
    Description could be inferred from the prompt or input that user gives
    If category is not mentioned, make a reasonable guess based on the description.
    If date is not mentioned, use today's date.
    """
    result = db_add_expense(
        amount=amount,
        description=description,
        currency=currency,
        category=category,
        expense_date=expense_date,
        tags=tags,
        notes=notes,
    )

    if result:
        return (
            f" Expense added!\n"
            f"  ID          : {result['id']}\n"
            f"  Amount      : ₹{result['amount']} {result['currency']}\n"
            f"  Description : {result['description']}\n"
            f"  Category    : {result.get('category') or 'Uncategorized'}\n"
            f"  Date        : {result['date']}\n"
            f"  Added at    : {result['created_at']}"
        )
    return "Failed to add expense."

@mcp.tool()
def get_expenses_by_date(
    expense_date: Annotated[str, Field(description="Date in YYYY-MM-DD format e.g. '2026-02-24'. Convert 'today', 'yesterday' to actual date before passing.")],
) -> str:
    """
    Fetch and list all expenses on a specific date.
    ALWAYS call this first before editing or deleting an expense.
    Show the list to the user and ask which expense they want to modify.
    Each expense shows a short 8-character ID used for edit/delete operations.
    """
    expenses = fetch_expenses_by_date(expense_date)

    if not expenses:
        return f"No expenses found on {expense_date}."

    lines = [f"📋 Expenses on {expense_date} — {len(expenses)} entries\n"]
    for i, e in enumerate(expenses, 1):
        lines.append(_format_expense_line(e, index=i))
    lines.append("\nWhich expense would you like to edit or delete?")
    return "\n".join(lines)

@mcp.tool()
def list_expenses(
    period: Annotated[str, Field(description="Time period: 'today', 'yesterday', 'this week', 'last week', 'this month', 'last month', 'this year'")] = "this month",
    category: Annotated[str | None, Field(description="Filter by category e.g. 'Food', 'Travel'. Leave empty for all categories.")] = None,
) -> str:
    """
    List expenses for a given time period with optional category filter.
    Use this when the user wants to see or review their expenses for a period.
    """
    start_date, end_date = _parse_period(period)
    expenses = fetch_expenses_by_category_and_duration(
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    if not expenses:
        return f"No expenses found for {period}."

    total = sum(e["amount"] for e in expenses)
    lines = [f"📋 {period.title()} expenses — {len(expenses)} entries | Total: ₹{total:.2f}\n"]
    for i, e in enumerate(expenses, 1):
        lines.append(f"  {i}. {e['date']} | ₹{e['amount']} | {e['description']} | {e.get('category') or 'Uncategorized'}")
    return "\n".join(lines)

@mcp.tool()
def list_all() -> str:
    """
    List every expense ever recorded.
    Use this when the user asks to see all expenses with no date filter.
    """
    expenses = list_all_expenses()

    if not expenses:
        return "No expenses found."

    total = sum(e["amount"] for e in expenses)
    lines = [f"📋 All expenses — {len(expenses)} entries | Total: ₹{total:.2f}\n"]
    for i, e in enumerate(expenses, 1):
        lines.append(f"  {i}. {e['date']} | ₹{e['amount']} | {e['description']} | {e.get('category') or 'Uncategorized'}")
    return "\n".join(lines)

@mcp.tool()
def edit_expense(
    expense_id: Annotated[str, Field(description="The 8-character short ID shown in get_expenses_by_date list e.g. 'df55f75c'")],
    amount: Annotated[float | None, Field(description="New amount in INR. Only pass if user wants to change the amount.")] = None,
    description: Annotated[str | None, Field(description="New description. Only pass if user wants to change it.")] = None,
    category: Annotated[str | None, Field(description="New category: Food, Travel, Shopping, Bills, Entertainment, Health, Other")] = None,
    expense_date: Annotated[str | None, Field(description="New date in YYYY-MM-DD. Only pass if user wants to change the date.")] = None,
    payment_method: Annotated[str | None, Field(description="New payment method: cash, upi, card, netbanking, other")] = None,
    notes: Annotated[str | None, Field(description="New notes. Only pass if user wants to change notes.")] = None,
) -> str:
    """
    Edit an existing expense by its short ID.
    ONLY call this AFTER calling get_expenses_by_date and the user has selected which expense to edit.
    Only pass the fields the user wants to change — everything else remains unchanged.
    """
    updates = {
        "amount": amount,
        "description": description,
        "category": category,
        "date": expense_date,
        "payment_method": payment_method,
        "notes": notes,
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = update_expense(expense_id, updates)

    if result:
        return (
            f" Expense updated!\n"
            f"  Description : {result['description']}\n"
            f"  Amount      : ₹{result['amount']}\n"
            f"  Category    : {result.get('category') or 'Uncategorized'}\n"
            f"  Date        : {result['date']}\n"
            f"  Updated at  : {result['updated_at']}"
        )
    return f"Could not find or update expense with ID '{expense_id}'. Try calling get_expenses_by_date again."


@mcp.tool()
def delete_expense_tool(
    expense_id: Annotated[str, Field(description="The 8-character short ID shown in get_expenses_by_date list e.g. 'df55f75c'. Get this by calling get_expenses_by_date first.")],
) -> str:
    """
    Delete an expense by its short ID.
    
    WORKFLOW — strictly follow this order:
    1. ALWAYS call get_expenses_by_date first to show the user their expenses
    2. Ask the user WHICH expense they want to delete
    3. Show the user exactly what will be deleted (description, amount, date)
    4. Ask for EXPLICIT confirmation — "Are you sure you want to delete this?"
    5. Only call this tool AFTER the user confirms with yes/confirm/delete

    NEVER call this tool without confirmation from the user.
    NEVER guess which expense to delete — always show the list first.
    """
    expense = fetch_expense_by_id(expense_id)
    if not expense:
        return f"No expense found with ID '{expense_id}'. Try calling get_expenses_by_date again."

    success = delete_expense(expense_id)
    if success:
        return (
            f" Deleted expense:\n"
            f"  Description : {expense['description']}\n"
            f"  Amount      : ₹{expense['amount']}\n"
            f"  Date        : {expense['date']}"
        )
    return "Failed to delete expense."


@mcp.tool()
def summarize_expenses(
    period: Annotated[str, Field(description="Time period: 'today', 'yesterday', 'this week', 'last week', 'this month', 'last month', 'this year'")] = "this month",
) -> str:
    """
    Summarize total spending and breakdown by category for a period.
    Use this when user asks 'how much did I spend', 'give me a summary', 'spending breakdown'.
    """
    start_date, end_date = _parse_period(period)
    total = fetch_total_by_period(start_date, end_date)
    by_category = fetch_total_by_category(start_date, end_date)

    if total == 0:
        return f"No expenses recorded for {period}."

    lines = [
        f" Summary — {period.title()} ({start_date} → {end_date})",
        f"   Total Spent : ₹{total:.2f}",
        "",
        "   By Category :",
    ]
    for cat, amt in by_category.items():
        pct = (amt / total) * 100
        bar = "█" * int(pct / 5)
        lines.append(f"   {cat:<20} ₹{amt:>8.2f}  {pct:>5.1f}%  {bar}")

    return "\n".join(lines)


@mcp.tool()
def summarize_by_month(
    month: Annotated[str, Field(description="Month as two digits e.g. '02' for February, '12' for December")],
    year: Annotated[str, Field(description="Year as four digits e.g. '2026'")],
) -> str:
    """
    Summarize total spending for a specific month and year.
    Use when user asks about a specific month like 'how much did I spend in January 2026'.
    """
    result = fetch_total_by_month_year(month, year)
    return (
        f" Summary for {result['month']}\n"
        f"   Total Spent : ₹{result['total']:.2f}"
    )

@mcp.tool()
def set_budget(
    month: Annotated[str, Field(description="Month in YYYY-MM format e.g. '2026-02' for February 2026")],
    amount: Annotated[float, Field(description="Budget limit in INR for that month e.g. 10000")],
) -> str:
    """
    Set a monthly budget limit.
    Use when user says 'set my budget for March to 15000' or 'I want to spend only 8000 this month'.
    """
    result = add_budget(month=month, amount=amount)
    if result:
        return f"Budget set: ₹{amount:.2f} for {month}"
    return "Failed to set budget."


@mcp.tool()
def check_budget(
    month: Annotated[str, Field(description="Month as two digits e.g. '02' for February")],
    year: Annotated[str, Field(description="Year as four digits e.g. '2026'")],
) -> str:
    """
    Check budget vs actual spending for a given month.
    Use when user asks 'am I over budget', 'how much budget is left', 'budget status for this month'.
    """
    result = actual_vs_budget(month, year)

    return (
        f"💰 Budget vs Actual — {result['month']}\n"
        f"   Budget      : ₹{result['budget']:.2f}\n"
        f"   Spent       : ₹{result['actual']:.2f}\n"
        f"   Remaining   : ₹{result['remaining']:.2f}\n"
        f"   Used        : {result['percent_used']}%\n"
        f"   Status      : {result['status']}"
    )


