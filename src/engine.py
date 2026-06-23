import pandas as pd
import yfinance as yf
import numpy as np
import asyncio
import os
import httpx
import json

try:
    from investor_agents import INVESTOR_AGENTS
    from rules import STRATEGIC_RULES
except ImportError:
    INVESTOR_AGENTS = {}
    STRATEGIC_RULES = {}

class LightweightHedgeFundEngine:
    def __init__(self):
        # Support both Gemini and OpenAI, prioritize Gemini for free tier
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"

    async def _get_llm_completion(self, system_prompt: str, user_content: str):
        if self.gemini_key:
            url = self.gemini_url
            key = self.gemini_key
            model = "gemini-1.5-flash"
        elif self.openai_key:
            url = self.openai_url
            key = self.openai_key
            model = "gpt-4o-mini"
        else:
            return "Error: No API key configured."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "temperature": 0.7
                    },
                    timeout=45.0 # Increased timeout for slow upstream
                )
                data = response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                return f"API Error: {json.dumps(data)}"
            except Exception as e:
                return f"LLM Connection Error: {str(e)}"

    async def fetch_financials(self, ticker: str):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            # v3.8.0 Low-RAM adjustment: Reduce history to 3 months
            hist = stock.history(period="3mo")
            
            if hist.empty:
                 return {"error": "No price history found."}

            close_prices = hist["Close"]
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            # Avoid divide by zero
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))

            metrics = {
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "pe_ratio": info.get("forwardPE", info.get("trailingPE")),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield", 0),
                "market_cap": info.get("marketCap"),
                "volatility": float(close_prices.pct_change().std() * np.sqrt(252)) if not hist.empty else 0,
                "rsi_14": float(rsi.iloc[-1]) if not rsi.empty else None,
                "debt_to_equity": info.get("debtToEquity"),
                "revenue_growth": info.get("revenueGrowth")
            }
            return metrics
        except Exception as e:
            return {"error": f"Finance API Error: {str(e)}"}

    async def run_multi_agent_analysis(self, ticker: str):
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics:
            return metrics

        context = f"Financial Context for {ticker}:\n{json.dumps(metrics, indent=2)}"
        context += f"\n\nStrategic Rules to Consider:\n{json.dumps(STRATEGIC_RULES, indent=2)}"

        # Respect free tier speed with Flash
        tasks = [self._get_llm_completion(prompt, context) for prompt in INVESTOR_AGENTS.values()]
        results = await asyncio.gather(*tasks)
        
        agent_reports = dict(zip(INVESTOR_AGENTS.keys(), results))

        pm_prompt = "You are the Portfolio Manager. Synthesize the findings from our specialized agents and the data. Provide a final Buy/Hold/Sell recommendation with a confidence score (0-1)."
        final_decision = await self._get_llm_completion(pm_prompt, f"Analyst Submissions:\n{json.dumps(agent_reports, indent=2)}")

        return {
            "ticker": ticker,
            "metrics": metrics,
            "analyst_reports": agent_reports,
            "portfolio_manager_decision": final_decision,
            "engine": "Gemini-1.5-Flash" if self.gemini_key else "GPT-4o-Mini"
        }
