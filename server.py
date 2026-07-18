from mcp.server.fastmcp import FastMCP
from src.db import init_db
from src.tools import register_tools

# Initialize the FastMCP server
mcp = FastMCP("Personal Budget Server")

# Register all budget tools
register_tools(mcp)

if __name__ == "__main__":
    init_db()
    # Runs over stdio by default, the standard transport for local MCP tools
    mcp.run()
