import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["knowledge_mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listing = await session.list_tools()
            print("list_tools 返回类型：", type(listing))
            print("list_tools 原始内容：", listing)

            if hasattr(listing, "tools"):
                print("工具名：", [tool.name for tool in listing.tools])
            else:
                print("工具列表：", listing)


asyncio.run(main())