import os
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
# This is the modern, clean way to build MCP servers.
mcp = FastMCP(
    "Kronos Analyst",
    title="Kronos Analyst Gemini",
    version="3.0.0"
)

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
    
    Args:
        ticker: Stock ticker symbol (e.g. TSLA, AAPL, MSFT)
    """
    eng = get_engine()
    try:
        raw_result = await eng.run_multi_agent_analysis(ticker)
        return json.dumps(raw_result, indent=2)
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"

@mcp.tool()
async def health() -> str:
    """Check server health and configuration status."""
    return json.dumps({
        "status": "online",
        "mode": "fastmcp",
        "gemini_key_configured": os.getenv("GEMINI_API_KEY") is not None,
        "version": "3.0.0"
    }, indent=2)

if __name__ == "__main__":
    # FastMCP handles SSE and Proxy headers internally in recent versions.
    # Running with 'sse' transport will expose /sse and /messages.
    mcp.run(transport="sse")
