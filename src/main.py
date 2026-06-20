import os
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Kronos-Analyst")

# Lazy-loaded engine
engine = None

def get_engine():
    global engine
    if engine is None:
        from .engine import LightweightHedgeFundEngine
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
        "mode": "fastmcp-sse-app",
        "version": "3.0.3"
    }, indent=2)

# FastMCP provides sse_app as a property that returns a Starlette application
app = mcp.sse_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
