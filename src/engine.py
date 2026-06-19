import pandas as pd
import yfinance as yf
import numpy as np
import asyncio
import os
import httpx
import json

class LightweightHedgeFundEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_url = "https://api.openai.com/v1/chat/completions"

    async def _get_llm_completion(self, system_prompt: str, user_content: str):
        if not self.api_key:
            return "Error: OPENAI_API_KEY not set."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.openai_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "temperature": 0.5
                    },
                    timeout=20.0
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"LLM Error: {str(e)}"

    async def fetch_financials(self, ticker: str):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            # Simplified metrics for persona analysis
            metrics = {
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "pe_ratio": info.get("forwardPE", info.get("trailingPE")),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield", 0),
                "market_cap": info.get("marketCap"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volatility": float(hist["Close"].pct_change().std() * np.sqrt(252)) if not hist.empty else 0
            }
            return metrics
        except Exception as e:
            return {"error": str(e)}

    async def run_multi_agent_analysis(self, ticker: str):
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics:
            return metrics

        context = f"Data for {ticker}: {json.dumps(metrics, indent=2)}"

        personas = {
            "Warren Buffett": "You are Warren Buffett. Focus on 'moat', long-term value, and cash flow. Is this a wonderful business at a fair price?",
            "Peter Lynch": "You are Peter Lynch. Look for 'ten-baggers' and growth at a reasonable price (GARP). Focus on PEG ratio and simple business models.",
            "Benjamin Graham": "You are Benjamin Graham, the father of value investing. Focus on 'margin of safety', book value, and avoiding overvalued growth. Be extremely defensive.",
        }

        # Run analysts in parallel
        tasks = [self._get_llm_completion(prompt, context) for prompt in personas.values()]
        results = await asyncio.gather(*tasks)
        
        agent_reports = dict(zip(personas.keys(), results))

        # Synthesis: Portfolio Manager
        synthesis_prompt = "You are a Portfolio Manager. Synthesize the reports from Buffett, Lynch, and Graham into one final Buy/Hold/Sell decision with a confidence score (0-1)."
        synthesis_user = f"Reports:\n{json.dumps(agent_reports, indent=2)}\n\nOriginal Data: {context}"
        
        final_decision = await self._get_llm_completion(synthesis_prompt, synthesis_user)

        return {
            "ticker": ticker,
            "metrics": metrics,
            "analyst_reports": agent_reports,
            "final_recommendation": final_decision
        }
