# Kronos-Leo-Analyst (Future-Vision MCP)

A production-ready FastAPI-based MCP server that integrates the **Kronos Foundation Model** (candlestick forecasting) with **Agentic Multi-Agent Investment Simulation** logic.

This "Combo Skill" allows Poke's L.E.O. agent to provide "Future-Vision" stock analysis, combining deep-learning time-series forecasts with legendary investor personas.

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   python src/main.py
   ```

3. **Test the Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{"ticker": "NVDA"}'
   ```

## ☁️ Deployment (Render)

1. Push this code to your GitHub repository.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your repository.
4. Select **Docker** as the Runtime.
5. Add an environment variable `PORT=8000`.
6. Once deployed, Render will provide a public URL (e.g., `https://kronos-leo.onrender.com`).

## 🤖 Register with Poke

To use this with L.E.O., ask Poke:
`"Request permissions for mcp:new:KronosAnalyst:https://your-render-url.com/analyze"`

## 🛠 Project Structure
- `src/main.py`: FastAPI & MCP Tool definitions.
- `src/engine.py`: The "Future-Vision" logic fusing Kronos forecasts with agentic signals.
- `src/data_utils.py`: Financial data fetching.
