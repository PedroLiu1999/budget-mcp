# 💰 Personal Budget MCP Server

A lightweight, locally-hosted Model Context Protocol (MCP) server for managing your personal finances. Built with Python, `FastMCP`, and SQLite, this server empowers any MCP-compatible LLM client to securely log transactions and analyze your budget directly on your machine.

## ✨ Features

- **Local & Private:** All financial data is stored locally in a serverless SQLite database (`budget.db`). 
- **Zero-Friction Setup:** Powered by `uv` for lightning-fast, reproducible dependency management. No virtual environment headaches.
- **Universal Compatibility:** Works seamlessly with Claude Desktop, Claude Code, Cursor, Goose, and any other MCP-compliant host.

---

## 🛠 Available Tools

This server exposes the following tools to the connected LLM:

| Tool Name | Description | Arguments |
| :--- | :--- | :--- |
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

## 🚀 Prerequisites

You only need one thing installed on your system:
- **[uv](https://docs.astral.sh/uv/)** - An extremely fast Python package and project manager written in Rust.

---

## 📦 Installation & Setup

1. **Clone or download** this project repository to your local machine.
2. **Navigate** to the project directory in your terminal:
   ```bash
   cd path/to/budget-mcp
   ```
3. **Initialize/Sync dependencies** (optional, as `uv run` handles this dynamically):
   ```bash
   uv sync
   ```

*(Note: The `budget.db` SQLite file will be automatically generated in the project root the first time a tool is called.)*

---

## 🔌 Connecting to MCP Clients

Because this server communicates over standard input/output (`stdio`), you must configure your AI client to execute it via `uv`. 

**Important:** Always use the **absolute path** to the project directory so your client can find it from anywhere.

### 1. Claude Code (CLI)
Run this command in your terminal to globally register the server with Claude Code:
```bash
claude mcp add budget -- uv run --directory "/absolute/path/to/budget-mcp" server.py
```
*(If you are on Windows and encounter path execution errors, point directly to the virtual environment python executable instead of using `uv run`.)*

### 2. Claude Desktop
Add the following configuration to your `claude_desktop_config.json` file (located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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
In Cursor, go to **Settings > Features > MCP**, click **Add New MCP Server**, and configure it as follows:
- **Type:** `command`
- **Name:** `budget-mcp`
- **Command:** `uv run --directory "/absolute/path/to/budget-mcp" server.py`

---

## 🧪 Testing Locally (Without an LLM)

You can use the official MCP Inspector to manually test the tools and ensure your SQLite database is working correctly:

```bash
npx -y @modelcontextprotocol/inspector uv run server.py
```

## 📝 License
MIT