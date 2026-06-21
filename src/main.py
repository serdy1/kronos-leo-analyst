import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kronos-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
# debug=True provides more details in logs if it crashes
mcp = FastMCP("Kronos-Analyst", debug=True)

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        logger.info("Initializing LightweightHedgeFundEngine...")
        try:
            # Absolute import
            from src.engine import LightweightHedgeFundEngine
            engine = LightweightHedgeFundEngine()
        except Exception as e:
            logger.warning(f"Failed absolute import: {e}. Trying relative...")
            try:
                # Relative import
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

# Define a custom health tool within FastMCP
@mcp.tool()
async def health_tool() -> str:
    """Check server health."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp-integrated",
        "version": "3.3.4"
    })

# Use the sse_app property directly which is the Starlette application
app = mcp.sse_app

# Manual routes are added to sse_app which is already a fully formed Starlette app.
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

# Ensure the server binds to the correct port for Render
if __name__ == "__main__":
    import uvicorn
    # Render provides PORT, default to 10000 which is Render's standard fallback
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    # Run uvicorn - binding to 0.0.0.0 is critical for Render to detect the open port
    uvicorn.run(app, host="0.0.0.0", port=port)
