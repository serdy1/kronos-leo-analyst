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
# debug=True will provide more details in logs if it crashes
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

# FastMCP implements the ASGI interface directly.
# mcp.as_asgi() creates a Starlette app that handles /sse and /messages.
app = mcp.as_asgi()

# Adding explicit health check to the Starlette app created by as_asgi()
@app.route("/health")
async def health(request):
    return JSONResponse({"status": "online", "source": "starlette_manual"})

@app.route("/")
async def root(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
