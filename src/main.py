import time
import json
import asyncio
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
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
# Version 2.2.1: Hard SSE Compression Bypass (ASGI Scope Fix)
#
# Problem: Version 2.2.0 used Starlette's Headers object to rebuild headers,
# which triggered an "AssertionError: Cannot set both headers and scope."
# Starlette is strict about not mixing high-level Headers objects with raw
# ASGI scopes.
#
# Fix:
#   1. Directly manipulate the raw ASGI scope["headers"] list (byte tuples).
#   2. Delete the cached _headers property in the Request object to force
#      Starlette to re-parse our modified scope.
#   3. Keep the aggressive anti-buffering headers in the response.
# ---------------------------------------------------------------------------

class SSECompressionBypassMiddleware(BaseHTTPMiddleware):
    """
    Intercepts every request whose path starts with /sse and removes the
    Accept-Encoding header by directly manipulating the ASGI scope.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/sse"):
            # Deep-dive into ASGI scope to strip compression negotiation
            new_headers = []
            for k, v in request.scope["headers"]:
                if k.lower() == b"accept-encoding":
                    # Force identity (no compression)
                    new_headers.append((b"accept-encoding", b"identity"))
                else:
                    new_headers.append((k, v))
            
            # Update the scope with patched headers
            request.scope["headers"] = new_headers
            
            # Clear Starlette's internal header cache so it reads the new scope
            if "_headers" in request.__dict__:
                del request.__dict__["_headers"]

        response = await call_next(request)

        if request.url.path.startswith("/sse"):
            # Force all anti-buffering / anti-compression headers on the way out
            response.headers["Content-Type"] = "text/event-stream; charset=utf-8"
            response.headers["Cache-Control"] = "no-cache, no-store, no-transform, must-revalidate, max-age=0"
            response.headers["X-Accel-Buffering"] = "no"
            response.headers["Connection"] = "keep-alive"
            response.headers["Content-Encoding"] = "identity"
            response.headers["Pragma"] = "no-cache"
            # Remove any compression-related headers that upstream may have set
            response.headers.pop("transfer-encoding", None)

        return response


app = FastAPI(
    title="Kronos Analyst - Gemini v2",
    description="Lightweight Multi-Agent Hedge Fund Analysis (Gemini API, <50MB RAM)",
    version="2.2.1",
)

# SSE compression bypass MUST be added before CORSMiddleware so it runs first
# in the middleware stack (Starlette processes middleware in LIFO order).
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

    Version 2.2.1:
    - SSECompressionBypassMiddleware strips Accept-Encoding via raw ASGI scope
      manipulation, bypassing Starlette's strict Headers validation.
    """
    scheme = "https" if (os.getenv("RENDER") or request.url.scheme == "https") else request.url.scheme
    messages_url = f"{scheme}://{request.url.netloc}/messages"

    async def event_generator():
        # Send an immediate 1 KB padding comment to force the TCP window open
        yield ": " + (" " * 1024) + "\n\n"
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
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-store, no-transform, must-revalidate, max-age=0",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Content-Encoding": "identity",
            "Pragma": "no-cache",
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
                "serverInfo": {"name": "Kronos Analyst Gemini", "version": "2.2.1"},
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
                "version": "2.2.1",
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
        "version": "2.2.1",
        "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        "openai_key_configured": os.getenv("OPENAI_API_KEY") is not None,
        "uptime": int(time.time() - _start_time)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
