import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

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
async def health_check() -> str:
    """Check server health."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp-sse",
        "version": "3.0.6"
    })

if __name__ == "__main__":
    import uvicorn
    # FastMCP creates its own Starlette/FastAPI app under the hood when run via SSE.
    # The 'as_asgi()' or 'sse_app' properties were causing mismatches in certain versions.
    # We will use the built-in Starlette app provided by FastMCP.
    
    # According to current FastMCP patterns, the sse_app is the property to use.
    # If the previous attempt with as_asgi() failed, it's likely due to 
    # as_asgi not being a method or property in this specific version.
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    # We'll use the 'mcp' instance directly if it supports the ASGI protocol, 
    # or the 'sse_app' if available. 
    # Most reliable for current FastMCP versions is mcp.sse_app
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=port)
