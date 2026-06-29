import { indices } from "../data/indices";
import { analysts } from "../data/agents";
import { stocks } from "../data/stocks";

export function WelcomeDashboard() {
  const activeAgents = analysts.filter((a) => a.isActive);
  const masadaCount = analysts.filter((a) => a.badge === "MASADA").length;
  const aktifCount = analysts.filter((a) => a.badge === "AKTİF").length;

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto">
      <div className="max-w-3xl mx-auto w-full space-y-6">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Konsey Odası</h1>
          <p className="text-xs text-slate-500 mt-1">
            Yatırım kararlarınızı tarihin en büyük yatırımcılarıyla tartışın
          </p>
        </div>

        <div className="grid grid-cols-4 gap-2">
          {indices.map((idx) => (
            <div
              key={idx.name}
              className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3"
            >
              <div className="text-[10px] text-slate-500 font-medium">{idx.name}</div>
              <div className="text-sm font-bold text-slate-200 mt-0.5">{idx.value}</div>
              <div
                className={`text-[10px] font-semibold ${
                  idx.positive ? "text-emerald-400" : "text-red-400"
                }`}
              >
                {idx.change}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-indigo-950/20 border border-indigo-900/40 rounded-xl p-5">
          <h3 className="text-xs font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <i className="fa-solid fa-play text-indigo-400" />
            Simülasyon Başlat
          </h3>
          <p className="text-[11px] text-slate-500 leading-relaxed mb-4">
            Bir hisse senedi seçin ve konseyin dev yatırımcılarının o hisse hakkındaki
            derinlemesine analizlerini, tartışmalarını ve stratejik öngörülerini canlı olarak
            izleyin.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            {stocks.quotes.map((stock) => (
              <button
                key={stock.ticker}
                className="px-3 py-1.5 text-xs font-semibold bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:bg-indigo-900/50 hover:border-indigo-700 transition-all"
              >
                {stock.ticker} <span className="text-slate-500">→</span>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-slate-800/20 border border-slate-700/30 rounded-xl p-5">
          <h3 className="text-xs font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <i className="fa-solid fa-chart-pie text-purple-400" />
            Konsey Kompozisyonu
          </h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-800/40 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-slate-100">{analysts.length}</div>
              <div className="text-[10px] text-slate-500">Toplam Üye</div>
            </div>
            <div className="bg-emerald-950/30 border border-emerald-900/30 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-emerald-400">{masadaCount}</div>
              <div className="text-[10px] text-emerald-600">Masada</div>
            </div>
            <div className="bg-blue-950/30 border border-blue-900/30 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-blue-400">{aktifCount}</div>
              <div className="text-[10px] text-blue-500">Aktif</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
