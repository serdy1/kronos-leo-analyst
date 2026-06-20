import time
import json
import asyncio
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Initialize the engine lazily
engine = None
_start_time = time.time()

def get_engine():
    global engine
    if engine is None:
        from .engine import LightweightHedgeFundEngine
        engine = LightweightHedgeFundEngine()
    return engine

# ---------------------------------------------------------------------------
# Version 2.2.4: Aggressive Proxy Buffer Flush
#
# Problem: Proxies like Nginx (Render's edge) and Cloudflare often have 
# buffer sizes of 4KB or 8KB. Our previous 1KB padding was insufficient to 
# force an immediate flush, causing the stream to hang and timeout.
#
# Fix:
#   1. Increase initial SSE padding to 8KB (8192 bytes). This "brute-force"
#      overflows most proxy buffers immediately upon connection.
#   2. Maintain the ASGI scope manipulation to kill Brotli/GZip compression.
#   3. Reinforce all anti-buffering headers.
# ---------------------------------------------------------------------------

class SSECompressionBypassMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/sse":
            new_headers = []
            for k, v in scope.get("headers", []):
                if k.lower() == b"accept-encoding":
                    # Force identity (no compression) to prevent proxy buffering
                    new_headers.append((b"accept-encoding", b"identity"))
                else:
                    new_headers.append((k, v))
            scope["headers"] = new_headers
        await self.app(scope, receive, send)


app = FastAPI(
    title="Kronos Analyst - Gemini v2",
    description="Lightweight Multi-Agent Hedge Fund Analysis (Gemini API, <50MB RAM)",
    version="2.2.4",
)

# Register pure ASGI middleware
app.add_middleware(SSECompressionBypassMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str

@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    MCP SSE transport endpoint.

    Version 2.2.4:
    - Increased padding to 8KB to force Nginx/Cloudflare buffer flush.
    """
    scheme = "https" if (os.getenv("RENDER") or request.url.scheme == "https") else request.url.scheme
    messages_url = f"{scheme}://{request.url.netloc}/messages"

    async def event_generator():
        # Send an immediate 8 KB padding comment to force the TCP window open
        # and overflow any proxy buffer (Nginx/Render/Cloudflare).
        yield ":" + (" " * 8192) + "\n\n"
        yield "data: connected\n\n"
        yield f"event: endpoint\ndata: {messages_url}\n\n"

        while True:
            try:
                if await request.is_disconnected():
                    break
                # SSE keep-alive comment
                yield ": keep-alive\n\n"
                await asyncio.sleep(15)
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache, no-store, no-transform, must-revalidate, max-age=0",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Content-Encoding": "identity",
            "Pragma": "no-cache"
        },
    )

@app.post("/messages")
async def messages_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    method = body.get("method", "")
    req_id = body.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Kronos Analyst Gemini", "version": "2.2.4"},
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
                        "description": "Multi-agent hedge fund analysis (Buffett, Burry, Graham, etc.) using Gemini Flash",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. TSLA)"},
                            },
                            "required": ["ticker"],
                        },
                    },
                    {
                        "name": "health",
                        "description": "Check server health",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ],
            },
        }

    if method == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        args = body.get("params", {}).get("arguments", {})
        eng = get_engine()

        if tool_name == "health":
            raw_result = {
                "status": "online",
                "mode": "gemini-api-v1",
                "version": "2.2.4",
                "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None
            }
        elif tool_name == "analyze":
            raw_result = await eng.run_multi_agent_analysis(args.get("ticker", ""))
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Unknown tool"}}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(raw_result, indent=2)}]}
        }

    return {"jsonrpc": "2.0", "id": req_id, "result": {}}

@app.get("/health")
def health():
    return {
        "status": "online",
        "mode": "gemini-api-v1",
        "version": "2.2.4",
        "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        "openai_key_configured": os.getenv("OPENAI_API_KEY") is not None,
        "uptime": int(time.time() - _start_time)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
