from fastmcp import FastMCP
from src.db import init_db
from src.tools import register_tools

# Ensure database tables exist and default categories are seeded
init_db()

# Initialize the FastMCP server
mcp = FastMCP("Personal Budget Server")

# Register all budget tools
register_tools(mcp)

if __name__ == "__main__":
    # Runs over stdio by default, the standard transport for local MCP tools
    mcp.run()

