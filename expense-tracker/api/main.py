from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import expenses, stats, budgets

app = FastAPI(title="Expense tracker API",version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])


@app.get("/")
def root():
    return {"message": "Expense Tracker API is running 🚀", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "Fast API server running"}
