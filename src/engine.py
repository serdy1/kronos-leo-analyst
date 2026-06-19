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

    async def _get_llm_completion(self, system_prompt: str, user_content: str, model="gpt-4o-mini"):
        if not self.api_key:
            return "Error: OPENAI_API_KEY not set."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.openai_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "temperature": 0.5
                    },
                    timeout=30.0
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
            
            # Extract technical indicators
            close_prices = hist["Close"]
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            metrics = {
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "pe_ratio": info.get("forwardPE", info.get("trailingPE")),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "dividend_yield": info.get("dividendYield", 0),
                "market_cap": info.get("marketCap"),
                "revenue_growth": info.get("revenueGrowth"),
                "ebitda_margins": info.get("ebitdaMargins"),
                "debt_to_equity": info.get("debtToEquity"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volatility": float(close_prices.pct_change().std() * np.sqrt(252)) if not hist.empty else 0,
                "rsi_14": float(rsi.iloc[-1]) if not rsi.empty else None,
                "beta": info.get("beta")
            }
            return metrics
        except Exception as e:
            return {"error": str(e)}

    async def run_multi_agent_analysis(self, ticker: str):
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics:
            return metrics

        context = f"Data for {ticker}: {json.dumps(metrics, indent=2)}"

        # 1. Specialist Agents (Data Analyzers)
        specialist_personas = {
            "Valuation Agent": "Calculate the intrinsic value of the stock using DCF or comparable multiples based on the provided data.",
            "Sentiment Agent": "Analyze general market sentiment and news positioning for this ticker. (Simulate based on price action and volatility).",
            "Fundamentals Agent": "Review the balance sheet and P&L metrics. Focus on debt-to-equity and margin health.",
            "Technicals Agent": "Analyze RSI, moving averages, and volatility. Identify if the stock is overbought or oversold."
        }

        # 2. Investor Personas (The Council)
        investor_personas = {
            "Aswath Damodaran": "The Dean of Valuation. Focus on the 'story' behind the numbers and disciplined valuation math.",
            "Ben Graham": "The Godfather of Value. Seek a significant margin of safety and low P/B ratios.",
            "Bill Ackman": "Activist Investor. Look for bold turnaround opportunities or hidden asset value to unlock.",
            "Cathie Wood": "Disruptive Growth. Focus on innovation, high growth rates, and long-term tech potential.",
            "Charlie Munger": "Look for wonderful businesses at fair prices. Focus on multi-disciplinary 'Lollapalooza' effects.",
            "Michael Burry": "Contrarian. Look for deep value or technical extremes that suggest a 'Big Short' or massive reversal.",
            "Mohnish Pabrai": "Dhandho Investor. Low risk, high uncertainty. Look for situations where 'heads I win, tails I don't lose much'.",
            "Nassim Taleb": "Black Swan Analyst. Focus on tail risk, antifragility, and asymmetric payoffs. Avoid 'fragile' debt-heavy companies.",
            "Peter Lynch": "Seek 'ten-baggers'. Focus on everyday businesses with understandable growth and low PEG ratios.",
            "Phil Fisher": "Growth via Scuttlebutt. Focus on management quality and the 'scuttlebutt' of long-term competitive advantage.",
            "Rakesh Jhunjhunwala": "The Big Bull. Look for structural growth stories in emerging market leaders.",
            "Stanley Druckenmiller": "Macro Trend Seeker. Focus on asymmetric opportunities and macro-economic positioning.",
            "Warren Buffett": "Moat and Long-term Value. Is there a durable competitive advantage and high ROE?"
        }

        # Run Analysis Phase
        specialist_tasks = [self._get_llm_completion(p, context) for p in specialist_personas.values()]
        investor_tasks = [self._get_llm_completion(p, context) for p in investor_personas.values()]
        
        all_reports = await asyncio.gather(*specialist_tasks, *investor_tasks)
        
        reports_map = dict(zip(list(specialist_personas.keys()) + list(investor_personas.keys()), all_reports))

        # 3. Risk Manager
        risk_prompt = "You are the Risk Manager. Review the reports and market data. Calculate risk metrics and identify if the position size should be limited based on volatility and debt."
        risk_report = await self._get_llm_completion(risk_prompt, f"Reports: {json.dumps(reports_map)}\nData: {context}")

        # 4. Portfolio Manager (Final Synthesis)
        pm_prompt = "You are the Portfolio Manager. Synthesize the findings from all 18 specialists and investors (Buffett, Graham, etc.) and the Risk Manager. Provide a final Buy/Hold/Sell recommendation with a confidence score (0-1) and position sizing advice."
        pm_synthesis = await self._get_llm_completion(pm_prompt, f"All Analyst Reports: {json.dumps(reports_map)}\nRisk Report: {risk_report}", model="gpt-4o")

        return {
            "ticker": ticker,
            "metrics": metrics,
            "specialist_analysis": {k: reports_map[k] for k in specialist_personas.keys()},
            "investor_signals": {k: reports_map[k] for k in investor_personas.keys()},
            "risk_assessment": risk_report,
            "final_portfolio_decision": pm_synthesis
        }
