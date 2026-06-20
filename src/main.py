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
# Version 2.2.6: Final "Green Light" Configuration
#
# Problem: 20s timeouts on Poke.com despite aggressive headers.
#
# Fix:
#   1. Gunicorn + UvicornWorker: Professional process management for SSE.
#   2. Interleaved Padding: Instead of one giant block, we send a comment 
#      after every data chunk to ensure the proxy buffer is always pushed.
#   3. Immediate Flush: Send 'connected' immediately, THEN the padding.
# ---------------------------------------------------------------------------

class SSEAggressiveFlushMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/sse":
            new_request_headers = []
            for k, v in scope.get("headers", []):
                if k.lower() == b"accept-encoding":
                    new_request_headers.append((b"accept-encoding", b"identity"))
                else:
                    new_request_headers.append((k, v))
            scope["headers"] = new_request_headers

            async def wrapped_send(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    forced_headers = [
                        (b"content-type", b"text/event-stream; charset=utf-8"),
                        (b"cache-control", b"no-cache, no-store, no-transform, must-revalidate, max-age=0"),
                        (b"x-accel-buffering", b"no"),
                        (b"connection", b"keep-alive"),
                        (b"content-encoding", b"identity"),
                        (b"pragma", b"no-cache"),
                        (b"x-content-type-options", b"nosniff"),
                    ]
                    header_keys_to_remove = [h[0] for h in forced_headers]
                    headers = [h for h in headers if h[0].lower() not in header_keys_to_remove]
                    headers.extend(forced_headers)
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, wrapped_send)
        else:
            await self.app(scope, receive, send)


app = FastAPI(
    title="Kronos Analyst - Gemini v2",
    description="Lightweight Multi-Agent Hedge Fund Analysis (Gemini API, <50MB RAM)",
    version="2.2.6",
)

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
    scheme = "https" if (os.getenv("RENDER") or request.url.scheme == "https") else request.url.scheme
    messages_url = f"{scheme}://{request.url.netloc}/messages"

    async def event_generator():
        # Step 1: Immediate signal to Poke.com (First byte is crucial)
        yield "data: connected\n\n"
        
        # Step 2: 4KB padding to push the 'connected' message through Nginx
        yield ":" + (" " * 4096) + "\n\n"
        
        # Step 3: Endpoint info
        yield f"event: endpoint\ndata: {messages_url}\n\n"
        
        # Step 4: Another 4KB padding to ensure the endpoint info is flushed
        yield ":" + (" " * 4096) + "\n\n"

        while True:
            try:
                if await request.is_disconnected():
                    break
                # Heartbeat every 2 seconds for maximum stability during connection phase
                yield ": keep-alive\n\n"
                await asyncio.sleep(2)
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
                "serverInfo": {"name": "Kronos Analyst Gemini", "version": "2.2.6"},
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
                "version": "2.2.6",
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
        "version": "2.2.6",
        "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        "openai_key_configured": os.getenv("OPENAI_API_KEY") is not None,
        "uptime": int(time.time() - _start_time)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), http="h11")
