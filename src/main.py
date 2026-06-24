import os
import json
import logging
import sys

# Ensure 'src' is in the path for reliable imports
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
    Core Squad Analysis (5 Agents + RICO Synthesis). 
    Fast, efficient, and strategic default analysis.
    """
    logger.info(f"Running core analysis for ticker: {ticker}")
    eng = get_engine()
    if not eng: return "Error: Engine not initialized."
    try:
        raw_result = await eng.run_core_analysis(ticker)
        return json.dumps(raw_result, indent=2)
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"

@mcp.tool()
async def council_analysis(ticker: str) -> str:
    """
    Full Strategic Council (19 Legendary Agents). 
    Comprehensive, deep-dive boardroom analysis.
    """
    logger.info(f"Running full council analysis for ticker: {ticker}")
    eng = get_engine()
    if not eng: return "Error: Engine not initialized."
    try:
        raw_result = await eng.run_full_council(ticker)
        return json.dumps(raw_result, indent=2)
    except Exception as e:
        return f"Error in council analysis for {ticker}: {str(e)}"

# Handler functions
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

# --- v4.1.0: THE HYBRID COUNCIL ARCHITECTURE ---
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
        scope["server"] = None

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"x-accel-buffering", b"no"))
                headers.append((b"cache-control", b"no-cache, no-transform"))
                message["headers"] = headers
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
