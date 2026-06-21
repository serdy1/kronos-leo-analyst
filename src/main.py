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
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

# Configure logging to see startup details
logging.basicConfig(level=logging.INFO)
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

# Handler functions for Starlette
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# Define the final application structure
# Starlette Mount logic: mounting at "/" can swallow specific sub-paths 
# depending on how the underlying app is built. 
# We explicitly mount the ASGI app provided by FastMCP.
# Note: In most recent MCP SDKs, FastMCP serves its own Starlette app 
# at the root when run as ASGI.

# Get the ASGI application from FastMCP
# We check all possible attributes to avoid AttributeError
mcp_asgi_app = None
for attr in ["as_asgi", "app", "_app", "sse_app"]:
    if hasattr(mcp, attr):
        val = getattr(mcp, attr)
        if callable(val) and attr == "as_asgi":
            mcp_asgi_app = val()
        else:
            mcp_asgi_app = val
        if mcp_asgi_app:
            logger.info(f"Using FastMCP attribute '{attr}' for ASGI app")
            break

if not mcp_asgi_app:
    # Fallback to the object itself if it implements ASGI
    mcp_asgi_app = mcp

app = Starlette(
    debug=True,
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        Mount("/", app=mcp_asgi_app)
    ]
)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    # Render standard port is 10000, default to 8000 for local testing
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    # Run uvicorn with the app object
    uvicorn.run(app, host="0.0.0.0", port=port)
