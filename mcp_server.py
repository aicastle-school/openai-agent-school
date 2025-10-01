import os
import inspect
from fastmcp import FastMCP
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# MCP 서버 설정
mcp = FastMCP("MCP Server")

# tools.py 모듈의 모든 함수를 MCP 툴로 등록
import tools
for name, fn in inspect.getmembers(tools, inspect.isfunction):
    mcp.tool(fn)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🔧 MCP Server: http://localhost:{port}/mcp")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
        log_level="info",
    )
