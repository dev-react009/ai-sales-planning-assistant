import json

from mcp import Client
from app.mcp_server import mcp


async def call_mcp_tool(
    tool_name: str,
    arguments: dict | None = None,
):
    async with Client(mcp) as client:
        result = await client.call_tool(
            tool_name,
            arguments or {},
        )

        if result.is_error:
            raise RuntimeError(
                f"MCP tool failed: {tool_name}"
            )

        data = []

        for item in result.content:
            if hasattr(item, "text"):
                try:
                    data.append(json.loads(item.text))
                except json.JSONDecodeError:
                    data.append(item.text)

        return data