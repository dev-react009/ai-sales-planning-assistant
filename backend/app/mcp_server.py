import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from mcp.server import MCPServer

from app.tools.sales_tools import (
    get_accounts_by_territory,
    get_quota_attainment,
    get_unassigned_accounts,
)


mcp = MCPServer(
    "AI Sales Planning Assistant",
)


@mcp.tool()
def quota_attainment(threshold: float = 70.0):
    """Get sales representatives below the specified quota attainment threshold."""
    return get_quota_attainment(threshold)


@mcp.tool()
def unassigned_enterprise_accounts():
    """Get enterprise accounts that currently have no assigned sales representative."""
    return get_unassigned_accounts()


@mcp.tool()
def accounts_by_territory(territory_name: str):
    """Get accounts belonging to a specific sales territory."""
    return get_accounts_by_territory(territory_name)


if __name__ == "__main__":
    mcp.run()