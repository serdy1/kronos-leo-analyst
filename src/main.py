import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse

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
        # Note: Absolute import from the 'src' package
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
        "version": "3.0.9"
    })

# --- ASGI APP DEFINITION ---
# FastMCP provides an SSE Starlette app. In the latest versions, 
# 'sse_app' is a property that returns the Starlette app instance.
# However, to be absolutely safe and handle both property/method cases:
def _resolve_app():
    target = mcp.sse_app
    if callable(target) and not hasattr(target, "dispatch"):
        # It's a method (get_sse_app style), call it to get the app
        return target()
    return target

app = _resolve_app()

# Add a basic health check route for Render
@app.route("/health")
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

if __name__ == "__main__":
    import uvicorn
    # Use the port Render expects
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    # Pass the app instance directly
    uvicorn.run(app, host="0.0.0.0", port=port)
