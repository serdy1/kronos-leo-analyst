import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .engine import FutureVisionEngine

app = FastAPI(title="Kronos Future-Vision MCP")
engine = None

class AnalysisRequest(BaseModel):
    ticker: str
    days_back: int = 300
    forecast_horizon: int = 30

@app.on_event("startup")
async def load_models():
    global engine
    # Initialize the unified engine
    engine = FutureVisionEngine()

@app.get("/health")
def health():
    return {"status": "online", "model": "Kronos-Hybrid-v1"}

@app.post("/analyze")
async def analyze(req: AnalysisRequest):
    """
    Primary MCP Tool: Analyzes a stock using Kronos for future forecasting 
    and AI-Hedge-Fund logic for agentic synthesis.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Model engine initializing")
    
    try:
        report = engine.run_unified_analysis(
            ticker=req.ticker, 
            days_back=req.days_back, 
            horizon=req.forecast_horizon
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use environment variable for port to support cloud deployments like Render
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
