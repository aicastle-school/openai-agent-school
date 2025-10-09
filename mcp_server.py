import os
from typing import Dict, Any
from fastmcp import FastMCP

# MCP 서버 설정
mcp = FastMCP("MCP Server")

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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🔧 MCP Server: http://localhost:{port}/mcp")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
