import os
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
# Setting 'debug=True' can help L.E.O. diagnose connection issues
mcp = FastMCP("Kronos-Analyst")

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        from src.engine import LightweightHedgeFundEngine
        engine = LightweightHedgeFundEngine()
    return engine

@mcp.tool()
async def analyze(ticker: str) -> str:
    """
    Multi-agent hedge fund analysis (Buffett, Burry, Graham, etc.) for a given stock ticker.
    """
    eng = get_engine()
    try:
        raw_result = await eng.run_multi_agent_analysis(ticker)
        return json.dumps(raw_result, indent=2)
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"

@mcp.tool()
async def health() -> str:
    """Check server health."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp-asgi",
        "version": "3.0.4"
    }, indent=2)

# FastMCP implements the ASGI interface directly, so the 'mcp' instance 
# itself is the ASGI application to be used by uvicorn.
app = mcp

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    # Note: When running as 'app = mcp', uvicorn should point to the instance
    uvicorn.run(app, host="0.0.0.0", port=port)
