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
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

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

# Handler functions for Starlette
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# --- ASGI APP SETUP (v3.4.9) ---
# Retrieve and patch the internal FastMCP app
mcp_asgi_app = mcp.sse_app()

# Patch the internal app's middleware to remove any TrustedHostMiddleware
if hasattr(mcp_asgi_app, "user_middleware"):
    logger.info(f"Original internal middleware: {mcp_asgi_app.user_middleware}")
    mcp_asgi_app.user_middleware = [
        m for m in mcp_asgi_app.user_middleware 
        if getattr(m, "cls", None) is not TrustedHostMiddleware
    ]
    # Rebuild stack to apply changes
    mcp_asgi_app.middleware_stack = mcp_asgi_app.build_middleware_stack()
    logger.info("Internal TrustedHostMiddleware removed (if existed)")

# Final Starlette app (Outer wrapper)
app = Starlette(debug=True)

# Add TrustedHostMiddleware with wildcard to the outer app to be safe
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Wide-open CORS for SSE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 1. Define specific routes first
@app.route("/health")
async def health(request):
    return JSONResponse({"status": "online"})

@app.route("/")
async def root(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# 2. Mount patched FastMCP at root
app.mount("/", app=mcp_asgi_app)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*",
        log_level="debug"
    )
