import os
import json
import logging
import sys

# Ensure 'src' is in the path for reliable imports on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("kronos-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Kronos-Analyst", debug=True)

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        logger.info("Initializing LightweightHedgeFundEngine...")
        try:
            from engine import LightweightHedgeFundEngine
            engine = LightweightHedgeFundEngine()
        except Exception as e:
            logger.error(f"Critical error loading engine: {e}")
            return None
    return engine

@mcp.tool()
async def analyze(ticker: str) -> str:
    """
    Multi-agent hedge fund analysis (Buffett, Burry, Graham, etc.) for a given stock ticker.
    """
    logger.info(f"Running analysis for ticker: {ticker}")
    eng = get_engine()
    if not eng:
        return "Error: Engine not initialized."
    try:
        raw_result = await eng.run_multi_agent_analysis(ticker)
        return json.dumps(raw_result, indent=2)
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {str(e)}")
        return f"Error analyzing {ticker}: {str(e)}"

# Handler functions
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/mcp/sse",
        "message": "Kronos Analyst MCP is live. Connect via /mcp/sse"
    })

# --- v3.6.0: ROOT MOUNT STRATEGY ---
# We mount the official sse_app directly to root (/) to prevent double-nesting (/mcp/mcp/sse).
# This ensures /mcp/sse and /mcp/messages resolve exactly where the Poke client expects them.

mcp_asgi_app = mcp.sse_app()

# Patch internal routes for health and root discovery
mcp_asgi_app.routes.insert(0, Route("/health", health_endpoint))
mcp_asgi_app.routes.insert(0, Route("/", root_endpoint))

# --- v3.6.0 BREACH ORCHESTRATOR ---
async def app_orchestrator(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")
        
        # 1. Immediate Health Check Bypass
        if path == "/health":
            response = JSONResponse({"status": "online"})
            await response(scope, receive, send)
            return

        # 2. Host Sanitization & Proxy Coalescing Fix
        # We strip Connection/TE to prevent HTTP/2 issues and keep Host flexible.
        headers = scope.get("headers", [])
        new_headers = []
        for name, value in headers:
            name_lower = name.lower()
            if name_lower in (b"connection", b"te"):
                continue
            new_headers.append((name, value))
        scope["headers"] = new_headers

    # 3. Response Patching: SSE Buffering Bypass (X-Accel-Buffering)
    async def send_wrapper(message):
        if message["type"] == "http.response.start":
            headers = message.get("headers", [])
            headers.append((b"x-accel-buffering", b"no"))
            headers.append((b"cache-control", b"no-cache, no-transform"))
            message["headers"] = headers
        await send(message)

    await mcp_asgi_app(scope, receive, send_wrapper)

# Export as 'app' for Render
app = app_orchestrator

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    # Enforce HTTP/1.1 (h11) for proxy stability
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        http="h11",
        log_level="debug"
    )
