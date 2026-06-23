import pandas as pd
import numpy as np
import yfinance as yf
import torch
import os
from datetime import datetime, timedelta


class KronosLeoEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.kronos_available = False
        self.tokenizer = None
        self.model = None
        self.predictor = None
        self._kronos_loaded = False

    def _ensure_kronos_loaded(self):
        if self._kronos_loaded:
            return
        self._kronos_loaded = True
        try:
            from src.kronos import KronosTokenizer, Kronos, KronosPredictor
            hf_token = os.getenv("HF_TOKEN")
            model_name = os.getenv("KRONOS_MODEL", "NeoQuasar/Kronos-small")
            tokenizer_name = os.getenv("KRONOS_TOKENIZER", "NeoQuasar/Kronos-Tokenizer-base")

            self.tokenizer = KronosTokenizer.from_pretrained(tokenizer_name, token=hf_token)
            self.model = Kronos.from_pretrained(model_name, token=hf_token)
            self.predictor = KronosPredictor(self.model, self.tokenizer, device=self.device, max_context=512)
            self.kronos_available = True
            print(f"[KRONOS] Loaded {model_name} on {self.device}")
        except Exception as e:
            print(f"[KRONOS] Model not loaded (using simulated forecasts): {e}")

    def _fetch_data(self, ticker: str, days_back: int = 365):
        period = f"{min(days_back, 730)}d"
        df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None
        df.columns = [c[0].lower() for c in df.columns]
        return df

    def _kronos_forecast(self, df: pd.DataFrame, horizon: int = 30):
        self._ensure_kronos_loaded()
        if self.kronos_available and self.predictor:
            x_timestamp = pd.Series(pd.to_datetime(df.index[-len(df):]))
            y_timestamp = pd.Series(pd.date_range(
                start=x_timestamp.iloc[-1] + timedelta(days=1),
                periods=horizon,
                freq="D"
            ))
            pred_df = self.predictor.predict(
                df=df[["open", "high", "low", "close", "volume"]],
                x_timestamp=x_timestamp,
                y_timestamp=y_timestamp,
                pred_len=horizon,
                T=1.0,
                top_p=0.9,
                sample_count=1,
                verbose=False
            )
            return pred_df
        return None

    def _simulate_forecast(self, df: pd.DataFrame, horizon: int = 30):
        last_close = float(df["close"].iloc[-1])
        returns = df["close"].pct_change().dropna()
        vol = returns.std()
        mu = returns.mean()
        last_date = df.index[-1]

        projected_returns = np.random.normal(mu, vol, horizon)
        cumulative_returns = np.cumprod(1 + projected_returns)
        forecast_prices = last_close * cumulative_returns

        forecast_df = pd.DataFrame({
            "open": forecast_prices * np.random.uniform(0.98, 1.0, horizon),
            "high": forecast_prices * np.random.uniform(1.01, 1.05, horizon),
            "low": forecast_prices * np.random.uniform(0.95, 0.99, horizon),
            "close": forecast_prices,
            "volume": np.random.randint(100000, 10000000, horizon),
            "amount": forecast_prices * np.random.randint(100000, 10000000, horizon),
        }, index=pd.date_range(start=last_date + timedelta(days=1), periods=horizon, freq="D"))

        return forecast_df

    def _analyze_fundamentals(self, ticker: str):
        try:
            info = yf.Ticker(ticker).info
            return {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "eps": info.get("trailingEps"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "name": info.get("longName"),
            }
        except Exception as e:
            return {"error": str(e)}

    def _fetch_rich_fundamentals(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
        except Exception:
            info = {}

        eps = info.get("trailingEps")
        pe_ratio = info.get("trailingPE")
        market_cap = info.get("marketCap")
        dividend_yield = info.get("dividendYield") or 0.0
        
        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity is not None:
            if debt_to_equity > 5.0:
                debt_to_equity = debt_to_equity / 100.0
        
        current_ratio = info.get("currentRatio")
        book_value_per_share = info.get("bookValue")
        
        roe = info.get("returnOnEquity")
        if roe is not None:
            roe = roe * 100.0 if abs(roe) < 1.0 else roe
            
        operating_margin = info.get("operatingMargins")
        if operating_margin is not None:
            operating_margin = operating_margin * 100.0 if abs(operating_margin) < 1.0 else operating_margin

        earnings_growth_rate = info.get("earningsGrowth")
        if earnings_growth_rate is not None:
            earnings_growth_rate = earnings_growth_rate * 100.0 if abs(earnings_growth_rate) < 1.0 else earnings_growth_rate
        else:
            earnings_growth_rate = 10.0
            
        free_cash_flow = info.get("freeCashflow")
        net_income = info.get("netIncomeToCommon") or info.get("netIncome")

        total_assets = None
        total_liabilities = None
        depreciation = None

        def get_df_value(df, keys, col_idx=0):
            if df is None or df.empty:
                return None
            for key in keys:
                for idx in df.index:
                    if key.lower() == str(idx).strip().lower() or key.lower() in str(idx).strip().lower():
                        val = df.loc[idx]
                        if isinstance(val, pd.Series):
                            return float(val.iloc[col_idx]) if col_idx < len(val) and not pd.isna(val.iloc[col_idx]) else None
                        return float(val) if not pd.isna(val) else None
            return None

        try:
            bs = t.balance_sheet
            total_assets = get_df_value(bs, ["Total Assets", "totalAssets"])
            total_liabilities = get_df_value(bs, ["Total Liabilities Net Minority Interest", "Total Liabilities", "totalLiabilities"])
            if not book_value_per_share:
                equity = get_df_value(bs, ["Common Stock Equity", "Stockholders Equity", "totalStockholdersEquity"])
                shares = info.get("sharesOutstanding")
                if equity and shares:
                    book_value_per_share = equity / shares
        except Exception as e:
            print(f"[ENGINE] Failed to fetch balance sheet for {ticker}: {e}")

        try:
            cf = t.cashflow
            depreciation = get_df_value(cf, ["Depreciation And Amortization", "Depreciation & Amortization", "Depreciation", "depreciationAndAmortization"])
            if not free_cash_flow:
                free_cash_flow = get_df_value(cf, ["Free Cash Flow", "freeCashFlow"])
        except Exception as e:
            print(f"[ENGINE] Failed to fetch cashflow for {ticker}: {e}")

        try:
            fin = t.financials
            if not net_income:
                net_income = get_df_value(fin, ["Net Income", "netIncome"])
        except Exception as e:
            print(f"[ENGINE] Failed to fetch financials for {ticker}: {e}")

        if total_assets is None:
            total_assets = 0.0
        if total_liabilities is None:
            total_liabilities = 0.0
        if book_value_per_share is None:
            book_value_per_share = 0.0
        if debt_to_equity is None:
            if total_liabilities and total_assets and (total_assets - total_liabilities) > 0:
                debt_to_equity = total_liabilities / (total_assets - total_liabilities)
            else:
                debt_to_equity = 0.5
        if current_ratio is None:
            current_ratio = 1.5
        if roe is None:
            roe = 10.0
        if operating_margin is None:
            operating_margin = 10.0
        if free_cash_flow is None:
            free_cash_flow = 0.0
        if net_income is None:
            net_income = 0.0
        if depreciation is None:
            depreciation = 0.0

        inventory_growth_pct = 0.0
        sales_growth_pct = 0.0
        try:
            bs = t.balance_sheet
            if bs is not None and len(bs.columns) >= 2:
                inv_val_cur = get_df_value(bs, ["Inventory", "inventories"], col_idx=0)
                inv_val_prev = get_df_value(bs, ["Inventory", "inventories"], col_idx=1)
                if inv_val_cur is not None and inv_val_prev and inv_val_prev > 0:
                    inventory_growth_pct = ((inv_val_cur - inv_val_prev) / inv_val_prev) * 100.0
            
            fin = t.financials
            if fin is not None and len(fin.columns) >= 2:
                rev_val_cur = get_df_value(fin, ["Total Revenue", "totalRevenue"], col_idx=0)
                rev_val_prev = get_df_value(fin, ["Total Revenue", "totalRevenue"], col_idx=1)
                if rev_val_cur is not None and rev_val_prev and rev_val_prev > 0:
                    sales_growth_pct = ((rev_val_cur - rev_val_prev) / rev_val_prev) * 100.0
        except Exception:
            pass

        # Try multiple price sources
        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
            or info.get("navPrice")
            or 0.0
        )
        # If still 0, try fast download for last close
        if not current_price:
            try:
                hist = t.history(period="5d")
                if hist is not None and not hist.empty:
                    current_price = float(hist["Close"].iloc[-1])
            except Exception:
                pass

        return {
            "current_price": current_price,
            "eps": eps,
            "pe_ratio": pe_ratio,
            "debt_to_equity": debt_to_equity,
            "current_ratio": current_ratio,
            "book_value_per_share": book_value_per_share,
            "earnings_growth_rate": earnings_growth_rate,
            "roe": roe,
            "operating_margin": operating_margin,
            "dividend_yield": dividend_yield * 100.0 if dividend_yield else 0.0,
            "market_cap": market_cap,
            "net_income": net_income,
            "depreciation": depreciation,
            "free_cash_flow": free_cash_flow,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "inventory_growth_pct": inventory_growth_pct,
            "sales_growth_pct": sales_growth_pct,
        }


    def _generate_agent_signals(self, ticker: str, forecast_df: pd.DataFrame, fundamentals: dict):
        forecast_return = (float(forecast_df["close"].iloc[-1]) / float(forecast_df["close"].iloc[0]) - 1) if forecast_df is not None else 0
        pe = fundamentals.get("pe_ratio") or 20
        beta = fundamentals.get("beta") or 1.0

        signals = {}

        if pe < 15 and forecast_return > 0.05:
            signals["warren_buffett"] = {"signal": "bullish", "confidence": 75, "reasoning": "Undervalued with positive forecast"}
        elif pe > 30:
            signals["warren_buffett"] = {"signal": "bearish", "confidence": 60, "reasoning": "Overvalued by historical standards"}
        else:
            signals["warren_buffett"] = {"signal": "neutral", "confidence": 50, "reasoning": "Fair valuation range"}

        if forecast_return > 0.10:
            signals["michael_burry"] = {"signal": "bearish", "confidence": 65, "reasoning": "Forecast suggests unsustainable rally"}
        elif forecast_return < -0.10:
            signals["michael_burry"] = {"signal": "bullish", "confidence": 70, "reasoning": "Forecast suggests potential value opportunity"}
        else:
            signals["michael_burry"] = {"signal": "neutral", "confidence": 50, "reasoning": "No extreme signals detected"}

        if beta < 0.8 and forecast_return > 0:
            signals["ben_graham"] = {"signal": "bullish", "confidence": 70, "reasoning": "Low volatility with positive outlook"}
        elif beta > 1.5:
            signals["ben_graham"] = {"signal": "bearish", "confidence": 55, "reasoning": "Excessive risk for value investor"}
        else:
            signals["ben_graham"] = {"signal": "neutral", "confidence": 50, "reasoning": "Risk profile within acceptable range"}

        if pe < 20 and forecast_return > 0.03:
            signals["peter_lynch"] = {"signal": "bullish", "confidence": 80, "reasoning": "Reasonable growth at reasonable price"}
        elif forecast_return > 0.20:
            signals["cathie_wood"] = {"signal": "bullish", "confidence": 85, "reasoning": "High growth forecast aligns with innovation thesis"}
        else:
            signals["cathie_wood"] = {"signal": "neutral", "confidence": 50, "reasoning": "Growth prospects unclear"}

        trend = "BULLISH" if forecast_return > 0 else "BEARISH"
        signals["kronos_technicals"] = {"signal": trend.lower(), "confidence": min(90, int(abs(forecast_return) * 100)), "reasoning": f"Kronos foundation model projects {forecast_return:.2%} return over forecast horizon"}

        return signals

    def run_unified_analysis(self, ticker: str, days_back: int = 365, horizon: int = 30):
        df = self._fetch_data(ticker, days_back)
        if df is None:
            return {"error": f"No data found for ticker {ticker}"}

        forecast_df = self._kronos_forecast(df, horizon)
        if forecast_df is None:
            forecast_df = self._simulate_forecast(df, horizon)

        fundamentals = self._analyze_fundamentals(ticker)
        last_price = float(df["close"].iloc[-1])
        forecast_price = float(forecast_df["close"].iloc[-1])
        projected_return = (forecast_price / last_price) - 1

        signals = self._generate_agent_signals(ticker, forecast_df, fundamentals)

        bullish = sum(1 for s in signals.values() if s.get("signal") == "bullish")
        bearish = sum(1 for s in signals.values() if s.get("signal") == "bearish")
        total = len(signals)

        if bullish > bearish:
            final_action = "BUY"
            confidence = (bullish / total) * 0.5 + min(abs(projected_return) * 2, 0.5)
        elif bearish > bullish:
            final_action = "SELL"
            confidence = (bearish / total) * 0.5 + min(abs(projected_return) * 2, 0.5)
        else:
            final_action = "HOLD"
            confidence = 0.5

        confidence = min(round(confidence, 2), 0.95)

        return {
            "ticker": ticker,
            "current_price": round(last_price, 2),
            "forecast_price": round(forecast_price, 2),
            "projected_return": f"{projected_return:.2%}",
            "kronos_model_loaded": self.kronos_available,
            "fundamentals": fundamentals,
            "agent_signals": signals,
            "signal_summary": {
                "bullish": bullish,
                "bearish": bearish,
                "neutral": total - bullish - bearish,
                "total": total,
            },
            "final_recommendation": final_action,
            "confidence": confidence,
            "historical_data_points": len(df),
            "forecast_horizon": horizon,
            "report_summary": (
                f"Unified analysis for {ticker} completed. Kronos foundation model {'loaded' if self.kronos_available else 'simulated'} "
                f"projects a {'bullish' if projected_return > 0 else 'bearish'} trend ({projected_return:.2%}). "
                f"Agentic synthesis: {bullish}/{total} bullish, {bearish}/{total} bearish. "
                f"Final decision: {final_action} with {confidence:.0%} confidence."
            ),
        }

    def run_hedge_fund(self, tickers: list[str], start_date: str, end_date: str, selected_analysts: list[str] = None):
        try:
            from src.hedge_fund.main import run_hedge_fund as hf_run
            portfolio = {
                "cash": 100000.0,
                "margin_requirement": 0.0,
                "margin_used": 0.0,
                "positions": {t: {"long": 0, "short": 0, "long_cost_basis": 0.0, "short_cost_basis": 0.0, "short_margin_used": 0.0} for t in tickers},
                "realized_gains": {t: {"long": 0.0, "short": 0.0} for t in tickers},
            }
            result = hf_run(
                tickers=tickers,
                start_date=start_date,
                end_date=end_date,
                portfolio=portfolio,
                show_reasoning=False,
                selected_analysts=selected_analysts or [],
                model_name=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                model_provider=os.getenv("LLM_PROVIDER", "OpenAI"),
            )
            return result
        except Exception as e:
            return {"error": f"Hedge fund workflow failed: {e}"}
