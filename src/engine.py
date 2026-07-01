"""
Kronos-Analyst Engine v5.0
Live market data layer: Yahoo Finance (yfinance) + correct BIST/FX/Gold symbols
"""

import pandas as pd
import yfinance as yf
import numpy as np
import asyncio
import os
import httpx
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("kronos-mcp.engine")

try:
    from investor_agents import CORE_SQUAD, FULL_COUNCIL
    from rules import STRATEGIC_RULES
except ImportError:
    CORE_SQUAD = {}
    FULL_COUNCIL = {}
    STRATEGIC_RULES = {}

# ──────────────────────────────────────────────────────────────────────────────
# Ticker normalization map
# Handles bare symbols → Yahoo Finance format
# ──────────────────────────────────────────────────────────────────────────────
TICKER_MAP = {
    # BIST stocks (no suffix → add .IS)
    "FROTO":  "FROTO.IS",
    "PGSUS":  "PGSUS.IS",
    "ANHYT":  "ANHYT.IS",
    "THYAO":  "THYAO.IS",
    "KCHOL":  "KCHOL.IS",
    "ASELS":  "ASELS.IS",
    "DOAS":   "DOAS.IS",
    "EREGL":  "EREGL.IS",
    "TUPRS":  "TUPRS.IS",
    "SAHOL":  "SAHOL.IS",
    "AKBNK":  "AKBNK.IS",
    "YKBNK":  "YKBNK.IS",
    "ISCTR":  "ISCTR.IS",
    "GARAN":  "GARAN.IS",
    "BIMAS":  "BIMAS.IS",
    "SISE":   "SISE.IS",
    "TCELL":  "TCELL.IS",
    "ARCLK":  "ARCLK.IS",
    "TOASO":  "TOASO.IS",
    # Index
    "BIST100": "XU100.IS",
    "XU100":   "XU100.IS",
    # FX
    "USDTRY":  "USDTRY=X",
    "USD/TRY": "USDTRY=X",
    "EURUSD":  "EURUSD=X",
    # Commodities / Crypto — handled specially in fetch_market_snapshot
    "ALTIN":   "__GOLD_TRY__",
    "GOLD":    "__GOLD_TRY__",
    "XAU":     "__GOLD_TRY__",
    "BTC":     "BTC-USD",
    "BITCOIN": "BTC-USD",
    "ETH":     "ETH-USD",
}

TROY_OZ_TO_GRAM = 31.1035  # 1 troy ounce = 31.1035 grams


def normalize_ticker(ticker: str) -> str:
    """Convert bare symbols to Yahoo Finance format."""
    upper = ticker.strip().upper()
    if upper in TICKER_MAP:
        return TICKER_MAP[upper]
    # If it already has a suffix (.IS, =X, -USD etc.), return as-is
    if "." in upper or "=" in upper or "-" in upper:
        return upper
    # Assume BIST if nothing matches
    return upper + ".IS"


def get_live_price(yahoo_ticker: str) -> float | None:
    """
    Robust price fetcher:
    1. Try fast_info.last_price  (real-time, no parsing overhead)
    2. Fall back to today's 1-minute history last close
    3. Fall back to info['currentPrice'] / 'regularMarketPrice'
    Returns None if all fail.
    """
    try:
        t = yf.Ticker(yahoo_ticker)

        # Method 1 – fast_info (fastest, most reliable for live price)
        try:
            price = t.fast_info.last_price
            if price and price > 0:
                logger.debug(f"[fast_info] {yahoo_ticker} → {price}")
                return float(price)
        except Exception:
            pass

        # Method 2 – intraday history (1-min, today)
        try:
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                logger.debug(f"[history 1m] {yahoo_ticker} → {price}")
                return price
        except Exception:
            pass

        # Method 3 – info dict
        try:
            info = t.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price and price > 0:
                logger.debug(f"[info] {yahoo_ticker} → {price}")
                return float(price)
        except Exception:
            pass

        logger.warning(f"All price methods failed for {yahoo_ticker}")
        return None

    except Exception as e:
        logger.error(f"get_live_price({yahoo_ticker}) fatal: {e}")
        return None


