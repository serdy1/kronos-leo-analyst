import pandas as pd
import yfinance as yf
import numpy as np
import asyncio
import os
import httpx
import json

try:
    from investor_agents import CORE_SQUAD, FULL_COUNCIL
    from rules import STRATEGIC_RULES
except ImportError:
    CORE_SQUAD = {}
    FULL_COUNCIL = {}
    STRATEGIC_RULES = {}

class LightweightHedgeFundEngine:
    def __init__(self):
        # Support both Gemini and OpenAI, prioritize Gemini for free tier
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"

    async def _get_llm_completion(self, system_prompt: str, user_content: str, temperature: float = 0.7):
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
                        "temperature": temperature
                    },
                    timeout=60.0 # Increased for larger council synthesis
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
            # v4.1.0 Low-RAM adjustment
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

    async def run_core_analysis(self, ticker: str):
        """Default behavior for 'analyze' tool: 5 core agents + RICO synthesis."""
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics: return metrics

        context = f"Data for {ticker}: {json.dumps(metrics)}"
        
        # Parallel Concise Perspectives
        tasks = [self._get_llm_completion(f"{p} Provide a 1-sentence perspective.", context) for p in CORE_SQUAD.values()]
        results = await asyncio.gather(*tasks)
        agent_reports = dict(zip(CORE_SQUAD.keys(), results))

        # RICO Synthesis
        rico_prompt = "You are RICO, Chief Investment Strategist. Review the perspectives from Buffett, Graham, Lynch, Munger, and Damodaran. Synthesize them with the raw data into a final strategic decision (Buy/Hold/Sell) and a concise report."
        final_decision = await self._get_llm_completion(rico_prompt, f"Analyst Inputs:\n{json.dumps(agent_reports)}")

        return {
            "ticker": ticker,
            "metrics": metrics,
            "core_squad_perspectives": agent_reports,
            "rico_strategic_verdict": final_decision,
            "mode": "Core Hybrid (v4.1.0)"
        }

    async def run_full_council(self, ticker: str):
        """On-demand behavior for 'council_analysis' tool: All 19 agents."""
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics: return metrics

        context = f"Data for {ticker}: {json.dumps(metrics)}"
        
        # Sequential Batching to avoid rate limits
        agent_names = list(FULL_COUNCIL.keys())
        agent_reports = {}
        
        # Process in batches of 5
        for i in range(0, len(agent_names), 5):
            batch = agent_names[i:i+5]
            tasks = [self._get_llm_completion(FULL_COUNCIL[name], context) for name in batch]
            results = await asyncio.gather(*tasks)
            for name, report in zip(batch, results):
                agent_reports[name] = report

        # Final Council Synthesis
        pm_prompt = "You are the Portfolio Manager. Review the analysis from all 19 legendary investors. Provide a comprehensive board-room summary and a final investment verdict."
        final_decision = await self._get_llm_completion(pm_prompt, f"Council Reports:\n{json.dumps(agent_reports)}")

        return {
            "ticker": ticker,
            "metrics": metrics,
            "council_reports": agent_reports,
            "final_verdict": final_decision,
            "mode": "Full Council Siege (v4.1.0)"
        }
