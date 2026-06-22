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
from starlette.responses import JSONResponse, Response
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

# --- v3.7.0: THE NUCLEAR HOST BYPASS ---
# FastMCP's internal logic is rejecting the Host header with a 421.
# We will completely strip the Host header from the scope before it reaches FastMCP.
# This forces FastMCP to either use a default or ignore host validation.

mcp_asgi_app = mcp.sse_app()

# Simple wrapper to strip Host header
async def host_stripper_middleware(scope, receive, send):
    if scope["type"] == "http":
        headers = scope.get("headers", [])
        # Remove Host header entirely to bypass validation
        new_headers = [(n, v) for n, v in headers if n.lower() != b"host"]
        scope["headers"] = new_headers
    await mcp_asgi_app(scope, receive, send)

main_app = Starlette(
    debug=True,
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        Mount("/mcp", host_stripper_middleware),
    ]
)

# Wide-open CORS
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

async def app_orchestrator(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")
        if path == "/health":
            await health_endpoint(None)
            response = JSONResponse({"status": "online"})
            await response(scope, receive, send)
            return

    async def send_wrapper(message):
        if message["type"] == "http.response.start":
            headers = message.get("headers", [])
            headers.append((b"x-accel-buffering", b"no"))
            headers.append((b"cache-control", b"no-cache, no-transform"))
            message["headers"] = headers
        await send(message)

    await main_app(scope, receive, send_wrapper)

app = app_orchestrator

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        http="h11",
        log_level="debug"
    )
