"""REST API for the Personal Expenses UI. Run with uvicorn on port 9005."""
from datetime import date
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from expense_service import add_expense, list_expenses, delete_expense, expense_summary

app = FastAPI(title="Personal Expenses API", version="1.0.0", description="Expense tracking API backed by SQLite")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ExpenseIn(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=500)
    expense_date: str | None = None

class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

@app.get("/health")
def health(): return {"status": "ok", "service": "personal-expenses-api"}

@app.post("/expenses")
def create(payload: ExpenseIn):
    try: return add_expense(payload.amount, payload.category, payload.description, payload.expense_date)
    except ValueError as e: raise HTTPException(400, str(e))

@app.get("/expenses")
def get_all(category: str | None = None, limit: int = 100):
    try: return list_expenses(category, limit)
    except (ValueError, TypeError) as e: raise HTTPException(400, str(e))

@app.delete("/expenses/{expense_id}")
def remove(expense_id: int):
    if not delete_expense(expense_id): raise HTTPException(404, "Expense not found")
    return {"deleted": True, "expense_id": expense_id}

@app.get("/summary")
def summary(month: str | None = None):
    try: return expense_summary(month)
    except ValueError as e: raise HTTPException(400, str(e))

@app.post("/chat")
def chat(payload: ChatIn):
    """Simple intent-based chatbot that invokes the same business functions as MCP tools."""
    text = payload.message.strip()
    low = text.lower()
    try:
        if any(w in low for w in ["summary", "total", "spent", "spending", "breakdown"]):
            month_match = re.search(r"\b(20\d{2}-\d{2})\b", text)
            data = expense_summary(month_match.group(1) if month_match else None)
            breakdown = ", ".join(f"{x['category']}: {x['total']:.2f}" for x in data['by_category']) or "no expenses yet"
            return {"reply": f"Your spending for {data['month']} is {data['total']:.2f} across {data['count']} expenses. By category: {breakdown}.", "data": data}
        if any(w in low for w in ["show", "list", "view", "recent"]):
            rows = list_expenses()
            if not rows: return {"reply": "You have no expenses recorded yet. Add your first expense using the form.", "data": rows}
            lines = [f"#{r['id']} {r['expense_date']} | {r['category']} | {r['amount']:.2f} | {r['description']}" for r in rows[:10]]
            return {"reply": "Here are your latest expenses:\n" + "\n".join(lines), "data": rows}
        match = re.search(r"(?:add|record|log)\s+(?:an?\s+)?expense\s+(?:of\s+)?(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)\s+(?:for|on|to)\s+([a-zA-Z ]+?)(?:\s+(?:for|,|-)\s+(.+))?$", text, re.I)
        if match:
            row = add_expense(float(match.group(1)), match.group(2).strip(), (match.group(3) or "").strip())
            return {"reply": f"Expense recorded: {row['amount']:.2f} for {row['category']} on {row['expense_date']} (ID #{row['id']}).", "data": row}
        return {"reply": "I can help you add expenses, list expenses, or view your monthly spending summary. Try: 'Add expense 250 for Food' or 'Show my expenses' or 'Monthly summary'.", "data": None}
    except ValueError as e: raise HTTPException(400, str(e))
