import os
import inspect
from fastmcp import FastMCP
import sys
sys.path.insert(0, "/etc/secrets")
    
# MCP 서버 설정
mcp = FastMCP("MCP Server")

# functions.py 모듈의 모든 함수를 MCP 툴로 등록
import functions
for name, fn in inspect.getmembers(functions, inspect.isfunction):
    mcp.tool(fn)
    print(f"[INFO] Registered tool: {name}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 MCP Server: http://localhost:{port}/mcp")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
