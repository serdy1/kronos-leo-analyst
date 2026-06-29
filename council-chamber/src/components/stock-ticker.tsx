import { stocks, StockQuote } from "../data/stocks";

interface StockTickerProps {
  activeTicker: string | null;
  onSelect: (stock: StockQuote) => void;
}

export function StockTicker({ activeTicker, onSelect }: StockTickerProps) {
  return (
    <div className="flex items-center gap-1 px-4 py-2 bg-[#0c1126] border-b border-slate-800 overflow-x-auto">
      <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 tracking-wider mr-2 shrink-0">
        <i className="fa-solid fa-chart-simple text-indigo-400" />
        TAKİP
      </div>
      {stocks.quotes.map((stock) => (
        <button
          key={stock.ticker}
          onClick={() => onSelect(stock)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all text-xs ${
            activeTicker === stock.ticker
              ? "bg-indigo-950/60 border-indigo-600 text-indigo-200 shadow-lg shadow-indigo-900/30"
              : "bg-slate-800/40 border-slate-700/50 text-slate-400 hover:border-slate-600 hover:text-slate-200"
          }`}
        >
          <span className="font-bold">{stock.ticker}</span>
          <span className="font-mono">
            {stock.currency}
            {stock.price.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}
          </span>
          <span
            className={`text-[10px] font-semibold ${
              stock.change >= 0 ? "text-emerald-400" : "text-red-400"
            }`}
          >
            {stock.change >= 0 ? "+" : ""}
            {stock.change}%
          </span>
        </button>
      ))}
    </div>
  );
}
