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

# Handler functions
async def health_endpoint(request):
    return JSONResponse({"status": "online"})

async def root_endpoint(request):
    return JSONResponse({
        "status": "online",
        "mcp_sse_path": "/sse",
        "message": "Kronos Analyst MCP is live. Connect via /sse"
    })

# --- ASGI APP SETUP ---
mcp_asgi_app = mcp.sse_app()

# Patch: Inject discovery routes directly into internal router
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

# --- THE v3.5.6 LOGGING & SANITIZATION ---
# We wrap the app in an orchestrator to diagnose 421 errors and sanitize headers.
async def app_orchestrator(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        path = scope.get("path", "")
        
        # 1. Immediate Health Check Bypass
        if path == "/health":
            response = JSONResponse({"status": "online"})
            await response(scope, receive, send)
            return

        # 2. Extract and Log Incoming Host (Debug only)
        original_host = "Unknown"
        headers = scope.get("headers", [])
        for name, value in headers:
            if name.lower() == b"host":
                original_host = value.decode(errors="ignore")
                break
        
        # 3. Aggressive Sanitization for SSE
        # We replace the host header to match Render's expectations.
        # We also ensure 'server' field in scope is set if possible.
        render_host_str = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "kronos-leo-analyst.onrender.com")
        render_host_bytes = render_host_str.encode()
        
        new_headers = []
        for name, value in headers:
            if name.lower() == b"host":
                new_headers.append((b"host", render_host_bytes))
            else:
                new_headers.append((name, value))
        
        scope["headers"] = new_headers
        
        # Force the scope 'server' to match the host to prevent internal 421s
        # Many ASGI apps check scope['server'] against the Host header.
        if "server" in scope and scope["server"]:
             # scope['server'] is (host, port)
             scope["server"] = (render_host_str, scope["server"][1])

    await mcp_asgi_app(scope, receive, send)

app = app_orchestrator

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    # We use log_level debug to see exactly how uvicorn handles the headers.
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*",
        log_level="debug"
    )
