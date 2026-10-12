import json

from mcp.server.mcpserver import MCPServer

from knowledge_agent import search_knowledge as kb_search

mcp = MCPServer("knowledge-search")


@mcp.tool()
def search_knowledge(query: str) -> str:
    """语义检索客服知识库，返回与问题最相关的政策片段。"""
    result = kb_search(query)
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
    