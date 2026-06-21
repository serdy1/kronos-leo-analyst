import os
import json
import logging
import sys

# Ensure 'src' is in the path for reliable imports on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
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

# Handler functions
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# --- ASGI APP SETUP (v3.5.3) ---
# Direct interception of the Host header to bypass internal MCP/Starlette validation.

mcp_asgi_app = mcp.sse_app()

# Patch: Inject discovery routes
mcp_asgi_app.routes.insert(0, Route("/health", health_endpoint))
mcp_asgi_app.routes.insert(0, Route("/", root_endpoint))

# Patch: Wide-open CORS
mcp_asgi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- THE HOST PATCH (v3.5.3) ---
# We wrap the app in a raw ASGI middleware that sanitizes the Host header 
# BEFORE it reaches FastMCP's internal logic. This is the most surgical breach possible.
async def host_sanitizer_middleware(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        headers = []
        # Find the Host header and force it to a safe value or remove it if problematic
        # But usually, providing the correct public host or a wildcard-safe one is better.
        # Here, we'll re-construct headers without a restrictive host if needed.
        new_headers = []
        for name, value in scope.get("headers", []):
            if name.lower() == b"host":
                # Force the host to match what the internal server might expect, 
                # or simply match the Render URL to avoid 421.
                # Since 421 means "Misdirected", we'll try to pass the Render host explicitly.
                render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "kronos-leo-analyst.onrender.com").encode()
                new_headers.append((b"host", render_host))
            else:
                new_headers.append((name, value))
        scope["headers"] = new_headers
    
    await mcp_asgi_app(scope, receive, send)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(
        host_sanitizer_middleware, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
