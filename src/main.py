import os
import json
import logging
import sys

# Ensure 'src' is in the path for reliable imports on Render
# The files are likely located in /workspace/user/src/ on Render if 'src' is a package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
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
            # Try to import from the src package directly
            from src.engine import LightweightHedgeFundEngine
            engine = LightweightHedgeFundEngine()
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"Absolute src import failed: {e}. Trying flat import...")
            try:
                # Try to import assuming src is in path or flat structure
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
        "version": "3.3.6"
    })

# Use the sse_app property directly which is the Starlette application
app = mcp.sse_app

# Manual routes for Poke validation
@app.route("/health")
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

@app.route("/")
async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# The uvicorn entry point is used by Render if the start command is 'python src/main.py'
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run("src.main:app" if os.path.exists(os.path.join(BASE_DIR, "src/main.py")) else "main:app", host="0.0.0.0", port=port, log_level="debug", factory=False)
