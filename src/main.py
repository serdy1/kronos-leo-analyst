import os
import json
import logging
import sys

# Add the current directory to sys.path
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
mcp = FastMCP("Kronos-Analyst", debug=True)

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        logger.info("Initializing LightweightHedgeFundEngine...")
        try:
            # We are in 'src' directory, engine.py is also in 'src'
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
        "mode": "fastmcp-integrated",
        "version": "3.3.9"
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

# FastMCP doesn't have as_asgi() or sse_app in some versions.
# Standard way to get the Starlette app is via the .app property.
# We wrap it to provide /health and / routes for Poke.
# In FastMCP, the underlying Starlette app is often at 'mcp.app'.
# If 'mcp.app' doesn't exist, we'll see it in the logs.

mcp_app = mcp.app

app = Starlette(
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        Mount("/", app=mcp_app)
    ]
)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
