# Personal Expenses: complete end-to-end application

A runnable expense tracker with a Python MCP server, FastAPI REST API, React + TypeScript UI, and a shared SQLite database. The MCP server and REST API expose the same business operations through `expense_service.py`.

## Architecture

- **React UI** (`05-expenses-ui-app`): dashboard, expense form, transaction list, category breakdown, and chat assistant.
- **FastAPI** (`expense_rest_api_server.py`): HTTP endpoints consumed by the browser UI on port 9005.
- **MCP server** (`expenses_mcp_server.py`): stdio MCP tools for MCP-compatible clients.
- **Shared service** (`expense_service.py`): validation and SQLite persistence used by both servers.
- **Database**: `expenses.db` is created automatically beside the Python files on first use.

The REST API and MCP server are separate entry points that share the same service and database. The browser talks to the REST API; an MCP host launches the MCP server over stdio. This avoids pretending that the REST API is itself an MCP client.

## Requirements

- Python 3.10 or newer (3.11+ recommended)
- Node.js 20.19+ or 22.12+ recommended
- npm

## Windows PowerShell: run all three processes

Extract this folder, open PowerShell in the `personal-expenses` project root, and keep three terminal windows open.

### Terminal 1: install Python dependencies and start MCP server

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py expenses_mcp_server.py
```

The MCP server uses stdio. It is expected to wait for an MCP host/client and may not print a web URL. Keep this terminal running. If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.

### Terminal 2: start REST API

Activate the same environment if this is a new terminal, then run:

```powershell
cd path\to\personal-expenses
.\.venv\Scripts\Activate.ps1
py -m uvicorn expense_rest_api_server:app --reload --port 9005
```

Check API health at http://localhost:9005/health and interactive API documentation at http://localhost:9005/docs.

### Terminal 3: start UI

```powershell
cd path\to\personal-expenses\05-expenses-ui-app
npm install
npm run dev
```

Open http://localhost:5173.

## Configure API URL

The UI defaults to `http://localhost:9005`. To override it, create `05-expenses-ui-app/.env.local`:

```env
VITE_API_URL=http://localhost:9005
```

Restart `npm run dev` after changing the environment file. You do not need to edit the TSX source.

## REST endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/expenses` | Add an expense |
| GET | `/expenses` | List expenses; optional `category` and `limit` |
| DELETE | `/expenses/{expense_id}` | Delete an expense |
| GET | `/summary` | Monthly totals; optional `month=YYYY-MM` |
| POST | `/chat` | Chat assistant |

Example add request:

```json
{"amount":250,"category":"Food","description":"Lunch","expense_date":"2026-11-25"}
```

## MCP tools

- `create_expense(amount, category, description, expense_date)`
- `get_expenses(category, limit)`
- `get_expense_summary(month)`
- `remove_expense(expense_id)`

Configure an MCP-compatible host to launch `py` with the absolute path to `expenses_mcp_server.py` as its argument, using the project root as its working directory and the project's Python environment. Example configuration shape (adjust paths for your machine):

```json
{
  "mcpServers": {
    "personal-expenses": {
      "command": "C:\\path\\to\\personal-expenses\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\personal-expenses\\expenses_mcp_server.py"],
      "cwd": "C:\\path\\to\\personal-expenses"
    }
  }
}
```

## End-to-end smoke test

1. Start all three processes as described above.
2. Open the UI and add an expense, e.g. INR 250, category Food, description Lunch.
3. Confirm it appears in Recent expenses and the monthly total changes.
4. In the chatbot, send `Show my expenses` and `Monthly summary`.
5. Open `/docs` and try `GET /expenses`.
6. Connect an MCP host and invoke `get_expenses` or `get_expense_summary`; the same SQLite records are used.

## Notes

- Currency display is INR; amounts are stored as decimal-like SQLite REAL values rounded to two decimal places.
- This is a local learning/demo application, not a production financial system. It has no authentication, multi-user isolation, or cloud backup. Do not expose the development servers to an untrusted network.
- The chat interface uses simple local intent parsing, not an LLM. MCP tools are available to an MCP host independently.
