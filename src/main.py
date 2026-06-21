import os
import json
import logging
import sys

# Ensure reliable imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("kronos-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
# Setting 'sse=True' explicitly in some versions might help, 
# but FastMCP usually detects it.
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

# Define a custom health tool
@mcp.tool()
async def health_tool() -> str:
    """Check server health."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp-manual-starlette",
        "version": "3.4.0"
    })

# --- ASGI APP DEFINITION ---
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# The 500 error on /sse is likely because Mount("/") was swallowing or 
# incorrectly delegating the sub-paths to mcp.app.
# FastMCP usually serves SSE on /sse and messages on /messages by default.
# We mount mcp.app explicitly and ensure the discovery routes are prioritized.

# In FastMCP, the starlette app is 'mcp.app'.
mcp_asgi = mcp.app

app = Starlette(
    debug=True,
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        # Mount the MCP app at the root so it can handle its own /sse and /messages paths
        Mount("/", app=mcp_asgi)
    ]
)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
