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
from starlette.routing import Route, Mount
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette

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
        "mcp_sse_path": "/mcp/sse",
        "message": "Kronos Analyst MCP is live. Connect via /mcp/sse"
    })

# --- v3.5.9: THE WILD-CARD HOST STRATEGY ---
# If Render/Cloudflare gives 421, it's because it dislikes the Host header mismatch.
# We will STOP explicitly overwriting the Host header with a fixed string, 
# and instead pass through whatever host Render's proxy is providing internally, 
# OR use a more permissive matching.

mcp_app = mcp.sse_app()

main_app = Starlette(
    debug=True,
    routes=[
        Route("/health", health_endpoint),
        Route("/", root_endpoint),
        Mount("/mcp", mcp_app),
    ]
)

# Wide-open CORS - vital for cross-origin SSE
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

async def app_orchestrator(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")
        
        # 1. Health check bypass
        if path == "/health":
            response = JSONResponse({"status": "online"})
            await response(scope, receive, send)
            return

        # 2. Permissive Host Handling
        # Instead of forcing a host, we let the incoming host pass, 
        # but we ENSURE it doesn't trigger internal Starlette 421s.
        # We also strip Connection/TE to prevent HTTP/2 coalescing issues.
        headers = scope.get("headers", [])
        new_headers = []
        for name, value in headers:
            name_lower = name.lower()
            if name_lower in (b"connection", b"te"):
                continue
            new_headers.append((name, value))
        scope["headers"] = new_headers

    # 3. Response Patching for SSE buffering bypass
    async def send_wrapper(message):
        if message["type"] == "http.response.start":
            headers = message.get("headers", [])
            headers.append((b"x-accel-buffering", b"no"))
            headers.append((b"cache-control", b"no-cache, no-transform"))
            message["headers"] = headers
        await send(message)

    await main_app(scope, receive, send_wrapper)

app = app_orchestrator

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    # We remove 'proxy_headers=True' to see if uvicorn's internal trust logic is tripping.
    # We stick to h11 (HTTP/1.1) for SSE stability.
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        http="h11",
        log_level="debug"
    )
