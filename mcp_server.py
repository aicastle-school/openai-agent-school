from typing import Dict, Any
from starlette.responses import JSONResponse
from fastmcp import FastMCP
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("My MCP Server")

@mcp.tool
def get_stock_price(symbol: str) -> Dict[str, Any]:
    """
    주가 조회 (Yahoo Finance 기반)
    Args:
        symbol (str): 종목 코드 (예: 'AAPL' 미국 애플, '005930.KS' 삼성전자)
    Returns:
        Dict[str, Any]: 주가 정보
    """
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        info = ticker.fast_info

        price = getattr(info, "last_price", None)
        currency = getattr(info, "currency", None)

        if price is None:
            hist = ticker.history(period="1d")
            if hist.empty:
                return {"ok": False, "symbol": symbol, "error": "거래 데이터 없음"}
            price = float(hist["Close"].iloc[-1])

        return {
            "ok": True,
            "symbol": symbol,
            "price": price,
            "currency": currency
        }
    except Exception as e:
        return {"ok": False, "symbol": symbol, "error": str(e)}

## app path
app = mcp.http_app(path="/")

## PASSWORD
PASSWORD = os.getenv("PASSWORD", "")

@app.middleware("http")
async def gate(req, call_next):
    if PASSWORD and req.query_params.get("password") != PASSWORD:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return await call_next(req)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8081)))