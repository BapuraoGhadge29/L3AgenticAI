"""MCP tools for the Personal Expenses application. Run: py expenses_mcp_server.py"""
from mcp.server.fastmcp import FastMCP
from expense_service import add_expense, list_expenses, delete_expense, expense_summary

mcp = FastMCP("personal-expenses")

@mcp.tool()
def create_expense(amount: float, category: str, description: str = "", expense_date: str = "") -> dict:
    """Record an expense. Date is optional and must be YYYY-MM-DD."""
    return add_expense(amount, category, description, expense_date or None)

@mcp.tool()
def get_expenses(category: str = "", limit: int = 100) -> list:
    """List recent expenses, optionally filtered by category."""
    return list_expenses(category or None, limit)

@mcp.tool()
def get_expense_summary(month: str = "") -> dict:
    """Get monthly spending totals and category breakdown. Month format: YYYY-MM."""
    return expense_summary(month or None)

@mcp.tool()
def remove_expense(expense_id: int) -> dict:
    """Delete an expense by its numeric ID."""
    return {"deleted": delete_expense(expense_id), "expense_id": expense_id}

if __name__ == "__main__":
    mcp.run(transport="stdio")
