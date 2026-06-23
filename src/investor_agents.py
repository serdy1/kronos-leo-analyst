import json
from .rules import INVESTMENT_RULES


class BaseInvestorAgent:
    def __init__(self, name: str):
        self.name = name
        rules = INVESTMENT_RULES.get(name, {})
        self.formulas = rules.get("formulas", {})
        self.checklist = rules.get("checklist", [])
        self.screening = rules.get("screening_criteria", {})
        self.strategy = rules.get("strategy", "")

    def get_identity(self):
        return {
            "name": self.name.replace("_", " ").title(),
            "strategy": self.strategy,
            "formulas": list(self.formulas.keys()),
            "checklist_count": len(self.checklist),
        }

    def analyze_stock(self, ticker: str, fundamentals: dict) -> dict:
        raise NotImplementedError

    def explain_rule(self, rule_name: str) -> str:
        if rule_name in self.formulas:
            return f"**{rule_name}**: {self.formulas[rule_name]}"
        for item in self.checklist:
            if rule_name.lower() in item.lower():
                return f"✓ {item}"
        return f"No rule found matching '{rule_name}'"

    def get_formulas(self) -> dict:
        return self.formulas

    def get_checklist(self) -> list:
        return self.checklist

    def ask(self, question: str) -> str:
        q = question.lower()
        if "formula" in q or "formül" in q:
            return json.dumps(self.formulas, indent=2, ensure_ascii=False)
        if "kural" in q or "check" in q or "list" in q:
            return "\n".join(f"{i+1}. {r}" for i, r in enumerate(self.checklist))
        if "strateji" in q or "strategy" in q:
            return self.strategy
        if "kimsin" in q or "who are you" in q or "identity" in q:
            return json.dumps(self.get_identity(), indent=2, ensure_ascii=False)
        return self._search_knowledge(q)

    def _search_knowledge(self, question: str) -> str:
        q = question.lower()
        results = []
        for formula_name, formula_text in self.formulas.items():
            if any(word in q for word in formula_name.replace("_", " ").split()):
                results.append(f"**{formula_name}**: {formula_text}")
        for item in self.checklist:
            if any(word in q for word in item.lower().split() if len(word) > 4):
                results.append(f"📋 {item}")
        if results:
            return "\n\n".join(results[:5])
        return f"'{question}' ile ilgili net bir kural bulamadım. Kullanabileceğin komutlar: formula, checklist, strategy, identity"


class BenjaminGrahamAgent(BaseInvestorAgent):
    def __init__(self):
        super().__init__("benjamin_graham")

    def analyze_stock(self, ticker: str, fundamentals: dict) -> dict:
        eps = fundamentals.get("eps") or 0
        growth = fundamentals.get("earnings_growth_rate") or 0
        current_price = fundamentals.get("current_price") or 0
        book_value = fundamentals.get("book_value_per_share") or 0
        debt_to_equity = fundamentals.get("debt_to_equity") if fundamentals.get("debt_to_equity") is not None else 999
        current_ratio = fundamentals.get("current_ratio") or 0
        total_assets = fundamentals.get("total_assets") or 0
        total_liabilities = fundamentals.get("total_liabilities") or 0

        intrinsic = eps * (8.5 + 2 * growth) if eps > 0 else 0
        ncav = total_assets - total_liabilities
        graham_number = (22.5 * eps * book_value) ** 0.5 if eps > 0 and book_value > 0 else 0
        margin_of_safety = ((intrinsic - current_price) / current_price * 100) if current_price > 0 and intrinsic > 0 else 0

        signals = []
        if intrinsic > 0 and current_price > 0 and current_price < intrinsic:
            signals.append(f"✅ UNDERVALUED: Intrinsic value (${intrinsic:.2f}) > Current price (${current_price:.2f})")
        else:
            signals.append(f"❌ OVERVALUED: Price (${current_price:.2f}) exceeds intrinsic value (${intrinsic:.2f})" if intrinsic > 0 else "⚠️ Cannot calculate intrinsic value (EPS missing or zero)")
        if debt_to_equity < 1.0:
            signals.append("✅ Debt/Equity ratio is acceptable")
        else:
            signals.append(f"❌ High debt/Equity: {debt_to_equity:.2f}")
        if current_ratio > 1.5:
            signals.append("✅ Current ratio indicates good liquidity")
        else:
            signals.append("❌ Current ratio too low")
        if graham_number > 0 and current_price < graham_number:
            signals.append(f"✅ Price below Graham Number (${graham_number:.2f})")
        elif graham_number > 0:
            signals.append(f"❌ Price above Graham Number (${graham_number:.2f})")
        if margin_of_safety > 0:
            signals.append(f"✅ Margin of safety: {margin_of_safety:.1f}%")

        return {
            "ticker": ticker,
            "agent": "Benjamin Graham",
            "intrinsic_value": round(intrinsic, 2),
            "graham_number": round(graham_number, 2),
            "ncav": round(ncav, 2) if ncav else None,
            "margin_of_safety_pct": round(margin_of_safety, 1),
            "signal_summary": signals,
            "verdict": "BUY (Margin of Safety)" if margin_of_safety > 0 and debt_to_equity < 1.0 else "HOLD - does not meet all defensive criteria",
        }


