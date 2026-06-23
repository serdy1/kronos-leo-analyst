import os
import time
import json
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

engine = None
_start_time = time.time()


def get_engine():
    global engine
    if engine is None:
        from .engine import KronosLeoEngine
        engine = KronosLeoEngine()
    return engine


app = FastAPI(
    title="Kronos LEO Analyst - Combo Skill",
    description="Unified API combining Kronos Foundation Model forecasting with AI Hedge Fund multi-agent analysis",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    ticker: str
    days_back: int = 365
    forecast_horizon: int = 30


class HedgeFundRequest(BaseModel):
    tickers: list[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    selected_analysts: Optional[list[str]] = None


# ============================================================
# MCP (Model Context Protocol) SSE Transport
# ============================================================

@app.get("/sse")
async def sse_endpoint(request: Request):
    """MCP SSE transport endpoint."""
    scheme = "https" if (os.getenv("RENDER") or request.url.scheme == "https") else request.url.scheme
    messages_url = f"{scheme}://{request.url.netloc}/messages"

    async def event_generator():
        # 1. Immediate heartbeat - wakes up Render/Cloudflare proxy buffer
        yield ": connected\n\n"

        # 2. Small delay to let proxy flush the first bytes
        await asyncio.sleep(0.05)

        # 3. Send the endpoint event (tells client where to POST requests)
        yield f"event: endpoint\ndata: {messages_url}\n\n"

        # 4. Keep connection alive with periodic heartbeats
        while True:
            try:
                if await request.is_disconnected():
                    break
                yield ": keep-alive\n\n"
                await asyncio.sleep(15)
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.post("/messages")
async def messages_endpoint(request: Request):
    """MCP messages endpoint - receives JSON-RPC requests from the client."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    method = body.get("method", "")
    req_id = body.get("id")

    # Notifications (no id) - silently accept
    if req_id is None:
        return JSONResponse(content={}, status_code=202)

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "Kronos LEO Analyst",
                    "version": "2.0.0",
                },
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "analyze",
                        "description": "Full combo analysis (Kronos forecast + AI Hedge Fund agent signals) for a stock ticker",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. NVDA, AAPL)"},
                                "days_back": {"type": "integer", "description": "Historical data window in days", "default": 365},
                                "forecast_horizon": {"type": "integer", "description": "Forecast horizon in days", "default": 30},
                            },
                            "required": ["ticker"],
                        },
                    },
                    {
                        "name": "kronos_forecast",
                        "description": "Run Kronos foundation model forecast only (no agent signals)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                                "days_back": {"type": "integer", "description": "Historical data window in days", "default": 365},
                                "forecast_horizon": {"type": "integer", "description": "Forecast horizon in days", "default": 30},
                            },
                            "required": ["ticker"],
                        },
                    },
                    {
                        "name": "health",
                        "description": "Check server health and model status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                    {
                        "name": "list_investors",
                        "description": "List all three available investor agents (Benjamin Graham, Peter Lynch, Warren Buffett) and their strategies",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                    {
                        "name": "ask_investor",
                        "description": "Ask a specific investor agent a question about their strategies, rules, checklists, or formulas",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "investor": {"type": "string", "description": "Name of the investor (graham, lynch, buffett)"},
                                "question": {"type": "string", "description": "The question to ask, or keywords like 'checklist', 'formulas', 'strategy'"}
                            },
                            "required": ["investor", "question"],
                        },
                    },
                    {
                        "name": "analyze_investor",
                        "description": "Run a deep fundamental stock analysis by a specific investor agent (Graham, Lynch, Buffett) using yfinance",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "investor": {"type": "string", "description": "Name of the investor (graham, lynch, buffett)"},
                                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. AAPL, MSFT)"}
                            },
                            "required": ["investor", "ticker"],
                        },
                    },
                ],
            },
        }

    if method == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        arguments = body.get("params", {}).get("arguments", {})

        eng = get_engine()
        try:
            if tool_name == "health":
                result = {
                    "status": "online",
                    "version": "2.0.0",
                    "kronos_loaded": eng.kronos_available,
                }
            elif tool_name == "analyze":
                result = eng.run_unified_analysis(
                    ticker=arguments.get("ticker", ""),
                    days_back=arguments.get("days_back", 365),
                    horizon=arguments.get("forecast_horizon", 30),
                )
            elif tool_name == "kronos_forecast":
                df = eng._fetch_data(arguments.get("ticker", ""), arguments.get("days_back", 365))
                if df is None:
                    result = {"error": "No data found"}
                else:
                    forecast = eng._kronos_forecast(df, arguments.get("forecast_horizon", 30))
                    if forecast is None:
                        forecast = eng._simulate_forecast(df, arguments.get("forecast_horizon", 30))
                    result = {"forecast": forecast.to_dict()}
            elif tool_name == "list_investors":
                from src.investor_agents import InvestorAgentFactory
                result = {"investors": InvestorAgentFactory.list_agents()}
            elif tool_name == "ask_investor":
                from src.investor_agents import InvestorAgentFactory
                investor = arguments.get("investor", "")
                question = arguments.get("question", "")
                agent = InvestorAgentFactory.get_agent(investor)
                result = {"investor": investor, "question": question, "answer": agent.ask(question)}
            elif tool_name == "analyze_investor":
                from src.investor_agents import InvestorAgentFactory
                investor = arguments.get("investor", "")
                ticker = arguments.get("ticker", "")
                fundamentals = eng._fetch_rich_fundamentals(ticker)
                agent = InvestorAgentFactory.get_agent(investor)
                result = agent.analyze_stock(ticker, fundamentals)
            else:
                return JSONResponse(
                    status_code=400,
                    content={"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}},
                )

            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

    return JSONResponse(
        status_code=400,
        content={"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}},
    )


# ============================================================
# REST Endpoints (backwards compatible)
# ============================================================

@app.get("/health")
def health():
    eng = get_engine()
    return {
        "status": "online",
        "version": "2.0.0",
        "uptime_seconds": int(time.time() - _start_time),
        "kronos_loaded": eng.kronos_available if eng else False,
        "engine_ready": eng is not None,
    }


@app.get("/ping")
def ping():
    return {"ok": True, "uptime": int(time.time() - _start_time)}


@app.get("/agents")
def list_agents():
    try:
        from src.hedge_fund.utils.analysts import get_agents_list
        return {"agents": get_agents_list()}
    except Exception as e:
        return {"agents": [], "error": str(e)}


@app.get("/investors")
def list_investor_agents():
    from src.investor_agents import InvestorAgentFactory
    return {"investors": InvestorAgentFactory.list_agents()}


@app.post("/investor/{investor_name}/ask")
async def ask_investor(investor_name: str, request: Request):
    from src.investor_agents import InvestorAgentFactory
    try:
        body = await request.json()
        question = body.get("question", "")
        agent = InvestorAgentFactory.get_agent(investor_name)
        return {"investor": investor_name, "question": question, "answer": agent.ask(question)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/investor/{investor_name}/analyze")
async def analyze_by_investor(investor_name: str, req: AnalysisRequest):
    from src.investor_agents import InvestorAgentFactory
    from .engine import KronosLeoEngine
    eng = KronosLeoEngine()
    try:
        fundamentals = eng._fetch_rich_fundamentals(req.ticker)
        # Ensure we have current price
        if not fundamentals.get("current_price"):
            df = eng._fetch_data(req.ticker, req.days_back)
            if df is not None and not df.empty:
                fundamentals["current_price"] = float(df["close"].iloc[-1])
            else:
                raise HTTPException(status_code=400, detail=f"No data for {req.ticker}")
        
        agent = InvestorAgentFactory.get_agent(investor_name)
        return agent.analyze_stock(req.ticker, fundamentals)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
def list_models():
    try:
        from src.hedge_fund.llm.models import get_models_list
        return {"models": get_models_list()}
    except Exception as e:
        return {"models": [], "error": str(e)}


@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    eng = get_engine()
    try:
        report = eng.run_unified_analysis(
            ticker=req.ticker,
            days_back=req.days_back,
            horizon=req.forecast_horizon,
        )
        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hedge-fund")
async def hedge_fund(req: HedgeFundRequest):
    eng = get_engine()
    try:
        from datetime import datetime
        now = datetime.now()
        start = req.start_date or now.strftime("%Y-%m-%d")
        end = req.end_date or now.strftime("%Y-%m-%d")

        result = eng.run_hedge_fund(
            tickers=req.tickers,
            start_date=start,
            end_date=end,
            selected_analysts=req.selected_analysts,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kronos-forecast")
async def kronos_forecast(req: AnalysisRequest):
    eng = get_engine()
    try:
        df = eng._fetch_data(req.ticker, req.days_back)
        if df is None:
            raise HTTPException(status_code=400, detail=f"No data for {req.ticker}")

        forecast = eng._kronos_forecast(df, req.forecast_horizon)
        if forecast is None:
            forecast = eng._simulate_forecast(df, req.forecast_horizon)

        return {
            "ticker": req.ticker,
            "model_loaded": eng.kronos_available,
            "historical_prices": df["close"].tail(10).to_dict(),
            "forecast": forecast.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
