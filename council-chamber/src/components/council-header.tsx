import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { stocks } from "../data/stocks";
import { debates } from "../data/debates";

export function CouncilHeader() {
  const bistChange = stocks.quotes.reduce((sum, q) => sum + q.changePercent, 0) / stocks.quotes.length;
  const isPositive = bistChange >= 0;
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const latestSession = debates[debates.length - 1];

  return (
    <header className="border-b border-slate-800 bg-[#020617]/95 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Left: Branding */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400 animate-pulse" />
            <span className="text-sm font-bold text-white tracking-wider uppercase font-mono">
              Büyük Yatırım Konseyi
            </span>
          </div>
          <div className="hidden md:flex items-center gap-3 border-l border-slate-800 pl-4">
            <span className="text-xs text-slate-500 font-mono">BIST-100</span>
            <div className={`flex items-center gap-1 text-sm font-bold font-mono ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
              {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{bistChange >= 0 ? "+" : ""}{bistChange.toFixed(2)}%</span>
            </div>
          </div>
          {latestSession && (
            <div className="hidden lg:flex items-center gap-2 border-l border-slate-800 pl-4 text-xs font-mono text-slate-500">
              <span className="text-slate-600">Son Oturum:</span>
              <span className="text-blue-400 font-bold">{latestSession.ticker}</span>
            </div>
          )}
        </div>

        {/* Right: Status */}
        <div className="flex items-center gap-4 text-xs font-mono text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            LIVE
          </span>
          <span className="hidden sm:inline">{time.toLocaleTimeString("tr-TR")}</span>
          <span className="hidden sm:inline border-l border-slate-800 pl-4">{new Date().toLocaleDateString("tr-TR")}</span>
        </div>
      </div>
    </header>
  );
}
