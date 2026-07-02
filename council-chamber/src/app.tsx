import { useState, useEffect, useMemo } from "react";
import { stocks, StockQuote } from "./data/stocks";
import { debates, DebateMessage } from "./data/debates";
import { analysts, Analyst } from "./data/agents";
import { AgentDatabase } from "./components/agent-database";
import { StockTicker } from "./components/stock-ticker";
import { WelcomeDashboard } from "./components/welcome-dashboard";
import { BoardroomTable } from "./components/boardroom-table";
import { TranscriptViewer } from "./components/transcript-viewer";

// 46.67 Decoupled Rate
const FIXED_USDTRY = 46.67;

// Portfolio Mapping: Ticker -> Quantity
const PORTFOLIO_QUANTITIES: Record<string, number> = {
  FROTO: 100,
  PGSUS: 12,
  ANHYT: 50, // Added based on typical asset list
  THYAO: 20,
  DOAS: 30,
  KCHOL: 25,
};

function findSpeakerAgentIds(messages: DebateMessage[]): string[] {
  const ids: string[] = [];
  for (const msg of messages) {
    const found = analysts.find(
      (a) => a.name.toLowerCase() === msg.speaker.toLowerCase()
    );
    if (found && !ids.includes(found.id)) ids.push(found.id);
  }
  return ids;
}

