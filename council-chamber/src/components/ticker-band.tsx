import { TrendingUp, TrendingDown } from "lucide-react";
import { stocks } from "../data/stocks";

export function TickerBand() {
  // Duplicate for seamless infinite scroll
  const tickerItems = [...stocks.quotes, ...stocks.quotes];

  return (
    <div className="bg-[#030812] border-b border-slate-800 overflow-hidden py-2">
      <div className="flex whitespace-nowrap animate-ticker">
        {tickerItems.map((stock, i) => {
          const isPositive = stock.change >= 0;
          return (
            <div key={`${stock.ticker}-${i}`} className="flex items-center gap-3 mx-8 text-sm">
              <span className="font-bold text-white font-mono tracking-wide">{stock.ticker}</span>
              <span className="text-slate-300 font-mono">{stock.price.toFixed(2)} ₺</span>
              <span
                className={`flex items-center gap-1 font-mono text-xs font-bold ${
                  isPositive ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {isPositive ? "+" : ""}
                {stock.change.toFixed(2)} ({isPositive ? "+" : ""}
                {stock.changePercent.toFixed(2)}%)
              </span>
              {stock.targetPrice && (
                <span className="text-slate-600 text-[10px] font-mono">
                  Hedef: {stock.targetPrice.toFixed(2)} ₺
                </span>
              )}
              <div className="h-3 w-px bg-slate-800" />
            </div>
          );
        })}
      </div>
    </div>
  );
}
