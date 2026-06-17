import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.engine import FutureVisionEngine

app = FastAPI(title="Kronos Future-Vision MCP")
engine = None

class AnalysisRequest(BaseModel):
    ticker: str
    days_back: int = 300
    forecast_horizon: int = 30

@app.on_event("startup")
async def load_models():
    global engine
    engine = FutureVisionEngine()

@app.get("/health")
def health():
    return {"status": "online", "model": "Kronos-Hybrid-v1"}

# --- MCP SSE IMPLEMENTATION ---

@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    Standard MCP SSE Transport Endpoint.
    Poke expects this to stay open and provide the /messages endpoint URL.
    """
    async def event_generator():
        # 1. Send the 'endpoint' event so Poke knows where to POST tool calls
        # We point it to the same host's /messages path
        endpoint_url = str(request.url_for("messages_endpoint"))
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        
        # 2. Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            yield ": keep-alive\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/messages")
async def messages_endpoint(request: Request):
    """
    Standard MCP Tool Dispatcher.
    Poke POSTs JSON-RPC here; we route 'analyze' to the engine.
    """
    payload = await request.json()
    method = payload.get("method")
    params = payload.get("params", {})
    request_id = payload.get("id")

    # Basic MCP 'list_tools' support
    if method == "list_tools":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [{
                    "name": "analyze",
                    "description": "Analyze a stock using Kronos forecasting and Agentic synthesis.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "days_back": {"type": "integer"},
                            "forecast_horizon": {"type": "integer"}
                        },
                        "required": ["ticker"]
                    }
                }]
            }
        }

    # Handle 'call_tool' for 'analyze'
    if method == "call_tool" and params.get("name") == "analyze":
        args = params.get("arguments", {})
        try:
            report = engine.run_unified_analysis(
                ticker=args.get("ticker"),
                days_back=args.get("days_back", 300),
                horizon=args.get("forecast_horizon", 30)
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(report)}]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(e)}
            }

    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}

# Original REST endpoint preserved for manual testing
@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Model engine initializing")
    return engine.run_unified_analysis(ticker=req.ticker, days_back=req.days_back, horizon=req.forecast_horizon)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