def get_gram_gold_try() -> dict:
    """
    Calculates Gram Gold in TRY dynamically:
      Gram Gold TRY = (Gold Spot USD/oz ÷ 31.1035) × USD/TRY rate
    """
    oz_price = get_live_price("GC=F")     # COMEX Gold Futures (USD/oz)
    usd_try   = get_live_price("USDTRY=X")

    if oz_price and usd_try:
        gram_usd = oz_price / TROY_OZ_TO_GRAM
        gram_try = gram_usd * usd_try
        return {
            "gold_oz_usd":   round(oz_price, 2),
            "usd_try":        round(usd_try, 4),
            "gold_gram_usd":  round(gram_usd, 4),
            "gold_gram_try":  round(gram_try, 2),
        }
    return {"error": "Could not fetch gold or USD/TRY prices"}


def fetch_ohlcv_metrics(yahoo_ticker: str) -> dict:
    """
    Fetch OHLCV + technical indicators for analysis tools.
    Uses 3-month daily data (auto-adjusted = True handles splits).
    """
    try:
        t = yf.Ticker(yahoo_ticker)
        # auto_adjust=True automatically applies split & dividend adjustments
        hist = t.history(period="3mo", interval="1d", auto_adjust=True)

        if hist.empty:
            return {"error": f"No history data for {yahoo_ticker}"}

        close = hist["Close"]
        volume = hist["Volume"]

        # RSI-14
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
        rs   = gain / loss.replace(0, np.nan)
        rsi  = float((100 - 100 / (1 + rs)).iloc[-1]) if not rs.empty else None

        # 20-day SMA
        sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None

        # Annualised volatility
        vol_annual = float(close.pct_change().std() * np.sqrt(252))

        # 52-week high/low (use up to 252 trading days)
        hist_1y = t.history(period="1y", interval="1d", auto_adjust=True)
        high_52w = float(hist_1y["High"].max()) if not hist_1y.empty else None
        low_52w  = float(hist_1y["Low"].min())  if not hist_1y.empty else None

        # Current price (most reliable: last close of today's data)
        current_price = float(close.iloc[-1])
        prev_close    = float(close.iloc[-2]) if len(close) >= 2 else current_price
        pct_change    = round((current_price - prev_close) / prev_close * 100, 2)

        # Fundamental data from info
        info = {}
        try:
            info = t.info
        except Exception:
            pass

        return {
            "ticker":          yahoo_ticker,
            "current_price":   current_price,
            "pct_change_day":  pct_change,
            "prev_close":      round(prev_close, 4),
            "sma20":           round(sma20, 4)  if sma20  else None,
            "rsi_14":          round(rsi,   2)   if rsi    else None,
            "volatility_ann":  round(vol_annual, 4),
            "high_52w":        round(high_52w, 4) if high_52w else None,
            "low_52w":         round(low_52w,  4) if low_52w  else None,
            "avg_volume":      int(volume.mean()) if not volume.empty else None,
            "pe_ratio":        info.get("forwardPE") or info.get("trailingPE"),
            "pb_ratio":        info.get("priceToBook"),
            "dividend_yield":  info.get("dividendYield"),
            "market_cap":      info.get("marketCap"),
            "debt_to_equity":  info.get("debtToEquity"),
            "revenue_growth":  info.get("revenueGrowth"),
            "currency":        info.get("currency", "TRY"),
            "fetched_at_utc":  datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"fetch_ohlcv_metrics({yahoo_ticker}): {e}")
        return {"error": f"Data fetch failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# LLM gateway
# ──────────────────────────────────────────────────────────────────────────────
class LightweightHedgeFundEngine:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"

    async def _get_llm_completion(self, system_prompt: str, user_content: str, temperature: float = 0.7) -> str:
        if self.gemini_key:
            url   = self.gemini_url
            key   = self.gemini_key
            model = "gemini-1.5-flash"
        elif self.openai_key:
            url   = self.openai_url
            key   = self.openai_key
            model = "gpt-4o-mini"
        else:
            return "Error: No API key configured (GEMINI_API_KEY or OPENAI_API_KEY)."

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model":    model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user",   "content": user_content}
                        ],
                        "temperature": temperature
                    },
                    timeout=90.0
                )
                data = response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                return f"API Error: {json.dumps(data)}"
            except Exception as e:
                return f"LLM Connection Error: {str(e)}"

    # ── public wrapper kept for backward compatibility ─────────────────────
    async def fetch_financials(self, ticker: str) -> dict:
        """
        Main data-fetch entry point.
        Normalises the ticker, handles special assets (gold, FX),
        and returns OHLCV + fundamental metrics.
        """
        yahoo_ticker = normalize_ticker(ticker)

        # Special case: gram gold in TRY
        if yahoo_ticker == "__GOLD_TRY__":
            return get_gram_gold_try()

        # All other tickers (stocks, indices, BTC, FX futures)
        return fetch_ohlcv_metrics(yahoo_ticker)

    # ── Analysis tools ─────────────────────────────────────────────────────
    async def run_core_analysis(self, ticker: str) -> dict:
        """5 core agents + RICO synthesis (default 'analyze' tool)."""
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics:
            return metrics

        context = (
            f"Live market data for {ticker} (fetched {metrics.get('fetched_at_utc','now')}):\n"
            f"{json.dumps(metrics, indent=2)}\n\n"
            "IMPORTANT: Use ONLY the numbers in this data block. Do NOT use training-data memory for prices."
        )

        tasks = [
            self._get_llm_completion(
                f"{p} Provide a 2-3 sentence perspective using ONLY the live data provided.",
                context
            )
            for p in CORE_SQUAD.values()
        ]
        results      = await asyncio.gather(*tasks)
        agent_reports = dict(zip(CORE_SQUAD.keys(), results))

        rico_prompt = (
            "You are RICO, Chief Investment Strategist of Kronos-Analyst. "
            "Review the perspectives from Buffett, Graham, Lynch, Munger, and Damodaran "
            "alongside the raw live data. Synthesize into a final Buy/Hold/Sell verdict "
            "with a concise rationale. Ground every claim in the provided data."
        )
        final_decision = await self._get_llm_completion(
            rico_prompt,
            f"Analyst Inputs:\n{json.dumps(agent_reports)}"
        )

        return {
            "ticker":                   ticker,
            "yahoo_ticker":             normalize_ticker(ticker),
            "metrics":                  metrics,
            "core_squad_perspectives":  agent_reports,
            "rico_strategic_verdict":   final_decision,
            "mode":                     "Core Hybrid (v5.0)",
        }

    async def run_full_council(self, ticker: str) -> dict:
        """All 19 legendary agents (council_analysis tool)."""
        metrics = await self.fetch_financials(ticker)
        if "error" in metrics:
            return metrics

        context = (
            f"Live market data for {ticker} (fetched {metrics.get('fetched_at_utc','now')}):\n"
            f"{json.dumps(metrics, indent=2)}\n\n"
            "IMPORTANT: Use ONLY the numbers in this data block. Do NOT hallucinate prices."
        )

        agent_names   = list(FULL_COUNCIL.keys())
        agent_reports = {}

        # Batched parallel execution (avoid rate limits)
        for i in range(0, len(agent_names), 5):
            batch   = agent_names[i:i+5]
            tasks   = [self._get_llm_completion(FULL_COUNCIL[name], context) for name in batch]
            results = await asyncio.gather(*tasks)
            for name, report in zip(batch, results):
                agent_reports[name] = report

        pm_prompt = (
            "You are the Portfolio Manager overseeing the Kronos Investment Council. "
            "Review analyses from all 19 legendary investors and provide a comprehensive "
            "board-room summary plus a final investment verdict. "
            "Cite specific data points from the live metrics provided."
        )
        final_decision = await self._get_llm_completion(
            pm_prompt,
            f"Council Reports:\n{json.dumps(agent_reports)}"
        )

        return {
            "ticker":         ticker,
            "yahoo_ticker":   normalize_ticker(ticker),
            "metrics":        metrics,
            "council_reports": agent_reports,
            "final_verdict":  final_decision,
            "mode":           "Full Council Siege (v5.0)",
        }
