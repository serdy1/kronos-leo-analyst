import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kronos-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Kronos-Analyst")

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        logger.info("Initializing LightweightHedgeFundEngine...")
        from src.engine import LightweightHedgeFundEngine
        engine = LightweightHedgeFundEngine()
    return engine

@mcp.tool()
async def analyze(ticker: str) -> str:
    """
    Multi-agent hedge fund analysis (Buffett, Burry, Graham, etc.) for a given stock ticker.
    """
    logger.info(f"Running analysis for ticker: {ticker}")
    eng = get_engine()
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
        "version": "3.0.7"
    })

# --- SSE APP INTEGRATION ---
# FastMCP.sse_app can be either a property returning a Starlette app 
# or a method returning one. We wrap it safely.

def get_app():
    try:
        # Try as a property first
        app = mcp.sse_app
        if callable(app) and not isinstance(app, Starlette):
            # It's a method (like get_sse_app)
            logger.info("sse_app is a method, calling it...")
            return app()
        logger.info("sse_app is a property or already an app.")
        return app
    except Exception as e:
        logger.error(f"Error accessing mcp.sse_app: {e}")
        # Fallback: Many versions of FastMCP are themselves ASGI apps
        return mcp

app = get_app()

# Add a basic health check route for Render
@app.route("/health")
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
