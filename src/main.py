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
# Version 2.2.5: Maximum Aggression SSE (The "Green Light" Fix)
#
# Problem: Despite 8KB padding and identity encoding, Poke.com still hits a 
# 20s timeout. This usually means the proxy (Cloudflare/Render) is stripping 
# our 'X-Accel-Buffering: no' header or ignoring it due to HTTP/2 multiplexing.
#
# Fix:
#   1. Pure ASGI Middleware: We intercept the 'http.response.start' message 
#      directly to ensure headers are NOT stripped or modified by other 
#      middleware.
#   2. Header Enforcement: We manually inject 'X-Accel-Buffering', 
#      'Cache-Control', and 'Content-Encoding' at the lowest possible level.
#   3. 16KB Padding: Doubling the padding to 16KB to be absolutely sure we 
#      hit the "flush" threshold of even the most stubborn proxies.
# ---------------------------------------------------------------------------

class SSEAggressiveFlushMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/sse":
            # 1. Modify request headers to prevent compression
            new_request_headers = []
            for k, v in scope.get("headers", []):
                if k.lower() == b"accept-encoding":
                    new_request_headers.append((b"accept-encoding", b"identity"))
                else:
                    new_request_headers.append((k, v))
            scope["headers"] = new_request_headers

            # 2. Wrap the 'send' function to inject headers into the response
            async def wrapped_send(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    
                    # Force essential SSE headers at the ASGI level
                    forced_headers = [
                        (b"content-type", b"text/event-stream; charset=utf-8"),
                        (b"cache-control", b"no-cache, no-store, no-transform, must-revalidate, max-age=0"),
                        (b"x-accel-buffering", b"no"),
                        (b"connection", b"keep-alive"),
                        (b"content-encoding", b"identity"),
                        (b"pragma", b"no-cache"),
                        (b"x-content-type-options", b"nosniff"),
                    ]
                    
                    # Remove existing versions of these headers
                    header_keys_to_remove = [h[0] for h in forced_headers]
                    headers = [h for h in headers if h[0].lower() not in header_keys_to_remove]
                    
                    # Add our forced headers
                    headers.extend(forced_headers)
                    message["headers"] = headers
                
                await send(message)

            await self.app(scope, receive, wrapped_send)
        else:
            await self.app(scope, receive, send)


app = FastAPI(
    title="Kronos Analyst - Gemini v2",
    description="Lightweight Multi-Agent Hedge Fund Analysis (Gemini API, <50MB RAM)",
    version="2.2.5",
)

# Aggressive middleware must be first
app.add_middleware(SSEAggressiveFlushMiddleware)

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
    Version 2.2.5: 16KB padding + ASGI-level header enforcement.
    """
    scheme = "https" if (os.getenv("RENDER") or request.url.scheme == "https") else request.url.scheme
    messages_url = f"{scheme}://{request.url.netloc}/messages"

    async def event_generator():
        # 16KB padding to overflow any proxy buffer (Nginx/Render/Cloudflare).
        # We use a comment format (:) so it's ignored by the client but forces a flush.
        yield ":" + (" " * 16384) + "\n\n"
        
        # Immediate signal to Poke.com that we are alive
        yield "data: connected\n\n"
        yield f"event: endpoint\ndata: {messages_url}\n\n"

        while True:
            try:
                if await request.is_disconnected():
                    break
                # Aggressive keep-alive (every 5 seconds instead of 15)
                # This keeps the connection "hot" in the eyes of the proxy.
                yield ": keep-alive\n\n"
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
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
                "serverInfo": {"name": "Kronos Analyst Gemini", "version": "2.2.5"},
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
                "version": "2.2.5",
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
        "version": "2.2.5",
        "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        "openai_key_configured": os.getenv("OPENAI_API_KEY") is not None,
        "uptime": int(time.time() - _start_time)
    }

if __name__ == "__main__":
    import uvicorn
    # Using h11 to ensure we don't have httptools buffering issues
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), http="h11")
