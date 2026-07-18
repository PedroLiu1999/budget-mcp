from src.tools.summary import register_summary_tools
from src.tools.transactions import register_transaction_tools
from src.tools.categories import register_category_tools

def register_tools(mcp):
    """Register all tool modules with the FastMCP instance."""
    register_summary_tools(mcp)
    register_transaction_tools(mcp)
    register_category_tools(mcp)

__all__ = ["register_tools"]
