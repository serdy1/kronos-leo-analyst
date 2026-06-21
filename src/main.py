import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

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
        try:
            from src.engine import LightweightHedgeFundEngine
            engine = LightweightHedgeFundEngine()
        except Exception:
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

@mcp.tool()
async def health_tool() -> str:
    """Check server health."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp-integrated",
        "version": "3.3.0"
    })

# --- ASGI APP DEFINITION ---
async def health_handler(request):
    return JSONResponse({"status": "online"})

async def root_handler(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# Re-implementing a clean Starlette wrapper to isolate the FastMCP SSE app.
# The previous 500 error was likely due to direct route injection into mcp.sse_app.
# We mount mcp.sse_app to a sub-path or use it as a standalone app if possible.
mcp_sse_app = mcp.sse_app

app = Starlette(
    routes=[
        Route("/health", health_handler),
        Route("/", root_handler),
        Mount("/", app=mcp_sse_app)
    ]
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
