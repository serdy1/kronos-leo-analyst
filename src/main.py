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
from starlette.applications import Starlette

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

# --- ASGI APP SETUP (v3.5.2) ---
# We use the built-in app but WE MANUALLY REMOVE any hidden TrustedHostMiddleware
# that might be causing the 421 error inside the FastMCP-generated app.

mcp_asgi_app = mcp.sse_app()

# Patch: Recursively check and remove TrustedHostMiddleware from the app's middleware list
try:
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    # Starlette apps store middleware in .user_middleware
    if hasattr(mcp_asgi_app, "user_middleware"):
        original_len = len(mcp_asgi_app.user_middleware)
        mcp_asgi_app.user_middleware = [
            m for m in mcp_asgi_app.user_middleware 
            if getattr(m, "cls", None) is not TrustedHostMiddleware
        ]
        if len(mcp_asgi_app.user_middleware) < original_len:
            logger.info("Successfully removed TrustedHostMiddleware from internal app.")
            # Rebuild the middleware stack to apply changes
            mcp_asgi_app.middleware_stack = mcp_asgi_app.build_middleware_stack()
except Exception as e:
    logger.error(f"Failed to patch internal middleware: {e}")

# Inject Poke discovery routes
mcp_asgi_app.routes.insert(0, Route("/health", health_endpoint))
mcp_asgi_app.routes.insert(0, Route("/", root_endpoint))

# Wide-open CORS
mcp_asgi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Render entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    # We must ensure uvicorn doesn't do its own host validation
    # proxy_headers=True is essential for Render
    uvicorn.run(
        mcp_asgi_app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*",
        log_level="debug"
    )