class PeterLynchAgent(BaseInvestorAgent):
    def __init__(self):
        super().__init__("peter_lynch")

    def categorize_growth(self, growth_rate: float) -> str:
        if growth_rate >= 20:
            return "Fast Grower"
        elif growth_rate >= 10:
            return "Stalwart"
        elif growth_rate >= 5:
            return "Slow Grower"
        else:
            return "Cyclical / Turnaround candidate"

    def analyze_stock(self, ticker: str, fundamentals: dict) -> dict:
        pe = fundamentals.get("pe_ratio") or 0
        growth = fundamentals.get("earnings_growth_rate") or 0
        current_price = fundamentals.get("current_price") or 0
        inventory_growth = fundamentals.get("inventory_growth_pct") or 0
        sales_growth = fundamentals.get("sales_growth_pct") or 0
        debt_to_equity = fundamentals.get("debt_to_equity") or 0
        dividend_yield = fundamentals.get("dividend_yield") or 0
        free_cash_flow = fundamentals.get("free_cash_flow") or 0
        market_cap = fundamentals.get("market_cap") or 1

        peg = pe / growth if growth > 0 and pe > 0 else 999
        category = self.categorize_growth(growth)
        fcf_yield = (free_cash_flow / market_cap * 100) if market_cap > 0 else 0
        adjusted_peg = pe / (dividend_yield + growth) if (dividend_yield + growth) > 0 else 999

        signals = []
        if peg < 1.0:
            signals.append(f"✅ PEG ratio ({peg:.2f}) < 1.0 - Undervalued relative to growth")
        else:
            signals.append(f"❌ PEG ratio ({peg:.2f}) > 1.0 - Overvalued relative to growth")
        if inventory_growth <= sales_growth:
            signals.append("✅ Inventory growth is under control")
        else:
            signals.append("❌ Inventory growing faster than sales - warning sign")
        if debt_to_equity < 0.8:
            signals.append("✅ Debt level is manageable")
        else:
            signals.append(f"❌ High debt/equity ratio: {debt_to_equity:.2f}")
        if fcf_yield > 3:
            signals.append(f"✅ Strong free cash flow yield: {fcf_yield:.1f}%")
        if dividend_yield > 0 and category == "Slow Grower":
            signals.append(f"✅ Dividend yield ({dividend_yield:.1f}%) adds return for slow grower")

        return {
            "ticker": ticker,
            "agent": "Peter Lynch",
            "category": category,
            "peg_ratio": round(peg, 2),
            "adjusted_peg": round(adjusted_peg, 2),
            "free_cash_flow_yield_pct": round(fcf_yield, 1),
            "signal_summary": signals,
            "verdict": f"BUY - {category}" if peg < 1.0 and inventory_growth <= sales_growth else "HOLD - keep monitoring or look for better opportunities",
        }


