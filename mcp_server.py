from typing import Dict, Any
from starlette.responses import JSONResponse
from fastmcp import FastMCP
import os, inspect, uvicorn
from dotenv import load_dotenv
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("My MCP Server")

# tools.py 모듈의 모든 함수를 MCP 툴로 등록
import tools
for name, fn in inspect.getmembers(tools, inspect.isfunction):
    mcp.tool(fn)

# 헬스체크 엔드포인트
@mcp.custom_route("/", methods=["GET"])
async def root(_req):
    return JSONResponse({"status": "ok"})

# /mcp 경로로 MCP 서버 노출
import os, json
app = mcp.http_app(path="/mcp")

# 비밀번호 환경 변수가 설정된 경우 인증 미들웨어 추가
if PASSWORD := os.getenv("PASSWORD", ""):
    @app.middleware("http")
    async def gate(req, call_next):
        # health check 허용
        if req.url.path == "/" and req.method == "GET" :
            return await call_next(req)
        # 스캐너 우회: tools/list만 무인증 허용
        try:
            if req.url.path == "/mcp" and req.method == "POST" and (await req.json()).get("method") == "tools/list":
                return await call_next(req)
        except Exception:
            pass

        # 인증 체크
        if PASSWORD and req.query_params.get("password") != PASSWORD:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(req)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")