export default function App() {
  const [activeTicker, setActiveTicker] = useState<string | null>(null);
  const [streamedMessages, setStreamedMessages] = useState<DebateMessage[]>([]);
  const [currentSpeaker, setCurrentSpeaker] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [systemTime, setSystemTime] = useState(new Date());
  const [liveQuotes, setLiveQuotes] = useState<StockQuote[]>(stocks.quotes);

  useEffect(() => {
    const timer = setInterval(() => setSystemTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulation of Live Telemetry Fetch (V7.0)
  // In a real environment, this would hit the MCP /backend.
  // Here we ensure the quantities and prices are bound for the UI.
  useEffect(() => {
    const fetchLiveTelemetry = async () => {
      // Simulate price fluctuation while keeping base from data
      const updated = stocks.quotes.map((q) => ({
        ...q,
        price: q.price * (1 + (Math.random() * 0.002 - 0.001)), // Mini fluctuations
      }));
      setLiveQuotes(updated);
    };

    const interval = setInterval(fetchLiveTelemetry, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!activeTicker) {
      setStreamedMessages([]);
      setCurrentSpeaker(null);
      setIsStreaming(false);
      return;
    }

    const session = debates.find((d) => d.ticker === activeTicker);
    if (!session) return;

    setIsStreaming(true);
    setStreamedMessages([]);
    setCurrentSpeaker(null);

    const agentIds = findSpeakerAgentIds(session.messages);
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < session.messages.length) {
        const nextMsg = session.messages[idx];
        setCurrentSpeaker(agentIds[idx] || null);
        setStreamedMessages((prev) => [...prev, nextMsg]);
        idx++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
        setCurrentSpeaker(null);
      }
    }, 3500);

    return () => clearInterval(interval);
  }, [activeTicker]);

  // Calculate Portfolio Value
  const portfolioSummary = useMemo(() => {
    let totalTL = 0;
    const assets = liveQuotes
      .filter((q) => PORTFOLIO_QUANTITIES[q.ticker])
      .map((q) => {
        const qty = PORTFOLIO_QUANTITIES[q.ticker];
        const valueTL = q.currency === "$" ? q.price * FIXED_USDTRY * qty : q.price * qty;
        totalTL += valueTL;
        return { ...q, qty, valueTL };
      });

    return { totalTL, totalUSD: totalTL / FIXED_USDTRY, assets };
  }, [liveQuotes]);

  const activeStock = liveQuotes.find((s) => s.ticker === activeTicker) || null;
  const activeSession = activeTicker ? debates.find((d) => d.ticker === activeTicker) : null;
  const activeAgentIds = activeSession ? findSpeakerAgentIds(activeSession.messages) : [];
  const activeAgents = activeAgentIds
    .map((id) => analysts.find((a) => a.id === id))
    .filter((a): a is Analyst => a !== undefined);

  const handleStockSelect = (stock: StockQuote) => {
    setActiveTicker(stock.ticker);
  };

  const formatTime = (d: Date) =>
    d.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });

  const formatDate = (d: Date) =>
    d.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });

  const potential = activeStock
    ? ((activeStock.targetPrice - activeStock.price) / activeStock.price) * 100
    : 0;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 flex font-sans overflow-hidden">
      <AgentDatabase onSelect={() => {}} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between px-4 py-2 bg-[#0a0f24] border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <i className="fa-solid fa-chess-king text-indigo-400 text-sm" />
              <span className="text-xs font-bold text-white tracking-wider uppercase">
                Konsey Odası
              </span>
            </div>
            <span className="text-[10px] text-slate-600 font-mono px-2 py-0.5 border border-slate-700 rounded">
              v7.0 Telemetry
            </span>
          </div>
          
          <div className="flex-1 max-w-sm mx-auto px-4">
             <div className="bg-slate-900/50 border border-slate-800 rounded px-3 py-1 flex justify-between items-center">
                <span className="text-[9px] text-slate-500 uppercase font-bold">Portföy Değeri</span>
                <div className="flex gap-4">
                   <span className="text-[11px] font-mono text-emerald-400">
                      ₺{portfolioSummary.totalTL.toLocaleString("tr-TR", { maximumFractionDigits: 0 })}
                   </span>
                   <span className="text-[11px] font-mono text-blue-400">
                      ${portfolioSummary.totalUSD.toLocaleString("tr-TR", { maximumFractionDigits: 0 })}
                   </span>
                </div>
                <span className="text-[9px] text-slate-700 font-mono">@ 46.67</span>
             </div>
          </div>

          <div className="flex items-center gap-3 text-[10px] font-mono text-slate-500">
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              CANLI
            </span>
            <span>{formatDate(systemTime)}</span>
            <span className="text-slate-600">{formatTime(systemTime)}</span>
          </div>
        </header>

        <StockTicker activeTicker={activeTicker} onSelect={handleStockSelect} />

        <main className="flex-1 overflow-y-auto bg-[#040814]">
          {!activeStock && <WelcomeDashboard />}

          {activeStock && activeSession && (
            <div className="flex flex-col h-full">
              <div className="bg-[#040814]/95 backdrop-blur border-b border-slate-800 px-6 py-4">
                <div className="flex items-baseline gap-3 mb-1">
                  <h1 className="text-2xl font-bold text-white tracking-tight">
                    {activeStock.ticker}
                  </h1>
                  <span className="text-sm text-slate-400">{activeStock.name}</span>
                </div>
                <div className="flex items-center gap-4 mt-1">
                  <span className="text-xl font-mono text-slate-200">
                    {activeStock.currency}
                    {activeStock.price.toLocaleString("tr-TR", {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                  <span
                    className={`text-xs font-mono font-semibold px-2 py-0.5 rounded border ${
                      activeStock.change >= 0
                        ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
                        : "bg-red-950/60 text-red-400 border-red-800"
                    }`}
                  >
                    {activeStock.change >= 0 ? "+" : ""}
                    {activeStock.change}%
                  </span>
                  <span className="text-xs text-slate-600">| Hedef: {activeStock.targetPrice.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</span>
                  <span className="text-xs text-emerald-500">
                    Potansiyel: +{potential.toFixed(1)}%
                  </span>
                  {PORTFOLIO_QUANTITIES[activeStock.ticker] && (
                    <span className="ml-auto text-[10px] bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded border border-indigo-500/30">
                       Varlık: {PORTFOLIO_QUANTITIES[activeStock.ticker]} Lot
                    </span>
                  )}
                </div>
              </div>

              <div className="flex-1 flex gap-6 p-6">
                <div className="flex-1 bg-slate-950/40 border border-slate-800/80 rounded-xl p-4 min-h-[400px] relative">
                  <BoardroomTable
                    activeAgents={activeAgents}
                    currentSpeaker={currentSpeaker}
                  />
                </div>
                <div className="w-[420px] shrink-0 bg-slate-950/40 border border-slate-800/80 rounded-xl flex flex-col">
                  <div className="px-4 py-2 border-b border-slate-800/60 flex items-center gap-2">
                    <i className="fa-solid fa-comment text-blue-400 text-[10px]" />
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      Tartışma Kaydı
                    </span>
                    {isStreaming && (
                      <span className="ml-auto text-[10px] text-emerald-400 animate-pulse flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Canlı
                      </span>
                    )}
                  </div>
                  <TranscriptViewer
                    messages={streamedMessages}
                    currentSpeaker={currentSpeaker}
                  />
                </div>
              </div>
            </div>
          )}
        </main>

        <footer className="border-t border-slate-800 px-4 py-2 bg-[#0a0f24] shrink-0">
          <div className="flex items-center justify-between text-[9px] text-slate-600 font-mono">
            <span>COUNCIL CHAMBER v7.0 // MIDAS TELEMETRY ACTIVE // FIXED USD: 46.67</span>
            <span>UPDATED: {formatDate(systemTime)} {formatTime(systemTime)}</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
