import os
import json
import logging
import sys

# Ensure 'src' is in the path for reliable imports on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

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
            from src.engine import LightweightHedgeFundEngine
            engine = LightweightHedgeFundEngine()
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"Absolute src import failed: {e}. Trying flat import...")
            try:
                from engine import LightweightHedgeFundEngine
                engine = LightweightHedgeFundEngine()
            except Exception as ex:
                logger.error(f"Critical error loading engine: {ex}")
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
        "version": "3.3.7"
    })

# --- ASGI APP DEFINITION ---
# Handler functions for Starlette
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# Wrap FastMCP using Starlette as suggested to avoid AttributeError
# We use mcp.as_asgi() to get the underlying Starlette/ASGI app for MCP
mcp_asgi_app = mcp.as_asgi()

app = Starlette(
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        Mount("/", app=mcp_asgi_app)
    ]
)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    # uvicorn.run accepts the app object directly
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
