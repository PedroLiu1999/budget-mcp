# 💰 Personal Budget MCP Server

A lightweight Model Context Protocol (MCP) server for managing personal finances. Built with Python, `FastMCP`, SQLAlchemy, SQLite, and PostgreSQL, this server empowers any MCP-compatible LLM client to securely log transactions, manage category libraries, and analyze budgets.

---

## ✨ Features

- **Local & Cloud Storage:** Runs with zero setup using local SQLite (in-memory or file-based `data/budget.db`), or seamlessly connects to cloud PostgreSQL providers like **Neon DB**.
- **Interactive Budget Dashboard:** Built-in UI application providing visual category pie charts and searchable transaction data tables via `prefab-ui`.
- **Zero-Friction Package Management:** Powered by `uv` for reproducible, lightning-fast dependency resolution.
- **Universal MCP Compatibility:** Connects with Claude Desktop, Claude Code, Cursor, Goose, Horizon, Open WebUI, and any other MCP host.

---

## 🛠 Available Tools

| Tool Name | Description | Arguments |
| :--- | :--- | :--- |
| `budget_dashboard` | Interactive UI application providing a category breakdown chart and searchable transaction table. | `month` (optional str: 'YYYY-MM')<br>`type` (optional str: 'income' or 'expense')<br>`limit` (optional int, default 100) |
| `add_transaction` | Logs a new income or expense to the database. | `amount` (float)<br>`category_id` (int: valid category ID from `list_categories`)<br>`description` (str)<br>`type` (str: 'income' or 'expense', defaults to 'expense')<br>`date` (optional str: 'YYYY-MM-DD' or ISO string, defaults to current date) |
| `get_summary` | Retrieves an aggregated financial summary (income, expense, net balance, and optional category breakdown). | `month` (optional str: 'YYYY-MM')<br>`start_date` (optional str: 'YYYY-MM-DD')<br>`end_date` (optional str: 'YYYY-MM-DD')<br>`category_id` (optional int)<br>`type` (optional str: 'income' or 'expense')<br>`by_category` (optional bool, default False) |
| `get_transactions` | Retrieves detailed transaction records based on filter criteria. | `category_id` (optional int)<br>`type` (optional str: 'income' or 'expense')<br>`month` (optional str: 'YYYY-MM')<br>`start_date` (optional str: 'YYYY-MM-DD')<br>`end_date` (optional str: 'YYYY-MM-DD')<br>`min_amount` (optional float)<br>`max_amount` (optional float)<br>`search` (optional str)<br>`limit` (optional int, default 50) |
| `update_transaction` | Updates an existing transaction record by ID. | `transaction_id` (int)<br>`amount` (optional float)<br>`category_id` (optional int)<br>`description` (optional str)<br>`type` (optional str: 'income' or 'expense')<br>`date` (optional str: 'YYYY-MM-DD') |
| `delete_transaction` | Removes a transaction record from the database by ID. | `transaction_id` (int) |
| `list_categories` | Lists active categories in the category library. | `type` (optional str: 'expense' or 'income') |
| `add_category` | Adds a new category to the category library. | `name` (str)<br>`type` (optional str: 'expense' or 'income', default 'expense')<br>`description` (optional str) |
| `update_category` | Updates an existing category's properties. | `category_id_or_name` (str)<br>`new_name` (optional str)<br>`type` (optional str)<br>`description` (optional str) |
| `delete_category` | Removes a category from the library. Denies deletion if active transactions are linked unless `reassign_to_category_id` is provided. | `category_id_or_name` (str)<br>`reassign_to_category_id` (optional int) |

---

## ⚙️ Database Setup & Configuration

Database settings are configured via the `DATABASE_URL` environment variable (defined in a `.env` file or environment settings).

### 1. Local SQLite (Default)
- **In-Memory** (default fallback if `DATABASE_URL` is omitted):
  ```env
  DATABASE_URL=sqlite:///:memory:
  ```
- **Local SQLite File**:
  ```env
  DATABASE_URL=sqlite:///data/budget.db
  ```

### 2. Cloud PostgreSQL (Neon DB)
To persist data across cloud deployments, set `DATABASE_URL` to your Neon DB / PostgreSQL connection string:
```env
DATABASE_URL=postgresql://<user>:<password>@<neon-hostname>/<dbname>?sslmode=require
```
*(Note: Database tables and 15 default category seeds are automatically created on initial server startup.)*

---

## ☁️ Cloud Deployment (Horizon & Remote Hosts)

When deploying to remote platforms like **Horizon** (`horizon.perfect.io`), Docker, or cloud hosts:

1. **Set Environment Variables**:
   In your deployment project settings, set `DATABASE_URL` to your cloud PostgreSQL database string (e.g., Neon DB):
   ```env
   DATABASE_URL=postgresql://user:password@ep-xyz.neon.tech/neondb?sslmode=require
   ```

2. **Entrypoint**:
   Point your cloud server runner or ASGI container to `server.py:mcp` or run via `fastmcp`:
   ```bash
   fastmcp run server.py:mcp
   ```
   *The server automatically initializes database schema tables and seeds default categories upon import on cloud environments.*

---

## 🔌 Connecting to Local MCP Clients

### 1. Claude Code (CLI)
Register the server globally:
```bash
claude mcp add budget -- uv run --directory "/absolute/path/to/budget-mcp" server.py
```

### 2. Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "personal-budget": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/budget-mcp",
        "server.py"
      ]
    }
  }
}
```

### 3. Cursor IDE
In Cursor **Settings > Features > MCP**, click **Add New MCP Server**:
- **Type:** `command`
- **Name:** `budget-mcp`
- **Command:** `uv run --directory "/absolute/path/to/budget-mcp" server.py`

---

## 🌐 Open WebUI Integration

Connect this stdio server to [Open WebUI](https://github.com/open-webui/open-webui) using **`mcpo`**:

```bash
# 1. Start the mcpo HTTP proxy
uvx mcpo --port 8000 -- uv run server.py

# 2. In Open WebUI, navigate to Admin Panel > Settings > External Tools
# Add OpenAPI Connection URL: http://localhost:8000 (or http://host.docker.internal:8000 if using Docker)
```

---

## 🧪 Testing & Diagnostics

Run automated tests:
```bash
uv run pytest
```

Manually inspect tools with MCP Inspector:
```bash
npx -y @modelcontextprotocol/inspector uv run server.py
```

---

## 📝 License
MIT