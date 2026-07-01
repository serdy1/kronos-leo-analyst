"""
Kronos-Analyst MCP Server v5.0
FastMCP entry-point with live market data tools.
"""

import os
import json
import logging
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("kronos-mcp")

load_dotenv()

mcp = FastMCP("Kronos-Analyst", debug=True)

# Lazy-loaded engine
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        logger.info("Initializing LightweightHedgeFundEngine...")
        try:
            from engine import LightweightHedgeFundEngine
            _engine = LightweightHedgeFundEngine()
        except Exception as e:
            logger.error(f"Critical error loading engine: {e}")
            return None
    return _engine


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 – Core Analysis (5 agents + RICO)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def analyze(ticker: str) -> str:
    """
    Core Squad Analysis (5 Agents + RICO Synthesis).
    Fast, efficient, and strategic default analysis.
    Accepts bare BIST symbols (e.g. FROTO, PGSUS) or full Yahoo tickers (FROTO.IS, NFLX).
    """
    logger.info(f"Running core analysis for ticker: {ticker}")
    eng = get_engine()
    if not eng:
        return "Error: Engine not initialized."
    try:
        raw_result = await eng.run_core_analysis(ticker)
        return json.dumps(raw_result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 – Full Council (19 agents)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def council_analysis(ticker: str) -> str:
    """
    Full Strategic Council (19 Legendary Agents).
    Comprehensive, deep-dive boardroom analysis.
    Accepts bare BIST symbols (e.g. FROTO, PGSUS) or full Yahoo tickers.
    """
    logger.info(f"Running full council analysis for ticker: {ticker}")
    eng = get_engine()
    if not eng:
        return "Error: Engine not initialized."
    try:
        raw_result = await eng.run_full_council(ticker)
        return json.dumps(raw_result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error in council analysis for {ticker}: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3 – Live price for a single ticker (no LLM, pure data)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def get_price(ticker: str) -> str:
    """
    Fetch the current live price for any ticker.
    Supports:
      • BIST stocks  → FROTO, PGSUS, ANHYT, THYAO, KCHOL, ASELS …
      • BIST index   → BIST100 or XU100
      • FX           → USDTRY or USDTRY=X
      • Gold (Gram TRY) → ALTIN or GOLD
      • Crypto       → BTC, ETH
      • US stocks    → NFLX, AAPL, TSLA …
    Returns JSON with current_price and key metrics.
    """
    from engine import normalize_ticker, get_live_price, fetch_ohlcv_metrics, get_gram_gold_try

    yahoo_ticker = normalize_ticker(ticker)

    if yahoo_ticker == "__GOLD_TRY__":
        result = get_gram_gold_try()
        result["ticker_requested"] = ticker
        result["asset"] = "Gram Altın (TRY)"
        return json.dumps(result, indent=2, ensure_ascii=False)

    result = fetch_ohlcv_metrics(yahoo_ticker)
    return json.dumps(result, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 4 – BIST dashboard snapshot (multiple symbols at once)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def bist_snapshot() -> str:
    """
    Returns a live dashboard of key Turkish market indicators:
    BIST 100, FROTO, PGSUS, ANHYT, USD/TRY, Gram Gold TRY, BTC/USD.
    All data fetched from Yahoo Finance in real-time.
    """
    from engine import normalize_ticker, get_live_price, get_gram_gold_try, fetch_ohlcv_metrics
    import asyncio

    symbols = {
        "BIST100": "XU100.IS",
        "FROTO":   "FROTO.IS",
        "PGSUS":   "PGSUS.IS",
        "ANHYT":   "ANHYT.IS",
        "THYAO":   "THYAO.IS",
        "KCHOL":   "KCHOL.IS",
        "ASELS":   "ASELS.IS",
        "USD/TRY": "USDTRY=X",
        "BTC/USD": "BTC-USD",
    }

    def fetch_one(name, yticker):
        price = get_live_price(yticker)
        return name, price

    # Run price fetches concurrently in a thread pool
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, fetch_one, name, yticker)
        for name, yticker in symbols.items()
    ]
    results_list = await asyncio.gather(*tasks)
    snapshot = {name: price for name, price in results_list}

    # Gram gold calculated separately (needs two prices)
    gold = get_gram_gold_try()
    if "error" not in gold:
        snapshot["ALTIN_GRAM_TRY"] = gold["gold_gram_try"]
        snapshot["ALTIN_OUNCE_USD"] = gold["gold_oz_usd"]
        snapshot["USD_TRY_FOR_GOLD"] = gold["usd_try"]

    from datetime import datetime, timezone
    snapshot["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    snapshot["note"] = (
        "Prices from Yahoo Finance. BIST data may have ~15 min delay. "
        "Gram Gold TRY = (GC=F ÷ 31.1035) × USDTRY=X"
    )

    return json.dumps(snapshot, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# ASGI plumbing (unchanged from v4.1.0)
# ─────────────────────────────────────────────────────────────────────────────
async def health_endpoint(request):
    return JSONResponse({"status": "online", "version": "5.0"})


mcp_asgi_app = mcp.sse_app()


async def mcp_orchestrator(scope, receive, send):
    if scope["type"] == "http":
        headers = []
        for name, value in scope.get("headers", []):
            name_lower = name.lower()
            if name_lower not in (b"host", b"x-forwarded-host", b"connection", b"te"):
                headers.append((name, value))

        port = os.environ.get("PORT", "7860")
        headers.append((b"host", f"127.0.0.1:{port}".encode()))
        scope["headers"] = headers
        scope["server"]  = None

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                h = message.get("headers", [])
                h.append((b"x-accel-buffering", b"no"))
                h.append((b"cache-control",     b"no-cache, no-transform"))
                message["headers"] = h
            await send(message)

        await mcp_asgi_app(scope, receive, send_wrapper)
    else:
        await mcp_asgi_app(scope, receive, send)


app = Starlette(
    debug=True,
    routes=[
        Route("/health", health_endpoint),
        Mount("/", mcp_orchestrator),
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port, http="h11")
