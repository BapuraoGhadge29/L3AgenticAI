"""Shared SQLite business logic used by the REST API and MCP server."""
import os, sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(os.getenv("EXPENSE_DB_PATH", Path(__file__).with_name("expenses.db")))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL CHECK(amount > 0),
        category TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        expense_date TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    db.commit()
    return db


def add_expense(amount: float, category: str, description: str = "", expense_date: str | None = None):
    if amount <= 0: raise ValueError("Amount must be greater than zero")
    if not category or not category.strip(): raise ValueError("Category is required")
    try: date.fromisoformat(expense_date or date.today().isoformat())
    except ValueError: raise ValueError("Date must use YYYY-MM-DD format")
    with connect() as db:
        cur = db.execute("INSERT INTO expenses(amount,category,description,expense_date) VALUES(?,?,?,?)",
                         (round(float(amount), 2), category.strip().title(), description.strip(), expense_date or date.today().isoformat()))
        row = db.execute("SELECT * FROM expenses WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)


def list_expenses(category: str | None = None, limit: int = 100):
    limit = max(1, min(int(limit), 500))
    with connect() as db:
        if category:
            rows = db.execute("SELECT * FROM expenses WHERE lower(category)=lower(?) ORDER BY expense_date DESC,id DESC LIMIT ?", (category, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM expenses ORDER BY expense_date DESC,id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def delete_expense(expense_id: int):
    with connect() as db:
        cur = db.execute("DELETE FROM expenses WHERE id=?", (int(expense_id),))
        return cur.rowcount > 0


def expense_summary(month: str | None = None):
    month = month or date.today().strftime("%Y-%m")
    try: date.fromisoformat(month + "-01")
    except ValueError: raise ValueError("Month must use YYYY-MM format")
    with connect() as db:
        total, count = db.execute("SELECT COALESCE(SUM(amount),0),COUNT(*) FROM expenses WHERE substr(expense_date,1,7)=?", (month,)).fetchone()
        rows = db.execute("SELECT category,SUM(amount) total,COUNT(*) count FROM expenses WHERE substr(expense_date,1,7)=? GROUP BY category ORDER BY total DESC", (month,)).fetchall()
        return {"month": month, "total": round(total, 2), "count": count, "by_category": [dict(r) for r in rows]}
