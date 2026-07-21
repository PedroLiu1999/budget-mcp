from fastmcp import FastMCP
from src.tools import register_tools

# Initialize the FastMCP server
mcp = FastMCP("Personal Budget Server")

# Register all budget tools (also ensures DB tables & seed data are initialized)
register_tools(mcp)

if __name__ == "__main__":
    # Runs over stdio by default, the standard transport for local MCP tools
    mcp.run()