class WarrenBuffettAgent(BaseInvestorAgent):
    def __init__(self):
        super().__init__("warren_buffett")

    def analyze_stock(self, ticker: str, fundamentals: dict) -> dict:
        roe = fundamentals.get("roe") or 0
        debt_to_equity = fundamentals.get("debt_to_equity") if fundamentals.get("debt_to_equity") is not None else 999
        operating_margin = fundamentals.get("operating_margin") or 0
        earnings_growth = fundamentals.get("earnings_growth_rate") or 0
        current_price = fundamentals.get("current_price") or 0
        net_income = fundamentals.get("net_income") or 0
        depreciation = fundamentals.get("depreciation") or 0
        maintenance_capex = fundamentals.get("maintenance_capex") or (depreciation * 0.85)
        book_value = fundamentals.get("book_value_per_share") or 0

        owner_earnings = net_income + depreciation - maintenance_capex
        roe_pct = roe * 100 if roe < 1 else roe

        signals = []
        if roe_pct > 15:
            signals.append(f"✅ ROE is strong at {roe_pct:.1f}% (>15%)")
        else:
            signals.append(f"❌ ROE is weak at {roe_pct:.1f}% (below 15%)")
        if debt_to_equity < 0.5:
            signals.append("✅ Conservative debt levels")
        elif debt_to_equity < 1.0:
            signals.append("⚠️ Moderate debt levels")
        else:
            signals.append(f"❌ High debt/equity: {debt_to_equity:.2f}")
        if operating_margin > 15:
            signals.append(f"✅ Strong operating margins: {operating_margin:.1f}%")
        else:
            signals.append(f"❌ Weak operating margins: {operating_margin:.1f}%")
        if earnings_growth > 5:
            signals.append(f"✅ Consistent earnings growth: {earnings_growth:.1f}%")
        else:
            signals.append(f"⚠️ Low earnings growth: {earnings_growth:.1f}%")
        if owner_earnings > 0:
            signals.append("✅ Positive owner earnings - company generates real value")

        return {
            "ticker": ticker,
            "agent": "Warren Buffett",
            "roe_pct": round(roe_pct, 1),
            "owner_earnings": round(owner_earnings, 2),
            "operating_margin_pct": round(operating_margin, 1),
            "signal_summary": signals,
            "verdict": f"BUY - Wonderful business at fair price" if roe_pct > 15 and debt_to_equity < 0.5 and operating_margin > 15 else "HOLD - does not meet Buffett's quality criteria",
        }


class InvestorAgentFactory:
    _agents = {
        "benjamin_graham": BenjaminGrahamAgent,
        "peter_lynch": PeterLynchAgent,
        "warren_buffett": WarrenBuffettAgent,
    }

    @classmethod
    def get_agent(cls, name: str) -> BaseInvestorAgent:
        name = name.lower().replace(" ", "_")
        if "graham" in name:
            return cls._agents["benjamin_graham"]()
        if "lynch" in name:
            return cls._agents["peter_lynch"]()
        if "buffett" in name or "warren" in name or "buffet" in name:
            return cls._agents["warren_buffett"]()
        raise ValueError(f"Unknown investor: {name}. Available: {', '.join(cls._agents.keys())}")

    @classmethod
    def list_agents(cls) -> list:
        return [
            {
                "id": key,
                "name": agent_cls().get_identity()["name"],
                "strategy": agent_cls().get_identity()["strategy"],
            }
            for key, agent_cls in cls._agents.items()
        ]

    @classmethod
    def ask_agent(cls, agent_name: str, question: str) -> str:
        agent = cls.get_agent(agent_name)
        return agent.ask(question)
